#!/usr/bin/env python
"""run_layer.py — modality-layer driver for the controllability tensor.

Generalizes run_cci.py from datasets to MODALITIES. The scientific method is unchanged: the
LOCKED CondInfo operator (isci-controllership skill). This driver only assembles per-modality
slices into one tensor object and enforces the contract that keeps the tensor honest:

  * every slice carries a magnitude residual + provenance (it must have been produced by the
    locked operator, so we validate schema, not recompute);
  * aggregation across modalities is rank-of-residuals + LATE — we never average raw scores,
    and we always keep the per-modality slice visible next to any aggregate.

A "layer" is one file `outputs/layers/<slice_id>/<name>_cci_result.json` written by a modality
adapter (RNA: run_cci.py; protein: Brief 06 totalVI on GPU; chromatin/spatial/FM: future).
This driver discovers those slice files, validates them, and writes:

  outputs/tensor/controllability_tensor.json   — all slices, canonical
  outputs/tensor/tensor_summary.csv            — one row per (system, modality) slice

Usage:
    python isci/run_layer.py                 # discover + assemble all slices
    python isci/run_layer.py --validate-only # check contracts, write nothing
"""
from __future__ import annotations
import json
import glob
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The canonical per-slice contract. A modality adapter MUST emit these keys. RNA slices
# (cci_result.json) already do; new modalities inherit the same schema so the operator layer
# stays single-implementation.
REQUIRED = ["id", "system", "verdict"]
# at least one magnitude-relationship field must be present (the honesty invariant)
MAG_FIELDS = ["spearman_mag", "spearman_C_magnitude", "spearman_protein_vs_rna",
              "lr_protein_given_rna_and_magnitude"]
EFFECT_FIELDS = ["delta_auprc", "bootstrap_dAUPRC_C", "gain"]


def _get(d, *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def discover_slices():
    """Find every modality slice file. RNA slices live in outputs/<id>/cci_result.json and
    outputs/generalization/*summary*; new-modality slices live in outputs/layers/*/*.json."""
    slices = []
    # RNA dataset slices (written by run_cci.py) → modality = RNA_coherence
    for p in sorted(glob.glob(str(REPO / "outputs" / "*" / "cci_result.json"))):
        slices.append(("RNA_coherence", Path(p)))
    for p in sorted(glob.glob(str(REPO / "outputs" / "external_tcell" / "*_cci_result.json"))):
        slices.append(("RNA_coherence", Path(p)))
    # New-modality slices (protein/chromatin/spatial/FM) → modality read from the file
    for p in sorted(glob.glob(str(REPO / "outputs" / "layers" / "*" / "*_result.json"))):
        slices.append(("FROM_FILE", Path(p)))
    return slices


def validate_slice(modality_hint, path):
    """Load one slice, enforce the tensor contract, normalize to a canonical row."""
    try:
        d = json.load(open(path))
    except Exception as e:
        return None, f"unreadable: {type(e).__name__}"
    # normalize id alias: RNA external slices use "dataset" instead of "id"
    if "id" not in d and "dataset" in d:
        d["id"] = d["dataset"]
    missing = [k for k in REQUIRED if k not in d]
    if missing:
        return None, f"missing required keys {missing}"
    # honesty invariant: a magnitude relationship must be reported
    if not any(k in d for k in MAG_FIELDS):
        return None, f"NO magnitude-relationship field (one of {MAG_FIELDS}) — refuses tensor entry"
    if not any(k in d for k in EFFECT_FIELDS):
        return None, f"NO effect field (one of {EFFECT_FIELDS})"
    # effect + CI (bootstrap dict OR flat keys)
    boot = d.get("bootstrap_dAUPRC_C") or {}
    gain = _get(d, "delta_auprc", "gain", default=boot.get("gain"))
    ci = d.get("ci95") or [d.get("ci_lo"), d.get("ci_hi")] if "ci_lo" in d else boot.get("ci95")
    modality = d.get("modality") if modality_hint == "FROM_FILE" else modality_hint
    row = {
        "slice_id": d["id"],
        "system": d["system"],
        "modality": modality or "UNSPECIFIED",
        "axis": d.get("axis", d.get("label", "immune_state")),
        "verdict": d["verdict"],
        "delta_auprc": round(float(gain), 4) if gain is not None else None,
        "ci_lo": round(float(ci[0]), 4) if ci and ci[0] is not None else None,
        "ci_hi": round(float(ci[1]), 4) if ci and ci[1] is not None else None,
        "spearman_vs_magnitude": _get(d, "spearman_mag", "spearman_C_magnitude"),
        "adds_over_prior_modality": _get(d, "lr_protein_given_rna_and_magnitude",
                                         "spearman_protein_vs_rna"),
        "n_pos": d.get("n_pos") or d.get("n_positives"),
        "source": str(path.relative_to(REPO)),
    }
    return row, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()

    rows, errors = [], []
    for hint, path in discover_slices():
        row, err = validate_slice(hint, path)
        if err:
            errors.append((str(path.relative_to(REPO)), err))
        else:
            rows.append(row)

    # report
    print(f"discovered {len(rows)} valid slice(s), {len(errors)} rejected")
    for r in rows:
        d = f"{r['delta_auprc']:+.3f}" if r["delta_auprc"] is not None else "  n/a"
        print(f"  [{r['modality']:16s}] {r['system']:18s} ΔAUPRC {d}  -> {r['verdict']}")
    for p, e in errors:
        print(f"  [REJECT] {p}: {e}")

    if args.validate_only:
        return

    outdir = REPO / "outputs" / "tensor"
    outdir.mkdir(parents=True, exist_ok=True)
    tensor = {
        "schema": "controllability_tensor.v1",
        "axes": ["gene", "axis", "system", "modality"],
        "invariants": ["magnitude-residualized entries only",
                       "rank-of-residuals late fusion (no raw averaging)",
                       "per-modality slice always shown next to any aggregate"],
        "slices": rows,
        "n_slices": len(rows),
        "modalities_present": sorted({r["modality"] for r in rows}),
    }
    json.dump(tensor, open(outdir / "controllability_tensor.json", "w"), indent=2)
    # flat CSV
    import csv
    with open(outdir / "tensor_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["slice_id"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nwrote outputs/tensor/controllability_tensor.json ({len(rows)} slices, "
          f"modalities: {tensor['modalities_present']})")


if __name__ == "__main__":
    main()
