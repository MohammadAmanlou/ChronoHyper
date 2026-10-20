"""Reproducible, HONEST 2025 Type-A frontier score on PREVIOUSLY INSPECTED questions.

Two separate CLI calls, with distinct data access:
--prepare imports the rank-only experiment, which NEVER opens ground_truth.json.
--evaluate verifies the frozen ranking digest, THEN reads gold from the private
supplied ZIP. This is development diagnosis, not a held-out test.
All outputs are confined to ignored local_only/; no 2025 answer data is pushed.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import random
import statistics
from pathlib import Path
from zipfile import ZipFile

from research_lab import retrieval_frontier as frontier
from research_lab.retrieval_v2 import index, norm

DEFAULT_DIR = 'local_only/retrieval_frontier/historical_v2'
EXPECTED_A = 14
EXPECTED_B = 4
BOOTSTRAP_DRAWS = 4000
BOOTSTRAP_SEED = 20261020


def _rooted(root, location):
    path = Path(location)
    return path if path.is_absolute() else Path(root) / path


def prepare(project='.', folder=DEFAULT_DIR, repeats=5):
    root = Path(project)
    dest = _rooted(root, folder)
    rankfile = dest / 'rankings.json'
    if rankfile.exists():
        rank = json.loads(rankfile.read_text(encoding='utf-8'))
        frontier.verify_rankings(rank)
        print('Existing frozen rank-only output preserved:', rankfile)
        return rank
    # Important: neither here nor rank() opens ground_truth.json.
    return frontier.rank(root, out=str(rankfile), repeats=repeats)


def _validate_gold_and_rankings(rank, gold, expected_a=EXPECTED_A,
                                expected_b=EXPECTED_B):
    """Requires exact question coverage, type consistency and nonempty Type A gold."""
    frontier.verify_rankings(rank)
    if rank.get('evaluation_stage') != 'HISTORICAL_REUSED_QUESTIONS_DEVELOPMENT_ONLY':
        raise ValueError('Only the predeclared original historical benchmark is allowed')
    if rank.get('cutoff') != 2025:
        raise ValueError('Expected the conservative 2025 retrieval cutoff')
    records = rank['results']
    n_a = sum(str(r.get('type')).upper() == 'A' for r in records)
    n_b = sum(str(r.get('type')).upper() == 'B' for r in records)
    if (n_a, n_b) != (expected_a, expected_b) or len(records) != n_a + n_b:
        raise ValueError(f'Unexpected task coverage: {n_a} Type A, {n_b} Type B')
    ids = [r['question_id'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate ranked question IDs')
    refs = {}
    for r in records:
        qid = r['question_id']
        if qid not in gold:
            raise ValueError('Question not in frozen source ground truth: ' + str(qid))
        reference = gold[qid]
        if str(reference.get('type')).upper() != str(r['type']).upper():
            raise ValueError('Gold/task type mismatch for ' + str(qid))
        if str(r['type']).upper() != 'A':
            continue
        targets = reference.get('expected_methods')
        if (not isinstance(targets, list) or not targets or
                not all(isinstance(t, str) and norm(t) for t in targets)):
            raise ValueError('Missing/invalid expected_methods for ' + str(qid))
        refs[qid] = list(targets)
    return refs


def _pair_bootstrap(values, n_draws=BOOTSTRAP_DRAWS, seed=BOOTSTRAP_SEED):
    if not values:
        return {'mean': None, 'ci95': [None, None], 'n': 0}
    rng = random.Random(seed)
    draws = [sum(values[rng.randrange(len(values))]
                 for _ in range(len(values))) / len(values) for _ in range(n_draws)]
    draws.sort()
    lower = draws[int(.025 * (n_draws - 1))]
    upper = draws[int(.975 * (n_draws - 1))]
    return {'mean': statistics.mean(values), 'ci95': [lower, upper],
            'n': len(values), 'resampling_unit': 'question',
            'n_bootstrap_draws': n_draws, 'seed': seed}


def _paired_sign(a, b):
    if len(a) != len(b):
        raise ValueError('Unmatched paired scores')
    win = sum(i > j for i, j in zip(a, b))
    loss = sum(i < j for i, j in zip(a, b))
    n = win + loss
    p = min(1., 2 * sum(math.comb(n, i) for i in range(min(win, loss) + 1))
            / (2 ** n)) if n else None
    return {'wins': win, 'losses': loss, 'ties': len(a) - n,
            'n_discordant': n, 'exact_two_sided_p_descriptive': p}


def _per_question(rank, refs, candidate_aliases):
    arms = ['flat'] + [f'route_{k}' for k in rank['budgets']]
    by_arm = {arm: [] for arm in arms}
    details = []
    for r in rank['results']:
        qid = r['question_id']
        if qid not in refs:
            continue
        wanted = {norm(t) for t in refs[qid]}
        eligible = wanted & candidate_aliases
        per = {'question_id': qid, 'expected_count': len(wanted),
               'eligible_count': len(eligible),
               'unavailable_count': len(wanted - eligible),
               'scores': {}}
        for arm in arms:
            entry = r['flat'] if arm == 'flat' else r['routes'][arm[6:]]
            retrieved = {t['normalized'] for t in entry['top5']}
            found = retrieved & wanted
            sc = {'hit_at_5': int(bool(found)),
                  'recall_at_5_all_expected': len(found) / len(wanted),
                  'recall_at_5_available': (len(found) / len(eligible)
                                            if eligible else None),
                  'n_found': len(found)}
            per['scores'][arm] = sc
            by_arm[arm].append(sc)
        details.append(per)
    return details, by_arm


def _summarize(rank, details, by_arm, candidate_aliases):
    arms = list(by_arm)
    n = len(details)
    if n != EXPECTED_A:
        raise ValueError('Historical benchmark must have 14 scored Type A questions')
    # The quality numerator is 14 Type-A tasks. Cost/timing uses EXACTLY the
    # same 14 tasks, not the 18-question (Type A+B) ungraded budget average.
    type_a = {r['question_id']: r for r in rank['results'] if r['question_id']
              in {d['question_id'] for d in details}}
    if len(type_a) != n:
        raise AssertionError('Missing ranked Type-A tasks for matched compute costs')
    per_arm = {}
    for arm, rows in by_arm.items():
        eligible = [r['recall_at_5_available'] for r in rows
                    if r['recall_at_5_available'] is not None]
        timings = []
        dot_products = []
        for qid in sorted(type_a):
            item = type_a[qid]
            record = item['flat'] if arm == 'flat' else item['routes'][arm[6:]]
            dot_products.append(record['candidates_scored'] +
                                (0 if arm == 'flat' else record['centroid_scores']))
            tkey = ('median_online_ms_including_top5' if arm == 'flat'
                    else 'median_online_ms_including_routing_and_top5')
            timings.append(record[tkey])
        per_arm[arm] = {
            'n_questions': len(rows),
            'hit_at_5': statistics.mean(r['hit_at_5'] for r in rows),
            'macro_recall_at_5_all_expected': statistics.mean(
                r['recall_at_5_all_expected'] for r in rows),
            'macro_recall_at_5_available': statistics.mean(eligible) if eligible else None,
            'n_questions_with_available_targets': len(eligible),
            'mean_total_online_dot_products': statistics.mean(dot_products),
            'mean_query_median_online_ms': statistics.mean(timings),
            'hit_minus_flat': (statistics.mean(r['hit_at_5'] for r in rows) -
                               statistics.mean(r['hit_at_5'] for r in by_arm['flat'])),
        }
    flat = [int(row['scores']['flat']['hit_at_5']) for row in details]
    contrasts = {}
    for arm in arms[1:]:
        hit = [int(row['scores'][arm]['hit_at_5']) for row in details]
        diff = [a-b for a,b in zip(hit,flat)]
        contrasts[arm] = {'paired_hit_at_5_difference_vs_flat':
                              _pair_bootstrap(diff, seed=BOOTSTRAP_SEED + int(arm[6:])),
                          'paired_sign_test': _paired_sign(hit,flat)}
    last = 'route_' + str(rank['budgets'][-1])
    if any(row['scores'][last] != row['scores']['flat'] for row in details):
        raise AssertionError('All-root retrieval must reproduce flat on every metric')
    return {
        'schema': 'chronohyper_historical_frontier_gold_diagnostic_v1',
        'evaluation_stage': 'HISTORICAL_PREVIOUSLY_INSPECTED_NOT_CONFIRMATORY',
        'gold_read_only_after_frozen_rank_verified': True,
        'rank_sha256': rank['ranking_sha256'],
        'n_ranked_queries': len(rank['results']),
        'n_scored_type_A': n, 'n_unscored_type_B': EXPECTED_B,
        'n_canonical_entities': rank['n_canonical_entities'],
        'n_distinct_candidate_aliases': len(candidate_aliases),
        'total_expected_normalized_targets': sum(x['expected_count'] for x in details),
        'total_eligible_normalized_targets': sum(x['eligible_count'] for x in details),
        'quality_measures': per_arm,
        'quality_cost_denominator': 'same 14 Type-A questions for quality, compute and timing',
        'separate_all_18_question_ungraded_budget_summary': rank['ungraded_budget_summary'],
        'paired_hit_at_5_contrasts': contrasts,
        'per_question': details,
        'limitations': [
            'Original questions and answers were previously inspected; this is not independent test performance.',
            'The method was developed after seeing this dataset; multiple budget contrasts are exploratory without multiplicity correction.',
            'Only exact normalized target-name matching is scored; scientific correctness of multi-claim answers is unmeasured.',
            'Timing includes online route+candidate+top5 only, excluding shared query vector encoding and offline indexing.',
            'All bootstraps resample 14 correlated historical questions, NOT independent source corpora.',
            'No model selection or reported method improvement is justified by this historical diagnostic.',
        ],
        'external_full_paper_entailment_verified': False,
        'genuine_new_question_evaluation_completed': False,
    }


def _save_figure(report, destination):
    """Static vector image; objective is auditable comparison, not presentation novelty."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    arms = ['route_1', 'route_2', 'route_4', 'route_8', 'route_12', 'flat']
    arms = [arm for arm in arms if arm in report['quality_measures']]
    stats = report['quality_measures']
    xy = [(stats[arm]['mean_total_online_dot_products'],
           stats[arm]['hit_at_5']) for arm in arms]
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.plot([p[0] for p in xy], [p[1] for p in xy], marker='o', linewidth=1.2)
    for arm,(x,y) in zip(arms,xy):
        ax.annotate(arm.replace('route_', 'roots=').replace('flat','flat'),
                    (x,y), xytext=(5,6), textcoords='offset points', fontsize=8)
    ax.set_xlim(left=0)
    ax.set_ylim(-.02, min(1.03, max(.20, max(y for _,y in xy)+.18)))
    ax.set_xlabel('Mean online dot products (candidates + root centroids)')
    ax.set_ylabel('Type-A Hit@5 (14 previously inspected questions)')
    ax.set_title('Exploratory routed retrieval: quality vs computation')
    ax.grid(True, alpha=.22)
    fig.text(.5,.012,'Development-only; not an independent benchmark or system-level latency claim',
             ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1))
    fig.savefig(destination, format='svg')
    plt.close(fig)


