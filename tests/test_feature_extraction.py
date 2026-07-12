import math

import pandas as pd

from isci.feature_extraction import (
    extract_controller_features,
    extract_controller_features_from_group_blocks,
)


AXES = {
    "axes": {
        "state_a": {"curated_markers": {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0}},
        "state_b": {"curated_markers": {"E": 1.0, "F": -1.0, "G": 1.0, "H": -1.0}},
    }
}


def _rows(perturbation, replicate_vectors, *, condition="stim"):
    rows = []
    for replicate_index, vector in enumerate(replicate_vectors):
        for feature, value in vector.items():
            rows.append(
                {
                    "perturbation": perturbation,
                    "feature": feature,
                    "condition": condition,
                    "donor": f"D{replicate_index}",
                    "guide": f"{perturbation}_g{replicate_index}",
                    "effect": value / 2,
                    "standardized_effect": value,
                    "target_expression": 10.0,
                    "n_guides": 2,
                    "n_cells": 200,
                    "benchmark_positive": perturbation == "A",
                }
            )
    return rows


def test_extracts_magnitude_loo_specificity_and_identical_replicate_coherence():
    vector = {"A": 50.0, "B": 2.0, "C": 2.0, "D": 2.0, "E": 0.0, "F": 0.0, "G": 0.0}
    table = pd.DataFrame(_rows("A", [vector, vector]))

    result = extract_controller_features(table, AXES)

    assert result.status == "COMPLETE"
    feature = result.features.iloc[0]
    # A is deliberately extreme. LOO removes it before scoring state_a, preventing self-credit.
    assert feature["specificity"] == 1.0
    assert feature["best_axis"] == "state_a"
    assert feature["reproducibility"] == 1.0
    assert feature["n_replicates"] == 2
    assert feature["n_replicate_pairs"] == 1
    assert feature["magnitude"] == math.sqrt((50**2 + 2**2 + 2**2 + 2**2) / 7)
    state_a = result.axis_scores.query("axis == 'state_a'").iloc[0]
    assert state_a["n_measured_markers"] == 3


def test_opposite_replicate_vectors_map_to_zero_reproducibility():
    forward = {"B": 1.0, "C": 2.0, "D": 3.0}
    reverse = {gene: -value for gene, value in forward.items()}
    table = pd.DataFrame(_rows("A", [forward, reverse]))

    result = extract_controller_features(table, AXES)

    assert result.features.iloc[0]["reproducibility"] == 0.0


def test_replicate_and_guide_define_independent_units_without_donor():
    forward = {"B": 1.0, "C": 2.0, "D": 3.0}
    reverse = {gene: -value for gene, value in forward.items()}
    table = pd.DataFrame(_rows("A", [forward, reverse])).drop(columns="donor")
    table["replicate"] = table["guide"].map({"A_g0": "R0", "A_g1": "R1"})
    table["guide"] = "A_g1"

    result = extract_controller_features(table, AXES)

    assert result.features.iloc[0]["n_replicates"] == 2
    assert result.features.iloc[0]["reproducibility"] == 0.0


def test_missing_replication_remains_missing_and_is_reported():
    table = pd.DataFrame(_rows("X", [{"A": 1.0, "B": 1.0, "C": 1.0}]))

    result = extract_controller_features(table, AXES)

    assert result.status == "NOT_EVALUABLE"
    assert math.isnan(result.features.iloc[0]["reproducibility"])
    assert "REPRODUCIBILITY_NOT_EVALUABLE" in {issue.code for issue in result.issues}
    assert result.report()["biological_verdict"] == "NOT_ISSUED"


def test_insufficient_axis_coverage_remains_missing_without_imputation():
    vector = {"A": 1.0, "B": 1.0, "E": 1.0}
    table = pd.DataFrame(_rows("A", [vector, vector]))

    result = extract_controller_features(table, AXES)

    assert result.status == "NOT_EVALUABLE"
    assert math.isnan(result.features.iloc[0]["specificity"])
    assert "AXIS_NOT_EVALUABLE" in {issue.code for issue in result.issues}


def test_complete_and_incomplete_groups_produce_partial_status():
    complete = _rows("X", [{"A": 1.0, "B": 1.0, "C": 1.0}] * 2)
    incomplete = _rows("Y", [{"A": 1.0, "B": 1.0, "C": 1.0}])

    result = extract_controller_features(pd.DataFrame(complete + incomplete), AXES)

    assert result.status == "PARTIAL"


