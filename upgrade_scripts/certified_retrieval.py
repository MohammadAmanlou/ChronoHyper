"""Independent EXACT hierarchical sparse TF-IDF retrieval audit.
Does not use Constructor ground truth for ranking or choose any hyperparameter from answers.
Unlike centroid-routing, computed cluster upper bounds provably dominate all leaf scores.
This preserves flat top-k, and measures online wall time and number of leaf dot products.
Run from repository root: python upgrade_scripts/certified_retrieval.py ...
"""
import argparse, csv, heapq, json, time, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().resolve()))
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from src.t1_audit import parse_archive
from src.retrieval import candidate_texts
from src.run import snapshot_raw

TYPES={'method','dataset','technique','component','cited_work'}

def load_context(root, year):
    graph,articles,questions,gold=parse_archive(str(root/'inputs/data.zip'))
    snap=snapshot_raw(graph,year)
    held=set(json.loads((root/'outputs/evaluation_split.json').read_text(encoding='utf-8'))['heldout_provenance_article_ids'])
    train=[e for e in snap['hyperedges'] if str(e.get('provenance',{}).get('article_id','?')) not in held]
    nodes=snap['nodes']
    texts=candidate_texts(nodes,train,articles)
    vec=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,strip_accents='unicode',max_features=40000,stop_words='english')
    M=vec.fit_transform(texts).tocsr()
    allowed={n['id']:i for i,n in enumerate(nodes) if n['type'] in TYPES}
    h=json.loads((root/f'outputs/hierarchy_{year}.json').read_text(encoding='utf-8'))
    supers={s['id']:s for s in h['supernodes'] if s['level']<=2}
    child=defaultdict(list)
    for ident,obj in supers.items():
        if obj['level']>0:
            parent=obj['parent_id']
            if parent not in supers:raise ValueError('Hierarchy parent missing: '+str(parent))
            child[parent].append(ident)
    entries={key:sorted(allowed[v] for v in s['member_ids'] if v in allowed) for key,s in supers.items()}
    roots=[key for key,s in supers.items() if s['level']==0 and entries[key]]
    assert len(set(i for k in roots for i in entries[k])) == len(allowed)
    assert sum(len(entries[k]) for k in roots)==len(allowed),'Non-disjoint root candidate sets'
    for parent,children in child.items():
        if entries[parent] and children:
            union=[i for c in children for i in entries[c]]
            if sorted(union)!=entries[parent]:raise ValueError('Hierarchy children mismatch: '+parent)
    from scipy.sparse import csr_matrix
    ub={key:csr_matrix(M[index].max(axis=0)) for key,index in entries.items() if index}
    return nodes,questions,gold,vec,M,allowed,supers,entries,roots,child,ub

def flat_topk(M,q,all_ids,nodes,k):
    t=time.perf_counter()
    s=np.asarray((M[list(all_ids)]@q.T).toarray()).ravel()
    ids=sorted(zip(all_ids,s),key=lambda x:(-float(x[1]),nodes[x[0]]['id']))[:k]
    return ids,time.perf_counter()-t

def certified_topk(M,q,nodes,supers,entries,roots,child,ub,k):
    """Admissible branch-and-bound: q, M >= 0 so cluster max feature dominates score.
    Expand top clusters, then children, then exact leaf scores. Prune strictly below kth
    score to preserve deterministic ties. This bounds candidate scoring, NOT all work.
    """
    begin=time.perf_counter()
    def score_upper(group):return float(ub[group].multiply(q).sum())
    queue=[]
    for root in roots:heapq.heappush(queue,(-score_upper(root),'group',root))
    retained=[]; scored=0; group_expanded=0
    while queue:
        max_bound=-queue[0][0]
        if len(retained)==k and max_bound < retained[-1][1]-1e-10:break
        neg,key_type,obj=heapq.heappop(queue)
        if key_type=='leaf':
            ix=obj; value=-neg
            retained.append((ix,value))
            retained.sort(key=lambda x:(-x[1],nodes[x[0]]['id']))
            if len(retained)>k:retained.pop()
        else:
            group_expanded+=1
            sons=[c for c in child.get(obj,[]) if c in entries and entries[c]]
            if sons:
                for c in sons:heapq.heappush(queue,(-score_upper(c),'group',c))
            else:
                for ix in entries[obj]:
                    # single leaf nonnegative score bounded by its parent group's upper bound
                    heapq.heappush(queue,(-float(M[ix].multiply(q).sum()),'leaf',ix))
                    # NOTE precomputing leaf scores is part of candidate score cost.
                    scored+=1
    return retained,time.perf_counter()-begin,scored,group_expanded

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',default='.')
    parser.add_argument('--out',default='outputs/certified_retrieval_audit.json')
    parser.add_argument('--year',type=int,default=2025)
    parser.add_argument('--top-k',type=int,default=5)
    args=parser.parse_args()
    root=Path(args.project).resolve()
    nodes,questions,gold,vectorizer,M,allowed,supers,entries,roots,child,ub=load_context(root,args.year)
    scored_rows=[]
    for rec in questions:
        query=vectorizer.transform([rec['question']]).tocsr()
        f,flat_seconds=flat_topk(M,query,list(allowed.values()),nodes,args.top_k)
        h,hier_seconds,scored,expanded=certified_topk(M,query,nodes,supers,entries,roots,child,ub,args.top_k)
        fi=[nodes[ix]['id'] for ix,_ in f]; hi=[nodes[ix]['id'] for ix,_ in h]
        if fi!=hi:
            raise AssertionError(f"EXACTness failed question={rec['question_id']}: {fi} != {hi}")
        scored_rows.append({'qid':rec['question_id'],'query_type':rec['type'],'exact_equal':True,
                'flat_topk_node_ids':fi,'certified_topk_node_ids':hi,
                'flat_candidate_count':len(allowed),'hier_leaf_scores_accounted':scored,
                'hier_groups_expanded':expanded,'flat_query_seconds':flat_seconds,
                'hier_query_seconds':hier_seconds})
    report={'audit_type':'exact sparse TF-IDF search, hierarchy with componentwise cluster upper bounds',
            'status':'VERIFIED_EXACT_TOPK' if all(x['exact_equal'] for x in scored_rows) else 'FAILED',
            'n_queries':len(scored_rows),'n_candidates':len(allowed),
            'mean_flat_seconds':float(np.mean([x['flat_query_seconds'] for x in scored_rows])),
            'mean_hierarchy_seconds':float(np.mean([x['hier_query_seconds'] for x in scored_rows])),
            'mean_hierarchy_leaf_scores_accounted':float(np.mean([x['hier_leaf_scores_accounted'] for x in scored_rows])),
            'caveat':'Same underlying flat ranking => Hit@K identical BY DESIGN, not an accuracy gain; report runtime/overhead fully. Hier leaf scores may be precomputed and therefore counted, including bounds/preprocessing. Does not establish superiority until measured faster end-to-end.',
            'ground_truth_used_for_ranking':False,'queries':scored_rows}
    path=root/args.out;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='queries'},indent=2))
    print('AUDIT FILE',path)

if __name__=='__main__':main()
