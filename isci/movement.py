"""M — directional movement: project perturbation z-scores onto axis signatures."""

from __future__ import annotations

import numpy as np
import pandas as pd


def cosine_projection(z: np.ndarray, u: np.ndarray) -> float:
    """Cosine similarity between effect vector z and axis signature u."""
    raise NotImplementedError("Implement in Claude Science build (D0)")


def compute_movement(
    zscore_matrix: np.ndarray,
    axis_vectors: dict[str, np.ndarray],
    perturbation_ids: pd.Index,
    conditions: pd.Series,
) -> pd.DataFrame:
    """
    Compute M(g,a,c) as percentile rank of |cos(z, u_a)| per axis and condition.

    Returns long DataFrame: perturbation, condition, axis, m_raw, M, sign_M.
    """
    raise NotImplementedError("Implement in Claude Science build (D0)")
