#!/usr/bin/env python
"""Three-coherence decomposition — position vs Shesha (Raju 2026) and test independence.

Reproducibility of a perturbation has (at least) three coordinates. This tests whether they are
independent dimensions, conditional on effect magnitude M:
  * Sp = cell-to-cell directional coherence (Shesha's perturbation stability): mean cosine of
         single-cell shift vectors to the mean perturbation direction.
  * R  = cross-guide reproducibility: mean pairwise correlation of per-guide effect vectors.
  * S  = functional-axis specificity: |cos(mean effect, leave-marker-out IFN axis)|.
Substrate: Frangieh Perturb-CITE-seq (218k cells, 248 targets, multiple guides/gene, IFNγ axis).
CPU only. Outcome-agnostic: if the three collapse, that unifies them; if independent, that is a
richer controllership geometry than either group (Shesha / us) has shown alone.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from scipy.stats import rankdata, spearmanr

DATA = Path("/mnt/dados2/abel-tsc/data_public/external_perturb")
OUT = Path("/mnt/dados2/abel-tsc/repo/outputs/three_coherence")
OUT.mkdir(parents=True, exist_ok=True)
MIN_CELLS = 30
N_MOVED = 2000

def partial_spearman(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    def resid(a, b):
        B = np.c_[np.ones_like(b), b]
        c, *_ = np.linalg.lstsq(B, a, rcond=None)
        return a - B @ c
    ex, ey = resid(rx, rz), resid(ry, rz)
    return float(np.corrcoef(ex, ey)[0, 1])

print("[load]", flush=True)
A = ad.read_h5ad(DATA / "FrangiehIzar2021_RNA.h5ad")
o = A.obs
# keep singlets + control across conditions (control cells of both conditions build the axis)
keep = (o["nperts"].astype(float) == 1) | (o["perturbation"].astype(str) == "control")
A = A[keep.values].copy()
sc.pp.normalize_total(A, target_sum=1e6); sc.pp.log1p(A)
import scipy.sparse as sp
X = A.X if sp.issparse(A.X) else sp.csr_matrix(A.X)
genes = np.array(A.var_names)
tgt = A.obs["perturbation"].astype(str).values
sg = A.obs["sgRNA"].astype(str).values
cond = A.obs["perturbation_2"].astype(str).values
IFN = cond == "IFNγ"
print(f"[cells] {A.n_obs} singlets+control; IFNγ={int(IFN.sum())}", flush=True)

# leave-marker-out IFN axis = IFNγ - Control in CONTROL cells (same recipe as EXEC-2, non-circular)
cm = tgt == "control"
mu_ctrl = np.asarray(X[cm & IFN].mean(0)).ravel()             # baseline for effects (IFNγ control)
axis_full = mu_ctrl - np.asarray(X[cm & (cond == "Control")].mean(0)).ravel()

def dense(mask):
    return X[mask].toarray() if sp.issparse(X) else np.asarray(X[mask])

rows = []
targets = [t for t in np.unique(tgt) if t != "control"]
for t in targets:
    m = (tgt == t) & IFN            # measure perturbation effects within IFNγ
    if m.sum() < MIN_CELLS:
        continue
    Xt = dense(m)                       # cells x genes (dense slice)
    d = Xt.mean(0) - mu_ctrl            # mean perturbation direction
    M = float(np.linalg.norm(d))
    moved = np.argsort(np.abs(d))[-N_MOVED:]
    # Sp: cell-to-cell coherence on moved genes
    shifts = Xt[:, moved] - mu_ctrl[moved]
    dref = d[moved]
    num = shifts @ dref
    den = (np.linalg.norm(shifts, axis=1) * (np.linalg.norm(dref) + 1e-12)) + 1e-12
    Sp = float(np.mean(num / den))
    # S: axis-specificity (leave-marker-out)
    ax = axis_full.copy()
    if t in genes:
        ax[genes == t] = 0.0
    S = float(abs(np.dot(d[moved], ax[moved]) / (np.linalg.norm(d[moved]) * np.linalg.norm(ax[moved]) + 1e-12)))
    # R: cross-guide reproducibility
    guides = [u for u in np.unique(sg[m]) if u not in ("nan", "")]
    gvecs = []
    for gu in guides:
        gm = m & (sg == gu)
        if gm.sum() >= 10:
            gvecs.append(dense(gm).mean(0)[moved] - mu_ctrl[moved])
    if len(gvecs) >= 2:
        G = np.vstack(gvecs)
        C = np.corrcoef(G); iu = np.triu_indices(C.shape[0], 1)
        R = float(np.nanmean(C[iu]))
    else:
        R = np.nan
    rows.append({"gene": t, "M": M, "Sp": Sp, "R": R, "S": S, "n_cells": int(m.sum()), "n_guides": len(gvecs)})

df = pd.DataFrame(rows).set_index("gene")
df.to_csv(OUT / "three_coherence_scores.csv")
d2 = df.dropna(subset=["Sp", "R", "S", "M"])
print(f"[targets with all 3 coherences] {len(d2)}", flush=True)

cols = ["Sp", "R", "S", "M"]
corr = {a: {b: round(float(spearmanr(d2[a], d2[b])[0]), 3) for b in cols} for a in cols}
# partial correlations controlling magnitude M
part_M = {
    "Sp~R|M": round(partial_spearman(d2["Sp"], d2["R"], d2["M"]), 3),
    "Sp~S|M": round(partial_spearman(d2["Sp"], d2["S"], d2["M"]), 3),
    "R~S|M":  round(partial_spearman(d2["R"], d2["S"], d2["M"]), 3),
}
res = {"dataset": "Frangieh Perturb-CITE-seq (IFNγ)", "n_targets": int(len(d2)),
       "spearman_matrix": corr,
       "vs_magnitude": {c: corr[c]["M"] for c in ["Sp", "R", "S"]},
       "partial_controlling_M": part_M,
       "interpretation_rule": "coordinates are INDEPENDENT if pairwise |partial rho|M| < 0.5; "
                              "Shesha reports Sp strongly tracks magnitude (0.75-0.97) - we test whether "
                              "R and S add beyond magnitude and beyond Sp."}
json.dump(res, open(OUT / "three_coherence_result.json", "w"), indent=2)
print(json.dumps(res, indent=2))
