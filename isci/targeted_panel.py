"""Memory-bounded helpers for targeted Perturb-seq MatrixMarket panels."""

from __future__ import annotations

import gzip
from pathlib import Path
from typing import Callable, Iterator

import numpy as np
import pandas as pd
from scipy import sparse


def matrix_market_header(path: Path | str) -> tuple[int, int, int, int]:
    """Return rows, columns, nonzeros and number of header lines in a gzip MTX."""

    with gzip.open(path, "rt") as handle:
        first = handle.readline().strip()
        if not first.startswith("%%MatrixMarket matrix coordinate"):
            raise ValueError("expected a coordinate MatrixMarket file")
        line_number = 1
        for line in handle:
            line_number += 1
            if line.startswith("%"):
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError("invalid MatrixMarket dimension line")
            rows, columns, nonzeros = (int(value) for value in parts)
            return rows, columns, nonzeros, line_number
    raise ValueError("MatrixMarket dimensions are missing")


def matrix_market_chunks(
    path: Path | str, *, header_lines: int, chunksize: int = 2_000_000
) -> Iterator[pd.DataFrame]:
    """Yield zero-based coordinate chunks using the C-backed pandas parser."""

    reader = pd.read_csv(
        path,
        compression="gzip",
        sep=r"\s+",
        skiprows=header_lines,
        names=["row", "column", "value"],
        dtype={"row": np.int32, "column": np.int32, "value": np.float64},
        chunksize=chunksize,
    )
    for chunk in reader:
        chunk["row"] -= 1
        chunk["column"] -= 1
        yield chunk


def aggregate_matrix_market_groups(
    path: Path | str,
    cell_to_group: np.ndarray,
    *,
    n_groups: int,
    chunksize: int = 2_000_000,
    progress: Callable[[int, int], None] | None = None,
) -> sparse.csr_matrix:
    """Aggregate feature×cell raw counts into feature×group counts in bounded memory."""

    n_features, n_cells, expected_nonzeros, header_lines = matrix_market_header(path)
    mapping = np.asarray(cell_to_group, dtype=int)
    if len(mapping) != n_cells:
        raise ValueError(f"cell mapping has {len(mapping)} entries; matrix has {n_cells}")
    aggregate = sparse.csr_matrix((n_features, n_groups), dtype=np.float64)
    observed_nonzeros = 0
    for chunk in matrix_market_chunks(path, header_lines=header_lines, chunksize=chunksize):
        observed_nonzeros += len(chunk)
        if progress is not None:
            progress(observed_nonzeros, expected_nonzeros)
        columns = chunk["column"].to_numpy()
        groups = mapping[columns]
        keep = groups >= 0
        if not keep.any():
            continue
        part = sparse.coo_matrix(
            (
                chunk.loc[keep, "value"].to_numpy(),
                (chunk.loc[keep, "row"].to_numpy(), groups[keep]),
            ),
            shape=(n_features, n_groups),
        ).tocsr()
        aggregate += part
    if observed_nonzeros != expected_nonzeros:
        raise RuntimeError(
            f"parsed {observed_nonzeros} nonzeros; header declares {expected_nonzeros}"
        )
    aggregate.eliminate_zeros()
    return aggregate


def log_cpm_profiles(group_counts: sparse.spmatrix) -> np.ndarray:
    """Return groups×features log1p counts-per-million profiles."""

    counts = group_counts.tocsc().astype(np.float64)
    library_size = np.asarray(counts.sum(axis=0)).ravel()
    if (library_size <= 0).any():
        raise ValueError("every retained group must have positive library size")
    for column in range(counts.shape[1]):
        start, stop = counts.indptr[column : column + 2]
        counts.data[start:stop] = np.log1p(
            counts.data[start:stop] * (1_000_000.0 / library_size[column])
        )
    return counts.toarray().T.astype(np.float32)
