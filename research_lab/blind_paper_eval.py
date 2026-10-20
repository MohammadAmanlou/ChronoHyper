"""Fresh key-isolated AI evaluation packet for Constructor ChronoHyper.

Makes 24 NEW level-1 real cluster samples (8 per 2020/2022/2024) plus
24 year-, sample-size-, and node-type-matched mixed-cluster controls.
Published code does not publish the condition key, score sheets, or private corpus.
Paper title provenance is weak external evidence, NOT full-text entailment.
Do not score with a model exposed to the condition key or historical scores.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

SEED = 20261021
YEARS = (2020, 2022, 2024)
EXCLUDED_TYPES = frozenset(('article', 'author', 'claim', 'cited_work'))
SAMPLE_N = 14
GROUPS_PER_YEAR = 8
HEADERS = ('blind_id', 'snapshot_year', 'member_count', 'member_names',
           'source_article_titles', 'source_evidence_limit',
           'coherence_score_1_to_5', 'evidence_sufficient_yes_no',
           'reviewer_id', 'evidence_notes')


def csv_read(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def csv_write(path, rows, headers):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(headers))
        w.writeheader()
        w.writerows(rows)


def _source(root):
    with ZipFile(root / 'inputs/data.zip') as archive:
        # Deliberately do not read data/questions.csv or data/ground_truth.json.
        graph = json.loads(archive.read('data/tkh_collection10.json'))
        papers = list(csv.DictReader(io.StringIO(
            archive.read('data/collection10_articles.csv').decode('utf-8-sig'))))
    return graph['nodes'], {str(p['id']): p for p in papers}


def _titles(sample, papers, year):
    titles = set()
    for n in sample:
        for aid in n.get('provenance', {}).get('articles', []):
            paper = papers.get(str(aid))
            if paper is None:
                continue
            try:
                valid_year = int(paper['year']) <= year
            except (ValueError, TypeError, KeyError):
                valid_year = False
            title = paper.get('title', '').strip()
            if valid_year and title:
                titles.add(title)
    return sorted(titles)[:8]


def _eligible(n, year):
    return n['type'] not in EXCLUDED_TYPES and int(n['first_seen_year']) <= year


def _matched_control(real_sample, donors, rng):
    want = Counter(n['type'] for n in real_sample)
    for _ in range(160):
        chosen = rng.sample(donors, 3)
        pool = defaultdict(list)
        for group in chosen:
            for n in group['members']:
                pool[n['type']].append((group['id'], n))
        if any(len(pool[k]) < count for k, count in want.items()):
            continue
        taken = []
        for kind, count in sorted(want.items()):
            taken.extend(rng.sample(pool[kind], count))
        if len({source_id for source_id, _ in taken}) >= 2:
            rng.shuffle(taken)
            return [n for _, n in taken], sorted({source_id for source_id, _ in taken})
    raise ValueError('Cannot construct 3-donor matched control with >=2 actual donors')


def prepare(project='.', out='local_only/reviews/fresh_semantic'):
    root = Path(project)
    dest = Path(out)
    if not dest.is_absolute():
        dest = root / dest
    # Original reviews were seen; exclude their (year, cluster) IDs upfront.
    old = csv_read(root/'research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv')
    old_ids = {(int(r['year']), r['stable_id']) for r in old}
    nodes, papers = _source(root)
    node_by_id = {n['id']: n for n in nodes}
    rng = random.Random(SEED)
    events = []
    for year in YEARS:
        hier = json.loads((root / f'outputs_selected/hierarchy_{year}.json').read_text(encoding='utf-8'))
        groups = []
        for s in hier['supernodes']:
            if int(s['level']) != 1:
                continue
            eligible = [node_by_id[i] for i in s['member_ids'] if _eligible(node_by_id[i], year)]
            if len(eligible) >= SAMPLE_N:
                groups.append({'id': s['id'], 'members': eligible})
        available = [g for g in groups if (year, g['id']) not in old_ids]
        if len(available) < GROUPS_PER_YEAR or len(groups) < 4:
            raise ValueError(f'Not enough new level-one clusters for year {year}')
        selected = rng.sample(sorted(available, key=lambda x: x['id']), GROUPS_PER_YEAR)
        for g in selected:
            actual = rng.sample(g['members'], SAMPLE_N)
            donors = [h for h in groups if h['id'] != g['id']]
            control, donor_ids = _matched_control(actual, donors, rng)
            events.append((year, g['id'], 'REAL', actual, [g['id']]))
            events.append((year, g['id'], 'MIXED_CONTROL', control, donor_ids))
    rng.shuffle(events)
    forms, keys = [], []
    for idx, (year, cluster_id, condition, sample, donors) in enumerate(events, 1):
        blind = f'P{idx:03d}'
        names = [n['surface_form'] for n in sample]
        titles = _titles(sample, papers, year)
        forms.append({'blind_id': blind, 'snapshot_year': year, 'member_count': len(sample),
                      'member_names': ' | '.join(names),
                      'source_article_titles': ' | '.join(titles),
                      'source_evidence_limit': 'Article titles only; not full texts; insufficient sources possible',
                      'coherence_score_1_to_5': '', 'evidence_sufficient_yes_no': '',
                      'reviewer_id': '', 'evidence_notes': ''})
        keys.append({'blind_id': blind, 'snapshot_year': year, 'condition': condition,
                     'target_cluster': cluster_id, 'donor_cluster_ids': ' | '.join(donors)})
    assert len(forms) == len(keys) == 48
    dest.mkdir(parents=True, exist_ok=True)
    csv_write(dest/'blind_review_48.csv', forms, HEADERS)
    csv_write(dest/'condition_key_PRIVATE.csv', keys,
              ('blind_id', 'snapshot_year', 'condition', 'target_cluster', 'donor_cluster_ids'))
    rubric = '''FRESH SCIENTIFIC COHERENCE RATING: source-limited AI judge.\n\nOnly read blind_review_48.csv. No access to source repository, method output, old reviews, or condition key.\nFor each row, independently assess whether the 14 listed scientific member names\nrepresent one coherent topic. Consider linked source article TITLES but do NOT\nassume titles entail the cluster claim or that all names are same scientific type.\nRatings: 1 unrelated, 2 weak theme, 3 partially coherent/mixed, 4 mostly coherent,\n5 tightly coherent. Set evidence_sufficient_yes_no to no when titles/names are too\nweak for a defensible rating; score may be blank when no. For yes, put integer 1–5.\nAlways fill a truthful AI model identifier and row-specific evidence notes.\nNever guess the REAL/control class, use gold, or see previous results.\nLeave all original data columns unchanged. Do not claim independent full-paper\nentailment from titles. Get corpus-sharing authorization before external AI upload.\n'''
    (dest/'JUDGE_INSTRUCTIONS.txt').write_text(rubric, encoding='utf-8')
    print('Prepared 48 NEW blind samples across 2020/2022/2024, 24 matched controls.')
    print('Reviewer file:', dest/'blind_review_48.csv')
    print('PRIVATE key, do not share:', dest/'condition_key_PRIVATE.csv')
    return forms, keys


def _exact_p(wins, losses):
    n = wins+losses
    if n == 0:
        return None
    return min(1.0, 2*sum(math.comb(n,k) for k in range(min(wins,losses)+1))/2**n)


def score(project='.', ratings='', packet='local_only/reviews/fresh_semantic',
          out='local_only/reviews/fresh_semantic/score_summary.json'):
    root = Path(project)
    dest = Path(packet)
    if not dest.is_absolute():dest = root/dest
    rated = Path(ratings)
    if not rated.is_absolute():rated = root/rated
    if not rated.is_file():raise FileNotFoundError('Explicit rated CSV required; never score blank sheet')
    original = csv_read(dest/'blind_review_48.csv')
    keys = csv_read(dest/'condition_key_PRIVATE.csv')
    responses = csv_read(rated)
    assert len(keys) == len(original) == len(responses) == 48
    norm = {r['blind_id']:r for r in original}
    key = {r['blind_id']:r for r in keys}
    observed = set()
    grouped = defaultdict(dict)
    excluded = defaultdict(list)
    for r in responses:
        bid = r.get('blind_id', '')
        if bid not in norm or bid in observed or bid not in key:
            raise ValueError('Duplicate, missing or unrecognized blind ID: '+bid)
        observed.add(bid)
        for field in ('snapshot_year', 'member_count', 'member_names',
                      'source_article_titles', 'source_evidence_limit'):
            if r.get(field, '') != norm[bid][field]:
                raise ValueError('Judge changed frozen evidence: '+bid+' '+field)
        if not r.get('reviewer_id','').strip() or not r.get('evidence_notes','').strip():
            raise ValueError('Reviewer identity/notes missing: '+bid)
        sufficient = r.get('evidence_sufficient_yes_no','').strip().lower()
        if sufficient not in ('yes','no'):
            raise ValueError('Missing sufficiency yes/no: '+bid)
        rating = r.get('coherence_score_1_to_5','').strip()
        if (sufficient == 'yes' and rating not in ('1','2','3','4','5')) or (sufficient=='no' and rating not in ('','1','2','3','4','5')):
            raise ValueError('Invalid confidence/rating: '+bid)
        k = key[bid]
        group = (int(k['snapshot_year']), k['target_cluster'])
        cond = k['condition']
        if sufficient == 'no':
            excluded[group].append(cond)
        if cond in grouped[group]:raise ValueError('Duplicate control condition: '+bid)
        grouped[group][cond] = int(rating) if sufficient == 'yes' else None
    if len(observed)!=48 or len(grouped)!=24:raise ValueError('Incomplete responses')
    pairs = []
    for group, arms in grouped.items():
        if set(arms) != {'REAL','MIXED_CONTROL'}:raise ValueError('Missing pair '+str(group))
        if all(v is not None for v in arms.values()):
            pairs.append({'year':group[0], 'real': arms['REAL'], 'control':arms['MIXED_CONTROL'],
                          'delta':arms['REAL']-arms['MIXED_CONTROL']})
    diffs = [x['delta'] for x in pairs]
    wins = sum(x>0 for x in diffs)
    losses = sum(x<0 for x in diffs)
    ties = len(diffs)-wins-losses
    rng = random.Random(20261022)
    ci = None
    if diffs:
        bs = sorted(statistics.mean(rng.choices(diffs,k=len(diffs))) for _ in range(10000))
        ci = [bs[249],bs[9749]]
    result = {'schema':'ckl_fresh_key_isolated_paper_title_coherence_v1',
              'n_blind_cases':48, 'n_matched_pairs':24, 'evaluable_pairs':len(pairs),
              'excluded_insufficient_pairs':24-len(pairs),
              'mean_real':statistics.mean(x['real'] for x in pairs) if pairs else None,
              'mean_control':statistics.mean(x['control'] for x in pairs) if pairs else None,
              'mean_paired_delta':statistics.mean(diffs) if diffs else None,
              'real_higher_pairs':wins,'control_higher_pairs':losses,'ties':ties,
              'exact_sign_p_descriptive_only':_exact_p(wins,losses),
              'paired_bootstrap_95ci_exploratory':ci,
              'by_year':{str(y):{'evaluable_pairs':len([x for x in pairs if x['year']==y]),
                       'mean_delta':statistics.mean(x['delta'] for x in pairs if x['year']==y)
                       if any(x['year']==y for x in pairs) else None} for y in YEARS},
              'self_reported_AI_independence_only':True,
              'independent_full_paper_entailment_verified':False,
              'source_scope':'Private node names + existing linked article titles, NOT full paper content. This is a blind LLM judgment using a different assessor, not an independent source corpus.',
              'interpretation':'Requires key-isolated evaluator attestation; source title correlations with node surface forms remain. Pre-existing degree/arity null p=0.69 is separate and unchanged.'}
    path = Path(out)
    if not path.is_absolute():path = root/path
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',default='.')
    p.add_argument('--prepare',action='store_true')
    p.add_argument('--score',action='store_true')
    p.add_argument('--ratings',default='')
    p.add_argument('--packet',default='local_only/reviews/fresh_semantic')
    p.add_argument('--out',default='local_only/reviews/fresh_semantic/score_summary.json')
    a=p.parse_args()
    if a.prepare:prepare(a.project,a.packet)
    elif a.score:
        if not a.ratings:p.error('--score requires --ratings for a genuinely completed rating CSV')
        score(a.project,a.ratings,a.packet,a.out)
    else:p.error('Choose --prepare or --score')

if __name__=='__main__':main()