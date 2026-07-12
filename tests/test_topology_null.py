import numpy as np
import pytest

from isci.topology_null import (
    expression_matched_random_sets,
    mean_absolute_correlation,
    topology_rarity,
)


def test_mean_absolute_correlation_excludes_diagonal():
    correlation = np.asarray([[1.0, -0.4, 0.2], [-0.4, 1.0, 0.6], [0.2, 0.6, 1.0]])
    assert mean_absolute_correlation([0, 1, 2], correlation) == pytest.approx(0.4)


def test_random_sets_preserve_decile_counts_and_exclude_real_axis():
    deciles = np.repeat([0, 1], 10)
    real = [0, 1, 10, 11]
    samples = expression_matched_random_sets(real, deciles, n_random=20, seed=4)
    assert not np.isin(samples, real).any()
    for sample in samples:
        np.testing.assert_array_equal(np.bincount(deciles[sample], minlength=2), [2, 2])


def test_topology_rarity_is_deterministic_and_detects_correlated_axis():
    correlation = np.eye(20)
    correlation[:3, :3] = 0.9
    np.fill_diagonal(correlation, 1.0)
    deciles = np.zeros(20, dtype=int)
    first, first_null = topology_rarity([0, 1, 2], deciles, correlation, n_random=100, seed=8)
    second, second_null = topology_rarity([0, 1, 2], deciles, correlation, n_random=100, seed=8)
    assert first == second
    np.testing.assert_array_equal(first_null, second_null)
    assert first.observed == 0.9
    assert first.percentile == 1.0
    assert first.upper_p == 1 / 101
