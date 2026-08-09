#!/usr/bin/env python3
"""Non-overwriting rescue worker for failed V4 2F6I centroid records.

This deliberately reuses the audited original worker and changes only the
conformer seed and Vina exhaustiveness. The receptor, fixed triad-centered
box, pose gate, canonical SMILES mapping, and fail-closed behavior are
unchanged. Rescue output is written to a separate tree.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE / "p1_v4_revalidate_clpp_2f6i.py"
spec = importlib.util.spec_from_file_location("p1_v4_original_clpp_worker", ORIGINAL)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load original worker: {ORIGINAL}")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)

# Rescue-only changes; all scientific/geometric constants remain inherited.
worker.SEED = 20260809
worker.EXHAUSTIVENESS = 32
# Keep the provenance layer explicit when this module is imported by the
# rescue wrapper; the original worker's result records still preserve the
# changed seed/exhaustiveness in vina_command.
worker.RESCUE_PROTOCOL = {
    "parent_worker": str(ORIGINAL),
    "seed": worker.SEED,
    "exhaustiveness": worker.EXHAUSTIVENESS,
    "box_unchanged": True,
    "biological_gate_unchanged": True,
}

_original_fail = worker.fail


def rescue_fail(message: str, out: Path) -> None:
    """Write retry provenance even when preparation or Vina fails."""
    out.mkdir(parents=True, exist_ok=True)
    import json
    from datetime import datetime, timezone
    (out / "failure.json").write_text(json.dumps({
        "schema": "p1-v4-clpp-2f6i-rescue-worker/v1",
        "status": "FAILED_CLOSED",
        "message": message,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "rescue_protocol": worker.RESCUE_PROTOCOL,
        "consensus_written": False,
        "rrs_pns_updated": False,
    }, indent=2) + "\n")
    raise SystemExit(message)


worker.fail = rescue_fail

if __name__ == "__main__":
    raise SystemExit(worker.main())
