# P1 — R2.6 Repository Release + Zenodo DOI (author-action checklist)

> **Companion-note update 2026-09-09:** the R2.4 two-arm DEKOIS re-run is now COMPLETE
> (honest-negative; retained AUC 0.502 [0.423, 0.586] vs stripped 0.563 [0.477, 0.646];
> `results/dekois_mtxstripped_20260909/`). Include `scripts/p1_r24_dekois_mtxstripped.py`,
> `scripts/p1_r24_analyze.py`, and that results directory in the Zenodo deposit inventory
> below, and cite the R2.6 Data-Availability update in the same resubmission package.

**Reviewer R2.6:** "The repository URL returns 404; the wild-type denominators do not appear
elsewhere; provide a maintained repository with license, release tag, and archival DOI."

**Status:** PREPARED (2026-09-09) — all steps below are author-admin actions on GitHub /
Zenodo; nothing here can be executed from the local workspace.

**Inventory validation (2026-09-09):** every Step-2 component was verified to exist on
disk before author action — DAR/status/checklist 3/3, manuscript 7/7 (tex + bib + PDFs),
tables 11/11 `.tex` (incl. the two new revision tables `sm_table_retrospective_antimalarials.tex`
and `sm_table_wt_mutant_scores.tex`), Graphics 5/5 `.pdf`, scripts 6/6, results 3/3 (`pfcrt_redock`
219 files, `retrospective` 98 files, `dekois_mtxstripped` incl. live R2.4 job
output). Test artifact `acs-smtest.bib` removed. `git diff --check` clean; remote confirmed
(`git@github.com:NanaEngo/Malaria_codesV2.git`); no LICENSE or release tag yet (author action).
→ **Step 2 inventory is ready to stage;**
author may trim results binaries before upload (provenance files must stay).

**Pattern followed:** P3 (`P3_ZENODO_DEPOSIT_MANIFEST.json`, DOI `10.5281/zenodo.19608875`
reserved, `reserved_pending_upload`) and P5 (`build_zenodo_package.py` +
`p5_zenodo_finalize.sh` + `zenodo_package_20260827/` staged 31/31 files,
`READY_FOR_UPLOAD_NOT_UPLOADED`).

---

## Step 1 — Repository (GitHub)

