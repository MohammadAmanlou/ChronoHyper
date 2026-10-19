"""Gold-blind retrieval and honest held-out SOURCE-COVERAGE scoring for Constructor Type-B.

Stages intentionally separate: rank never opens data/ground_truth.json; score reads
frozen rankings, then opens gold only to measure source coverage, NOT answer truth.

RUN FROM REPO ROOT:
 python -m research_lab.type_b_source_audit rank --out research_outputs/type_b_audit
 python -m research_lab.type_b_source_audit score --out research_outputs/type_b_audit

This project uses *previously viewed* task questions and gold: exploratory only.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import random
import re
from zipfile import ZipFile

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

CUTOFF=2025
TOP_KS=(3,5,10)

def stable_json(v):
    return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')

def name_key(text):
    return re.sub('[^a-z0-9]','',str(text).lower())

def rank(project, out, cutoff=CUTOFF, seed=17, routes=4):
    project=Path(project);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with ZipFile(project/'inputs/data.zip') as z:
        # Deliberately NEVER open ground_truth.json at the ranking stage.
        graph=json.loads(z.read('data/tkh_collection10.json'))
        articles=list(csv.DictReader(io.StringIO(z.read('data/collection10_articles.csv').decode('utf-8-sig'))))
        questions=list(csv.DictReader(io.StringIO(z.read('data/questions.csv').decode('utf-8-sig')),delimiter=';'))
    docs=sorted((a for a in articles if int(a['year'])<=cutoff),key=lambda a:int(a['id']))
    if not docs:raise ValueError('No eligible source articles')
    hier=json.loads((project/f'outputs_selected/hierarchy_{cutoff}.json').read_text(encoding='utf-8'))
    # Frozen level-0 partition; prohibit use of gold claims or benchmark answers.
    v_to_cluster={}
    roots=[s for s in hier['supernodes'] if s['level']==0]
    for s in roots:
        for ident in s['member_ids']:
            if ident in v_to_cluster:raise AssertionError(f'Non-disjoint top partition: {ident}')
            v_to_cluster[ident]=s['id']
    allowed={n['id']:n for n in graph['nodes'] if n['first_seen_year']<=cutoff}
    artnodes=defaultdict(list)
    groups=defaultdict(set)
    for n in allowed.values():
        for rawid in n.get('provenance',{}).get('articles',[]):
            aid=str(rawid)
            artnodes[aid].append(n)
            if n['id'] in v_to_cluster:groups[aid].add(v_to_cluster[n['id']])
    text=[]
    eligible_by_id={a['id']:a for a in docs}
    for a in docs:
        # Source-paper metadata and entity names, no gold, no prospective 2026 facts.
        names=sorted({n['surface_form'] for n in artnodes[a['id']] if n['type'] not in ('article','author','claim','cited_work')})
        text.append((' '+a['title'])*3+' '+' '.join(names[:180]))
    tf=TfidfVectorizer(ngram_range=(1,2),stop_words='english',sublinear_tf=True,strip_accents='unicode')
    X=tf.fit_transform(text).tocsr()
    row_id={a['id']:i for i,a in enumerate(docs)}
    # Each paper can cover several macro-clusters; score all papers with same TF-IDF.
    root_papers=defaultdict(list)
    no_group=[]
    for a in docs:
        if not groups.get(a['id']):no_group.append(row_id[a['id']])
        for group in groups.get(a['id'],[]):root_papers[group].append(row_id[a['id']])
    if not root_papers:raise AssertionError('No papers routed by the frozen hierarchy')
    from scipy.sparse import vstack,csr_matrix
    rootkeys=sorted(root_papers)
    cent=vstack([csr_matrix(X[root_papers[g]].mean(axis=0)) for g in rootkeys]).tocsr()
    cent=normalize(cent)
    records=[]
    for q in questions:
        if q['type']!='B':continue
        query=tf.transform([q['question']]);scores=np.asarray((X@query.T).toarray()).ravel()
        flat=sorted(range(len(docs)),key=lambda i:(-float(scores[i]),docs[i]['id']))
        centroid_scores=np.asarray((cent@query.T).toarray()).ravel()
        group_pos=sorted(range(len(rootkeys)),key=lambda j:(-centroid_scores[j],rootkeys[j]))[:routes]
        candidate_ids=sorted(set(no_group)|{idx for j in group_pos for idx in root_papers[rootkeys[j]]})
        hier_rank=sorted(candidate_ids,key=lambda i:(-float(scores[i]),docs[i]['id']))
        records.append({'question_id':q['question_id'],'question':q['question'],
             'flat_ranked_paper_ids':[docs[i]['id'] for i in flat],
             'hier_ranked_paper_ids':[docs[i]['id'] for i in hier_rank],
             'flat_papers_scored':len(docs),'hier_papers_scored':len(candidate_ids),
             'centroids_scored':len(rootkeys),'visited_cluster_ids':[rootkeys[j] for j in group_pos]})
    source_inventory=[{'id':a['id'],'year':int(a['year']),'title':a['title']} for a in docs]
    result={'schema':'type_b_source_retrieval_frozen_v1','stage':'GOLD_BLIND_RANKING','cutoff':cutoff,
      'seed':seed,'visited_top_clusters':routes,'questions_source':'data/questions.csv (B only)',
      'candidate_sources':'data/collection10_articles.csv and provenance entity names',
      'hierarchy_source':f'outputs_selected/hierarchy_{cutoff}.json',
      'n_eligible_articles':len(docs),'n_unrouted_papers_included_both_methods':len(no_group),
      'gold_was_not_opened':True,'public_article_index':source_inventory,'questions':records,
      'caveats':['All 4 questions were previously seen during model research. This is EXPLORATORY, not a new untouched test.',
                 'Gold labels or required claim texts never enter this ranking script.',
                 'Routing centroids add computation; candidates_scored is NOT latency.',
                 'Article titles/metadata and entity names may be visible across source-group heldout splits: not an independent unseen-paper retrieval test.',
                 'No answer generation and no factual-claim correctness measurement.']}
    digest=hashlib.sha256(stable_json(result)).hexdigest()
    result['ranking_sha256']=digest
    (out/'frozen_rankings.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print('RANK FROZEN',len(records),'B-questions',len(docs),'paper candidates','SHA256',digest)
    return result

def score(project, out, n_random=2000, random_seed=101):
    project=Path(project);out=Path(out)
    r=json.loads((out/'frozen_rankings.json').read_text(encoding='utf-8'))
    claimed=r.pop('ranking_sha256')
    if hashlib.sha256(stable_json(r)).hexdigest()!=claimed:
        raise ValueError('Frozen ranked-list contents changed after ranking')
    r['ranking_sha256']=claimed
    # Gold opened only AFTER the frozen ranking digest was verified.
    with ZipFile(project/'inputs/data.zip') as z:
        gold=json.loads(z.read('data/ground_truth.json'))
    inventory={x['id']:x for x in r['public_article_index']}
    title_idx=defaultdict(list)
    for pid,a in inventory.items():title_idx[name_key(a['title'])].append(pid)
    qs=[];rubric_rows=[]
    for q in r['questions']:
        ident=q['question_id']; ref=gold[ident]
        if ref.get('type')!='B':raise ValueError('Gold type mismatch')
        src_map={}
        for source_id,metadata in ref['sources'].items():
            # Exact normalized title only; never guess matching sources.
            candidates=title_idx[name_key(metadata['title'])]
            src_map[source_id]={'source_title':metadata['title'],'eligible_match_ids':candidates,
               'match_status':'EXACT_NORMALIZED' if len(candidates)==1 else 'ABSENT' if not candidates else 'AMBIGUOUS'}
        hit_gold=set(pid for v in src_map.values() for pid in v['eligible_match_ids'] if v['match_status']=='EXACT_NORMALIZED')
        scores={}
        for name in ('flat','hier'):
            ranking=q[name+'_ranked_paper_ids']
            scores[name]={}
            for k in TOP_KS:
                retrieved=set(ranking[:k]);hits=retrieved & hit_gold
                scores[name][f'gold_source_recall_at_{k}_available']=len(hits)/len(hit_gold) if hit_gold else None
                scores[name][f'gold_source_recall_at_{k}_all']=len(hits)/len(ref['sources']) if ref['sources'] else None
                scores[name][f'gold_reference_precision_at_{k}']=len(hits)/min(k,len(ranking)) if ranking else None
                scores[name][f'claim_source_coverage_at_{k}']=sum(any(s in src_map and set(src_map[s]['eligible_match_ids'])&retrieved for s in c.get('sources',[])) for c in ref['required_claims'])/len(ref['required_claims']) if ref['required_claims'] else None
        claim_eligible=sum(any(src_map.get(s,{}).get('eligible_match_ids') for s in claim.get('sources',[])) for claim in ref['required_claims'])
        qout={'question_id':ident,'query':q['question'],'n_gold_sources':len(ref['sources']),
               'n_gold_sources_exact_available':len(hit_gold),'n_required_claims':len(ref['required_claims']),
               'n_claims_with_at_least_one_eligible_source':claim_eligible,'source_mapping':src_map,'scores':scores,
               'flat_top_10':[inventory[a] for a in q['flat_ranked_paper_ids'][:10]],
               'hier_top_10':[inventory[a] for a in q['hier_ranked_paper_ids'][:10]],
               'status':'REFERENCE_RETRIEVAL_ONLY_NOT_ANSWER_CORRECTNESS'}
        qs.append(qout)
        for claim in ref['required_claims']:
            rub={'question_id':ident,'claim_id':claim['id'],'required_claim':claim['text'],
                 'reference_coverage_flag':claim.get('coverage','not_provided'),
                 'gold_eligible_source_ids':' | '.join(pid for sid in claim.get('sources',[]) for pid in src_map.get(sid,{}).get('eligible_match_ids',[])),
                 'flat_top5_has_gold_source':bool(set(q['flat_ranked_paper_ids'][:5]) & {pid for sid in claim.get('sources',[]) for pid in src_map.get(sid,{}).get('eligible_match_ids',[])}),
                 'hier_top5_has_gold_source':bool(set(q['hier_ranked_paper_ids'][:5]) & {pid for sid in claim.get('sources',[]) for pid in src_map.get(sid,{}).get('eligible_match_ids',[])}),
                 'manual_claim_supported_yes_no_unclear':'','manual_source_citation_verified_yes_no_unclear':'',
                 'human_reviewer':'','reviewer_notes':''}
            rubric_rows.append(rub)
    summary={}
    for method in ('flat','hier'):
        for k in TOP_KS:
            for metric in (f'gold_source_recall_at_{k}_available',f'gold_source_recall_at_{k}_all',f'claim_source_coverage_at_{k}'):
                vals=[q['scores'][method][metric] for q in qs if q['scores'][method][metric] is not None]
                summary[method+'_'+metric+'_macro_mean']=round(float(np.mean(vals)),5) if vals else None
    # Random paper-source retrieval: null model, NOT a new independent test or statistical significance for trained retrieval.
    rng=random.Random(random_seed)
    random_means=[]; eligible_sources={q['question_id']:set(pid for x in q['source_mapping'].values() for pid in x['eligible_match_ids'] if x['match_status']=='EXACT_NORMALIZED') for q in qs}
    universe=list(inventory)
    for _ in range(n_random):
        vals=[]
        for q in qs:
            pool=set(rng.sample(universe,min(5,len(universe))))
            available=eligible_sources[q['question_id']]
            if available: vals.append(len(pool&available)/len(available))
        random_means.append(float(np.mean(vals)))
    observed=summary.get('hier_gold_source_recall_at_5_available_macro_mean')
    pval=(1+sum(x>=observed for x in random_means))/(1+len(random_means)) if observed is not None else None
    result={'schema':'type_b_source_score_v1','ranking_sha256':claimed,'gold_source':'data/ground_truth.json (opened only in score phase)',
      'n_type_b':len(qs),'k_values':TOP_KS,'n_random_controls':n_random,
      'summary':summary,'random_null_p_hier_reference_recall_at5':pval,
      'random_null_reference_recall_at5_mean':round(float(np.mean(random_means)),5),
      'question_breakdown':qs,
      'claim_answer_accuracy_measured':False,
      'assessment_status':'EXPLORATORY_SOURCE_COVERAGE_NOT_ANSWER_FAITHFULNESS',
      'limitations':['No full-text article passage evidence; the gold file provides reference citations/claim rubrics, not source text to independently verify every claim.',
       'All four benchmark questions and golden sources were previously inspected during project development, so p-values are descriptive and cannot establish generalization.',
       '2025 snapshot excludes 2026 papers even if published before Feb 2026 (no reliable month available in archive).',
       'The reference titles in gold are NOT necessarily the only relevant articles; reference-list precision is not true citation precision.',
       'At-most four questions and one corpus prevent reliable domain-general statistical inference.',
       'Candidate-score savings ignore centroid route overhead and do not imply measured wallclock gains.']}
    out.mkdir(parents=True,exist_ok=True)
    (out/'type_b_source_scores.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'CLAIM_LEVEL_REVIEW_BLANK.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(rubric_rows[0]));writer.writeheader();writer.writerows(rubric_rows)
    print('TYPE B SCORE',json.dumps({'n':len(qs),'summary':summary,'random_reference_recall_p':pval,'human_answer_accuracy':'NOT_MEASURED'},indent=2,ensure_ascii=False))
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('stage',choices=['rank','score'])
    ap.add_argument('--project',default='.')
    ap.add_argument('--out',default='research_outputs/type_b_audit')
    ap.add_argument('--cutoff',type=int,default=CUTOFF)
    a=ap.parse_args()
    if a.stage=='rank':rank(a.project,a.out,a.cutoff)
    else:score(a.project,a.out)
if __name__=='__main__':main()
