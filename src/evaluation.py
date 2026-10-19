"""Independent title-source coherence, null models, robustness, and diagnostics.
No gold reference method list is consumed here or during model construction.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score
from scipy.sparse import vstack,csr_matrix
from src.core import fit_coarse, hyper_connectivity,partition_ari


def _bootstrap(values,seed=101,reps=1000):
    if not len(values):return {'mean':None,'ci95':[None,None],'n':0}
    a=np.asarray(values,dtype=float)
    rng=np.random.default_rng(seed)
    means=rng.choice(a,size=(reps,len(a)),replace=True).mean(axis=1)
    return {'mean':float(a.mean()),'ci95':[float(np.percentile(means,2.5)),float(np.percentile(means,97.5))],'n':len(a),
            'individual_values':[float(x) for x in a]}


def article_title_vectors(nodes,articles,cutoff):
    """Evaluation-only signal: independent publication titles, not clustering node surface features.
    Distinct features and source; still not independent expert validation (explicitly disclose).
    """
    aid={str(a['id']):str(a['title']) for a in articles if int(a['year']) <= cutoff}
    vec=TfidfVectorizer(analyzer='char',ngram_range=(3,5),min_df=1,sublinear_tf=True)
    labels=sorted(aid)
    titles=vec.fit_transform([aid[k] for k in labels])
    index={k:i for i,k in enumerate(labels)}
    rows=[]; eligible=[]
    for i,n in enumerate(nodes):
        provenance=n.get('provenance',{}).get('articles',[])
        ix=sorted(set(index[str(a)] for a in provenance if str(a) in index))
        if ix:
            y=titles[ix].mean(axis=0)
            rows.append(csr_matrix(y)); eligible.append(i)
        else:rows.append(csr_matrix((1,titles.shape[1])))
    Y=vstack(rows,format='csr')
    norms=np.sqrt(Y.multiply(Y).sum(axis=1)).A1
    from scipy.sparse import diags
    Y=diags(1/np.maximum(norms,1e-12))@Y
    return Y, np.asarray(eligible,dtype=int)


def pair_similarity_by_clusters(Y, labels, eligible, seed=2001, max_pairs=3000):
    rng=np.random.default_rng(seed)
    pools=defaultdict(list)
    for i in eligible:pools[int(labels[i])].append(int(i))
    valid=[v for v in pools.values() if len(v)>=2]
    if not valid:return None
    pairs=[]
    # weighted roughly proportional to number of scientific nodes per cluster, not square-size dominated
    weights=np.array([len(p) for p in valid],dtype=float)
    weights=weights/weights.sum()
    for _ in range(max_pairs):
        pool=valid[int(rng.choice(len(valid),p=weights))]
        a,b=rng.choice(pool,size=2,replace=False)
        pairs.append((a,b))
    a=np.asarray([x for x,y in pairs]);b=np.asarray([y for x,y in pairs]);
    scores=np.asarray(Y[a].multiply(Y[b]).sum(axis=1)).ravel()
    return float(scores.mean())


def independent_coherence(nodes,articles,labels,seed=17,n_null=40,cutoff=2024):
    Y,eligible=article_title_vectors(nodes,articles,cutoff)
    real=pair_similarity_by_clusters(Y,labels,eligible,seed=seed)
    rng=np.random.default_rng(seed+301)
    null=[]
    for j in range(n_null):
        shuffled=rng.permutation(labels)  # preserves cluster sizes exactly
        null.append(pair_similarity_by_clusters(Y,shuffled,eligible,seed=seed+100+j,max_pairs=1000))
    null=[x for x in null if x is not None]
    if real is None:return {'status':'not_evaluated','reason':'No source-title labels'}
    p=(1+sum(x>=real for x in null))/(len(null)+1) if null else None
    return {'source':'provenance-linked scientific article titles, char 3-5-gram TF-IDF; not clustering node embeddings',
            'n_valid_nodes':len(eligible),'observed':real,'random_size_matched_mean':float(np.mean(null)) if null else None,
            'random_size_matched_sd':float(np.std(null,ddof=1)) if len(null)>1 else None,
            'effect_delta':float(real-np.mean(null)) if null else None,
            'randomization_p_ge':p,'null_draws':len(null),
            'limitations':'Article titles are distinct from the input surface forms/embeddings but correlated by publication; this is an independent evidence VIEW, not human-judged semantic correctness. Null labels exactly preserve sizes.'}


def incidence_degree_preserving_shuffle(edges,seed=17,multiple=5):
    """Bipartite double-edge swaps, preserve hyperedge arity & per-node occurrence degree exactly.
    Restrict swaps to same relation type and asserting paper-year when possible.
    """
    rng=np.random.default_rng(seed)
    ed=[{**e,'members':list(e['members'])} for e in edges]
    buckets=defaultdict(list)
    for i,e in enumerate(ed):
        buckets[(e['relation_type'],e.get('provenance',{}).get('article_year',e['year']))].append(i)
    num_swaps=0
    for bucket in buckets.values():
        if len(bucket)<2:continue
        attempts=multiple*sum(len(ed[i]['members']) for i in bucket)
        for _ in range(attempts):
            u,v=rng.choice(bucket,2,replace=False)
            su,sv=set(ed[u]['members']),set(ed[v]['members'])
            ou=list(su-sv);ov=list(sv-su)
            if not ou or not ov:continue
            a=ou[int(rng.integers(len(ou)))];b=ov[int(rng.integers(len(ov)))]
            j=ed[u]['members'].index(a);k=ed[v]['members'].index(b)
            ed[u]['members'][j]=b;ed[v]['members'][k]=a
            num_swaps+=1
    return ed,num_swaps


def heldout_edges(edges,seed=42):
    """Group by provenance article to avoid evaluating training edges from same heldout paper."""
    papers=sorted({str(e.get('provenance',{}).get('article_id','?')) for e in edges})
    rng=np.random.default_rng(seed)
    held=set(rng.choice(papers,size=max(1,int(round(.20*len(papers)))),replace=False))
    train=[e for e in edges if str(e.get('provenance',{}).get('article_id','?')) not in held]
    test=[e for e in edges if str(e.get('provenance',{}).get('article_id','?')) in held]
    return train,test,held


def heldout_edge_compactness(held,assign):
    values=[]
    for e in held:
        if len(e['members'])>=2:
            values.append((len({assign[x] for x in e['members']})-1)/(len(e['members'])-1))
    return float(np.mean(values)) if values else None


def robustness(nodes,X,train_edges,reference,seed=17,variant='joint',n_runs=5):
    ids=[n['id'] for n in nodes]
    values=[]
    for s in range(n_runs):
        rng=np.random.default_rng(seed+s*73)
        keep=rng.choice(len(train_edges),size=int(round(.90*len(train_edges))),replace=False)
        perturbed=[train_edges[int(i)] for i in sorted(keep)]
        pred=fit_coarse(ids,X,perturbed,12,seed=seed,variant=variant)
        values.append(adjusted_rand_score(reference,pred))
    return {'ari':_bootstrap(values,seed=seed+1),'deleted_fraction':.10,'seeds':n_runs,
            'interpretation':'5 independent deletion draws, all nodes held fixed; bootstrap CI over 5 draws is descriptive and uncertain.'}


def cross_snapshot_ari_ci(prev,current,seed=67,reps=250):
    common=sorted(set(prev)&set(current))
    if len(common)<3:return {'ari':None,'ci95':[None,None],'nodes':len(common)}
    a=np.array([prev[x] for x in common]);b=np.array([current[x] for x in common]);score=float(adjusted_rand_score(a,b))
    # Node bootstrap is an approximation, especially for nodes from same articles.
    rng=np.random.default_rng(seed); vals=[]
    for _ in range(reps):
        ix=rng.integers(0,len(common),size=len(common));vals.append(adjusted_rand_score(a[ix],b[ix]))
    return {'ari':score,'ci95':[float(np.percentile(vals,2.5)),float(np.percentile(vals,97.5))],
            'nodes':len(common),'bootstrap_unit':'node (shared provenance means this may underestimate uncertainty)'}


def native_structural_null(nodes,X,original_train,heldout,original_labels,seed=171,n_null=8):
    ids=[n['id'] for n in nodes]
    actual=heldout_edge_compactness(heldout,dict(zip(ids,original_labels)))
    if actual is None:return {'status':'not_evaluated','reason':'No heldout edges'}
    values=[];swaps=[]
    orig_degrees=Counter(v for e in original_train for v in e['members'])
    for j in range(n_null):
        shuffled,n_swap=incidence_degree_preserving_shuffle(original_train,seed=seed+j,multiple=3)
        new_degrees=Counter(v for e in shuffled for v in e['members'])
        assert orig_degrees==new_degrees
        assert all(len(a['members'])==len(b['members']) for a,b in zip(original_train,shuffled))
        pred=fit_coarse(ids,X,shuffled,12,seed=17,variant='joint')
        values.append(heldout_edge_compactness(heldout,dict(zip(ids,pred))))
        swaps.append(n_swap)
    val=[x for x in values if x is not None]
    return {'measure':'Heldout paper hyperedge normalized connectivity (smaller is better)',
            'observed':actual,'null_mean':float(np.mean(val)) if val else None,
            'null_scores':val,'shuffle_count':len(val),'successful_swaps':swaps,
            'randomization_p_le':(1+sum(v<=actual for v in val))/(len(val)+1) if val else None,
            'constraints':'exact node incidence degrees, exact hyperedge arities; swaps within relation type and asserting article year',
            'limitations':'Constrained null with few repeats; heldout paper split independent of cluster-training hyperedges. Semantic features of heldout paper nodes may still overlap.'}


def loss_metrics(edges,labels,ids):
    mapping=dict(zip(ids,labels))
    net_count=len(edges)
    sizes=[len(e['members']) for e in edges]
    ratio=sum((len({mapping[x] for x in e['members']})-1) for e in edges)/max(1,sum(max(1,k-1) for k in sizes))
    return {'normalized_hyperedge_connectivity':ratio,'n_hyperedges':net_count,
            'hyperedges_with_3plus_endpoints':sum(x>=3 for x in sizes),
            'fraction_of_3plus_hyperedge_events_lost_as_unique_when_cliquified':sum(x>=3 for x in sizes)/max(1,net_count),
            'pairwise_projection_note':'Clique expansion is many-to-one: original event ID, relation grouping, and multiplicity provenance are not uniquely recoverable. Fraction is diagnostic, not exact information-theoretic loss.'}
