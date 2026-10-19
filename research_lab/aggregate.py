#!/usr/bin/env python3
"""Preserve and summarize ALL scientific variants incl. failures; no winning-only reporting.

Run after experiment_suite. Aggregation never recomputes models or uses gold answers.
"""
import argparse,csv,json,math,statistics,hashlib
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FIELDS=['heldout_normalized_connectivity_lower_better',
        'independent_article_title_view_coherence_higher_better',
        'cross_year_shared_node_ari','elapsed_seconds',
        'fraction_train_events_internal','n_clusters','n_train_edges','n_heldout_papers']

def write_csv(path,items):
    path.parent.mkdir(parents=True,exist_ok=True)
    header=sorted({k for x in items for k in x}) if items else ['run_id','status']
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=header);w.writeheader()
        for r in items:w.writerow({k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v) for k,v in r.items()})

def paired_article_bootstrap(ref,alt,seed=7):
    common=sorted(set(ref)&set(alt))
    if len(common)<2:return None
    # Difference = (candidate heldout cut - reference heldout cut), lower is better.
    diffs=np.array([alt[p]-ref[p] for p in common],dtype=float)
    rng=np.random.default_rng(seed)
    boot=rng.choice(diffs,size=(1000,len(diffs)),replace=True).mean(axis=1)
    return {'n_papers':len(common),'delta_cut_candidate_minus_ref':float(diffs.mean()),
            'ci95':[float(np.percentile(boot,2.5)),float(np.percentile(boot,97.5))],
            'sign':'negative means better than reference, positive means worse',
            'unit':'asserting paper; multiple edges per paper are NOT independent samples'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='research_outputs');p.add_argument('--reference',default='native_joint_70');args=p.parse_args()
    root=Path(args.out);prot=json.loads((root/'protocol.json').read_text(encoding='utf-8'))
    expected=[(m,s) for m in prot['method_ids'] for s in prot['seeds']]
    status=[];rows=[];results={}
    for name,seed in expected:
        label=f'{name}__seed{seed}';dir=root/'runs'/label
        sp=dir/'status.json'
        if not sp.exists():
            status.append({'run_id':label,'method':name,'seed':seed,'status':'MISSING','error':'No run status'});continue
        state=json.loads(sp.read_text(encoding='utf-8'))
        status.append({'run_id':label,'method':name,'seed':seed,'status':state.get('status'),
                       'error':state.get('exception',''),'elapsed_seconds':state.get('elapsed_seconds')})
        if state.get('status')=='complete':
            r=json.loads((dir/'metrics.json').read_text(encoding='utf-8'))
            if r.get('status')!='complete':raise RuntimeError('Mismatched complete status '+label)
            for record in r['years']:
                results[(name,seed,record['year'])]=record
                rows.append({k:record.get(k) for k in ['run_id','seed','model','family','year',*FIELDS,'projected_pair_events',
                                                        'n_nodes','n_heldout_edges','train_highorder_events_still_3plus_coarse']})
    write_csv(root/'experiment_registry.csv',status)
    write_csv(root/'all_runs.csv',rows)
    buckets=defaultdict(list)
    for r in rows:buckets[(r['model'],r['year'])].append(r)
    sumrows=[]
    for (m,y),grp in sorted(buckets.items()):
        result={'model':m,'year':y,'n_seeds':len(grp),
                'status':'COMPLETE' if len(grp)==len(prot['seeds']) else 'PARTIAL',
                'expected_seeds':len(prot['seeds'])}
        for f in FIELDS:
            values=[float(a[f]) for a in grp if a.get(f) is not None]
            result[f+'_mean']=float(statistics.mean(values)) if values else None
            result[f+'_sd_over_seeds']=float(statistics.stdev(values)) if len(values)>1 else None
            result[f+'_min']=min(values) if values else None
            result[f+'_max']=max(values) if values else None
        sumrows.append(result)
    write_csv(root/'method_summary.csv',sumrows)
    comparisons=[]
    for (method,seed,year),rec in sorted(results.items()):
        if method==args.reference:continue
        ref=results.get((args.reference,seed,year))
        if not ref:continue
        delta=paired_article_bootstrap(ref['heldout_paper_scores'],rec['heldout_paper_scores'],seed=seed+year)
        if delta:comparisons.append({'method':method,'reference':args.reference,'seed':seed,'year':year,**delta})
    write_csv(root/'paired_paper_bootstrap.csv',comparisons)
    # Non-inferiority is NOT enough to assert admissions significance. Strict Pareto
    # front only among 2024 methods with complete seed set; coherence up, cut down, runtime down.
    yr=max(prot['years']);eligible=[r for r in sumrows if r['year']==yr and r['status']=='COMPLETE']
    dimension=[('heldout_normalized_connectivity_lower_better_mean',-1),
               ('independent_article_title_view_coherence_higher_better_mean',1),
               ('elapsed_seconds_mean',-1)]
    pareto=[]
    for a in eligible:
        def dominates(b,a):
            if any(b.get(z) is None or a.get(z) is None for z,_ in dimension):return False
            return (all((b[z]-a[z])*sign>=-1e-12 for z,sign in dimension)
                    and any((b[z]-a[z])*sign>1e-12 for z,sign in dimension))
        if not any(dominates(other,a) for other in eligible if other['model']!=a['model']):pareto.append(a['model'])
    (root/'pareto_front.json').write_text(json.dumps({'year':yr,'models':pareto,'dimensions':dimension,
         'caution':'Descriptive 3-metric Pareto, same 52-paper source; not statistical discovery, does not measure interpretability or actual retrieval performance.'},indent=2),encoding='utf-8')
    # Matplotlib one chart per file, no claimed tuned display values.
    for metric,label,file in [
        ('heldout_normalized_connectivity_lower_better_mean','Heldout paper normalized hyperedge cut (lower is better)','fig_cut.png'),
        ('independent_article_title_view_coherence_higher_better_mean','Article-title coherence proxy (higher is better)','fig_title_coherence.png'),
        ('elapsed_seconds_mean','Model run time per snapshot (seconds; lower is better)','fig_runtime.png')]:
        subset=[x for x in sumrows if x['year']==yr and x.get(metric) is not None]
        if subset:
            fig,ax=plt.subplots(figsize=(max(9,len(subset)*.8),4.8))
            ax.bar(range(len(subset)),[x[metric] for x in subset])
            ax.set_xticks(range(len(subset)),[x['model'] for x in subset],rotation=65,ha='right')
            ax.set_ylabel(label);ax.set_title('All attempted methods (completed only; failures listed separately)')
            fig.tight_layout();fig.savefig(root/file,dpi=160);plt.close(fig)
    errs=[x for x in status if x['status']!='complete']
    lines=['# Research experiment registry — all outcomes, not a winners-only report','',
           f"**Original-data SHA256**: `{prot['data_sha256']}`",
           f"**Frozen embeddings seed**: {prot['embedding_seed']}",
           f"**Held-out asserting papers split seed**: {prot['paper_holdout_seed']}",
           f"**Expected executions**: {len(expected)}; completed {len(expected)-len(errs)}; failed/missing {len(errs)}",'',
           '## ALL method/year results','',
           '| Method | Year | Seeds complete | Heldout hyperedge cut ↓ | Independent-view title coherence ↑ | Temporal ARI ↑ | Seconds/snapshot ↓ |',
           '|---|---:|---:|---:|---:|---:|---:|']
    fmt=lambda v: '—' if v is None else f'{v:.4f}'
    for r in sorted(sumrows,key=lambda d:(d['year'],d['model'])):
        lines.append(f"| {r['model']} | {r['year']} | {r['n_seeds']}/{r['expected_seeds']} | "+
                     f"{fmt(r.get('heldout_normalized_connectivity_lower_better_mean'))} | "+
                     f"{fmt(r.get('independent_article_title_view_coherence_higher_better_mean'))} | "+
                     f"{fmt(r.get('cross_year_shared_node_ari_mean'))} | {fmt(r.get('elapsed_seconds_mean'))} |")
    lines += ['',f'## Descriptive Pareto front on {yr}','',', '.join(pareto) if pareto else 'Not available; insufficient completed methods','',
              '## All failed / missing jobs','']
    lines += ['- '+(x['run_id']+' — '+x['status']+': '+x['error']) for x in errs] or ['- None.']
    lines+=['', '## Interpretation and limits','',
            '- Do not select a model based only on the 18 previously opened reference questions. Those are exploratory data after inspection.',
            '- The article-title coherence is a second feature view, not blinded expert semantic faithfulness; the latter remains separately unverified until actual annotated review.',
            '- The same paper set underlies every seed; seed standard deviations are NOT cross-corpus generalization confidence intervals.',
            '- Per-paper bootstrap CI is descriptive for the holdout paper subset; clustered edge/node dependence persists.',
            '- Full native hyperedge cut, hierarchy validity P1/P2, collapsed edge conservation and temporal identity must be verified again for any selected method before final claimed T2-T4 performance.',
            '- Clique projection is unweighted: a hyperedge of arity n contributes n(n-1)/2 pair edges and overweights large events. This is a lossy diagnostic, not a fair loss-normalized substitute.',
            '- A high ARI can result from a frozen partition even with bad scientific responsiveness: inspect cut/coherence trade-off jointly.',
            '- No output here proves a PhD offer, supervisor acceptance or funding.']
    (root/'RESEARCH_COMPARISON_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Completed',len(expected)-len(errs),'of',len(expected),'executions; all recorded in',root,'; Pareto:',pareto)

if __name__=='__main__':main()
