"""Automatically retrieve OPEN-ACCESS primary PDFs and rank original text passages.

No LLM, manual paste, licensed-site bypass, or fabricated full-text.
Source paper IDs/titles/years come from the existing private 28-paper library.
The original library, frozen results, 24-case blind keys, and Gold are READ-ONLY.
Results remain in the gitignored local_only tree; outputs are evidence CANDIDATES,
NOT human-inspected source verification or scientifically graded labels.

Usage:
  python -m research_lab.auto_primary_evidence --project .
  python -m research_lab.auto_primary_evidence --project . --limit 3
  python -m research_lab.auto_primary_evidence --project . --offline   # cached PDFs

Optional dependency: pip install -r requirements_paper_auto.txt
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from research_lab.fulltext_label_audit import BASE, OUT, LIBRARY, _snapshot, _source_baseline
from research_lab.blind_paper_eval import csv_read, csv_write

AUTO = "AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv"
SUMMARY = "AUTO_EVIDENCE_STATUS.json"
HEADERS = ("blind_id","snapshot_year","paper_id","paper_title",
           "versioned_source_url","source_version_date","date_status",
           "download_sha256","passage_locator","passage_text",
           "match_score","evidence_status","notes")
MAX_BYTES = 24_000_000
AGENT = "ChronoHyperResearchAssessment/1.0 (private academic evidence audit; open access only)"
STOP=set("a an the and of to on for from with by in is are using based data new methods method model models using study studies paper investigation investigation an over approach high low including we our their into compared use have this that materials material system systems computational".split())


def _normalize(text):
    text=unicodedata.normalize("NFKD",text or "").lower()
    return " ".join(re.findall(r"[a-z0-9]{3,}",text))

def _tokens(text):
    return {t for t in _normalize(text).split() if t not in STOP}

def _arxiv_id(url):
    # Explicit /abs/NNNN.NNNNN or /pdf/NNNN.NNNNN; strip versions and query.
    path=urllib.parse.urlparse(url).path
    m=re.search(r"/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})(?:v[0-9]+)?(?:\.pdf)?$",path)
    return m.group(1) if m else None

def _request(url, *, cap=MAX_BYTES, accept="application/pdf"):
    q=urllib.parse.urlparse(url)
    if q.scheme!="https" or not q.hostname:
        raise ValueError("Only HTTPS source URLs permitted")
    if q.hostname in ("localhost",) or q.hostname.endswith((".local",".internal")):
        raise ValueError("Local addresses prohibited")
    request=urllib.request.Request(url,headers={"User-Agent":AGENT,"Accept":accept})
    with urllib.request.urlopen(request,timeout=22) as resp:
        final=urllib.parse.urlparse(resp.geturl())
        if final.scheme!="https" or not final.hostname:
            raise ValueError("Insecure HTTP redirect blocked")
        mime=(resp.headers.get("Content-Type") or "").lower()
        if "pdf" not in mime and accept=="application/pdf" and (
                not resp.geturl().lower().split("?")[0].endswith(".pdf")):
            raise ValueError("Response is not a PDF: "+mime)
        body=resp.read(cap+1)
        if len(body)>cap:
            raise ValueError("Oversized source response")
        return body,resp.geturl()

def _json(url):
    body,_=_request(url,cap=2_000_000,accept="application/json")
    return json.loads(body.decode("utf-8"))

def _arxiv_version1(arxiv_id, *, offline=False):
    """Only accepted dated source: arXiv v1 metadata explicitly returned by API."""
    if offline:return None
    endpoint="https://export.arxiv.org/api/query?id_list="+arxiv_id+"v1"
    body,_=_request(endpoint,cap=300_000,accept="application/atom+xml")
    root=ET.fromstring(body)
    ns={"a":"http://www.w3.org/2005/Atom"}
    entry=root.find("a:entry",ns)
    if entry is None:return None
    identifier=(entry.findtext("a:id","",namespaces=ns) or "").lower()
    if arxiv_id not in identifier:
        return None
    published=entry.findtext("a:published","",namespaces=ns)
    updated=entry.findtext("a:updated","",namespaces=ns)
    for stamp in (published,updated):
        if stamp and re.match(r"^\d{4}-\d{2}-\d{2}T",stamp):
            # For v1, publication date is the original submission.
            if stamp==published:
                return stamp[:10]
    return None

def _openalex_candidate(title, year, *, offline=False):
    if offline:return []
    url="https://api.openalex.org/works?"+urllib.parse.urlencode({
      "search":title,"per-page":5,
      "select":"id,title,publication_year,best_oa_location,primary_location,locations,doi"})
    work=_json(url).get("results",[])
    accepted=[]
    for item in work:
        sim=SequenceMatcher(None,_normalize(title),_normalize(item.get("title",""))).ratio()
        pub=item.get("publication_year")
        if sim<0.86 or (pub is not None and abs(int(pub)-int(year))>2):
            continue
        locs=[item.get("best_oa_location"),item.get("primary_location")]+(item.get("locations") or [])
        for loc in locs:
            if not isinstance(loc,dict):continue
            pdf=loc.get("pdf_url") or ""
            if pdf.startswith("https://"):
                accepted.append((sim,pdf,str(item.get("id",""))))
    return [url for _,url,_ in sorted(accepted,reverse=True)][:5]

def _pdf_text(pdf_bytes):
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Not a PDF")
    import pymupdf
    doc=pymupdf.open(stream=pdf_bytes,filetype="pdf")
    if doc.page_count<1 or doc.page_count>450:
        raise ValueError("Invalid/oversized page count")
    pages=[]
    for idx,page in enumerate(doc):
        txt=" ".join(page.get_text("text",sort=True).split())
        if txt:pages.append((idx+1,txt))
    doc.close()
    if sum(len(s) for _,s in pages)<1000:
        raise ValueError("No substantial readable PDF text; OCR not assumed")
    return pages

def _windows(page_text, *, width=850, stride=550):
    if len(page_text)<160:
        return []
    return [page_text[start:start+width] for start in range(0,len(page_text),stride)
            if len(page_text[start:start+width])>=160]

def _rank_passage(pages, query):
    terms=_tokens(query)
    if not terms:
        return None
    best=None
    for page_no,text in pages:
        for window in _windows(text):
            toks=_tokens(window)
            hits=len(terms&toks)
            score=hits/max(1,len(terms))
            # Ignore junk back matter; prefer coverage rather than repetition.
            if hits<2:continue
            record=(round(score,4),hits,-page_no,window,page_no)
            if best is None or record[:3]>best[:3]:
                best=record
    if best is None:return None
    return {"score":best[0],"passage":best[3],"page":best[4],
            "terms_matched":best[1]}

def _paper_candidates(paper, *, offline=False):
    url=paper.get("source_url","").strip()
    if not url:
        return []
    arxiv=_arxiv_id(url)
    if arxiv:
        return [("https://arxiv.org/pdf/"+arxiv+"v1", "arxiv_v1", arxiv)]
    direct=[]
    if url.lower().split("?")[0].endswith(".pdf"):
        direct.append((url,"original_pdf_unverified",None))
    for candidate in _openalex_candidate(paper["paper_title"],paper["paper_year"],offline=offline):
        direct.append((candidate,"openalex_oa_pdf_unverified",None))
    seen=set()
    return [x for x in direct if not(x[0] in seen or seen.add(x[0]))]


def run(project=".",limit=None,offline=False):
    root=Path(project).resolve()
    _,_,cases,keys=_snapshot(root)
    folder=root/OUT
    library=folder/LIBRARY
    if not library.is_file():
        raise FileNotFoundError("Run python -m research_lab.fulltext_label_audit --project . --prepare first")
    papers=csv_read(library)
    if len(papers)!=28 or len({x["paper_id"] for x in papers})!=28:
        raise ValueError("Expected the original distinct 28 source papers; never alter IDs")
    if not any(r["source_url"].strip() for r in papers):
        raise ValueError("Add original source URLs first; do NOT paste passages manually")
    source_by_id={x["paper_id"]:x for x in papers}
    # The source case->paper mapping is a project artifact, never synthetic.
    cases_sheet=csv_read(folder/"SOURCE_PASSAGES_TO_FILL.csv")
    if len(cases_sheet)!=92:
        raise ValueError("Expected 92 original case-paper links")
    case_by_id={x["blind_id"]:x for x in cases}
    if len(case_by_id)!=24:
        raise ValueError("Private blind source ID corruption")
    for r in cases_sheet:
        if r["paper_id"] and r["paper_id"] not in source_by_id:
            raise ValueError("Case-paper source IDs mismatch")
    if any(r.get("evidence_access","").strip() for r in cases_sheet if r["paper_id"]):
        raise ValueError("Per-case source worksheet already edited; refuse automated copy")
    target=folder/AUTO
    status=folder/SUMMARY
    if target.exists() or status.exists():
        raise FileExistsError("Do not overwrite a prior automatic run; archive its output explicitly")
    cache=folder/"open_access_pdf_cache"
    cache.mkdir(parents=True,exist_ok=True)
    statuses={}
    chosen={}
    if limit is not None and limit<1:
        raise ValueError("Limit must be positive")
    work=papers if limit is None else papers[:limit]
    # Group case evidence requirements before PDF retrieval.
    bypaper=defaultdict(list)
    for r in cases_sheet:
        if r["paper_id"]:
            bypaper[r["paper_id"]].append(r)
    for idx,p in enumerate(work,1):
        pid=p["paper_id"]
        linked=bypaper.get(pid,[])
        earliest=min(int(x["snapshot_year"]) for x in linked) if linked else 9999
        if earliest==9999:
            statuses[pid]={"status":"NO_LINKED_CASES"}
            continue
        record={"status":"NO_VERIFIED_OPEN_PDF","earliest_snapshot":earliest,
                "original_paper_year":p["paper_year"],"attempts":[]}
        options=[]
        try:
            options=_paper_candidates(p,offline=offline)
        except Exception as e:
            record["attempts"].append("discovery: "+str(e)[:180])
        for url,kind,arxiv in options:
            cachefile=cache/(hashlib.sha256(url.encode()).hexdigest()+".pdf")
            try:
                if cachefile.exists():
                    body=cachefile.read_bytes()
                    resolved=url
                elif offline:
                    continue
                else:
                    body,resolved=_request(url)
                    if not body.startswith(b"%PDF-"):
                        raise ValueError("HTTP response was not PDF")
                    cachefile.write_bytes(body)
                pages=_pdf_text(body)
                date=None
                if arxiv:
                    try:
                        date=_arxiv_version1(arxiv,offline=offline)
                    except Exception as e:
                        record["attempts"].append("version metadata: "+str(e)[:120])
                date_ok=bool(date and date<=f"{earliest}-12-31")
                # DOI or arbitrary OA PDF can be newer than the original;
                # date and version are NOT independently verified here.
                if date and not date_ok:
                    record["attempts"].append("v1 date after cutoff: "+date)
                    continue
                record.update({"status":"AUTO_EXTRACTED_HISTORICAL_V1_METADATA" if date_ok
                                      else "AUTO_EXTRACTED_DATE_UNVERIFIED",
                               "source_url":resolved,"source_version_date":date or "",
                               "source_version_type":kind,
                               "date_within_earliest_snapshot":date_ok,
                               "pdf_sha256":hashlib.sha256(body).hexdigest(),
                               "pdf_page_count":len(pages),
                               "pdf_cached_locally":True,
                               "independent_scientific_semantics_verified":False})
                chosen[pid]=(record,pages)
                break
            except Exception as e:
                record["attempts"].append(kind+": "+str(e)[:180])
        statuses[pid]=record
        print(f"[{idx}/{len(work)}] {pid} {record['status']}",flush=True)
    rows=[]
    for ref in cases_sheet:
        pid=ref["paper_id"]
        if not pid or pid not in chosen:
            continue
        info,pages=chosen[pid]
        case=case_by_id[ref["blind_id"]]
        # Candidate selection is lexical only; cannot establish entailment.
        query=" ".join((case["label_A"],case["label_B"],case["member_names"]))
        best=_rank_passage(pages,query)
        if best is None:
            continue
        rows.append({
            "blind_id":ref["blind_id"],"snapshot_year":ref["snapshot_year"],
            "paper_id":pid,"paper_title":source_by_id[pid]["paper_title"],
            "versioned_source_url":info["source_url"],
            "source_version_date":info.get("source_version_date",""),
            "date_status":"ARXIV_V1_WITHIN_CUTOFF" if info["date_within_earliest_snapshot"] else "UNVERIFIED",
            "download_sha256":info["pdf_sha256"],
            "passage_locator":f"PDF page {best['page']} (machine extracted)",
            "passage_text":best["passage"],
            "match_score":best["score"],
            "evidence_status":"AUTO_RETRIEVED_UNVERIFIED_NOT_REVIEWED",
            "notes":"Authentic PDF bytes cached locally; matching passage selected lexically; no independent entailment review"})
    csv_write(target,rows,HEADERS)
    summary={
       "schema":"chronohyper_auto_open_primary_evidence_v1",
       "research_stage":"PRIVATE_AUTOMATED_EVIDENCE_CANDIDATES_NOT_BLIND_EVALUATION",
       "number_of_original_papers":len(papers),
       "number_of_attempted_papers":len(work),
       "unique_accessible_pdf_count":len(chosen),
       "arxiv_v1_within_cutoff_count":sum(1 for z in statuses.values()
                    if z.get("status")=="AUTO_EXTRACTED_HISTORICAL_V1_METADATA"),
       "pdf_date_version_unverified_count":sum(1 for z in statuses.values()
                    if z.get("status")=="AUTO_EXTRACTED_DATE_UNVERIFIED"),
       "candidate_case_paper_passages":len(rows),
       "cases_with_candidate_passages":len({x["blind_id"] for x in rows}),
       "paper_statuses":statuses,
       "original_paper_library_unchanged":True,
       "gold_opened":False,
       "blind_mapping_exported":False,
       "external_judge_scores_fabricated":False,
       "passages_are_machine_extracted_not_independently_scientifically_verified":True,
       "copyright_scope":"Local private research only; do not publish PDFs or full extracted passages",
       "files":{"candidate_evidence":str(target),"status":str(status)},
    }
    status.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("paper_statuses","files")},
                     ensure_ascii=False,indent=2))
    print("Automatic evidence candidates:",target)
    print("Full errors/source status:",status)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",default=".")
    p.add_argument("--limit",type=int)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    run(a.project,a.limit,a.offline)

if __name__=="__main__":
    main()
