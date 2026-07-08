#!/usr/bin/env python
"""Brief 03 GATE — patient-level response label check + study confound + IEC gene coverage.

Decides EVALUABLE / NOT-EVALUABLE for Brief 04. Does not invent or impute labels.
"""
import json
import numpy as np
import pandas as pd
import anndata as ad

H5AD = "/mnt/dados2/abel-tsc/data_public/cart/Atlas_integ_scArches_FINAL_V5.h5ad"
OUTDIR = "/mnt/dados2/abel-tsc/repo/outputs/cart_atlas"

A = ad.read_h5ad(H5AD, backed="r")
obs = A.obs.copy()
var_names = set(map(str, A.var_names))
print(f"[shape] {A.n_obs:,} cells x {A.n_vars:,} genes", flush=True)

# --- find the multi-study/author column (14 author-labelled studies) ---
study_author_col = None
for c in obs.columns:
    vals = obs[c].astype(str)
    if vals.str.contains("_et_al", case=False, na=False).mean() > 0.5:
        study_author_col = c
        break
print(f"[study-author col] {study_author_col}", flush=True)

PATIENT = "Norm_Patient_Name"
STUDY = study_author_col or "Source"
RESP_COLS = ["Initial_Response", "Max_Response", "Anytime_Response", "Relapse"]
TOX_COLS = ["CRS", "CRS_Grade", "ICANS", "ICANS_Grade"]

def na(s):  # treat literal 'nan'/'NA' strings and real NaN as missing
    return s.astype("string").replace({"nan": pd.NA, "NA": pd.NA, "": pd.NA})

gate = {"n_cells": int(A.n_obs), "n_genes": int(A.n_vars),
        "patient_col": PATIENT, "study_col": STUDY,
        "response_cols": RESP_COLS, "obsm_keys": list(A.obsm.keys())}

# study cardinality
gate["n_studies"] = int(obs[STUDY].nunique())
gate["studies"] = {str(k): int(v) for k, v in obs[STUDY].value_counts().items()}

# --- patient-level table: one row per patient ---
prim = "Max_Response"  # primary label for Brief 04 (best RECIST-like response)
rows = []
for pid, g in obs.groupby(PATIENT, observed=True):
    def mode_or_na(col):
        v = na(g[col]).dropna()
        return v.mode().iloc[0] if len(v) else pd.NA
    rows.append({
        "patient_id": str(pid),
        "study": str(g[STUDY].iloc[0]),
        "disease": str(g["Person_source_General"].iloc[0]) if "Person_source_General" in g else pd.NA,
        "n_cells": int(len(g)),
        "Initial_Response": mode_or_na("Initial_Response"),
        "Max_Response": mode_or_na("Max_Response"),
        "Anytime_Response": mode_or_na("Anytime_Response"),
        "Relapse": mode_or_na("Relapse"),
        "CRS": mode_or_na("CRS"),
        "ICANS": mode_or_na("ICANS"),
    })
pt = pd.DataFrame(rows)
pt.to_csv(f"{OUTDIR}/atlas_patient_response.csv", index=False)
print(f"[patients] {len(pt)} unique", flush=True)

# --- consistency: is response constant within a patient? (label sanity) ---
consistency = {}
for col in RESP_COLS:
    per_pt_nuniq = obs.groupby(PATIENT, observed=True)[col].apply(lambda s: na(s).dropna().nunique())
    consistency[col] = {"patients_with_>1_value": int((per_pt_nuniq > 1).sum())}
gate["within_patient_label_consistency"] = consistency

# --- THE GATE counts ---
gate["patients_total"] = int(len(pt))
resp_gate = {}
for col in RESP_COLS:
    lab = pt[col].dropna()
    resp_gate[col] = {
        "n_patients_labeled": int(lab.notna().sum()),
        "patient_value_counts": {str(k): int(v) for k, v in lab.value_counts().items()},
        "n_cells_labeled": int(na(obs[col]).notna().sum()),
    }
gate["response_gate"] = resp_gate

# --- primary label patient x study confound cross-tab ---
labeled = pt[pt[prim].notna()].copy()
ct = pd.crosstab(labeled["study"], labeled[prim])
gate["primary_label"] = prim
gate["patient_study_x_response"] = ct.to_dict(orient="index")
# collapse to responder(CR/PR) vs non-responder(NR) for a cleaner confound view
labeled["responder"] = labeled[prim].map(lambda x: "R" if x in ("CR", "PR") else ("NR" if x == "NR" else pd.NA))
ct2 = pd.crosstab(labeled["study"], labeled["responder"])
gate["patient_study_x_RvsNR"] = ct2.to_dict(orient="index")
# confound severity: does any single study contribute all of one class?
gate["n_studies_with_labeled_patients"] = int(labeled["study"].nunique())
gate["n_studies_with_both_R_and_NR"] = int(((ct2.get("R", 0) > 0) & (ct2.get("NR", 0) > 0)).sum()) if "R" in ct2 and "NR" in ct2 else 0

# --- IEC gene coverage ---
IEC = {
 "persist_memory_stem": ["TCF7","LEF1","IL7R","SELL","CCR7","BACH2","ID3","KLF2","FOXO1"],
 "persist_migration":   ["CCR7","SELL","S1PR1","ITGAL","RHOA","WASF2","CORO1A","CXCR3"],
 "persist_synapse":     ["LCK","LAT","ZAP70","PLCG1","VAV1","LCP2","ITK","FYN","WAS","CORO1A","RHOA","CDC42","RAC2","TLN1","PXN","MYH9","CD2","CD58"],
 "kill":                ["GZMB","PRF1","NKG7","GNLY","IFNG","FASLG","GZMA"],
 "resist_exhaustion":   ["TOX","TOX2","PDCD1","LAG3","HAVCR2","NR4A2","NR4A3","TIGIT","ENTPD1"],
 "cd8_identity":        ["CD8A","CD8B","CD4","IL7R"],
}
cov = {}
for k, genes in IEC.items():
    present = [g for g in genes if g in var_names]
    missing = [g for g in genes if g not in var_names]
    cov[k] = {"n": len(genes), "present": len(present), "frac": round(len(present)/len(genes), 3), "missing": missing}
gate["iec_gene_coverage"] = cov

json.dump(gate, open(f"{OUTDIR}/gate_result.json", "w"), indent=2, default=str)
print("[write] gate_result.json + atlas_patient_response.csv", flush=True)

# --- console summary ---
print("\n==== GATE SUMMARY ====", flush=True)
print(f"patients total: {gate['patients_total']}  | studies: {gate['n_studies']}")
for col in RESP_COLS:
    print(f"  {col}: n_patients_labeled={resp_gate[col]['n_patients_labeled']}  {resp_gate[col]['patient_value_counts']}")
print(f"\nprimary={prim}: labeled patients={len(labeled)}, studies with labeled patients={gate['n_studies_with_labeled_patients']}, studies with BOTH R&NR={gate['n_studies_with_both_R_and_NR']}")
print("\npatient study x R/NR:")
print(ct2)
print("\nIEC coverage:", {k: f"{v['present']}/{v['n']}" for k, v in cov.items()})
