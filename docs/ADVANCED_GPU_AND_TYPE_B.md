# Advanced GPU retrieval and real Type-B answer evaluation

This is a **research extension** beyond the locked native_temporal_20
hypergraph hierarchy. See the original assignment in ASSIGNMENT_SOURCE.md.
No result is claimed until actually run. The 34 previously inspected new
questions are now DEVELOPMENT, not an untouched confirmatory benchmark.

## 1. Why the method may help

The original lexical index has about 2,647 canonical target entries with
names and paper titles but little explanatory language. This candidate
retriever adds original 2025-cutoff native hyperedge *co-mentions*
(not verified scientific relations), semantic BGE-M3 sentence embeddings,
character/word TF-IDF, rank-based reciprocal rank fusion, BGE-M3 neural
cross-encoder reranking, and a non-pruning soft root-aware ablation.

Models: https://huggingface.co/BAAI/bge-m3 and
https://huggingface.co/BAAI/bge-reranker-v2-m3 .
The paper/text source remains the original corpus; no external abstract is
silently substituted. GPU cost is reported separately from the legacy
dot-product measurements. The ranking stage never opens Gold.

## 2. Create a private Kaggle GPU bundle from Windows

~~~powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m unittest research_lab.test_advanced_retrieval -v
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_gpu_rank_only.ps1
~~~

**Kaggle ZIP format fix (22 October 2026):** The previous Windows
`Compress-Archive` produced member names with backslash separators,
which Kaggle rejects. The rank-only and Type-B PowerShell wrappers now
use Python `zipfile` with explicit POSIX `/` member paths and check
the archive against the exact allowed-file list. If an old ZIP exists,
preserve it under a legacy filename before rerunning:

~~~powershell
$old = ".\local_only\gpu_rank_only.zip"
if (Test-Path $old) {
    $backup = ".\local_only\gpu_rank_only_windows_legacy.zip"
    if (Test-Path $backup) { throw "Legacy backup already exists; choose another backup name" }
    Move-Item -LiteralPath $old -Destination $backup
}
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_gpu_rank_only.ps1

.\.venv\Scripts\python.exe -c "from zipfile import ZipFile; p='local_only/gpu_rank_only.zip'; z=ZipFile(p); print(z.namelist()); assert all(chr(92) not in n for n in z.namelist()); assert not any('gold_private' in n.lower() for n in z.namelist()); print('KAGGLE ZIP: PASS')"
~~~

Upload **only the new `gpu_rank_only.zip`** to the private Kaggle Dataset.
Do not upload the Windows legacy ZIP. The inner original `inputs/data.zip`
is retained as a legitimate source archive; its bytes were not modified.

This creates local_only/gpu_rank_only.zip. It includes ONLY the source data
ZIP, 2025 hierarchy, ranking queries, permitted code, and optional dependency
pins. It does NOT contain Gold, ratings, previous scored outcomes, or blind
mapping. Make the Kaggle Dataset **PRIVATE**; do not publish the Constructor
corpus accidentally. Enable GPU accelerator and Internet on the Kaggle
Notebook (or run on a local CUDA server).

Kaggle cell A: unpack the private input ZIP.

~~~python
import zipfile
from pathlib import Path
inputs=list(Path('/kaggle/input').rglob('gpu_rank_only.zip'))
assert len(inputs)==1, inputs
root=Path('/kaggle/working/chronohyper')
root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(inputs[0]) as f: f.extractall(root)
print(root)
~~~

Kaggle cell B: install optional research dependencies.

~~~python
import subprocess,sys
subprocess.run([sys.executable,'-m','pip','install','-q','-r',
                '/kaggle/working/chronohyper/requirements_advanced.txt'],
               check=True)
~~~

Kaggle cell C: run the new retriever (no Gold).

~~~python
subprocess.run([sys.executable,'-m','research_lab.advanced_retrieval',
 '--project','/kaggle/working/chronohyper','--rank','--device','cuda',
 '--questions','local_only/fresh_retrieval_screened34/queries_only.csv',
 '--out','local_only/advanced_retrieval',
 '--candidate-k','100','--rerank-k','64'],
 cwd='/kaggle/working/chronohyper',check=True)
~~~

Kaggle cell D: download only rankings.json.

~~~python
from IPython.display import FileLink,display
display(FileLink('/kaggle/working/chronohyper/local_only/advanced_retrieval/rankings.json'))
~~~

