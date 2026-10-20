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

class FrozenKeyRecovery(unittest.TestCase):
    def test_recover_existing_24_pairs_matches_exact_candidate_texts(self):
        from research_lab.label_v2 import recover_frozen_blind_key
        project=Path(__file__).resolve().parents[1]
        if not (project/'research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv').exists():
            self.skipTest('Frozen user data unavailable')
        with tempfile.TemporaryDirectory() as d:
            private=Path(d)/'local_key.json'
            key=recover_frozen_blind_key(project,private)
            self.assertEqual(len(key),24)
            self.assertEqual(set(key.values()),{'A','B'})
            self.assertEqual(recover_frozen_blind_key(project,private),key)

class ReviewOriginSafety(unittest.TestCase):

    def test_raw_ai_review_status_is_not_human_confirmation(self):
        from research_lab.label_v2 import score_blind
        root=Path(__file__).resolve().parents[1]
        blank=root/'research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv'
        if not blank.exists():self.skipTest('Canonical review data unavailable')
        import csv
        with blank.open(encoding='utf-8-sig',newline='') as f:
            cases=list(csv.DictReader(f))
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            # Exact frozen columns preserved; ratings are explicitly marked AI.
            for case in cases:
                case['A_accuracy_accurate_vague_wrong']='vague'
                case['B_accuracy_accurate_vague_wrong']='vague'
                case['A_gloss_overclaim_yes_no_unclear']='unclear'
                case['B_gloss_overclaim_yes_no_unclear']='unclear'
                case['reviewer_id']='AI_PRELIM_SANITY_CHECK'
            with (p/'ai.csv').open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(cases[0]))
                writer.writeheader();writer.writerows(cases)
            from research_lab.label_v2 import recover_frozen_blind_key
            recover_frozen_blind_key(root,p/'key.json')
            out=score_blind(p/'ai.csv',p/'key.json',p/'out')
            self.assertEqual(out['status'],'COMPLETE_AI_ONLY_DIAGNOSTIC')
            self.assertEqual(out['paired_cases_with_both_ratings_and_reviewer_id'],24)
            cases[0]['label_A']='TAMPERED'
            with (p/'wrong.csv').open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(cases[0]))
                writer.writeheader();writer.writerows(cases)
            with self.assertRaisesRegex(ValueError,'changed original evidence'):
                score_blind(p/'wrong.csv',p/'key.json',p/'out2')
    def test_ai_identified_rows_cannot_be_reported_as_human(self):
        import csv
        from research_lab.label_v2 import score_blind
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            fields=['year','stable_id','A_accuracy_accurate_vague_wrong',
              'B_accuracy_accurate_vague_wrong','A_gloss_overclaim_yes_no_unclear',
              'B_gloss_overclaim_yes_no_unclear','reviewer_id']
            with (p/'sheet.csv').open('w',newline='',encoding='utf-8') as fp:
                w=csv.DictWriter(fp,fieldnames=fields)
                w.writeheader()
                w.writerow({'year':2024,'stable_id':'s1',
                   'A_accuracy_accurate_vague_wrong':'vague',
                   'B_accuracy_accurate_vague_wrong':'accurate',
                   'A_gloss_overclaim_yes_no_unclear':'unclear',
                   'B_gloss_overclaim_yes_no_unclear':'no',
                   'reviewer_id':'AI_PRELIM_PERSPECTIVE_01'})
            (p/'key.json').write_text(json.dumps({'2024:s1':'B'}),encoding='utf-8')
            result=score_blind(p/'sheet.csv',p/'key.json',p/'out')
            self.assertEqual(result['status'],'COMPLETE_AI_ONLY_DIAGNOSTIC')
            self.assertTrue(result['all_reported_reviewers_explicitly_ai'])
            self.assertFalse(result['human_independence_verified'])


