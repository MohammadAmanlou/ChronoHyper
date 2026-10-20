# Independent evidence gate for Constructor CKL

> **Current state (20 October 2026):** The 24-pair V2/V3 and 48-row
> coherence sheets have **already** been returned and scored with AI
> identifiers/flags. See [ASSESSMENT_STATUS.md](ASSESSMENT_STATUS.md).
> Their same-corpus title/name-level judgments do not prove source-full-text
> scientific entailment or remove the requirement for externally grounded
> independent checks. The instructions below are the reusable protocol, not
> claims that these particular assessments remain wholly unstarted.


The source cohort is confidential. Do not upload employer-provided names, papers,
review packets or hidden keys to an external model or reviewer without permission.
Evidence-checking cannot turn previously inspected cases into a new test set.

## 1. Blind V2 versus V3 title audit

Only give an authorized, truly separated reviewer:
- local_only/reviews/label_v3_fresh/blind_v2_v3_24.csv
- local_only/reviews/label_v3_fresh/JUDGE_INSTRUCTIONS.txt

Never give the A/B mapping, old ratings, source methods, or prior results.
Require all 24 original rows, honest reviewer identity, scientific evidence
notes and explicit "unclear" when title-only evidence cannot support a claim.
Save completed ratings under local_only/reviews/label_v3_fresh/rated_24.csv.

Run:
    python -m research_lab.label_v3_blind --project . --score --ratings local_only/reviews/label_v3_fresh/rated_24.csv

Inspect result_LOCAL.json. This remains a same-corpus developmental result.

## 2. Blind 48-case coherence test

Only provide the authorized evaluator with blind_review_48.csv and
JUDGE_INSTRUCTIONS.txt from local_only/reviews/fresh_semantic/.
Never send condition_key_PRIVATE.csv. If packet missing, run:
    python -m research_lab.blind_paper_eval --project . --prepare

Save completed ratings as local_only/reviews/fresh_semantic/ratings_fresh_48.csv.
Run:
    python -m research_lab.blind_paper_eval --project . --score --ratings local_only/reviews/fresh_semantic/ratings_fresh_48.csv

Report evaluable pair count, uncertainty, reviewer type, and weak title-only
evidence limitation. Retain the independent constrained-shuffle p=0.69.

## 3. Full-text entailment and 36 Type-B source claims

Create a local working copy of
research_outputs/type_b_audit/CLAIM_LEVEL_REVIEW_BLANK.csv.
Review article *full text*, citations, cutoff, contrary evidence and claims.
Unavailable or ambiguous primary text must remain unclear. The resulting
source-claim entailment rate is not a generated-answer accuracy rate.

## 4. Fresh task-grounded evaluation

Have an authorized separated source construct new task questions and gold
before seeing search output. Keep gold away from index/ranking, freeze rankings
first, then score. Do not tune routing using those same test references.
Never treat original 14 Type-A or four Type-B questions as unseen again.

## Release checklist

P1/P2 nested budgets; P3 independent coherence with null and caveats;
P4 genuine high-order collapse; P5 tracked temporal evolution and uncertainty;
P6 faithful labels with measured overclaim denominator or NOT_EVALUATED;
one task-grounded evaluation; reproducible pinned tests; truthful, visually
checked 3-5-page PDF and complete AI_USAGE.md disclosure.

Passing source checks alone does not prove independent semantic correctness.


## Permission-gated key-free ZIP export and response validation (added 20 October)

The script `research_lab/review_handoff.py` **does not upload data or manufacture ratings**.
It refuses to make any private reviewer ZIP unless the operator explicitly
attests permission using `--authorized-share`. The flag records only an
operator assertion; it does **not** itself grant or verify the data owner's
permission. Do not send confidential Constructor information to a public AI
service or unauthorized person.

First check the source sheets exist under `local_only/reviews`. Do
not regenerate or overwrite a saved blind mapping unless its original sheet was
lost and the recovery is independently checked. With sharing permission,
the following commands create **ZIPs containing only worksheet + rubric +
scope disclaimer**, not mapping keys:


```powershell
.\.venv\Scripts\python.exe -m research_lab.review_handoff --pack --kind label24 --project . --authorized-share
.\.venv\Scripts\python.exe -m research_lab.review_handoff --pack --kind coherence48 --project . --authorized-share
Get-ChildItem .\local_only\reviewer_exports

```


Give each permitted evaluator only the ZIP for the relevant task. Ensure they
have no key, prior score, or decision logic; ask them to preserve every header,
row and source cell. A **truly independent new reviewer** must be a fresh
assessor with no old-key exposure, not this same chat.

After the completed real reviewer CSVs are returned, save to:

- `local_only/reviews/label_v3_fresh/rated_24.csv`
- `local_only/reviews/fresh_semantic/ratings_fresh_48.csv`

Then validate the unchanged evidence **without first unblinding**:


```powershell
.\.venv\Scripts\python.exe -m research_lab.review_handoff --validate --kind label24 --project . --response .\local_only\reviews\label_v3_fresh\rated_24.csv
.\.venv\Scripts\python.exe -m research_lab.review_handoff --validate --kind coherence48 --project . --response .\local_only\reviews\fresh_semantic\ratings_fresh_48.csv

```


If both pass, the two existing local scorers can read their local PRIVATE keys
and compute paired results. The validator checks the **form**, not the truth
of the reported reviewer identity, source accessibility, or scientific
entailment. If no authorized independent judgments exist, leave these gates
clearly **PENDING**; do not fill rows with guesses or AI-generated confidence
to make a scoring command pass.
