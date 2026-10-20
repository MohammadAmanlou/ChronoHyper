"""Synthetic evidence fixtures for exhaustive V3 lexical/provenance checks."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_lab.label_v3 import improve_case
from research_lab.v3_provenance_audit import audit

class V3ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for path in ('outputs_selected','research_outputs/label_v2',
                     'local_only/label_v3_dev'):
            (self.root/path).mkdir(parents=True,exist_ok=True)
        self.nodes = [
            {'id':'n1','type':'method','surface_form':'Graph Neural Network A',
             'first_seen_year':2019,'provenance':{'articles':[1]}},
            {'id':'n2','type':'method','surface_form':'Graph Neural Network B',
             'first_seen_year':2019,'provenance':{'articles':[2]}},
            {'id':'n3','type':'method','surface_form':'Graph Neural Network C',
             'first_seen_year':2020,'provenance':{'articles':[1,2]}},
        ]
        self.articles=[{'id':1,'year':2019},{'id':2,'year':2020}]
        self.row = {
            'year':2020,'level':0,'stable_id':'c0','member_count':3,
            'member_ids':['n1','n2','n3'],'eligible_member_count':3,
            'v2_label':'Graph Neural','v2_gloss':'Frozen lexical description',
            'phrase_evidence':{
                'graph neural':{'support_count':3,'support_node_ids':['n1','n2','n3'],
                                'provenance_article_ids':['1','2']}
            }}
        self._write()
    def tearDown(self):
        self.tmp.cleanup()
    def _put(self, path, value):
        (self.root/path).write_text(json.dumps(value),encoding='utf-8')
    def _write(self):
        self._put('outputs_selected/hierarchy_2020.json',
                  {'supernodes':[{'id':'c0','level':0,
                                  'member_ids':['n1','n2','n3']}]})
        self._put('research_outputs/label_v2/candidates_v2_2020.json',[self.row])
        self._put('local_only/label_v3_dev/v3_dev_2020.json',
                  [improve_case(self.row)])
    def _run(self):
        with patch('research_lab.v3_provenance_audit.parse_archive',
                   return_value=({'nodes':self.nodes},self.articles,None,None)):
            return audit(self.root,years=(2020,),expected_per_year=1)
    def test_frozen_full_member_evidence_is_accepted(self):
        result=self._run()
        self.assertEqual(result['n_labels_checked'],1)
        self.assertEqual(result['n_name_supported_leading_or_partial'],1)
        self.assertEqual(result['full_member_name_phrase_support_occurrences_checked'],3)
        self.assertIsNone(result['scientific_overclaim_rate'])
        self._run()  # Deterministic repeated run must not overwrite differing evidence.
    def test_future_source_article_is_rejected(self):
        self.articles[1]['year']=2024
        with self.assertRaisesRegex(ValueError,'undated publication provenance'):
            self._run()
    def test_changed_supporter_name_is_rejected(self):
        self.nodes[2]['surface_form']='Deep learning transformer'
        with self.assertRaisesRegex(ValueError,'unsupported/missing lexical phrase'):
            self._run()
    def test_tampered_v3_label_is_rejected(self):
        path=self.root/'local_only/label_v3_dev/v3_dev_2020.json'
        record=json.loads(path.read_text(encoding='utf-8'))
        record[0]['v3_development_label']='Superconductivity'
        path.write_text(json.dumps(record),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'V3 output changed'):
            self._run()
    def test_altered_hierarchy_members_are_rejected(self):
        self._put('outputs_selected/hierarchy_2020.json',
                  {'supernodes':[{'id':'c0','level':0,'member_ids':['n1','n2']}]})
        with self.assertRaisesRegex(ValueError,'V2 member set differs'):
            self._run()

if __name__=='__main__':
    unittest.main()
