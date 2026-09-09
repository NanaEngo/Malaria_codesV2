#!/usr/bin/env python3
"""P1 V8 — build the R2.6 Zenodo deposit package.

Reviewer R2.6 requires a maintained, archivable data/code release. This script
stages the P1 canonical artifacts into `zenodo_package_P1/` at the repository
root, following the P5 pattern (build_zenodo_package.py):
  - DAR, revision status, release checklist, package audit
  - submission package sources (main, SM, response, cover, tables, graphics)
  - revision result directories (PfCRT re-dock, retrospective, DEKOIS two-arm)
  - revision scripts (r12/r23/r24 + figure annotation + launcher)
A sha256 checksum file is written for every staged file. The manifest
(`P1_ZENODO_DEPOSIT_MANIFEST.json`) follows the P3 pattern with
`status: prepared_pending_doi_reservation` — the DOI must be reserved on
Zenodo before upload, then the manifest updated and the deposit verified.

Usage:  python scripts/build_p1_zenodo_package.py            # build
        python scripts/build_p1_zenodo_package.py --verify   # verify checksums
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
P1 = REPO / "Project1_Chem_space_antimalarial_V7_CorrectedGrid"
SUB = P1 / "submission_ACS_P1V8"
OUT = REPO / "zenodo_package_P1"

# (source relative to P1, destination relative to OUT)
FILES = [
    ("P1_DATA_ANALYSIS_REPORT.md", "P1_DATA_ANALYSIS_REPORT.md"),
    ("P1_V8_REVISION_STATUS.md", "P1_V8_REVISION_STATUS.md"),
    ("P1_R26_RELEASE_CHECKLIST.md", "P1_R26_RELEASE_CHECKLIST.md"),
    ("P1_V8_PACKAGE_AUDIT_20260909.md", "P1_V8_PACKAGE_AUDIT_20260909.md"),
    ("submission_ACS_P1V8/P1_V8_main.tex", "manuscript/P1_V8_main.tex"),
    ("submission_ACS_P1V8/P1_V8_SM.tex", "manuscript/P1_V8_SM.tex"),
    ("submission_ACS_P1V8/Response_to_Reviewers_P1_V8.tex", "manuscript/Response_to_Reviewers_P1_V8.tex"),
    ("submission_ACS_P1V8/Cover_Letter_P1_V8.tex", "manuscript/Cover_Letter_P1_V8.tex"),
    ("submission_ACS_P1V8/Sao_Chim_Space.bib", "manuscript/Sao_Chim_Space.bib"),
    ("submission_ACS_P1V8/SUBMISSION_MANIFEST_V8.md", "manuscript/SUBMISSION_MANIFEST_V8.md"),
]

DIRS = [
    ("submission_ACS_P1V8/tables", "manuscript/tables"),
    ("submission_ACS_P1V8/Graphics", "manuscript/Graphics"),
    ("results/pfcrt_redock_v2grid_20260909", "results/pfcrt_redock_v2grid_20260909"),
    ("results/retrospective_approved_antimalarials_20260909", "results/retrospective_approved_antimalarials_20260909"),
    ("results/dekois_mtxstripped_20260909", "results/dekois_mtxstripped_20260909"),
]

SCRIPTS = [
    "scripts/p1_r12_retrospective.py",
    "scripts/p1_r23_pfcrt_redock.py",
    "scripts/p1_r23_rrs_recompute.py",
    "scripts/p1_r24_dekois_mtxstripped.py",
    "scripts/p1_r24_analyze.py",
    "scripts/launch_r24.sh",
    "scripts/v8_figure2_annotations.py",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    copied: list[str] = []

    for src_rel, dst_rel in FILES:
        src, dst = P1 / src_rel, OUT / dst_rel
        if not src.exists():
            sys.exit(f"ERROR: missing {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(dst_rel)

    for src_rel, dst_rel in DIRS:
        src, dst = P1 / src_rel, OUT / dst_rel
        if not src.exists():
            sys.exit(f"ERROR: missing {src}")
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("work_retained", "work_stripped", "*.pyc"))
        n = sum(1 for p in dst.rglob("*") if p.is_file())
        copied.append(f"{dst_rel}/ ({n} files)")

    for rel in SCRIPTS:
        src, dst = P1 / rel, OUT / rel
        if not src.exists():
            sys.exit(f"ERROR: missing {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)

    write_checksums()
    write_manifest(copied)
    total = sum(1 for p in OUT.rglob("*") if p.is_file())
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"Staged {total} files ({size / 1e6:.1f} MB) in {OUT}")
    print(f"Checksums: {OUT}/sha256sums.txt")


def write_checksums() -> None:
    lines = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.name != "sha256sums.txt":
            lines.append(f"{sha256(p)}  {p.relative_to(OUT)}")
    (OUT / "sha256sums.txt").write_text("\n".join(lines) + "\n")


def write_manifest(copied: list[str]) -> None:
    manifest = {
        "project": "P1 — Chemical-space antimalarial polypharmacology (JCIM V8 revision)",
        "built_on": str(date.today()),
        "status": "prepared_pending_doi_reservation",
        "reviewer_item": "R2.6 — repository release + archival DOI",
        "license": "MIT (repository root LICENSE)",
        "contents": sorted(set(copied)),
        "checksums": "sha256sums.txt",
        "related_repositories": [
            "NanaEngo/Malaria_codesV2 (code; to be made public with release tag)",
            "Companion P2/P3/P5/P6 Zenodo deposits follow the same pattern",
        ],
        "upload_steps": [
            "Reserve the DOI on Zenodo (reserved_pending_upload until verified)",
            "Upload this directory as a single versioned deposit",
            "Verify sha256 checksums post-upload and resolve the DOI",
            "Update Data Availability (main) + SM reproducibility section + response R2.6 with the DOI",
            "Make the GitHub repository public and tag the release",
        ],
    }
    (OUT / "P1_ZENODO_DEPOSIT_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n")


def verify() -> None:
    bad = 0
    for line in (OUT / "sha256sums.txt").read_text().splitlines():
        expected, rel = line.split("  ", 1)
        actual = sha256(OUT / rel)
        if actual != expected:
            print(f"MISMATCH: {rel}")
            bad += 1
    print("VERIFY OK" if bad == 0 else f"{bad} mismatches")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.verify:
        verify()
    else:
        build()
