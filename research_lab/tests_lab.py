"""Run with: python -m unittest research_lab.tests_lab -v, from project root."""
import unittest
import numpy as np
from research_lab.experiment_suite import (IDS,Method,_clique_expansion,
   _incidence_svd,_paper_group_scores,_fit)

class LabTests(unittest.TestCase):
 def setUp(self):
  self.ids=['n1','n2','n3','n4','n5','n6']
  self.X=np.array([[1,0],[1,.1],[.1,1],[0,1],[.3,.8],[.95,.05]],dtype=float)
  self.edges=[{'id':'e1','year':2020,'members':['n1','n2','n3'],
               'relation_type':'test','provenance':{'article_id':'paperA'}},
              {'id':'e2','year':2020,'members':['n4','n5','n6'],
               'relation_type':'test','provenance':{'article_id':'paperB'}}]
 def test_clique_expansion_preserves_expected_pair_count(self):
  proj=_clique_expansion(self.edges)
  self.assertEqual(len(proj),6)
  self.assertTrue(all(len(e['members'])==2 for e in proj))
 def test_incidence_embedding_covers_all_nodes(self):
  Z=_incidence_svd(self.ids,self.edges,17)
  self.assertEqual(Z.shape[0],len(self.ids))
 def test_all_method_specs_have_distinct_ids(self):
  self.assertGreaterEqual(len(IDS),10)
  self.assertEqual(len(IDS),len(set(IDS)))
 def test_semantic_model_covers_all_nodes(self):
  out,_=_fit(self.ids,self.X,self.edges,IDS['semantic_kmeans'],17)
  self.assertEqual(len(out),len(self.ids))
 def test_article_groups_calculated_from_original_events(self):
  p=_paper_group_scores(self.edges,{'n1':0,'n2':0,'n3':1,'n4':1,'n5':1,'n6':1})
  self.assertAlmostEqual(p['paperA'],.5)
  self.assertEqual(p['paperB'],0)
if __name__=='__main__':unittest.main()