Put that JSON on Windows at local_only/advanced_retrieval/rankings.json.
Keep gold_PRIVATE.csv on Windows. Score locally after the ranking digest is
frozen:

~~~powershell
.\.venv\Scripts\python.exe -m research_lab.advanced_retrieval --project . --score
Get-Content .\local_only\advanced_retrieval\score_DEVELOPMENT_ONLY.json
~~~

Report lexical, dense, RRF, rerank and soft-hierarchy results, NOT only the
best arm. The test was already seen: all these numbers are developmental,
not confirmatory. A genuinely fresh and pre-frozen benchmark is required
after a final approach is selected, especially to establish any Hit@5 claim
above the frozen Flat 3/34 and Route-4 2/34.

### Kaggle automatically extracted the nested source ZIP

Kaggle's dataset import can recursively unpack `inputs/data.zip` into
`inputs/data/data/tkh_collection10.json` and
`inputs/data/data/collection10_articles.csv`. In that case the old
Kaggle cell requiring `inputs/data.zip` will fail even though the source
files exist. Do **not** upload the raw original `ground_truth.json` into
the ranker: that file is hidden benchmark gold. On an already uploaded
PRIVATE Kaggle dataset, stage only the exact ranking allowlist into
`/kaggle/working/chronohyper/`, then reconstruct `inputs/data.zip`
from only graph and article metadata:

~~~python
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil

base=Path('/kaggle/input/datasets/mohammadamanlou/gpu-rank-only')
root=Path('/kaggle/working/chronohyper')
files=[
 'research_lab/__init__.py',
 'research_lab/advanced_retrieval.py',
 'research_lab/retrieval_v2.py',
 'research_lab/retrieval_frontier.py',
 'outputs_selected/hierarchy_2025.json',
 'local_only/fresh_retrieval_screened34/queries_only.csv',
 'requirements_advanced.txt'
]
for rel in files:
 src=base/rel
 assert src.is_file(),src
 dst=root/rel
 dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src,dst)
source=base/'inputs/data/data'
inner=('tkh_collection10.json','collection10_articles.csv')
(root/'inputs').mkdir(parents=True,exist_ok=True)
with ZipFile(root/'inputs/data.zip','w',ZIP_DEFLATED) as z:
 for name in inner:
  assert (source/name).is_file(),name
  z.write(source/name,arcname='data/'+name)
with ZipFile(root/'inputs/data.zip') as z:
 assert set(z.namelist())=={'data/'+x for x in inner}
 assert 'data/ground_truth.json' not in z.namelist()
print('READY:',root)
~~~

For **future** bundles, `scripts/make_gpu_zip.py` now strips
`ground_truth.json` from the **nested** source ZIP (not only the outer
allowlist). The current imported Kaggle Dataset still has a separate
copy if uploaded before this correction; keep it PRIVATE and replace
it with a newly sanitized version before sharing or publishing. This
staging step is a practical no-gold data-access boundary for the rank
process, not a claim the old Kaggle Dataset never held gold.

## 3. Actually generate Type-B answers from scientific papers

Type-B is **not** measured by the earlier 36 claim-source judgments. Actual
answers to the four original (previously seen) questions must be produced
and then scored separately.

Start on Windows from repo root:

~~~powershell
.\.venv\Scripts\python.exe -m unittest research_lab.test_type_b_answer_generation -v
.\.venv\Scripts\python.exe -m research_lab.type_b_answer_generation --project . --prepare
explorer .\local_only\type_b_generation
~~~

This creates SOURCE_PASSAGES_TO_FILL.csv (every original eligible 2025
source paper ID/title/year is frozen) and type_b_questions_readonly.json.

Give ONLY those two files to another authorized research-enabled AI chat;
ask it to inspect actual dated PRIMARY publication full text and fill
source_url, source_version_date (YYYY-MM-DD at latest 2025-12-31),
passage_locator, passage_text (accurate relevant original passage),
evidence_access = FULL_TEXT for actually inspected sources. Leave rows
without authenticated passages empty. NEVER invent scientific quotes,
assume an abstract equals full text, change original paper IDs, or
disclose ground_truth.json / previous answer review as a shortcut.
The original date restriction is conservative and deliberately excludes
January/February 2026 versions, even if some could satisfy a broader
question-specific cutoff.

Once the worksheet has REAL verified full-text passages, use a CUDA server
or a separate private Kaggle session with the same repo and permitted
passages. Install requirements_advanced.txt and run:

~~~bash
python -m research_lab.type_b_answer_generation --project . --generate
~~~

