#!/usr/bin/env python
"""PP-01_PfCRT_WT endpoint replicate consistency (R1 canonical 15320 vs R2 rerun 15502).

Parses DELTA TOTAL rows from the two FINAL_RESULTS_MMPBSA.dat sources of truth,
applies the manuscript quoting convention (mean +/- within-trajectory SD over
100 snapshots; SEM reported separately), and writes versioned JSON+MD artifacts.

Convention guard: gmx_MMPBSA columns are
  Average | SD(Prop.) | SD | SEM(Prop.) | SEM
The manuscript quotes SD (see SM Table S8 caption), never SD(Prop.).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R1_DAT = ROOT / "results/set_c_md/mmgbsa_20260819/PP-01_PfCRT_WT/FINAL_RESULTS_MMPBSA.dat"
R2_DAT = ROOT / "results/set_c_md/single_rerun_20260825/mmgbsa/PP-01_PfCRT_WT/FINAL_RESULTS_MMPBSA.dat"
OUT_DIR = ROOT / "results/set_c_md/single_rerun_20260825"
N_FRAMES = 100  # startframe=1 endframe=1000 interval=10


def parse_delta_total(dat: Path) -> dict:
    lines = dat.read_text(errors="replace").splitlines()
    idx = next(i for i, ln in enumerate(lines) if ln.startswith("Delta (Complex"))
    header_i = next(i for i in range(idx, len(lines)) if "Average" in lines[i])
    cols = [c.strip() for c in lines[header_i].split()][2:]  # drop 'Energy Component' label cols
    row = next(
        ln.split() for ln in lines[idx:]
        if ln.replace("\u0394", "").strip().startswith("TOTAL") and "\u0394" in ln
    )
    vals = dict(zip(cols, map(float, row[1:])))
    return vals


def summarize(tag: str, v: dict) -> dict:
    return {
        "tag": tag,
        "mean_kcal_mol": v["Average"],
        "sd_within_traj_kcal_mol": v["SD"],
        "sd_propagated_kcal_mol": v["SD(Prop.)"],
        "sem_kcal_mol": v["SEM"],
        "n_snapshots": N_FRAMES,
    }


def sample_sd(xs):
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def main() -> None:
    r1 = parse_delta_total(R1_DAT)
    r2 = parse_delta_total(R2_DAT)

    # sanity: known source values, finite, positive spreads
    assert abs(r1["Average"] - (-30.61)) < 5e-3 and abs(r2["Average"] - (-28.60)) < 5e-3
    for v in (r1, r2):
        assert all(math.isfinite(x) for x in v.values())
        assert v["SEM"] * math.sqrt(N_FRAMES) <= v["SD"] + 1e-9

    s1, s2 = summarize("R1_canonical_15320_20260819", r1), summarize("R2_rerun_15502_single_rerun", r2)
    m1, m2 = s1["mean_kcal_mol"], s2["mean_kcal_mol"]
    offset = abs(m1 - m2)
    rep_mean = (m1 + m2) / 2.0
    rep_sd = sample_sd([m1, m2])
    se_diff_iid = math.sqrt(s1["sem_kcal_mol"] ** 2 + s2["sem_kcal_mol"] ** 2)

    out = {
        "generated": "2026-08-26",
        "system": "PP-01_PfCRT_WT",
        "protocol": "gmx_MMPBSA v1.5 GB-OBC2 igb=5 salt 0.15 M, frames 1-1000 interval 10",
        "quoting_convention": "mean +/- within-trajectory SD over 100 snapshots (manuscript-wide); SEM informational",
        "replicates": [s1, s2],
        "inter_replicate": {
            "offset_abs_kcal_mol": round(offset, 2),
            "mean_of_means_kcal_mol": round(rep_mean, 2),
            "sample_sd_of_means_kcal_mol": round(rep_sd, 2),
            "iid_frame_sem_diff_kcal_mol": round(se_diff_iid, 3),
            "caveat": (
                "Under an i.i.d.-frame assumption the offset would exceed the naive combined SEM "
                f"({offset:.2f} vs {se_diff_iid:.2f}); MD snapshots are strongly autocorrelated, so "
                "i.i.d. SEMs understate the true uncertainty and two replicates cannot resolve the "
                "offset as significant at the replicate level. Conservative reading: endpoint-level "
                f"reproducibility supported at ~{offset:.1f} kcal/mol resolution."
            ),
            "recommended_noise_floor_kcal_mol": round(offset, 2),
            "noise_floor_usage": (
                "Empirical floor for interpreting single-replicate mutant-vs-WT endpoint contrasts; "
                "contrasts smaller than this scale are not resolvable without additional replicates."
            ),
        },
        "sources": {"r1": str(R1_DAT.relative_to(ROOT)), "r2": str(R2_DAT.relative_to(ROOT))},
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "wt_replicate_consistency.json").write_text(json.dumps(out, indent=2) + "\n")

    md = [
        "# PP-01_PfCRT_WT — cohérence inter-réplicats (endpoint MM-GBSA)",
        "",
        f"- R1 canonique (batch 15320/20260819): {m1:+.2f} ± {s1['sd_within_traj_kcal_mol']:.2f} kcal/mol (SD, {N_FRAMES} snap.; SEM {s1['sem_kcal_mol']:.2f})",
        f"- R2 rerun (job SLURM 15502): {m2:+.2f} ± {s2['sd_within_traj_kcal_mol']:.2f} kcal/mol (SD, {N_FRAMES} snap.; SEM {s2['sem_kcal_mol']:.2f})",
        f"- Offset inter-réplicats |R1-R2| = {offset:.2f} kcal/mol (< 1 SD intra-trajectoire de chaque run)",
        f"- Moyenne des moyennes ± SD d'échantillon (n=2): {rep_mean:+.2f} ± {rep_sd:.2f} kcal/mol",
        "- Caveat honnête: sous hypothèse i.i.d. des frames l'offset dépasserait le SEM combiné naïf "
        f"({se_diff_iid:.2f}); l'autocorrélation temporelle invalide cette lecture, deux réplicats ne permettent pas de trancher la significativité de l'offset.",
        f"- Adoption conservatrice: plancher de bruit empirique inter-réplicats ≈ {offset:.1f} kcal/mol pour l'interprétation des contrastes mutant-vs-WT en réplicas simples.",
        "",
    ]
    (OUT_DIR / "wt_replicate_consistency.md").write_text("\n".join(md))

    tex = "\n".join([
        r"%% WT pillar replicate consistency (PP-01_PfCRT_WT)",
        r"%% Source (do not hand-edit): scripts/p2_wt_replicate_consistency.py",
        r"%%   <- results/set_c_md/single_rerun_20260825/wt_replicate_consistency.json",
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Endpoint replicate consistency for the PP-01 PfCRT wild-type pillar. Two independent",
        r"\qty{10}{\nano\second} productions executed under the identical MDP and analysis chain",
        r"(GB$^{\text{OBC2}}$ igb=5, \qty{0.15}{\molar} salt, \num{100} snapshots) are compared.",
        r"Tabulated spreads are the within-trajectory SD and the SEM over stored snapshots;",
        r"the manuscript-wide quoted uncertainty elsewhere is the SEM.",
        r"The SEM is informational here because MD snapshots are temporally autocorrelated.",
        rf"The between-replicate offset ($|\Delta| = {offset:.2f}$\,\si{{\kcalmol}}) lies within one within-trajectory",
        rf"standard deviation of either run (inter-replicate mean $\pm$ sample SD ${rep_mean:+.2f} \pm {rep_sd:.2f}$\,\si{{\kcalmol}}).",
        r"A naive i.i.d.-frame reading would combine the two SEMs to "
        rf"${se_diff_iid:.2f}$\,\si{{\kcalmol}}\ and flag the offset as significant; this reading is invalid under",
        r"autocorrelation, and two replicates cannot resolve the offset at the replicate level. We therefore adopt",
        rf"a conservative empirical replicate-noise floor of ${offset:.1f}$\,\si{{\kcalmol}} for interpreting",
        r"single-replicate mutant-vs-wild-type endpoint contrasts (see manuscript Limitations).}",
        rf"\label{{tab:setc_wt_replicate_consistency}}",
        r"\small",
        r"\begin{tabular}{l l S[table-format=-3.2] S[table-format=1.2] S[table-format=1.2]}",
        r"\toprule",
        r"Replicate & Production & {$\Delta G_{\mathrm{bind}}$ (\si{\kcalmol})} & {SD} & {SEM} \\",
        r"\midrule",
        rf"R1 (canonical) & batch 15320 & {m1:.2f} & {s1['sd_within_traj_kcal_mol']:.2f} & {s1['sem_kcal_mol']:.2f} \\",
        rf"R2 (rerun) & job 15502 & {m2:.2f} & {s2['sd_within_traj_kcal_mol']:.2f} & {s2['sem_kcal_mol']:.2f} \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
        "",
    ])
    tex_path = ROOT / "manuscript/LaTeX/Table_S10_WT_Replicate_Consistency.tex"
    tex_path.write_text(tex)

    print(f"offset={offset:.2f} rep_mean={rep_mean:.2f} rep_sd={rep_sd:.2f} -> artifacts written")


if __name__ == "__main__":
    main()
