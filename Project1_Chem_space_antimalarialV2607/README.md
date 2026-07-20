# DEPRECATED 2026-07-17

This directory has been **archived** to:
    /home/nanaengo/Malaria_codesV2/.archive_P1_V2607_20260717/

The active V2 corrected-grid pipeline lives at:
    /home/nanaengo/Project1_Chem_space_antimalarial_V2_CorrectedGrid/   (canonical, top-level)

---

## Recovery commands

```bash
# Walk git history across the move (shows original commit + rename)
git log --follow -- .archive_P1_V2607_20260717/

# Inspect archived contents (top level)
ls -la .archive_P1_V2607_20260717/

# Search for any specific file inside the archive
find .archive_P1_V2607_20260717/ -name '*.py' -o -name '*.sh'

# If you accidentally wrote to this stub, the archive is the source of truth
# and this stub is disposable.
```

## Do NOT

- Create new files in this stub. They will NOT be tracked by V2.
- Re-run scripts that previously pointed at this path. Update them to the
  canonical path first.
- Revert the DIR-DEDUP-1 commit without also reverting AGENTS.md wording
  (DIR-DEDUP-DOC-PAST).
