"""24-case V2/V3 blind AI title-review packet; private mapping never committed.

Eight previously unreviewed level-one cases each from 2020, 2022 and 2024.
Never use this to claim full-paper scientific entailment from node/paper titles.
"""
from __future__ import annotations
import argparse,csv,json,random,hashlib,statistics,math
from pathlib import Path
from collections import Counter
from research_lab.blind_paper_eval import _source,_titles,_eligible,csv_write,csv_read
from research_lab.label_v3 import improve_case

YEARS=(2020,2022,2024)
SEED=20261022
FIELDS=('blind_id','snapshot_year','member_count','member_names',
        'source_article_titles','label_A','gloss_A','label_B','gloss_B',
        'A_accuracy_accurate_vague_wrong','B_accuracy_accurate_vague_wrong',
        'A_gloss_overclaim_yes_no_unclear','B_gloss_overclaim_yes_no_unclear',
        'evidence_sufficient_yes_no','reviewer_id','review_notes')
RATING={'wrong':0,'vague':1,'accurate':2}

def resolve(root,p):
    q=Path(p)
    return q if q.is_absolute() else root/q

def prepare(project='.',packet='local_only/reviews/label_v3_fresh'):
    root=Path(project);out=resolve(root,packet);out.mkdir(parents=True,exist_ok=True)
    if (out/'blind_v2_v3_24.csv').exists() or (out/'mapping_PRIVATE.csv').exists():
        raise FileExistsError('Preserve existing private blind packet and mapping; do not regenerate')
    prior={(int(r['year']),r['stable_id']) for r in csv_read(
        root/'research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv')}
    nodes,papers=_source(root);byid={n['id']:n for n in nodes}
    rng=random.Random(SEED);selected=[]
    for year in YEARS:
        source=json.loads((root/f'research_outputs/label_v2/candidates_v2_{year}.json').read_text(encoding='utf-8'))
        available=[r for r in source if int(r['level'])==1 and
            (year,r['stable_id']) not in prior and
            sum(_eligible(byid[v],year) for v in r['member_ids'])>=14]
        if len(available)<8:raise ValueError('Insufficient unused clusters')
        selected.extend(rng.sample(sorted(available,key=lambda x:x['stable_id']),8))
    rng.shuffle(selected);rows=[];secrets=[]
    for i,item in enumerate(selected,1):
        year=int(item['year']);v3=improve_case(item)
        members=[byid[v] for v in item['member_ids'] if _eligible(byid[v],year)]
        sample=rng.sample(members,14);v3_is_a=bool(rng.randrange(2))
        old=(item['v2_label'],item['v2_gloss'])
        new=(v3['v3_development_label'],v3['v3_development_gloss'])
        A,B=(new,old) if v3_is_a else (old,new)
        bid=f'L{i:03d}'
        r={'blind_id':bid,'snapshot_year':year,'member_count':len(item['member_ids']),
           'member_names':' | '.join(n['surface_form'] for n in sample),
           'source_article_titles':' | '.join(_titles(sample,papers,year)),
           'label_A':A[0],'gloss_A':A[1],'label_B':B[0],'gloss_B':B[1]}
        r.update({f:'' for f in FIELDS if f not in r});rows.append(r)
        secrets.append({'blind_id':bid,'v3_side':'A' if v3_is_a else 'B',
                        'year':year,'stable_id':item['stable_id']})
    assert len(rows)==24 and len({r['blind_id'] for r in rows})==24
    csv_write(out/'blind_v2_v3_24.csv',rows,FIELDS)
    csv_write(out/'mapping_PRIVATE.csv',secrets,('blind_id','v3_side','year','stable_id'))
    rubric="""Anonymized comparison of 24 scientific title+gloss A/B pairs.
Read only the blind CSV and these instructions, not the method/secret key or
earlier assessments. For A and B separately, rate title accurate/vague/wrong
relative to sampled scientific members. Accurate=dominant topic correct;
vague=generic or limited; wrong=misleading. For each gloss use yes/no/unclear
for scientific overclaim. A statement that only cites node names is not
independent paper entailment. Set evidence_sufficient_yes_no=no if only
partial/poor evidence exists; in that case mark BOTH glosses unclear and
accuracy grades may be blank. Give row-specific notes, model identifier and
preserve every original column in a completed UTF-8 CSV. No external upload
of private Constructor content unless explicitly authorized.
"""
    (out/'JUDGE_INSTRUCTIONS.txt').write_text(rubric,encoding='utf-8')
    print('Prepared 24 blinded V2/V3 title cases; mapping saved only in ignored local folder:',out)
    return rows,secrets

