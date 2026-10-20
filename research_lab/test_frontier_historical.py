"""Synthetic-fixture regression tests; never impersonate real-domain validation."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_lab import retrieval_frontier as frontier
from research_lab import frontier_historical as historical


class HistoricalFrontierTests(unittest.TestCase):
    @staticmethod
    def frozen_fixture():
        rank = {
            'schema': 'chronohyper_gold_separated_budget_frontier_v1',
            'evaluation_stage': 'HISTORICAL_REUSED_QUESTIONS_DEVELOPMENT_ONLY',
            'gold_accessed_by_ranker': False,
            'full_root_exactness_asserted': True,
            'cutoff': 2025,
            'n_canonical_entities': 12,
            'budgets': [1, 2],
            'ungraded_budget_summary': {
                'flat': {'mean_total_dot_products': 12, 'mean_query_median_online_ms': .7},
                'route_1': {'mean_total_dot_products': 5, 'mean_query_median_online_ms': .5},
                'route_2': {'mean_total_dot_products': 14, 'mean_query_median_online_ms': .9},
            },
            'results': [
                {'question_id': 'Q1', 'type': 'A',
                 'flat': {'top5': [{'normalized': 'mace'}]},
                 'routes': {'1': {'top5': [{'normalized': 'nequip'}]},
                            '2': {'top5': [{'normalized': 'mace'}]}}},
                {'question_id': 'Q2', 'type': 'B',
                 'flat': {'top5': [{'normalized': 'alpha'}]},
                 'routes': {'1': {'top5': [{'normalized': 'alpha'}]},
                            '2': {'top5': [{'normalized': 'alpha'}]}}}
            ]
        }
        rank['ranking_sha256'] = frontier._rank_hash(rank)
        return rank

    def test_hash_freezes_entire_ranking(self):
        rank = self.frozen_fixture()
        self.assertEqual(frontier.verify_rankings(rank), rank['ranking_sha256'])
        tampered = copy.deepcopy(rank)
        tampered['results'][0]['routes']['1']['top5'][0]['normalized'] = 'mace'
        with self.assertRaisesRegex(ValueError, 'modified'):
            frontier.verify_rankings(tampered)

    def test_historical_gold_must_match_ids_and_task_type(self):
        rank = self.frozen_fixture()
        gold = {'Q1': {'type': 'A', 'expected_methods': ['MACE','NequIP']},
                'Q2': {'type': 'B', 'required_claims': []}}
        refs = historical._validate_gold_and_rankings(rank, gold, expected_a=1,expected_b=1)
        self.assertEqual(refs['Q1'], ['MACE','NequIP'])
        bad = copy.deepcopy(gold)
        bad['Q1']['type'] = 'B'
        with self.assertRaisesRegex(ValueError, 'type mismatch'):
            historical._validate_gold_and_rankings(rank, bad,expected_a=1,expected_b=1)
        bad2 = copy.deepcopy(gold)
        bad2['Q1']['expected_methods'] = []
        with self.assertRaisesRegex(ValueError, 'expected_methods'):
            historical._validate_gold_and_rankings(rank,bad2,expected_a=1,expected_b=1)

    def test_rerun_protects_frozen_ranking_without_opening_gold(self):
        fixed = self.frozen_fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'local_only/retrieval_frontier/historical_v2'
            path.mkdir(parents=True)
            (path/'rankings.json').write_text(json.dumps(fixed),encoding='utf-8')
            with patch.object(frontier, 'rank', side_effect=AssertionError('Should not rerank')):
                result=historical.prepare(tmp)
            self.assertEqual(result['ranking_sha256'], fixed['ranking_sha256'])

    def test_paired_sign_and_ci(self):
        s=historical._paired_sign([1,0,1,0],[0,1,1,0])
        self.assertEqual((s['wins'],s['losses'],s['ties']),(1,1,2))
        self.assertEqual(s['exact_two_sided_p_descriptive'],1.0)
        ci=historical._pair_bootstrap([1,0,-1,0],n_draws=400,seed=1)
        self.assertEqual(ci['n'],4)
        self.assertLessEqual(ci['ci95'][0], ci['mean'])
        self.assertGreaterEqual(ci['ci95'][1], ci['mean'])

    def test_genuinely_unavailable_gold_is_separate_from_retrieval_failure(self):
        rank=self.frozen_fixture()
        gold={'Q1':['MACE','NequIP']}
        details, arms=historical._per_question(rank,gold,{'mace'})
        self.assertEqual(details[0]['eligible_count'],1)
        self.assertEqual(details[0]['unavailable_count'],1)
        self.assertEqual(details[0]['scores']['flat']['hit_at_5'],1)
        self.assertEqual(details[0]['scores']['flat']['recall_at_5_all_expected'],.5)
        self.assertEqual(details[0]['scores']['flat']['recall_at_5_available'],1.)
        self.assertEqual(details[0]['scores']['route_1']['hit_at_5'],1)  # name seen, regardless of index set

    def test_not_a_confirmatory_result(self):
        rank=self.frozen_fixture()
        rank['results'] = [dict(self.frozen_fixture()['results'][0],question_id=f'Q{i}')
                           for i in range(14)]
        rank['ranking_sha256'] = frontier._rank_hash(rank)
        refs={f'Q{i}':['MACE','NequIP'] for i in range(14)}
        details,arms=historical._per_question(rank,refs,{'mace','nequip'})
        report=historical._summarize(rank,details,arms,{'mace','nequip'})
        self.assertEqual(report['n_scored_type_A'],14)
        self.assertFalse(report['genuine_new_question_evaluation_completed'])
        self.assertFalse(report['external_full_paper_entailment_verified'])
        self.assertEqual(report['quality_measures']['flat']['hit_at_5'],1)
        self.assertEqual(report['quality_measures']['route_2']['hit_at_5'],1)
        self.assertEqual(report['quality_measures']['route_1']['hit_minus_flat'],0.)


if __name__=='__main__':
    unittest.main()
