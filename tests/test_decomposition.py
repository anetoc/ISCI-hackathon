import numpy as np
import pandas as pd
import pytest

from isci.decomposition import (
    EmpiricalRanker,
    MatchedBlock,
    RankResidualizer,
    benjamini_hochberg,
    block_bootstrap_transport_delta,
    block_bootstrap_delta,
    blocked_oof_predictions,
    component_verdict,
    condition_transport_delta,
    delta_auprc,
    match_unique_blocks,
    leave_one_condition_out_predictions,
    permute_positive_within_blocks,
    validate_blocks,
)


def fixture_data(n_blocks: int = 8, n_negatives: int = 5):
    rng = np.random.default_rng(7)
    rows = []
    blocks = []
    for block_index in range(n_blocks):
        positive = f"P{block_index}"
        negatives = tuple(f"N{block_index}_{j}" for j in range(n_negatives))
        blocks.append(MatchedBlock(positive, negatives))
        rows.append((positive, rng.normal(), 2.0 + rng.normal(scale=0.2)))
        rows.extend((gene, rng.normal(), rng.normal(scale=0.2)) for gene in negatives)
    frame = pd.DataFrame(rows, columns=["gene", "E", "S"]).set_index("gene")
    return frame, blocks


def condition_fixture():
    frame, blocks = fixture_data()
    rows = []
    for condition_index, condition in enumerate(["Rest", "Stim8hr", "Stim48hr"]):
        for gene, row in frame.iterrows():
            rows.append(
                {
                    "gene": gene,
                    "condition": condition,
                    "E": row.E + condition_index * 0.1,
                    "S": row.S + condition_index * 0.05,
                }
            )
    return pd.DataFrame(rows), blocks


def test_empirical_ranker_never_refits_on_test_values():
    ranker = EmpiricalRanker().fit([0.0, 1.0, 2.0])
    before = ranker.transform([1.5])
    ranker.transform([1_000_000.0])
    np.testing.assert_array_equal(before, ranker.transform([1.5]))


def test_rank_residualizer_removes_monotone_training_relation():
    effect = np.arange(20, dtype=float)
    component = effect * 3.0
    residual = RankResidualizer().fit(effect, component).transform(effect, component)
    assert np.max(np.abs(residual)) < 1e-12


def test_oof_predictions_are_deterministic_and_cover_each_gene_once():
    frame, blocks = fixture_data()
    first = blocked_oof_predictions(frame, blocks, effect_col="E", component_col="S")
    second = blocked_oof_predictions(frame, blocks, effect_col="E", component_col="S")
    pd.testing.assert_frame_equal(first, second)
    assert first["gene"].is_unique
    assert set(first["gene"]) == set(frame.index)
    assert first.groupby("block")["label"].sum().eq(1).all()


def test_held_block_cannot_change_other_folds_predictions():
    frame, blocks = fixture_data()
    original = blocked_oof_predictions(frame, blocks, effect_col="E", component_col="S")
    changed = frame.copy()
    changed.loc[list(blocks[0].genes), "S"] += 10_000
    rerun = blocked_oof_predictions(changed, blocks, effect_col="E", component_col="S")
    other = original["block"] != blocks[0].positive
    # The changed block is training data for other folds, so their predictions may change.
    # Its own predictions, however, use transformations fitted without its values.
    held = ~other
    np.testing.assert_allclose(
        original.loc[held, "base_prediction"], rerun.loc[held, "base_prediction"]
    )


def test_component_imputation_uses_training_fold_only():
    frame, blocks = fixture_data()
    frame.loc[blocks[0].positive, "S"] = np.nan
    result = blocked_oof_predictions(frame, blocks, effect_col="E", component_col="S")
    assert np.isfinite(result[["base_prediction", "full_prediction"]]).all().all()


def test_blocks_reject_overlap_and_insufficient_negatives():
    frame, blocks = fixture_data(n_blocks=2)
    overlap = [blocks[0], MatchedBlock(blocks[1].positive, blocks[0].negatives)]
    with pytest.raises(ValueError, match="more than one"):
        validate_blocks(frame, overlap)
    with pytest.raises(ValueError, match="requires at least 5"):
        validate_blocks(frame, [MatchedBlock("P0", ("N0_0",)), blocks[1]])


