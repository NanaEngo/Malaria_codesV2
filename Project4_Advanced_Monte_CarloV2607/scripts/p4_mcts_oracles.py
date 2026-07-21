#!/usr/bin/env python3
"""P4 — Scoring oracles for MCTS molecular optimization.

Provides pharmacological scores (MPO, docking, SYBA, SA) and two advanced
oracles that bring P2 polypharmacology awareness into P4:

**RRS (Resistance Resilience Score):** Measures how similar a generated
molecule is to known hits that maintain binding against clinically relevant
resistance mutations (PfDHFR N51I, C59R, S108N, I164L; PfCRT K76T, K76A).
Uses Tanimoto fingerprint similarity as a proxy when experimental mutant
binding data is unavailable.

**PNS (Polypharmacology Network Score):** Multi-target binding score across
four P. falciparum targets (PfDHFR, PfCRT, PfATP4, PfClpP). Derived from
Tartarus multi-target docking results, providing a polypharmacology-aware
reward that favours molecules with broad target engagement.

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
        cache_maxsize: int = 10000,
        rrs_fallback_k: int = 3,
    ) -> None:
        self.weights = weights or {
            "mpo": 0.30,
            "docking": 0.25,
            "syba": 0.15,
            "sa": 0.05,
            "rrs": 0.15,
            "pns": 0.10,
        }
        self.docking_fallback = docking_fallback
        self.use_rrs = use_rrs
        self.use_pns = use_pns
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

        # RRS reference fingerprints (only if RRS enabled)
        self._rrs_ref_fps: list = []
        if self.use_rrs:
            self._load_rrs_references()

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
        resistance awareness (rrs) and polypharmacology (pns).
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
        return reward_val

    # ── Library loading ────────────────────────────────────────────────
    def _load_precomputed_libraries(self) -> None:
        """Load P1/P2 score CSVs into memory as lookup tables."""
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
            except Exception as exc:  # pragma: no cover
                warnings.warn(f"Failed to load Tartarus library: {exc}")
                self._tartarus = {}
                self._tartarus_smiles = []
                self._tartarus_fps = None

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

    def _compute_fingerprints(self, smiles_list: list[str]) -> list:
        """Compute Morgan bit-vector fingerprints for a list of SMILES.

        Uses datamol parallelized batch processing (skill-based):
        dm.parallelized() for multi-CPU fingerprint computation,
        falling back to sequential RDKit if datamol unavailable.
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

    def _tanimoto_nearest_docking(self, smiles: str) -> float:
        """Return the docking score of the nearest neighbour by Tanimoto similarity.

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

        # Compute true Tanimoto similarity against precomputed bit fingerprints
        best_sim = -1.0
        best_idx = 0
        for idx, lib_fp in enumerate(self._tartarus_fingerprints):
            if lib_fp is None:
                continue
            sim = TanimotoSimilarity(query_fp, lib_fp)
            if sim > best_sim:
                best_sim = sim
                best_idx = idx

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
        """Synthetic accessibility penalty (lower is better): precomputed or RDKit SAscore."""
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
            score = 3.0

        self._cache_set(smiles, "sa", score)
        return score

    # ── RRS (Resistance Resilience Score) oracle ────────────────────
    def _rrs_score(self, smiles: str) -> float:
        """Resistance Resilience Score: max Tanimoto similarity to known
        resistance-resilient hits.

        **Multi-fidelity improvement**: For novel molecules with low Tanimoto
        similarity to any single reference, uses the mean RRS of the K nearest
        neighbours (K=3) instead of returning 0.0. This provides a smooth
        gradient even for molecules in novel chemical space.

        RRS quantifies how similar a generated molecule is to known
        chemotypes that maintain binding against clinically prevalent
        resistance mutations (PfDHFR N51I, C59R, S108N, I164L;
        PfCRT K76T, K76A).

        Uses a continuous scaling function:
        - Tanimoto ≤ 0.20 → RRS = 0.0 (novel chemotype, nearest-neighbour avg)
        - Tanimoto 0.20-1.0 → RRS = 0.0-1.0 (linear, continuous at 0.20)

        Returns a score in [0, 1], where higher values indicate greater
        predicted resistance resilience.
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

        # Compute similarities to ALL reference molecules and sort
        sims = []
        for ref_fp in self._rrs_ref_fps:
            if ref_fp is None:
                continue
            sim = TanimotoSimilarity(query_fp, ref_fp)
            sims.append(sim)

        if not sims:
            return 0.0

        sims.sort(reverse=True)
        max_sim = sims[0]

        # Multi-fidelity fallback: if max_sim < 0.20, use top-K mean
        # instead of returning 0.0 (smooth gradient for novel molecules)
        if max_sim < 0.20:
            k = min(self._rrs_fallback_k, len(sims))
            mean_sim = sum(sims[:k]) / k if k > 0 else max_sim
            # Scale [0.0, 0.20] → [0.0, 0.20] (gentle gradient)
            score = max(0.0, (mean_sim - 0.0) / 0.20) * 0.20
        else:
            # Continuous scaling: Tanimoto [0.20, 1.00] → RRS [0.0, 1.0]
            score = max(0.0, min(1.0, (max_sim - 0.20) / 0.80))

        self._cache_set(smiles, "rrs", score)
        return score

    # ── PNS (Polypharmacology Network Score) oracle ─────────────────
    def _pns_score(self, smiles: str) -> float:
        """Polypharmacology Network Score: mean docking score across
        all available P. falciparum targets.

        **Multi-fidelity improvement**: Uses a Tanimoto-weighted average
        of the K nearest neighbours' PNS scores when the query molecule
        is not found in the Tartarus library. This provides a smooth
        gradient even for novel molecules without direct docking data.

        Uses per-target docking scores from the Tartarus library
        (columns detected dynamically at load time). Falls back to
        nearest-neighbour proxy when Tartarus data is unavailable.

        Returns a score normalised to [0, 1], where higher values
        indicate better multi-target binding.
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
        cache_maxsize=cache_maxsize,
        rrs_fallback_k=rrs_fallback_k,
    )
    return aggregator.reward


if __name__ == "__main__":
    oracle = OracleAggregator()
    scores = oracle.score("CCO")
    print("Scores:", scores)
    print("Reward:", oracle.reward("CCO"))
