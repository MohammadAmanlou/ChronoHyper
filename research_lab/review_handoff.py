"""Permission-gated, key-free reviewer handoff for confidential CKL blind packets.

No network operations. Source or hidden mapping NEVER enters the reviewer ZIP.
Preparing packets is NOT reviewing or independently validating them.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

SPEC = {
    "label24": {
        "directory": "local_only/reviews/label_v3_fresh",
        "worksheet": "blind_v2_v3_24.csv",
        "instructions": "JUDGE_INSTRUCTIONS.txt",
        "rows": 24,
        "id": "blind_id",
        "fixed": ("blind_id","snapshot_year","member_count","member_names",
                  "source_article_titles","label_A","gloss_A","label_B","gloss_B"),
        "scored": ("A_accuracy_accurate_vague_wrong",
                   "B_accuracy_accurate_vague_wrong",
                   "A_gloss_overclaim_yes_no_unclear",
                   "B_gloss_overclaim_yes_no_unclear",
                   "evidence_sufficient_yes_no","reviewer_id","review_notes"),
    },
    "coherence48": {
        "directory": "local_only/reviews/fresh_semantic",
        "worksheet": "blind_review_48.csv",
        "instructions": "JUDGE_INSTRUCTIONS.txt",
        "rows": 48,
        "id": "blind_id",
        "fixed": ("blind_id","snapshot_year","member_count",
                  "member_names","source_article_titles","source_evidence_limit"),
        "scored": ("coherence_score_1_to_5","evidence_sufficient_yes_no",
                   "reviewer_id","evidence_notes"),
    },
}

READ_ME = """Confidential blind assessment — authorized recipients only.

The blind worksheet and judge instructions are the only permitted input.
Do not infer which rows are controls, original, V2 or V3, and do not request
unblinding keys, code, older reviews, study outcomes, or hidden gold.

Respect scientific evidence sufficiency; titles and entity names are not
full scientific papers. Set unclear or insufficient when warranted, and keep
all original columns and rows. Report actual model name/reviewer identity,
not an invented expert status. This task is not an independently new corpus.

