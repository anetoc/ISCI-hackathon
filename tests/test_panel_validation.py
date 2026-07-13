import numpy as np
import pandas as pd

from isci.panel_validation import (
    overlap_weighted_delta,
    paired_context_delta,
    paired_context_oof,
    repeated_overlap_oof,
    stratified_paired_gene_bootstrap,
    stratified_gene_bootstrap,
    swap_paired_context_features,
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
    frame["label"] = frame["label"].astype(bool)
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


def paired_fixture():
    base = panel_fixture().reset_index(names="gene")
    rows = []
    for context in ["nostim", "stim"]:
        part = base.copy()
        part["context"] = context
        if context == "stim":
            part["S"] = np.random.default_rng(12).normal(size=len(part))
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def test_paired_context_pipeline_is_aligned_and_deterministic():
    frame = paired_fixture()
    kwargs = dict(
        gene_col="gene",
        context_col="context",
        contexts=("nostim", "stim"),
        label_col="label",
        effect_col="E",
        component_col="S",
        overlap_cols=["base_expr", "cells"],
        n_repeats=2,
        seed=9,
    )
    first = paired_context_oof(frame, **kwargs)
    second = paired_context_oof(frame, **kwargs)
    for context in kwargs["contexts"]:
        pd.testing.assert_frame_equal(first[context], second[context])
    assert paired_context_delta(first, contexts=kwargs["contexts"]) > 0


def test_paired_bootstrap_and_context_swap_preserve_gene_pairing():
    frame = paired_fixture()
    predictions = paired_context_oof(
        frame,
        gene_col="gene",
        context_col="context",
        contexts=("nostim", "stim"),
        label_col="label",
        effect_col="E",
        component_col="S",
        overlap_cols=["base_expr", "cells"],
        n_repeats=2,
    )
    first = stratified_paired_gene_bootstrap(
        predictions, contexts=("nostim", "stim"), n_resamples=10, seed=4
    )
    second = stratified_paired_gene_bootstrap(
        predictions, contexts=("nostim", "stim"), n_resamples=10, seed=4
    )
    np.testing.assert_array_equal(first, second)

    genes = sorted(frame["gene"].unique())
    mask = np.zeros(len(genes), dtype=bool)
    mask[0] = True
    swapped = swap_paired_context_features(
        frame,
        gene_col="gene",
        context_col="context",
        contexts=("nostim", "stim"),
        feature_cols=["E", "S", "base_expr", "cells"],
        swap_mask=mask,
    )
    original = frame.set_index(["gene", "context"])
    changed = swapped.set_index(["gene", "context"])
    np.testing.assert_array_equal(
        changed.loc[(genes[0], "nostim"), ["E", "S", "base_expr", "cells"]],
        original.loc[(genes[0], "stim"), ["E", "S", "base_expr", "cells"]],
    )
    assert changed.loc[(genes[0], "nostim"), "label"] == original.loc[(genes[0], "nostim"), "label"]
