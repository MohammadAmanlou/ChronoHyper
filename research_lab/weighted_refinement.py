"""Exploratory native hyperedge coarsening with explicit arity/source weighting.

This is our own heuristic. It is NOT an implementation of published Mt-KaHyPar.
Retains original hyperedge IDs and one high-order event per scientific assertion.
Designed to address mismatch of train loss (λ-1) vs heldout evaluation
(λ-1)/(arity-1) on irregular event sizes.
"""
from collections import Counter,defaultdict
import numpy as np

def weighted_native_refinement(ids,X,edges,labels,semantic=.70,hyper=.30,
                               temporal=0.0,previous=None,rounds=3,
                               weighting='arity'):
    labels=np.asarray(labels,dtype=int).copy(); n=len(ids)
    if n<2 or not edges:return labels
    k=int(labels.max())+1
    size=np.bincount(labels,minlength=k).astype(int)
    if k<2:return labels
    source_counts=Counter(str(e.get('provenance',{}).get('article_id','?')) for e in edges)
    weights=[];bins=[];inc=defaultdict(list)
    map0=dict(zip(ids,map(int,labels)))
    for j,e in enumerate(edges):
        members=e['members']
        if len(members)<2:raise ValueError('Expected hyperedge arity at least 2')
        w=1/max(1,len(members)-1)
        if weighting=='arity+source':
            paper=str(e.get('provenance',{}).get('article_id','?'))
            w=w/max(1,source_counts[paper])
        elif weighting!='arity':raise ValueError('weighting must be arity or arity+source')
        weights.append(w)
        bins.append(Counter(map0[v] for v in members))
        for v in members:inc[v].append(j)
    sums=np.zeros((k,X.shape[1]))
    for i,c in enumerate(labels):sums[c]+=X[i]
    prev=None if previous is None else np.asarray(previous,dtype=int)
    max_size=max(int(np.ceil(.43*n)),int(np.ceil(n/k*1.05)))
    order=sorted(range(n),key=lambda i:(-len(inc[ids[i]]),str(ids[i])))
    for _ in range(rounds):
        centers=sums/np.maximum(size[:,None],1)
        centers/=np.maximum(np.linalg.norm(centers,axis=1,keepdims=True),1e-12)
        changed=0
        for i in order:
            src=int(labels[i]);node=ids[i]
            if size[src]<=1:continue
            sem=centers@X[i]
            candidates=set(np.argsort(sem)[-min(4,k):].tolist())
            for j in inc[node]:candidates.update(bins[j])
            candidates.add(src)
            score_best=0.;dst_best=src
            norm=max(1.e-9,sum(weights[j] for j in inc[node]))
            for dst in candidates:
                dst=int(dst)
                if src==dst or size[dst]>=max_size:continue
                diff=0.0
                for j in inc[node]:
                    ctr=bins[j]
                    before=len(ctr)
                    after=before-(1 if ctr[src]==1 else 0)+(1 if ctr.get(dst,0)==0 else 0)
                    diff+=weights[j]*(after-before)
                gain=semantic*float(sem[dst]-sem[src])-hyper*diff/norm
                if prev is not None and prev[i]>=0:
                    gain+=temporal*(float(dst==prev[i])-float(src==prev[i]))
                gain+=.015*(size[src]-size[dst])/max(1,n)
                if gain>score_best+1.e-8:
                    score_best=gain;dst_best=dst
            if dst_best!=src:
                for j in inc[node]:
                    bins[j][src]-=1
                    if bins[j][src]==0:del bins[j][src]
                    bins[j][dst_best]+=1
                sums[src]-=X[i];sums[dst_best]+=X[i]
                size[src]-=1;size[dst_best]+=1
                labels[i]=dst_best;changed+=1
        if not changed:break
    return labels