def score(project='.',ratings='',packet='local_only/reviews/label_v3_fresh'):
    root=Path(project);folder=resolve(root,packet);rated=resolve(root,ratings)
    if not rated.is_file():raise FileNotFoundError('Completed reviewer CSV required')
    forms=csv_read(folder/'blind_v2_v3_24.csv')
    secrets=csv_read(folder/'mapping_PRIVATE.csv');graded=csv_read(rated)
    if len(forms)!=24 or len(secrets)!=24 or len(graded)!=24:raise ValueError('Expected 24 cases')
    originals={r['blind_id']:r for r in forms};key={r['blind_id']:r for r in secrets}
    if len(originals)!=24 or len(key)!=24:raise ValueError('Nonunique private IDs')
    seen=set();win=loss=tie=excluded=0;differences=[];evaluated=Counter();unknown=Counter();over=Counter();models=set()
    for x in graded:
        bid=x.get('blind_id')
        if bid not in originals or bid in seen:raise ValueError('Unknown or repeated ID')
        seen.add(bid)
        if any(x.get(f)!=originals[bid].get(f) for f in FIELDS[:9]):
            raise ValueError('Changed frozen evidence: '+bid)
        if not x.get('reviewer_id','').strip() or not x.get('review_notes','').strip():
            raise ValueError('Reviewer ID and notes required')
        models.add(x['reviewer_id'].strip())
        suff=x.get('evidence_sufficient_yes_no','').lower().strip()
        if suff not in ('yes','no'):raise ValueError('Evidence sufficiency must be yes/no')
        v3=key[bid]['v3_side'];v2='B' if v3=='A' else 'A'
        title={k:x.get(k+'_accuracy_accurate_vague_wrong','').strip().lower() for k in ('A','B')}
        gloss={k:x.get(k+'_gloss_overclaim_yes_no_unclear','').strip().lower() for k in ('A','B')}
        if any(t not in ('yes','no','unclear') for t in gloss.values()):
            raise ValueError('Invalid gloss overclaim grade')
        if suff=='yes':
            if any(t not in RATING for t in title.values()):raise ValueError('Missing paired title grades')
            d=RATING[title[v3]]-RATING[title[v2]]
            differences.append(d)
            if d>0:win+=1
            elif d<0:loss+=1
            else:tie+=1
        else:
            excluded+=1
            if any(t!='unclear' for t in gloss.values()):
                raise ValueError('Insufficient evidence cannot establish no-overclaim')
        for method,side in [('v2',v2),('v3',v3)]:
            if gloss[side]=='unclear':unknown[method]+=1
            else:
                evaluated[method]+=1
                if gloss[side]=='yes':over[method]+=1
    if len(seen)!=24:raise ValueError('Incomplete case IDs')
    n=win+loss
    p=min(1,2*sum(math.comb(n,k) for k in range(min(win,loss)+1))/2**n) if n else None
    result={'schema':'chronohyper_v3_v2_blind_AI_names_titles_only_v1',
        'n_pairs':24,'evaluable':len(differences),'excluded':excluded,
        'v3_wins':win,'v3_losses':loss,'ties':tie,
        'mean_rating_delta_v3_minus_v2':statistics.mean(differences) if differences else None,
        'descriptive_sign_p_two_sided':p,
        'gloss_overclaim_evaluable':{k:evaluated[k] for k in ('v2','v3')},
        'gloss_overclaim_unclear':{k:unknown[k] for k in ('v2','v3')},
        'gloss_overclaim_rate':{k:over[k]/evaluated[k] if evaluated[k] else None for k in ('v2','v3')},
        'self_reported_reviewer_ids':sorted(models),
        'rated_csv_sha256':hashlib.sha256(rated.read_bytes()).hexdigest(),
        'independent_paper_entailment_verified':False,
        'independent_judge_identity_verified':False,
        'development_review_not_confirmatory':True,
        'original_locked_outputs_unchanged':True}
    (folder/'result_LOCAL.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2));return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--project',default='.')
    p.add_argument('--prepare',action='store_true')
    p.add_argument('--score',action='store_true')
    p.add_argument('--ratings',default='')
    p.add_argument('--packet',default='local_only/reviews/label_v3_fresh')
    a=p.parse_args()
    if a.prepare:prepare(a.project,a.packet)
    elif a.score:
        if not a.ratings:p.error('--score requires --ratings')
        score(a.project,a.ratings,a.packet)
    else:p.error('Choose --prepare or --score')
if __name__=='__main__':main()
