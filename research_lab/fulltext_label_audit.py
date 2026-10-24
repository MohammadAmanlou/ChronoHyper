"""Local-only authentic primary-paper evidence intake for 24 blind V2/V3 labels.

PREPARE creates an empty, source-linked passage worksheet using ORIGINAL
year-cutoff provenance and the previously prepared blind cases. It never
opens hidden retrieval Gold and never fetches or invents paper text.

ASSEMBLE accepts user-inspected, dated primary full-text passages; preserves
the original case identities while adding passages to a reviewer worksheet.
Incomplete coverage is always marked INSUFFICIENT. This is not independent
validation until an isolated, qualified reviewer actually rates it.

SCORE checks ALL immutable evidence cells and explicitly counts title/gloss
overclaims, uncertainties and effective denominators; keeps private keys,
source passages and individual judgments under ignored local_only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

from research_lab.blind_paper_eval import _source, csv_read, csv_write
from research_lab.label_v3_blind import FIELDS, RATING

BASE = Path("local_only/reviews/label_v3_fresh")
OUT = Path("local_only/reviews/fulltext_label24")
SOURCE = "SOURCE_PASSAGES_TO_FILL.csv"
REVIEW = "BLIND_FULLTEXT_LABEL24.csv"
KEYS = "mapping_PRIVATE.csv"
PAPER_FIELDS = (
    "blind_id", "snapshot_year", "paper_id", "paper_title", "paper_year",
    "source_url", "source_version_date", "passage_locator", "passage_text",
    "evidence_access",
)
FIXED_REVIEW = (*FIELDS[:9], "primary_source_passages", "evidence_status", "passage_count")
REVIEW_FIELDS = (*FIXED_REVIEW, *FIELDS[9:])
ALLOWED_ACCESS = {"FULL_TEXT_USER_INSPECTED", "UNAVAILABLE"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
YEARS = (2020, 2022, 2024)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _snapshot(root):
    original = root / BASE / "blind_v2_v3_24.csv"
    private = root / BASE / KEYS
    if not original.is_file() or not private.is_file():
        raise FileNotFoundError("Prepare the original private 24-case blind packet first: python -m research_lab.label_v3_blind --project . --prepare")
    orig = csv_read(original)
    keys = csv_read(private)
    ids = [r["blind_id"] for r in orig]
    if len(ids) != 24 or len(set(ids)) != 24 or (
            set(ids) != {r["blind_id"] for r in keys}):
        raise ValueError("Expected unchanged 24-case blind sheet and local key")
    if any(any((r.get(field) or "").strip() for field in FIELDS[9:]) for r in orig):
        raise ValueError("Original blind form has already been rated or modified")
    return original, private, orig, {r["blind_id"]:r for r in keys}


def _case_sources(case, secret, entries, nodes, papers, max_papers=4):
    year = int(case["snapshot_year"])
    item = entries.get((year, secret["stable_id"]))
    if item is None:
        raise ValueError("Original source cluster missing for "+case["blind_id"])
    raw = case["member_names"].split(" | ")
    wanted = Counter(raw)
    candidates = [nodes[i] for i in item["member_ids"] if (
        nodes[i]["type"] not in ("article","author","claim","cited_work")
        and int(nodes[i]["first_seen_year"])<=year)]
    matching = []
    for name, count in wanted.items():
        options = [n for n in candidates if n["surface_form"] == name]
        if len(options) < count:
            raise ValueError("Blind member name missing from original chosen cluster: "+
                             case["blind_id"]+" "+name)
        # Ties are retained conservatively; no ungrounded node disambiguation.
        matching.extend(options)
    coverage = Counter()
    for n in matching:
        ids = set(map(str, n.get("provenance",{}).get("articles",[])))
        for aid in ids:
            p = papers.get(aid)
            if p is None or not str(p.get("year","")).isdigit() or (
                    int(p["year"]) > year):
                continue
            if p.get("title","").strip():
                coverage[aid] += 1
    ordered = sorted(coverage,key=lambda a:(-coverage[a],int(papers[a]["year"]),a))
    return [papers[a] for a in ordered[:max_papers]]


def prepare(project="."):
    root = Path(project).resolve()
    orig_path,key_path,cases,keys = _snapshot(root)
    out = root/OUT
    out.mkdir(parents=True,exist_ok=True)
    worksheet = out/SOURCE
    manifest = out/"manifest_LOCAL.json"
    if worksheet.exists() or manifest.exists():
        raise FileExistsError("Existing evidence intake is frozen; do not overwrite: "+str(worksheet))
    raw_nodes,papers = _source(root)
    nodes = {x["id"]:x for x in raw_nodes}
    entries = {}
    for year in YEARS:
        path=root/f"research_outputs/label_v2/candidates_v2_{year}.json"
        rows=json.loads(path.read_text(encoding="utf-8"))
        for item in rows:
            entries[(year,item["stable_id"])] = item
    rows=[]
    counts={}
    for case in cases:
        found=_case_sources(case,keys[case["blind_id"]],entries,nodes,papers)
        counts[case["blind_id"]]=len(found)
        if not found:
            rows.append({x:"" for x in PAPER_FIELDS} |
                        {"blind_id":case["blind_id"],"snapshot_year":case["snapshot_year"],
                         "evidence_access":"UNAVAILABLE"})
        for p in found:
            item={x:"" for x in PAPER_FIELDS}
            item.update({"blind_id":case["blind_id"],"snapshot_year":case["snapshot_year"],
                         "paper_id":str(p["id"]),"paper_title":p["title"],
                         "paper_year":str(p["year"])})
            rows.append(item)
    csv_write(worksheet,rows,PAPER_FIELDS)
    manifest_doc={
        "schema":"chronohyper_fulltext_label24_source_intake_v1",
        "stage":"SOURCE_LINKING_ONLY_NOT_SCIENTIFIC_VERIFICATION",
        "cases":24,"source_rows":len(rows),
        "cases_with_at_least_one_original_linked_paper":sum(x>0 for x in counts.values()),
        "cases_without_linked_papers":sorted(k for k,v in counts.items() if v==0),
        "per_case_linked_paper_counts":counts,
        "max_papers_per_case":4,
        "original_blind_sha256":_sha(orig_path),
        "private_key_sha256":_sha(key_path),
        "original_paper_metadata_from_local_corpus":True,
        "paper_fulltexts_retrieved":False,
        "fulltext_evidence_verified":False,
        "blind_key_exported":False,
        "worksheet_sha256_initial":_sha(worksheet),
        "corpus_sharing_authorization_unknown":True
    }
    manifest.write_text(json.dumps(manifest_doc,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest_doc.items() if k!="per_case_linked_paper_counts"},indent=2))
    print("Fill actual primary paper passages here (LOCAL ONLY):",worksheet)
    return manifest_doc


def _trusted_passages(rows, base):
    """Reject metadata edits, false evidence dates, and unsupported source URLs.

    USER_ATTESTED does not mean independently verified online authenticity.
    """
    bykey={(r["blind_id"],r["paper_id"]):r for r in base}
    if len(rows)!=len(base) or len(bykey)!=len(base):
        raise ValueError("Do not drop, add, or duplicate any source rows")
    result=defaultdict(list)
    pending=Counter()
    for row in rows:
        k=(row["blind_id"],row["paper_id"])
        frozen=bykey.get(k)
        if frozen is None:
            raise ValueError("Unknown or duplicated case-paper source row")
        for name in PAPER_FIELDS[:5]:
            if row.get(name)!=frozen[name]:
                raise ValueError("Source citation metadata edited: "+str(k))
        access=row["evidence_access"].strip()
        if not row["paper_id"]:
            if access!="UNAVAILABLE" or any(
                    row.get(x,"").strip() for x in PAPER_FIELDS[5:9]):
                raise ValueError("No-linked-source placeholder cannot claim a passage")
            pending[row["blind_id"]]+=1
            continue
        if access == "UNAVAILABLE":
            if any(row.get(x,"").strip() for x in PAPER_FIELDS[5:9]):
                raise ValueError("Unavailable source cannot contain invented evidence")
            pending[row["blind_id"]]+=1
            continue
        if access != "FULL_TEXT_USER_INSPECTED":
            raise ValueError("Every linked paper must be explicitly FULL_TEXT_USER_INSPECTED or UNAVAILABLE")
        url=row["source_url"].strip()
        parsed=urlparse(url)
        if parsed.scheme!="https" or not parsed.netloc or (
                parsed.username is not None or parsed.password is not None):
            raise ValueError("Evidence needs a working original HTTPS paper/preprint URL")
        date=row["source_version_date"].strip()
        if (not DATE_PATTERN.fullmatch(date) or
                date>f"{row['snapshot_year']}-12-31" or
                date[:4] > row["paper_year"] and date[:4] > row["snapshot_year"]):
            raise ValueError("Dated paper version exceeds snapshot cutoff: "+str(k))
        if len(row["passage_locator"].strip())<5 or len(row["passage_text"].strip())<90:
            raise ValueError("Primary paper passage and section/page required: "+str(k))
        result[row["blind_id"]].append(row)
    return result,pending


def _source_baseline(root):
    origpath,keypath,cases,keys=_snapshot(root)
    out=root/OUT
    manifest=json.loads((out/"manifest_LOCAL.json").read_text(encoding="utf-8"))
    if _sha(origpath)!=manifest["original_blind_sha256"] or (
            _sha(keypath)!=manifest["private_key_sha256"]):
        raise ValueError("Original blind source or private mapping changed")
    initial = out/"SOURCE_PASSAGES_TO_FILL.csv"
    if not initial.is_file():
        raise FileNotFoundError(str(initial))
    raw=csv_read(initial)
    return cases,keys,raw,manifest


def assemble(project="."):
    root=Path(project).resolve()
    cases,_,current,manifest=_source_baseline(root)
    out=root/OUT
    # Freeze reference headers and metadata from corpus, not from an edited worksheet.
    raw_nodes,papers=_source(root)
    keys={r["blind_id"]:r for r in csv_read(root/BASE/KEYS)}
    nodes={n["id"]:n for n in raw_nodes}
    entries={}
    for yr in YEARS:
        for item in json.loads((root/f"research_outputs/label_v2/candidates_v2_{yr}.json").read_text(encoding="utf-8")):
            entries[(yr,item["stable_id"])]=item
    pristine=[]
    for case in cases:
        ps=_case_sources(case,keys[case["blind_id"]],entries,nodes,papers)
        if not ps:
            pristine.append({x:"" for x in PAPER_FIELDS}|
                            {"blind_id":case["blind_id"],"snapshot_year":case["snapshot_year"],
                             "evidence_access":"UNAVAILABLE"})
        for p in ps:
            row={x:"" for x in PAPER_FIELDS}
            row.update({"blind_id":case["blind_id"],"snapshot_year":case["snapshot_year"],
                        "paper_id":str(p["id"]),"paper_title":p["title"],"paper_year":str(p["year"])})
            pristine.append(row)
    supports,pending=_trusted_passages(current,pristine)
    if not sum(map(len,supports.values())):
        raise ValueError("No authentic full-text excerpts supplied; cannot create a scientific reviewer packet")
    target=out/REVIEW
    if target.exists():
        raise FileExistsError("Reviewer packet already exists; never overwrite")
    result=[]
    for case in cases:
        excerpts=supports.get(case["blind_id"],[])
        fixed={k:case[k] for k in FIELDS[:9]}
        blocks=[]
        for source in excerpts:
            blocks.append(f"PAPER {source['paper_id']} | {source['paper_title']} "
                          f"({source['paper_year']}); {source['source_url']}; "
                          f"version {source['source_version_date']}; "
                          f"{source['passage_locator']}\n{source['passage_text'].strip()}")
        row={**fixed,
             "primary_source_passages":"\n\n".join(blocks),
             "evidence_status":"USER_ATTESTED_FULLTEXT" if blocks else "INSUFFICIENT_NO_FULLTEXT",
             "passage_count":str(len(excerpts))}
        row.update({x:"" for x in FIELDS[9:]})
        result.append(row)
    csv_write(target,result,REVIEW_FIELDS)
    instructions=(out/"JUDGE_INSTRUCTIONS.txt")
    instructions.write_text(
        "INDEPENDENT BLIND SCIENTIFIC LABEL REVIEW (24 pairs).\n"
        "Review only BLIND_FULLTEXT_LABEL24.csv, never the repository, private "
        "mapping, past scores, or original experiment groups.\n"
        "For A and B titles, grade accurate/vague/wrong when the supplied dated "
        "full-text passages are sufficient. For both glosses, mark overclaim "
        "yes/no/unclear. For insufficient sources, set evidence_sufficient_yes_no=no "
        "and BOTH overclaims=unclear; leave title grades empty.\n"
        "Cited passages were USER-ATTESTED but not independently web-verified by "
        "code; confirm source URL, version date, scope and section. "
        "Names and article titles alone do not prove scientific entailment.\n"
        "Keep original case/evidence columns and all 24 rows unchanged. Fill your "
        "ACTUAL reviewer name/model and specific evidence notes. Never infer A/B mapping.\n"
        "No evidence of independent review exists until genuine completed ratings "
        "are returned and validated. External sharing requires corpus authorization.\n",
        encoding="utf-8")
    receipt={"schema":"chronohyper_fulltext_label24_blind_handoff_v1",
       "stage":"PACKET_ASSEMBLED_NO_REVIEW_YET",
       "n_cases":24,"cases_with_user_attested_passages":sum(bool(supports.get(c["blind_id"])) for c in cases),
       "n_passages_user_attested":sum(map(len,supports.values())),
       "cases_lacking_fulltext":[c["blind_id"] for c in cases if not supports.get(c["blind_id"])],
       "blind_packet_sha256":_sha(target),
       "original_mapping_kept_private":True,"primary_fulltext_verified_by_software":False,
       "external_sharing_permission_not_verified":True}
    (out/"assembled_receipt_LOCAL.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))
    print("BLIND REVIEWER FILE (share only if authorized):",target)
    return receipt


def _wilson(positive,total):
    if not total:return None
    z=1.959963984540054
    p=positive/total
    d=1+z*z/total
    centre=(p+z*z/(2*total))/d
    rad=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/d
    return [max(0,centre-rad),min(1,centre+rad)]


def score(project=".",ratings=""):
    root=Path(project).resolve();out=root/OUT
    worksheet=out/REVIEW
    if not worksheet.is_file():raise FileNotFoundError("Assemble the reviewed source packet first")
    if not ratings:raise ValueError("Provide a completed external reviewer CSV")
    path=Path(ratings)
    if not path.is_absolute():path=root/path
    original=csv_read(worksheet)
    reviewed=csv_read(path)
    keys={r["blind_id"]:r for r in csv_read(root/BASE/KEYS)}
    if len(original)!=24 or len(reviewed)!=24:raise ValueError("Full 24-case evaluation required")
    forms={r["blind_id"]:r for r in original}
    if len(forms)!=24 or len({r["blind_id"] for r in reviewed})!=24:
        raise ValueError("Bad blind ID count")
    wins=losses=ties=0
    adequate=0
    bytype={s:{"overclaim":0,"evaluable":0,"unclear":0} for s in ("v2","v3")}
    reporters=set()
    for row in reviewed:
        bid=row["blind_id"]
        frozen=forms.get(bid)
        if frozen is None or any(row.get(k)!=frozen.get(k) for k in FIXED_REVIEW):
            raise ValueError("Reviewer changed frozen evidence: "+bid)
        if not row.get("reviewer_id","").strip() or len(row.get("review_notes","").strip())<15:
            raise ValueError("Actual reviewer identity and case-specific notes required")
        reporters.add(row["reviewer_id"].strip())
        suff=row.get("evidence_sufficient_yes_no","").strip().lower()
        if suff not in ("yes","no"):
            raise ValueError("Every case needs evidence sufficiency yes/no")
        if suff=="yes" and frozen["evidence_status"]!="USER_ATTESTED_FULLTEXT":
            raise ValueError("A case lacking full text cannot be assessed as sufficient")
        v3=keys[bid]["v3_side"];v2="A" if v3=="B" else "B"
        title={s:row.get(s+"_accuracy_accurate_vague_wrong","").strip().lower() for s in ("A","B")}
        gloss={s:row.get(s+"_gloss_overclaim_yes_no_unclear","").strip().lower() for s in ("A","B")}
        if suff=="yes":
            adequate+=1
            if any(x not in RATING for x in title.values()) or any(x not in ("yes","no","unclear") for x in gloss.values()):
                raise ValueError("Invalid evidence-based title/gloss grades")
            delta=RATING[title[v3]]-RATING[title[v2]]
            wins+=delta>0;losses+=delta<0;ties+=delta==0
        else:
            if any(x!="unclear" for x in gloss.values()) or any(title.values()):
                raise ValueError("Insufficient evidence requires blank titles and unclear glosses")
        for model,arm in (("v2",v2),("v3",v3)):
            flag=gloss[arm]
            if flag=="unclear":bytype[model]["unclear"]+=1
            else:
                bytype[model]["evaluable"]+=1
                bytype[model]["overclaim"]+=int(flag=="yes")
    n=wins+losses
    pval=min(1.0,2*sum(math.comb(n,j) for j in range(min(wins,losses)+1))/2**n) if n else None
    scoredoc={"schema":"chronohyper_blind_fulltext_label24_scored_v1",
       "stage":"DEVELOPMENT_SAME_CORPUS_REVIEW_NOT_FRESH_CONFIRMATION",
       "reviewed_cases":24,"sufficient_source_cases":adequate,
       "insufficient_cases":24-adequate,
       "paired_title_v3_wins":wins,"v3_losses":losses,"ties":ties,
       "two_sided_unadjusted_p_exploratory":pval,
       "overclaim_by_model":{
           model:{**stats,"rate":stats["overclaim"]/stats["evaluable"] if stats["evaluable"] else None,
                  "wilson_95ci":_wilson(stats["overclaim"],stats["evaluable"])}
           for model,stats in bytype.items()},
       "reviewer_ids_as_reported":sorted(reporters),
       "reviewed_sheet_sha256":_sha(path),
       "evidence_passages_independently_verified_by_software":False,
       "independence_of_reviewers_verified_by_software":False,
       "no_unseen_corpus_or_new_train_split_claim":True}
    dest=out/"score_LOCAL_PRIVATE.json"
    if dest.exists():raise FileExistsError("Preserve original evidence-based review score")
    dest.write_text(json.dumps(scoredoc,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(scoredoc,indent=2))
    return scoredoc


def main():
    p=argparse.ArgumentParser(description=__doc__)
    a=p.add_mutually_exclusive_group(required=True)
    for flag in ("prepare","assemble","score"):a.add_argument("--"+flag,action="store_true")
    p.add_argument("--project",default=".")
    p.add_argument("--ratings",default="")
    x=p.parse_args()
    if x.prepare:prepare(x.project)
    elif x.assemble:assemble(x.project)
    else:score(x.project,x.ratings)


if __name__=="__main__":
    main()
