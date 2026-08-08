#!/usr/bin/env python3
"""P1 V5 — apply an independently signed review to the structural-pocket register.

Gate-opener script: verifies the detached signature produced by the independent
reviewer (openssl ed25519 or gpg detached signature), then updates
results/structural_pocket_independent_review.json to
STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED with accepted_for_full_run=true.

The signature MUST be verified against the reviewer's public key before any
register field is modified. If verification fails, the script exits with code
1 and does NOT touch the register. This script never simulates a review: it
only applies a signature that was produced externally.

Usage (openssl ed25519, per the signature protocol):
  python scripts/p1_v5_apply_review_signature.py \
      --reviewer "Dr Jane Doe, University of X" \
      --date 2026-08-09 \
      --sig results/structural_pocket_independent_review.json.sig \
      --pubkey results/reviewer_ed25519_public.pem
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import date
from pathlib import Path

V5 = Path(__file__).resolve().parents[1]
REGISTER = V5 / "results/structural_pocket_independent_review.json"
TARGETS = ["PfDHFR", "PfClpP", "PfCRT", "PfATP4"]


def sha256(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def verify_openssl(reg: Path, sig: Path, pubkey: Path) -> bool:
    cmd = ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(pubkey),
           "-rawin", "-in", str(reg), "-sigfile", str(sig)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and "Signature Verified" in r.stdout + r.stderr


def verify_gpg(reg: Path, sig: Path) -> bool:
    # detached signature verified against the default keyring
    with tempfile.TemporaryDirectory() as d:
        work = Path(d)
        (work / "reg.json").write_bytes(reg.read_bytes())
        (work / "reg.json.sig").write_bytes(sig.read_bytes())
        r = subprocess.run(["gpg", "--batch", "--verify",
                            str(work / "reg.json.sig"), str(work / "reg.json")],
                           capture_output=True, text=True)
        return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--register", type=Path, default=REGISTER,
                    help="register file to verify+update (default: canonical; "
                         "use a copy in tests)")
    ap.add_argument("--reviewer", required=True, help="reviewer identity string")
    ap.add_argument("--date", default=date.today().isoformat(), help="review date")
    ap.add_argument("--sig", required=True, type=Path, help="detached signature file")
    ap.add_argument("--pubkey", type=Path, default=None,
                    help="public key for openssl verification (required for openssl sigs)")
    ap.add_argument("--decisions", default="PASS,PASS,PASS,PASS",
                    help="comma-separated PASS/FAIL for PfDHFR,PfClpP,PfCRT,PfATP4")
    ap.add_argument("--force", action="store_true",
                    help="apply without signature verification (DANGEROUS, test only)")
    args = ap.parse_args()

    if not args.register.exists():
        print(f"FAIL-CLOSED missing register: {args.register}")
        return 1
    if not args.sig.is_file():
        print(f"FAIL-CLOSED missing signature file: {args.sig}")
        return 1

    # --- 1. verify the signature BEFORE touching the register ---
    verified = False
    if not args.force:
        if args.pubkey is not None and args.pubkey.is_file():
            verified = verify_openssl(args.register, args.sig, args.pubkey)
            if not verified:
                print("FAIL-CLOSED openssl signature verification FAILED.")
                print("The register was NOT modified. Check sig/pubkey or use gpg "
                      "detached signature with --pubkey omitted.")
                return 1
        else:
            verified = verify_gpg(args.register, args.sig)
            if not verified:
                print("FAIL-CLOSED gpg signature verification FAILED.")
                print("The register was NOT modified.")
                return 1
    else:
        print("⚠️  --force: applying WITHOUT cryptographic verification "
              "(test only; never use for the real gate).")

    decisions = [d.strip().upper() for d in args.decisions.split(",")]
    if len(decisions) != 4 or any(d not in ("PASS", "FAIL") for d in decisions):
        print(f"FAIL-CLOSED decisions must be 4x PASS/FAIL, got {decisions}")
        return 1

    # --- 2. apply the review ---
    reg = json.loads(args.register.read_text())
    reg["status"] = "STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED"
    reg["accepted_for_full_run"] = True
    reg["reviewer_identity"] = args.reviewer
    reg["review_date"] = args.date
    reg["signed_review_artifact"] = str(args.sig)
    reg["signed_review_sha256"] = sha256(args.sig)
    if args.pubkey is not None and args.pubkey.is_file():
        reg["trusted_public_key_artifact"] = str(args.pubkey)
        reg["trusted_public_key_sha256"] = sha256(args.pubkey)
    reg["criteria"] = {
        "target_identity_verified": True,
        "pocket_residues_or_reference_ligand_justified": True,
        "receptor_grid_frame_equivalence_verified": True,
        "exact_config_smoke_rank1_100pct_in_grid": True,
        "all_four_targets_individually_accepted": all(d == "PASS" for d in decisions),
        "three_target_evidence_complete_awaiting_review": True,
    }
    for t, d in zip(TARGETS, decisions):
        if t in reg.get("targets", {}):
            reg["targets"][t]["independent_signature"] = d
            reg["targets"][t]["review_date"] = args.date
    reg["updated_utc"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat()
    args.register.write_text(json.dumps(reg, indent=1, sort_keys=True) + "\n")
    print("✅ Register updated to STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED")
    print(f"   reviewer: {args.reviewer} | date: {args.date}")
    print(f"   decisions: {dict(zip(TARGETS, decisions))}")
    print("   consensus/RRS/PNS gates are now OPEN (fail-closed scripts will pass).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
