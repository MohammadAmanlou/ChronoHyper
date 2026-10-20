"""Fair development-only retrieval. Shared index, route before node scores, no gold in ranking."""
from __future__ import annotations
import argparse,csv,io,json,re,statistics,time
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from scipy.sparse import hstack,vstack,csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

def norm(s):return re.sub(r'[^a-z0-9]+','',str(s).lower())
TYPES={'method','dataset','technique','component','cited_work'}

def index(root,cutoff=2025):
    with ZipFile(root/'inputs/data.zip') as z:
        g=json.loads(z.read('data/tkh_collection10.json'))
        articles=list(csv.DictReader(io.StringIO(z.read('data/collection10_articles.csv').decode('utf-8-sig'))))
    papers={str(a['id']):a['title'] for a in articles if int(a['year'])<=cutoff}
    hierarchy=json.loads((root/f'outputs_selected/hierarchy_{cutoff}.json').read_text(encoding='utf-8'))
    ancestor={}
    for sn in hierarchy['supernodes']:
        if sn['level']==0:
            for v in sn['member_ids']:
                if v in ancestor:raise ValueError('Overlapping root')
                ancestor[v]=sn['id']
    aliases=defaultdict(list)
    for n in g['nodes']:
        if n['type'] in TYPES and n['first_seen_year']<=cutoff and norm(n['surface_form']):
            aliases[(n['type'],norm(n['surface_form']))].append(n)
    entries=[]
    for (typ,normalized),nodes in sorted(aliases.items()):
        roots=sorted({ancestor[n['id']] for n in nodes if n['id'] in ancestor})
        if not roots:continue
        titles=sorted({papers[str(aid)] for n in nodes for aid in n.get('provenance',{}).get('articles',[]) if str(aid) in papers})[:6]
        surface=sorted(n['surface_form'] for n in nodes)[0]
        entries.append({'type':typ,'name':surface,'normalized':normalized,'roots':roots,
                        'node_ids':sorted(n['id'] for n in nodes),
                        'text':(surface+' ')*3+typ+' '+' '.join(titles)})
    if not entries:raise ValueError('Empty entity index')
    corpus=[r['text'] for r in entries]
    word=TfidfVectorizer(ngram_range=(1,2),stop_words='english',sublinear_tf=True,strip_accents='unicode')
    char=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),sublinear_tf=True)
    X=normalize(hstack([word.fit_transform(corpus)*.7,char.fit_transform(corpus)*.3],format='csr'))
    roots=sorted({c for r in entries for c in r['roots']})
    groups={c:np.array([i for i,r in enumerate(entries) if c in r['roots']],dtype=int) for c in roots}
    t=time.perf_counter()
    centroids=normalize(vstack([csr_matrix(X[groups[c]].mean(axis=0)) for c in roots]))
    preprocessing_s=time.perf_counter()-t
    return entries,X,word,char,roots,groups,centroids,preprocessing_s

def top(scores,ix,entries,k=5):
    pairs=sorted(zip(ix,scores),key=lambda p:(-float(p[1]),entries[int(p[0])]['normalized'],entries[int(p[0])]['type']))
    return [{'name':entries[int(i)]['name'],'normalized':entries[int(i)]['normalized'],
             'type':entries[int(i)]['type'],'score':round(float(s),6)}
            for i,s in pairs[:k]]

def questions(root,custom=None):
    if custom:
        p=Path(custom)
        if not p.is_absolute():p=root/p
        with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
    with ZipFile(root/'inputs/data.zip') as z:
        return list(csv.DictReader(io.StringIO(z.read('data/questions.csv').decode('utf-8-sig')),delimiter=';'))

