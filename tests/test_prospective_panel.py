import pandas as pd
import pytest

from isci.prospective_panel import plan_panel_resources, select_prospective_panel


def make_guidecalls(target_guides: dict[str, list[tuple[str, int, int]]]) -> pd.DataFrame:
    """Create singleton calls whose barcode suffix preserves the two contexts."""

    rows = []
    serial = 0
    for _target, guides in target_guides.items():
        for guide_id, nostim_cells, stim_cells in guides:
            for well, count in ((1, nostim_cells), (5, stim_cells)):
                for _ in range(count):
                    serial += 1
                    rows.append(
                        {"cell_barcode": f"CELL{serial}-{well}", "feature_call": guide_id}
                    )
    return pd.DataFrame(rows)


def test_panel_selection_uses_technical_coverage_not_outcomes():
    labels = pd.DataFrame(
        {
            "gene": ["P1", "P2", "P3", "N1", "S1", "S2"],
            "is_positive": [True, True, True, False, True, True],
            "is_matched_negative": [False, False, False, True, False, False],
            "external_effect": [1000, -1000, 9999, 0, 0, 0],
        }
    )
    calls = make_guidecalls(
        {
            "P1": [("P1-1", 12, 12), ("P1-2", 11, 11)],
            "P2": [("P2-1", 22, 22), ("P2-2", 21, 21)],
            "P3": [("P3-1", 32, 32), ("P3-2", 31, 31)],
            "N1": [("N1-1", 10, 10), ("N1-2", 9, 9)],
            "S1": [("S1-1", 8, 8), ("S1-2", 7, 7)],
            "S2": [("S2-1", 6, 6), ("S2-2", 5, 5)],
            "NO-TARGET": [
                ("NO-TARGET-1", 50, 50),
                ("NO-TARGET-2", 40, 40),
            ],
        }
    )
    first = select_prospective_panel(
        labels,
        calls,
        positive_count=2,
        sentinels=("S1", "S2"),
        non_target_count=2,
    )
    labels["external_effect"] = [-value for value in labels["external_effect"]]
    second = select_prospective_panel(
        labels,
        calls,
        positive_count=2,
        sentinels=("S1", "S2"),
        non_target_count=2,
    )

    pd.testing.assert_frame_equal(first, second)
    positives = first.loc[first["role"] == "PRIMARY_POSITIVE", "target"].unique()
    assert positives.tolist() == ["P3", "P2"]
    assert set(first.loc[first["role"] == "MATCHED_NEGATIVE", "target"]) == {"N1"}
    assert not first.loc[
        first["role"].isin(["MECHANISTIC_SENTINEL", "NON_TARGET_CONTROL"]),
        "counted_in_primary",
    ].any()
    assert first["sequence_status"].eq("REQUIRES_DESIGN_AND_VALIDATION").all()


def test_panel_requires_two_guides_for_every_target():
    labels = pd.DataFrame(
        {"gene": ["P1"], "is_positive": [True], "is_matched_negative": [False]}
    )
    calls = make_guidecalls(
        {
            "P1": [("P1-1", 5, 5)],
            "NO-TARGET": [("NO-TARGET-1", 5, 5)],
        }
    )
    with pytest.raises(ValueError, match="fewer than 2 singleton guides"):
        select_prospective_panel(
            labels,
            calls,
            positive_count=1,
            sentinels=(),
            non_target_count=1,
        )


def test_resource_plan_is_deterministic_and_conservative():
    scenarios = plan_panel_resources(54, donor_counts=(8, 10, 12))
    assert [row["usable_cells"] for row in scenarios] == [43_200, 54_000, 64_800]
    assert [row["captured_cells"] for row in scenarios] == [72_000, 90_000, 108_000]
    assert [row["planning_channels"] for row in scenarios] == [4, 5, 6]


def test_resource_plan_rejects_invalid_assumptions():
    with pytest.raises(ValueError, match="usable fraction"):
        plan_panel_resources(10, usable_fraction=0)