def evaluate(project='.', folder=DEFAULT_DIR):
    root = Path(project)
    dest = _rooted(root, folder)
    ranking = dest / 'rankings.json'
    if not ranking.is_file():
        raise FileNotFoundError('Run --prepare first, without access to gold')
    if (dest / 'historical_audit.json').exists():
        raise FileExistsError('Previous audit retained. Use a new --folder for a new run.')
    artifact = json.loads(ranking.read_text(encoding='utf-8'))
    frontier.verify_rankings(artifact)
    # Source ground truth is opened only after rank-only SHA verification.
    with ZipFile(root / 'inputs/data.zip') as archive:
        gold = json.loads(archive.read('data/ground_truth.json'))
    refs = _validate_gold_and_rankings(artifact, gold)
    # Unseen gold must never influence candidate ranking / budget selection.
    entries, _, _, _, _, _, _, _ = index(root, cutoff=2025)
    if len(entries) != artifact['n_canonical_entities']:
        raise ValueError('Candidate index changed since rankings were frozen')
    candidate_aliases = {r['normalized'] for r in entries}
    details, by_arm = _per_question(artifact, refs, candidate_aliases)
    report = _summarize(artifact, details, by_arm, candidate_aliases)
    dest.mkdir(parents=True, exist_ok=True)
    # Local, source-preserving GOLD. NEVER copy into a tracked directory.
    with (dest / 'historical_gold_PRIVATE.csv').open(
            'w', newline='', encoding='utf-8-sig') as fp:
        writer = csv.DictWriter(fp, fieldnames=['question_id','expected_methods'])
        writer.writeheader()
        for ident, methods in sorted(refs.items()):
            writer.writerow({'question_id':ident,'expected_methods':'|'.join(methods)})
    raw_score = frontier.score(project=root, rankings=str(ranking),
                               references=str(dest / 'historical_gold_PRIVATE.csv'),
                               out=str(dest / 'raw_score_PRIVATE.json'))
    if raw_score['n_evaluated'] != EXPECTED_A:
        raise AssertionError('Only 14 original Type-A questions should be scored')
    (dest / 'historical_audit.json').write_text(
        json.dumps(report,indent=2,ensure_ascii=False) + '\n', encoding='utf-8')
    _save_figure(report, dest / 'historical_quality_cost.svg')
    print('HISTORICAL FRONTIER (exploratory only):', len(details), 'Type A; 4 Type B unscored')
    for name, value in report['quality_measures'].items():
        print(name, 'Hit@5=',round(value['hit_at_5'],4),
              'mean online dot products=',round(value['mean_total_online_dot_products'],2))
    print('Local-only audit:', dest / 'historical_audit.json')
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare', action='store_true')
    g.add_argument('--evaluate', action='store_true')
    ap.add_argument('--project', default='.')
    ap.add_argument('--folder', default=DEFAULT_DIR)
    ap.add_argument('--repeats', type=int, default=5)
    a = ap.parse_args()
    if a.prepare:
        prepare(a.project, a.folder, a.repeats)
    else:
        evaluate(a.project, a.folder)


if __name__ == '__main__':
    main()
