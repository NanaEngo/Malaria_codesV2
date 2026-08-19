#!/usr/bin/env bash
# =============================================================================
# sync_data_results.sh
#
# Keep the `data-results` branch in sync with `master` by rebuilding it as the
# *union* of the two trees:
#
#   data-results' new tree = master tree  +  (files present only on data-results)
#
# Rationale
# ---------
# - `data-results` is the "full repo with all data" branch. Master already
#   tracks the heavy data files (13k+ .pdbqt, CSVs, PDFs), so the two branches
#   differ only by a small set of extra snapshot/legacy files that live solely
#   on `data-results` (V2/V3 archive copies, working notes, etc.).
# - A plain `git merge master` would work today but can hit content conflicts
#   whenever a file edited on `data-results` is also changed on `master`
#   (e.g. the P4 manuscript conflict resolved on 2026-08-19). Rebuilding the
#   union tree is conflict-free and idempotent:
#     * every file on master appears verbatim (full repo guarantee), and
#     * every file unique to data-results is carried forward.
#   For any path present on BOTH branches, master's version wins (master is
#   the source of truth for code and manuscripts).
# - The tree is assembled with plumbing commands (read-tree / update-index /
#   write-tree) so no worktree checkout of the 40k-file repo is needed.
#
# Safety
# ------
# - Never force-pushes. If the remote `data-results` advanced since we
#   fetched (someone pushed directly), the non-fast-forward push fails and
#   the job errors loudly instead of overwriting.
# - No-op commits are skipped (tree unchanged -> exit 0, nothing pushed).
#
# Usage: sync_data_results.sh [--dry-run]
# =============================================================================
set -euo pipefail

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then DRY_RUN=1; fi

log()  { echo "[sync] $*"; }
die()  { echo "[sync] ERROR: $*" >&2; exit 1; }

# --- locate repo --------------------------------------------------------------
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# --- fetch latest refs --------------------------------------------------------
git fetch origin master data-results --prune || die "git fetch failed"

MASTER_REF="origin/master"
DR_REF="origin/data-results"
MASTER_SHA="$(git rev-parse "$MASTER_REF")"
DR_SHA="$(git rev-parse "$DR_REF")"
log "master:        $MASTER_SHA"
log "data-results:  $DR_SHA"

# --- build union tree ----------------------------------------------------------
# master file list
git ls-tree -r --name-only "$MASTER_REF" | sort > /tmp/sync_m_files.txt
# data-results full entries: "<mode> <type> <sha>\t<path>"
git ls-tree -r "$DR_REF" | sort > /tmp/sync_dr_entries.txt
# data-results-only paths
git ls-tree -r --name-only "$DR_REF" | sort | \
    comm -23 - /tmp/sync_m_files.txt > /tmp/sync_dr_only.txt

ONLY_COUNT="$(wc -l < /tmp/sync_dr_only.txt)"
log "master files:      $(wc -l < /tmp/sync_m_files.txt)"
log "data-only extras:  ${ONLY_COUNT}"

# start from master's tree
export GIT_INDEX_FILE=/tmp/sync_index_$$.index
rm -f "$GIT_INDEX_FILE"
git read-tree "$MASTER_REF"

# re-add data-results-only entries (join on path)
if [[ "$ONLY_COUNT" -gt 0 ]]; then
    # build a lookup: path -> full entry
    awk -F'\t' '{print $2 "\t" $1}' /tmp/sync_dr_entries.txt | sort > /tmp/sync_dr_entries_by_path.txt
    join -t$'\t' -j 1 \
        <(sort /tmp/sync_dr_only.txt) \
        /tmp/sync_dr_entries_by_path.txt \
    | while IFS=$'\t' read -r path meta; do
        mode="$(echo "$meta" | awk '{print $1}')"
        sha="$(echo "$meta" | awk '{print $3}')"
        git update-index --add --cacheinfo "$mode,$sha,$path"
    done
fi

UNION_TREE="$(git write-tree)"
log "union tree:        $UNION_TREE"

# --- skip no-op -----------------------------------------------------------------
if [[ "$UNION_TREE" == "$(git rev-parse "$DR_REF^{tree}")" ]]; then
    log "data-results already contains the full master tree + all extras. Nothing to do."
    exit 0
fi

# --- create commit ----------------------------------------------------------------
DR_LOG="$(git log -1 --format='%s' "$DR_REF")"
MSG="sync: merge master ($MASTER_SHA) into data-results

Automated sync of data-results with master.
- master tree:   $MASTER_SHA
- data extras:   ${ONLY_COUNT} files preserved from data-results
- union tree:    $UNION_TREE
"
UNION_COMMIT="$(printf '%s' "$MSG" | git commit-tree "$UNION_TREE" -p "$DR_SHA" -p "$MASTER_SHA")"
log "sync commit:       $UNION_COMMIT"

if [[ "$DRY_RUN" -eq 1 ]]; then
    log "DRY-RUN: would push $UNION_COMMIT -> origin/data-results"
    exit 0
fi

# --- push (fast-forward only) ------------------------------------------------------
log "pushing $UNION_COMMIT -> origin/data-results"

# In CI, authenticate with the provided token (PAT or GITHUB_TOKEN). Locally
# (no token env), the existing SSH/credential setup is used as-is.
if [[ -n "${GIT_PUSH_TOKEN:-}" ]]; then
    REMOTE_URL="$(git config --get remote.origin.url)"
    # github.com:NanaEngo/Malaria_codesV2.git -> https://TOKEN@github.com/NanaEngo/Malaria_codesV2.git
    PUSH_URL="$(printf '%s' "$REMOTE_URL" | sed -E 's#^git@github.com:([^/]+)/(.+)\.git$#https://x-access-token:'"$GIT_PUSH_TOKEN"'@github.com/\1/\2.git#; s#^https://github.com/([^/]+)/(.+)\.git$#https://x-access-token:'"$GIT_PUSH_TOKEN"'@github.com/\1/\2.git#')"
    git push "$PUSH_URL" "$UNION_COMMIT:refs/heads/data-results"
else
    git push origin "$UNION_COMMIT:refs/heads/data-results"
fi
log "done."