| # | Action | Command / detail | Done |
|---|--------|------------------|:----:|
| 1.1 | Confirm the remote | `git remote -v` → `git@github.com:NanaEngo/Malaria_codesV2.git` | ⬜ |
| 1.2 | Commit all canonical V8 changes on `data-results` | `git status --short` must show only intended files; `git diff --check` clean | ✅ 2026-09-09 (R2.4 integration commit; package rebuilt from clean tree) |
| 1.3 | Merge/align `data-results` with `master` and push | `git push origin data-results` (author approval required; provenance rule 10) | ✅ 2026-09-09 `data-results` pushed (incl. remote merge of the author's parallel commits); `master` alignment remains an author decision |
| 1.4 | **Make the repository public** | GitHub → Settings → Danger Zone → Change visibility → Public | ✅ 2026-09-09 `gh repo edit --visibility public` (URL verified, HTTP 200) |
| 1.5 | **Add a software license** | e.g. MIT or CC-BY-4.0 (recommended for code+data mix); add `LICENSE` at repo root; state it in the README | ✅ MIT `LICENSE` already present at repo root |
| 1.6 | **Versioned release tag** | `git tag -a v1.0.0 -m "P1 V8 JCIM submission (RRS/polypharmacology)" && git push origin v1.0.0` | ✅ 2026-09-09 tag `v1.0.0` pushed + GitHub release created (`releases/tag/v1.0.0`) |
| 1.7 | Add a top-level `README.md` with: paper title, DOI (after Step 3), data/script layout, license, conda env `malaria_md` | ✅ 2026-09-09 README updated (P1 V8 status, MIT license, `malaria_md` env); DOI line to add after Step 3 |

## Step 2 — Zenodo deposit package (P1 inventory)

Stage the canonical P1 V8 artifacts into a self-contained package
(`submission_ACS_P1V8/zenodo_package_P1V8/` mirroring P5's layout). Proposed inventory
(author may trim results binaries before upload; provenance files must stay):

| Component | Files |
|---|---|
| DAR (source of truth) | `P1_DATA_ANALYSIS_REPORT.md`, `P1_V8_REVISION_STATUS.md`, `P1_R26_RELEASE_CHECKLIST.md` |
| Manuscript package | `submission_ACS_P1V8/` → `P1_V8_main.tex/_SM.tex`, `Cover_Letter_P1_V8.tex`, `Response_to_Reviewers_P1_V8.tex`, `.bib`, `tables/*.tex`, `Graphics/*.pdf`, compiled PDFs |
| Scripts (reproducibility) | `scripts/p1_r23_pfcrt_redock.py`, `p1_r23_rrs_recompute.py`, `p1_r12_retrospective.py`, `p1_r24_dekois_mtxstripped.py`, `v8_figure2_annotations.py`, `launch_r24.sh` |
| Results (canonical, 2026-09-09) | `results/pfcrt_redock_v2grid_20260909/` (scores, RRS/N_fav, receptors, run logs), `results/retrospective_approved_antimalarials_20260909/` (scores, RRS profiles), `results/dekois_mtxstripped_20260909/` (scores, metrics, summary) |
| Inputs (P2-sourced, referenced not duplicated) | pointer file listing P2 DEKOIS/grid/receptor paths instead of copying large binaries |
| License | copy of the Step 1.5 `LICENSE` |
| Deposit manifest | `P1_ZENODO_DEPOSIT_MANIFEST.json` (template below) |

`P1_ZENODO_DEPOSIT_MANIFEST.json` template:

```json
{
  "canonical_workspace": "Project1_Chem_space_antimalarial_V7_CorrectedGrid",
  "deposit_doi": "10.5281/zenodo.<XXXXX>",   // author reserves via Zenodo "New upload"
  "status": "prepared_pending_doi_reservation",
  "release_tag": "v1.0.0",
  "license": "CC-BY-4.0 (data) / MIT (code) [confirm]",
  "inventory": [
    "P1_DATA_ANALYSIS_REPORT.md",
    "submission_ACS_P1V8/P1_V8_main.tex", "...",
    "scripts/p1_r23_pfcrt_redock.py", "...",
    "results/pfcrt_redock_v2grid_20260909/", "..."
  ],
  "note": "Manifest staged locally; DOI reservation and upload require the author's Zenodo account."
}
```

## Step 3 — Zenodo upload

| # | Action | Detail | Done |
|---|--------|--------|:----:|
| 3.1 | Reserve DOI | Zenodo → New upload → **Reserve DOI** (pattern: P3 `10.5281/zenodo.19608875`) | ⬜ |
| 3.2 | Fill metadata | Title = manuscript title; creators = 5 authors with ORCIDs (AGENTS.md); version = `v1.0.0`; license = Step 1.5 | ⬜ |
| 3.3 | Upload the staged package + tarball | Follow P5 (`zenodo_package_20260827/` + tarball, 31/31 verified) | ✅ 2026-09-09 staged locally: `zenodo_package_P1/` (384 files, 14.4 MB, sha256 verified, manifest `prepared_pending_doi_reservation`); upload is the author's Zenodo account action |
| 3.4 | Verify DOI + files | DOI resolves; per-file sha256 manifest matches; mark status `published` in `P1_ZENODO_DEPOSIT_MANIFEST.json` | ⬜ |

## Step 4 — Manuscript update (after DOI exists)

| # | Action | Detail | Done |
|---|--------|--------|:----:|
| 4.1 | Data Availability statement (main) | add GitHub URL + DOI: `https://github.com/NanaEngo/Malaria_codesV2` · DOI `10.5281/zenodo.<XXXXX>` | ✅ 2026-09-09 URL + MIT + `v1.0.0` inserted; DOI sentence pending Zenodo assignment |
| 4.2 | SM §S11 (Reproducibility) | same URL + DOI (`\url{...}`) | ✅ 2026-09-09 same as 4.1 |
| 4.3 | Response letter R2.6 | replace `[TO COMPLETE]` with the public URL, license, release tag, and DOI | ✅ 2026-09-09 rewritten (public URL, MIT, `v1.0.0`, staged package); DOI to append after assignment |
| 4.4 | Recompile main + SM + response; sync PDFs; `git diff --check` | 0 errors / 0 undefined | ⬜ |

## Gates before submission

- [ ] `curl -sI https://github.com/NanaEngo/Malaria_codesV2` returns 200 (public)
- [ ] LICENSE present at repo root and inside the Zenodo package
- [ ] Release tag `v1.0.0` exists on GitHub and is referenced in the deposit
- [ ] DOI resolves (`https://doi.org/10.5281/zenodo.<XXXXX>`)
- [ ] WT/mutant denominator table is inside the SI (already satisfied: corrected PfCRT RRS values in main Table 1; full panel in SM S3/S12.7 + repository)
- [ ] `git diff --check` clean; provenance manifests included