class V2FullMembershipSourceAudit(unittest.TestCase):
    def test_frozen_24_glosses_are_scoped_correctly(self):
        import csv
        from research_lab.label_v2 import audit_v2_24_literal_source_claims
        project=Path(__file__).resolve().parents[1]
        if not (project/'inputs/data.zip').is_file():self.skipTest('Original data archive not available')
        with tempfile.TemporaryDirectory() as temp:
            summary=audit_v2_24_literal_source_claims(project,temp)
            self.assertEqual(summary['n_literal_count_claims'],23)
            self.assertEqual(summary['n_qualitative_abstentions'],1)
            self.assertIsNone(summary['full_text_scientific_overclaim_rate'])
            self.assertEqual(summary['full_text_scientific_overclaim_unclear_n'],24)
            with (Path(temp)/'v2_gloss_source_audit_24.csv').open(encoding='utf-8-sig',newline='') as fp:
                rows=list(csv.DictReader(fp))
            self.assertEqual(len(rows),24)
            self.assertEqual(sum(r['machine_lexical_claim_status']=='PASS_FULL_MEMBER_RECOUNT' for r in rows),23)
            self.assertTrue(all(r['independent_scientific_overclaim_status']=='unclear' for r in rows))


class ScopedV2TitleAITable(unittest.TestCase):
    def test_ai_title_ratings_are_source_scoped_and_not_expert_verdicts(self):
        import csv
        root=Path(__file__).resolve().parents[1]
        p=root/'research_outputs/label_v2/v2_title_ai_views_24.csv'
        with p.open(encoding='utf-8-sig',newline='') as file:
            rows=list(csv.DictReader(file))
        self.assertEqual(len(rows),24)
        self.assertEqual(len({(x['year'],x['stable_id']) for x in rows}),24)
        self.assertEqual(sum(x['AI_views_agree']=='yes' for x in rows),18)
        self.assertEqual(sum(x['AI_views_agree']=='no' for x in rows),6)
        self.assertTrue(all(x['full_paper_semantic_entailment']=='NOT_VERIFIED' for x in rows))
        self.assertTrue(all('AI_ONLY' in x['independent_review_status'] for x in rows))

class Stage3CoherenceAIRubric(unittest.TestCase):
    def test_48_case_sample_name_coherence_reproduction_and_scoped_reporting(self):
        from research_lab.coherence_ai import generate_form, analyze
        import hashlib, shutil
        root=Path(__file__).resolve().parents[1]
        frozen=root/'research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv'
        if not frozen.exists():self.skipTest('Frozen selected A/B cases not found')
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            target=base/'research_outputs/label_v2'
            target.mkdir(parents=True)
            shutil.copy2(frozen,target/frozen.name)
            sample,key=generate_form(base)
            self.assertEqual(len(sample),48)
            self.assertEqual(len(key),48)
            with (base/'local_only/reviews/coherence/coherence_blind_48.csv').open('rb') as fp:
                self.assertEqual(hashlib.sha256(fp.read()).hexdigest(),'1721c535c698a455666ec8d631bbebc66de79180eddc0b857633255755b43313')
            score_src=root/'research_outputs/coherence_ai/ratings_48_AI.csv'
            score_dst=base/'research_outputs/coherence_ai/ratings_48_AI.csv'
            score_dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(score_src,score_dst)
            result=analyze(base)
            self.assertEqual((result['n_pairs'],result['real_higher_pairs'],result['null_higher_pairs'],result['tie_pairs']),(24,19,2,3))
            self.assertAlmostEqual(result['mean_real'],3.6666666666666665)
            self.assertAlmostEqual(result['mean_null'],2.3333333333333335)
            self.assertFalse(result['strict_blind_independence'])


class V2GlossAuditCLI(unittest.TestCase):
    def test_cli_v2_gloss_audit_flag(self):
        import subprocess
        import sys
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            p=subprocess.run([sys.executable, "-m", "research_lab.label_v2",
                "--project", str(root), "--out", tmp, "--audit-v2-gloss"],
                cwd=str(root), text=True, capture_output=True, timeout=90)
            self.assertEqual(p.returncode, 0, p.stderr)
            with (Path(tmp)/"v2_gloss_source_summary_24.json").open(encoding="utf-8") as fp:
                r=json.load(fp)
            self.assertEqual((r["n_literal_count_claims"], r["n_qualitative_abstentions"]),(23,1))
            self.assertEqual(r["full_text_scientific_overclaim_unclear_n"], 24)
            self.assertIsNone(r["full_text_scientific_overclaim_rate"])


