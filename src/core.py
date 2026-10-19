"""Hypergraph-native refinement, collapse, hierarchies and temporal identity.
No pairwise projection is used in primary clustering. Most input is public science metadata.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import itertools
import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score


def edge_collapse(edge, membership):
    """Preserve an original event, endpoint multiplicity, source, and relation at coarser level."""
    counts = Counter(membership[x] for x in edge['members'])
    return dict(id=edge['id'], original_arity=len(edge['members']),
                coarse_members=sorted(counts), multiplicity=dict(sorted(counts.items())),
                internal=len(counts)==1, relation_type=edge['relation_type'],
                provenance=edge.get('provenance', {}))


def collapse_all(edges, memberships):
    return [edge_collapse(edge, memberships) for edge in edges]


def hyper_connectivity(edges, membership):
    """Native hyperedge connectivity-1 objective, normalized per incidence."""
    total = sum(max(0, len({membership[v] for v in edge['members']}) - 1) for edge in edges)
    return total/max(1, len(edges))


def _incidence(edge_list, ids):
    adj=defaultdict(list)
    for j,edge in enumerate(edge_list):
        for x in edge['members']:
            if x in ids:
                adj[x].append(j)
    return adj


def kmeans_initial(X,k,random_state,centers=None):
    k=min(k,len(X))
    if k<=1: return np.zeros(len(X),dtype=int)
    kw=dict(n_clusters=k,random_state=random_state,max_iter=70,algorithm='lloyd')
    if centers is not None and len(centers)==k:
        kw.update(init=np.asarray(centers),n_init=1)
    else: kw.update(n_init=3)
    return KMeans(**kw).fit_predict(X).astype(int)


def refine_native(ids, X, edges, labels, semantic=0.77, hyper=0.23,
                  temporal=0.0, previous=None, rounds=2, cap_share=0.43):
    """Sequential bounded local improvement of normalized cosine+native λ-1.
    Only affected hyperedges recomputed after a move; no clique expansion.
    Move scoring evaluates data-dependent candidate labels and avoids emptying clusters.
    """
    labels=np.asarray(labels,dtype=int).copy()
    k=int(labels.max())+1
    if k<2: return labels
    edge_list=[e for e in edges if len(e['members'])>=2]
    inc=_incidence(edge_list,set(ids))
    pos={x:i for i,x in enumerate(ids)}
    sums=np.zeros((k,X.shape[1])); sizes=np.bincount(labels,minlength=k).astype(int)
    for i,g in enumerate(labels): sums[g]+=X[i]
    # T4 is operational inside the solver: actual coarse hyperedge multiplicities
    # are the mutable state used for native connectivity cost in each candidate move.
    # This is the SAME collapse function exported to collapsed_edges_<year>_level0.json.
    memberships={ids[i]:int(labels[i]) for i in range(len(ids))}
    ebins=[]
    for e in edge_list:
        collapsed=edge_collapse(e,memberships)
        ebins.append(Counter(collapsed['multiplicity']))
    max_size=max(int(np.ceil(cap_share*len(ids))),int(np.ceil(len(ids)/k*1.05)))
    norm=max(float(np.linalg.norm(X,axis=1).mean()), 1e-9)
    prev=np.asarray(previous,dtype=int) if previous is not None else None
    # deterministic node order, higher incidence first, stable tie by ID
    order=sorted(range(len(ids)),key=lambda i:(-len(inc[ids[i]]),ids[i]))
    for _ in range(rounds):
        changed=0
        centers=sums/np.maximum(sizes[:,None],1)
        c_norm=np.linalg.norm(centers,axis=1,keepdims=True)
        centers=centers/np.maximum(c_norm,1e-12)
        for i in order:
            src=int(labels[i]); vertex=ids[i]
            if sizes[src]<=1: continue
            # candidates from semantic top-3 and native incident edges. Keep small.
            sem_scores=centers@X[i]
            candidates=set(np.argsort(sem_scores)[-min(4,k):].tolist())
            for j in inc[vertex]: candidates.update(ebins[j])
            candidates.add(src)
            best=src; best_score=0.0
            for dst in candidates:
                dst=int(dst)
                if dst==src or sizes[dst]>=max_size:continue
                delta_sem=float((sem_scores[dst]-sem_scores[src])) * semantic
                delta_h=0
                for j in inc[vertex]:
                    ctr=ebins[j]
                    loss_before=len(ctr)
                    loss_after=loss_before-(1 if ctr[src]==1 else 0)+(1 if ctr.get(dst,0)==0 else 0)
                    delta_h+=loss_after-loss_before
                # Hyperedge connectivity improvement; bound influence of nodes with huge incidence
                delta_h=-hyper*delta_h/max(1.0,len(inc[vertex]))
                delta_t=0.0
                if prev is not None and prev[i]>=0:
                    delta_t=temporal*((int(dst==prev[i]))-(int(src==prev[i])))
                balance=0.015*(sizes[src]-sizes[dst])/max(1,len(ids))
                score=delta_sem+delta_h+delta_t+balance
                if score>best_score+1e-8:
                    best_score=score;best=dst
            if best!=src:
                for j in inc[vertex]:
                    ebins[j][src]-=1
                    if ebins[j][src]==0:del ebins[j][src]
                    ebins[j][best]+=1
                sums[src]-=X[i];sums[best]+=X[i]
                sizes[src]-=1;sizes[best]+=1
                labels[i]=best;changed+=1
        if changed==0:break
    return labels


def fit_coarse(ids, X, edges, k, seed=17, variant='joint', prior_ids=None,
               prior_partition=None, temporal_weight=.08):
    """Fixed semantic space. Initial centers from previous clusters and temporal move penalty.
    Note: prior centers computed on current shared nodes for consistent feature space.
    """
    centers=None;prev=None
    if prior_partition and variant=='joint' and len(prior_ids or [])>0:
        prev=np.array([prior_partition.get(v,-1) for v in ids],dtype=int)
        cs=[]
        for lab in range(k):
            sel=np.where(prev==lab)[0]
            if len(sel): cs.append(X[sel].mean(axis=0))
            else: cs.append(X[np.random.default_rng(seed+lab).integers(len(ids))])
        centers=np.asarray(cs)
        centers=centers/np.maximum(np.linalg.norm(centers,axis=1,keepdims=True),1e-12)
    labels=kmeans_initial(X,k,seed,centers)
    if variant=='semantic':return labels
    if variant=='structure':
        # hyperedge connectivity dominates; semantics stabilises isolated nodes
        return refine_native(ids,X,edges,labels,semantic=.12,hyper=.88,rounds=3)
    if variant=='joint':
        return refine_native(ids,X,edges,labels,semantic=.70,hyper=.30,
                             temporal=temporal_weight if prev is not None else 0,
                             previous=prev,rounds=3)
    raise ValueError(variant)


def fit_hierarchy(nodes,edges,X,top_labels,seed=17):
    """Top12 -> up to48 -> up to144 -> n singleton, strictly nested; no overlapping.
    Level1 and level2 split *within each parent*; local hyperedge coarsening is used
    to constrain child reassignments through refine_native.
    """
    ids=[x['id'] for x in nodes]
    groups0={i:int(top_labels[j]) for j,i in enumerate(ids)}
    n=len(ids); lookup={x:i for i,x in enumerate(ids)}
    levels=[groups0]
    old=groups0
    for splits in [4,3]:
        new={};next_gid=0
        parent_members=defaultdict(list)
        for ident,c in old.items():parent_members[c].append(ident)
        for parent, members in sorted(parent_members.items()):
            ix=[lookup[v] for v in members]
            k=min(splits,len(members))
            if k==1:
                for v in members:new[v]=next_gid
                next_gid+=1;continue
            subX=X[ix]
            local_edges=[e for e in edges if len(set(e['members'])&set(members))>=2]
            # Restrict boundary to this parent; partial edges are still one high-order incidence.
            local_edges=[{**e,'members':[v for v in e['members'] if v in set(members)]} for e in local_edges]
            init=kmeans_initial(subX,k,seed+int(parent))
            refined=refine_native(members,subX,local_edges,init,rounds=1)
            for v,c in zip(members,refined):new[v]=next_gid+int(c)
            next_gid+=k
        old=new;levels.append(new)
    singleton={ident:i for i,ident in enumerate(ids)}
    levels.append(singleton)
    return levels


def check_laminar(levels,ids,budgets=(12,48,144,None)):
    base=set(ids)
    for i,level in enumerate(levels):
        if set(level)!=base:raise AssertionError('Missing or extra members')
        if len(set(level.values()))>(budgets[i] or len(ids)):raise AssertionError('Level size exceeded')
        if i:
            parent_of={}
            for v,c in level.items():
                p=levels[i-1][v]
                if c in parent_of and parent_of[c]!=p:raise AssertionError('Non-laminar')
                parent_of[c]=p
    if len(set(levels[-1].values()))!=len(ids):raise AssertionError('Leaves must be singleton')
    return True


def temporal_match(prev,current,old_ids,next_serial,minimum=.03):
    """Stable identity from overlap/Hungarian; event attribution separately uses many-to-many overlap.
    prev/current maps node id->cluster local int, for same cutoff partition level 0.
    """
    A=sorted(set(prev.values())) if prev else []
    B=sorted(set(current.values()))
    sets_a={g:{v for v,c in prev.items() if c==g} for g in A}
    sets_b={g:{v for v,c in current.items() if c==g} for g in B}
    weight=np.zeros((len(A),len(B)))
    for ia,a in enumerate(A):
        for ib,b in enumerate(B):
            intersect=len(sets_a[a]&sets_b[b])
            if intersect:weight[ia,ib]=intersect/len(sets_a[a]|sets_b[b])
    assigned={};matches=[]
    if A and B:
        rows,cols=linear_sum_assignment(-weight)
        for i,j in zip(rows,cols):
            if weight[i,j]>=minimum:
                assigned[B[j]]=old_ids[A[i]]
                matches.append((A[i],B[j],float(weight[i,j])))
    for b in B:
        if b not in assigned:
            assigned[b]=f'concept_{next_serial:04d}';next_serial+=1
    events=[]
    if not prev:
        events=[{'event':'birth','source_ids':[],'target_ids':[assigned[b]], 'member_count':len(sets_b[b])} for b in B]
    else:
        for b in B:
            parents=[a for a in A if len(sets_a[a]&sets_b[b])>=max(2,round(.12*len(sets_b[b])))]
            old_identity=[old_ids[a] for a in parents]
            if len(parents)>1:events.append({'event':'merge','source_ids':old_identity,'target_ids':[assigned[b]],'common_members':int(sum(len(sets_a[a]&sets_b[b]) for a in parents))})
            if not parents:events.append({'event':'birth','source_ids':[],'target_ids':[assigned[b]],'member_count':len(sets_b[b])})
            elif any(b2==b for a,b2,w in matches):
                a=next(a for a,b2,w in matches if b2==b)
                growth=len(sets_b[b]-sets_a[a])
                if growth>0:events.append({'event':'growth','source_ids':[old_ids[a]],'target_ids':[assigned[b]],'new_members':growth})
        for a in A:
            children=[b for b in B if len(sets_a[a]&sets_b[b])>=max(2,round(.12*len(sets_a[a])))]
            if len(children)>1:events.append({'event':'split','source_ids':[old_ids[a]],'target_ids':[assigned[b] for b in children]})
            if not children:events.append({'event':'death','source_ids':[old_ids[a]],'target_ids':[]})
    return assigned,events,next_serial,weight


def partition_ari(previous,current):
    ids=sorted(set(previous)&set(current))
    if len(ids)<2:return None
    return float(adjusted_rand_score([previous[v] for v in ids],[current[v] for v in ids]))
