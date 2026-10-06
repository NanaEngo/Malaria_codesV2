import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 4.8))
rows = [
    ("Phase 1 — QMSE development\n(kernel alignment)", 2.5, 3.5, "#1f4e79"),
    ("Phase 2 — Hybrid architectures\n(QKT core; QFE/Q-GNN stretched)", 6.0, 3.5, "#2e75b6"),
    ("Phase 3 — Scaffold-split validation\n(+ stretched Q-GNN)", 9.0, 3.0, "#5b9bd5"),
    ("Phase 4 — Dissemination\n+ final report", 10.0, 2.0, "#9dc3e6"),
]
# Mobility schedule (FR=red FR->CM, CM=blue CM->FR) — matches V2 budget tables (6 solo mobilities)
mobilities = [
    ("M1 FR->CM (PI)", 4.5, "#c00000"),
    ("M2b CM->FR (PI)", 5.5, "#0070c0"),
    ("M1b FR->CM (postdoc)", 6.5, "#c00000"),
    ("M2 CM->FR (PhD)", 7.5, "#0070c0"),
    ("M3a FR->CM (PhD)", 8.5, "#c00000"),
    ("M4 CM->FR (postdoc)", 10.5, "#0070c0"),
]
ylabels = []
for i, (name, start, dur, color) in enumerate(rows):
    y = len(rows) - i
    ax.barh(y, dur, left=start, height=0.45, color=color, edgecolor="white")
    ylabels.append((y, name))
for j, (name, month, color) in enumerate(mobilities):
    ymin = 0.70 + 0.032 * (j % 5)
    ymax = ymin + 0.05
    ax.axvline(month, color=color, linestyle="--", linewidth=1.2, alpha=0.9, ymin=ymin, ymax=ymax)
    level = 0  # months are distinct; no label conflicts
    ax.text(month, 5.30 + 0.24 * level, name, rotation=40, fontsize=6.5, color=color, ha="left", va="bottom")
ax.set_yticks([y for y, _ in ylabels])
ax.set_yticklabels([n for _, n in ylabels], fontsize=8)
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ax.set_xticks(range(1, 13))
ax.set_xticklabels(months, fontsize=8)
ax.set_xlim(0.5, 12.4)
ax.set_ylim(0.3, 6.9)
ax.axvline(2.5, color="black", linewidth=0.8)
ax.text(2.55, 0.45, "start 15 Mar", fontsize=7)
ax.axvline(12.0, color="black", linewidth=0.8)
ax.text(11.95, 0.45, "end 31 Dec", fontsize=7, ha="right")
ax.set_xlabel("2027 (civil year)", fontsize=9)
ax.set_title("PHC Bantou 2027 — work plan and mobilities (France-Cameroon corridor only; conf. costs = lab means)", fontsize=8.5)
ax.spines[["top","right"]].set_visible(False)
ax.grid(axis="x", linestyle=":", alpha=0.4)
fig.tight_layout()
fig.savefig("/home/taamangtchu/Documents/Malaria_codesV2/Bantou_PHC/figures/gantt_2027.pdf", bbox_inches="tight")
fig.savefig("/home/taamangtchu/Documents/Malaria_codesV2/Bantou_PHC/figures/gantt_2027.png", dpi=150, bbox_inches="tight")
print("gantt updated")
