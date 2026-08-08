#!/usr/bin/env python3
"""P4 — Scoring oracles for MCTS molecular optimization.

Provides pharmacological scores (MPO, docking, SYBA, SA) and two advanced
oracles that bring P2 polypharmacology awareness into P4:

**RRS-informed proxy:** Measures Morgan/Tanimoto similarity to P2 reference
chemotypes selected as resistance-resilience exemplars. The current P4
implementation does not propagate P2 per-target WT/mutant ratios; it is a
chemotype-similarity proxy, not a validated mutant-binding prediction.

**PNS-informed proxy:** A normalized multi-target docking score derived from
the Tartarus columns `score_1syh`, `score_6y2f` and `score_4lde`. It is a
polypharmacology-aware proxy for broad docking engagement in that three-target
Tartarus panel, not a direct four-target PfDHFR/PfCRT/PfATP4/PfClpP score.

References
----------
- RRS/ACSI/PNS framework: Project 2 (Temgoua et al., in preparation)
- STRING network: Szklarczyk et al. (2023) Nucleic Acids Res.
"""

from __future__ import annotations

import math
import warnings
from collections import OrderedDict
from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from rdkit.DataStructs import TanimotoSimilarity


# ── Optional third-party scorers ─────────────────────────────────────
try:
    from syba.syba import SybaClassifier

    _HAS_SYBA = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_SYBA = False

try:
    import sascorer

    _HAS_SASCORER = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_SASCORER = False


# ── Paths to P1/P2 score libraries ───────────────────────────────────
def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


# ── datamol for molecular operations (scientific-agent-skills skill) ──
try:
    import datamol as dm
    _HAS_DATAMOL = True
except ImportError:
    _HAS_DATAMOL = False


# ── medchem for drug-likeness filtering (scientific-agent-skills: medchem) ──
try:
    import medchem as mc
    _HAS_MEDCHEM = True
except ImportError:
    _HAS_MEDCHEM = False


# ── CuPy for GPU-accelerated batch Tanimoto (scientific-agent-skills: optimize-for-gpu) ──
# M3 fix (2026-08-03): `_HAS_CUPY` only records that the module imports; it does
# NOT guarantee a GPU device exists on the current node. Allocating CuPy arrays on
# a GPU-less node raises, and the broad try/except in `_load_precomputed_libraries`
# then silently empties the Tartarus library, making rewards node-dependent.
# We therefore probe for an actual device at runtime and fall back to numpy.
try:
    import cupy as cp
    _HAS_CUPY = True
except ImportError:
    cp = None
    _HAS_CUPY = False


def _cupy_available() -> bool:
    """True only if CuPy imports AND a usable CUDA device is present."""
    if not _HAS_CUPY:
        return False
    try:
        return cp.cuda.runtime.getDeviceCount() > 0
    except Exception:
        return False


# Resolve the array backend once at import time (probe the device now).
_USE_GPU = _cupy_available()
if _HAS_CUPY and not _USE_GPU:
    print("[p4_mcts_oracles] CuPy present but no CUDA device found — using numpy backend "
          "(results are identical, only the backend differs).", flush=True)


C6_CSV = (
    _repo_root()
    / "Project2_Polypharmacology_MD_ValidationV2607"
    / "data"
    / "from_project1"
    / "results"
    / "c6_primary_leads_synthesisable.csv"
)

TARTARUS_CSV = (
    _repo_root()
    / "Project2_Polypharmacology_MD_ValidationV2607"
    / "results"
    / "tartarus_output.csv"
)

# Public ChEMBL malaria IC50/EC50 actives (independent dataset, shared with the
# P5 GNN external validation and the P3 descriptor external validation). The
# activity oracle rewards Tanimoto proximity to these experimentally active
# antimalarials.
ACTIVITY_CSV = (
    _repo_root()
    / "Project5_GNN_Transformer_DrugDiscovery"
    / "results"
    / "p5_public_chembl_malaria.csv"
)


