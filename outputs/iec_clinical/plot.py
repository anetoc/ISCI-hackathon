#!/usr/bin/env python
"""Brief 04 step 3 — figure: CV-AUROC per axis vs baselines (with CI) + axis-by-response strip."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = "/mnt/dados2/abel-tsc/repo/outputs/iec_clinical"
res = json.load(open(f"{OUTDIR}/cv_results.json"))
r = res["all"]
t = pd.read_csv(f"{OUTDIR}/patient_axis_scores_all.csv")

fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))

# --- panel A: leave-study-out AUROC, axes vs baselines, with bootstrap CI ---
items, aucs, los, his, colors = [], [], [], [], []
for key, d in r["tests"].items():
    lso = d["leave_study_out"]
    items.append(key.replace("__", "\n")); aucs.append(lso["auroc"])
    los.append(lso["auroc"] - lso["ci"][0]); his.append(lso["ci"][1] - lso["auroc"])
    colors.append("#2b6cb0" if key.startswith("A_persist") else "#805ad5")
for b in ["b_total_counts", "b_cd8_frac", "b_n_cells", "b_n_features"]:
    lso = r["baselines"][b]["leave_study_out"]
    items.append(b.replace("b_", "base:\n")); aucs.append(lso["auroc"])
    los.append(0); his.append(0); colors.append("#a0aec0")

xpos = np.arange(len(items))
ax[0].bar(xpos, aucs, color=colors, edgecolor="black", linewidth=0.6)
ax[0].errorbar(xpos[:4], aucs[:4], yerr=[los[:4], his[:4]], fmt="none", ecolor="black", capsize=4, lw=1.2)
ax[0].axhline(0.5, ls="--", c="red", lw=1, label="chance")
ax[0].set_xticks(xpos); ax[0].set_xticklabels(items, fontsize=8, rotation=0)
ax[0].set_ylabel("leave-one-STUDY-out CV-AUROC (pooled OOF)")
ax[0].set_ylim(0, 1); ax[0].set_title(f"A. Response prediction — PRIMARY test\n(n={r['n_patients']}: {r['n_R']}R/{r['n_NR']}NR, {r['n_studies']} studies)", fontsize=10)
ax[0].legend(fontsize=8)

# --- panel B: A_persist patient mean by response ---
for lab, sub, c in [("NR", t[t.R == 0], "#e53e3e"), ("R (CR/PR)", t[t.R == 1], "#38a169")]:
    x = np.full(len(sub), 0 if lab == "NR" else 1) + np.random.default_rng(1).normal(0, 0.06, len(sub))
    ax[1].scatter(x, sub["A_persist__mean"], c=c, s=28, alpha=0.7, edgecolor="black", linewidth=0.4, label=lab)
    ax[1].hlines(sub["A_persist__mean"].median(), (0 if lab == "NR" else 1) - 0.2, (0 if lab == "NR" else 1) + 0.2, colors="black", lw=2)
ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["NR", "R (CR/PR)"])
ax[1].set_ylabel("A_persist (patient mean)"); ax[1].set_title("B. Primary axis by response (patient level)", fontsize=10)
ax[1].legend(fontsize=8)

plt.tight_layout()
plt.savefig(f"{OUTDIR}/iec_prediction.png", dpi=140, bbox_inches="tight")
print("[write] iec_prediction.png")
