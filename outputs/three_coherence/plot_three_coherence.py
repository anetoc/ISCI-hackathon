#!/usr/bin/env python
"""Figure: Shesha's Sp collapses onto magnitude; our R/S are the orthogonal plane."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/mnt/dados2/abel-tsc/repo/outputs/three_coherence"
r = json.load(open(f"{OUT}/three_coherence_result.json"))
df = pd.read_csv(f"{OUT}/three_coherence_scores.csv").dropna(subset=["Sp", "R", "S", "M"])

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))

# A: |Spearman vs magnitude| for each coordinate
vm = r["vs_magnitude"]
names = ["Sp\n(Shesha\ncell-to-cell)", "S\n(axis-\nspecificity)", "R\n(cross-guide\nreproducibility)"]
vals = [vm["Sp"], vm["S"], vm["R"]]
cols = ["#a0aec0", "#2b6cb0", "#2f855a"]
ax[0].bar(range(3), np.abs(vals), color=cols, edgecolor="black", lw=0.6)
for i, v in enumerate(vals):
    ax[0].text(i, abs(v) + 0.02, f"{v:.2f}", ha="center", fontsize=11)
ax[0].axhline(0.3, ls="--", c="red", lw=1, label="magnitude-proxy threshold 0.3")
ax[0].set_xticks(range(3)); ax[0].set_xticklabels(names, fontsize=8)
ax[0].set_ylabel("|Spearman ρ| vs effect magnitude"); ax[0].set_ylim(0, 1.05)
ax[0].set_title("A. Shesha's coherence IS magnitude (0.97);\nour R/S are magnitude-orthogonal", fontsize=10)
ax[0].legend(fontsize=8)

# B: Sp vs M (tight line)
ax[1].scatter(df["M"], df["Sp"], s=16, alpha=0.5, c="#a0aec0", edgecolor="black", lw=0.3)
ax[1].set_xlabel("effect magnitude M"); ax[1].set_ylabel("Sp (cell-to-cell coherence)")
ax[1].set_title(f"B. Sp ~ magnitude (ρ={vm['Sp']:.2f})\n= Shesha's finding, replicated", fontsize=10)

# C: R vs M (flat cloud)
ax[2].scatter(df["M"], df["R"], s=16, alpha=0.5, c="#2f855a", edgecolor="black", lw=0.3)
ax[2].set_xlabel("effect magnitude M"); ax[2].set_ylabel("R (cross-guide reproducibility)")
ax[2].set_title(f"C. R ⟂ magnitude (ρ={vm['R']:.2f})\n= our orthogonal coordinate", fontsize=10)

plt.tight_layout()
plt.savefig(f"{OUT}/three_coherence.png", dpi=140, bbox_inches="tight")
print("[write] three_coherence.png")
