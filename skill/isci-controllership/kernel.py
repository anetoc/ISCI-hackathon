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