The local pretrained Qwen/Qwen2.5-3B-Instruct model writes four actual
answers, each citing supplied [SOURCE paper_id], in
local_only/type_b_generation/GENERATED_ANSWERS_PRIVATE.csv. Unsupported
subclaims must explicitly receive INSUFFICIENT_EVIDENCE. A separate
BLIND_ANSWER_REVIEW.csv contains the question, generated answer, and the
exact supporting passages, with empty fields for correctness, completeness,
citation faithfulness and original-question coverage.

Have an **isolated different AI reviewer** inspect the 4 answers and full
primary evidence, fill EVERY yes/no/unclear column, record the actual model
identifier, and give case-specific reasoning. Do not call it a human review.
Save as BLIND_ANSWER_REVIEW_RATED_AI.csv and run:

~~~powershell
.\.venv\Scripts\python.exe -m research_lab.type_b_answer_generation --project . --score --ratings .\local_only\type_b_generation\BLIND_ANSWER_REVIEW_RATED_AI.csv
Get-Content .\local_only\type_b_generation\type_b_answer_score_LOCAL.json
~~~

Until actual source passages, generated answers and independent AI ratings
exist, Type-B **GENERATED ANSWER ACCURACY IS NOT MEASURED**.


### Kaggle option for the actual Type-B generator

After the factual source passage worksheet has been completed, checked and
approved, create a separate PRIVATE upload zip on Windows:

~~~powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_gpu_type_b_private.ps1
~~~

This source-only bundle is intentionally different from the retrieval bundle
and includes real full-text excerpts. Keep it private and permitted by the
article owners' terms. Attach gpu_type_b_private.zip to a separate Kaggle
GPU notebook. Run:

~~~python
from pathlib import Path
import zipfile,subprocess,sys
zips=list(Path('/kaggle/input').rglob('gpu_type_b_private.zip'))
assert len(zips)==1,zips
root=Path('/kaggle/working/type_b')
root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(zips[0]) as z:z.extractall(root)
subprocess.run([sys.executable,'-m','pip','install','-q','-r',
                str(root/'requirements_advanced.txt')],check=True)
subprocess.run([sys.executable,'-m','research_lab.type_b_answer_generation',
                '--project',str(root),'--generate'],cwd=str(root),check=True)
~~~

Download these **three** outputs and put them in your Windows repo at
local_only/type_b_generation:

~~~python
from IPython.display import FileLink,display
for name in ('GENERATED_ANSWERS_PRIVATE.csv','BLIND_ANSWER_REVIEW.csv',
             'generation_manifest.json'):
    display(FileLink('/kaggle/working/type_b/local_only/type_b_generation/'+name))
~~~

No correctness claim exists until a separate AI has actually rated the
answers against original source passages and the original questions.

## 4. What is necessary for the Constructor evaluation

A much larger model does not repair missing source evidence or circularity.
Strong results require full-paper independent label/coherence reviews,
a real question-grounded evaluation, and an untouched holdout AFTER the
retrieval approach is frozen. Keep original negative evidence, including
degree/arity structural null p≈0.69, worse source-held-out cut, low Hit@5,
and two prospective pre-rank source failures. Do not retune the locked
hypergraph or silently relabel the inspected 34 questions as test.


## First actual BGE GPU score and follow-up (22 October 2026)

Observed 22 October GPU result (34 already-inspected questions; post-hoc development only): BGE-M3 dense Hit@5=10/34 (29.41%, MRR@5=0.1887); new lexical=4/34, hybrid RRF=6/34, neural reranker=1/34, and reranker+soft root=1/34. Previous separately frozen Flat=3/34 and route4=2/34 remain unchanged. No improved independent-test accuracy, no Type-B generated-answer accuracy and no significant generalization claim.

The neural reranker severely degraded exact-entity retrieval. A read-only, SHA-verifying post-hoc diagnostic is implemented in research_lab/posthoc_retrieval_diagnostics.py. It examines all 34 source-qualified queries, Gold only after ranking verification, dense wins lost by fusion/reranking, known top-20 visibility, and fixed post-hoc score-free allocations. Candidate@64 recall cannot be reconstructed from top-20 exports; no new GPU run or model retuning occurred in this update.

To run (on Windows, from repo root):

    git pull --ff-only origin main
    .\.venv\Scripts\python.exe -m unittest research_lab.test_posthoc_retrieval_diagnostics -v
    .\.venv\Scripts\python.exe -m research_lab.posthoc_retrieval_diagnostics --project .

