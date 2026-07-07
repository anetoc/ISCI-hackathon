"""D0 runner: real-data ISCI-core on Marson DE_stats.

ISCI_core(g,a,c) = rank_product(M_signed_positive, Q, R)  aggregated to gene level.
Produces: outputs/isci_d0_ranked.csv, outputs/d0_benchmark.json, outputs/manifest_d0.json

Run: python scripts/run_d0.py
"""
from __future__ import annotations

import os
# numba cannot write its JIT cache into read-only site-packages (sandbox) — redirect
# BEFORE importing scanpy/pertpy, or scanpy import fails with "no locator available".
os.environ.setdefault("NUMBA_CACHE_DIR", "/tmp/numba_cache")
os.makedirs(os.environ["NUMBA_CACHE_DIR"], exist_ok=True)

import sys
import json
from pathlib import Path

# make the repo importable whether or not isci is pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from isci import io as isci_io
from isci import axes as axesmod
from isci import movement, qc, repro, baselines, index, validate

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
OUT = REPO / "outputs"
OUT.mkdir(exist_ok=True)
SEED = 42


def assemble_ground_truth() -> dict:
    import yaml
    D = DATA / "emdann"
    cfg = yaml.safe_load(open(REPO / "config" / "axes.yaml"))
    gt = cfg.get("ground_truth_controllers", {})
    clinical = sorted({g for lst in gt.values() for g in lst})
    coef = pd.read_csv(D / "polarization_prediction_condition_comparison_regulator_coefficients.csv", index_col=0)
    marson_native = sorted(coef.loc[coef["known_regulators"] == True, "regulator"].unique())
    return {"clinical": clinical, "marson_native": marson_native}


def main():
    de_path = DATA / "GWCD4i.DE_stats.h5ad"
    print(f"Loading {de_path} (backed) ...")
    adata = isci_io.load_de_stats(de_path, backed="r")
    print(f"  {adata.shape[0]} pert-cond x {adata.shape[1]} genes; layers={list(adata.layers.keys())}")

    gene_names = (adata.var["gene_name"].tolist() if "gene_name" in adata.var
                  else adata.var_names.tolist())
    obs = adata.obs.copy()
    gene_col = "target_contrast_gene_name"

    print("Reading zscore layer ...")
    Z = adata.layers["zscore"]
    Z = np.asarray(Z.todense()) if hasattr(Z, "todense") else np.asarray(Z[:])
    Z = np.nan_to_num(Z, nan=0.0)

    cfg = axesmod.load_axes_config(REPO / "config" / "axes.yaml")
    marker_genes = set()
    for a in cfg["axes"].values():
        marker_genes |= set((a.get("curated_markers") or {}).keys())

    uv_full = axesmod.build_axis_vectors(cfg, gene_names, suppl_dir=DATA / "emdann")
    M = movement.compute_movement(Z, uv_full, pd.Index(obs[gene_col].values),
                                  pd.Series(obs["culture_condition"].values))

    # LOO override for marker genes (C1)
    print(f"Applying leave-one-out to {len(marker_genes)} marker genes ...")
    row_gene = obs[gene_col].values
    cond_arr = obs["culture_condition"].values
    for g in marker_genes:
        rows = np.where(row_gene == g)[0]
        if len(rows) == 0:
            continue
        uv_g = axesmod.build_axis_vectors(cfg, gene_names, suppl_dir=DATA / "emdann", leave_one_out=g)
        for axis, u in uv_g.items():
            for ri in rows:
                mr = movement.cosine_projection(Z[ri], u)
                mask = ((M["perturbation"] == g) & (M["axis"] == axis) &
                        (M["condition"] == cond_arr[ri]))
                M.loc[mask, "m_raw"] = mr
                M.loc[mask, "sign_M"] = np.sign(mr)
    M["M"] = M.groupby(["axis", "condition"])["m_raw"].transform(lambda s: s.abs().rank(pct=True))

    Q = qc.compute_qc(obs)
    R = repro.compute_reproducibility(obs)

    # per-row component table
    q_lookup = pd.Series(Q.values, index=pd.MultiIndex.from_arrays([obs[gene_col].values, cond_arr]))
    r_lookup = pd.Series(R.values, index=pd.MultiIndex.from_arrays([obs[gene_col].values, cond_arr]))
    M = M.reset_index(drop=True)
    M["Q"] = [q_lookup.get((p, c), np.nan) for p, c in zip(M["perturbation"], M["condition"])]
    M["R"] = [r_lookup.get((p, c), np.nan) for p, c in zip(M["perturbation"], M["condition"])]
    M["M_mag"] = M["m_raw"].abs()          # direction-AGNOSTIC: controllership (a controller
                                            # pushes the state either way along an axis)
    M["M_pos"] = M["m_raw"].clip(lower=0)  # direction-POSITIVE: therapeutic-direction movement

    # ISCI-core (controllership) = rank_product(|M|, Q, R) per row, gene-level via max over (axis,cond).
    # Controllership is direction-agnostic -> use magnitude. M_pos is reported separately as the
    # therapeutic-direction score (for the +memory/-exhaustion demo framing), NOT the benchmark score.
    core = index.rank_product([
        pd.Series(M["M_mag"].values, index=M.index),
        pd.Series(M["Q"].values, index=M.index),
        pd.Series(M["R"].values, index=M.index),
    ])
    M["ISCI_core"] = core.values
    core_ther = index.rank_product([
        pd.Series(M["M_pos"].values, index=M.index),
        pd.Series(M["Q"].values, index=M.index),
        pd.Series(M["R"].values, index=M.index),
    ])
    M["ISCI_therapeutic"] = core_ther.values
    gene_isci = M.groupby("perturbation")["ISCI_core"].max().sort_values(ascending=False)

    # Benchmark vs baselines
    gt = assemble_ground_truth()
    scores = {
        "ISCI_core": gene_isci,
        "DE_magnitude": baselines.de_magnitude_baseline(obs, gene_col),
        "n_downstream": baselines.effect_size_baseline(obs, gene_col),
        "ontarget": baselines.ontarget_effect_baseline(obs, gene_col),
    }
    bench = {}
    for pos_name, pos in [("clinical", gt["clinical"]), ("marson_native", gt["marson_native"])]:
        bench[pos_name] = {sc: validate.ground_truth_recovery(s, pos) for sc, s in scores.items()}

    sdf = gene_isci.reset_index(); sdf.columns = ["gene", "ISCI_core"]
    sdf = index.null_permutation_test(sdf, score_col="ISCI_core", group_col=None, n_perm=1000, seed=SEED)
    sdf.to_csv(OUT / "isci_d0_ranked.csv", index=False)
    with open(OUT / "d0_benchmark.json", "w") as f:
        json.dump(bench, f, indent=2)
    manifest = isci_io.build_manifest(
        inputs={"DE_stats": de_path}, seeds={"null_permutation": SEED},
        params={"aggregator": "rank_product(M_pos,Q,R)", "leave_one_out": True, "n_perm": 1000},
        repo_dir=REPO)
    isci_io.write_manifest(OUT / "manifest_d0.json", manifest)

    print("\n=== D0 benchmark (precision@20 | AUPRC | AUROC) ===")
    for pos_name, d in bench.items():
        print(f"[{pos_name}]")
        for k, v in d.items():
            print(f"  {k:14s} p@20={v['precision_at_20']:.3f}  AUPRC={v['auprc']:.3f}  AUROC={v['auroc']:.3f}")
    print(f"\nTop 20 ISCI-core: {list(gene_isci.head(20).index)}")


if __name__ == "__main__":
    main()
