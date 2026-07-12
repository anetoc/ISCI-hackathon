import numpy as np
import pytest

from isci.topology_null import (
    convergence_diagnostics,
    decile_counts,
    effective_sample_size,
    gelman_rubin,
    mean_absolute_correlation,
)


def test_topology_statistic_uses_absolute_off_diagonal_values():
    correlation = np.asarray([[1.0, -0.4, 0.2], [-0.4, 1.0, 0.6], [0.2, 0.6, 1.0]])
    assert mean_absolute_correlation(correlation, [0, 1, 2]) == pytest.approx(0.4)


def test_decile_counts_preserve_exact_composition():
    assert decile_counts([0, 0, 1, 2], [0, 2, 3]) == {0: 1, 1: 1, 2: 1}


def test_rhat_and_ess_for_well_mixed_deterministic_traces():
    rng = np.random.default_rng(4)
    chains = rng.normal(size=(4, 200))
    assert gelman_rubin(chains) < 1.1
    assert effective_sample_size(chains) > 100


def test_diagnostics_require_unique_samples_and_three_chains():
    samples = [
        [[chain, index, index + 1000] for index in range(50)] for chain in range(4)
    ]
    rng = np.random.default_rng(8)
    traces = [rng.normal(0.15, 0.01, 50) for _ in range(4)]
    diagnostics = convergence_diagnostics(samples, traces, proposal_acceptance=0.1)
    assert diagnostics["n_unique"] == 200
    assert diagnostics["n_initialized_chains"] == 4
    assert diagnostics["effective_sample_size"] >= 50


def test_invalid_gene_set_is_rejected():
    with pytest.raises(ValueError, match="unique"):
        mean_absolute_correlation(np.eye(3), [0, 0])
