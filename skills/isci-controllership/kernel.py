"""ISCI controllership helpers. Pure functions over pandas DataFrames.

All operate on a gene-level feature table indexed by gene, with at least a
`magnitude` column plus candidate feature columns. See SKILL.md for the method.
"""

def expression_matched_negatives(positives, obs, gene_col="gene",
                                  match_cols=None, n_per_positive=8, exclude=None):
    """For each positive gene, draw the nearest non-positive perturbations by
    standardized Euclidean distance over expression/power covariates.

    positives: list of gene names. obs: per-perturbation DataFrame with gene_col
    and match_cols. Returns a deduplicated list of matched negative gene names.
    """
    import numpy as np, pandas as pd
    if match_cols is None:
        match_cols = ["target_baseMean", "n_cells_target"]
    exclude = set(exclude or positives)
    g = obs.groupby(gene_col, observed=True)[match_cols].apply(
        lambda d: d.apply(lambda s: np.nanmean(pd.to_numeric(s, errors="coerce"))))
    g = g.dropna()
    mu, sd = g.mean(), g.std().replace(0, 1)
    z = (g - mu) / sd
    pos_z = z.loc[[p for p in positives if p in z.index]]
    cand = z.loc[[i for i in z.index if i not in exclude]]
    chosen = []
    for p in pos_z.index:
        d = ((cand - pos_z.loc[p]) ** 2).sum(axis=1).pow(0.5).sort_values()
        chosen += list(d.head(n_per_positive).index)
    return list(dict.fromkeys(chosen))


def conditional_lr_test(feat, positives, negatives, base_col="magnitude", feature_cols=None):
    """Likelihood-ratio test: does each feature add over `base_col` for
    positive-vs-negative discrimination? Returns a DataFrame with LR stat,
    p-value, coefficient, and a boolean `adds` per feature.
    """
    import numpy as np, pandas as pd, statsmodels.api as sm
    from scipy.stats import chi2
    from sklearn.preprocessing import StandardScaler
    if feature_cols is None:
        feature_cols = [c for c in feat.columns if c != base_col]
    idx = [g for g in list(positives) + list(negatives) if g in feat.index]
    y = np.array([1] * sum(g in feat.index for g in positives) +
                 [0] * sum(g in feat.index for g in negatives))
    X = feat.loc[idx]
    def fit(cols):
        Xs = sm.add_constant(StandardScaler().fit_transform(X[cols].fillna(0)))
        return sm.Logit(y, Xs).fit(disp=0)
    base = fit([base_col])
    rows = []
    for f in feature_cols:
        full = fit([base_col, f])
        lr = 2 * (full.llf - base.llf)
        rows.append({"feature": f, "lr_stat": lr, "p_value": float(chi2.sf(lr, 1)),
                     "coef": float(full.params[-1]), "adds": bool(chi2.sf(lr, 1) < 0.05)})
    return pd.DataFrame(rows).sort_values("p_value")


def bootstrap_auprc_gain(feat, positives, negatives, base_col="magnitude",
                         feature_cols=None, score_col=None, n_boot=500, seed=0):
    """Bootstrap the AUPRC gain of base+features over base alone.

    If score_col is given, compares that precomputed score vs base_col.
    Otherwise fits a logistic model on [base_col]+feature_cols per resample.
    Returns dict with base/full mean AUPRC, gain, 95% CI, and P(gain>0).
    """
    import numpy as np, pandas as pd
    from sklearn.metrics import average_precision_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(seed)
    pos = [g for g in positives if g in feat.index]
    neg = [g for g in negatives if g in feat.index]
    if feature_cols is None and score_col is None:
        feature_cols = [c for c in feat.columns if c != base_col]
    base_ap, full_ap = [], []
    for _ in range(n_boot):
        pb = rng.choice(pos, len(pos), replace=True)
        nb = rng.choice(neg, len(neg), replace=True)
        idx = list(pb) + list(nb)
        yb = np.array([1] * len(pb) + [0] * len(nb))
        base_ap.append(average_precision_score(yb, feat.loc[idx, base_col].values))
        if score_col is not None:
            full_ap.append(average_precision_score(yb, feat.loc[idx, score_col].values))
        else:
            Xs = StandardScaler().fit_transform(feat.loc[idx, [base_col] + feature_cols].fillna(0))
            p = LogisticRegression(max_iter=2000).fit(Xs, yb).predict_proba(Xs)[:, 1]
            full_ap.append(average_precision_score(yb, p))
    base_ap, full_ap = np.array(base_ap), np.array(full_ap)
    gain = full_ap - base_ap
    return {"base_auprc": float(base_ap.mean()), "full_auprc": float(full_ap.mean()),
            "gain": float(gain.mean()),
            "ci95": [float(np.percentile(gain, 2.5)), float(np.percentile(gain, 97.5))],
            "p_gain_gt0": float((gain > 0).mean()), "n_boot": n_boot}


