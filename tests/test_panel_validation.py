import numpy as np
import pandas as pd

from isci.panel_validation import (
    overlap_weighted_delta,
    repeated_overlap_oof,
    stratified_gene_bootstrap,
)


def panel_fixture():
    rng = np.random.default_rng(5)
    n = 60
    label = np.asarray([1] * 20 + [0] * 40)
    return pd.DataFrame(
        {
            "label": label,
            "E": rng.normal(size=n),
            "S": label + rng.normal(scale=0.5, size=n),
            "base_expr": rng.normal(size=n),
            "cells": rng.normal(size=n),
        },
        index=[f"G{index}" for index in range(n)],
    )


def test_repeated_overlap_oof_is_deterministic_and_gene_level():
    frame = panel_fixture()
    kwargs = dict(
        label_col="label",
        effect_col="E",
        component_col="S",
        overlap_cols=["base_expr", "cells"],
        n_repeats=2,
        seed=7,
    )
    first = repeated_overlap_oof(frame, **kwargs)
    second = repeated_overlap_oof(frame, **kwargs)
    pd.testing.assert_frame_equal(first, second)
    assert first.index.equals(frame.index)
    assert first["overlap_weight"].between(0.05, 0.95).all()
    assert overlap_weighted_delta(first) > 0


def test_stratified_bootstrap_is_deterministic():
    frame = panel_fixture()
    predictions = repeated_overlap_oof(
        frame,
        label_col="label",
        effect_col="E",
        component_col="S",
        overlap_cols=["base_expr", "cells"],
        n_repeats=2,
    )
    first = stratified_gene_bootstrap(predictions, n_resamples=20, seed=3)
    second = stratified_gene_bootstrap(predictions, n_resamples=20, seed=3)
    np.testing.assert_array_equal(first, second)
