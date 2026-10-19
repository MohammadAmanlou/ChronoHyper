"""Regressions for evidence-grounded temporal labels; no generated human ratings."""
import json
import tempfile
import unittest
from pathlib import Path
from research_lab.label_v2 import label_partition, phrases, make_blind_sheet, write_outputs


class EvidenceGroundedV2(unittest.TestCase):
    def setUp(self):
        self.nodes=[
            {'id':'n1','type':'method','surface_form':'Graph neural network force fields','first_seen_year':2019,'provenance':{'articles':[1]}},
            {'id':'n2','type':'technique','surface_form':'Graph neural network potentials','first_seen_year':2020,'provenance':{'articles':[2]}},
            {'id':'n3','type':'method','surface_form':'Atomic density functional theory','first_seen_year':2018,'provenance':{'articles':[3]}},
            {'id':'future','type':'method','surface_form':'Graph neural network special claim','first_seen_year':2028,'provenance':{'articles':[4]}}
        ]
        self.articles=[{'id':1,'year':2019},{'id':2,'year':2020},{'id':3,'year':2018},{'id':4,'year':2028}]
        self.supernodes=[{'id':'s1','level':0,'member_ids':['n1','n2'],'label':'Old topic','gloss':'Old template'},
                         {'id':'s2','level':0,'member_ids':['n3'],'label':'Other','gloss':'Other'}]

    def test_exact_contiguous_phrases(self):
        self.assertIn('neural network',phrases('Graph neural network force fields'))
        self.assertNotIn('field network',phrases('Field based on network'))

    def test_future_node_and_provenance_excluded(self):
        r,s=label_partition(self.nodes,self.supernodes,self.articles,2020)
        self.assertEqual(len(r),2)
        self.assertTrue(all(a!='4' for x in r for p in x['phrase_evidence'].values() for a in p['provenance_article_ids']))
        self.assertTrue(all('future' not in p['support_node_ids'] for x in r for p in x['phrase_evidence'].values()))
        self.assertEqual(s['lexical_source_assertions_unsupported'],0)

    def test_deterministic(self):
        a=label_partition(self.nodes,self.supernodes,self.articles,2020)[0]
        b=label_partition(self.nodes[::-1],self.supernodes[::-1],self.articles[::-1],2020)[0]
        self.assertEqual(a,b)

    def test_explicit_abstention(self):
        r,_=label_partition(self.nodes,self.supernodes,self.articles,2020)
        self.assertEqual([x for x in r if x['stable_id']=='s2'][0]['confidence'],'abstain')

    def test_blind_pairs_do_not_reveal_methods(self):
        a=label_partition(self.nodes,self.supernodes,self.articles,2020)[0]
        a[0]['year']=2022;a[1]['year']=2022
        sh,key=make_blind_sheet(a,[],self.nodes,self.articles)
        self.assertTrue(sh)
        self.assertFalse(any('v1' in k or 'v2' in k for k in sh[0]))
        self.assertEqual(set(key.values())-{'A','B'},set())

    def test_original_data_end_to_end_if_present(self):
        project=Path(__file__).resolve().parents[1]
        if not (project/'inputs/data.zip').exists() or not (project/'outputs_selected/hierarchy_2024.json').exists():self.skipTest('Original data/output not present')
        with tempfile.TemporaryDirectory() as d:
            a=write_outputs(project,d)
            self.assertEqual(a['years']['2024']['labels'],60)
            self.assertEqual(a['years']['2024']['lexical_source_assertions_unsupported'],0)
            self.assertEqual(a['blind_review_cases_unseen_in_prior_sheet'],24)

if __name__=='__main__':unittest.main()

class PairedEvaluation(unittest.TestCase):
    def test_never_impute_missing_reviews(self):
        import csv
        from research_lab.label_v2 import score_blind
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            fields=['year','stable_id','label_A','gloss_A','label_B','gloss_B',
              'A_accuracy_accurate_vague_wrong','B_accuracy_accurate_vague_wrong',
              'A_gloss_overclaim_yes_no_unclear','B_gloss_overclaim_yes_no_unclear','reviewer_id']
            sheet=p/'review.csv'
            with sheet.open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
                w.writerow({'year':2024,'stable_id':'s1','A_accuracy_accurate_vague_wrong':'accurate',
                    'B_accuracy_accurate_vague_wrong':'wrong','reviewer_id':'reviewer_1',
                    'A_gloss_overclaim_yes_no_unclear':'no','B_gloss_overclaim_yes_no_unclear':'unclear'})
                w.writerow({'year':2024,'stable_id':'s2','A_accuracy_accurate_vague_wrong':'accurate',
                    'B_accuracy_accurate_vague_wrong':'wrong','reviewer_id':'',
                    'A_gloss_overclaim_yes_no_unclear':'no','B_gloss_overclaim_yes_no_unclear':'yes'})
            k=p/'key.json';k.write_text(json.dumps({'2024:s1':'A','2024:s2':'B'}))
            x=score_blind(sheet,k,p/'out')
            self.assertEqual(x['paired_cases_with_both_ratings_and_reviewer_id'],1)
            self.assertEqual(x['requested_cases'],2)
            self.assertEqual(x['status'],'PARTIAL_REVIEW')
            self.assertEqual(x['v2_wins'],1)

class AIPairedDiagnostic(unittest.TestCase):
    def test_unblinding_requires_matching_original_both_arms(self):
        import csv
        from research_lab.label_v2 import summarize_ai_review
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/'research_outputs/label_v2'
            p.mkdir(parents=True)
            c=[{'year':2022,'stable_id':'s1','v1_label':'old','v1_gloss':'old gloss',
                'v2_label':'new','v2_gloss':'new gloss'}]
            (p/'candidates_v2_2022.json').write_text(json.dumps(c))
            (p/'candidates_v2_2024.json').write_text('[]')
            # Function deliberately refuses partial/incomplete or ambiguous 24-case audits.
            with (p/'BLIND_LABEL_COMPARISON_TO_FILL.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['year','stable_id','label_A','gloss_A','label_B','gloss_B'])
                w.writeheader()
                w.writerow({'year':2022,'stable_id':'s1','label_A':'new','gloss_A':'new gloss',
                            'label_B':'old','gloss_B':'old gloss'})
            with (p/'ai_label_review.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['year','stable_id','A_label_rating_AI','B_label_rating_AI',
                    'provisional_A_B_preference_AI','not_independent_human'])
                w.writeheader()
                w.writerow({'year':2022,'stable_id':'s1','A_label_rating_AI':'accurate',
                            'B_label_rating_AI':'wrong','provisional_A_B_preference_AI':'A',
                            'not_independent_human':'TRUE'})
            with self.assertRaisesRegex(ValueError,'Expected 24 unique'):
                summarize_ai_review(root)