def controllership_score(feat, components, method="balanced", magnitude_col="magnitude",
                         detectable_floor=True, eps=1e-3):
    """Aggregate component columns into a controllership score.

    method="balanced": geomean of percentile ranks of `components` (includes
      magnitude if listed) — effect-weighted.
    method="orthogonal": mean percentile rank of magnitude-RESIDUALIZED
      components only (magnitude-independent), optionally gated to genes with
      above-median magnitude (detectable_floor).
    Returns a Series aligned to feat.index (NaN for gated-out genes).
    """
    import numpy as np, pandas as pd
    f = feat.copy()
    if method == "balanced":
        pr = np.column_stack([f[c].rank(pct=True).values for c in components])
        return pd.Series(np.exp(np.mean(np.log(np.clip(pr, eps, None)), axis=1)), index=f.index)
    if method == "orthogonal":
        def residualize(y, x):
            xr, yr = pd.Series(x).rank().values, pd.Series(y).rank().values
            return yr - np.polyval(np.polyfit(xr, yr, 1), xr)
        resid = {c: pd.Series(residualize(f[c], f[magnitude_col]), index=f.index).rank(pct=True)
                 for c in components if c != magnitude_col}
        score = pd.concat(resid, axis=1).mean(axis=1)
        if detectable_floor:
            score = score.where(f[magnitude_col] >= f[magnitude_col].median())
        return score
    raise ValueError("method must be 'balanced' or 'orthogonal'")


def movability_gate(zscore_matrix, gene_index, module_genes, min_frac=0.30):
    """Check whether a clinical module's genes are actually MOVED by perturbations
    (not just measured). A module gene is movable if its cross-perturbation z-score
    SD and responsive fraction (|z|>2) both exceed the genome-wide median.

    zscore_matrix: perturbations x genes (numpy). gene_index: dict gene->col.
    module_genes: list. Returns dict with movable gene list, frac, verdict.
    Use BEFORE reverse-mapping a module: if its defining genes are not moved by any
    perturbation, the module is not reverse-mappable (same ceiling that makes
    CD8/exhaustion markers unusable in CD4+ data).
    """
    import numpy as np
    z_sd = np.nanstd(zscore_matrix, axis=0)
    z_resp = np.nanmean(np.abs(zscore_matrix) > 2, axis=0)
    sd_med, resp_med = np.nanmedian(z_sd), np.nanmedian(z_resp)
    movable = [g for g in module_genes if g in gene_index
               and z_sd[gene_index[g]] > sd_med and z_resp[gene_index[g]] > resp_med]
    frac = len(movable) / max(len(module_genes), 1)
    return {"movable": movable, "frac_movable": round(frac, 3),
            "verdict": "PASS" if frac >= min_frac else "FAIL"}


