"""M — directional movement: project perturbation z-scores onto axis signatures."""

from __future__ import annotations

import numpy as np
import pandas as pd


def cosine_projection(z: np.ndarray, u: np.ndarray) -> float:
    """Cosine similarity between effect vector z and (unit) axis signature u.

    NaNs in z (genes not tested for this perturbation) are treated as 0.

    NOTE: diluted in high-dim, sparse-axis regimes — a dense effect vector (perturbation
    that moves ~1000 genes) is near-orthogonal to a 9-gene axis because ~10k zero-weight
    dims dominate the denominator. Use ``enrichment_projection`` as the primary M metric;
    cosine is kept for the ablation ("why not cosine").
    """
    z = np.nan_to_num(np.asarray(z, dtype=float), nan=0.0)
    nz = np.linalg.norm(z)
    if nz == 0:
        return 0.0
    return float(np.dot(z, u) / nz)  # u is already unit-norm from axes.build_axis_vectors


def enrichment_projection(z: np.ndarray, u: np.ndarray) -> float:
    """NES-style signed enrichment of effect vector z on axis signature u.

    Restricted to the axis's nonzero genes: weighted sum of z over the axis gene set,
    normalized by the signature norm on that set. Unlike cosine, this is NOT diluted by
    the ~10k off-axis zero dims — it measures how strongly the perturbation moves the
    *axis genes specifically*, in the axis's own weighted direction. Sign = direction
    along the axis. NaNs in z treated as 0.

    Empirically this recovers strong controllers cosine suppresses (e.g. FOXO1 on the
    memory axis moves from rank 573 -> 121), which is the intended fix for the C3/M_signed
    dilution problem.
    """
    z = np.nan_to_num(np.asarray(z, dtype=float), nan=0.0)
    idx = np.nonzero(u)[0]
    if idx.size == 0:
        return 0.0
    w = u[idx]
    denom = np.sqrt(np.sum(w * w)) + 1e-12
    return float(np.dot(z[idx], w) / denom)


def compute_movement(
    zscore_matrix: np.ndarray,
    axis_vectors: dict[str, np.ndarray],
    perturbation_ids: pd.Index,
    conditions: pd.Series,
    method: str = "enrichment",
) -> pd.DataFrame:
    """Compute M(g,a,c) = percentile rank of |projection(z, u_a)| within (axis, condition).

    m_raw keeps sign (direction along axis); M is the ranked magnitude in [0,1];
    sign_M records the direction for interpretation. Ranking is done *within each
    condition* so M is comparable across conditions.

    Parameters
    ----------
    zscore_matrix : (n_obs, n_genes) array — DE_stats .layers['zscore'], columns
                    aligned to the gene order used to build ``axis_vectors``.
    perturbation_ids : per-row perturbed-gene symbol (DE_stats.obs target_contrast_gene_name)
    conditions : per-row culture_condition, aligned to zscore_matrix rows.
    method : "enrichment" (default, NES-style, restricted to axis genes — the primary
             metric) or "cosine" (full-dim cosine, kept for the ablation).
    """
    proj = enrichment_projection if method == "enrichment" else cosine_projection
    conditions = pd.Series(np.asarray(conditions), name="condition").reset_index(drop=True)
    perturbation_ids = pd.Index(perturbation_ids)
    rows = []
    for axis, u in axis_vectors.items():
        raw = np.array([proj(zscore_matrix[i], u)
                        for i in range(zscore_matrix.shape[0])])
        df = pd.DataFrame({
            "perturbation": perturbation_ids.values,
            "condition": conditions.values,
            "axis": axis,
            "m_raw": raw,
            "sign_M": np.sign(raw),
        })
        # percentile-rank |m_raw| within each condition (so M in [0,1] per condition)
        df["M"] = (df.groupby("condition", observed=True)["m_raw"]
                     .transform(lambda s: s.abs().rank(pct=True)))
        rows.append(df)
    return pd.concat(rows, ignore_index=True)
