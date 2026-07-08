#!/usr/bin/env python
"""Brief 03 — CAR-T atlas structure + patient-response label GATE.

Read-only inspection of the integrated atlas AnnData. Produces the numbers that
feed atlas_structure_report.md and (IF response labels exist) atlas_patient_response.csv.
Does NOT invent or impute labels — if no patient-level response is present, the gate
verdict is NOT-EVALUABLE.
"""
import sys, json, re
import numpy as np
import pandas as pd
import anndata as ad

H5AD = sys.argv[1] if len(sys.argv) > 1 else "/mnt/dados2/abel-tsc/data_public/cart/Atlas_integ_scArches_FINAL_V5.h5ad"
OUTDIR = "/mnt/dados2/abel-tsc/repo/outputs/cart_atlas"

# --- load in backed mode: we only need obs / var / obsm shapes, not X ---
print(f"[load] {H5AD} (backed='r')", flush=True)
A = ad.read_h5ad(H5AD, backed="r")
print(f"[shape] n_obs={A.n_obs:,}  n_var={A.n_vars:,}", flush=True)

result = {"h5ad": H5AD, "n_obs": int(A.n_obs), "n_var": int(A.n_vars)}
result["obsm_keys"] = list(A.obsm.keys())
result["layers"] = list(A.layers.keys())
result["uns_keys"] = list(A.uns.keys())
result["var_names_head"] = list(map(str, A.var_names[:5]))

# --- obs schema: dtype + cardinality + (small) value counts ---
obs = A.obs
schema = {}
for c in obs.columns:
    s = obs[c]
    nuniq = int(s.nunique(dropna=True))
    n_missing = int(s.isna().sum())
    entry = {"dtype": str(s.dtype), "n_unique": nuniq, "n_missing": n_missing}
    if nuniq <= 40 and not pd.api.types.is_float_dtype(s):
        vc = s.value_counts(dropna=False)
        entry["values"] = {str(k): int(v) for k, v in vc.items()}
    schema[c] = entry
result["obs_schema"] = schema
print(f"[obs] {len(obs.columns)} columns", flush=True)

# --- heuristics: identify candidate columns for the gate ---
def match(cols, pats):
    out = []
    for c in cols:
        cl = c.lower()
        if any(re.search(p, cl) for p in pats):
            out.append(c)
    return out

cols = list(obs.columns)
cand = {
    "patient": match(cols, [r"patient", r"donor", r"subject", r"^pt$", r"pid", r"sample_?id", r"individual"]),
    "study":   match(cols, [r"study", r"batch", r"dataset", r"cohort", r"gse", r"paper", r"author", r"source"]),
    "response":match(cols, [r"response", r"respond", r"\bcr\b", r"\bpr\b", r"\bnr\b", r"outcome", r"efficac", r"remission", r"relapse"]),
    "icans":   match(cols, [r"icans", r"crs", r"neurotox", r"toxicit"]),
    "phenotype":match(cols, [r"pheno", r"celltype", r"cell_type", r"annotation", r"state", r"cluster", r"leiden", r"louvain", r"ident"]),
    "cd48":    match(cols, [r"cd4", r"cd8", r"lineage"]),
}
result["candidate_columns"] = cand
print("[candidates]", json.dumps(cand, indent=1), flush=True)

json.dump(result, open(f"{OUTDIR}/atlas_structure_raw.json", "w"), indent=2, default=str)
print(f"[write] {OUTDIR}/atlas_structure_raw.json", flush=True)
print("[done] structure pass complete; inspect candidates before running the gate", flush=True)
