"""Synthetic regressions for source-delta temporal locality (no answer gold)."""
import unittest
from research_lab.temporal_locality_audit import assignments, dated_edges, paired_locality

def doc(year, parts):
    groups = {}
    for node, label in parts.items():
        groups.setdefault(label, []).append(node)
    return {"cutoff":year,"supernodes":[
        {"id":label,"level":0,"member_ids":members}
        for label, members in sorted(groups.items())
    ]}

def graph():
    return {
        "nodes":[
            {"id":n,"type":"method","first_seen_year":2020}
            for n in "abcd"
        ],
        "hyperedges":[
            {"id":"old","year":2019,"members":["a","c"],
             "provenance":{"article_year":2019,"article_id":10}},
            {"id":"new","year":2022,"members":["b","d"],
             "provenance":{"article_year":2022,"article_id":20}},
            {"id":"future_source","year":2022,"members":["a","b"],
             "provenance":{"article_year":2024,"article_id":30}},
        ],
    }

class TemporalLocalityAuditTests(unittest.TestCase):
    def test_churn_localized_near_a_new_source_hyperedge(self):
        p=doc(2020,{"a":"X","b":"X","c":"Y","d":"Y"})
        q=doc(2022,{"a":"X","b":"Y","c":"Y","d":"Y"})
        x=paired_locality(graph(),p,q,2020,2022,repetitions=49,seed=2)
        self.assertEqual(x["shared_preexisting_nodes"],4)
        self.assertEqual(x["new_hyperedges_added"],1)
        self.assertEqual(x["shared_nodes_touched_by_new_native_hyperedge"],2)
        self.assertEqual(x["root_identity_changes_touched"],1)
        self.assertEqual(x["root_identity_changes_untouched"],0)
        self.assertAlmostEqual(x["touched_minus_untouched_change_rate"],0.5)
        self.assertFalse(x.get("gold_questions_read",False))
        self.assertEqual(x["table"],{
            "touched_changed":1,"touched_unchanged":1,
            "untouched_changed":0,"untouched_unchanged":2
        })

    def test_churn_outside_new_evidence_is_not_silently_hidden(self):
        p=doc(2020,{"a":"X","b":"X","c":"Y","d":"Y"})
        q=doc(2022,{"a":"Y","b":"X","c":"Y","d":"Y"})
        x=paired_locality(graph(),p,q,2020,2022,repetitions=39,seed=3)
        self.assertEqual(x["root_identity_changes_touched"],0)
        self.assertEqual(x["root_identity_changes_untouched"],1)
        self.assertLess(x["touched_minus_untouched_change_rate"],0)

    def test_future_source_evidence_does_not_leak(self):
        self.assertEqual(set(dated_edges(graph(),2022)),{"old","new"})
        self.assertEqual(set(dated_edges(graph(),2020)),{"old"})

    def test_heldout_original_papers_excluded_from_model_exposure(self):
        self.assertEqual(set(dated_edges(graph(),2022,excluded_source_papers={"20"})),{"old"})
        p=doc(2020,{"a":"X","b":"X","c":"Y","d":"Y"})
        q=doc(2022,{"a":"X","b":"Y","c":"Y","d":"Y"})
        z=paired_locality(graph(),p,q,2020,2022,
                          repetitions=19,seed=7,excluded_source_papers={"20"})
        self.assertEqual(z["new_hyperedges_added"],0)
        self.assertEqual(z["shared_nodes_touched_by_new_native_hyperedge"],0)
        self.assertEqual(z["root_identity_changes_untouched"],1)

    def test_reject_non_laminar_root_overlap(self):
        with self.assertRaisesRegex(ValueError,"multiple root clusters"):
            assignments({"supernodes":[
                {"id":"A","level":0,"member_ids":["a","b"]},
                {"id":"B","level":0,"member_ids":["a","c"]}
            ]})

    def test_reject_deleted_original_events(self):
        p=doc(2020,{"a":"X","b":"X","c":"Y","d":"Y"})
        q=doc(2022,{"a":"X","b":"X","c":"Y","d":"Y"})
        # Source-node loss is forbidden; the original graph must be monotonic.
        q["supernodes"][0]["member_ids"].remove("a")
        with self.assertRaisesRegex(ValueError,"not nested"):
            paired_locality(graph(),p,q,2020,2022,repetitions=9)

    def test_deterministic_seed_repeats_conditional_pvalue(self):
        p=doc(2020,{"a":"X","b":"X","c":"Y","d":"Y"})
        q=doc(2022,{"a":"X","b":"Y","c":"Y","d":"Y"})
        a=paired_locality(graph(),p,q,2020,2022,repetitions=49,seed=91)
        b=paired_locality(graph(),p,q,2020,2022,repetitions=49,seed=91)
        self.assertEqual(a,b)

if __name__=="__main__":
    unittest.main()