Read local_only/advanced_retrieval/posthoc_error_audit_LOCAL.json and preserve it under ignored local_only. It is an error analysis, NOT a held-out test. Freeze the selected dense-only approach before evaluating on separately authored new questions.


## Follow-up: multi-view BGE-M3 candidate coverage on the same 34 queries

The post-hoc failure audit found Dense 10/34 Hit@5, Dense 14/34
Top-20 visibility, rerank demotion of seven correct answers and three
other dense successes missing from the exported reranker Top-20.
It cannot determine rerank candidate@64 recall.

A NEW isolated multiview_dense development module indexes three
evidence-bound views of each canonical entity: original long native
co-mention context, canonical name plus type, and recorded dated
paper titles. It reports 5 arms: context, name, paper, equal-weight
3-view RRF and 3-view maximum cosine. Each exports top-100, permitting
real Recall/Hit@5,10,20,50,100 diagnosis. This is DEVELOPMENT,
not a fresh untouched validation. No neural reranker is used, and no
new definitions or source abstracts are fabricated.

### Windows: create a private and Gold-free rank-only ZIP

~~~powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main

.\.venv\Scripts\python.exe -m unittest research_lab.test_multiview_dense -v

powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_gpu_rank_only.ps1 -Output "local_only\gpu_rank_multiview.zip"

.\.venv\Scripts\python.exe -c "from zipfile import ZipFile; import io; z=ZipFile('local_only/gpu_rank_multiview.zip'); assert 'research_lab/multiview_dense.py' in z.namelist(); sub=ZipFile(io.BytesIO(z.read('inputs/data.zip'))); assert 'data/ground_truth.json' not in sub.namelist(); print('PRIVATE MULTIVIEW ZIP OK')"
~~~

Upload the new gpu_rank_multiview.zip as a NEW PRIVATE Kaggle
Dataset. Keep the older Kaggle Dataset PRIVATE: its original import
may have contained recursively extracted ground_truth.json.

### Kaggle GPU notebook: stage source files and rank without Gold

Attach the NEW private Dataset; Kaggle can unpack nested ZIPs.
Run this single cell with GPU and Internet access enabled:

~~~python
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil, subprocess, sys

found=list(Path('/kaggle/input').rglob('multiview_dense.py'))
assert len(found)==1, f'Attach exactly one new private multiview Dataset: {found}'
base=found[0].parent.parent
root=Path('/kaggle/working/chronohyper_multiview')
required=[
 'research_lab/__init__.py','research_lab/advanced_retrieval.py',
 'research_lab/multiview_dense.py','research_lab/retrieval_v2.py',
 'research_lab/retrieval_frontier.py','outputs_selected/hierarchy_2025.json',
 'local_only/fresh_retrieval_screened34/queries_only.csv',
 'requirements_advanced.txt'
]
for rel in required:
    src=base/rel
    assert src.is_file(),str(src)
    dst=root/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
(root/'inputs').mkdir(parents=True,exist_ok=True)
inner=base/'inputs/data.zip'
if inner.is_file():
    with ZipFile(inner) as z:
        assert set(z.namelist())=={
          'data/tkh_collection10.json','data/collection10_articles.csv'}
    shutil.copy2(inner,root/'inputs/data.zip')
else:
    nested=base/'inputs/data/data'
    with ZipFile(root/'inputs/data.zip','w',ZIP_DEFLATED) as z:
        for name in ('tkh_collection10.json','collection10_articles.csv'):
            assert (nested/name).is_file(),str(nested/name)
            z.write(nested/name,arcname='data/'+name)
subprocess.run([sys.executable,'-m','pip','install','-q','-r',
                str(root/'requirements_advanced.txt')],check=True)
subprocess.run([sys.executable,'-m','research_lab.multiview_dense',
 '--project',str(root),'--rank','--device','cuda',
 '--out','local_only/multiview_dense_development'],
 cwd=root,check=True)
~~~

Download only the new gold-blind ranking file:

~~~python
from IPython.display import FileLink,display
display(FileLink('/kaggle/working/chronohyper_multiview/'
                 'local_only/multiview_dense_development/rankings.json'))
~~~

### Windows: score after returning from Kaggle

Save new Kaggle rankings.json in a separate ignored folder, NOT in the
original advanced_retrieval directory.

~~~powershell
New-Item -ItemType Directory -Force .\local_only\multiview_dense_development

Copy-Item "$env:USERPROFILE\Downloads\rankings.json" ".\local_only\multiview_dense_development\rankings.json"