def test_unique_matching_is_deterministic_and_uses_covariates_only():
    frame, blocks = fixture_data(n_blocks=3, n_negatives=6)
    frame["match"] = np.arange(len(frame), dtype=float)
    positives = [block.positive for block in blocks]
    candidates = [gene for block in blocks for gene in block.negatives]
    first = match_unique_blocks(
        frame, positives, candidates, match_cols=["match"], n_negatives=5
    )
    changed = frame.copy()
    changed[["E", "S"]] *= 1_000
    second = match_unique_blocks(
        changed, positives, candidates, match_cols=["match"], n_negatives=5
    )
    assert first == second
    genes = [gene for block in first for gene in block.negatives]
    assert len(genes) == len(set(genes)) == 15


def test_block_permutation_preserves_membership_and_one_positive():
    _, blocks = fixture_data()
    permuted = permute_positive_within_blocks(blocks, seed=20260712)
    for original, changed in zip(blocks, permuted, strict=True):
        assert set(original.genes) == set(changed.genes)
        assert changed.positive not in changed.negatives
        assert len(changed.negatives) == len(original.negatives)


def test_bootstrap_and_delta_are_deterministic():
    frame, blocks = fixture_data()
    predictions = blocked_oof_predictions(frame, blocks, effect_col="E", component_col="S")
    assert np.isfinite(delta_auprc(predictions))
    a = block_bootstrap_delta(predictions, n_resamples=30, seed=4)
    b = block_bootstrap_delta(predictions, n_resamples=30, seed=4)
    np.testing.assert_array_equal(a, b)


def test_condition_transport_covers_every_block_in_every_condition():
    frame, blocks = condition_fixture()
    predictions = leave_one_condition_out_predictions(
        frame,
        blocks,
        conditions=["Rest", "Stim8hr", "Stim48hr"],
        effect_col="E",
        component_col="S",
    )
    assert len(predictions) == len(frame)
    assert predictions.groupby(["condition", "block"])["label"].sum().eq(1).all()
    mean_gain, gains = condition_transport_delta(predictions)
    assert np.isfinite(mean_gain)
    assert set(gains) == {"Rest", "Stim8hr", "Stim48hr"}


def test_held_condition_does_not_change_its_training_coefficient():
    frame, blocks = condition_fixture()
    original = leave_one_condition_out_predictions(
        frame, blocks, conditions=["Rest", "Stim8hr", "Stim48hr"], effect_col="E", component_col="S"
    )
    changed = frame.copy()
    changed.loc[changed.condition == "Rest", "S"] += 10_000
    rerun = leave_one_condition_out_predictions(
        changed, blocks, conditions=["Rest", "Stim8hr", "Stim48hr"], effect_col="E", component_col="S"
    )
    assert (
        original.attrs["condition_component_coefficients"]["Rest"]
        == rerun.attrs["condition_component_coefficients"]["Rest"]
    )


def test_transport_bootstrap_is_blocked_and_deterministic():
    frame, blocks = condition_fixture()
    predictions = leave_one_condition_out_predictions(
        frame, blocks, conditions=["Rest", "Stim8hr", "Stim48hr"], effect_col="E", component_col="S"
    )
    a = block_bootstrap_transport_delta(predictions, n_resamples=20, seed=9)
    b = block_bootstrap_transport_delta(predictions, n_resamples=20, seed=9)
    np.testing.assert_array_equal(a, b)


def test_bh_and_frozen_verdicts():
    np.testing.assert_allclose(benjamini_hochberg([0.01, 0.04, 1.0]), [0.03, 0.06, 1.0])
    assert component_verdict(gain=0.1, coefficient=0.2, ci_low=0.01, q_value=0.01) == "SUPPORTED"
    assert component_verdict(gain=0.1, coefficient=0.2, ci_low=-0.01, q_value=0.01) == "DIRECTIONAL_UNCERTAIN"
    assert component_verdict(gain=-0.1, coefficient=0.2, ci_low=-0.2, q_value=0.5) == "UNSUPPORTED"
    assert component_verdict(gain=1, coefficient=1, ci_low=1, q_value=0, evaluable=False) == "NOT_EVALUABLE"
