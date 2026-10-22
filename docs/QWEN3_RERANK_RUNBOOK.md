# Qwen3 entity reranking: private GPU experiment (POST-HOC only)

## Current evidence

The original 34-question BGE-M3 Multi-View experiment scored 10/34
for each of Context, Paper, RRF and Max-Cosine at Hit@5, and
6/34 for Name. At Top-100, RRF and Max-Cosine each reached 26/34.
This is a good reason to try improved reranking, but NOT a guarantee
of higher top-five accuracy. A previous BGE reranker degraded Hit@5.

A new isolated experiment tests Qwen/Qwen3-Reranker-0.6B with
a custom instruction to select the exact scientific entity
answering the question, rather than a broadly related entity.
Official model: https://huggingface.co/Qwen/Qwen3-Reranker-0.6B

The rank stage reads only the frozen original BGE rankings,
frozen 34 query texts, original year-cut graph and dated article
titles. Gold, old scores and reviewer votes are excluded. The
candidate pool is a gold-blind round-robin union of up to 300
candidates from the source five top-100 lists (Name first 50).
Three reranked arms (raw, anchor first 1 Context result, anchor
first 2 Context results) are compared with untouched Context/RRF.
All resulting scores on these inspected 34 are DEVELOPMENT ONLY.

## Step 1: Windows private rerank package

~~~powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m unittest research_lab.test_qwen_entity_rerank -v
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_gpu_qwen_rerank.ps1
~~~

Output: local_only/gpu_qwen_entity_rerank_private.zip.
The ZIP includes the multiview gold-blind rankings but NEVER
ground_truth.json or any previous scored output. Upload as a
NEW PRIVATE Kaggle Dataset and attach it to a GPU notebook.

## Step 2: Kaggle notebook, reconstruct files and run GPU rerank

~~~python
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import shutil,subprocess,sys,torch

p=list(Path('/kaggle/input').rglob('qwen_entity_rerank.py'))
assert len(p)==1, ('Attach exactly one new private dataset',p)
base=p[0].parent.parent
root=Path('/kaggle/working/chronohyper_qwen_rerank')
required=[
'research_lab/__init__.py','research_lab/qwen_entity_rerank.py',
'research_lab/advanced_retrieval.py','research_lab/retrieval_v2.py',
'research_lab/retrieval_frontier.py','outputs_selected/hierarchy_2025.json',
'local_only/fresh_retrieval_screened34/queries_only.csv',
'local_only/multiview_dense_development/rankings.json',
'requirements_advanced.txt'
]
for rel in required:
 src=base/rel
 assert src.is_file(),src
 dst=root/rel
 dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src,dst)
(root/'inputs').mkdir(parents=True,exist_ok=True)
srczip=base/'inputs/data.zip'
allowed={'data/tkh_collection10.json','data/collection10_articles.csv'}
if srczip.is_file():
 with ZipFile(srczip) as z:assert set(z.namelist())==allowed
 shutil.copy2(srczip,root/'inputs/data.zip')
else:
 folder=base/'inputs/data/data'
 with ZipFile(root/'inputs/data.zip','w',ZIP_DEFLATED) as z:
  for name in ('tkh_collection10.json','collection10_articles.csv'):
   assert (folder/name).is_file()
   z.write(folder/name,arcname='data/'+name)
with ZipFile(root/'inputs/data.zip') as z:
 assert set(z.namelist())==allowed
 assert 'data/ground_truth.json' not in z.namelist()

assert torch.cuda.is_available(),'Enable GPU in Kaggle notebook settings'
print('GPU:',torch.cuda.get_device_name(0))
subprocess.run([sys.executable,'-m','pip','install','-q','-r',
 str(root/'requirements_advanced.txt')],check=True)
subprocess.run([sys.executable,'-m','research_lab.qwen_entity_rerank',
 '--project',str(root),'--rank','--device','cuda',
 '--model','Qwen/Qwen3-Reranker-0.6B','--batch-size','4',
 '--max-length','512','--max-candidates','300'],
 cwd=root,check=True)
~~~

If disconnected, run the LAST subprocess call again in the SAME
working directory. Gold-blind completed questions are checkpointed.

## Step 3: Kaggle output download

~~~python
from IPython.display import display,FileLink
display(FileLink(
'/kaggle/working/chronohyper_qwen_rerank/'
'local_only/qwen_entity_rerank_development/rankings.json'))
~~~

## Step 4: Windows independent score

Save the new downloaded rankings.json in a separate local folder:

~~~powershell
cd C:\Users\a\Desktop\constructor-ckl-research
New-Item -ItemType Directory -Force .\local_only\qwen_entity_rerank_development
Copy-Item "$env:USERPROFILE\Downloads\rankings.json" ".\local_only\qwen_entity_rerank_development\rankings.json"
.\.venv\Scripts\python.exe -m research_lab.qwen_entity_rerank --project . --score
Get-Content ".\local_only\qwen_entity_rerank_development\score_DEVELOPMENT_ONLY.json"
~~~

The scorer validates source-rank SHA, new-rank SHA, complete 34
question IDs and all five arms. It reports Hit@1/5/10/20/100 and
MRR@5. These are POST-HOC development scores on ALREADY INSPECTED
questions. Only an independently authored, primary-source-verified
and previously unseen frozen test can confirm a generalization claim.
