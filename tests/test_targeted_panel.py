import gzip

import numpy as np

from isci.targeted_panel import (
    aggregate_matrix_market_groups,
    log_cpm_profiles,
    matrix_market_header,
)


def write_fixture(path):
    with gzip.open(path, "wt") as handle:
        handle.write("%%MatrixMarket matrix coordinate integer general\n")
        handle.write("% synthetic feature by cell counts\n")
        handle.write("3 4 5\n")
        handle.write("1 1 2\n")
        handle.write("2 1 3\n")
        handle.write("1 2 5\n")
        handle.write("3 3 7\n")
        handle.write("2 4 11\n")


def test_header_and_group_aggregation(tmp_path):
    path = tmp_path / "matrix.mtx.gz"
    write_fixture(path)
    assert matrix_market_header(path) == (3, 4, 5, 3)
    aggregate = aggregate_matrix_market_groups(
        path, np.asarray([0, 0, 1, -1]), n_groups=2, chunksize=2
    )
    np.testing.assert_array_equal(aggregate.toarray(), [[7, 0], [3, 0], [0, 7]])


def test_log_cpm_is_group_by_feature_and_finite(tmp_path):
    path = tmp_path / "matrix.mtx.gz"
    write_fixture(path)
    aggregate = aggregate_matrix_market_groups(
        path, np.asarray([0, 0, 1, 1]), n_groups=2, chunksize=3
    )
    profiles = log_cpm_profiles(aggregate)
    assert profiles.shape == (2, 3)
    assert np.isfinite(profiles).all()
    assert profiles[0, 0] > profiles[0, 1]
