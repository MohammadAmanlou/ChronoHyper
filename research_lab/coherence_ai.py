"""ChronoHyper AI-only sample-name coherence control (not independent expert science).

Frozen input: the original 24-case A/B sheet, using only sample member names.
Null: equal-sized mixes from three other selected clusters of the same snapshot year.
WARNING: The assistant that gave subjective scores had already seen a subset of
control-key mappings in conversation, so scores are NOT independently blind.
"""
from __future__ import annotations
import argparse, csv, json, hashlib, random, math, statistics
from collections import defaultdict
from pathlib import Path

SEED = 20261020
BASE = 'research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv'


def load_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:raise ValueError('Cannot write empty table')
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields or list(rows[0]));writer.writeheader();writer.writerows(rows)


def generate_form(project='.', out='local_only/reviews/coherence'):
    root=Path(project);rows=load_csv(root/BASE)
    if len(rows)!=24 or len({(r['year'],r['stable_id']) for r in rows})!=24:
        raise ValueError('Expected 24 unique frozen A/B cases')
    rng=random.Random(SEED)
    pool=defaultdict(list)
    for row in rows:
        row['_members']=[s.strip() for s in row['random_member_names'].split(' | ') if s.strip()]
        if len(row['_members'])<12:raise ValueError('Too few sampled members')
        pool[row['year']].append(row)
    events=[]
    for row in rows:
        members=row['_members'];n=len(members)
        events.append({'year':row['year'],'condition':'REAL','cluster':row['stable_id'],
                'source_clusters':row['stable_id'],'members':members})
        others=[z for z in pool[row['year']] if z['stable_id']!=row['stable_id']]
        selected=rng.sample(others,3)
        splits=[n//3,n//3,n-2*(n//3)]
        mixed=[]
        for x,k in zip(selected,splits):mixed+=rng.sample(x['_members'],k)
        rng.shuffle(mixed)
        events.append({'year':row['year'],'condition':'MIXED_NULL','cluster':row['stable_id'],
            'source_clusters':' | '.join(x['stable_id'] for x in selected),'members':mixed})
    rng.shuffle(events)
    forms=[];keys=[]
    for i,event in enumerate(events,1):
        key='B'+str(i).zfill(3)
        forms.append({'blind_id':key,'year':event['year'],'sample_member_count':len(event['members']),
          'sample_member_names':' | '.join(event['members']),
          'coherence_rating_1_to_5':'','evidence_sufficient_yes_no':'','reviewer_id':'','review_notes':''})
        keys.append({'blind_id':key,'year':event['year'],'condition':event['condition'],
                     'target_cluster':event['cluster'],'sampled_from_clusters':event['source_clusters']})
    assert len(forms)==len(keys)==48
    out=root/out;out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'coherence_blind_48.csv',forms)
    write_csv(out/'coherence_key_PRIVATE.csv',keys)
    print('Generated blind 48-row form and local-only control key in',out)
    return forms,keys


def analyze(project='.', rating_file='research_outputs/coherence_ai/ratings_48_AI.csv',
            key_file='local_only/reviews/coherence/coherence_key_PRIVATE.csv',
            out='local_only/reviews/coherence/summary.json'):
    root=Path(project);ratings=load_csv(root/rating_file);keys=load_csv(root/key_file)
    if len(ratings)!=48 or len(keys)!=48:raise ValueError('Expected 48 rated and 48 key records')
    rmap={r['blind_id']:r for r in ratings};kmap={r['blind_id']:r for r in keys}
    if len(rmap)!=48 or len(kmap)!=48 or set(rmap)!=set(kmap):raise ValueError('Missing/duplicate/mismatched IDs')
    groups=defaultdict(dict)
    for ident,row in rmap.items():
        rating=row['coherence_rating_1_to_5']
        if rating not in ('1','2','3','4','5') or not row['reviewer_id'] or not row['review_notes']:
            raise ValueError('Invalid rating, absent reviewer identity or missing evidence note '+ident)
        if row['evidence_sufficient_yes_no'] not in ('yes','no'):
            raise ValueError('Missing evidence sufficiency flag '+ident)
        k=kmap[ident];cond=k['condition']
        if cond not in ('REAL','MIXED_NULL'):raise ValueError('Unknown control class '+cond)
        g=(k['year'],k['target_cluster'])
        if cond in groups[g]:raise ValueError('Duplicate class in pair '+str(g))
        groups[g][cond]=int(rating)
    if len(groups)!=24 or any(set(x)!={'REAL','MIXED_NULL'} for x in groups.values()):
        raise ValueError('Missing paired controls')
    pairs=[(x['REAL'],x['MIXED_NULL']) for x in groups.values()]
    differences=[real-null for real,null in pairs]
    wins=sum(d>0 for d in differences);losses=sum(d<0 for d in differences);ties=sum(d==0 for d in differences)
    discord= wins+losses
    if discord:
        m=min(wins,losses)
        p=min(1.0,2*sum(math.comb(discord,k) for k in range(m+1))/(2**discord))
    else:p=None
    rng=random.Random(1062020)
    boots=[]
    for _ in range(25000):
        boots.append(statistics.mean(differences[rng.randrange(len(differences))] for _ in differences))
    boots.sort()
    report={'schema':'chronohyper_coherence_AI_rubric_v1',
      'ratings':'GPT-6_AI_ASSISTED_NONINDEPENDENT',
      'n_pairs':24,'n_real':24,'n_mixed_null':24,
      'mean_real':statistics.mean(x[0] for x in pairs),
      'mean_null':statistics.mean(x[1] for x in pairs),
      'mean_paired_delta':statistics.mean(differences),
      'real_higher_pairs':wins,'null_higher_pairs':losses,'tie_pairs':ties,
      'exact_sign_p_descriptive_only':p,
      'paired_bootstrap_95ci_exploratory':[boots[624],boots[24374]],
      'strict_blind_independence':False,
      'independent_full_paper_semantic_validation':False,
      'limited_scope':'14 sampled exported node names per cluster only, not all source papers; no independent human evaluator; analyst saw part of control key in context before scoring. Does not overrule degree-and-arity null p=0.69.'}
    path=root/out;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--project',default='.')
    p.add_argument('--generate',action='store_true')
    p.add_argument('--score',action='store_true')
    p.add_argument('--ratings',default='research_outputs/coherence_ai/ratings_48_AI.csv')
    p.add_argument('--key',default='local_only/reviews/coherence/coherence_key_PRIVATE.csv')
    p.add_argument('--out',default='local_only/reviews/coherence/summary.json')
    a=p.parse_args()
    if a.generate:generate_form(a.project)
    if a.score:analyze(a.project,a.ratings,a.key,a.out)
    if not a.generate and not a.score:p.error('Choose --generate or --score')

if __name__=='__main__':main()