def clinical_reversal_score(zscore_matrix, gene_index, perturbation_ids,
                            resistance_modules, sensitivity_modules, n_perm=1000, seed=42):
    """ClinicalReversalScore(g) = mean_z(sensitivity module genes) - mean_z(resistance
    module genes), per perturbation. High = pushes cells toward sensitivity and away
    from resistance programs. Includes a permutation null over module identity.

    resistance_modules / sensitivity_modules: dict name->gene list. perturbation_ids:
    numpy array aligned to zscore_matrix rows. Returns (per_gene_reversal_Series, null_dict).
    Caveat: effect vectors are KNOCKDOWNs, so a high score means knocking the gene down
    shifts cells toward sensitivity; the therapeutic sign is not automatic.
    """
    import numpy as np, pandas as pd
    def mod_mean(genes):
        idx = [gene_index[g] for g in genes if g in gene_index]
        return np.nanmean(zscore_matrix[:, idx], axis=1)
    res = np.nanmean([mod_mean(g) for g in resistance_modules.values()], axis=0)
    sen = np.nanmean([mod_mean(g) for g in sensitivity_modules.values()], axis=0)
    df = pd.DataFrame({"perturbation": perturbation_ids, "reversal_score": sen - res})
    gene_rev = df.groupby("perturbation")["reversal_score"].mean().dropna().sort_values(ascending=False)
    rng = np.random.default_rng(seed)
    all_genes = [g for gl in list(resistance_modules.values()) + list(sensitivity_modules.values()) for g in gl]
    n_res = sum(len(g) for g in resistance_modules.values())
    pool = list(gene_index.keys()); top = gene_rev.head(10).index.tolist()
    def grev(gene, ridx, sidx):
        rows = (perturbation_ids == gene)
        if rows.sum() == 0: return np.nan
        return np.nanmean(zscore_matrix[rows][:, sidx]) - np.nanmean(zscore_matrix[rows][:, ridx])
    null_max = np.zeros(n_perm)
    for p in range(n_perm):
        samp = rng.choice(pool, len(all_genes), replace=False)
        ridx = [gene_index[g] for g in samp[:n_res]]; sidx = [gene_index[g] for g in samp[n_res:]]
        null_max[p] = np.nanmax(np.abs([grev(g, ridx, sidx) for g in top]))
    obs_max = float(np.nanmax(np.abs(gene_rev.head(10).values)))
    pval = (np.sum(null_max >= obs_max) + 1) / (n_perm + 1)
    return gene_rev, {"observed_max": obs_max, "null_p95": float(np.percentile(null_max, 95)),
                      "p_value": float(pval), "n_perm": n_perm}


# --- Bloco A expansion helpers -------------------------------------------------

def matched_null_enrichment(target_genes, pool_df, family_sets, match_cols,
                            gene_col="gene", n_perm=1000, n_bins=5, seed=42):
    """Family/gene-set over-representation vs a covariate-matched null.
    pool_df has gene_col + numeric match_cols; family_sets: name -> set(genes).
    Returns DataFrame: observed, expected, fold, p_emp, q_bh per family.
    Call TWICE with different match_cols for Null A / Null B (e.g. +/- TCR_shutdown)."""
    import numpy as np, pandas as pd
    from collections import defaultdict
    try:
        from scipy.stats import false_discovery_control
    except Exception:
        false_discovery_control = None
    rng = np.random.default_rng(seed)
    P = pool_df.dropna(subset=list(match_cols)).set_index(gene_col)
    target_genes = [g for g in target_genes if g in P.index]
    binned = {c: pd.qcut(P[c].rank(method="first"), n_bins, labels=False) for c in match_cols}
    strata = pd.Series(list(zip(*[binned[c] for c in match_cols])), index=P.index)
    bucket = defaultdict(list)
    for g, s in strata.items():
        bucket[s].append(g)
    def fam_counts(genes):
        return {f: sum(g in gs for g in genes) for f, gs in family_sets.items()}
    tgt_strata = strata.loc[target_genes].tolist()
    obs = fam_counts(target_genes)
    fams = list(family_sets.keys())
    null = np.zeros((n_perm, len(fams)))
    for i in range(n_perm):
        samp = [bucket[s][rng.integers(len(bucket[s]))] for s in tgt_strata]
        fc = fam_counts(samp)
        null[i] = [fc[f] for f in fams]
    rows = []
    for j, f in enumerate(fams):
        o = obs[f]; exp = null[:, j].mean()
        p = (np.sum(null[:, j] >= o) + 1) / (n_perm + 1)
        rows.append({"family": f, "observed": o, "expected": round(float(exp), 2),
                     "fold": round(o / exp, 2) if exp > 0 else float("inf"), "p_emp": p})
    res = pd.DataFrame(rows)
    if false_discovery_control is not None and len(res):
        res["q_bh"] = false_discovery_control(res["p_emp"].values, method="bh").round(4)
    return res


def confounder_ledger(master_df, score_cols, confounder_cols, min_n=30):
    """Spearman of each score vs each confounder. Returns score -> {confounder: rho}.
    A score whose max|rho| stays low across all confounders is confounder-robust."""
    from scipy.stats import spearmanr
    ledger = {}
    for s in score_cols:
        row = {}
        for c in confounder_cols:
            d = master_df[[s, c]].dropna()
            if len(d) > min_n:
                rho, _ = spearmanr(d[s], d[c])
                row[c] = round(float(rho), 3)
        ledger[s] = row
    return ledger
