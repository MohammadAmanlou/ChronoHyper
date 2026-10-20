"""Gold-separated routed retrieval budget frontier (DEVELOPMENT-ONLY).

Ranking never reads gold, changes locked outputs, or certifies independence.
The original 2025 benchmark was previously inspected. All generated results
are local-only diagnostics unless independently sourced queries are supplied.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import platform
import statistics
import time
from pathlib import Path

import numpy as np
from scipy.sparse import hstack
from sklearn.preprocessing import normalize
from research_lab.retrieval_v2 import index, questions, top, norm

ROUTE_BUDGETS = (1, 2, 4, 8, 12)


def _rank_hash(data):
    """Stable digest of the entire immutable ranking artifact, excluding the digest field."""
    payload = {k: v for k, v in data.items() if k != 'ranking_sha256'}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def verify_rankings(data):
    ranking_digest = verify_rankings(data)
    digest = data.get('ranking_sha256')
    if not digest:
        raise ValueError('Unfrozen legacy rankings. Rerun the rank step into a NEW local-only path.')
    if digest != _rank_hash(data):
        raise ValueError('Frozen rankings were modified after rank-only stage')
    if not data.get('full_root_exactness_asserted'):
        raise ValueError('All-root exactness not confirmed')
    if not data.get('results'):
        raise ValueError('No ranked questions')
    return digest




def _path(root, value):
    candidate = Path(value)
    return candidate if candidate.is_absolute() else root / candidate


def _selected_rows(roots, groups, scores, k):
    """Union of the top-k root groups; overlapping aliases remain unique."""
    if k < 1 or k > len(roots):
        raise ValueError('Route budget outside available roots')
    selected_roots = sorted(range(len(roots)), key=lambda j: (-float(scores[j]), roots[j]))[:k]
    selected = np.unique(np.concatenate([groups[roots[j]] for j in selected_roots]))
    if not len(selected):
        raise ValueError('Empty routed candidate set')
    return selected


def _rank_full(X, Q, entries):
    scores = (X @ Q.T).toarray().ravel()
    return top(scores, np.arange(X.shape[0]), entries, k=5)


def _rank_route(X, C, Q, entries, roots, groups, k):
    centroid_scores = (C @ Q.T).toarray().ravel()
    rows = _selected_rows(roots, groups, centroid_scores, k)
    scores = (X[rows] @ Q.T).toarray().ravel()
    return top(scores, rows, entries, k=5), int(len(rows))


def _median_timed(fn, repeats):
    fn()  # warm-up excluded
    durations = []
    result = None
    for _ in range(repeats):
        before = time.perf_counter()
        result = fn()
        durations.append((time.perf_counter() - before) * 1000)
    return result, float(statistics.median(durations))


def rank(project='.', out='local_only/retrieval_frontier/rankings.json',
         question_file=None, cutoff=2025, repeats=5):
    if repeats < 1:
        raise ValueError('repeats must be positive')
    root = Path(project)
    entries, X, word, char, roots, groups, C, preprocessing_s = index(root, cutoff)
    budgets = tuple(k for k in ROUTE_BUDGETS if k <= len(roots))
    if len(roots) not in budgets:
        budgets += (len(roots),)
    queries = questions(root, question_file)
    if not queries:
        raise ValueError('No queries')
    output = []
    seen = set()
    for q in queries:
        qid = str(q.get('question_id', '')).strip()
        content = str(q.get('question', '')).strip()
        if not qid or not content or qid in seen:
            raise ValueError('Missing or duplicate query ID / empty question')
        seen.add(qid)
        # Shared query representation, candidate index and exact top-5 scorer.
        Q = normalize(hstack([word.transform([content]) * .7,
                              char.transform([content]) * .3], format='csr'))
        baseline, flat_ms = _median_timed(lambda: _rank_full(X, Q, entries), repeats)
        route = {}
        previous_rows = 0
        for k in budgets:
            (res, n), elapsed = _median_timed(
                lambda budget=k: _rank_route(X, C, Q, entries, roots, groups, budget), repeats)
            if n < previous_rows:
                raise AssertionError('More roots cannot reduce the candidate union')
            previous_rows = n
            if k == len(roots) and res != baseline:
                raise AssertionError('All-root routed ranking must reproduce exact flat top-5')
            route[str(k)] = {
                'top5': res, 'candidates_scored': n,
                'centroid_scores': len(roots),
                'median_online_ms_including_routing_and_top5': elapsed,
            }
        output.append({'question_id': qid, 'type': q.get('type', ''),
                       'flat': {'top5': baseline, 'candidates_scored': len(entries),
                                'median_online_ms_including_top5': flat_ms},
                       'routes': route})
    ungraded = {
        'flat': {
            'mean_candidate_dot_products': float(len(entries)),
            'mean_centroid_dot_products': 0.0,
            'mean_total_dot_products': float(len(entries)),
            'mean_query_median_online_ms': float(statistics.mean(
                x['flat']['median_online_ms_including_top5'] for x in output)),
        }
    }
    for k in budgets:
        key = str(k)
        mean_c = float(statistics.mean(x['routes'][key]['candidates_scored'] for x in output))
        ungraded['route_' + key] = {
            'mean_candidate_dot_products': mean_c,
            'mean_centroid_dot_products': float(len(roots)),
            'mean_total_dot_products': mean_c + len(roots),
            'fraction_of_flat_online_dot_products': (mean_c + len(roots)) / len(entries),
            'mean_query_median_online_ms': float(statistics.mean(
                x['routes'][key]['median_online_ms_including_routing_and_top5']
                for x in output)),
        }
    result = {
        'schema': 'chronohyper_gold_separated_budget_frontier_v1',
        'evaluation_stage': ('HISTORICAL_REUSED_QUESTIONS_DEVELOPMENT_ONLY'
                             if question_file is None else 'NEW_QUERY_PROVENANCE_NOT_VERIFIED'),
        'gold_accessed_by_ranker': False,
        'full_root_exactness_asserted': True,
        'quality_or_speed_superiority_claimed': False,
        'source': 'shared dated node-name and paper-title TF-IDF index',
        'cutoff': cutoff, 'repeats_per_query_arm': repeats,
        'n_queries': len(output), 'n_canonical_entities': len(entries),
        'n_roots': len(roots), 'budgets': list(budgets),
        'offline_centroid_build_s': preprocessing_s,
        'timing_scope': ('Online candidate scores, centroid routing and top-5; '
                         'shared query vector construction and offline indexing excluded. '
                         'Order-dependent CPU timings are diagnostics, not speedup guarantees.'),
        'ungraded_budget_summary': ungraded,
        'machine': {'python': platform.python_version(), 'system': platform.system(),
                    'processor': platform.processor()},
        'results': output,
    }
    result['ranking_sha256'] = _rank_hash(result)
    dest = _path(root, out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('RANK FRONTIER', len(output), 'queries;', len(roots), 'roots;',
          len(entries), 'entities; no gold accessed;', dest)
    for arm, stats in ungraded.items():
        print(arm, 'mean total dot-products',
              round(stats['mean_total_dot_products'], 1),
              'mean query-median ms', round(stats['mean_query_median_online_ms'], 4))
    return result


def score(project='.', rankings='local_only/retrieval_frontier/rankings.json',
          references='', out='local_only/retrieval_frontier/score.json'):
    if not references:
        raise ValueError('Separate reference CSV required; no automatic unblinding')
    root = Path(project)
    data = json.loads(_path(root, rankings).read_text(encoding='utf-8'))
    if data.get('schema') != 'chronohyper_gold_separated_budget_frontier_v1':
        raise ValueError('Unexpected rankings schema')
    if data.get('gold_accessed_by_ranker') is not False:
        raise ValueError('Gold may not be used while ranking')
    with _path(root, references).open(encoding='utf-8-sig', newline='') as fp:
        rows = list(csv.DictReader(fp))
    references_by_id = {}
    for r in rows:
        qid = str(r.get('question_id', '')).strip()
        if not qid or qid in references_by_id:
            raise ValueError('Missing or duplicate gold ID')
        references_by_id[qid] = {
            norm(t) for t in str(r.get('expected_methods', '')).split('|') if norm(t)}
    budgets = [str(k) for k in data['budgets']]
    arms = ['flat'] + ['route_' + k for k in budgets]
    observed = {arm: [] for arm in arms}
    costs = {arm: [] for arm in arms}
    timings = {arm: [] for arm in arms}
    paired = []
    for item in data['results']:
        gold = references_by_id.get(item['question_id'], set())
        if not gold:  # Do not grade open-ended Type B as simple name retrieval.
            continue
        hits = {}
        for arm in arms:
            datum = item['flat'] if arm == 'flat' else item['routes'][arm.removeprefix('route_')]
            found = {r['normalized'] for r in datum['top5']} & gold
            hits[arm] = int(bool(found))
            observed[arm].append({'hit': hits[arm], 'recall': len(found) / len(gold)})
            costs[arm].append(datum['candidates_scored'] +
                              (0 if arm == 'flat' else datum['centroid_scores']))
            field = ('median_online_ms_including_top5' if arm == 'flat'
                     else 'median_online_ms_including_routing_and_top5')
            timings[arm].append(datum[field])
        paired.append({'question_id': item['question_id'], 'hit': hits})
    if not paired:
        raise ValueError('No nonempty gold rows matching ranked questions')
    summary = {}
    for arm in arms:
        obs = observed[arm]
        summary[arm] = {
            'hit_at_5': statistics.mean(x['hit'] for x in obs),
            'macro_recall_at_5': statistics.mean(x['recall'] for x in obs),
            'mean_online_dot_products_including_centroids': statistics.mean(costs[arm]),
            'mean_query_median_online_ms': statistics.mean(timings[arm]),
        }
    if any(x['hit']['flat'] != x['hit']['route_' + budgets[-1]] for x in paired):
        raise AssertionError('All-root must equal flat on graded queries')
    result = {
        'schema': 'chronohyper_budget_frontier_gold_score_v1',
        'n_evaluated': len(paired), 'n_references': len(rows),
        'ranking_sha256_verified': ranking_digest,
        'evaluation_stage': data['evaluation_stage'],
        'independent_test_certified': False,
        'full_root_equivalent_to_flat': True,
        'per_arm': summary, 'paired_query_hits': paired,
        'interpretation': ('Scores are computed after rankings are frozen. '
                           'Original inspected questions are exploratory; independently '
                           'sourced references cannot be certified by this code. '
                           'Small-N Hit@5 and CPU timings do not prove general superiority.'),
    }
    dest = _path(root, out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('SCORED FRONTIER', len(paired), 'queries;', dest)
    for arm, value in summary.items():
        print(arm, 'Hit@5', round(value['hit_at_5'], 4),
              'dot products', round(value['mean_online_dot_products_including_centroids'], 1))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--rank', action='store_true')
    modes.add_argument('--score', action='store_true')
    p.add_argument('--project', default='.')
    p.add_argument('--questions', default=None)
    p.add_argument('--rankings', default='local_only/retrieval_frontier/rankings.json')
    p.add_argument('--references', default='')
    p.add_argument('--out', default=None)
    p.add_argument('--cutoff', type=int, default=2025)
    p.add_argument('--repeats', type=int, default=5)
    a = p.parse_args()
    if a.rank:
        rank(a.project, a.out or a.rankings, a.questions, a.cutoff, a.repeats)
    else:
        score(a.project, a.rankings, a.references,
              a.out or 'local_only/retrieval_frontier/score.json')


if __name__ == '__main__':
    main()
