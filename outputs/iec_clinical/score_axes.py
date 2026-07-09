#!/usr/bin/env python
"""Brief 04 step 1 — per-cell IEC axis scores on the CAR-T atlas, aggregated to patient level.

CPU only. IEC axes = gene-set scores (sc.tl.score_genes) on log-normalized counts — NOT the
scVI latent. Writes patient-level scores for all labeled cells and for the infusion-product
compartment (robustness). No labels invented: only cells with Max_Response in {CR,PR,NR}.
"""
import json
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad

H5AD = "/mnt/dados2/abel-tsc/data_public/cart/Atlas_integ_scArches_FINAL_V5.h5ad"
OUTDIR = "/mnt/dados2/abel-tsc/repo/outputs/iec_clinical"

PATIENT, STUDY, RESP = "Norm_Patient_Name", "orig_ident", "Max_Response"

MODULES = {
 "memory_stem": ["TCF7","LEF1","IL7R","SELL","CCR7","BACH2","ID3","KLF2","FOXO1"],
 "migration":   ["CCR7","SELL","S1PR1","ITGAL","RHOA","WASF2","CORO1A","CXCR3"],
 "synapse":     ["LCK","LAT","ZAP70","PLCG1","VAV1","LCP2","ITK","FYN","WAS","CORO1A","RHOA","CDC42","RAC2","TLN1","PXN","MYH9","CD2","CD58"],
 "kill":        ["GZMB","PRF1","NKG7","GNLY","IFNG","FASLG","GZMA"],
 "exhaustion":  ["TOX","TOX2","PDCD1","LAG3","HAVCR2","NR4A2","NR4A3","TIGIT","ENTPD1"],
 "cd8":         ["CD8A","CD8B"],
 "cd4":         ["CD4"],
}

print("[load backed]", flush=True)
A = ad.read_h5ad(H5AD, backed="r")
o = A.obs
resp = o[RESP].astype("string").replace({"nan": pd.NA})
mask = resp.notna().values
print(f"[subset] labeled cells = {int(mask.sum()):,}", flush=True)

# load labeled cells into memory (sparse CSR)
Asub = A[mask].to_memory()
print(f"[in memory] {Asub.shape}", flush=True)
Asub.var_names_make_unique()

# normalize -> log1p (raw counts in X)
sc.pp.normalize_total(Asub, target_sum=1e4)
sc.pp.log1p(Asub)

present = set(map(str, Asub.var_names))
cov = {}
for name, genes in MODULES.items():
    g = [x for x in genes if x in present]
    cov[name] = {"present": len(g), "total": len(genes), "missing": [x for x in genes if x not in present]}
    sc.tl.score_genes(Asub, g, score_name=f"s_{name}", use_raw=False)
print("[coverage]", {k: f"{v['present']}/{v['total']}" for k, v in cov.items()}, flush=True)

df = Asub.obs.copy()
def z(s):
    s = pd.to_numeric(s, errors="coerce"); return (s - s.mean()) / (s.std(ddof=0) + 1e-9)

# axes
df["z_memory_stem"] = z(df["s_memory_stem"]); df["z_migration"] = z(df["s_migration"]); df["z_synapse"] = z(df["s_synapse"])
df["A_persist"] = df[["z_memory_stem","z_migration","z_synapse"]].mean(axis=1)
df["A_kill"] = z(df["s_kill"])
df["A_resist"] = -z(df["s_exhaustion"])             # resistance = inverted exhaustion
df["A_eff_exh"] = df["A_kill"] - df["A_resist"]      # coupled effector/exhaustion axis (secondary)
df["cd8_identity"] = z(df["s_cd8"]) - z(df["s_cd4"])
# CD8 membership from phenotype
ph = df["manual_celltype_annotation_high"].astype("string")
df["is_cd8"] = ph.str.startswith("CD8").astype(float)
df["resp"] = resp[mask].values
df["R"] = df["resp"].map({"CR":1,"PR":1,"NR":0}).astype(int)
df["total_counts"] = pd.to_numeric(df["nCount_RNA"], errors="coerce")
df["n_features"] = pd.to_numeric(df["nFeature_RNA"], errors="coerce")

keep = [PATIENT, STUDY, "Person_source_General", "Time_Point_Ranges", "R", "resp",
        "A_persist","A_kill","A_resist","A_eff_exh","cd8_identity","is_cd8","total_counts","n_features"]
df[keep].to_parquet(f"{OUTDIR}/cell_axis_scores.parquet")
json.dump(cov, open(f"{OUTDIR}/axis_gene_coverage.json","w"), indent=2)
print(f"[write] cell_axis_scores.parquet ({len(df):,} cells)", flush=True)

# global medians for fraction-above-median aggregation
AX = ["A_persist","A_eff_exh","A_kill","A_resist","cd8_identity"]
gmed = {a: float(df[a].median()) for a in AX}

def patient_table(sub, tag):
    rows = []
    for pid, g in sub.groupby(PATIENT, observed=True):
        row = {"patient_id": str(pid), "study": str(g[STUDY].iloc[0]),
               "disease": str(g["Person_source_General"].iloc[0]),
               "R": int(g["R"].iloc[0]), "n_cells": int(len(g))}
        for a in AX:
            row[f"{a}__mean"] = float(g[a].mean())
            row[f"{a}__frachi"] = float((g[a] > gmed[a]).mean())
        row["b_total_counts"] = float(g["total_counts"].mean())
        row["b_cd8_frac"] = float(g["is_cd8"].mean())
        row["b_n_cells"] = int(len(g))
        row["b_n_features"] = float(g["n_features"].mean())
        rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(f"{OUTDIR}/patient_axis_scores_{tag}.csv", index=False)
    print(f"[patients {tag}] {len(t)}  R={int(t.R.sum())} NR={int((t.R==0).sum())} studies={t.study.nunique()}", flush=True)
    return t

patient_table(df, "all")
patient_table(df[df["Time_Point_Ranges"] == "Infusion_Product"], "infusionproduct")
print("[done] scoring complete", flush=True)
