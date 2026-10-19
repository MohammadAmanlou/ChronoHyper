#!/usr/bin/env python3
"""Reproducible multi-method experiments on the *actual* Constructor original data.

This is an additive research suite. It does not modify src/ or overwrite the
original metrics/report. No gold answers/questions are read by this module.
Every method/year/seed is recorded, including errors and negative outcomes.

Notes: incidence_svd is an incidence-normalized SVD baseline, NOT a full reimplementation
of the Zhou hypergraph spectral eigenproblem. clique is an unweighted clique expansion,
which biases high-arity events: compare as a deliberately lossy baseline.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math,os,sys,time,traceback,io
from zipfile import ZipFile
from collections import Counter,defaultdict
from dataclasses import asdict,dataclass
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from sklearn.metrics import adjusted_rand_score
from src.run import snapshot_raw,semantic_embeddings
from src.core import (fit_coarse,kmeans_initial,refine_native,fit_hierarchy,check_laminar,
                      collapse_all,partition_ari,hyper_connectivity)
from src.evaluation import (heldout_edge_compactness,article_title_vectors,
                            pair_similarity_by_clusters)
from research_lab.weighted_refinement import weighted_native_refinement

def parse_science_only_zip(path):
    """Deliberately do NOT open/read questions.csv or ground_truth.json."""
    with ZipFile(path) as z:
        graph=json.loads(z.read('data/tkh_collection10.json'))
        articles=list(csv.DictReader(io.StringIO(z.read('data/collection10_articles.csv').decode('utf-8-sig'))))
    return graph,articles

@dataclass(frozen=True)
class Method:
    id:str
    family:str
    semantic:float=0.70
    hyper:float=0.30
    temporal:float=0.00
    init:str='kmeans'
    explanation:str=''
    expensive:bool=False

METHODS=[
    Method('semantic_kmeans','semantic',1,0,0,explanation='Frozen 2020-only word feature KMeans baseline'),
    Method('native_structure','native',.12,.88,0,explanation='Native hyperedge connectivity-driven local refinement'),
    Method('native_semantic_85','native',.85,.15,0,explanation='Semantics-dominant, native high-order refinement'),
    Method('native_balanced_50','native',.50,.50,0,explanation='Balanced structural/semantic joint refinement'),
    Method('native_joint_70','native',.70,.30,0,explanation='Reference-style native joint refinement without temporal coupling'),
    Method('native_structure_75','native',.25,.75,0,explanation='Structure-weighted, native high-order refinement'),
    Method('native_temporal_03','native',.70,.30,.03,explanation='Warm-start evolutionary joint optimization'),
    Method('native_temporal_08','native',.70,.30,.08,explanation='Reference temporal strength, prior partition provided'),
    Method('native_temporal_20','native',.70,.30,.20,explanation='Strong evolutionary inertia; possible failure to adapt'),
    Method('incidence_svd','incidence',.40,.60,0,init='incidence_svd',explanation='Normalized node-hyperedge incidence SVD + native refinement'),
    Method('clique_pairwise','projection',.70,.30,0,init='clique',explanation='Full unweighted clique expansion for deliberately lossy graph baseline',expensive=True),
    Method('frozen_previous','temporal_control',1,0,1,init='freeze',explanation='Control: fixed survivor cluster memberships; new nodes nearest prior centroid'),
    Method('native_arity_normalized','native_new',.70,.30,.08,init='weighted_arity',explanation='Proposal: train weight 1/(arity-1), aligned with heldout normalized connectivity metric'),
    Method('native_paper_balanced','native_new',.70,.30,.08,init='weighted_article',explanation='Proposal: edge weight 1/((arity-1)*n_events_in_asserting_paper); may overcorrect'),
]
IDS={m.id:m for m in METHODS}

def json_write(path,x):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_suffix(p.suffix+'.tmp')
    temp.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True,default=convert),encoding='utf-8')
    os.replace(temp,p)

def convert(x):
    if isinstance(x,np.integer):return int(x)
    if isinstance(x,np.floating):return float(x)
    if isinstance(x,np.ndarray):return x.tolist()
    raise TypeError(str(type(x)))

def hash_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()

def clamp_clusters(labels,k):
    # Most algorithms instantiate k labels and rarely emit empty clusters;
    # DO NOT silently invent them. Record observed cluster count in metrics.
    return np.asarray(labels,dtype=int)

def _incidence_svd(ids,edges,seed,k=12):
    index={v:i for i,v in enumerate(ids)}
    row=[];col=[];weights=[]
    for j,e in enumerate(edges):
        mem=[index[v] for v in e['members'] if v in index]
        for i in mem:
            row.append(i);col.append(j);weights.append(1/math.sqrt(max(1,len(mem))))
    if not row:
        return None
    H=csr_matrix((weights,(row,col)),shape=(len(ids),len(edges)),dtype=float)
    degrees=np.asarray(H.sum(axis=1)).ravel()
    from scipy.sparse import diags
    H=diags(1/np.maximum(degrees,1e-12))@H
    n_components=max(1,min(24,len(ids)-1,len(edges)-1))
    Z=TruncatedSVD(n_components=n_components,random_state=seed).fit_transform(H)
    return normalize(Z)

def _clique_expansion(edges):
    """A deliberately explicit, lossy, UNWEIGHTED full clique baseline.
    Arity n creates n*(n-1)/2 pair events, thereby severely overweighting n>>2.
    This is a property to discuss, not a hypergraph representation.
    """
    result=[]
    for e in edges:
        for j,(a,b) in enumerate(itertools.combinations(e['members'],2)):
            result.append({'id':str(e['id'])+':pair:'+str(j),
                           'members':[a,b],'relation_type':'clique_pair',
                           'year':e['year'],
                           'provenance':e.get('provenance',{})})
    return result

def _fit(ids,X,train,m,seed,prior=None):
    prior=prior or {}
    if m.init=='freeze' and prior:
        centers=[]
        for lab in range(12):
            ix=[i for i,v in enumerate(ids) if prior.get(v)==lab]
            centers.append(X[ix].mean(axis=0) if ix else np.zeros(X.shape[1]))
        cn=normalize(np.asarray(centers))
        scores=X@cn.T
        labels=np.asarray([prior.get(v,int(np.argmax(scores[i]))) for i,v in enumerate(ids)],dtype=int)
        return labels,{'method':'frozen-control; no reoptimization','projected_pair_events':0}
    if m.id=='semantic_kmeans':
        return kmeans_initial(X,12,seed),{'method':'semantic-only KMeans','projected_pair_events':0}
    if m.init.startswith('weighted_'):
        if prior and m.temporal:
            centers=[]
            for lab in range(12):
                ix=[i for i,v in enumerate(ids) if prior.get(v)==lab]
                if ix:centers.append(X[ix].mean(axis=0))
                else:centers.append(X[np.random.default_rng(seed+lab).integers(len(ids))])
            init=kmeans_initial(X,12,seed,centers=normalize(np.asarray(centers)))
            prev=np.asarray([prior.get(v,-1) for v in ids],dtype=int)
        else:
            init=kmeans_initial(X,12,seed);prev=None
        weighting='arity+source' if m.init=='weighted_article' else 'arity'
        pred=weighted_native_refinement(ids,X,train,init,semantic=m.semantic,hyper=m.hyper,
                   previous=prev,temporal=m.temporal if prev is not None else 0,
                   rounds=3,weighting=weighting)
        return pred,{'method':'original high-order event-aware normalized connectivity; '+weighting,
                     'projected_pair_events':0}
    if m.init=='incidence_svd':
        Z=_incidence_svd(ids,train,seed)
        if Z is None:raise ValueError('No eligible incidence in snapshot')
        init=kmeans_initial(Z,12,seed)
        pred=refine_native(ids,X,train,init,semantic=m.semantic,hyper=m.hyper,rounds=2)
        return pred,{'method':'incidence-normalized SVD initialization + high-order local refinement','projected_pair_events':0}
    if m.init=='clique':
        pair=_clique_expansion(train)
        pred=refine_native(ids,X,pair,kmeans_initial(X,12,seed),semantic=m.semantic,hyper=m.hyper,rounds=2)
        return pred,{'method':'unweighted pairwise clique expansion, high arity quadratic bias','projected_pair_events':len(pair)}
    if m.id=='native_structure':
        return fit_coarse(ids,X,train,12,seed=seed,variant='structure'),{'method':'native structure-dominant','projected_pair_events':0}
    # Explicit prior-conditioned initialization and penalty apply to every temporal variant
    # and no such prior is passed for non-temporal methods.
    if m.temporal and prior:
        centers=[]
        for lab in range(12):
            ix=[i for i,v in enumerate(ids) if prior.get(v)==lab]
            if ix:centers.append(X[ix].mean(axis=0))
            else:centers.append(X[np.random.default_rng(seed+lab).integers(len(ids))])
        centers=normalize(np.asarray(centers))
        init=kmeans_initial(X,12,seed,centers=centers)
        prev=np.asarray([prior.get(v,-1) for v in ids],dtype=int)
    else:
        init=kmeans_initial(X,12,seed);prev=None
    pred=refine_native(ids,X,train,init,semantic=m.semantic,hyper=m.hyper,
                       temporal=m.temporal if prev is not None else 0,
                       previous=prev,rounds=3)
    return pred,{'method':'native joint high-order local refinement','projected_pair_events':0}

def _paper_group_scores(edges,assignment):
    by=defaultdict(list)
    for e in edges:
        if len(e['members'])<2:continue
        score=(len({assignment[x] for x in e['members']})-1)/(len(e['members'])-1)
        key=str(e.get('provenance',{}).get('article_id','unknown'))
        by[key].append(float(score))
    return {p:sum(v)/len(v) for p,v in sorted(by.items())}

def _title_coherence(Y,eligible,labels,seed):
    value=pair_similarity_by_clusters(Y,labels,eligible,seed=seed,max_pairs=700)
    return value

def _sample_uncertainty(groups,seed):
    # Per-paper bootstrap gives descriptive uncertainty for the sampled publication subset.
    # It cannot correct the small number of papers or transductive node exposure.
    if len(groups)<2:return [None,None]
    rng=np.random.default_rng(seed)
    vals=np.array(list(groups.values()),dtype=float)
    means=rng.choice(vals,size=(400,len(vals)),replace=True).mean(axis=1)
    return [float(np.percentile(means,2.5)),float(np.percentile(means,97.5))]

def _run_method(g,articles,snapshots,embeddings,excluded_papers,m,seed,years,output,coherence,completed,evaluation_papers=None):
    begun=time.perf_counter();run_name=f'{m.id}__seed{seed}'
    base=output/'runs'/run_name
    base.mkdir(parents=True,exist_ok=True)
    state_path=base/'status.json'
    json_write(state_path,{'status':'running','run_id':run_name,'method':asdict(m),'seed':seed,'start_unix':time.time()})
    prior={};last={};rows=[];assignments={};error=None
    try:
        for year in years:
            tic=time.perf_counter();key=str(year);snap=snapshots[key]
            ids=[n['id'] for n in snap['nodes']];X=embeddings[key]
            train=[e for e in snap['hyperedges'] if str(e.get('provenance',{}).get('article_id','unknown')) not in excluded_papers]
            hold=[e for e in snap['hyperedges'] if str(e.get('provenance',{}).get('article_id','unknown')) in (evaluation_papers or set())]
            labels,detail=_fit(ids,X,train,m,seed,prior)
            labels=clamp_clusters(labels,12)
            mapping=dict(zip(ids,map(int,labels)))
            if len(mapping)!=len(ids):raise ValueError('Missing labels for nodes')
            n_clusters=len(set(labels.tolist()))
            if n_clusters>12 or n_clusters<1:raise ValueError('Invalid hard size budget')
            # Explicitly keep all (original, high-order) event IDs/multiplicities for hierarchy audit.
            collapsed=collapse_all(train,mapping)
            if len(collapsed)!=len(train):raise AssertionError('Lost original edge events')
            if any(sum(e['multiplicity'].values())!=e['original_arity'] for e in collapsed):
                raise AssertionError('Endpoint mass conservation violated')
            title=_title_coherence(*coherence[key],labels,seed+year)
            group_scores=_paper_group_scores(hold,mapping)
            cut=heldout_edge_compactness(hold,mapping)
            ari=partition_ari(last,mapping) if last else None
            n_old=len(set(last)&set(mapping)) if last else 0
            # Cluster label IDs are locally generated. For different non-temporal fits,
            # fractional label changes are NOT aligned and so are not reported.
            row={'run_id':run_name,'seed':seed,'model':m.id,'family':m.family,'year':year,
                 'n_nodes':len(ids),'n_train_edges':len(train),'n_heldout_edges':len(hold),
                 'n_heldout_papers':len(group_scores),'heldout_paper_scores':group_scores,'n_clusters':n_clusters,
                 'heldout_normalized_connectivity_lower_better':cut,
                 'heldout_group_bootstrap_ci95':_sample_uncertainty(group_scores,seed+year),
                 'independent_article_title_view_coherence_higher_better':title,
                 'native_training_connectivity_lambda_minus_one':hyper_connectivity(train,mapping),
                 'fraction_train_events_internal':sum(e['internal'] for e in collapsed)/max(1,len(collapsed)),
                 'train_highorder_events_still_3plus_coarse':sum(len(e['coarse_members'])>=3 for e in collapsed),
                 'actual_train_edge_ids_preserved':len(collapsed),
                 'cross_year_shared_node_ari':ari,'shared_node_count':n_old,
                 'elapsed_seconds':round(time.perf_counter()-tic,3),
                 **detail}
            rows.append(row)
            assignments[key]=mapping
            json_write(base/f'metrics_{year}.json',row)
            print(run_name,year,'cut',cut,'title',title,'ARI',ari,'s',row['elapsed_seconds'],flush=True)
            prior=mapping;last=mapping
        json_write(base/'assignments.json',assignments)
        json_write(base/'metrics.json',{'run_id':run_name,'method':asdict(m),'seed':seed,
                                        'elapsed_seconds':round(time.perf_counter()-begun,3),'years':rows,
                                        'status':'complete'})
        json_write(state_path,{'status':'complete','run_id':run_name,
                               'elapsed_seconds':round(time.perf_counter()-begun,3),
                               'years_completed':[x['year'] for x in rows]})
        return rows,None
    except Exception as e:
        error={'status':'failed','run_id':run_name,'exception':str(e),'traceback':traceback.format_exc(),
               'years_completed':[x['year'] for x in rows],
               'elapsed_seconds':round(time.perf_counter()-begun,3)}
        json_write(state_path,error)
        (base/'ERROR.txt').write_text(error['traceback'],encoding='utf-8')
        print('FAILED',run_name,str(e),flush=True)
        return rows,error

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data',default='inputs/data.zip')
    ap.add_argument('--out',default='research_outputs')
    ap.add_argument('--years',default='2020,2022,2024')
    ap.add_argument('--seeds',default='17')
    ap.add_argument('--methods',default='semantic_kmeans,native_joint_70,native_temporal_08')
    ap.add_argument('--embedding-seed',type=int,default=17)
    ap.add_argument('--paper-holdout-seed',type=int,default=42)
    ap.add_argument('--stage',choices=['development','confirmation'],default='development')
    ap.add_argument('--lock-file',default='')
    ap.add_argument('--include-expensive',action='store_true')
    ap.add_argument('--overwrite',action='store_true')
    args=ap.parse_args()
    years=[int(x) for x in args.years.split(',')]
    seeds=[int(x) for x in args.seeds.split(',')]
    if sorted(set(years))!=years or not years or years[0]!=2020:ap.error('years must be unique, increasing, and start with 2020 to fit the fixed primary encoder')
    ids=[x.strip() for x in args.methods.split(',') if x.strip()]
    if not ids or any(x not in IDS for x in ids):ap.error('Unknown method; choices: '+','.join(IDS))
    if args.stage=='confirmation':
        if len(ids)!=1 or not args.lock_file:ap.error('Confirmatory stage requires exactly one --methods value and a frozen --lock-file')
        lf=Path(args.lock_file)
        if not lf.exists():ap.error('Selection lock does not exist')
        lock=json.loads(lf.read_text(encoding='utf-8'))
        if lock.get('method')!=ids[0] or lock.get('years')!=years or lock.get('seeds')!=seeds:
            ap.error('Model/years/seeds differ from locked selection. Do not change the confirmation protocol.')
        if lock.get('data_sha256')!=hash_file(args.data):ap.error('Source data differ from frozen selection')
    if any(IDS[x].expensive for x in ids) and not args.include_expensive:
        ap.error('Clique full projection has quadratic size; explicitly pass --include-expensive')
    output=Path(args.out);output.mkdir(parents=True,exist_ok=True)
    source_hash=hash_file(args.data)
    source_codes=['research_lab/experiment_suite.py','research_lab/weighted_refinement.py','src/core.py','src/run.py','src/evaluation.py']
    if any(not Path(p).is_file() for p in source_codes):
        raise SystemExit('Launch from project root; missing one or more source files required for provenance fingerprint.')
    source_code_hashes={p:hash_file(p) for p in source_codes}
    protocol={'method_ids':ids,'seeds':seeds,'years':years,'data_sha256':source_hash,
              'source_code_sha256':source_code_hashes,
              'paper_holdout_seed':args.paper_holdout_seed,'embedding_seed':args.embedding_seed,
              'evaluation_stage':args.stage,'selection_lock':hash_file(args.lock_file) if args.lock_file else None,
              'no_answer_leakage':'Neither questions.csv nor ground_truth.json is accessed or scored here.',
              'honesty':'Source title view is a correlated but separately generated proxy, NOT blinded expert semantic coherence.',
              'leakage_warning':'Transductive node surface forms and all provenance-linked article titles may contain heldout-source content; group-heldout edges only, not prospective out-of-domain paper testing.',
              'multi_method':'Methods are local custom implementations; do not misidentify as official implementations of Mt-KaHyPar/Leiden/Zhou.',
              'performance':'all models share source snapshots, heldout papers, frozen encoder and K<=12; CPU and complexity differ.',
              'pre_registration':'predeclared matrix, NOT hyperparameters selected from the 18 known benchmark gold answers.'}
    conf_file=output/'protocol.json'
    if conf_file.exists() and json.loads(conf_file.read_text(encoding='utf-8'))!=protocol:
        raise SystemExit('Existing directory has a DIFFERENT protocol. Choose a new --out directory.')
    json_write(conf_file,protocol)
    graph,articles=parse_science_only_zip(args.data)
    # Neither evaluation questions nor their reference answers were even opened.
    snaps={str(y):snapshot_raw(graph,y) for y in years}
    features,_=semantic_embeddings(snaps,seed=args.embedding_seed)
    all_papers=sorted({str(e.get('provenance',{}).get('article_id','unknown')) for e in graph['hyperedges']})
    rng=np.random.default_rng(args.paper_holdout_seed)
    ordered=rng.permutation(all_papers).tolist()
    ndev=max(1,round(.20*len(all_papers)));nconfirm=max(1,round(.20*len(all_papers)))
    dev=set(ordered[:ndev]);confirm=set(ordered[ndev:ndev+nconfirm]);excluded=dev|confirm
    held=dev if args.stage=='development' else confirm
    json_write(output/'paper_split.json',{'paper_ids_for_development':sorted(dev),
                    'paper_ids_reserved_for_confirmation':sorted(confirm),
                    'paper_ids_heldout_of_all_model_fitting':sorted(excluded),
                    'n_fitting_papers':len(all_papers)-len(excluded),
                    'actual_evaluation_stage':args.stage,'actual_evaluation_papers':sorted(held),
                    'total_papers':len(all_papers),'split_seed':args.paper_holdout_seed,
                    'note':'Held-out edges by asserting article. All published node text remains visible transductively. Confirm only a prelocked single method.'})
    titles={str(y):article_title_vectors(snaps[str(y)]['nodes'],articles,y) for y in years}
    report=[];failed=[];skipped=[]
    for i in ids:
        m=IDS[i]
        for seed in seeds:
            target=output/'runs'/f'{m.id}__seed{seed}'
            if target.exists() and (target/'status.json').exists():
                status=json.loads((target/'status.json').read_text(encoding='utf-8')).get('status')
                if status=='complete' and not args.overwrite:
                    skipped.append(f'{m.id}__seed{seed}');print('SKIP existing',skipped[-1],flush=True);continue
                if status!='complete' and not args.overwrite:
                    raise SystemExit('Prior partial/error run '+str(target)+'; preserve it; retry with --overwrite or new output folder')
            rows,error=_run_method(graph,articles,snaps,features,excluded,m,seed,years,output,titles,[],evaluation_papers=held)
            report.extend(rows)
            if error:failed.append(error)
            json_write(output/'batch_status.json',{'successfully_finished_in_this_invocation':len({r['run_id'] for r in report}),
                                                    'failures_in_this_invocation':failed,
                                                    'skipped_existing_runs':skipped})
    summary={'protocol_sha256':hash_file(conf_file),'finished_this_invocation':len(set(r['run_id'] for r in report)),
             'all_expected_runs':len(ids)*len(seeds),'failed':failed,'skipped_previously_completed':skipped,
             'no_methods_discarded':True,'total_elapsed_metric':'See every run own metrics.json'}
    json_write(output/'batch_status.json',summary)
    print('BATCH FINISHED',summary,flush=True)
    if failed:sys.exit(2)

if __name__=='__main__':main()
