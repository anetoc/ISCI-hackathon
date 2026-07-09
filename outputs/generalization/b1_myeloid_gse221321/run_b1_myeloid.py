#!/usr/bin/env python
"""B1 far-test (PRE-REGISTERED in reports/PREREGISTRATION.md, tier B1) —
Conditional Controllability Invariant in a NON-T immune screen: THP-1 macrophages,
GSE221321 (Yao et al., Nat Biotechnol 2023), CRISPRi (KD) conventional arm.

Frozen protocol (skills/isci-controllership/kernel.py; same as Marson/Norman/Replogle):
  M = magnitude (L2 norm of pseudobulk effect vs matched controls)
  S = axis-specificity = |cos(effect, LPS/NF-kB inflammatory axis)|  (leave-marker-out)
  R = cross-REPLICATE reproducibility (Run_1 vs Run_2 effect correlation, leave-marker-out)
  residualize S,R on M -> C = mean(Sr,Rr) on detectable subset (M>=median)
  positives = canonical NF-kB/TLR regulators targeted in-screen
  negatives = expression_matched_negatives(target_baseMean + n_cells_target), 8/positive
  PASS iff bootstrap dAUPRC(M->M+C) CI excludes 0 AND conditional LR p<0.05 AND |rho(C,M)| small
       AND direction-aware guard (median residual C higher in positives).
Pre-registered PREDICTION: PASS (property is immune-wide). A FAIL tightens scope to T-cell.
CPU only. No GPU. Zero-shot to our labels.
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import anndata as ad
from scipy.stats import spearmanr, pearsonr

REPO = Path("/mnt/dados2/abel-tsc/repo")
sys.path.insert(0, str(REPO / "skills" / "isci-controllership"))
import kernel
OUT = REPO / "outputs/generalization/b1_myeloid_gse221321"
OUT.mkdir(parents=True, exist_ok=True)
H5AD = REPO / "data/gse221321/GSM6858449_KD_conventional.h5ad"
SEED = 0

# ---- functional axis: LPS / NF-kB inflammatory response (downstream effectors) ----
AXIS_UP = ["TNF","IL1B","IL1A","IL6","IL12B","IL23A","CXCL8","IL8","CXCL1","CXCL2","CXCL3",
           "CXCL10","CXCL11","CCL2","CCL3","CCL4","CCL5","CCL20","CCL8","NFKBIA","NFKBIZ",
           "TNFAIP3","TNFAIP2","PTGS2","SOD2","BIRC3","ICAM1","CD40","CD80","CD83","TRAF1",
           "IER3","PLAUR","SERPINB2","IL1RN","G0S2","CCL7","CXCL5","EBI3","INHBA"]
# canonical NF-kB / TLR signaling REGULATORS (upstream) = positives
POS = ["MYD88","IRAK1","IRAK4","TRAF6","MAP3K7","CHUK","IKBKB","IKBKG","RELA","NFKB1","NFKB2",
       "REL","RELB","NFKBIA","NFKBIB","TLR4","TLR2","TNF","TNFAIP3","IRF1","STAT1","TAB1","TAB2",
       "RIPK1","TRAF2","TNFRSF1A","TICAM1","TIRAP","UBE2N","MAP3K8"]

print("[load]", flush=True)
A = ad.read_h5ad(H5AD).to_memory() if ad.read_h5ad(H5AD, backed="r").isbacked else ad.read_h5ad(H5AD)
A.var_names = A.var["features"].astype(str).values
A.var_names_make_unique()
X = A.X
if hasattr(X, "toarray"):
    X = X.toarray()
X = np.asarray(X, dtype=np.float32)
genes = np.array(A.var_names); gidx = {g: i for i, g in enumerate(genes)}
pert = A.obs["Guides_collapsed_by_gene"].astype(str).values
rep = A.obs["Biological_replicate"].astype(str).values
print(f"[cells] {X.shape}, reps={sorted(set(rep))}", flush=True)

CTRL = {"non-targeting", "safe-targeting"}
is_ctrl = np.isin(pert, list(CTRL))
# single-gene perturbations = no combo '--', not a control, target measured
def single_targets():
    out = []
    for p in pd.unique(pert):
        if "--" in p or p in CTRL:
            continue
        out.append(p)
    return out
targets = single_targets()
print(f"[targets] {len(targets)} single-gene perturbations; controls={int(is_ctrl.sum())} cells", flush=True)

reps = sorted(set(rep))
# control pseudobulk per replicate
ctrl_pb = {r: X[(is_ctrl) & (rep == r)].mean(0) for r in reps}
ctrl_all = X[is_ctrl].mean(0)          # for target_baseMean
axis_idx = np.array([gidx[g] for g in AXIS_UP if g in gidx])
print(f"[axis] {len(axis_idx)}/{len(set(AXIS_UP))} inflammatory axis genes measured", flush=True)

rows = []
for g in targets:
    mask = pert == g
    n_cells = int(mask.sum())
    if n_cells < 20:
        continue
    # per-replicate effect vs matched-replicate control
    eff_r = {}
    for r in reps:
        m = mask & (rep == r)
        if m.sum() < 5:
            eff_r[r] = None; continue
        eff_r[r] = X[m].mean(0) - ctrl_pb[r]
    eff = np.nanmean([e for e in eff_r.values() if e is not None], axis=0)
    # leave-marker-out: zero the perturbed gene's own coordinate
    lmo = eff.copy()
    if g in gidx:
        lmo[gidx[g]] = 0.0
    # magnitude
    M = float(np.linalg.norm(lmo))
    # axis-specificity = |cos(effect, axis)| with axis = +1 on inflammatory genes (self excluded)
    axg = np.array([i for i in axis_idx if i != gidx.get(g, -1)])
    av = np.zeros_like(lmo); av[axg] = 1.0
    denom = (np.linalg.norm(lmo) * np.linalg.norm(av))
    S = float(abs(float(lmo @ av) / denom)) if denom > 0 else np.nan
    # reproducibility = cross-replicate effect correlation (leave-marker-out)
    if eff_r[reps[0]] is not None and eff_r[reps[1]] is not None:
        e1, e2 = eff_r[reps[0]].copy(), eff_r[reps[1]].copy()
        if g in gidx:
            e1[gidx[g]] = 0.0; e2[gidx[g]] = 0.0
        R = float(pearsonr(e1, e2)[0])
    else:
        R = np.nan
    target_baseMean = float(ctrl_all[gidx[g]]) if g in gidx else np.nan
    rows.append({"gene": g, "magnitude": M, "S": S, "R": R,
                 "target_baseMean": target_baseMean, "n_cells_target": n_cells})

feat = pd.DataFrame(rows).set_index("gene").dropna(subset=["magnitude", "S", "R"])
print(f"[feat] {len(feat)} perturbations with complete M,S,R", flush=True)

# detectable gate (magnitude >= median) + C = mean of magnitude-residualized S,R percentiles
med = feat["magnitude"].median()
feat["detectable"] = feat["magnitude"] >= med
C = kernel.controllership_score(feat, components=["S", "R"], method="orthogonal",
                                magnitude_col="magnitude", detectable_floor=True)
feat["C"] = C
det = feat[feat["C"].notna()].copy()

positives = [g for g in POS if g in det.index]
# negatives: expression/power-matched from non-positive detectable perturbations (locked helper)
obs_for_match = det.reset_index()[["gene", "target_baseMean", "n_cells_target"]]
negatives = kernel.expression_matched_negatives(
    positives, obs_for_match, gene_col="gene",
    match_cols=["target_baseMean", "n_cells_target"], n_per_positive=8,
    exclude=set(positives))
negatives = [g for g in negatives if g in det.index]
print(f"[labels] positives={len(positives)} negatives={len(negatives)} (detectable set n={len(det)})", flush=True)

# ---- adjudication ----
rho_CM = float(spearmanr(feat["C"].dropna(), feat.loc[feat["C"].notna(), "magnitude"])[0])
lr = kernel.conditional_lr_test(det, positives, negatives, base_col="magnitude",
                                feature_cols=["S", "R", "C"])
boot = kernel.bootstrap_auprc_gain(det, positives, negatives, base_col="magnitude",
                                   score_col="C", n_boot=1000, seed=SEED)
# direction-aware guard: residual C should be HIGHER in positives than matched negatives
med_pos = float(det.loc[positives, "C"].median())
med_neg = float(det.loc[negatives, "C"].median())
direction_ok = med_pos > med_neg
lr_C = lr[lr.feature == "C"].iloc[0]
ci = boot["ci95"]

verdict = "PASS" if (ci[0] > 0 and float(lr_C.p_value) < 0.05 and abs(rho_CM) < 0.3
                     and direction_ok) else "FAIL"
# near-miss flag: same sign but CI crosses 0 or LR n.s.
near = (verdict == "FAIL" and boot["gain"] > 0 and direction_ok
        and (ci[0] <= 0 or float(lr_C.p_value) >= 0.05))

result = {
    "id": "b1_myeloid_gse221321",
    "label": "THP-1 macrophage (GSE221321, KD/CRISPRi)",
    "system": "immune (non-T: myeloid)",
    "perturbation": "CRISPRi (LPS-stimulated)",
    "axis": "LPS / NF-kB inflammatory response",
    "n_pos": len(positives), "n_neg": len(negatives), "n_detectable": int(len(det)),
    "n_perturbations_total": int(len(feat)),
    "delta_auprc": round(boot["gain"], 3), "base_auprc": round(boot["base_auprc"], 3),
    "full_auprc": round(boot["full_auprc"], 3),
    "ci_lo": round(ci[0], 3), "ci_hi": round(ci[1], 3), "p_gain_gt0": boot["p_gain_gt0"],
    "lr_p_C": float(lr_C.p_value), "lr_coef_C": float(lr_C.coef),
    "lr_p_S": float(lr[lr.feature == "S"].iloc[0].p_value),
    "lr_p_R": float(lr[lr.feature == "R"].iloc[0].p_value),
    "spearman_mag": round(rho_CM, 3),
    "direction_aware": {"median_C_pos": round(med_pos, 3), "median_C_neg": round(med_neg, 3),
                        "positives_higher": bool(direction_ok)},
    "verdict": verdict + (" (near-miss)" if near else ""),
    "prereg_prediction": "PASS (immune-wide)",
    "prereg_outcome_meaning": ("PASS => property is immune-wide, not T-cell-specific; "
                               "FAIL => tightens scope to T-cell state controllability"),
    "positives": positives, "negatives": negatives,
    "provenance": {"dataset": "GSE221321 GSM6858449 KD_conventional", "cells": list(X.shape),
                   "reps": reps, "seed": SEED, "compute": "CPU", "method": "kernel.py (locked)"},
}
json.dump(result, open(OUT / "cci_result.json", "w"), indent=2)
feat.to_csv(OUT / "b1_myeloid_features.csv")
print("\n==== B1 MYELOID (GSE221321) ====")
print(f"positives={len(positives)} negatives={len(negatives)} detectable={len(det)}")
print(f"dAUPRC {boot['gain']:+.3f} [{ci[0]:+.3f},{ci[1]:+.3f}]  base {boot['base_auprc']:.3f} -> full {boot['full_auprc']:.3f}")
print(f"LR p(C)={float(lr_C.p_value):.3g} coef={float(lr_C.coef):+.2f} | S p={result['lr_p_S']:.3g} R p={result['lr_p_R']:.3g}")
print(f"Spearman(C,M)={rho_CM:+.3f} | direction pos>neg={direction_ok} ({med_pos:.3f} vs {med_neg:.3f})")
print(f"VERDICT: {result['verdict']}  (pre-registered prediction: PASS)")
