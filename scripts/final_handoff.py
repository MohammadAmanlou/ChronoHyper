"""Read-only Constructor handoff checks and optional PRIVATE tracked-file ZIP.

Usage:
  python scripts/final_handoff.py --project .
  python scripts/final_handoff.py --project . --package

The ZIP is created from git HEAD using git archive, not the working tree.
It includes provider-supplied inputs/data.zip; share ONLY with an authorized
Constructor reviewer. It NEVER includes ignored local_only/, .env or credentials.

Scientific qualifications are explicit; no human-independent semantic
validation, successful application, or statistical win is inferred here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

YEARS = ("2020", "2022", "2024")
BASE_FILES = (
    "README.md", "AI_USAGE.md", "requirements.txt",
    "report.pdf", "report.md", "metrics.json", "inputs/data.zip",
    "src/core.py", "verify_selected_outputs.py", "final_preflight.py",
    "research_outputs/model_lock.json",
    "outputs_selected/selected_export_manifest.json",
    "outputs_selected/temporal_events.json",
    "docs/ASSIGNMENT_SOURCE.md",
)
YEAR_FILES = tuple(
    f"outputs_selected/{prefix}_{year}{suffix}"
    for year in YEARS
    for prefix, suffix in (
        ("hierarchy", ".json"),
        ("label_evidence", ".json"),
        ("collapsed_edges", "_level0.json"),
    )
)
NEEDED = BASE_FILES + YEAR_FILES


def _git(root: Path, *args: str, capture: bool = True):
    return subprocess.run(
        ["git", *args], cwd=root, check=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    ).stdout.strip() if capture else None


def _digest(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as src:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def audit(root: Path):
    root = root.resolve()
    blockers = []
    warnings = [
        "Independent expert full-paper label/gloss entailment not yet confirmed.",
        "Type-B generated-answer factual correctness not independently established.",
        "Flat/Route-4 retrieval does not outperform flat in accuracy on 34 already-inspected same-corpus cases.",
        "BGE/Qwen3 exploratory same-corpus models were tuned/compared after inspecting results; paired 5 wins/3 losses/26 ties, p=0.7266 is not significant.",
        "Structural degree/arity null p=0.69, and held-out source-group cut worsened: never claim superiority.",
    ]
    paths = {}
    for name in NEEDED:
        path = root / name
        if not path.is_file() or not path.stat().st_size:
            blockers.append("Required tracked deliverable missing/empty: " + name)
        else:
            paths[name] = {"bytes": path.stat().st_size, "sha256": _digest(path)}
    head = None
    branch = None
    dirty = None
    try:
        head = _git(root, "rev-parse", "HEAD")
        branch = _git(root, "branch", "--show-current")
        dirty = _git(root, "status", "--porcelain", "--untracked-files=normal")
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        blockers.append("Not a readable local Git checkout: " + str(exc))
    if dirty:
        blockers.append(
            "Working tree is not clean; inspect 'git status --short' before packaging. "
            "Never auto-restore or overwrite local work."
        )
    if branch and branch != "main":
        warnings.append("Checked-out branch is " + branch + ", not the main release branch.")

    manifest_path = root / "outputs_selected/selected_export_manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            reference = manifest.get("dataset_sha256")
            if reference and "inputs/data.zip" in paths:
                if reference != paths["inputs/data.zip"]["sha256"]:
                    blockers.append("Original provider input ZIP does not match selected output manifest.")
            elif not reference:
                warnings.append("Selected export manifest does not expose the original input ZIP digest.")
            if manifest.get("locked_method") not in (None, "native_temporal_20"):
                blockers.append("Selected manifest method differs from predeclared native_temporal_20.")
        except (ValueError, OSError) as exc:
            blockers.append("Cannot parse selected export manifest: " + str(exc))

    # A private original provider input archive may include reference Gold.
    # Do not inspect or copy a hidden key, and never publish this handoff ZIP.
    page_count = None
    pdf = root / "report.pdf"
    if pdf.is_file():
        try:
            import pymupdf  # optional locally installed for open-access PDF audit
            with pymupdf.open(str(pdf)) as doc:
                page_count = doc.page_count
            if not 3 <= page_count <= 5:
                blockers.append(f"Report PDF has {page_count} pages, not the required 3–5.")
        except ImportError:
            warnings.append(
                "PDF page count was not checked locally (PyMuPDF unavailable); "
                "verify through the Published PDF reproducibility GitHub workflow."
            )
        except Exception as exc:
            blockers.append("Could not inspect report PDF: " + str(exc))

    local_progress = {}
    status = root / "local_only/reviews/fulltext_label24/AUTO_EVIDENCE_STATUS.json"
    if status.is_file():
        try:
            z = json.loads(status.read_text(encoding="utf-8"))
            for key in (
                "unique_accessible_pdf_count",
                "arxiv_v1_within_cutoff_count",
                "pdf_date_version_unverified_count",
                "candidate_case_paper_passages",
                "cases_with_candidate_passages",
            ):
                local_progress[key] = z.get(key)
            local_progress["stage"] = "machine-extracted candidates, NOT independent reviewed evidence"
        except (ValueError, OSError):
            warnings.append("Local source-candidate progress JSON was unreadable.")

    return {
        "schema": "chronohyper_constructor_handoff_audit_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_commit_sha": head,
        "branch": branch,
        "tracked_tree_clean": dirty == "" if dirty is not None else None,
        "required_files_verified": len(paths),
        "required_files_expected": len(NEEDED),
        "report_pdf_page_count_locally_checked": page_count,
        "file_evidence": paths,
        "scientific_qualifications": warnings,
        "local_machine_extracted_evidence_optional": local_progress,
        "blockers": blockers,
        "handoff_package_ready_with_disclosed_limitations": not blockers,
        "not_a_scientific_validation_or_admission_decision": True,
        "private_source_data_requires_authorized_assessor": True,
    }


def package(root: Path, audit_result: dict):
    if audit_result["blockers"]:
        raise RuntimeError("Cannot package an unclean or incomplete working tree.")
    output_dir = root / "local_only" / "constructor_handoff"
    output_dir.mkdir(parents=True, exist_ok=True)
    sha = audit_result["source_commit_sha"]
    archive = output_dir / ("ChronoHyper_Constructor_" + sha[:12] + ".zip")
    if archive.exists():
        raise FileExistsError("Preserve existing release ZIP: " + str(archive))
    _git(root, "archive", "--format=zip", f"--output={archive}", "HEAD")
    try:
        with zipfile.ZipFile(archive) as z:
            members = set(z.namelist())
            for item in NEEDED:
                if item not in members:
                    raise RuntimeError("Archived tracked file missing: " + item)
            forbidden = [
                item for item in members if item.startswith(("local_only/", ".git/"))
                or item.endswith((".env", "mapping_PRIVATE.csv", "BLIND_KEY_KEEP_SEPARATE.json"))
                or "/open_access_pdf_cache/" in item
            ]
            if forbidden:
                raise RuntimeError("Archive contains forbidden private paths: " + repr(forbidden[:8]))
            corrupt = z.testzip()
            if corrupt:
                raise RuntimeError("Corrupt archive member: " + corrupt)
            count = len(members)
    except Exception:
        archive.unlink(missing_ok=True)
        raise
    return {
        "zip_path": str(archive),
        "zip_sha256": _digest(archive),
        "git_tracked_entries": count,
        "contains_original_provider_dataset": True,
        "excluded_gitignored_private_local_only": True,
        "distribution": "AUTHORIZED_CONSTRUCTOR_REVIEWERS_ONLY",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".")
    parser.add_argument("--package", action="store_true")
    args = parser.parse_args()
    root = Path(args.project).resolve()
    result = audit(root)
    if args.package and not result["blockers"]:
        result["package"] = package(root, result)
    output_dir = root / "local_only" / "constructor_handoff"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "HANDOFF_AUDIT.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_commit_sha": result["source_commit_sha"],
        "required_files_verified": result["required_files_verified"],
        "required_files_expected": result["required_files_expected"],
        "report_pdf_page_count": result["report_pdf_page_count_locally_checked"],
        "blockers": result["blockers"],
        "scientific_qualifications": result["scientific_qualifications"],
        "local_evidence_status": result["local_machine_extracted_evidence_optional"],
        "zip_path": result.get("package", {}).get("zip_path"),
        "saved_audit": str(output),
    }, indent=2, ensure_ascii=False))
    if result["blockers"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
