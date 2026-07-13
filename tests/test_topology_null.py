import numpy as np
import pytest

from isci.topology_null import (
    conditional_topology_samples,
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


def test_conditional_sampler_preserves_topology_and_excludes_real_genes():
    correlation = np.full((30, 30), 0.05)
    for start in range(0, 30, 3):
        correlation[start : start + 3, start : start + 3] = 0.85
    np.fill_diagonal(correlation, 1.0)
    deciles = np.zeros(30, dtype=int)
    samples, diagnostics = conditional_topology_samples(
        [0, 1, 2],
        deciles,
        correlation,
        n_samples=5,
        n_chains=2,
        burn_in=20,
        thinning=5,
        max_initialization_steps=5_000,
        seed=3,
    )
    assert len(samples) == diagnostics.collected_samples
    assert 1 <= len(samples) <= 5
    assert diagnostics.unique_sample_fraction == len(samples) / 5
    assert diagnostics.initialized_chains >= 1
    assert not np.isin(samples, [0, 1, 2]).any()
    for sample in samples:
        statistic = mean_absolute_correlation(sample, correlation)
        assert diagnostics.lower_bound <= statistic <= diagnostics.upper_bound


def test_conditional_sampler_is_deterministic():
    correlation = np.eye(16) * 0.9 + 0.1
    deciles = np.repeat([0, 1], 8)
    kwargs = dict(
        n_samples=4,
        n_chains=2,
        burn_in=10,
        thinning=2,
        max_initialization_steps=500,
        seed=11,
    )
    first, first_diagnostics = conditional_topology_samples(
        [0, 1, 8, 9], deciles, correlation, **kwargs
    )
    second, second_diagnostics = conditional_topology_samples(
        [0, 1, 8, 9], deciles, correlation, **kwargs
    )
    np.testing.assert_array_equal(first, second)
    assert first_diagnostics == second_diagnostics
