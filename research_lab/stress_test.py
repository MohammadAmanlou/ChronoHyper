#!/usr/bin/env python3
"""Matched-protocol perturbation and degree/arity-preserving null tests.

Every refit uses the SAME method, temporal previous partition, fixed embeddings,
original fitting paper exclusions, and seed as the reference run.
This fixes the apples-to-oranges temporal confound of the earlier prototype.
Gold answers are never accessed/scored.
"""
import argparse,json,time,traceback
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.metrics import adjusted_rand_score
from src.run import snapshot_raw,semantic_embeddings
from src.evaluation import incidence_degree_preserving_shuffle,heldout_edge_compactness,_bootstrap
from research_lab.experiment_suite import IDS,_fit,json_write,hash_file,parse_science_only_zip

def main():
    p=argparse.ArgumentParser();p.add_argument('--experiment-dir',default='research_outputs/development')
    p.add_argument('--data',default='inputs/data.zip');p.add_argument('--model',default='native_temporal_08')
    p.add_argument('--seed',type=int,default=17);p.add_argument('--year',type=int,default=2024)
    p.add_argument('--deletion-runs',type=int,default=5);p.add_argument('--null-runs',type=int,default=19)
    p.add_argument('--out',default='');a=p.parse_args()
    root=Path(a.experiment_dir)
    protocol=json.loads((root/'protocol.json').read_text(encoding='utf-8'))
    if protocol['data_sha256']!=hash_file(a.data):p.error('Data SHA mismatch against original experiment')
    if a.model not in IDS:p.error('Unknown method')
    runs=root/'runs'/f'{a.model}__seed{a.seed}'
    if not runs.exists():p.error('Base run missing: '+str(runs))
    baseline=json.loads((runs/'metrics.json').read_text(encoding='utf-8'))
    if baseline['status']!='complete':p.error('Base run is not complete')
    byyear={x['year']:x for x in baseline['years']}
    if a.year not in byyear:p.error('Year not found in reference run')
    assign=json.loads((runs/'assignments.json').read_text(encoding='utf-8'))
    idx=protocol['years'].index(a.year);prior=assign[str(protocol['years'][idx-1])] if idx>0 else {}
    reference=assign[str(a.year)]
    split=json.loads((root/'paper_split.json').read_text(encoding='utf-8'))
    excluded=set(split['paper_ids_heldout_of_all_model_fitting']);evaluation=set(split['actual_evaluation_papers'])
    g,articles=parse_science_only_zip(a.data)
    snap=snapshot_raw(g,a.year)
    # Full initial 2020 fit only for feature encoder, frozen in all follow-up snapshots.
    snaps={'2020':snapshot_raw(g,2020),str(a.year):snap}
    X=semantic_embeddings(snaps,seed=protocol['embedding_seed'])[0][str(a.year)]
    ids=[n['id'] for n in snap['nodes']]
    train=[e for e in snap['hyperedges'] if str(e.get('provenance',{}).get('article_id','unknown')) not in excluded]
    held=[e for e in snap['hyperedges'] if str(e.get('provenance',{}).get('article_id','unknown')) in evaluation]
    observed=heldout_edge_compactness(held,reference)
    out=Path(a.out or root/'stress'/f'{a.model}__seed{a.seed}__{a.year}')
    out.mkdir(parents=True,exist_ok=True)
    prev=prior if idx>0 else None
    vals=[];nullvals=[];swaps=[];start=time.perf_counter()
    try:
        for s in range(a.deletion_runs):
            rng=np.random.default_rng(a.seed+73*s)
            chosen=np.sort(rng.choice(len(train),size=round(len(train)*.90),replace=False))
            pert=[train[int(i)] for i in chosen]
            labels,_=_fit(ids,X,pert,IDS[a.model],a.seed,prev)
            value=float(adjusted_rand_score([reference[v] for v in ids],labels))
            vals.append(value)
            json_write(out/'progress.json',{'phase':'deletion','n_completed':len(vals),'ari_values':vals})
        degree=Counter(x for e in train for x in e['members'])
        for s in range(a.null_runs):
            shuffled,nswap=incidence_degree_preserving_shuffle(train,seed=a.seed+10000+s,multiple=3)
            if Counter(x for e in shuffled for x in e['members'])!=degree:
                raise AssertionError('Node incidence degree NOT preserved')
            if any(len(e['members'])!=len(t['members']) for e,t in zip(train,shuffled)):
                raise AssertionError('Hyperedge arity NOT preserved')
            labels,_=_fit(ids,X,shuffled,IDS[a.model],a.seed,prev)
            val=heldout_edge_compactness(held,dict(zip(ids,map(int,labels))))
            nullvals.append(val);swaps.append(nswap)
            json_write(out/'progress.json',{'phase':'shuffle','n_completed':len(nullvals),
                                            'null_cut_values':nullvals,'successful_swaps':swaps})
        if all(x==0 for x in swaps) and a.null_runs>0:
            status='degenerate_null_no_successful_swaps'; pvalue=None
        else:
            status='complete'
            # lower hyperedge connectivity loss is better.
            pvalue=(1+sum(n is not None and n<=observed for n in nullvals))/(1+len(nullvals)) if nullvals else None
        result={'status':status,'method':a.model,'seed':a.seed,'year':a.year,
                'same_previous_partition_for_every_refit':bool(prior),
                'same_encoder_seed':protocol['embedding_seed'],'source_data_sha256':protocol['data_sha256'],
                'assessment_stage':protocol['evaluation_stage'],
                'heldout_cut_observed':observed,'null_scores':nullvals,'null_count':len(nullvals),
                'null_degree_arity_preserved':True,'null_successful_swaps':swaps,
                'randomization_p_lower_better':pvalue,
                'perturbation_10pct_ARI':vals,'perturbation_bootstrap_descriptive':_bootstrap(vals,seed=a.seed+39),
                'elapsed_seconds':round(time.perf_counter()-start,2),
                'limitations':['Only sample-paper article holdout, not new corpus generalization',
                               'Same transductive node surface/text available to fit even when assertions held out',
                               'Five edge-deletion replicates yield very uncertain descriptive CIs',
                               'Multiple models/years tried: adjust any inferential interpretation for selection',
                               'Null swaps are constrained by relation+article_year; few swaps may cause null degeneracy']}
        json_write(out/'result.json',result)
        print('STRESS PASSED',out,'perturb_mean',np.mean(vals) if vals else None,
              'null_p',pvalue,'seconds',result['elapsed_seconds'])
    except Exception as exc:
        json_write(out/'status_FAILED.json',{'status':'failed','exception':str(exc),'traceback':traceback.format_exc()})
        raise

if __name__=='__main__':main()
