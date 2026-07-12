#!/usr/bin/env python
"""Run the frozen target-paired GSE190604 Th2 context interaction diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.panel_validation import (  # noqa: E402
    overlap_weighted_delta,
    paired_context_delta,
    paired_context_oof,
    stratified_paired_gene_bootstrap,
    swap_paired_context_features,
)

SEED = 20260712
CONTEXTS = ("nostim", "stim")
FEATURES = ROOT / "outputs/decomposition_v2/gse190604_features.parquet"
AXES = ROOT / "config/axes.yaml"
OUTPUT_DIR = ROOT / "outputs/decomposition_v2"
RESULT_OUTPUT = OUTPUT_DIR / "gse190604_context_interaction.json"
RESAMPLE_OUTPUT = OUTPUT_DIR / "gse190604_context_interaction_resamples.parquet"
COMPONENT = "precision__th2"
SWAP_FEATURES = [
    "effect_reach",
    COMPONENT,
    "target_base_expr",
    "n_cells_target",
    "log_base_expr",
    "log_cells",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fit_paired(frame: pd.DataFrame, *, n_repeats: int) -> dict[str, pd.DataFrame]:
    """Apply the unchanged per-context OOF model with identical gene ordering."""

    return paired_context_oof(
        frame,
        gene_col="gene",
        context_col="context",
        contexts=CONTEXTS,
        label_col="is_positive",
        effect_col="effect_reach",
        component_col=COMPONENT,
        overlap_cols=["log_base_expr", "log_cells"],
        n_splits=5,
        n_repeats=n_repeats,
        seed=SEED,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-resamples", type=int, default=1_000)
    parser.add_argument("--n-repeats", type=int, default=10)
    args = parser.parse_args()
    if args.n_resamples < 1 or args.n_repeats < 1:
        raise SystemExit("resamples and repeats must be positive")

    frame = pd.read_parquet(FEATURES)
    required = [
        "gene",
        "context",
        "is_positive",
        "effect_reach",
        COMPONENT,
        "target_base_expr",
        "n_cells_target",
    ]
    frame = frame.dropna(subset=required).copy()
    frame["log_base_expr"] = np.log1p(frame["target_base_expr"].clip(lower=0))
    frame["log_cells"] = np.log1p(frame["n_cells_target"])
    pair_counts = frame.groupby("gene", observed=True)["context"].nunique()
    paired_genes = sorted(pair_counts[pair_counts == 2].index.astype(str))
    frame = frame[frame["gene"].isin(paired_genes)].sort_values(
        ["gene", "context"], kind="mergesort"
    )
    labels = frame.drop_duplicates("gene")["is_positive"]
    n_positive = int(labels.sum())
    n_negative = int(len(labels) - n_positive)
    if n_positive < 8 or n_negative < 15:
        raise RuntimeError("paired interaction class-count gate failed")
    numeric = frame[SWAP_FEATURES].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise RuntimeError("paired interaction features must be finite")
    print(
        f"[GSE190604 interaction] pairs={len(paired_genes)} "
        f"pos={n_positive} neg={n_negative}",
        flush=True,
    )

    predictions = fit_paired(frame, n_repeats=args.n_repeats)
    observed = paired_context_delta(predictions, contexts=CONTEXTS)
    context_gains = {
        context: overlap_weighted_delta(predictions[context]) for context in CONTEXTS
    }
    bootstrap = stratified_paired_gene_bootstrap(
        predictions,
        contexts=CONTEXTS,
        n_resamples=args.n_resamples,
        seed=SEED,
    )

    null = np.empty(args.n_resamples, dtype=float)
    for iteration in range(args.n_resamples):
        # Exchange the whole observed feature bundle within each gene. This
        # preserves labels and pair membership while removing context identity.
        rng = np.random.default_rng(SEED + 100_000 + iteration)
        mask = rng.random(len(paired_genes)) < 0.5
        permuted = swap_paired_context_features(
            frame,
            gene_col="gene",
            context_col="context",
            contexts=CONTEXTS,
            feature_cols=SWAP_FEATURES,
            swap_mask=mask,
        )
        null_predictions = fit_paired(permuted, n_repeats=args.n_repeats)
        null[iteration] = paired_context_delta(null_predictions, contexts=CONTEXTS)
        if (iteration + 1) % max(1, args.n_resamples // 10) == 0:
            print(
                f"[GSE190604 interaction] swaps {iteration + 1}/{args.n_resamples}",
                flush=True,
            )

    ci_low, ci_high = np.quantile(bootstrap, [0.025, 0.975])
    p_swap = float((1 + np.sum(null >= observed)) / (args.n_resamples + 1))
    if observed <= 0:
        verdict = "UNSUPPORTED"
    elif ci_low > 0 and p_swap < 0.05:
        verdict = "POSTHOC_CONTEXT_SUPPORT"
    else:
        verdict = "DIRECTIONAL_UNCERTAIN"

    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    timestamp = datetime.now().astimezone().isoformat()
    command = (
        "python scripts/run_gse190604_context_interaction.py "
        f"--n-resamples {args.n_resamples} --n-repeats {args.n_repeats}"
    )
    provenance = {
        "git_sha": git_sha,
        "data_sha256": sha256(FEATURES),
        "axes_sha256": sha256(AXES),
        "timestamp": timestamp,
        "command": command,
        "seed": SEED,
        "method_version": "gse190604_target_paired_context_v1",
    }
    result = {
        "test": "GSE190604 target-paired Th2 context interaction",
        "status": verdict,
        "n_pairs": len(paired_genes),
        "n_positive": n_positive,
        "n_negative": n_negative,
        "context_gains": context_gains,
        "interaction": observed,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "p_context_swap": p_swap,
        "null_median": float(np.median(null)),
        "boundary": (
            "Post-result target-paired diagnostic; not donor-paired, mechanistic or "
            "independent replication."
        ),
        "provenance": provenance,
    }
    resamples = pd.DataFrame(
        {
            "resample_type": np.repeat(["paired_gene_bootstrap", "context_swap_null"], args.n_resamples),
            "iteration": np.tile(np.arange(args.n_resamples), 2),
            "statistic": np.concatenate([bootstrap, null]),
        }
    )
    for key, value in provenance.items():
        resamples[key] = value
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_OUTPUT.write_text(json.dumps(result, indent=2))
    resamples.to_parquet(RESAMPLE_OUTPUT, index=False)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
