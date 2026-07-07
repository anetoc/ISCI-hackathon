"""Build functional axis signature vectors u_a from config and dataset-native tables."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def load_axes_config(path: Path | str) -> dict[str, Any]:
    """Load config/axes.yaml."""
    raise NotImplementedError("Implement in Claude Science build (D0)")


def build_axis_vectors(
    config: dict[str, Any],
    gene_names: list[str],
    suppl_dir: Path | None = None,
) -> dict[str, np.ndarray]:
    """
    Return unit L2-normalized signature vector u_a per axis, aligned to gene_names.

    Combines curated markers from axes.yaml with data-native tables (Th1/Th2, activation)
    when suppl_dir is provided.
    """
    raise NotImplementedError("Implement in Claude Science build (D0)")
