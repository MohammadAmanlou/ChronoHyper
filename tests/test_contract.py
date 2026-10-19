"""Core invariant and no-leakage tests. Run: python -m unittest discover -s tests -v"""
import unittest,json
from pathlib import Path
from collections import Counter
import numpy as np
from src.core import edge_collapse,check_laminar,temporal_match,fit_coarse,fit_hierarchy
from src.evaluation import incidence_degree_preserving_shuffle
from src.t1_audit import parse_archive,observe
from src.run import snapshot_raw,semantic_embeddings


class Core(unittest.TestCase):
    def test_three_collapse_cases(self):
        e={'id':'e','members':['a','b','c','d'],'relation_type':'claims','provenance':{'article_year':2020}}
        a=edge_collapse(e,{'a':'x','b':'x','c':'x','d':'x'})
        self.assertTrue(a['internal']);self.assertEqual(a['multiplicity'],{'x':4})
        b=edge_collapse(e,{'a':'x','b':'x','c':'x','d':'y'})
        self.assertFalse(b['internal']);self.assertEqual(sum(b['multiplicity'].values()),4)
        c=edge_collapse(e,{'a':'x','b':'x','c':'y','d':'z'})
        self.assertEqual(len(c['coarse_members']),3);self.assertEqual(sum(c['multiplicity'].values()),4)

    def test_laminar_and_budget(self):
        ids=list('abcdef');levels=[dict.fromkeys(ids,0),dict(zip(ids,[0,0,1,1,2,2])),dict(enumerate([],0))]
        levels[2]={v:i for i,v in enumerate(ids)}
        self.assertTrue(check_laminar(levels,ids,budgets=(12,48,144)))
        bad=[levels[0],dict(zip(ids,[0,0,0,1,1,1])),dict(zip(ids,[0,1,0,0,1,2]))]
        with self.assertRaises(AssertionError):check_laminar(bad,ids,budgets=(12,48,144))

    def test_degree_arity_preserving_shuffle(self):
        es=[{'id':str(i),'year':2020,'relation_type':'claim','provenance':{'article_year':2020},'members':e} for i,e in enumerate([
            ['a','b','c'],['b','c','d'],['a','d','e','f'],['c','e','f'],['a','b','e']])]
        sh,n=incidence_degree_preserving_shuffle(es,seed=7,multiple=20)
        self.assertGreater(n,0)
        self.assertEqual(Counter(v for e in es for v in e['members']),Counter(v for e in sh for v in e['members']))
        self.assertEqual([len(e['members']) for e in es],[len(e['members']) for e in sh])
        self.assertTrue(all(len(set(e['members']))==len(e['members']) for e in sh))

    def test_stable_matching(self):
        prev={'a':0,'b':0,'c':1,'d':1}
        curr={'a':1,'b':1,'c':0,'d':0,'e':0}
        ids={0:'old0',1:'old1'}
        mapping,ev,n,w=temporal_match(prev,curr,ids,next_serial=50)
        self.assertEqual(mapping[1],'old0');self.assertEqual(mapping[0],'old1')
        self.assertTrue(any(v['event']=='growth' for v in ev))

    def test_real_archive_temporal_policy(self):
        p=Path(__file__).resolve().parents[1]/'inputs/data.zip'
        graph,articles,questions,gt=parse_archive(p)
        self.assertEqual(len(graph['nodes']),5798)
        s=snapshot_raw(graph,2024)
        ids={n['id'] for n in s['nodes']}
        self.assertEqual(len(ids),4164)
        self.assertTrue(all(e['year']<=2024 and e['provenance']['article_year']<=2024 for e in s['hyperedges']))
        self.assertTrue(all(set(e['members'])<=ids for e in s['hyperedges']))
        self.assertEqual(len(s['hyperedges']),983)

    def test_main_clustering_native_uses_source_events(self):
        ids=list('abcdefghij');nodes=[{'id':v,'surface_form':v,'type':'method'} for v in ids]
        X=np.eye(10)[:,:4].copy()
        edges=[{'id':'e'+str(i),'members':ids[i:i+3],'relation_type':'uses','provenance':{'article_year':2020}} for i in range(0,8,2)]
        pred=fit_coarse(ids,X,edges,k=3,variant='joint')
        self.assertEqual(len(pred),10)
        layers=fit_hierarchy(nodes,edges,X,pred)
        self.assertTrue(check_laminar(layers,ids))

if __name__=='__main__':unittest.main()
