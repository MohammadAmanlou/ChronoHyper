"""Neutral Type-B AI reviewer packet and audited import; never include gold or prior judgments."""
import argparse,csv,hashlib,json
from pathlib import Path

BASE="research_outputs/type_b_audit/CLAIM_LEVEL_REVIEW_BLANK.csv"
PACKET="local_only/reviews/type_b_ai_packet/CLAIMS_FOR_AI.csv"
MERGED="local_only/reviews/type_b_ai_packet/claims_rated_AI.csv"
COLS=("question_id","claim_id","required_claim",
      "manual_claim_supported_yes_no_unclear",
      "manual_source_citation_verified_yes_no_unclear",
      "human_reviewer","reviewer_notes")
OUTPUTS=COLS[3:]

def read(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:
        d=csv.DictReader(f)
        if not d.fieldnames or len(set(d.fieldnames))!=len(d.fieldnames):raise ValueError("Invalid CSV header")
        return d.fieldnames,list(d)

def write(p,fields,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="raise");w.writeheader();w.writerows(rows)

def baseline(project):
    root=Path(project).resolve()
    head,rows=read(root/BASE)
    if len(rows)!=36 or len({v["claim_id"] for v in rows})!=36:raise ValueError("Expected 36 unique source claims")
    if not set(COLS).issubset(head):raise ValueError("Missing source review columns")
    return root,head,rows

def prepare(project="."):
    root,head,rows=baseline(project)
    dest=root/PACKET
    intended=[{k:row[k] for k in COLS} for row in rows]
    if dest.exists():
        old_h,old=read(dest)
        if old_h!=list(COLS) or old!=intended:raise ValueError("Existing packet differs, do not overwrite")
    else:write(dest,COLS,intended)
    print(json.dumps({"packet":str(dest),"rows":36,"excluded_private_fields":sorted(set(head)-set(COLS)),
      "old_reviewer_opinions_included":False,"gold_included":False},indent=2))
    return dest

def merge(project=".",ratings="",out=MERGED):
    if not ratings:raise ValueError("A completed AI reviewer CSV is required")
    root,head,rows=baseline(project)
    packet=root/PACKET
    if not packet.is_file():raise FileNotFoundError("Run --prepare first")
    path=Path(ratings)
    if not path.is_absolute():path=root/path
    h,assessed=read(path)
    if h!=list(COLS) or len(assessed)!=36:raise ValueError("Reviewer must retain 36 rows and the exact packet columns")
    ref={r["claim_id"]:r for r in rows}
    if {r["claim_id"] for r in assessed}!=set(ref):raise ValueError("Missing/extra/duplicate claim IDs")
    rated={}
    for r in assessed:
        for k in COLS[:3]:
            if r[k]!=ref[r["claim_id"]][k]:raise ValueError("Original claim evidence was edited")
        if not all(r[k].strip().lower() in {"yes","no","unclear"} for k in OUTPUTS[:2]):
            raise ValueError("Every row must contain yes/no/unclear for both judgements")
        if not r["human_reviewer"].strip() or len(r["reviewer_notes"].strip())<15:
            raise ValueError("Real AI model identifier and case-specific notes required")
        if (r["manual_source_citation_verified_yes_no_unclear"].strip().lower()=="yes"
            and "http" not in r["reviewer_notes"].lower() and "doi:" not in r["reviewer_notes"].lower()):
            raise ValueError("Cited yes requires URL/DOI in notes")
        rated[r["claim_id"]]=r
    result=[]
    for old in rows:
        copy=dict(old);copy.update({k:rated[old["claim_id"]][k] for k in OUTPUTS});result.append(copy)
    dest=Path(out)
    if not dest.is_absolute():dest=root/dest
    if dest.exists():raise FileExistsError("Existing completed review protected: "+str(dest))
    write(dest,head,result)
    print(json.dumps({"output":str(dest),"rows":len(result),"reviewers_self_reported":sorted({r["human_reviewer"] for r in result}),
      "gold_and_source_coverage_flags_unchanged":True,"reviewer_independence_verified_by_code":False,
      "fulltext_entailment_verified_by_code":False,"sha256":hashlib.sha256(dest.read_bytes()).hexdigest()},indent=2))
    return dest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_mutually_exclusive_group(required=True);sub.add_argument("--prepare",action="store_true");sub.add_argument("--merge",action="store_true")
    p.add_argument("--project",default=".");p.add_argument("--ratings",default="");p.add_argument("--out",default=MERGED)
    a=p.parse_args()
    if a.prepare:prepare(a.project)
    else:merge(a.project,a.ratings,a.out)
if __name__=="__main__":main()
