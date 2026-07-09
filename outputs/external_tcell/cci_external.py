#!/usr/bin/env python
"""Reusable CCI test on an external Perturb-seq h5ad (Schmidt-recipe, exact).

Replicates the protocol used for the committed Schmidt/Norman/Replogle generalization runs
(outputs/generalization/near_immune_cci_report.md §2), reusing the LOCKED kernel helpers for
the final statistics. Parameterized by a dataset config dict; no new science.

Steps:
 1. singlets + control; CPM+log1p.
 2. pseudobulk per (target x sample/well), >=MIN_CELLS each.
 3. leave-marker-out state axis from control cells (treatment - baseline), top/bottom 200 genes.
 4. M = L2 norm of mean well effect vector (target - well-matched control).
 5. S = |cos(effect, signed axis)| on axis genes; R = mean pairwise Pearson of per-well effects.
 6. residualize S,R on M (rank regression) -> S_resid,R_resid; C = mean residual percentiles.
 7. detectable gate (M >= median); magnitude-matched negatives via locked helper.
 8. conditional LR (C over M) + bootstrap dAUPRC(M -> M+C).
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from scipy.stats import rankdata, spearmanr, mannwhitneyu

REPO = Path("/mnt/dados2/abel-tsc/repo")
sys.path.insert(0, str(REPO / "skills" / "isci-controllership"))
import kernel as H

MIN_CELLS = 25
N_AXIS = 200
N_MOVED = 2000

def resid_on(x, m):
    """rank-regression residual of x on m (both rank-transformed)."""
    rx, rm = rankdata(x), rankdata(m)
    A = np.c_[np.ones_like(rm), rm]
    coef, *_ = np.linalg.lstsq(A, rx, rcond=None)
    return rx - A @ coef

def pct(x):
    return rankdata(x) / len(x)

def run(cfg):
    A = ad.read_h5ad(cfg["path"])
    o = A.obs
    tcol, scol = cfg["target_col"], cfg["sample_col"]
    ctrl = cfg["control_label"]
    # singlets + controls (controls carry nperts==0, must be kept for the baseline)
    if "nperts" in o and cfg.get("singlets", True) and (o["nperts"] == 1).any():
        keep = (o["nperts"].astype(float) == 1) | (o[tcol].astype(str) == ctrl)
        A = A[keep.values].copy()
    # restrict to analysis condition if given
    if cfg.get("condition_col") and cfg.get("analysis_condition"):
        A = A[A.obs[cfg["condition_col"]].astype(str) == cfg["analysis_condition"]].copy()
    o = A.obs
    # CPM + log1p (X assumed raw counts); keep X SPARSE (avoid densifying 200k x 24k)
    sc.pp.normalize_total(A, target_sum=1e6); sc.pp.log1p(A)
    genes = np.array(A.var_names)
    import scipy.sparse as sp
    X = A.X if sp.issparse(A.X) else sp.csr_matrix(A.X)
    def gmean(mask):  # dense 1-D mean over selected rows (0-vector if empty)
        if int(np.asarray(mask).sum()) == 0:
            return np.zeros(X.shape[1])
        return np.asarray(X[mask].mean(0)).ravel()
    tgt = o[tcol].astype(str).values
    smp = o[scol].astype(str).values

    # base expression per gene (for matching)
    base_expr_gene = np.asarray(X.mean(0)).ravel()

    # --- pseudobulk per (target, sample) with >= MIN_CELLS ---
    prof = {}   # (target, sample) -> mean log-CPM vector
    ncells = {}
    for t in np.unique(tgt):
        for s in np.unique(smp):
            m = (tgt == t) & (smp == s)
            if m.sum() >= MIN_CELLS:
                prof[(t, s)] = gmean(m); ncells[(t, s)] = int(m.sum())
    samples = sorted(set(s for (_, s) in prof))
    targets = sorted(set(t for (t, _) in prof if t != ctrl))

    # --- state axis (leave-marker-out) from control cells: treatment - baseline ---
    axis_full = None
    if cfg.get("axis_condition_col"):
        acc, base_lab, trt_lab = cfg["axis_condition_col"], cfg["axis_baseline"], cfg["axis_treatment"]
        cm = (tgt == ctrl)
        cbase = gmean(cm & (o[acc].astype(str).values == base_lab))
        ctrt = gmean(cm & (o[acc].astype(str).values == trt_lab))
        axis_full = ctrt - cbase
    else:  # axis = control profile spread (fallback: mean control effect direction unavailable)
        axis_full = None

    # --- per-target effect vectors (target - well-matched control), M, S, R ---
    rows = []
    for t in targets:
        eff_by_s = []
        for s in samples:
            if (t, s) in prof and (ctrl, s) in prof:
                eff_by_s.append(prof[(t, s)] - prof[(ctrl, s)])
        if len(eff_by_s) == 0:
            continue
        E = np.vstack(eff_by_s)            # wells x genes
        mean_eff = E.mean(0)
        M = float(np.linalg.norm(mean_eff))
        # S: |cos| with signed axis on axis genes (leave-marker-out)
        if axis_full is not None:
            ax = axis_full.copy()
            if t in genes:                 # leave-marker-out
                ax[genes == t] = 0.0
            top = np.argsort(ax)[-N_AXIS:]; bot = np.argsort(ax)[:N_AXIS]
            idx = np.concatenate([top, bot])
            v, a = mean_eff[idx], ax[idx]
            S = float(abs(np.dot(v, a) / (np.linalg.norm(v) * np.linalg.norm(a) + 1e-12)))
        else:
            S = np.nan
        # R: mean pairwise Pearson of per-well effects on top moved genes
        if E.shape[0] >= 2:
            moved = np.argsort(np.abs(mean_eff))[-N_MOVED:]
            C_ = np.corrcoef(E[:, moved])
            iu = np.triu_indices(C_.shape[0], 1)
            R = float(np.nanmean(C_[iu]))
        else:
            R = np.nan
        # base expression of the target's neighborhood: mean expr across genes of the effect (power proxy)
        n_de = int((np.abs(mean_eff) > 1.0).sum())
        base_expr = float(base_expr_gene[genes == t][0]) if t in genes else float(base_expr_gene.mean())
        n_cells = int(np.mean([ncells[(t, s)] for s in samples if (t, s) in ncells]))
        rows.append({"gene": t, "magnitude": M, "S": S, "R": R, "n_de": n_de,
                     "base_expr": base_expr, "n_cells": n_cells, "n_wells": E.shape[0]})
    df = pd.DataFrame(rows).set_index("gene")

    # --- residualize + C ---
    det = df["magnitude"] >= df["magnitude"].median()
    df["detectable"] = det
    sub = df[det].copy()
    sub["S_resid"] = resid_on(sub["S"].fillna(sub["S"].median()), sub["magnitude"])
    sub["R_resid"] = resid_on(sub["R"].fillna(sub["R"].median()), sub["magnitude"])
    sub["C"] = (pct(sub["S_resid"]) + pct(sub["R_resid"])) / 2
    for c in ["S_resid", "R_resid", "C"]:
        df.loc[sub.index, c] = sub[c]

    # --- positives / matched negatives ---
    pos_all = [g for g in cfg["positives"] if g in sub.index]
    obs_match = sub.reset_index()[["gene", "magnitude", "base_expr", "n_cells"]]
    negs = H.expression_matched_negatives(pos_all, obs_match, gene_col="gene",
                                          match_cols=["magnitude", "base_expr", "n_cells"],
                                          n_per_positive=cfg.get("n_per_pos", 3), exclude=set(cfg["positives"]))
    negs = [g for g in negs if g in sub.index]

    result = {"dataset": cfg["id"], "label": cfg["label"], "system": cfg["system"],
              "n_targets": int(len(df)), "n_detectable": int(det.sum()),
              "n_positives": len(pos_all), "n_negatives": len(negs),
              "positives": pos_all, "negatives": negs}

    if len(pos_all) < cfg.get("min_pos", 5) or len(negs) < cfg.get("min_neg", 5):
        result["verdict"] = "NOT-EVALUABLE"
        result["reason"] = f"insufficient positive/negative contrast (pos={len(pos_all)}, neg={len(negs)}); need >= {cfg.get('min_pos',5)}/{cfg.get('min_neg',5)}"
    else:
        feat = sub[["magnitude", "C", "S_resid", "R_resid"]].copy()
        # magnitude balance check
        mw = mannwhitneyu(sub.loc[pos_all, "magnitude"], sub.loc[negs, "magnitude"]).pvalue
        lr = H.conditional_lr_test(feat, pos_all, negs, base_col="magnitude", feature_cols=["C", "S_resid", "R_resid"])
        boot = H.bootstrap_auprc_gain(feat, pos_all, negs, base_col="magnitude", feature_cols=["C"], n_boot=1000, seed=0)
        rho_cm = float(spearmanr(sub["C"], sub["magnitude"])[0])
        lr_C = lr[lr["feature"] == "C"].iloc[0]
        result.update({
            "magnitude_balance_MW_p": float(mw),
            "spearman_C_magnitude": rho_cm,
            "lr": lr.to_dict(orient="records"),
            "bootstrap_dAUPRC_C": boot,
            "verdict": ("PASS" if (boot["ci95"][0] > 0 and bool(lr_C["adds"]) and abs(rho_cm) < 0.3) else "FAIL"),
        })
    df.to_csv(f"{cfg['outdir']}/{cfg['id']}_scores.csv")
    json.dump(result, open(f"{cfg['outdir']}/{cfg['id']}_cci_result.json", "w"), indent=2, default=str)
    print(json.dumps({k: result[k] for k in result if k not in ("positives","negatives","lr")}, indent=2, default=str))
    return result


if __name__ == "__main__":
    import importlib.util
    cfgfile = sys.argv[1]
    spec = importlib.util.spec_from_file_location("cfg", cfgfile)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    run(mod.CONFIG)
