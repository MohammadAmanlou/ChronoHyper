"""Fixture tests: honest gold separation and exact all-root retrieval."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scipy.sparse import hstack, vstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from research_lab import retrieval_frontier as frontier


class BudgetFrontierTests(unittest.TestCase):
    def test_root_union_never_loses_entities(self):
        roots = ['r0', 'r1']
        groups = {'r0': np.array([0, 1]), 'r1': np.array([1, 2])}
        scores = np.array([.8, .6])
        self.assertEqual(frontier._selected_rows(roots, groups, scores, 1).tolist(), [0, 1])
        self.assertEqual(frontier._selected_rows(roots, groups, scores, 2).tolist(), [0, 1, 2])
        with self.assertRaises(ValueError):
            frontier._selected_rows(roots, groups, scores, 3)

    def test_ranking_and_gold_scoring_are_separate(self):
        texts = ['graph embeddings', 'hypergraph partition', 'temporal evolution',
                 'language modeling']
        entries = [{'name': t, 'normalized': frontier.norm(t), 'type': 'method'}
                   for t in texts]
        word = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        char = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
        X = normalize(hstack([word.fit_transform(texts) * .7,
                              char.fit_transform(texts) * .3], format='csr'))
        roots = ['r0', 'r1']
        groups = {'r0': np.array([0, 1]), 'r1': np.array([2, 3])}
        C = normalize(vstack([csr_matrix(X[groups[r]].mean(axis=0)) for r in roots]))
        fixture = (entries, X, word, char, roots, groups, C, .01)
        qs = [{'question_id': 'q1', 'question': 'graph embeddings', 'type': 'A'},
              {'question_id': 'q2', 'question': 'temporal evolution', 'type': 'A'}]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(frontier, 'index', return_value=fixture), \
                 patch.object(frontier, 'questions', return_value=qs):
                ranked = frontier.rank(root, repeats=1)
            self.assertEqual(ranked['n_queries'], 2)
            self.assertFalse(ranked['gold_accessed_by_ranker'])
            self.assertEqual(ranked['budgets'], [1, 2])
            for row in ranked['results']:
                self.assertEqual(row['flat']['top5'], row['routes']['2']['top5'])
            references = root / 'references_PRIVATE.csv'
            with references.open('w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=['question_id', 'expected_methods'])
                w.writeheader()
                w.writerow({'question_id': 'q1', 'expected_methods': 'graph embeddings'})
                w.writerow({'question_id': 'q2', 'expected_methods': 'temporal evolution'})
            outcome = frontier.score(root, references=str(references))
            self.assertEqual(outcome['n_evaluated'], 2)
            self.assertEqual(outcome['per_arm']['flat']['hit_at_5'], 1)
            self.assertEqual(outcome['per_arm']['flat']['hit_at_5'],
                             outcome['per_arm']['route_2']['hit_at_5'])
            self.assertFalse(outcome['independent_test_certified'])

    def test_duplicate_gold_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            out = root / 'local_only/retrieval_frontier'
            out.mkdir(parents=True)
            (out / 'rankings.json').write_text(json.dumps({
                'schema': 'chronohyper_gold_separated_budget_frontier_v1',
                'gold_accessed_by_ranker': False, 'budgets': [1],
                'evaluation_stage': 'HISTORICAL_REUSED_QUESTIONS_DEVELOPMENT_ONLY',
                'results': []}), encoding='utf-8')
            with (root / 'references.csv').open('w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=['question_id', 'expected_methods'])
                w.writeheader()
                w.writerow({'question_id': 'q1', 'expected_methods': 'method'})
                w.writerow({'question_id': 'q1', 'expected_methods': 'method'})
            with self.assertRaisesRegex(ValueError, 'duplicate gold'):
                frontier.score(root, references='references.csv')


if __name__ == '__main__':
    unittest.main()