.\.venv\Scripts\python.exe -m research_lab.multiview_dense --project . --score

Get-Content ".\local_only\multiview_dense_development\score_DEVELOPMENT_ONLY.json"
~~~

The scorer checks the frozen ranking digest, exact all-34 ID coverage,
and SHA of the original local question texts BEFORE opening private
Gold. All detailed judgments remain under ignored local_only.
Do not reclassify these development numbers as unseen test accuracy:
a new source-verified, independently authored and frozen question set
is required after choosing a final retrieval architecture.


## Follow-up to real 34-case multi-view scores (23 October 2026)

The applicant's new SHA-verified multiview rank is
\`88f536d78e9e408f526d08bc079111cdd32db76ce13744b0f318c400341c13cd\`.
The identical previously inspected 34 questions gave:

| View | Hit@5 | Hit@20 | Hit@50 | Hit@100 |
|---|---:|---:|---:|---:|
| BGE original context | 10 | 14 | 20 | 25 |
| Canonical entity name+type | 6 | 14 | 17 | 21 |
| Original dated source paper titles | 10 | 15 | 20 | 24 |
| Equal-weight three-view RRF | 10 | 16 | 21 | 26 |
| Max cosine of three views | 10 | 15 | 21 | 26 |

The considerable RRF@100 coverage, but no improvement in RRF@5,
shows a significant difference between *candidate existence* and
top-five ranking. It DOES NOT establish 26/34 attainable Hit@5.
The previous model-agnostic 2025 dated source has not been
revalidated for full-text entailment. These are **post-hoc
development** metrics, not a second independent benchmark.

### CPU read-only source-union and fixed-pool audit

A new module computes (a) how often the correct candidate appears
in **any** previously exported view, at the original ranks, and
(b) recoverability in a **gold-blind predetermined round-robin pool**
of 100/200/300 candidates, deduplicating typed identities.
It uses only the already frozen rankings and prior score, and
NEVER opens the hidden reference Gold directly. "Best across
views" is an oracle upper bound requiring access to the correct
answer; it is **not a deployable retrieval policy**. The fixed pool
recall is NOT Hit@5.

Run on Windows where your existing two JSON files already are:

~~~powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main

.\.venv\Scripts\python.exe -m unittest research_lab.test_multiview_source_union_audit -v

.\.venv\Scripts\python.exe -m research_lab.multiview_source_union_audit --project .

(Get-Content ".\local_only\multiview_dense_development\multiview_source_union_audit_LOCAL.json" -Raw | ConvertFrom-Json) |
    Select-Object -ExpandProperty fixed_gold_blind_3view_round_robin_pool_RECALL_upper_k
~~~

The complete local output also identifies all absent candidates,
union-at-5/20/100 oracle coverage and per-query rank movement.
A new confirmatory benchmark **must** be authored/frozen before
any model selected from the same 34 queries is described as a
generalization improvement.

### Next OPTIONAL GPU model: Qwen3 entity-specific reranker

A different research-only experiment already exists in
\`research_lab/qwen_entity_rerank.py\`. It is a checkpointed
\`Qwen/Qwen3-Reranker-0.6B\` scorer with an instruction to choose the
SPECIFIC scientific entity answering the question, not generic
topic similarity, over a gold-blind union of source-view candidates.
It compares direct Qwen, dense-anchored safety variants and
two unchanged BGE baselines. It is still **post-hoc
development only**, and could also hurt quality.
The model does not have externally verified full-text descriptions,
so it cannot substitute for factual answer evaluation.

Qwen3-Reranker in Sentence Transformers requires a new enough
\`CrossEncoder\` implementation. The Qwen packaging now includes
\`requirements_qwen_rerank.txt\` pinning \`sentence-transformers==5.4.0\`;
the older BGE dependency file remains untouched.
The official model card documents this CrossEncoder usage:
https://huggingface.co/Qwen/Qwen3-Reranker-0.6B.

To create a fresh PRIVATE inference-only bundle on Windows:

~~~powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_gpu_qwen_rerank.ps1
~~~

It packages source graph and titles, question text, Qwen Python code,
and the already frozen previous multiview RANKINGS ONLY,
not hidden Gold, score files or reviewer answers.
Unlike a dense embedding model, a cross-encoder scores each
question-candidate pair; a 300-candidate budget over 34
questions entails up to 10,200 pair evaluations. GPU availability,
model memory, runtime and actual accuracy have not been verified.

In Kaggle attach the NEW private reranker Dataset, enable GPU and
Internet, then use the following notebook cell. Kaggle may
recursively unpack the nested input ZIP:

~~~python
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil, subprocess, sys

mods=list(Path('/kaggle/input').rglob('qwen_entity_rerank.py'))
assert len(mods)==1, f'Attach exactly one Qwen3 PRIVATE source Dataset: {mods}'
base=mods[0].parent.parent
root=Path('/kaggle/working/chronohyper_qwen')
keep=[
 'research_lab/__init__.py',
 'research_lab/qwen_entity_rerank.py',
 'research_lab/advanced_retrieval.py',
 'research_lab/retrieval_v2.py',
 'research_lab/retrieval_frontier.py',
 'outputs_selected/hierarchy_2025.json',
 'local_only/fresh_retrieval_screened34/queries_only.csv',
 'local_only/multiview_dense_development/rankings.json',
 'requirements_qwen_rerank.txt',
]
for rel in keep:
    src=base/rel
    assert src.is_file(), src
    dst=root/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
(root/'inputs').mkdir(parents=True,exist_ok=True)
sourcezip=base/'inputs/data.zip'
if sourcezip.is_file():
    with ZipFile(sourcezip) as z:
        assert set(z.namelist())=={
          'data/tkh_collection10.json','data/collection10_articles.csv'}
    shutil.copy2(sourcezip,root/'inputs/data.zip')
else:
    unpacked=base/'inputs/data/data'
    with ZipFile(root/'inputs/data.zip','w',ZIP_DEFLATED) as z:
        for filename in ('tkh_collection10.json','collection10_articles.csv'):
            src=unpacked/filename
            assert src.is_file(), src
            z.write(src,arcname='data/'+filename)

import torch
assert torch.cuda.is_available(), 'Enable GPU in Kaggle settings'
subprocess.run([sys.executable,'-m','pip','install','-q','-r',
                str(root/'requirements_qwen_rerank.txt')],check=True)

subprocess.run([
 sys.executable,'-m','research_lab.qwen_entity_rerank',
 '--project',str(root),'--rank','--device','cuda',
 '--model','Qwen/Qwen3-Reranker-0.6B',
 '--batch-size','4','--max-candidates','300',
],cwd=root,check=True)
~~~

If interrupted, rerun the same command against the same writable
Kaggle Working directory: checkpoint_GOLD_BLIND.json is used
without overwriting completed query results. A new Kaggle session
does not automatically inherit prior Working files; restore its
checkpoint privately before resuming if needed.

Download **only** the new
\`local_only/qwen_entity_rerank_development/rankings.json\` from Kaggle,
place it locally into a NEW
\`local_only/qwen_entity_rerank_development\` folder, and score:

~~~powershell
.\.venv\Scripts\python.exe -m research_lab.qwen_entity_rerank --project . --score
Get-Content ".\local_only\qwen_entity_rerank_development\score_DEVELOPMENT_ONLY.json"
~~~

Do not choose the winning policy solely from these 34 known queries
then claim it was confirmed on them.


### Qwen candidate-policy correction (23 October 2026)

Important update: use the CURRENT Qwen code from GitHub, not the original five-source
candidate policy described above. The current ranker now uses the **entire**
top-100 lists from context, name, and paper, in fixed round-robin order,
without dropping Name depth 51–100. RRF and max-cosine are composites,
not new independent source representations. The source-view union
contains 175–248 distinct candidates per question (mean 208.94).
This fixes loss of some legitimate candidates before a reranker sees them.

The local CPU-only preflight checks source/query integrity and computes
actual Qwen pool recall using the already-scored DEVELOPMENT ranks,
without reading the reference Gold file itself:

~~~powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m unittest research_lab.test_qwen_candidate_preflight -v
.\.venv\Scripts\python.exe -m research_lab.qwen_candidate_preflight --project .
~~~

Expected prior-sample source-union candidate recall: **29/34**.
This is ONLY candidate coverage, never Qwen Hit@5 or fresh test accuracy.
Read the new private output at
`local_only/qwen_entity_rerank_development/candidate_preflight_LOCAL_PRIVATE.json`.
If the preflight disagrees or source hashes differ, do not run Qwen.
The source-ranked algorithm was changed **before Qwen inference**,
but after the original 34-question scores were visible; it is post-hoc.

The optional GPU commands further up remain usable after passing this gate.
The private Kaggle package excludes every Gold, score and reviewer file.
