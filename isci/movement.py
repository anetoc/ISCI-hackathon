"""M — directional movement: project perturbation z-scores onto axis signatures."""

from __future__ import annotations

import numpy as np
import pandas as pd


def cosine_projection(z: np.ndarray, u: np.ndarray) -> float:
    """Cosine similarity between effect vector z and (unit) axis signature u.

    NaNs in z (genes not tested for this perturbation) are treated as 0.
    """
    z = np.nan_to_num(np.asarray(z, dtype=float), nan=0.0)
    nz = np.linalg.norm(z)
    if nz == 0:
        return 0.0
    return float(np.dot(z, u) / nz)  # u is already unit-norm from axes.build_axis_vectors


def compute_movement(
    zscore_matrix: np.ndarray,
    axis_vectors: dict[str, np.ndarray],
    perturbation_ids: pd.Index,
    conditions: pd.Series,
) -> pd.DataFrame:
    """Compute M(g,a,c) = percentile rank of |cos(z, u_a)| within (axis, condition).

    m_raw keeps sign (direction along axis); M is the ranked magnitude in [0,1];
    sign_M records the direction for interpretation. Ranking is done *within each
    condition* so M is comparable across conditions.

    Parameters
    ----------
    zscore_matrix : (n_obs, n_genes) array — DE_stats .layers['zscore'], columns
                    aligned to the gene order used to build ``axis_vectors``.
    perturbation_ids : per-row perturbed-gene symbol (DE_stats.obs target_contrast_gene_name)
    conditions : per-row culture_condition, aligned to zscore_matrix rows.
    """
    conditions = pd.Series(np.asarray(conditions), name="condition").reset_index(drop=True)
    perturbation_ids = pd.Index(perturbation_ids)
    rows = []
    for axis, u in axis_vectors.items():
        raw = np.array([cosine_projection(zscore_matrix[i], u)
                        for i in range(zscore_matrix.shape[0])])
        df = pd.DataFrame({
            "perturbation": perturbation_ids.values,
            "condition": conditions.values,
            "axis": axis,
            "m_raw": raw,
            "sign_M": np.sign(raw),
        })
        # percentile-rank |m_raw| within each condition (so M in [0,1] per condition)
        df["M"] = (df.groupby("condition")["m_raw"]
                     .transform(lambda s: s.abs().rank(pct=True)))
        rows.append(df)
    return pd.concat(rows, ignore_index=True)
