"""Review handoff tests operate only on synthetic worksheet rows and fake keys."""
import csv
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from research_lab.review_handoff import SPEC, prepare, validate_response

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def _fixture(self,kind):
        sp=SPEC[kind]
        folder=self.root/sp["directory"]
        folder.mkdir(parents=True,exist_ok=True)
        headers=list(sp["fixed"])+list(sp["scored"])
        with (folder/sp["worksheet"]).open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=headers)
            w.writeheader()
            for i in range(sp["rows"]):
                row={c:"" for c in headers}
                row.update({"blind_id":f"X{i:03d}","snapshot_year":"2024",
                            "member_count":"14","member_names":"graph neural",
                            "source_article_titles":"A paper"})
                if kind=="label24":
                    row.update({"label_A":"Graph","gloss_A":"Lexical names",
                                "label_B":"Network","gloss_B":"Unknown"})
                else:
                    row["source_evidence_limit"]="paper titles only"
                w.writerow(row)
        (folder/sp["instructions"]).write_text("Judge independently.",encoding="utf-8")
        (folder/"mapping_PRIVATE.csv").write_text("secret",encoding="utf-8")
        return folder,headers
    def test_authorization_is_required(self):
        self._fixture("label24")
        with self.assertRaises(PermissionError):
            prepare(self.root,"label24")
    def test_only_whitelisted_files_in_zip(self):
        for kind in ("label24","coherence48"):
            self._fixture(kind)
            info=prepare(self.root,kind,authorization=True)
            archive=self.root/"local_only"/"reviewer_exports"/f"{kind}_KEY_FREE.zip"
            with ZipFile(archive) as z:
                names=z.namelist()
                self.assertEqual(len(names),3)
                self.assertTrue(all("PRIVATE" not in name.upper() for name in names))
                self.assertNotIn(b"secret",b"".join(z.read(name) for name in names))
            self.assertEqual(info["n_rows"],SPEC[kind]["rows"])
    def test_response_cannot_tamper_with_evidence(self):
        folder,headers=self._fixture("label24")
        form=folder/"blind_v2_v3_24.csv"
        with form.open(encoding="utf-8",newline="") as fp:
            data=list(csv.DictReader(fp))
        for row in data:
            row.update({"reviewer_id":"TEST_FIXTURE","review_notes":"Insufficient",
                        "evidence_sufficient_yes_no":"no",
                        "A_gloss_overclaim_yes_no_unclear":"unclear",
                        "B_gloss_overclaim_yes_no_unclear":"unclear"})
        output=folder/"response.csv"
        def store():
            with output.open("w",encoding="utf-8",newline="") as f:
                w=csv.DictWriter(f,fieldnames=headers)
                w.writeheader()
                w.writerows(data)
        store()
        self.assertEqual(validate_response(self.root,"label24",str(output))["n_rows"],24)
        data[0]["label_A"]="Hacked"
        store()
        with self.assertRaisesRegex(ValueError,"edited"):
            validate_response(self.root,"label24",str(output))
    def test_coherence_insufficient_never_imputed(self):
        folder,headers=self._fixture("coherence48")
        with (folder/"blind_review_48.csv").open(encoding="utf-8",newline="") as f:
            data=list(csv.DictReader(f))
        for row in data:
            row.update({"reviewer_id":"TEST_FIXTURE","evidence_notes":"Only names",
                        "evidence_sufficient_yes_no":"no"})
        dest=folder/"rated.csv"
        with dest.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=headers)
            w.writeheader()
            w.writerows(data)
        self.assertEqual(validate_response(self.root,"coherence48",str(dest))["n_rows"],48)
        data[0]["coherence_score_1_to_5"]="5"
        with dest.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=headers)
            w.writeheader()
            w.writerows(data)
        with self.assertRaisesRegex(ValueError,"insufficient"):
            validate_response(self.root,"coherence48",str(dest))

if __name__=="__main__":
    unittest.main()
