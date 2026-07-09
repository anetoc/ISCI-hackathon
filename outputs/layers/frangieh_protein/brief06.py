#!/usr/bin/env python
"""Brief 06 (Layer 1) — Frangieh protein controllership slice via totalVI (CPU).

Fills T[gene, immune_evasion, Frangieh, PROTEIN]. Same locked CondInfo operator, protein substrate.
totalVI trains in minibatch -> CPU is fine (accelerator='cpu'); subsample ~80-100k cells stratified
by perturbation (power is set by ~10 positives, not cell count). Protein feature from DENOISED
protein (never re-derived from RNA). Headline = does C_prot add over C_rna given magnitude.
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from scipy.stats import rankdata, spearmanr, mannwhitneyu, chi2
import statsmodels.api as sm

REPO = Path("/mnt/dados2/abel-tsc/repo")
DATA = Path("/mnt/dados2/abel-tsc/data_public/external_perturb")
OUT = REPO / "outputs" / "layers" / "frangieh_protein"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO / "skills" / "isci-controllership"))
import kernel as H

CAP = 400            # stratified cap per perturbation
N_HVG = 4000
SEED = 0
rng = np.random.default_rng(SEED)

def resid_on(x, m):
    rx, rm = rankdata(x), rankdata(m)
    B = np.c_[np.ones_like(rm), rm]
    c, *_ = np.linalg.lstsq(B, rx, rcond=None)
    return rx - B @ c
def pct(x):
    return rankdata(x) / len(x)

# ---------- build paired AnnData ----------
print("[load] RNA + protein", flush=True)
R = ad.read_h5ad(DATA / "FrangiehIzar2021_RNA.h5ad")
P = ad.read_h5ad(DATA / "FrangiehIzar2021_protein.h5ad")
R = R[P.obs_names].copy()                       # align (identical set, enforce order)
Pdf = pd.DataFrame(P.X.toarray() if hasattr(P.X, "toarray") else np.asarray(P.X),
                   index=P.obs_names, columns=[str(v) for v in P.var_names])
R.layers["counts"] = R.X.copy()
R.obsm["protein_expression"] = Pdf.loc[R.obs_names]

# singlets + control only (clean perturbation assignment)
keep = (R.obs["nperts"].astype(float) == 1) | (R.obs["perturbation"].astype(str) == "control")
R = R[keep.values].copy()
print(f"[cells] singlets+control = {R.n_obs}", flush=True)

# ---------- stratified subsample ~80-100k ----------
tgt = R.obs["perturbation"].astype(str).values
idx_keep = []
percounts = {}
for t in np.unique(tgt):
    ii = np.where(tgt == t)[0]
    if len(ii) > CAP:
        ii = rng.choice(ii, CAP, replace=False)
    idx_keep.append(ii); percounts[t] = int(len(ii))
idx_keep = np.sort(np.concatenate(idx_keep))
R = R[idx_keep].copy()
print(f"[subsample] {R.n_obs} cells kept (cap {CAP}/perturbation)", flush=True)

# HVGs for totalVI (RNA); keep counts layer intact
Rlog = R.copy(); sc.pp.normalize_total(Rlog, target_sum=1e4); sc.pp.log1p(Rlog)
sc.pp.highly_variable_genes(Rlog, n_top_genes=N_HVG, flavor="seurat")
R = R[:, Rlog.var["highly_variable"].values].copy()   # R.X is already raw counts on HVGs (never normalized)
print(f"[hvg] {R.n_vars} genes; proteins {R.obsm['protein_expression'].shape[1]}; X max={float(R.X.max()):.0f}", flush=True)

# ---------- totalVI on CPU ----------
import scvi
scvi.settings.seed = SEED
scvi.model.TOTALVI.setup_anndata(R, batch_key="perturbation_2", protein_expression_obsm_key="protein_expression")
model = scvi.model.TOTALVI(R)
print("[train] totalVI CPU (early-stopping, max 200)", flush=True)
model.train(accelerator="cpu", max_epochs=200, early_stopping=True)
n_epochs = len(model.history["elbo_train"]) if "elbo_train" in model.history else None
_, pro = model.get_normalized_expression(R, n_samples=25, return_mean=True)   # denoised protein
pro = pd.DataFrame(np.asarray(pro), index=R.obs_names, columns=R.obsm["protein_expression"].columns)
model.save(str(OUT / "totalvi_model"), overwrite=True)
print(f"[totalVI] done; epochs={n_epochs}", flush=True)

# ---------- protein CondInfo features (denoised protein) ----------
prot = np.array(pro.columns)
iso = np.array([("IgG" in p) for p in prot]); keepp = ~iso
Xp = pro.values                                   # denoised protein, cells x proteins
o = R.obs
tg = o["perturbation"].astype(str).values
cond = o["perturbation_2"].astype(str).values
cm = tg == "control"
# leave-marker-out immune-evasion axis = IFNγ - Control in control cells (denoised protein)
axis = Xp[cm & (cond == "IFNγ")][:, keepp].mean(0) - Xp[cm & (cond == "Control")][:, keepp].mean(0)

rows = []
conds = ["Control", "IFNγ", "Co-culture"]
for t in np.unique(tg):
    if t == "control":
        continue
    m = tg == t
    if m.sum() < 30:
        continue
    # mean effect across conditions (target - control within each condition), + per-condition for R
    effs = []
    for c in conds:
        mt = m & (cond == c); mc = cm & (cond == c)
        if mt.sum() >= 10 and mc.sum() >= 10:
            effs.append(Xp[mt][:, keepp].mean(0) - Xp[mc][:, keepp].mean(0))
    if not effs:
        continue
    E = np.vstack(effs); d = E.mean(0)
    Mp = float(np.linalg.norm(d))
    ax = axis.copy()
    Sp = float(abs(np.dot(d, ax) / (np.linalg.norm(d) * np.linalg.norm(ax) + 1e-12)))
    if E.shape[0] >= 2:
        C = np.corrcoef(E); iu = np.triu_indices(C.shape[0], 1); Rp = float(np.nanmean(C[iu]))
    else:
        Rp = np.nan
    rows.append({"gene": t, "M_prot": Mp, "S_prot": Sp, "R_prot": Rp, "n_cells": int(m.sum())})
df = pd.DataFrame(rows).set_index("gene")

# residualize + C_prot on the detectable subset
det = df["M_prot"] >= df["M_prot"].median()
sub = df[det].copy()
sub["S_resid"] = resid_on(sub["S_prot"].fillna(sub["S_prot"].median()), sub["M_prot"])
sub["R_resid"] = resid_on(sub["R_prot"].fillna(sub["R_prot"].median()), sub["M_prot"])
sub["C_prot"] = (pct(sub["S_resid"]) + pct(sub["R_resid"])) / 2

# ---------- positives + matched negatives + CondInfo ----------
POS = ["B2M", "HLA-B", "HLA-E", "IFNGR1", "IFNGR2", "IRF3", "JAK1", "JAK2", "STAT1", "TAPBP", "HLA-A", "HLA-C", "CD274"]
pos = [g for g in POS if g in sub.index]
obs_match = sub.reset_index()[["gene", "M_prot", "n_cells"]].rename(columns={"M_prot": "magnitude"})
negs = H.expression_matched_negatives(pos, obs_match, gene_col="gene",
                                      match_cols=["magnitude", "n_cells"], n_per_positive=3, exclude=set(POS))
negs = [g for g in negs if g in sub.index]

feat = sub[["M_prot", "C_prot", "S_resid", "R_resid"]].rename(columns={"M_prot": "magnitude"})
res = {"id": "frangieh_protein", "system": "immune", "modality": "PROTEIN_coherence",
       "axis": "immune_evasion", "n_pos": len(pos), "n_neg": len(negs),
       "n_cells_used": int(R.n_obs), "totalvi_epochs": n_epochs,
       "panel": [str(p) for p in prot], "compute": "CPU (accelerator=cpu), subsample cap 400/pert"}

if len(pos) >= 5 and len(negs) >= 5:
    lr = H.conditional_lr_test(feat, pos, negs, base_col="magnitude", feature_cols=["C_prot", "S_resid", "R_resid"])
    boot = H.bootstrap_auprc_gain(feat, pos, negs, base_col="magnitude", feature_cols=["C_prot"], n_boot=1000, seed=SEED)
    rho_cm = float(spearmanr(sub["C_prot"], sub["magnitude" if "magnitude" in sub else "M_prot"])[0]) if False else float(spearmanr(sub["C_prot"], sub["M_prot"])[0])
    lrC = lr[lr["feature"] == "C_prot"].iloc[0]
    # ---- incremental over RNA ----
    rna = pd.read_csv(REPO / "outputs" / "external_tcell" / "frangieh_perturbcite_scores.csv").set_index("gene")
    J = sub.join(rna[["C", "magnitude"]].rename(columns={"C": "C_rna", "magnitude": "M_rna"}), how="inner").dropna(subset=["C_rna"])
    Ji = [g for g in pos + negs if g in J.index]
    y = np.array([1 if g in pos else 0 for g in Ji])
    def lr_add(base_cols, add):
        X0 = sm.add_constant(J.loc[Ji, base_cols].values.astype(float))
        X1 = sm.add_constant(J.loc[Ji, base_cols + [add]].values.astype(float))
        m0 = sm.Logit(y, X0).fit(disp=0); m1 = sm.Logit(y, X1).fit(disp=0)
        stat = 2 * (m1.llf - m0.llf); return float(stat), float(chi2.sf(stat, 1))
    sp_pr = float(spearmanr(J["C_prot"], J["C_rna"])[0])
    lr_stat, lr_p = lr_add(["M_prot", "C_rna"], "C_prot")
    # DIRECTION-AWARE: a controllership PASS requires positives to have HIGHER residual C than
    # negatives (as in RNA/Marson). bootstrap_auprc_gain is direction-agnostic (LR learns the sign),
    # so a strong gain with positives LOWER on C is an INVERTED result, NOT a controllership PASS.
    pos_med = float(sub.loc[pos, "C_prot"].median()); neg_med = float(sub.loc[negs, "C_prot"].median())
    positive_direction = pos_med > neg_med
    res.update({
        "delta_auprc": boot["gain"], "ci_lo": boot["ci95"][0], "ci_hi": boot["ci95"][1],
        "p_gain_gt0": boot["p_gain_gt0"], "base_auprc": boot["base_auprc"], "full_auprc": boot["full_auprc"],
        "spearman_C_magnitude": rho_cm, "lr_Cprot_over_magnitude_p": float(lrC["p_value"]),
        "spearman_protein_vs_rna": sp_pr,
        "lr_protein_given_rna_and_magnitude": lr_p, "lr_protein_given_rna_and_magnitude_stat": lr_stat,
        "Cprot_pos_median": pos_med, "Cprot_neg_median": neg_med,
        "direction": "positives_higher" if positive_direction else "INVERTED_positives_lower",
        "auto_verdict_direction_agnostic": ("PASS" if (boot["ci95"][0] > 0 and bool(lrC["adds"]) and abs(rho_cm) < 0.3) else "FAIL"),
        "verdict": ("PASS" if (positive_direction and boot["ci95"][0] > 0 and bool(lrC["adds"]) and abs(rho_cm) < 0.3) else "FAIL"),
        "adds_over_rna": bool(lr_p < 0.05 and positive_direction),
        "top5_protein_controllers": list(sub["C_prot"].sort_values(ascending=False).head(5).index),
    })
else:
    res["verdict"] = "NOT-EVALUABLE"; res["reason"] = f"pos={len(pos)} neg={len(negs)}"

sub.join(pd.read_csv(REPO/"outputs"/"external_tcell"/"frangieh_perturbcite_scores.csv").set_index("gene")[["C"]].rename(columns={"C":"C_rna"}), how="left").to_csv(OUT / "protein_scores.csv")
json.dump({"per_perturbation_counts": percounts, **res}, open(OUT / "protein_cci_result.json", "w"), indent=2, default=str)
print(json.dumps({k: v for k, v in res.items() if k != "panel"}, indent=2, default=str))
print("[done]")
