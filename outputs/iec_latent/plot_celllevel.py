#!/usr/bin/env python
"""EXEC-1 figure — 2.5-axis structure: cross-system replication + CD8 guard."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = "/mnt/dados2/abel-tsc/repo/outputs/iec_latent"
r = json.load(open(f"{OUTDIR}/iec_celllevel_result.json"))

fig, ax = plt.subplots(1, 2, figsize=(12.5, 5))

# Panel A: pairwise axis correlations, two systems
pairs = ["A_persist__A_kill", "A_persist__A_resist", "A_kill__A_resist"]
labels = ["persist↔kill", "persist↔resist", "kill↔resist"]
atlas = [r["axis_axis_spearman"][p] for p in pairs]
mars = [r["marson_pseudobulk"][p.replace("A_", "").replace("__", "__")] for p in
        ["persist__kill", "persist__resist", "kill__resist"]]
x = np.arange(3); w = 0.38
ax[0].bar(x - w/2, atlas, w, label="CAR-T atlas (cell-level, n=455k)", color="#2b6cb0", edgecolor="black", lw=0.6)
ax[0].bar(x + w/2, mars, w, label="Marson (pseudobulk)", color="#dd6b20", edgecolor="black", lw=0.6)
ax[0].axhline(-0.5, ls="--", c="red", lw=1, label="entanglement threshold |ρ|=0.5")
ax[0].axhline(0.5, ls="--", c="red", lw=1)
ax[0].axhline(0, c="black", lw=0.6)
ax[0].set_xticks(x); ax[0].set_xticklabels(labels)
ax[0].set_ylabel("Spearman ρ between axes"); ax[0].set_ylim(-0.75, 0.75)
ax[0].set_title("A. 2.5-axis structure replicates across systems\n(persist clean; kill↔resist entangled ~−0.5 in BOTH)", fontsize=10)
ax[0].legend(fontsize=8, loc="upper right")

# Panel B: CD8 guard
g = r["cd8_guard"]
names = ["A_kill ↔ CD8-identity\n(raw)", "kill↔resist\n(raw)", "kill↔resist\n(partial, ctrl CD8)"]
vals = [g["kill_vs_cd8_raw"], r["axis_axis_spearman"]["A_kill__A_resist"], g["kill_vs_resist_partial_ctrl_cd8"]]
cols = ["#805ad5", "#e53e3e", "#c53030"]
ax[1].bar(np.arange(3), vals, color=cols, edgecolor="black", lw=0.6)
ax[1].axhline(0, c="black", lw=0.6)
for i, v in enumerate(vals):
    ax[1].text(i, v + (0.03 if v > 0 else -0.06), f"{v:.2f}", ha="center", fontsize=10)
ax[1].set_xticks(np.arange(3)); ax[1].set_xticklabels(names, fontsize=8)
ax[1].set_ylabel("Spearman ρ"); ax[1].set_ylim(-0.7, 0.75)
ax[1].set_title("B. CD8 guard: killing overlaps CD8-identity (0.57),\nbut kill↔resist entanglement survives CD8 control (−0.44)", fontsize=10)

plt.tight_layout()
plt.savefig(f"{OUTDIR}/iec_axis_decomposition.png", dpi=140, bbox_inches="tight")
print("[write] iec_axis_decomposition.png")
