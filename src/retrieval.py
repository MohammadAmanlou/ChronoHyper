"""Exploratory Constructor benchmark questions, inspected during development. Gold is used only for final scoring.
Ranking features use only exported node/edge/public article titles, not reference answers.
"""
from __future__ import annotations
from collections import defaultdict
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


def normalize_name(s):
    return re.sub(r'[^a-z0-9]+','',str(s).lower())


def candidate_texts(nodes,edges,articles):
    nodes_by_id={n['id']:n for n in nodes}
    connected=defaultdict(list)
    for e in edges:
        if len(e['members'])>70:continue
        for v in e['members']:
            if nodes_by_id[v]['type'] in ('method','dataset','technique','component','cited_work'):
                # limit context: no extraction from ground truth, all from current snapshot
                for w in e['members']:
                    if v!=w and nodes_by_id[w]['type'] in ('task','problem','article','metric','dataset','method'):
                        connected[v].append(nodes_by_id[w]['surface_form'])
    aid={str(a['id']):a['title'] for a in articles}
    txt=[]
    for n in nodes:
        titles=[aid.get(str(k),'') for k in n['provenance'].get('articles',[])][:4]
        neighbors=list(dict.fromkeys(connected[n['id']]))[:12]
        # Repeat own surface form to stop high-arity generic context from dominating
        txt.append((' '+n['surface_form'])*3 + ' ' + n['type']+' '+' '.join(neighbors)+' '+' '.join(titles))
    return txt


def evaluate_retrieval(nodes,edges,articles,questions,ground_truth,coarse_assign,top_k=5,visit_clusters=4):
    """Exploratory candidate ranking; reference targets are used only for scoring.
    CAUTION: BOTH routes first compute the global candidate score vector (M @ Q.T).
    The hierarchy then restricts ranking to candidates within routed clusters.
    Therefore hier_inspected is a route-eligibility count, NOT actual dot-product
    work or demonstrated query-time acceleration. Historical values are retained.
    """
    corpus=candidate_texts(nodes,edges,articles)
    tf=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,strip_accents='unicode',max_features=40000,stop_words='english')
    M=tf.fit_transform(corpus)
    candidate_ix=[i for i,n in enumerate(nodes) if n['type'] in ('method','dataset','technique','component','cited_work')]
    if not candidate_ix:raise ValueError('No retrieval candidates')
    group=defaultdict(list)
    for i in candidate_ix:group[str(coarse_assign[nodes[i]['id']])].append(i)
    groups=sorted(group)
    # Sparse sum mean, then normalize, remain sparse
    from scipy.sparse import vstack,csr_matrix
    cen=vstack([csr_matrix(M[group[g]].mean(axis=0)) for g in groups],format='csr')
    cen=normalize(cen)
    counts={}
    per=[]
    for q in questions:
        qid=q['question_id'];txt=q['question']
        Q=tf.transform([txt])
        scores=(M@Q.T).toarray().ravel()
        global_rank=sorted(candidate_ix,key=lambda i:(-scores[i],nodes[i]['id']))
        cent_scores=(cen@Q.T).toarray().ravel()
        best=sorted(range(len(groups)),key=lambda j:-cent_scores[j])[:visit_clusters]
        visited=sorted({i for j in best for i in group[groups[j]]})
        hierarchy_rank=sorted(visited,key=lambda i:(-scores[i],nodes[i]['id']))
        flat_ids=global_rank[:top_k];hier_ids=hierarchy_rank[:top_k]
        record={'id':qid,'type':q['type'],'question':txt,
                'flat_node_ids':[nodes[i]['id'] for i in flat_ids],
                'flat_surface_forms':[nodes[i]['surface_form'] for i in flat_ids],
                'hier_node_ids':[nodes[i]['id'] for i in hier_ids],
                'hier_surface_forms':[nodes[i]['surface_form'] for i in hier_ids],
                'flat_inspected':len(candidate_ix),'hier_inspected':len(visited),
                'centroid_visits':len(best),'ranked_clusters':[groups[j] for j in best]}
        if q['type']=='A':
            expected=ground_truth[qid].get('expected_methods',[])
            possible={normalize_name(n['surface_form']) for i,n in enumerate(nodes) if i in candidate_ix}
            available=[x for x in expected if normalize_name(x) in possible]
            absent=[x for x in expected if normalize_name(x) not in possible]
            gold={normalize_name(s) for s in expected}
            record.update(gold_expected=expected,gold_present=available,gold_absent_in_snapshot=absent,
                          flat_hits=[nodes[i]['surface_form'] for i in flat_ids if normalize_name(nodes[i]['surface_form']) in gold],
                          hier_hits=[nodes[i]['surface_form'] for i in hier_ids if normalize_name(nodes[i]['surface_form']) in gold])
            record['flat_hit_at_5']=bool(record['flat_hits'])
            record['hier_hit_at_5']=bool(record['hier_hits'])
            record['flat_recall_at_5']=len(set(map(normalize_name,record['flat_hits'])))/max(1,len(gold))
            record['hier_recall_at_5']=len(set(map(normalize_name,record['hier_hits'])))/max(1,len(gold))
            record['flat_recall_given_available']=len(set(map(normalize_name,record['flat_hits'])))/max(1,len(available)) if available else None
            record['hier_recall_given_available']=len(set(map(normalize_name,record['hier_hits'])))/max(1,len(available)) if available else None
        else:
            record['scoring_status']='NOT_SCORED_B: requires multi-claim source-grounded synthesis and citation verification; ranked candidate nodes alone cannot measure this truth.'
        per.append(record)
    records=[x for x in per if x['type']=='A']
    def avg(field):return float(np.mean([float(r[field]) for r in records])) if records else None
    counts={'evaluated_type_A':len(records),'type_B_not_scored':sum(q['type']=='B' for q in questions),
            'flat_hit_at_5':avg('flat_hit_at_5'),'hier_hit_at_5':avg('hier_hit_at_5'),
            'flat_recall_at_5':avg('flat_recall_at_5'),'hier_recall_at_5':avg('hier_recall_at_5'),
            'mean_flat_nodes_scored':float(np.mean([r['flat_inspected'] for r in records])),
            'mean_hier_nodes_scored':float(np.mean([r['hier_inspected'] for r in records])),
            'mean_available_gold_per_question':float(np.mean([len(r['gold_present']) for r in records])),
            'mean_absent_gold_per_question':float(np.mean([len(r['gold_absent_in_snapshot']) for r in records])),
            'comparison':'same question/candidates/TF-IDF ranker; GLOBAL scores for ALL candidates are computed for both flat and hierarchy. Hierarchy filters the ranked candidate pool after scoring; mean_hier_nodes_scored is a legacy MISNOMER that denotes eligible/visited route members, not the number of query dot-products. Centroid computations add work; this is not a verified speedup.',
            'caveat':'14 Type-A lists use exact normalized surface matches; aliases may undercount recall. Benchmarks had been inspected previously (exploratory only). The current implementation scores ALL candidates even when hierarchy filters some out, so eligible-route counts are NOT savings in CPU time. Type-B answer correctness unmeasured. 2025 cutoff excludes unknown-month 2026 papers.'}
    return {'summary':counts,'per_question':per}