def rank(project='.',out='local_only/retrieval_v2/rankings.json',
         question_file=None,cutoff=2025,visit=4,repeats=3):
    root=Path(project)
    entries,X,word,char,roots,group,C,preprocessing=index(root,cutoff)
    qs=questions(root,question_file)
    output=[]
    for q in qs:
        if not q.get('question_id') or not q.get('question'):raise ValueError('question_id/question missing')
        Q=normalize(hstack([word.transform([q['question']])*.7,char.transform([q['question']])*.3],format='csr'))
        flat_ms=[];route_ms=[]
        for rep in range(repeats):
            start=time.perf_counter()
            f=(X@Q.T).toarray().ravel()
            flat_ms.append((time.perf_counter()-start)*1000)
            start=time.perf_counter()
            cs=(C@Q.T).toarray().ravel()
            chosen=sorted(range(len(roots)),key=lambda j:(-cs[j],roots[j]))[:visit]
            subset=np.unique(np.concatenate([group[roots[j]] for j in chosen]))
            h=(X[subset]@Q.T).toarray().ravel()
            route_ms.append((time.perf_counter()-start)*1000)
        output.append({'question_id':q['question_id'],'type':q.get('type',''),
                       'flat':top(f,np.arange(len(entries)),entries),
                       'hier':top(h,subset,entries),
                       'flat_dot_products':len(entries),'hier_dot_products':len(subset),
                       'centroid_dot_products':len(roots),
                       'flat_ms_median':statistics.median(flat_ms),
                       'hier_ms_median':statistics.median(route_ms)})
    artifact={'schema':'chronohyper_new_fair_ranker_development_v1','cutoff':cutoff,
              'n_canonical_entities':len(entries),'n_root_clusters':len(roots),
              'n_queries':len(output),'centroid_build_s':preprocessing,
              'gold_used_for_ranking':False,
              'freshness':'PREVIOUSLY_INSPECTED_EXPLORATORY' if question_file is None
                          else 'USER_SUPPLIED_NOT_AUTOMATICALLY_VERIFIED',
              'timing_scope':'centroid+subset included in hierarchy; index/offline cost separate; query vector transform shared and excluded',
              'results':output}
    p=Path(out)
    if not p.is_absolute():p=root/p
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
    print('Ranked',len(output),'questions with same scorer; flat actual docs',len(entries),
          '; median hier candidate docs',statistics.median(x['hier_dot_products'] for x in output))
    return artifact

def score(project='.',rankings='',references='',out='local_only/retrieval_v2/score.json'):
    root=Path(project)
    def path(v):
        p=Path(v);return p if p.is_absolute() else root/p
    x=json.loads(path(rankings).read_text(encoding='utf-8'))
    with path(references).open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    g={r['question_id']:{norm(t) for t in r['expected_methods'].split('|') if norm(t)} for r in rows}
    if len(g)!=len(rows):raise ValueError('Duplicate question ids')
    each=[]
    for q in x['results']:
        target=g.get(q['question_id'],set())
        if not target:continue
        hits={}
        for arm in ('flat','hier'):
            found={r['normalized'] for r in q[arm]}&target
            hits[arm]={'hit':int(bool(found)),'recall':len(found)/len(target)}
        each.append({'question_id':q['question_id'],**hits})
    if not each:raise ValueError('No matching reference rows')
    r={'n_evaluated':len(each),'freshness':x['freshness'],
       'flat_hit_at_5':statistics.mean(y['flat']['hit'] for y in each),
       'hier_hit_at_5':statistics.mean(y['hier']['hit'] for y in each),
       'flat_recall_at_5':statistics.mean(y['flat']['recall'] for y in each),
       'hier_recall_at_5':statistics.mean(y['hier']['recall'] for y in each),
       'independent_test_certified':False,
       'note':'Original questions or self-written gold are not automatically an independent benchmark.',
       'per_question':each}
    file=path(out);file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in r.items() if k!='per_question'},indent=2))
    return r

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--project',default='.')
    p.add_argument('--rank',action='store_true')
    p.add_argument('--score',action='store_true')
    p.add_argument('--questions',default=None)
    p.add_argument('--rankings',default='local_only/retrieval_v2/rankings.json')
    p.add_argument('--references',default=None)
    p.add_argument('--out',default='local_only/retrieval_v2/score.json')
    a=p.parse_args()
    if a.rank:rank(a.project,a.rankings,a.questions)
    elif a.score:
        if not a.references:p.error('--score requires a separately preserved --references CSV')
        score(a.project,a.rankings,a.references,a.out)
    else:p.error('Choose --rank or --score')
if __name__=='__main__':main()