class OracleAggregator:
    """Aggregate multiple oracle scores into a scalar reward.

    Parameters
    ----------
    weights : dict[str, float]
        Weight for each oracle component. Keys: mpo, docking, syba, sa.
    use_precomputed : bool
        If True, load P1/P2 score libraries and use them for lookups.
    docking_fallback : str
        How to score novel molecules when no precomputed docking value exists.
        Options: "similarity" (Tanimoto nearest-neighbour proxy), "default".
    """

    # ── RRS reference molecules (resistance-resilient chemotypes) ─────
    # Known hit molecules from P2 that maintain binding against resistance
    # mutations. Used as Tanimoto similarity targets for the RRS oracle.
    # SMILES are canonical representations of validated multi-target hits.
    _RRS_REFERENCE_SMILES: list[str] = [
        "Cc1ccc(C(=O)Nc2ccc(C(C)(C)C)cc2)cc1",       # Hit class A (pan-resilient)
        "COc1ccc(C(=O)Nc2ccccc2C(=O)O)cc1",           # Hit class B (multi-target)
        "O=C(Nc1ccc(F)cc1)C1CCN(c2ncccn2)CC1",        # PfDHFR/PfCRT dual
        "Cc1cc(C)n(-c2ccc(S(=O)(=O)N3CCCCC3)cc2)n1",  # PfATP4 binder
        "O=C1CCc2ccccc2N1c1ccc(Cl)cc1",                # PfClpP active
        "Cc1ccc(S(=O)(=O)N2CCN(c3ccc(Cl)cc3)CC2)cc1", # Broad-spectrum
        "COc1cc2c(cc1OC)CC(C(=O)O)CC2",                # Natural product-inspired
        "O=c1[nH]c2ccccc2n1-c1ccccc1",                 # Privileged scaffold
        "Cc1nc(-c2ccccc2)nc(N2CCOCC2)n1",              # Kinase-inspired
        "O=C(Nc1ccccc1)c1cccs1",                        # Simple amide hit
    ]

    # ── P2 data paths for RRS reference loading ───────────────────────
    _RRS_DATA_CSV = (
        Path(__file__).resolve().parents[2]
        / "Project2_Polypharmacology_MD_ValidationV2607"
        / "Tuto_MD_MC"
        / "md_top20_candidates.csv"
    )

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        use_precomputed: bool = True,
        docking_fallback: str = "similarity",
        use_rrs: bool = True,
        use_pns: bool = True,
        use_activity: bool = True,
        cache_maxsize: int = 10000,
        rrs_fallback_k: int = 3,
    ) -> None:
        # v12 (2026-08-08): public-activity oracle added as a reward term
        # (max Morgan-2 Tanimoto to ChEMBL actives). Weights rebalanced to keep
        # sum = 1.0 (previous components scaled by 0.90, activity = 0.10).
        self.weights = weights or {
            "mpo": 0.27,
            "docking": 0.225,
            "syba": 0.135,
            "sa": 0.045,
            "rrs": 0.135,
            "pns": 0.09,
            "activity": 0.10,
        }
        self.docking_fallback = docking_fallback
        self.use_rrs = use_rrs
        self.use_pns = use_pns
        self.use_activity = use_activity
        # LRU cache with bounded size (prevents OOM)
        self._runtime_cache: Dict[str, Dict[str, float]] = OrderedDict()
        self._cache_maxsize = cache_maxsize
        self._canonical_cache: Dict[str, str] = {}
        self._rrs_fallback_k = rrs_fallback_k

        # Precomputed P1/P2 libraries
        self._c6: Dict[str, Dict[str, float]] = {}
        self._tartarus: Dict[str, Dict[str, float]] = {}
        self._tartarus_smiles: list[str] = []
        self._tartarus_fingerprints: list = []
        self._tartarus_target_cols: list[str] = []  # detected dynamically
        # Dense fingerprint matrix + bit-count norms precomputed once at load
        # (value-preserving speedup: same float32 Tanimoto as _batch_tanimoto_gpu,
        #  but built once instead of rebuilt on every oracle call).
        self._tartarus_dense = None
        self._tartarus_norms = None

        # RRS reference fingerprints (only if RRS enabled)
        self._rrs_ref_fps: list = []
        if self.use_rrs:
            self._load_rrs_references()

        # Public-activity library (dense fingerprint matrix, built once)
        self._activity_dense = None
        self._activity_norms = None
        self._activity_n = 0
        if self.use_activity:
            self._load_activity_library()

        if use_precomputed:
            self._load_precomputed_libraries()

        # Optional on-the-fly scorers
        self._syba: Optional[object] = None
        if _HAS_SYBA:
            try:
                self._syba = SybaClassifier()
                self._syba.fitDefaultScore()
            except Exception as exc:  # pragma: no cover
                warnings.warn(f"SYBA initialisation failed: {exc}")
                self._syba = None

    # ── RRS reference preparation ────────────────────────────────────
    def _load_rrs_references(self) -> None:
        """Load RRS reference molecules, preferring P2 data CSV with
        fallback to the hardcoded reference list."""
        ref_smiles: list[str] = []

        # Try loading from P2 top-20 candidates CSV
        if self._RRS_DATA_CSV.exists():
            try:
                df = pd.read_csv(self._RRS_DATA_CSV)
                smi_col = next((c for c in df.columns
                               if c.lower() in ("smiles", "smile", "input", "canonical_smiles")),
                               df.columns[0])
                ref_smiles = df[smi_col].dropna().unique().tolist()[:20]
            except Exception:
                ref_smiles = []

        # Fallback to hardcoded reference list
        if not ref_smiles:
            ref_smiles = list(self._RRS_REFERENCE_SMILES)

        # Compute fingerprints
        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        valid_count = 0
        for smi in ref_smiles:
            mol = Chem.MolFromSmiles(smi)
            if mol:
                self._rrs_ref_fps.append(gen.GetFingerprint(mol))
                valid_count += 1

        if valid_count == 0:
            warnings.warn("No valid RRS reference molecules loaded — RRS oracle will return 0.0")

    # ── Public API ───────────────────────────────────────────────────
    def score(self, smiles: str) -> Dict[str, float]:
        """Return a dictionary of individual oracle scores.

        Includes core scores (mpo, docking, syba, sa) and, if enabled,
        resistance awareness (rrs), polypharmacology (pns), and
        drug-likeness filters (drug_like, lipinski, veber, pains).

        Drug-likeness filters use the medchem library when available
        (scientific-agent-skills: medchem), falling back to RDKit-only
        Lipinski/PAINS checks.
        """
        result = {
            "mpo": self._mpo_score(smiles),
            "docking": self._docking_score(smiles),
            "syba": self._syba_score(smiles),
            "sa": self._sa_score(smiles),
        }
        if self.use_rrs:
            result["rrs"] = self._rrs_score(smiles)
        if self.use_pns:
            result["pns"] = self._pns_score(smiles)
        if self.use_activity:
            result["activity"] = self._activity_score(smiles)
        # Drug-likeness filter (medchem or RDKit fallback)
        drug_info = self._medchem_filter(smiles)
        result["drug_like"] = 1.0 if drug_info["drug_like"] else 0.0
        result["lipinski"] = 1.0 if drug_info["lipinski"] else 0.0
        result["veber"] = 1.0 if drug_info["veber"] else 0.0
        result["pains"] = 1.0 if drug_info["pains"] else 0.0
        return result

    @staticmethod
    def _normalize_docking(dock_score: float) -> float:
        """Normalise un score de docking (kcal/mol) en [0, 1].

        Plage physique : [-12, -5] kcal/mol.
        -12 kcal/mol (très fort) → 1.0
        -5 kcal/mol (faible) → 0.0
        Les valeurs hors plage sont clampées.
        """
        raw = OracleAggregator._clamp_docking(dock_score, default=-7.0)
        # raw est négatif dans [-15, -0.1] après clamp
        # Plage physique : [-12, -5] kcal/mol
        # -12 kcal/mol (très fort) → 1.0
        # -5 kcal/mol (faible) → 0.0
        # Formule : (-raw - 5) / 7  (car -raw est positif)
        norm = max(0.0, min(1.0, (-raw - 5.0) / 7.0))
        return norm  # 0.0 = faible, 1.0 = fort

    @staticmethod
    def _normalize_syba(syba_score: float) -> float:
        """Normalise un score SYBA en [0, 1].

        SYBA peut aller de négatif (difficile) à très positif (facile).
        On utilise une fonction sigmoïde centrée à 0 :
        syba=0 → 0.5 (neutre), syba=+10 → ~0.88, syba=-10 → ~0.12
        """
        # Sigmoid centrée : 1 / (1 + exp(-x)), x = syba / 5.0
        x = syba_score / 5.0
        return 1.0 / (1.0 + math.exp(-x))

    def reward(self, smiles: str) -> float:
        """Compute weighted scalar reward with all components normalised to [0, 1].

        **Normalisation** : chaque composante est ramenée à [0, 1] avant
        pondération pour éviter qu'une composante domine les autres.
        - MPO : déjà en [0, 1]
        - Docking : [-12, -5] kcal/mol → [0, 1]
        - SYBA : sigmoïde centrée → [0, 1]
        - SA : inversion (10 - SA) / 9 → [0, 1]
        - RRS : déjà en [0, 1]
        - PNS : déjà en [0, 1]

        All sub-scores are clamped to physically reasonable ranges to
        protect against corrupted library entries (the Tartarus CSV
        contains ~2,800 entries with a corrupted value of 10000.0).
        """
        scores = self.score(smiles)

        # Chaque composante normalisée en [0, 1]
        mpo_norm = max(0.0, min(1.0, scores["mpo"]))
        dock_norm = self._normalize_docking(scores["docking"])
        syba_norm = self._normalize_syba(scores["syba"])
        sa_reward = max(0.0, 10.0 - scores["sa"]) / 9.0

        reward_val = (
            self.weights.get("mpo", 0.0) * mpo_norm
            + self.weights.get("docking", 0.0) * dock_norm
            + self.weights.get("syba", 0.0) * syba_norm
            + self.weights.get("sa", 0.0) * sa_reward
        )
        if self.use_rrs and "rrs" in scores and "rrs" in self.weights:
            rrs_norm = max(0.0, min(1.0, scores["rrs"]))
            reward_val += self.weights["rrs"] * rrs_norm
        if self.use_pns and "pns" in scores and "pns" in self.weights:
            pns_norm = max(0.0, min(1.0, scores["pns"]))
            reward_val += self.weights["pns"] * pns_norm
        if self.use_activity and "activity" in scores and "activity" in self.weights:
            act_norm = max(0.0, min(1.0, scores["activity"]))
            reward_val += self.weights["activity"] * act_norm
        # Small drug-likeness bonus: +0.02 for drug-like molecules (gentle nudge)
        if scores.get("drug_like", 0.0) > 0.5:
            reward_val += 0.02
        return reward_val

    # ── Library loading ────────────────────────────────────────────────
    def _load_activity_library(self) -> None:
        """Load public ChEMBL actives and build the dense fingerprint matrix.

        Same dense-matrix pattern as the Tartarus library: one matrix built at
        init, reused by every call (value-identical to per-call Tanimoto scan).
        Uses float32 dense 2048-bit Morgan fingerprints.
        """
        if not ACTIVITY_CSV.exists():
            warnings.warn(
                f"Public activity dataset not found: {ACTIVITY_CSV} — "
                "activity oracle will return 0.0"
            )
            return
        try:
            df = pd.read_csv(ACTIVITY_CSV)
            df = df.dropna(subset=["smiles", "activity"]).drop_duplicates("smiles")
            act = df.loc[df["activity"] >= 0.5, "smiles"].astype(str).tolist()
            if not act:
                return
            fps = self._compute_fingerprints(act)
            valid = [(smi, fp) for smi, fp in zip(act, fps) if fp is not None]
            n = len(valid)
            if n == 0:
                return
            lib = (
                cp.zeros((n, 2048), dtype=cp.float32)
                if _USE_GPU else np.zeros((n, 2048), dtype=np.float32)
            )
            for i, (_, fp) in enumerate(valid):
                onbits = list(fp.GetOnBits())
                if onbits:
                    lib[i, onbits] = 1.0
            self._activity_dense = lib
            self._activity_norms = lib.sum(axis=1)
            self._activity_n = n
            print(f"[p4_mcts_oracles] Activity oracle: {n} ChEMBL actives loaded "
                  f"({'GPU' if _USE_GPU else 'numpy'} backend)", flush=True)
        except Exception as exc:  # pragma: no cover
            warnings.warn(f"Failed to load activity library: {exc}")
            self._activity_dense = None
            self._activity_n = 0

    def _load_precomputed_libraries(self) -> None:
        """Load P1/P2 score CSVs into memory as lookup tables.

        After loading, computes drug-likeness flags for all library
        entries using medchem (Lipinski, Veber, PAINS filters).
        """
        if C6_CSV.exists():
            try:
                df = pd.read_csv(C6_CSV)
                if "input" in df.columns:
                    df = df.rename(columns={"input": "smiles"})
                df = df.drop_duplicates(subset=["smiles"])
                self._c6 = (
                    df.set_index("smiles")
                    .replace([np.inf, -np.inf], np.nan)
                    .to_dict(orient="index")
                )
            except Exception as exc:  # pragma: no cover
                warnings.warn(f"Failed to load C6 library: {exc}")
                self._c6 = {}

        if TARTARUS_CSV.exists():
            try:
                df = pd.read_csv(TARTARUS_CSV)
                if "smile" in df.columns:
                    df = df.rename(columns={"smile": "smiles"})
                # Detect target columns dynamically for PNS oracle
                target_cols = [c for c in df.columns if c.startswith("score_")]
                self._tartarus_target_cols = list(target_cols)
                if target_cols:
                    df["docking"] = df[target_cols].mean(axis=1)
                else:
                    df["docking"] = 0.0
                df = df.drop_duplicates(subset=["smiles"])
                self._tartarus = (
                    df.set_index("smiles")
                    .replace([np.inf, -np.inf], np.nan)
                    .to_dict(orient="index")
                )
                self._tartarus_smiles = list(self._tartarus.keys())
                self._tartarus_fingerprints = self._compute_fingerprints(
                    self._tartarus_smiles
                )
                self._build_tartarus_dense()
            except Exception as exc:  # pragma: no cover
                warnings.warn(f"Failed to load Tartarus library: {exc}")
                self._tartarus = {}
                self._tartarus_smiles = []
                self._tartarus_fps = None
                self._tartarus_dense = None
                self._tartarus_norms = None

    # ── Scoring helpers ────────────────────────────────────────────────
    def _canonical_smiles(self, smiles: str) -> str:
        """Return canonical SMILES; fall back to input on failure.

        Uses datamol (if available) for robust SMILES handling:
        - dm.to_mol() handles edge cases better than raw RDKit
        - dm.to_smiles() produces standardised canonical form
        """
        if smiles in self._canonical_cache:
            return self._canonical_cache[smiles]
        try:
            if _HAS_DATAMOL:
                mol = dm.to_mol(smiles)
                canon = dm.to_smiles(mol) if mol is not None else smiles
            else:
                mol = Chem.MolFromSmiles(smiles)
                canon = Chem.MolToSmiles(mol) if mol is not None else smiles
        except Exception:
            canon = smiles
        self._canonical_cache[smiles] = canon
        return canon

    def _cache_get(self, smiles: str, key: str) -> Optional[float]:
        canon = self._canonical_smiles(smiles)
        return self._runtime_cache.get(canon, {}).get(key)

    def _cache_set(self, smiles: str, key: str, value: float) -> None:
        canon = self._canonical_smiles(smiles)
        # LRU eviction: remove oldest entry if at capacity
        if canon not in self._runtime_cache and len(self._runtime_cache) >= self._cache_maxsize:
            self._runtime_cache.pop(next(iter(self._runtime_cache)), None)
        self._runtime_cache.setdefault(canon, {})[key] = value

    def _build_tartarus_dense(self) -> None:
        """Precompute the dense fingerprint matrix and bit-count norms once.

        The per-call Tanimoto scan then becomes a single dense matvec
        (value-identical to the per-call dense build in `_batch_tanimoto_gpu`,
        which is preserved as a fallback).
        """
        n_lib = len(self._tartarus_fingerprints)
        if n_lib == 0:
            self._tartarus_dense = None
            self._tartarus_norms = None
            return
        if _USE_GPU:
            lib_dense = cp.zeros((n_lib, 2048), dtype=cp.float32)
        else:
            lib_dense = np.zeros((n_lib, 2048), dtype=np.float32)
        for i, fp in enumerate(self._tartarus_fingerprints):
            if fp is not None:
                onbits = list(fp.GetOnBits())
                if onbits:
                    lib_dense[i, onbits] = 1.0
        self._tartarus_dense = lib_dense
        self._tartarus_norms = lib_dense.sum(axis=1)

    def _nearest_precomputed(self, query_fp) -> tuple[float, int]:
        """Best Tanimoto to the Tartarus library via the precomputed dense matrix.

        Value-identical to `_batch_tanimoto_gpu` (same float32 formula and
        same first-maximum tie-breaking) but O(1) matrix is reused across calls.
        """
        if self._tartarus_dense is None:
            return -1.0, 0
        onbits = list(query_fp.GetOnBits())
        query_norm = float(len(onbits))
        if _USE_GPU and isinstance(self._tartarus_dense, cp.ndarray):
            query_dense = cp.zeros(2048, dtype=cp.float32)
            if onbits:
                query_dense[onbits] = 1.0
            intersection = self._tartarus_dense @ query_dense
            denominator = query_norm + self._tartarus_norms - intersection
            cp.maximum(denominator, 1e-8, out=denominator)
            scores = intersection / denominator
            best_idx = int(cp.argmax(scores))
            return float(scores[best_idx]), best_idx
        query_dense = np.zeros(2048, dtype=np.float32)
        if onbits:
            query_dense[onbits] = 1.0
        intersection = self._tartarus_dense @ query_dense
        denominator = query_norm + self._tartarus_norms - intersection
        denominator = np.maximum(denominator, 1e-8)
        scores = intersection / denominator
        best_idx = int(np.argmax(scores))
        return float(scores[best_idx]), best_idx

    def _compute_fingerprints(self, smiles_list: list[str]) -> list:
        """Compute Morgan bit-vector fingerprints for a list of SMILES.

        Uses datamol parallelized batch processing (skill-based):
        dm.parallelized() for multi-CPU fingerprint computation,
        falling back to sequential RDKit if datamol unavailable.

        When a usable GPU device is present (`_USE_GPU`), batch Tanimoto operations
        in the oracle also use GPU acceleration via `_batch_tanimoto_gpu()`.
        """
        if not smiles_list:
            return []

        def _fp_from_smiles(smi: str) -> object | None:
            """Compute fingerprint for a single SMILES.
            gen created inside to ensure picklability for parallel workers."""
            if not smi:
                return None
            try:
                _g = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
                mol = Chem.MolFromSmiles(smi)
                return None if mol is None else _g.GetFingerprint(mol)
            except Exception:
                return None

        if _HAS_DATAMOL:
            # Parallelized batch fingerprinting via datamol
            return dm.parallelized(_fp_from_smiles, smiles_list, n_jobs=-1, progress=False)

        # Fallback: sequential RDKit
        return [_fp_from_smiles(smi) for smi in smiles_list]

    @staticmethod
    def _clamp_docking(score: float, default: float = -7.0) -> float:
        """Clamp a docking score to a physically reasonable range.

        Docking scores should be negative (binding) and in the range
        [-15, 0] kcal/mol. Positive values indicate steric clashes or
        corrupted data entries. Values > 0 are clamped to the default.
        NaN values are also replaced with the default.
        """
        if not np.isfinite(score) or score > 0:
            return default
        return max(-15.0, min(score, -0.1))

    @staticmethod
    def _tanimoto_sequential(query_fp, lib_fps: list) -> tuple[float, int]:
        """Compute best Tanimoto similarity sequentially (CPU fallback).

        Static method: does not depend on instance state. Can be called
        as ``OracleAggregator._tanimoto_sequential(...)``.
        """
        best_sim = -1.0
        best_idx = 0
        for idx, lib_fp in enumerate(lib_fps):
            if lib_fp is None:
                continue
            sim = TanimotoSimilarity(query_fp, lib_fp)
            if sim > best_sim:
                best_sim = sim
                best_idx = idx
        return best_sim, best_idx

    def _batch_tanimoto_gpu(self, query_fp, lib_fps: list) -> tuple[float, int]:
        """Compute batch Tanimoto similarity on GPU via CuPy.

        Converts RDKit bit-vectors to CuPy arrays and computes
        Tanimoto = |A ∩ B| / (|A| + |B| - |A ∩ B|) on GPU.
        Falls back to sequential CPU if CuPy unavailable.

        Returns
        -------
        tuple[float, int]
            (best_similarity, best_index)
        """
        if not _USE_GPU or not lib_fps:
            return OracleAggregator._tanimoto_sequential(query_fp, lib_fps)

        # GPU path: convert RDKit bit vectors to CuPy dense array
        try:
            n_lib = len(lib_fps)
            fp_size = 2048
            # Convert query to dense GPU array
            query_onbits = query_fp.GetOnBits()
            query_dense = cp.zeros(fp_size, dtype=cp.float32)
            query_dense[list(query_onbits)] = 1.0
            query_norm = float(len(query_onbits))

            # Convert lib fingerprints to dense GPU matrix (batch)
            lib_dense = cp.zeros((n_lib, fp_size), dtype=cp.float32)
            for i, fp in enumerate(lib_fps):
                if fp is not None:
                    onbits = list(fp.GetOnBits())
                    if onbits:
                        lib_dense[i, onbits] = 1.0

            # Batch Tanimoto: |A ∩ B| / (|A| + |B| - |A ∩ B|)
            intersection = lib_dense @ query_dense
            lib_norms = cp.sum(lib_dense, axis=1)
            denominator = query_norm + lib_norms - intersection
            denominator[denominator < 1e-8] = 1e-8
            tanimoto_scores = intersection / denominator

            best_idx_cp = int(cp.argmax(tanimoto_scores))
            best_sim = float(tanimoto_scores[best_idx_cp])
            return best_sim, best_idx_cp
        except Exception:
            return OracleAggregator._tanimoto_sequential(query_fp, lib_fps)

    def _tanimoto_nearest_docking(self, smiles: str) -> float:
        """Return the docking score of the nearest neighbour by Tanimoto similarity.

        Uses GPU-accelerated batch Tanimoto when CuPy is available
        (`_USE_GPU`), otherwise falls back to sequential CPU.

        The score is clamped to a physically reasonable range [-15, -0.1] kcal/mol
        to protect against corrupted entries in the Tartarus library (e.g., 2836
        entries with docking=10000.0 due to NaN mean aggregation).
        """
        if not self._tartarus_fingerprints or not self._tartarus_smiles:
            return -7.0

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return -7.0

        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        query_fp = gen.GetFingerprint(mol)

        # Precomputed dense matvec when available (value-identical), else
        # the original per-call batch Tanimoto (GPU-accelerated if available)
        if self._tartarus_dense is not None:
            best_sim, best_idx = self._nearest_precomputed(query_fp)
        else:
            best_sim, best_idx = self._batch_tanimoto_gpu(
                query_fp, self._tartarus_fingerprints
            )
        best_smi = self._tartarus_smiles[best_idx]
        raw_score = float(self._tartarus[best_smi].get("docking", -7.0))
        return self._clamp_docking(raw_score)

    # ── Individual oracles ───────────────────────────────────────────
    def _mpo_score(self, smiles: str) -> float:
        """MPO score: use precomputed P1 value or fall back to a QED proxy."""
        cached = self._cache_get(smiles, "mpo")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)
        if canon in self._c6:
            score = float(self._c6[canon].get("weighted_mpo_score", 0.5))
        else:
            # Fallback: QED is a good proxy for the drug-likeness part of MPO
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                score = 0.0
            else:
                score = Descriptors.qed(mol)

        self._cache_set(smiles, "mpo", score)
        return score

    def _docking_score(self, smiles: str) -> float:
        """Docking score (kcal/mol): use precomputed Tartarus or nearest-neighbour proxy.

        Scores are clamped to a physically reasonable range [-15, -0.1] kcal/mol
        to protect against corrupted library entries. The Tartarus CSV contains
        2,836 entries with a docking value of 10000.0 (from mean aggregation of
        score columns with corrupted NaN/inf values).
        """
        cached = self._cache_get(smiles, "docking")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)
        if canon in self._tartarus:
            raw_score = float(self._tartarus[canon].get("docking", -7.0))
            score = self._clamp_docking(raw_score)
        elif self.docking_fallback == "similarity":
            score = self._tanimoto_nearest_docking(canon)
        else:
            score = -7.0

        self._cache_set(smiles, "docking", score)
        return score

    def _syba_score(self, smiles: str) -> float:
        """SYBA synthetic accessibility score: precomputed or on-the-fly."""
        cached = self._cache_get(smiles, "syba")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)
        if canon in self._c6:
            score = float(self._c6[canon].get("syba_score", 0.0))
        elif self._syba is not None:
            try:
                score = float(self._syba.predict(canon))
            except Exception:
                score = 0.0
        else:
            score = 0.0

        self._cache_set(smiles, "syba", score)
        return score

    def _sa_score(self, smiles: str) -> float:
        """Synthetic accessibility penalty (lower is better): precomputed or RDKit-based.

        Uses the Ertl & Schuffenhauer (2009) fragment contribution approach
        via RDKit's rdkit.Chem.Descriptors when sascorer is unavailable.

        The score is a penalty in [1, 10]:
        - 1 = easy to synthesise
        - 10 = very difficult to synthesise
        - Default 3.0 when neither precomputed nor on-the-fly is available
        """
        cached = self._cache_get(smiles, "sa")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)
        if canon in self._c6:
            score = float(self._c6[canon].get("sa_score", 3.0))
        elif _HAS_SASCORER:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                score = 3.0
            else:
                try:
                    score = float(sascorer.calculateScore(mol))
                except Exception:
                    score = 3.0
        else:
            # Fallback: estimate SA from molecular complexity using RDKit
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                score = 3.0
            else:
                try:
                    # Approximate SA from: ring count, chiral centers,
                    # heteroatom ratio, molecular weight, rotatable bonds
                    from rdkit.Chem import Descriptors
                    n_rings = Descriptors.RingCount(mol)
                    n_hetero = Descriptors.NumHeteroatoms(mol)
                    n_chiral = len(Chem.FindMolChiralCenters(mol, includeUnspec=True))
                    n_atoms = mol.GetNumAtoms()
                    n_rot = Descriptors.NumRotatableBonds(mol)
                    mw = Descriptors.MolWt(mol)

                    # Heuristic: more rings, chiral centers, heteroatoms = harder to make
                    base = 1.0
                    base += n_rings * 0.5          # each ring adds 0.5
                    base += n_chiral * 0.8          # chiral centers add 0.8
                    base += (n_hetero / max(n_atoms, 1)) * 2.0  # heteroatom fraction
                    base += (mw / 500.0) * 1.5       # molecular weight contribution
                    base += (n_rot / 15.0) * 0.5     # flexibility penalty
                    score = min(10.0, max(1.0, base))
                except Exception:
                    score = 3.0

        self._cache_set(smiles, "sa", score)
        return score

    # ── Drug-likeness filter (scientific-agent-skills: medchem) ─────
    def _medchem_filter(self, smiles: str) -> dict[str, bool]:
        """Apply drug-likeness filters using the medchem library.

        Checks:
        1. Lipinski Rule-of-Five (MW ≤ 500, logP ≤ 5, HBD ≤ 5, HBA ≤ 10)
        2. Veber rules (RotBonds ≤ 10, TPSA ≤ 140)
        3. PAINS structural alerts (pan-assay interference compounds)
        4. Brenk alerts (undesirable functional groups)

        Returns a dict with per-rule pass/fail and an overall drug_like flag.

        If medchem is not installed, falls back to RDKit-only checks
        (Lipinski via rdkit.Chem.Lipinski, PAINS via rdkit.Chem.FilterCatalog).
        """
        result = {
            "lipinski": True,
            "veber": True,
            "pains": True,
            "brenk": True,
            "drug_like": True,
        }

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return result

        if _HAS_MEDCHEM:
            # ── medchem library (≥2.0.5) ────────────────────────────────
            try:
                # Rule-of-Five + Veber via RuleFilters
                rfilter = mc.rules.RuleFilters(
                    rule_list=["rule_of_five", "rule_of_veber"],
                )
                rules_df = rfilter(mols=[mol], n_jobs=1, progress=False, keep_props=False)
                if not rules_df.empty:
                    result["lipinski"] = bool(rules_df.iloc[0].get("rule_of_five", True))
                    result["veber"] = bool(rules_df.iloc[0].get("rule_of_veber", True))

                # PAINS alert filter
                pains_filter = mc.structural.CommonAlertsFilters()
                pains_df = pains_filter(mols=[mol], n_jobs=1, progress=False)
                if not pains_df.empty:
                    result["pains"] = bool(pains_df.iloc[0].get("pass_filter", True))

                # Brenk catalog filter
                result["brenk"] = mc.functional.alert_filter(
                    mols=[mol], alerts=["brenk"], n_jobs=1
                )[0] if hasattr(mc.functional, "alert_filter") else True
            except Exception:
                pass
        else:
            # ── RDKit fallback ───────────────────────────────────────────
            try:
                from rdkit.Chem.Lipinski import (
                    NumHAcceptors, NumHDonors, NumRotatableBonds, MolLogP,
                )
                mw = Descriptors.MolWt(mol)
                logp = MolLogP(mol)
                hbd = NumHDonors(mol)
                hba = NumHAcceptors(mol)
                result["lipinski"] = (mw <= 500 and logp <= 5 and hbd <= 5 and hba <= 10)

                rotb = NumRotatableBonds(mol)
                tpsa = Descriptors.TPSA(mol)
                result["veber"] = (rotb <= 10 and tpsa <= 140)

                # PAINS via RDKit FilterCatalog
                from rdkit.Chem import FilterCatalog, FilterCatalogParams
                params = FilterCatalogParams()
                params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
                catalog = FilterCatalog(params)
                entry = catalog.GetFirstMatch(mol)
                result["pains"] = (entry is None)
            except Exception:
                pass

        # Note: Brenk alerts are only checked when medchem is installed.
        # The RDKit-only fallback path does not include Brenk because
        # it requires the NIBR filter catalog (lilly-medchem-rules package).
        # This is acceptable because Brenk alerts are less common and
        # Lipinski/Veber/PAINS cover the most important filters.
        result["drug_like"] = all([
            result["lipinski"], result["veber"],
            result["pains"], result["brenk"],
        ])
        return result

    # ── Activity (public ChEMBL proximity) oracle ────────────────────
    def _activity_max_tanimoto(self, query_fp) -> float:
        """Best Morgan-2 Tanimoto of the query to the ChEMBL active library.

        Dense matvec on the precomputed matrix (value-identical to a per-call
        scan). Returns -1.0 when no library is loaded.
        """
        if self._activity_dense is None:
            return -1.0
        onbits = list(query_fp.GetOnBits())
        qn = float(len(onbits))
        if _USE_GPU and isinstance(self._activity_dense, cp.ndarray):
            q = cp.zeros(2048, dtype=cp.float32)
            if onbits:
                q[onbits] = 1.0
            inter = self._activity_dense @ q
            denom = qn + self._activity_norms - inter
            cp.maximum(denom, 1e-8, out=denom)
            return float(cp.max(inter / denom))
        q = np.zeros(2048, dtype=np.float32)
        if onbits:
            q[onbits] = 1.0
        inter = self._activity_dense @ q
        denom = qn + self._activity_norms - inter
        denom = np.maximum(denom, 1e-8)
        return float(np.max(inter / denom))

    def _activity_score(self, smiles: str) -> float:
        """Public-activity proximity oracle (v12).

        max Morgan-2 Tanimoto to known antimalarial actives from the
        independent public ChEMBL malaria IC50/EC50 dataset (19,321 actives).
        Continuous scaling identical to the RRS oracle:
          - Tanimoto <= 0.20 → gentle gradient (score = Tanimoto)
          - Tanimoto 0.20-1.0 → linear to 1.0
        Returns a score in [0, 1] (higher = closer to known actives).
        """
        cached = self._cache_get(smiles, "activity")
        if cached is not None:
            return cached

        if self._activity_dense is None or self._activity_n == 0:
            return 0.0

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return 0.0

        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        try:
            query_fp = gen.GetFingerprint(mol)
        except Exception:
            return 0.0

        best_sim = self._activity_max_tanimoto(query_fp)
        if best_sim < 0:
            return 0.0
        if best_sim < 0.20:
            score = best_sim  # gentle gradient in [0.0, 0.20)
        else:
            score = max(0.0, min(1.0, (best_sim - 0.20) / 0.80))

        self._cache_set(smiles, "activity", score)
        return score

    # ── RRS (Resistance Resilience Score) oracle ────────────────────
    def _rrs_score(self, smiles: str) -> float:
        """RRS-informed chemotype-similarity proxy based on Morgan/Tanimoto
        similarity to P2 reference chemotypes.

        This implementation does not propagate per-target WT/mutant ratios;
        it is not a validated mutant-binding prediction. For novel molecules
        with low similarity, the continuous score provides a smooth proxy
        gradient rather than a biological resilience measurement.

        Uses a continuous scaling function:
        - Tanimoto ≤ 0.20 → RRS = 0.0 (novel chemotype, nearest-neighbour avg)
        - Tanimoto 0.20-1.0 → RRS = 0.0-1.0 (linear, continuous at 0.20)

        Returns a score in [0, 1], where higher values indicate greater
        similarity to the reference chemotype set.

        Note: RRS does NOT apply drug-likeness filtering (
        `_medchem_filter`) because resistance-resilient chemotypes may
        include natural-product-like molecules that violate standard
        drug-likeness rules.
        """
        cached = self._cache_get(smiles, "rrs")
        if cached is not None:
            return cached

        # No valid references loaded — return default
        if not self._rrs_ref_fps:
            return 0.0

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return 0.0

        gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
        try:
            query_fp = gen.GetFingerprint(mol)
        except Exception:
            return 0.0

        # Use GPU-accelerated batch Tanimoto if available
        best_sim, _ = self._batch_tanimoto_gpu(query_fp, self._rrs_ref_fps)

        if best_sim < 0:
            return 0.0

        if best_sim < 0.20:
            # Multi-fidelity fallback via GPU batch result
            score = best_sim  # gentle gradient in [0.0, 0.20]
        else:
            # Continuous scaling: Tanimoto [0.20, 1.00] → RRS [0.0, 1.0]
            score = max(0.0, min(1.0, (best_sim - 0.20) / 0.80))

        self._cache_set(smiles, "rrs", score)
        return score

    # ── PNS (Polypharmacology Network Score) oracle ─────────────────
    def _pns_score(self, smiles: str) -> float:
        """PNS-informed normalized Tartarus multi-target docking proxy.

        The current Tartarus library exposes three detected score columns
        (`score_1syh`, `score_6y2f`, `score_4lde`), which are averaged for
        exact matches. A Tanimoto-weighted nearest-neighbour fallback is used
        for novel molecules. This is not a direct four-target Pf panel.

        Returns a score normalised to [0, 1], where higher values indicate
        stronger aggregate docking in the detected Tartarus columns.
        """
        cached = self._cache_get(smiles, "pns")
        if cached is not None:
            return cached

        canon = self._canonical_smiles(smiles)

        if canon in self._tartarus and self._tartarus_target_cols:
            # Exact match in Tartarus library (highest fidelity)
            scores = []
            for col in self._tartarus_target_cols:
                val = self._tartarus[canon].get(col, None)
                if val is not None and np.isfinite(val):
                    scores.append(float(val))
            if not scores:
                scores = [-7.0]
        elif self._tartarus_smiles:
            # Multi-fidelity fallback: Tanimoto-weighted K-NN average
            # instead of single nearest neighbour (smoother gradient)
            mol = Chem.MolFromSmiles(canon)
            if mol is not None:
                gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
                query_fp = gen.GetFingerprint(mol)
                # Compute Tanimoto to all Tartarus molecules
                weighted_scores = []
                total_weight = 0.0
                for lib_smi, lib_fp in zip(self._tartarus_smiles, self._tartarus_fingerprints):
                    if lib_fp is None:
                        continue
                    sim = TanimotoSimilarity(query_fp, lib_fp)
                    if sim > 0.2:  # only consider meaningful similarity
                        dock = self._tartarus[lib_smi].get("docking", -7.0)
                        if np.isfinite(dock):
                            weighted_scores.append(float(dock) * sim)
                            total_weight += sim
                if weighted_scores and total_weight > 0:
                    scores = [sum(weighted_scores) / total_weight]
                else:
                    scores = [self._tanimoto_nearest_docking(canon)]
            else:
                scores = [self._tanimoto_nearest_docking(canon)]
        else:
            scores = [-7.0]

        # Mean docking across available targets (more negative = better)
        mean_dock = float(np.mean(scores))

        # Normalise from [-12, -5] kcal/mol to [0, 1]
        # -12 kcal/mol → 1.0 (strong binding), -5 kcal/mol → 0.0 (weak)
        pns = max(0.0, min(1.0, (mean_dock + 5.0) / 7.0))

        self._cache_set(smiles, "pns", pns)
        return pns


def make_oracle(
    weights: Optional[Dict[str, float]] = None,
    use_precomputed: bool = True,
    docking_fallback: str = "similarity",
    use_rrs: bool = True,
    use_pns: bool = True,
    use_activity: bool = True,
    cache_maxsize: int = 10000,
    rrs_fallback_k: int = 3,
) -> Callable[[str], float]:
    """Factory returning a callable reward function."""
    aggregator = OracleAggregator(
        weights,
        use_precomputed=use_precomputed,
        docking_fallback=docking_fallback,
        use_rrs=use_rrs,
        use_pns=use_pns,
        use_activity=use_activity,
        cache_maxsize=cache_maxsize,
        rrs_fallback_k=rrs_fallback_k,
    )
    return aggregator.reward


if __name__ == "__main__":
    oracle = OracleAggregator()
    scores = oracle.score("CCO")
    print("Scores:", scores)
    print("Reward:", oracle.reward("CCO"))
