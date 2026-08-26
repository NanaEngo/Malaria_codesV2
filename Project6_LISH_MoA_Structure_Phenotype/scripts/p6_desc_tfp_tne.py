#!/usr/bin/env python
"""Compute TFP (78-D) and TNE (192-D) descriptors for the P6 mapped cohort.

Reuses the frozen P3 pipelines verbatim:
* TFP: ``p3_tda_pipeline.process_molecule`` (n_conf=1, Vietoris-Rips persistence)
* TNE: ``p3_tne_pipeline.smiles_to_tensor`` + ``tucker_compress``

Descriptors are computed once per UNIQUE canonical SMILES in the validated
mapping and saved keyed by SMILES; row-level alignment happens downstream.

Outputs (under results/p6_phase2/):
* ``p6_tfp_tne_descriptors.npz``
* ``p6_tfp_tne_descriptors_report.json``
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJ = Path(__file__).resolve().parents[1]
MAPPING = PROJ / "data" / "mappings" / "drugid_to_smiles_v2_validated.csv"
OUT_DIR = PROJ / "results" / "p6_phase2"
P3_SCRIPTS = PROJ.parent / "Project3_Quantum_Inspired_RepresentationsV2607" / "scripts"
TFP_DIM, TNE_DIM = 78, 192


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    from joblib import Parallel, delayed
    sys.path.insert(0, str(P3_SCRIPTS))
    from p3_tda_pipeline import process_molecule
    from p3_tne_pipeline import smiles_to_tensor, tucker_compress

    mp = pd.read_csv(MAPPING)[["smiles_rdkit"]].drop_duplicates().reset_index(drop=True)
    smiles = mp["smiles_rdkit"].astype(str).tolist()

    def one_tfp(s):
        try:
            x = process_molecule(s, n_conf=1)
            return None if x is None else x.astype(np.float32)
        except Exception:
            return None

    def one_tne(s):
        t = smiles_to_tensor(s)
        if t is None:
            return None
        try:
            return tucker_compress(t, 8, use_gpu=False).astype(np.float32)
        except Exception:
            return None

    tfp_vals = Parallel(n_jobs=12)(delayed(one_tfp)(s) for s in smiles)
    tne_vals = Parallel(n_jobs=12, backend="threading")(delayed(one_tne)(s) for s in smiles)

    tfp_fail = [i for i, x in enumerate(tfp_vals) if x is None or not np.all(np.isfinite(x))]
    tne_fail = [i for i, x in enumerate(tne_vals) if x is None or not np.all(np.isfinite(x))]
    tfp = np.vstack([np.zeros(TFP_DIM, np.float32) if i in set(tfp_fail) else tfp_vals[i] for i in range(len(smiles))])
    tne = np.vstack([np.zeros(TNE_DIM, np.float32) if i in set(tne_fail) else tne_vals[i] for i in range(len(smiles))])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    npz = OUT_DIR / "p6_tfp_tne_descriptors.npz"
    np.savez_compressed(npz, smiles=np.array(smiles, dtype=object), tfp=tfp, tne=tne,
                        tfp_fail_idx=np.asarray(tfp_fail), tne_fail_idx=np.asarray(tne_fail))
    report = {
        "mapping": str(MAPPING),
        "mapping_sha256": sha256(MAPPING),
        "n_unique_molecules": len(smiles),
        "n_tfp_failures_zero_vector_itt": len(tfp_fail),
        "n_tne_failures_zero_vector_itt": len(tne_fail),
        "failure_indices": {"TFP": tfp_fail, "TNE": tne_fail},
        "tfp_source": "p3_tda_pipeline.process_molecule(n_conf=1)",
        "tne_source": "p3_tne_pipeline.smiles_to_tensor + tucker_compress(bond_dim=8, cpu)",
        "artifact_sha256": sha256(npz),
        "status": "COMPUTED",
    }
    (OUT_DIR / "p6_tfp_tne_descriptors_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
