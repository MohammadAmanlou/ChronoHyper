"""Create portable, allowlisted PRIVATE GPU Kaggle archives using POSIX ZIP names.

Python's zipfile stores archive names exactly as provided. Do not use
Windows Compress-Archive for this repository's nested inputs: it can write
backslashes into entry names, which Kaggle rejects during dataset upload.

No hidden Gold, reviewer ratings, control mappings, or prior score outputs
may be included. This is a packaging utility, not a model evaluator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

ALLOW = {
    "rank": (
        "research_lab/__init__.py",
        "research_lab/advanced_retrieval.py",
        "research_lab/retrieval_v2.py",
        "research_lab/retrieval_frontier.py",
        "inputs/data.zip",
        "outputs_selected/hierarchy_2025.json",
        "local_only/fresh_retrieval_screened34/queries_only.csv",
        "requirements_advanced.txt",
    ),
    "type-b": (
        "research_lab/__init__.py",
        "research_lab/type_b_answer_generation.py",
        "inputs/data.zip",
        "requirements_advanced.txt",
        "local_only/type_b_generation/SOURCE_PASSAGES_TO_FILL.csv",
    ),
}

DEFAULT = {
    "rank": "local_only/gpu_rank_only.zip",
    "type-b": "local_only/gpu_type_b_private.zip",
}
DENIED_PARTS = {"gold_private.csv", "mapping_private.csv"}
DENIED_FRAGMENT = ("reviews/", "rankings.json", "scored.json", "score_development_only")


def _checked_name(path: str) -> str:
    if "\\" in path:
        raise ValueError("ZIP manifest path must use POSIX forward slashes: " + path)
    relative = PurePosixPath(path)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("Invalid or unsafe ZIP path: " + path)
    if (any(part.lower() in DENIED_PARTS for part in relative.parts)
            or any(fragment in path.lower() for fragment in DENIED_FRAGMENT)):
        raise ValueError("Private evaluation data forbidden in ZIP: " + path)
    return relative.as_posix()


def create(project=".", kind="rank", output=None, entries=None):
    if kind not in ALLOW:
        raise ValueError("Unknown GPU archive kind")
    root = Path(project).resolve(strict=True)
    dest = Path(output or DEFAULT[kind])
    if not dest.is_absolute():
        dest = root / dest
    if dest.exists():
        raise FileExistsError("Existing Kaggle ZIP protected; preserve or rename: " + str(dest))
    wanted = tuple(entries if entries is not None else ALLOW[kind])
    if not wanted or len(set(wanted)) != len(wanted):
        raise ValueError("Empty or duplicate ZIP manifest")
    # Allowlist must be checked even when a caller supplies a custom manifest.
    allowed = set(ALLOW[kind])
    if set(wanted) != allowed:
        raise ValueError("GPU bundle must have EXACT approved allowlist; no extras/missing files")
    members = []
    for item in wanted:
        arcname = _checked_name(item)
        f = (root / item).resolve(strict=True)
        if not f.is_file() or not f.is_relative_to(root):
            raise ValueError("Input missing, not a regular file, or escapes project: " + item)
        members.append((f, arcname))
    dest.parent.mkdir(parents=True, exist_ok=True)
    staging = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".gpu_zip_", suffix=".zip", dir=dest.parent,
                delete=False) as temp:
            staging = Path(temp.name)
        with ZipFile(staging, mode="w", compression=ZIP_DEFLATED,
                     compresslevel=6, allowZip64=True) as z:
            for src, arcname in members:
                z.write(src, arcname=arcname)
        with ZipFile(staging, "r") as z:
            actual = z.namelist()
            expected = [arc for _, arc in members]
            if actual != expected:
                raise AssertionError("Archive member list differs from approved manifest")
            if any("\\" in name or name.startswith("/")
                   or ".." in PurePosixPath(name).parts for name in actual):
                raise AssertionError("Invalid path separator or unsafe ZIP entry")
            if z.testzip() is not None:
                raise AssertionError("Archive failed CRC integrity check")
            if any("gold_private" in name.lower() or "mapping_private" in name.lower()
                   or "reviews/" in name.lower() for name in actual):
                raise AssertionError("Sensitive grading data detected")
        # Exclusive creation: do not accidentally replace old zipped evidence.
        with dest.open("xb") as out, staging.open("rb") as inp:
            import shutil
            shutil.copyfileobj(inp, out)
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()
        result = {
            "zip": str(dest), "kind": kind, "members": [m[1] for m in members],
            "sha256": digest, "kaggle_path_separator_validated": True,
            "gold_or_reviewers_included": False,
            "keep_kaggle_dataset_private": True
        }
        print(json.dumps(result, indent=2))
        return result
    finally:
        if staging is not None:
            staging.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".")
    p.add_argument("--kind", choices=sorted(ALLOW), default="rank")
    p.add_argument("--out")
    args = p.parse_args()
    create(args.project, args.kind, args.out)


if __name__ == "__main__":
    main()
