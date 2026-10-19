"""Interpretable, evidence-bounded keyphrase labels with verifiable scoped gloss claims.
Method avoids an untestable LLM narrative; a separately sampled human/NLI audit
would be required for richer entailment claims.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import math,re

STOP={'an','a','the','and','or','in','on','with','for','to','of','by','at','via','from','between',
      'model','models','method','methods','using','use','based','study','new','improved','paper',
      'learning','data','approach','analysis','effect','work','graph','results','system',
      'neural','deep','of','its','vs','prediction','research','high','large','low','state',
      'multiple','accurate','simple','efficient','machine'}

def terms(text):
    words=[w.lower() for w in re.findall(r'[a-zA-Z][a-zA-Z0-9+\-]*',text)]
    words=[w for w in words if w not in STOP and len(w)>2]
    return list(dict.fromkeys(words+[' '.join((words[i],words[i+1])) for i in range(len(words)-1)]))

def name_from_members(members,all_nodes,global_document_frequency=None):
    byid={n['id']:n for n in all_nodes}
    objs=[byid[v] for v in members]
    counts=Counter(n['type'] for n in objs)
    terms_to_source=defaultdict(set)
    for n in objs:
        if n['type'] in ('author','claim','cited_work'):
            continue
        for phrase in terms(n['surface_form']):terms_to_source[phrase].add(n['id'])
    if not terms_to_source:
        for n in objs:
            for phrase in terms(n['surface_form']):terms_to_source[phrase].add(n['id'])
    n_doc=len(all_nodes)
    def rating(phrase,ids):
        support=len(ids)
        if support<2:return -1
        df=global_document_frequency.get(phrase,support) if global_document_frequency else support
        return support * (math.log((n_doc+1)/(df+1))+1) * (1.40 if ' ' in phrase else 1.0)
    ranked=sorted(terms_to_source,key=lambda t:(-rating(t,terms_to_source[t]),t))
    selected=[]
    for phrase in ranked:
        if rating(phrase,terms_to_source[phrase])<=0:continue
        if any(set(phrase.split())&set(old.split()) for old in selected):continue
        if len(phrase)>32:continue
        selected.append(phrase)
        if len(selected)==2:break
    if not selected:
        n=max(objs,key=lambda x:(len(x.get('provenance',{}).get('articles',[])),-len(x['surface_form'])))
        selected=[n['surface_form'][:40]]
        terms_to_source[selected[0]].add(n['id'])
    title=' / '.join(phrase.title() for phrase in selected)[:83]
    gloss=f'Observed cluster of {len(objs)} exported entities; member labels document '+', '.join(f'"{p}"' for p in selected)+'.'
    source=sorted(set.union(*(set(terms_to_source[p]) for p in selected)))[:20]
    evidence={'source_node_ids':source,'member_count':len(objs),'type_counts':dict(counts),
              'evidence_phrases':selected,'support_node_ids_per_phrase':{p:sorted(terms_to_source[p])[:20] for p in selected},
              'support_mode':'Exact n-gram in original node names, with timestamp <= cutoff; not scientific implication or human entailment.'}
    return title,gloss,evidence


def generate_levels(nodes,levels,cutoff,persistent_ids):
    # Document frequency computed over available node names only; never uses future nodes.
    df=Counter()
    for n in nodes: df.update(set(terms(n['surface_form'])))
    evidence={};labels={}
    for l in (0,1):
        group=defaultdict(list)
        for v,c in levels[l].items():group[c].append(v)
        for g,members in group.items():
            stable=persistent_ids[l][g]
            label,gloss,prov=name_from_members(sorted(members),nodes,global_document_frequency=df)
            labels[(l,g)]=(label,gloss)
            evidence[stable]={'label':label,'gloss':gloss,'evidence':prov,'cutoff':cutoff,'level':l}
    return labels,evidence


def support_audit(evidence,nodes,levels,ids):
    byid={n['id']:n for n in nodes}
    counts={l:Counter(assign.values()) for l,assign in enumerate(levels)}
    reverse={l:{stable:gid for gid,stable in m.items()} for l,m in enumerate(ids)}
    checks=[]
    for stable,obj in evidence.items():
        level=obj['level'];rec=obj['evidence'];source=rec['source_node_ids']
        gid=reverse[level].get(stable)
        valid_thing=gid is not None and counts[level][gid]==rec['member_count']
        valid_phrases=True
        for phrase, evid_ids in rec['support_node_ids_per_phrase'].items():
            if '"'+phrase+'"' not in obj['gloss']:valid_phrases=False
            for ident in evid_ids:
                if ident not in byid or ident not in levels[level] or levels[level][ident]!=gid or phrase not in terms(byid[ident]['surface_form']) or byid[ident]['first_seen_year']>obj['cutoff']:
                    valid_phrases=False
        checks.append(bool(valid_thing and valid_phrases))
    return {'automatic_membership_claims_audited':len(checks),'unsupported_membership_claims':sum(not x for x in checks),
            'bounded_structural_claim_error_rate':sum(not x for x in checks)/max(1,len(checks)),
            'independent_semantic_overclaim_rate':None,'independent_semantic_overclaim_status':'NOT_EVALUATED_NO_BLIND_REVIEW',
            'description':'All cluster glosses assert exactly recorded membership, counts and surface-name phrases. This is a machine-verifiable factual overclaim proxy, NOT independent literature-level entailment.'}
