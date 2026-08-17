#!/usr/bin/env python3
"""Archive an authoritative PfCRT UniProt record for local provenance.

Network is used only when this script is explicitly run. The output contains
raw FASTA/flat-file copies and a JSON manifest; no structures or MD are changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Malaria_codesV2-local-provenance/1.0"})
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accession", default="W7FI62")
    parser.add_argument("--strain", default="7G8")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    base = f"https://rest.uniprot.org/uniprotkb/{args.accession}"
    fasta = fetch(base + ".fasta")
    flat = fetch(base + ".txt")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fasta_path = args.output_dir / f"{args.accession}.fasta"
    flat_path = args.output_dir / f"{args.accession}.txt"
    fasta_path.write_bytes(fasta); flat_path.write_bytes(flat)
    first = fasta.decode("utf-8").splitlines()[0]
    sequence = "".join(line.strip() for line in fasta.decode("utf-8").splitlines()[1:] if line.strip())
    if len(sequence) != 424:
        raise RuntimeError(f"Unexpected {args.accession} sequence length: {len(sequence)}")
    if sequence[75] != "T":
        raise RuntimeError(f"Expected 7G8 K76T sequence residue, got {sequence[75]!r}")
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FETCHED_AUTHORITATIVE_SEQUENCE",
        "accession": args.accession,
        "strain": args.strain,
        "source": base,
        "fasta": {"path": str(fasta_path), "sha256": sha256(fasta), "length": len(sequence), "residue_76": sequence[75], "header": first},
        "flatfile": {"path": str(flat_path), "sha256": sha256(flat)},
        "interpretation": "7G8 PfCRT sequence; K76T is the strain state, not a 3D7 WT sequence",
    }
    manifest_path = args.output_dir / f"{args.accession}_provenance.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
