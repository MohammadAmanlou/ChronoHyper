"""Regression checks for Constructor B-question source retrieval audit."""
import json
import tempfile
import unittest
from pathlib import Path

from research_lab.type_b_source_audit import rank, score, stable_json

ROOT=Path(__file__).resolve().parents[1]

class TypeBSourceAudit(unittest.TestCase):
    def test_real_data_rank_without_gold_and_score(self):
        if not (ROOT/'inputs/data.zip').exists() or not (ROOT/'outputs_selected/hierarchy_2025.json').exists():
            self.skipTest('Real Constructor data unavailable')
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            a=rank(ROOT,out)
            self.assertEqual(a['stage'],'GOLD_BLIND_RANKING')
            self.assertEqual(len(a['questions']),4)
            self.assertEqual(a['n_eligible_articles'],46)
            self.assertTrue(a['gold_was_not_opened'])
            self.assertTrue(all(int(x['year'])<=2025 for x in a['public_article_index']))
            self.assertTrue(all(set(q['hier_ranked_paper_ids']).issubset(set(q['flat_ranked_paper_ids'])) for q in a['questions']))
            b=score(ROOT,out,n_random=101)
            self.assertEqual(b['n_type_b'],4)
            self.assertFalse(b['claim_answer_accuracy_measured'])
            with (out/'CLAIM_LEVEL_REVIEW_BLANK.csv').open(encoding='utf-8-sig',newline='') as f:
                review_rows=list(__import__('csv').DictReader(f))
            self.assertEqual(len(review_rows),36)
            self.assertTrue(all(z['n_gold_sources_exact_available']<=z['n_gold_sources'] for z in b['question_breakdown']))
            self.assertTrue(all(not any(k.startswith('manual_') and z[k] for k in z) for z in review_rows))

    def test_modified_ranking_refused(self):
        if not (ROOT/'inputs/data.zip').exists():self.skipTest('No source')
        with tempfile.TemporaryDirectory() as temp:
            o=Path(temp)
            a=rank(ROOT,o)
            a['questions'][0]['flat_ranked_paper_ids'].reverse()
            (o/'frozen_rankings.json').write_text(json.dumps(a))
            with self.assertRaisesRegex(ValueError,'changed'):
                score(ROOT,o,n_random=1)

    def test_name_normalization_is_conservative(self):
        from research_lab.type_b_source_audit import name_key
        self.assertEqual(name_key('E(3)-equivariant'),name_key('e3 EQUIVARIANT'))
        self.assertNotEqual(name_key('inter-atomic'),name_key('intra-atomic'))

if __name__=='__main__':unittest.main()
