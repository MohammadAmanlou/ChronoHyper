"""Reproducible graph-projection representation audit: counts, not information-theoretic entropy."""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from collections import Counter
from itertools import combinations
from pathlib import Path
from zipfile import ZipFile

YEARS=(2020,2022,2024)

def audit(project='.',out='research_outputs/projection_loss'):
    root=Path(project);out=Path(out)
    if not out.is_absolute():out=root/out
    with ZipFile(root/'inputs/data.zip') as z:
        g=json.loads(z.read('data/tkh_collection10.json'))
    node_year={n['id']:int(n['first_seen_year']) for n in g['nodes']}
    edges=g['hyperedges']
    def compute(es):
        arities=Counter(len(e['members']) for e in es)
        pairs=Counter()
        for edge in es:
            members=edge['members']
            if len(set(members))!=len(members) or any(i not in node_year for i in members):
                raise ValueError('Invalid original hyperedge membership')
            pairs.update(combinations(sorted(members),2))
        n=len(es)
        projected=sum(v for v in pairs.values())
        return {'native_events':n,'native_event_arities':{str(k):v for k,v in sorted(arities.items())},
                'higher_order_events_arity_at_least_3':sum(v for k,v in arities.items() if k>=3),
                'higher_order_fraction':sum(v for k,v in arities.items() if k>=3)/n if n else None,
                'native_incidence_occurrences':sum(k*v for k,v in arities.items()),
                'max_hyperedge_arity':max(arities) if arities else None,
                'clique_pair_occurrences':projected,'simple_unique_pairs':len(pairs),
                'repeated_pair_occurrences_collapsed_by_simple_graph':projected-len(pairs),
                'pairs_represented_by_multiple_source_events':sum(v>1 for v in pairs.values()),
                'pair_expansion_per_native_event':projected/n if n else None}
    years={}
    for y in YEARS:
        allowed={i for i,v in node_year.items() if v<=y}
        es=[e for e in edges if int(e['year'])<=y and int(e.get('provenance',{}).get('article_year',e['year']))<=y
            and all(i in allowed for i in e['members'])]
        years[str(y)]=compute(es)
    doc={'schema':'chronohyper_pairwise_projection_loss_v1',
         'dataset_sha256':hashlib.sha256((root/'inputs/data.zip').read_bytes()).hexdigest(),
         'scope':'Original Constructor hypergraph events; native incident groupings vs untyped, unprovenanced, undirected simple clique graph',
         'method':'Each native arity-r event emits choose(r,2) undirected pairs. Counts omit article IDs, relation IDs and labels in flattened graph.',
         'interpretation':'Flattening removes identifiable multi-party event boundaries and provenance/relation attributes unless they are stored externally. This is a representation comparison, not a proven entropy value or downstream loss.',
         'global':compute(edges),'snapshots':years,
         'not_claimed':'Weighted/clique projections retaining per-event IDs could reconstruct incidence; this audit targets ordinary untyped pairwise projection, not every possible encoding.'}
    out.mkdir(parents=True,exist_ok=True)
    (out/'projection_loss.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7.4,4.4),layout='constrained')
    ratios=[years[str(y)]['pair_expansion_per_native_event'] for y in YEARS]
    bars=ax.bar([str(y) for y in YEARS],ratios,color=['#138C88','#416AB4','#8057AE'],width=.54)
    for rect,value in zip(bars,ratios):ax.text(rect.get_x()+rect.get_width()/2,rect.get_height()+.6,f'{value:.1f}x',ha='center',weight='bold')
    ax.set_ylabel('Clique pair occurrences / original hyperedges')
    ax.set_ylim(0,max(ratios)*1.18);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    ax.set_title('Expanding native higher-order events into pairwise cliques',loc='left',fontweight='bold')
    fig.text(.015,.015,'Native event identity, relation and provenance cannot be inferred from an untyped simple pair graph.',fontsize=7.5,color='#526078')
    fig.savefig(out/'projection_loss.svg',format='svg',bbox_inches='tight')
    plt.close(fig)
    print(json.dumps({'global':doc['global'],'snapshots':{k:{'native_events':v['native_events'],'clique_pair_occurrences':v['clique_pair_occurrences'],'pair_expansion_per_native_event':v['pair_expansion_per_native_event']} for k,v in years.items()}},indent=2))
    return doc

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--project',default='.')
    ap.add_argument('--out',default='research_outputs/projection_loss')
    a=ap.parse_args();audit(a.project,a.out)