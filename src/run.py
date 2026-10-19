"""Run the Constructor research assessment with real TKH and defensible evaluation.
No claims about admission/funding; no simulated original dataset.
Usage: python -m src.run --data inputs/data.zip --out outputs --seed 17
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv,hashlib,json,os,time
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer,TfidfTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from src.t1_audit import parse_archive,observe
from src.core import fit_coarse,fit_hierarchy,edge_collapse,collapse_all,check_laminar,temporal_match
from src.evaluation import (independent_coherence,robustness,cross_snapshot_ari_ci,
                            heldout_edge_compactness,native_structural_null,loss_metrics)
from src.retrieval import evaluate_retrieval
from src.labeling import generate_levels,support_audit,name_from_members

YEARS=[2020,2022,2024,2025]


def write_json(path, data):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=convert),encoding='utf-8')

def convert(v):
    if isinstance(v,np.integer):return int(v)
    if isinstance(v,np.floating):return float(v)
    if isinstance(v,np.ndarray):return v.tolist()
    raise TypeError(type(v))


def semantic_embeddings(snapshots,dim=48,seed=17):
    """Learn semantics only from time-2020 nodes to prevent fitting on future content.
    Hashing vectorizer vocabulary is frozen; SVD learned from first cutoff only.
    This may impair encoding of unseen vocabulary in 2025: disclose.
    """
    hv=HashingVectorizer(n_features=2**15,alternate_sign=False,norm='l2',
                         ngram_range=(1,2),stop_words='english',lowercase=True)
    first=snapshots[str(YEARS[0])]['nodes']
    texts=[n['surface_form'] for n in first]
    matrix=hv.transform(texts)
    svd=TruncatedSVD(n_components=dim,n_iter=5,random_state=seed)
    svd.fit(matrix)
    X={}
    for y,s in snapshots.items():
        data=hv.transform([n['surface_form'] for n in s['nodes']]);z=svd.transform(data)
        X[y]=normalize(z)
    return X,{'primary_encoder':'HashingVectorizer(2**15,word_ngrams=(1,2)) + 48d TruncatedSVD fit only 2020','embedding_dim':dim,'svd_training_year':YEARS[0],
              'future_leakage_precaution':'No future surface strings used in fitted SVD. Fixed deterministic hashing features used for future years.',
              'limitations':'Word-hash representations from 2020 can underrepresent novel scientific vocabulary in later snapshots; does not use a pretrained scientific encoder.'}


def snapshot_raw(graph,cutoff):
    ids={n['id'] for n in graph['nodes'] if n['first_seen_year']<=cutoff}
    nodes=[n for n in graph['nodes'] if n['id'] in ids]
    edges=[e for e in graph['hyperedges'] if e['year']<=cutoff
           and e.get('provenance',{}).get('article_year',e['year'])<=cutoff
           and all(v in ids for v in e['members'])]
    return {'cutoff':cutoff,'nodes':nodes,'hyperedges':edges}


def group_id_map(levels,prev_levels,prev_ids,next_serial,cutoff):
    ids_by_level=[]; events=[]; matches={}
    for l,p in enumerate(levels):
        if l==3:
            # node identity itself: persistent as long as original node exists
            ids_by_level.append({g:'node_'+v for v,g in p.items()});continue
        past=prev_levels[l] if prev_levels else {}
        old=prev_ids[l] if prev_ids else {}
        current_ids,logs,next_serial,weights=temporal_match(past,p,old,next_serial,minimum=.03)
        prefix={g:f'L{l}_{persistent}' for g,persistent in current_ids.items()}
        if not prev_levels:
            # prefixing is deterministic and stable as current_ids inherited next iteration
            pass
        ids_by_level.append(prefix)
        for entry in logs:
            # internal stable IDs include no level prefix yet; prefix source/target
            events.append({'cutoff':cutoff,'level':l,**{k:(['L'+str(l)+'_'+val for val in entry[k]] if k in ('source_ids','target_ids') else entry[k]) for k in entry}})
        matches[str(l)]={'matched_prev_current':len(set(current_ids.values()) & set(old.values())) if old else 0,
                         'current_clusters':len(set(p.values()))}
        # Strip prefix for prev next loop? storing prefix and then would double prefix;
        # store original persistent without prefix; handled below.
        ids_by_level[-1]=current_ids
    return ids_by_level,events,matches,next_serial


def hierarchy_records(nodes,levels,pids,labels,cutoff):
    nd={n['id']:n for n in nodes}
    result=[]
    for l,assignment in enumerate(levels):
        groups=defaultdict(list)
        for v,g in assignment.items(): groups[g].append(v)
        for g,members in sorted(groups.items()):
            members=sorted(members)
            par=None
            if l>0:par='L'+str(l-1)+'_'+pids[l-1][levels[l-1][members[0]]] if l<3 else 'L2_'+pids[2][levels[2][members[0]]]
            persistent=('L'+str(l)+'_'+pids[l][g]) if l<3 else pids[l][g]
            if l in (0,1):title,gloss=labels[(l,g)]
            elif l==2:
                title,gloss,_=name_from_members(members,nodes)
            else:
                n=nd[members[0]];title=n['surface_form'][:130];gloss=f'Exported {n["type"]} entity, observed by {cutoff}: {title}.'
            result.append({'id':persistent,'level':l,'parent_id':par,'member_ids':members,
                           'label':title,'gloss':gloss,'snapshot_cutoff':cutoff})
    return result


def null_label_coherence_by_variant(nodes,X,train_edges,held,articles,seed):
    ids=[n['id'] for n in nodes]
    variants={};models={}
    for typ in ['semantic','structure','joint']:
        pred=fit_coarse(ids,X,train_edges,12,seed=seed,variant=typ)
        asg=dict(zip(ids,map(int,pred)))
        coh=independent_coherence(nodes,articles,pred,seed=seed,n_null=16,cutoff=2024)
        variants[typ]={'coherence':coh,'heldout_hyperedge_normalized_connectivity':heldout_edge_compactness(held,asg),
                       'hypergraph_native_diagnostic':loss_metrics(train_edges,pred,ids)}
        models[typ]=pred
    return variants,models


def run(args):
    tic=time.perf_counter();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    g,articles,questions,gold=parse_archive(args.data)
    eda,snapshots=observe(g,articles,questions,gold,YEARS[:3])
    snapshots['2025']=snapshot_raw(g,2025)
    write_json(out/'eda_summary.json',eda)
    for y in YEARS:
        # 2025 retrieval-only snapshot additional to mandatory 3 longitudinal slices
        write_json(out/f'snapshot_stats_{y}.json',{'nodes':len(snapshots[str(y)]['nodes']), 'edges':len(snapshots[str(y)]['hyperedges'])})
    embeddings,encoder=semantic_embeddings(snapshots,seed=args.seed)
    # Freeze global holdout papers before any modeling; no ground truth or query text used.
    all_papers=sorted({str(e.get('provenance',{}).get('article_id','?')) for e in g['hyperedges']})
    rng=np.random.default_rng(42)
    test_papers=set(rng.choice(all_papers,size=max(1,round(.20*len(all_papers))),replace=False))
    write_json(out/'evaluation_split.json',{'heldout_provenance_article_ids':sorted(test_papers),'article_groups_total':len(all_papers),
               'split_seed':42,'test_fraction_of_papers':len(test_papers)/len(all_papers),'note':'Holdout is grouped at asserting-article ID; no edges from those articles in clustering. Gold reference answers used only after outputs frozen.'})
    prev_top={};prev_levels=None;prev_ids=None; serial=0;events_all=[]
    metrics={'dataset_sha256':hashlib.sha256(Path(args.data).read_bytes()).hexdigest(),
             'source':'original applicant-supplied Constructor data.zip','seed':args.seed,'encoder':encoder,
             'evaluation_protocol':{'gold_answers':'held out until retrieval scoring','article_holdout_seed':42,
                                    'level_budgets':[12,48,144,'singletons'],'cutoffs':YEARS,
                                    'coarse_model_selection':'fixed a priori; no tuning to evaluation test questions'},
             'snapshots':{},'temporal':{},'retrieval':None,'label_audit':{},'limitations':[]}
    comparisons={}
    for y in YEARS:
        key=str(y);snap=snapshots[key];nodes=snap['nodes'];edges=snap['hyperedges'];ids=[n['id'] for n in nodes];X=embeddings[key]
        train=[e for e in edges if str(e.get('provenance',{}).get('article_id','?')) not in test_papers]
        held=[e for e in edges if str(e.get('provenance',{}).get('article_id','?')) in test_papers]
        prior={v:prev_top[v] for v in ids if v in prev_top}
        coarse=fit_coarse(ids,X,train,12,seed=args.seed,variant='joint',prior_ids=list(prior),prior_partition=prior,temporal_weight=.08)
        levels=fit_hierarchy(nodes,train,X,coarse,seed=args.seed)
        check_laminar(levels,ids)
        pids,events,matches,serial=group_id_map(levels,prev_levels,prev_ids,serial,y)
        # event stable source IDs already stored without level prefix; prefix at serialization
        for ev in events:
            events_all.append({'snapshot':y,**ev})
        labels,evidence=generate_levels(nodes,levels,y,[{v:'L'+str(l)+'_'+s for v,s in idmap.items()} for l,idmap in enumerate(pids[:3])])
        audit=support_audit(evidence,nodes,levels,[{v:'L'+str(l)+'_'+s for v,s in idmap.items()} for l,idmap in enumerate(pids[:3])])
        hierarchy=hierarchy_records(nodes,levels,pids,labels,y)
        write_json(out/f'hierarchy_{y}.json',{'cutoff':y,'levels':[{'level':l,'n_clusters':len(set(d.values()))} for l,d in enumerate(levels)],
                                             'supernodes':hierarchy})
        write_json(out/f'label_evidence_{y}.json',evidence)
        summary=[]
        for l in range(3):
            collapsed=collapse_all(train,levels[l]);
            assert len(collapsed)==len(train)
            assert all(sum(c['multiplicity'].values())==c['original_arity'] for c in collapsed)
            assert all(len(set(c['coarse_members']))==len(c['coarse_members']) for c in collapsed)
            summary.append({'level':l,'n_edges':len(collapsed),'internal':sum(c['internal'] for c in collapsed),
                            'highorder_remaining':sum(len(c['coarse_members'])>=3 for c in collapsed)})
            if l==0:write_json(out/f'collapsed_edges_{y}_level0.json',collapsed)
        write_json(out/f'collapse_stats_{y}.json',summary)
        met={'n_nodes':len(ids),'n_train_edges':len(train),'n_heldout_edges':len(held),'n_total_edges':len(edges),
             'clusters_per_level':[len(set(d.values())) for d in levels],
             'heldout_normalized_connectivity':heldout_edge_compactness(held,dict(zip(ids,coarse))),
             'label_support_audit':audit,'native_loss':loss_metrics(train,coarse,ids),
             'coherence':independent_coherence(nodes,articles,coarse,seed=args.seed,n_null=30,cutoff=y),
             'robustness':robustness(nodes,X,train,coarse,seed=args.seed,n_runs=5) if y!=2025 else None,
             'edge_collapse_summary':summary}
        metrics['snapshots'][key]=met;metrics['label_audit'][key]=audit
        if prev_levels:
            metrics['temporal'][f'{YEARS[YEARS.index(y)-1]}_{y}']=cross_snapshot_ari_ci(prev_levels[0],levels[0],seed=args.seed)
        if y==2024:
            v,_=null_label_coherence_by_variant(nodes,X,train,held,articles,args.seed)
            metrics['ablations_2024']=v
            metrics['structural_null_2024']=native_structural_null(nodes,X,train,held,coarse,seed=args.seed,n_null=args.null_runs)
        if y==2025:
            # trained model frozen; only now uses questions and gold in ranking evaluation
            metrics['retrieval']=evaluate_retrieval(nodes,train,articles,questions,gold,levels[0])
            write_json(out/'retrieval_per_question.json',metrics['retrieval']['per_question'])
        prev_top=dict(zip(ids,map(int,coarse)));prev_levels=levels;prev_ids=pids
        print(f'{y}: {len(ids)} nodes, {len(train)} train + {len(held)} independent held-out edges; levels {[len(set(d.values())) for d in levels]}',flush=True)
    write_json(out/'temporal_events.json',{'events':events_all,'definition':'Evidence-overlap matching; split/merge are heuristic attribution not proof of scientific concept ontology evolution.',
                                          'persistent_identity':'Stable identifiers across snapshots for all supernode levels 0-2, original stable node identity at singleton level',
                                          'temporal_coupling':'Prior top-level cluster centroids warm-start new KMeans; top-level regularization discourages moving surviving nodes.'})
    metrics['elapsed_seconds']=round(time.perf_counter()-tic,2)
    metrics['limitations']=[
       'The 52-paper sample is narrow, with strongly article-linked extracted entities; labels describe membership not expert ontology.',
       'Independent article-title coherence still shares publication-derived vocabulary; no blind expert semantic rating was obtained.',
       'The structural label membership audit does not replace an independent semantic over-claim score; this is explicitly NOT_EVALUATED.',
       'With 5 perturbations, bootstrap confidence intervals are descriptive, not strong significance claims.',
       'February 2026 cutoff questions are evaluated using all data evidenced by end of 2025; unseen 2026-month data cannot be assumed available in February.',
       'Question types B require multi-claim source citation checking and are reported as not scored rather than guessed.',
       'Original hyperedge event identity retained at each coarse level; no unique inversion is possible from a clique projection alone.',
       'Supernode temporal matching events are heuristic, not verified real scientific birth/death events.'
    ]
    write_json(out/'metrics.json',metrics)
    make_figures(out,metrics)
    from src.report import write_reports
    write_reports(out,metrics)
    print('FINAL OUTPUTS at',out.absolute(),'seconds',metrics['elapsed_seconds'],flush=True)
    return metrics


def make_figures(out,met):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    years=YEARS[:3]
    fig,ax=plt.subplots(figsize=(7.5,3.5));xx=np.arange(3)
    ax.plot(xx,[met['snapshots'][str(y)]['n_nodes'] for y in years],marker='o',label='Nodes')
    ax.plot(xx,[met['snapshots'][str(y)]['n_total_edges'] for y in years],marker='s',label='Hyperedges')
    ax.set_xticks(xx,[str(y) for y in years]);ax.set_xlabel('Evidence cutoff year');ax.set_ylabel('Count')
    ax.set_title('Actual Constructor TKH: evidence-aware temporal growth');ax.legend(frameon=False);fig.tight_layout();fig.savefig(out/'fig_temporal_growth.png',dpi=180);plt.close(fig)
    abl=met.get('ablations_2024',{})
    fig,ax=plt.subplots(figsize=(7.5,3.5));names=list(abl)
    scores=[abl[k]['coherence'].get('effect_delta') for k in names]
    ax.bar(names,[0 if x is None else x for x in scores]);ax.axhline(0,color='black',linewidth=.7)
    ax.set_title('Independent article-title coherence: gain over random-size null (2024)');ax.set_ylabel('Mean cosine gain');fig.tight_layout();fig.savefig(out/'fig_coherence.png',dpi=180);plt.close(fig)
    r=met['retrieval']['summary']
    fig,ax=plt.subplots(figsize=(7.5,3.4))
    ax.bar(['Flat','Hierarchical'],[r['flat_hit_at_5'],r['hier_hit_at_5']]);ax.set_ylim(0,1);ax.set_ylabel('Hit@5 (Type A questions)')
    ax.set_title('Actual held-out retrieval queries (2025-safe data)');fig.tight_layout();fig.savefig(out/'fig_retrieval.png',dpi=180);plt.close(fig)


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='inputs/data.zip');p.add_argument('--out',default='outputs');p.add_argument('--seed',type=int,default=17);p.add_argument('--null-runs',type=int,default=8)
    run(p.parse_args())

if __name__=='__main__':main()