class FreshSemanticBlindPacket(unittest.TestCase):
    def test_new_48_blind_samples_and_local_scoring(self):
        import csv
        from research_lab.blind_paper_eval import prepare, score
        root=Path(__file__).resolve().parents[1]
        if not (root/'inputs/data.zip').exists():
            self.skipTest('Employer dataset unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            packet=Path(tmp)/'private_packet'
            forms,keys=prepare(root,packet)
            self.assertEqual(len(forms),48)
            self.assertEqual(len(keys),48)
            self.assertEqual(len({x['blind_id'] for x in forms}),48)
            self.assertEqual(sum(x['condition']=='REAL' for x in keys),24)
            self.assertEqual(sum(x['condition']=='MIXED_CONTROL' for x in keys),24)
            for year in (2020,2022,2024):
                self.assertEqual(sum(int(x['snapshot_year'])==year for x in forms),16)
            old=root/'research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv'
            with old.open(encoding='utf-8-sig',newline='') as f:
                previous={(int(x['year']),x['stable_id']) for x in csv.DictReader(f)}
            self.assertTrue(all((int(k['snapshot_year']),k['target_cluster']) not in previous for k in keys))
            self.assertFalse(any('condition' in row or 'target_cluster' in row for row in forms))
            for row in forms:
                row['coherence_score_1_to_5']='3'
                row['evidence_sufficient_yes_no']='yes'
                row['reviewer_id']='TEST_SIMULATED_NOT_AN_ACTUAL_ASSESSOR'
                row['evidence_notes']='Test-only fixture, not scientific evidence'
            ratings=packet/'fake_test_only.csv'
            with ratings.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(forms[0]));writer.writeheader();writer.writerows(forms)
            result=score(root,ratings,packet,packet/'test_result.json')
            self.assertEqual(result['evaluable_pairs'],24)
            self.assertEqual((result['real_higher_pairs'],result['control_higher_pairs'],result['ties']),(0,0,24))
            forms[0]['member_names']='ILLICIT CHANGE'
            with ratings.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(forms[0]));writer.writeheader();writer.writerows(forms)
            with self.assertRaisesRegex(ValueError,'changed frozen evidence'):
                score(root,ratings,packet,packet/'bad.json')

class FreshSemanticLimitedEvidenceExport(unittest.TestCase):
    def test_publish_anonymized_aggregate_without_private_evidence(self):
        import csv
        from research_lab.blind_paper_eval import prepare, publish_limited_summary
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            packet=Path(tmp)/'packet'
            forms,key=prepare(root,packet)
            for row in forms:
                row['coherence_score_1_to_5']='3'
                row['evidence_sufficient_yes_no']='yes'
                row['reviewer_id']='TEST_ONLY_MODEL'
                row['evidence_notes']='Test fixture, not actual scientific assessment'
            rated=packet/'simulated_only.csv'
            with rated.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(forms[0]))
                writer.writeheader();writer.writerows(forms)
            out=Path(tmp)/'aggregate'
            summary=publish_limited_summary(root,rated,packet,out)
            self.assertEqual(summary['summary']['evaluable_pairs'],24)
            self.assertEqual(summary['summary']['ties'],24)
            self.assertFalse(summary['strict_independence_verified_by_software'])
            self.assertTrue((out/'paired_coherence_AI_only.pdf').stat().st_size>1500)
            payload=(out/'summary_AI_only.json').read_text(encoding='utf-8')
            self.assertNotIn('Test fixture, not actual scientific assessment',payload)
            self.assertNotIn('source_article_titles',payload)
            self.assertNotIn('condition_key_PRIVATE',payload)