The project has not certified external-sharing permission. Receipt of this ZIP
does not imply permission to redistribute the underlying employer corpus.
"""

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        rd=csv.DictReader(f)
        if rd.fieldnames is None or len(set(rd.fieldnames))!=len(rd.fieldnames):
            raise ValueError("Missing or duplicate CSV headers")
        return rd.fieldnames, list(rd)

def _input(root, kind):
    if kind not in SPEC: raise ValueError("Unsupported packet kind")
    sp=SPEC[kind]
    folder=root/sp["directory"]
    a=folder/sp["worksheet"]
    b=folder/sp["instructions"]
    if not a.is_file() or not b.is_file():
        raise FileNotFoundError("Prepare original blind worksheet and instructions first: "+str(folder))
    headers, data=rows(a)
    needed=set(sp["fixed"])|set(sp["scored"])
    if needed-set(headers):
        raise ValueError("Missing worksheet columns: "+",".join(sorted(needed-set(headers))))
    ids=[str(z[sp["id"]]).strip() for z in data]
    if len(data)!=sp["rows"] or not all(ids) or len(set(ids))!=len(ids):
        raise ValueError("Invalid blind IDs/row count")
    if any(str(z.get(key,"")).strip() for z in data for key in sp["scored"]):
        raise ValueError("Original blinded worksheet already contains ratings; preserve and investigate")
    return sp,a,b,headers,data

def prepare(project=".",kind="label24",output=None,authorization=False):
    if not authorization:
        raise PermissionError("Explicit --authorized-share flag required; secure evaluator permission must be verified by user")
    root=Path(project).resolve()
    sp,form,instructions,headers,data=_input(root,kind)
    destination=(Path(output) if output else
                 root/"local_only"/"reviewer_exports"/f"{kind}_KEY_FREE.zip")
    if not destination.is_absolute(): destination=root/destination
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        raise FileExistsError("Preserving existing exported ZIP: "+str(destination))
    content=form.read_bytes()
    rules=instructions.read_bytes()
    if not rules.strip():
        raise ValueError("Empty reviewer instructions")
    with ZipFile(destination,"x",compression=ZIP_DEFLATED) as archive:
        archive.writestr(sp["worksheet"],content)
        archive.writestr(sp["instructions"],rules)
        archive.writestr("README_FOR_REVIEWER.txt",READ_ME.encode("utf-8"))
    with ZipFile(destination) as zipf:
        actual=set(zipf.namelist())
        expected={sp["worksheet"],sp["instructions"],"README_FOR_REVIEWER.txt"}
        if actual!=expected or any("PRIVATE" in name.upper() or "KEY" in name.upper()
                                  for name in actual):
            raise AssertionError("Reviewer handoff includes an unexpected name")
    info={
        "kind":kind,"schema":"chronohyper_authorized_key_free_reviewer_handoff_v1",
        "contents":sorted(actual),"n_rows":len(data),
        "worksheet_sha256":hashlib.sha256(content).hexdigest(),
        "rubric_sha256":hashlib.sha256(rules).hexdigest(),
        "zip_sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
        "evaluator_independence_verified":False,
        "permission_attested_by_cli_flag_only":True,
        "blind_mapping_not_embedded":True,
        "exterior_network_upload_performed":False,
    }
    receipt=destination.with_suffix(".receipt_LOCAL.json")
    receipt.write_text(json.dumps(info,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(destination),"reviewer_rows":len(data),
                      "files":sorted(actual),"contains_key":False,
                      "external_share_requires_permission":True},indent=2))
    return info

def validate_response(project=".",kind="label24",response=""):
    if not response: raise ValueError("Completed, actual reviewer response CSV required")
    root=Path(project).resolve()
    sp,original,_,headers,baseline=_input(root,kind)
    dest=Path(response)
    if not dest.is_absolute(): dest=root/dest
    h,received=rows(dest)
    if h!=headers: raise ValueError("Original columns or their order were changed")
    ref={v[sp["id"]]:v for v in baseline}
    if len(received)!=len(ref) or len({r[sp["id"]] for r in received})!=len(ref):
        raise ValueError("Missing, extra, duplicated case IDs")
    for r in received:
        item=ref.get(r[sp["id"]])
        if item is None or any(r.get(k)!=item.get(k) for k in sp["fixed"]):
            raise ValueError("Blind source columns were edited: "+str(r[sp["id"]]))
        if not str(r.get("reviewer_id","")).strip():
            raise ValueError("Missing actual reviewer_id: "+str(r[sp["id"]]))
        field="review_notes" if kind=="label24" else "evidence_notes"
        if not str(r.get(field,"")).strip():
            raise ValueError("Missing case-specific review notes: "+str(r[sp["id"]]))
        suff=str(r.get("evidence_sufficient_yes_no","")).strip().lower()
        if suff not in ("yes","no"):
            raise ValueError("Evidence sufficiency must be yes/no")
        if kind=="coherence48":
            rating=str(r.get("coherence_score_1_to_5","")).strip()
            if suff=="yes" and rating not in {"1","2","3","4","5"}:
                raise ValueError("Missing valid sufficient-evidence rating")
            if suff=="no" and rating:
                raise ValueError("Do not assign a confident score when insufficient")
        else:
            for part in ("A","B"):
                label=str(r.get(part+"_accuracy_accurate_vague_wrong","")).strip().lower()
                gloss=str(r.get(part+"_gloss_overclaim_yes_no_unclear","")).strip().lower()
                if suff=="yes" and label not in {"accurate","vague","wrong"}:
                    raise ValueError("Missing sufficient-evidence paired title grade")
                if gloss not in {"yes","no","unclear"}:
                    raise ValueError("Unknown gloss overclaim grade")
                if suff=="no" and gloss!="unclear":
                    raise ValueError("Insufficient-evidence gloss cannot be assigned a definite overclaim grade")
    result={
        "schema":"chronohyper_reviewer_response_integrity_v1",
        "kind":kind,"n_rows":len(received),"original_row_count_preserved":True,
        "blind_source_fields_unchanged":True,
        "response_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
        "identities_are_self_reported_not_independently_verified":True,
        "full_paper_entailment_independently_verified":False,
    }
    print(json.dumps(result,indent=2))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--pack",action="store_true",help="Generate a NO-KEY local ZIP (requires authorization flag)")
    group.add_argument("--validate",action="store_true",help="Validate completed reviewer CSV without unblinding")
    p.add_argument("--project",default=".")
    p.add_argument("--kind",choices=sorted(SPEC),required=True)
    p.add_argument("--authorized-share",action="store_true",
                   help="User verified permission from data owner and intended independent reviewer")
    p.add_argument("--out",default=None)
    p.add_argument("--response",default="")
    args=p.parse_args()
    if args.pack:
        prepare(args.project,args.kind,args.out,args.authorized_share)
    else:
        validate_response(args.project,args.kind,args.response)

if __name__=="__main__":
    main()
