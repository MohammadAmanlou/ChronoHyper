#!/usr/bin/env python3
"""Read-only diagnostics for Constructor selected label annotation CSV.

Does not edit the source annotation file, hierarchy, labels, or scientific results.
Usage:
    python Constructor_Label_Review_Diagnostics.py --file outputs_selected/label_review_sheet.csv \
        --out outputs_selected/label_review_diagnostics.md
"""
import argparse
import csv
from collections import Counter
from pathlib import Path

CATEGORIES = {'accurate', 'vague', 'wrong'}
OVERCLAIM = {'yes', 'no', 'unclear'}
EVIDENCE = {'yes', 'no'}

def norm(v):
    return (v or '').strip().lower()

def clean_cell(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ').replace('\r', ' ').strip()

def create_report(src: Path, dst: Path):
    with src.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        expected = {'snapshot','level','stable_id','label','gloss',
            'label_rating_accurate_vague_wrong','gloss_overclaim_yes_no_unclear',
            'adequate_evidence_yes_no','reviewer_id','review_notes'}
        missing = expected - set(reader.fieldnames or [])
        if missing:
            raise ValueError('Missing CSV columns: ' + ', '.join(sorted(missing)))
    values = Counter(norm(row['label_rating_accurate_vague_wrong']) or '<blank>' for row in rows)
    claims = Counter(norm(row['gloss_overclaim_yes_no_unclear']) or '<blank>' for row in rows)
    n_binary = claims['yes']+claims['no']
    deficient = []
    for row_num, row in enumerate(rows, 2):
        errs = []
        rating = norm(row['label_rating_accurate_vague_wrong'])
        claim = norm(row['gloss_overclaim_yes_no_unclear'])
        evidence = norm(row['adequate_evidence_yes_no'])
        if rating not in CATEGORIES:
            errs.append('Invalid/missing label rating')
        elif rating in ('vague', 'wrong'):
            errs.append('Poor semantic label: ' + rating)
        if claim not in OVERCLAIM:
            errs.append('Invalid/missing gloss claim judgment')
        elif claim == 'unclear':
            errs.append('Overclaim judgment uncertain; resolve with evidence or keep as explicitly inconclusive')
        if evidence not in EVIDENCE:
            errs.append('Missing/invalid evidence adequacy judgment')
        elif evidence == 'no':
            errs.append('Evidence inadequate')
        if not norm(row['reviewer_id']):
            errs.append('Missing reviewer identity')
        if rating in ('wrong', 'vague') and not (row['review_notes'] or '').strip():
            errs.append('Missing reason for wrong/vague label')
        if errs:
            deficient.append((row_num, row, '; '.join(errs)))
    lines = [
        '# Constructor label review: diagnostic (READ ONLY)', '',
        '**Never interpret `0` overclaims over the 8 definite judgments as `0/48` or as perfect scientific accuracy.**', '',
        '## Current annotation totals', '',
        f'- Rows: **{len(rows)}**',
        f'- Title ratings: **{values["accurate"]} accurate / {values["vague"]} vague / {values["wrong"]} wrong**; invalid or blank: **{len(rows)-sum(values[k] for k in CATEGORIES)}**',
        f'- Gloss claims: **{claims["yes"]} yes / {claims["no"]} no / {claims["unclear"]} unclear**; blank/invalid: **{len(rows)-sum(claims[k] for k in OVERCLAIM)}**',
        f'- Binary gloss-claim evaluations: **{n_binary}/{len(rows)}**',
        f'- Unknown gloss-claim rate: **{claims["unclear"]}/{len(rows)}**; do NOT coerce inconclusive judgments to `no`',
        f'- Rows flagged for review or documentation: **{len(deficient)}**', '',
        '## Rows requiring review or documentation', '',
        '| Excel row | Snapshot | Level | Stable ID | Current label | Diagnostic |',
        '|---:|---:|---:|---|---|---|',
    ]
    for row_num, row, reason in deficient:
        lines.append('| ' + ' | '.join([
            str(row_num), clean_cell(row['snapshot']), clean_cell(row['level']),
            clean_cell(row['stable_id']), clean_cell(row['label']), clean_cell(reason)
        ]) + ' |')
    lines.extend(['', '## Correct follow-up', '',
        '1. Keep a timestamped original CSV as the baseline. Do not rerun the `make` generator over annotations.',
        '2. For all wrong/vague labels: record an evidence-backed reason in `review_notes`. Keep the original prediction unchanged for baseline evaluation.',
        '3. For each `unclear` gloss claim: verify the exact gloss against visible node/article evidence. Use `yes` or `no` only when supported; otherwise retain `unclear` and report low coverage.',
        '4. Make sure each judgment has a real `reviewer_id`, and the evidence adequacy field is filled. Do not fabricate independent/blind review.',
        '5. To improve T5, design and generate NEW automatic labels in a separate output version; compare them on the SAME 48 pre-specified clusters and with a fixed reviewer protocol.',
        '6. Rerun `selected_label_audit.py score --file outputs_selected/label_review_sheet.csv` and `final_preflight.py --project .`; update final report to distinguish title error, gloss overclaim and inconclusive judgments.', ''])
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote {dst}; n={len(rows)}, titles={values["accurate"]}/{values["vague"]}/{values["wrong"]}, gloss_yes={claims["yes"]}, gloss_no={claims["no"]}, gloss_unclear={claims["unclear"]}, flagged={len(deficient)}')
    return len(rows), values, claims

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--file',required=True)
    parser.add_argument('--out',default='outputs_selected/label_review_diagnostics.md')
    args=parser.parse_args()
    create_report(Path(args.file),Path(args.out))
if __name__ == '__main__':
    main()
