"""Regression: Windows Kaggle ZIP member names must use '/' not '\\'."""
from __future__ import annotations
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts import make_gpu_zip


class PortableKaggleZipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for item in make_gpu_zip.ALLOW["rank"]:
            path = self.root / item
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(("synthetic only " + item).encode("utf-8"))
        # Source upload from Constructor contains sensitive reference truth.
        # The nested ZIP *must* be stripped during GPU packaging.
        data = self.root / "inputs/data.zip"
        data.unlink()
        with ZipFile(data, "w") as z:
            z.writestr("data/tkh_collection10.json", '{"nodes":[],"hyperedges":[]}')
            z.writestr("data/collection10_articles.csv", "id,title,year\\n")
            z.writestr("data/questions.csv", "question_id;question;type\\n")
            z.writestr("data/ground_truth.json", "TOP SECRET CONTROL GOLD")
        private = self.root / "local_only/fresh_retrieval_screened34/gold_PRIVATE.csv"
        private.write_text("HIDDEN GOLD MUST NOT BE PACKAGED", encoding="utf-8")
        self.gold_path = private

    def tearDown(self):
        self.temp.cleanup()

    def test_rank_only_archive_uses_posix_paths_and_is_minimal(self):
        result = make_gpu_zip.create(self.root, "rank")
        dest = Path(result["zip"])
        with ZipFile(dest) as archive:
            names = archive.namelist()
            self.assertEqual(names, list(make_gpu_zip.ALLOW["rank"]))
            self.assertTrue(all("\\" not in n and "/" in n
                                for n in names if "/" in n))
            self.assertNotEqual(archive.read("inputs/data.zip"),
                                (self.root / "inputs/data.zip").read_bytes())
            with ZipFile(io.BytesIO(archive.read("inputs/data.zip"))) as nested:
                self.assertEqual(nested.namelist(),
                                 list(make_gpu_zip.DATA_INPUTS["rank"]))
                self.assertNotIn("data/ground_truth.json", nested.namelist())
            self.assertNotIn("HIDDEN GOLD", "\n".join(
                archive.read(name).decode("utf-8")
                for name in names if name != "inputs/data.zip"))
        self.assertEqual(result["sha256"], hashlib.sha256(dest.read_bytes()).hexdigest())
        self.assertTrue(result["kaggle_path_separator_validated"])

    def test_archive_refuses_overwrite(self):
        make_gpu_zip.create(self.root, "rank")
        with self.assertRaises(FileExistsError):
            make_gpu_zip.create(self.root, "rank")

    def test_archive_refuses_extra_gold_even_via_custom_manifest(self):
        bad = list(make_gpu_zip.ALLOW["rank"]) + [
            "local_only/fresh_retrieval_screened34/gold_PRIVATE.csv"
        ]
        with self.assertRaisesRegex(ValueError, "EXACT approved allowlist"):
            make_gpu_zip.create(self.root, "rank", entries=bad)

    def test_archive_refuses_windows_backslash_members(self):
        with self.assertRaisesRegex(ValueError, "forward slashes"):
            make_gpu_zip._checked_name(r"research_lab\advanced_retrieval.py")

    def test_type_b_package_uses_slashes(self):
        for item in make_gpu_zip.ALLOW["type-b"]:
            path = self.root / item
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("fake source passage", encoding="utf-8")
        result = make_gpu_zip.create(self.root, "type-b")
        with ZipFile(result["zip"]) as archive:
            self.assertEqual(archive.namelist(),list(make_gpu_zip.ALLOW["type-b"]))
            self.assertTrue(all("\\" not in n for n in archive.namelist()))
            with ZipFile(io.BytesIO(archive.read("inputs/data.zip"))) as nested:
                self.assertEqual(nested.namelist(),
                                 list(make_gpu_zip.DATA_INPUTS["type-b"]))
                self.assertNotIn("data/ground_truth.json", nested.namelist())


if __name__ == "__main__":
    unittest.main()