def test_invalid_or_empty_inputs_are_not_evaluable():
    missing = extract_controller_features(pd.DataFrame({"perturbation": ["A"]}), AXES)
    empty = extract_controller_features(
        pd.DataFrame(columns=["perturbation", "feature", "effect", "standardized_effect"]),
        AXES,
    )

    assert missing.status == empty.status == "NOT_EVALUABLE"
    assert missing.issues[0].code == "MISSING_COLUMNS"
    assert empty.issues[0].code == "EMPTY_INPUT"


def test_absent_benchmark_metadata_does_not_create_false_benchmark_columns():
    table = pd.DataFrame(_rows("X", [{"A": 1.0, "B": 1.0, "C": 1.0}] * 2)).drop(
        columns=["benchmark_positive", "target_expression", "n_guides", "n_cells"]
    )

    result = extract_controller_features(table, AXES)

    assert "benchmark_positive" not in result.features
    assert "target_expression" not in result.features


def test_extraction_is_deterministic_for_shuffled_input():
    rows = _rows("X", [{"A": 1.0, "B": 2.0, "C": 3.0}] * 2)
    table = pd.DataFrame(rows)

    first = extract_controller_features(table, AXES)
    second = extract_controller_features(table.sample(frac=1, random_state=9), AXES)

    pd.testing.assert_frame_equal(first.features, second.features)
    pd.testing.assert_frame_equal(first.axis_scores, second.axis_scores)


def test_weighted_summary_matches_the_same_observations_expanded():
    table = pd.DataFrame(
        _rows(
            "X",
            [
                {"A": 1.0, "B": 2.0, "C": 3.0},
                {"A": 3.0, "B": 2.0, "C": 1.0},
            ],
        )
    )
    first_replicate = table[table["donor"] == "D0"]
    second_replicate = table[table["donor"] == "D1"]
    expanded = pd.concat([first_replicate] * 3 + [second_replicate], ignore_index=True)
    weighted = table.copy()
    weighted["_weight"] = weighted["donor"].map({"D0": 3, "D1": 1})

    expanded_result = extract_controller_features(expanded, AXES)
    weighted_result = extract_controller_features(weighted, AXES)

    columns = ["magnitude", "magnitude_sensitivity", "specificity", "reproducibility"]
    pd.testing.assert_series_equal(
        expanded_result.features.iloc[0][columns],
        weighted_result.features.iloc[0][columns],
    )


def test_nonpositive_internal_weights_are_rejected():
    table = pd.DataFrame(_rows("X", [{"A": 1.0, "B": 1.0, "C": 1.0}] * 2))
    table["_weight"] = 0

    result = extract_controller_features(table, AXES)

    assert result.status == "NOT_EVALUABLE"
    assert result.issues[0].code == "INVALID_WEIGHTS"


def test_group_block_extraction_matches_materialized_long_table():
    x = pd.DataFrame(_rows("X", [{"A": 1.0, "B": 2.0, "C": 3.0}] * 2))
    y = pd.DataFrame(_rows("Y", [{"A": -1.0, "B": -2.0, "C": -3.0}] * 2))
    blocks = [
        (("stim", "X"), x[x["donor"] == "D0"]),
        (("stim", "X"), x[x["donor"] == "D1"]),
        (("stim", "Y"), y),
    ]

    materialized = extract_controller_features(pd.concat([x, y], ignore_index=True), AXES)
    streamed = extract_controller_features_from_group_blocks(blocks, AXES)

    pd.testing.assert_frame_equal(materialized.features, streamed.features)
    pd.testing.assert_frame_equal(materialized.axis_scores, streamed.axis_scores)
    assert streamed.methods["streaming_grouped"] is True
    assert streamed.methods["peak_summary_buffer_rows"] < len(pd.concat([x, y]))


def test_stream_excludes_nonfinite_rows_with_explicit_counts():
    block = pd.DataFrame(_rows("X", [{"A": 1.0, "B": 2.0, "C": 3.0}] * 2))
    block.loc[0, "effect"] = float("nan")

    result = extract_controller_features_from_group_blocks([(("stim", "X"), block)], AXES)

    assert result.methods["excluded_nonfinite_rows"] == 1
    assert "NONFINITE_ROWS_EXCLUDED" in {issue.code for issue in result.issues}


def test_noncontiguous_stream_group_is_rejected():
    x = pd.DataFrame(_rows("X", [{"A": 1.0, "B": 1.0, "C": 1.0}] * 2))
    y = pd.DataFrame(_rows("Y", [{"A": 1.0, "B": 1.0, "C": 1.0}] * 2))
    blocks = [(("stim", "X"), x), (("stim", "Y"), y), (("stim", "X"), x)]

    result = extract_controller_features_from_group_blocks(blocks, AXES)

    assert result.status == "NOT_EVALUABLE"
    assert result.issues[0].code == "NONCONTIGUOUS_GROUP"
