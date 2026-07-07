"""ISCI aggregation, null permutation, FDR, and graceful degradation by ambition tier."""

from __future__ import annotations

import numpy as np
import pandas as pd


def rank_product(components: list[pd.Series], names: list[str] | None = None) -> pd.Series:
    """ISCI-core aggregation: geometric mean of per-component percentile ranks.

    rank_product = ( prod_i rank_pct(component_i) ) ** (1/k), computed in log space.
    This is the PRIMARY ISCI-core aggregator (revised architecture): non-parametric,
    scale-free, and robust to the different units of M/Q/R/C. Components are aligned on
    their union index; a gene missing from a component gets rank 0 there (worst),
    which is correct — absence of evidence in a component is not neutral.

    Each input is percentile-ranked here (so callers may pass raw component values).
    Returns a Series in [0,1], higher = stronger candidate state-shift controller.
    """
    if not components:
        raise ValueError("need at least one component")
    idx = components[0].index
    for c in components[1:]:
        idx = idx.union(c.index)
    log_ranks = []
    for c in components:
        r = c.reindex(idx).rank(pct=True)          # NaN -> NaN, ranked among present
        r = r.fillna(0.0).clip(lower=1e-6)          # missing = worst rank, avoid log(0)
        log_ranks.append(np.log(r.to_numpy()))
    rp = np.exp(np.mean(log_ranks, axis=0))
    return pd.Series(rp, index=idx, name="ISCI_core")


def _geomean_eps(components: list[pd.Series], epsilon: float) -> pd.Series:
    """Epsilon-floored geometric mean (C4): a single zero component must not annihilate
    the score, but low components should still pull it down. Aligns on the union index."""
    if not components:
        raise ValueError("need at least one component")
    idx = components[0].index
    for c in components[1:]:
        idx = idx.union(c.index)
    logs = []
    for c in components:
        x = c.reindex(idx).fillna(epsilon).clip(lower=epsilon, upper=1.0)
        logs.append(np.log(x.to_numpy()))
    return pd.Series(np.exp(np.mean(logs, axis=0)), index=idx)


def geometric_mean_components(
    m: pd.Series,
    d: pd.Series | None,
    a: pd.Series | None,
    s: pd.Series | None,
    r: pd.Series,
    epsilon: float = 1e-3,
) -> pd.Series:
    """ISCI = R * S * geomean_eps(M, D, A) with epsilon floor (C4).

    Missing components are omitted from the geomean (graceful degradation):
    D0 reduces to R * geomean_eps(M) = R * M. S and R multiply the core; when S is
    absent it is treated as 1 (no stability gating yet).
    """
    core_components = [c for c in (m, d, a) if c is not None]
    core = _geomean_eps(core_components, epsilon)
    idx = core.index.union(r.index)
    if s is not None:
        idx = idx.union(s.index)
    core = core.reindex(idx).fillna(epsilon)
    r_al = r.reindex(idx).fillna(epsilon)
    s_al = (s.reindex(idx).fillna(epsilon)) if s is not None else pd.Series(1.0, index=idx)
    return (r_al * s_al * core).rename("ISCI")


def null_permutation_test(
    scores: pd.DataFrame,
    score_col: str = "ISCI",
    group_col: str | None = "axis",
    n_perm: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """Empirical p-values by shuffling perturbation labels; BH-FDR q-values.

    Valid null for the Movement-driven score (permuting which perturbation owns which
    effect vector). NOTE (C6): this is *not* a valid null for the D (network topology)
    or S (replicate structure) components — those need degree-preserving rewiring and
    within-perturbation guide shuffling respectively, implemented in network.py/stability.py.

    Returns ``scores`` with added columns: p_value, q_value (BH-FDR).
    """
    from statsmodels.stats.multitest import multipletests

    rng = np.random.default_rng(seed)
    out = scores.copy().reset_index(drop=True)
    obs = out[score_col].to_numpy()

    def _null_ge(vals: np.ndarray) -> np.ndarray:
        ge = np.zeros(len(vals))
        for _ in range(n_perm):
            perm = rng.permutation(vals)
            ge += (perm >= vals)
        return (ge + 1) / (n_perm + 1)  # +1 smoothing

    if group_col and group_col in out:
        p = np.empty(len(out))
        for _, idx in out.groupby(group_col).groups.items():
            idx = np.array(list(idx))
            p[idx] = _null_ge(obs[idx])
    else:
        p = _null_ge(obs)

    out["p_value"] = p
    out["q_value"] = multipletests(p, method="fdr_bh")[1]
    return out
