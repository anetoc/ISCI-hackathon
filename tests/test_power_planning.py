import numpy as np
import pytest

from isci.power_planning import simulate_partial_donor_gate_power


def test_power_planning_is_deterministic_and_effect_sensitive():
    contrasts = np.asarray([0.04, 0.08, 0.12, 0.16, 0.20, 0.24])
    kwargs = dict(
        donor_counts=[6, 10],
        effect_scales=[0.5, 1.0],
        n_trials=40,
        n_bootstrap=30,
        seed=5,
    )
    first = simulate_partial_donor_gate_power(contrasts, **kwargs)
    second = simulate_partial_donor_gate_power(contrasts, **kwargs)
    assert first == second
    lookup = {(row["donor_count"], row["effect_scale"]): row for row in first}
    assert lookup[(10, 1.0)]["partial_gate_power"] >= lookup[(10, 0.5)][
        "partial_gate_power"
    ]


def test_power_planning_rejects_too_few_or_constant_pilots():
    with pytest.raises(ValueError, match="four pilot donors"):
        simulate_partial_donor_gate_power(
            np.asarray([0.1, 0.2, 0.3]), donor_counts=[6], n_bootstrap=20
        )
    with pytest.raises(ValueError, match="finite and variable"):
        simulate_partial_donor_gate_power(
            np.ones(4), donor_counts=[6], n_bootstrap=20
        )
