#!/usr/bin/env python
"""Build a component-resolved, non-scalar Controllability Profile v2."""

from __future__ import annotations

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

from isci.decomposition import RankResidualizer, pareto_front_mask  # noqa: E402

FEATURES = ROOT / "outputs/decomposition_v2/marson_condition_features.parquet"
TRANSPORT = ROOT / "outputs/decomposition_v2/t4_condition_transport_v2.json"
RANKING = ROOT / "results/final/isci_final_ranking.csv"
AXES = ROOT / "config/axes.yaml"
OUTPUT_DIR = ROOT / "outputs/decomposition_v2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def residual_percentile(effect: pd.Series, component: pd.Series) -> pd.Series:
    valid = effect.notna() & component.notna()
    result = pd.Series(np.nan, index=effect.index, dtype=float)
    residualizer = RankResidualizer().fit(effect[valid], component[valid])
    residual = residualizer.transform(effect[valid], component[valid])
    result.loc[valid] = pd.Series(residual, index=effect.index[valid]).rank(pct=True)
    return result


def classify(row: pd.Series) -> str:
    high_reach = row["reach_pct"] >= 0.75
    high_precision = row["precision_th2_conditional_pct"] >= 0.75
    high_repeatability = row["repeatability_conditional_pct"] >= 0.75
    if high_reach and high_precision and high_repeatability:
        return "robust_axis_controller"
    if high_precision and high_repeatability:
        return "precise_repeatable_low_reach"
    if high_precision:
        return "precise_context_controller"
    if high_reach and high_repeatability:
        return "repeatable_broad_mover"
    if high_reach:
        return "high_reach_mover"
    if high_repeatability:
        return "repeatable_low_precision"
    return "unresolved"


def main() -> None:
    condition = pd.read_parquet(FEATURES)
    ranking = pd.read_csv(RANKING).set_index("gene")
    numeric = [
        "effect_reach",
        "repeatability",
        *[column for column in condition.columns if column.startswith("precision__")],
    ]
    profile = condition.groupby("gene", observed=True)[numeric].mean()
    profile = profile.join(
        ranking[
            [
                "known_regulator",
                "clinical_controller",
                "ISCI_primary_rank",
                "ISCI_orthogonal",
            ]
        ],
        how="left",
    )
    profile["reach_pct"] = profile["effect_reach"].rank(pct=True)
    profile["repeatability_conditional_pct"] = residual_percentile(
        profile["effect_reach"], profile["repeatability"]
    )
    for column in [name for name in profile.columns if name.startswith("precision__")]:
        axis = column.removeprefix("precision__")
        profile[f"precision_{axis}_conditional_pct"] = residual_percentile(
            profile["effect_reach"], profile[column]
        )

    transport = json.loads(TRANSPORT.read_text())
    evidence = {row["component"]: row["verdict"] for row in transport["results"]}
    profile["th2_evidence"] = evidence["th2"]
    profile["th1_evidence"] = evidence["th1_effector"]
    profile["repeatability_evidence"] = evidence["repeatability"]
    profile["profile_archetype"] = profile.apply(classify, axis=1)
    pareto_columns = [
        "reach_pct",
        "precision_th2_conditional_pct",
        "repeatability_conditional_pct",
    ]
    profile["pareto_front"] = pareto_front_mask(profile[pareto_columns].to_numpy())
    profile["profile_version"] = "controllability_profile_v2"
    profile["profile_is_scalar"] = False
    profile = profile.reset_index()

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    provenance = {
        "git_sha": git_sha,
        "data_sha256": json.dumps(
            {
                str(FEATURES.relative_to(ROOT)): sha256(FEATURES),
                str(TRANSPORT.relative_to(ROOT)): sha256(TRANSPORT),
                str(RANKING.relative_to(ROOT)): sha256(RANKING),
            },
            sort_keys=True,
        ),
        "axes_sha256": sha256(AXES),
        "timestamp": datetime.now().astimezone().isoformat(),
        "command": "python scripts/build_controllability_profile_v2.py",
        "method_version": "controllability_profile_v2",
    }
    for key, value in provenance.items():
        profile[key] = value

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    profile.to_csv(OUTPUT_DIR / "controllability_profile_v2.csv", index=False)
    summary = {
        "artifact": "Controllability Profile v2",
        "status": "EXPLORATORY_EVOLUTIONARY",
        "n_genes": len(profile),
        "n_pareto_front": int(profile["pareto_front"].sum()),
        "archetype_counts": profile["profile_archetype"].value_counts().to_dict(),
        "pareto_genes": profile.loc[profile["pareto_front"], "gene"].tolist(),
        "evidence": evidence,
        "design": (
            "No new scalar: Pareto dimensions are reach, Th2 precision conditional on reach, "
            "and repeatability conditional on reach."
        ),
        "provenance": provenance,
    }
    (OUTPUT_DIR / "controllability_profile_v2.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({key: summary[key] for key in ["n_genes", "n_pareto_front", "archetype_counts"]}, indent=2))
    columns = [
        "gene",
        "profile_archetype",
        "pareto_front",
        "reach_pct",
        "precision_th2_conditional_pct",
        "repeatability_conditional_pct",
        "known_regulator",
    ]
    print(
        profile[profile["pareto_front"]]
        .sort_values(["known_regulator", "precision_th2_conditional_pct"], ascending=False)[columns]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
