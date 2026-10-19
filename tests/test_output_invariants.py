import unittest,json
from pathlib import Path
from collections import defaultdict

BASE=Path(__file__).resolve().parents[1]/'outputs'

class Artifacts(unittest.TestCase):
    def test_all_levels_exhaustive_nested(self):
        for y in [2020,2022,2024,2025]:
            j=json.loads((BASE/f'hierarchy_{y}.json').read_text(encoding='utf-8'))
            arr=j['supernodes'];levels=defaultdict(list)
            for item in arr: levels[item['level']].append(item)
            self.assertEqual([len(levels[l]) for l in range(4)], [x['n_clusters'] for x in j['levels']])
            self.assertLessEqual(len(levels[0]),12);self.assertLessEqual(len(levels[1]),48);self.assertLessEqual(len(levels[2]),144)
            full={x['member_ids'][0] for x in levels[3]}
            self.assertEqual(len(full),len(levels[3]))
            for lev in range(4):
                seen=[]
                for x in levels[lev]:
                    seen.extend(x['member_ids'])
                    self.assertTrue(x['label'] and x['gloss'])
                self.assertEqual(set(seen),full)
                self.assertEqual(len(seen),len(full))
            for l in (1,2,3):
                parents={x['id']:set(x['member_ids']) for x in levels[l-1]}
                for x in levels[l]:
                    self.assertIn(x['parent_id'],parents)
                    self.assertTrue(set(x['member_ids'])<=parents[x['parent_id']])

    def test_all_original_edges_preserved_at_coarse_level(self):
        for y in [2020,2022,2024,2025]:
            met=json.loads((BASE/'metrics.json').read_text(encoding='utf-8'))['snapshots'][str(y)]
            es=json.loads((BASE/f'collapsed_edges_{y}_level0.json').read_text(encoding='utf-8'))
            self.assertEqual(len(es),met['n_train_edges'])
            self.assertEqual(len({e['id'] for e in es}),len(es))
            for e in es:
                self.assertEqual(sum(e['multiplicity'].values()),e['original_arity'])
                self.assertEqual(set(map(int,e['multiplicity'])),set(e['coarse_members']))

    def test_temporal_event_references(self):
        events=json.loads((BASE/'temporal_events.json').read_text(encoding='utf-8'))['events']
        self.assertTrue(events)
        allowed={'birth','growth','merge','split','death'}
        self.assertTrue({e['event'] for e in events}<=allowed)
        self.assertGreaterEqual(len({e['snapshot'] for e in events}),3)

    def test_evaluation_no_fake_overclaim(self):
        m=json.loads((BASE/'metrics.json').read_text(encoding='utf-8'))
        self.assertIsNone(m['label_audit']['2024']['independent_semantic_overclaim_rate'])
        self.assertEqual(m['retrieval']['summary']['evaluated_type_A'],14)
        self.assertEqual(m['retrieval']['summary']['type_B_not_scored'],4)
        self.assertEqual(m['snapshots']['2024']['robustness']['ari']['n'],5)
        self.assertGreaterEqual(m['structural_null_2024']['shuffle_count'],8)

if __name__=='__main__':unittest.main()
