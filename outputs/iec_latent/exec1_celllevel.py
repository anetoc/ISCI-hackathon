#!/usr/bin/env python
"""EXEC-1 / MASTER_ROADMAP Phase 5 — IEC cell-level 2.5-axis orthogonality test.

Structure test (NOT clinical): score A_persist / A_kill / A_resist per cell on the full CAR-T
atlas, test pairwise Spearman + each vs magnitude + whether A_kill is separable from CD8 identity
(partial correlation). Compare the correlation structure to the Marson pseudobulk pre-test.
CPU only. Pre-registered: axes "distinct" iff pairwise |rho|<0.5 AND vs-magnitude |rho|<0.3.
"""
import json
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from scipy.stats import rankdata, spearmanr

H5AD = "/mnt/dados2/abel-tsc/data_public/cart/Atlas_integ_scArches_FINAL_V5.h5ad"
OUTDIR = "/mnt/dados2/abel-tsc/repo/outputs/iec_latent"
MARSON_PB = f"{OUTDIR}/iec_axis_scores_pseudobulk_stim48.csv"

MODULES = {
 "memory_stem": ["TCF7","LEF1","IL7R","SELL","CCR7","BACH2","ID3","KLF2","FOXO1"],
 "migration":   ["CCR7","SELL","S1PR1","ITGAL","RHOA","WASF2","CORO1A","CXCR3"],
 "synapse":     ["LCK","LAT","ZAP70","PLCG1","VAV1","LCP2","ITK","FYN","WAS","CORO1A","RHOA","CDC42","RAC2","TLN1","PXN","MYH9","CD2","CD58"],
 "kill":        ["GZMB","PRF1","NKG7","GNLY","IFNG","FASLG","GZMA"],
 "exhaustion":  ["TOX","TOX2","PDCD1","LAG3","HAVCR2","NR4A2","NR4A3","TIGIT","ENTPD1"],
 "cd8":         ["CD8A","CD8B"], "cd4": ["CD4"],
}

def z(s):
    s = pd.to_numeric(s, errors="coerce"); return (s - s.mean()) / (s.std(ddof=0) + 1e-9)

def partial_spearman(x, y, z_ctrl):
    """Spearman partial correlation of x,y controlling z_ctrl (rank-transform then linear partial)."""
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z_ctrl)
    def resid(a, b):
        b1 = np.c_[np.ones_like(b), b]
        coef, *_ = np.linalg.lstsq(b1, a, rcond=None)
        return a - b1 @ coef
    ex, ey = resid(rx, rz), resid(ry, rz)
    r = np.corrcoef(ex, ey)[0, 1]
    return float(r)

print("[load]", flush=True)
A = ad.read_h5ad(H5AD, backed="r").to_memory()
print(f"[cells] {A.shape}", flush=True)
sc.pp.normalize_total(A, target_sum=1e4); sc.pp.log1p(A)
present = set(map(str, A.var_names))
cov = {}
for name, genes in MODULES.items():
    g = [x for x in genes if x in present]; cov[name] = f"{len(g)}/{len(genes)}"
    sc.tl.score_genes(A, g, score_name=f"s_{name}", use_raw=False)

d = A.obs
d["A_persist"] = pd.concat([z(d["s_memory_stem"]), z(d["s_migration"]), z(d["s_synapse"])], axis=1).mean(axis=1)
d["A_kill"] = z(d["s_kill"])
d["A_resist"] = -z(d["s_exhaustion"])
d["cd8_identity"] = z(d["s_cd8"]) - z(d["s_cd4"])
d["magnitude"] = pd.to_numeric(d["nCount_RNA"], errors="coerce")

AX = ["A_persist", "A_kill", "A_resist"]
res = {"system": "CAR-T atlas (cell-level)", "n_cells": int(A.n_obs), "coverage": cov,
       "preregistered": "distinct iff pairwise |rho|<0.5 AND vs-magnitude |rho|<0.3"}

# pairwise axis correlations + vs magnitude + vs cd8
pairs = {}
for i in range(len(AX)):
    for j in range(i+1, len(AX)):
        r, _ = spearmanr(d[AX[i]], d[AX[j]])
        pairs[f"{AX[i]}__{AX[j]}"] = round(float(r), 3)
vs_mag = {a: round(float(spearmanr(d[a], d["magnitude"])[0]), 3) for a in AX}
vs_cd8 = {a: round(float(spearmanr(d[a], d["cd8_identity"])[0]), 3) for a in AX}
res["axis_axis_spearman"] = pairs
res["axis_vs_magnitude"] = vs_mag
res["axis_vs_cd8_identity"] = vs_cd8

# CD8 guard: is A_kill separable from CD8 identity? partial corr of kill vs others controlling cd8
res["cd8_guard"] = {
    "kill_vs_cd8_raw": vs_cd8["A_kill"],
    "kill_vs_persist_partial_ctrl_cd8": round(partial_spearman(d["A_kill"], d["A_persist"], d["cd8_identity"]), 3),
    "kill_vs_resist_partial_ctrl_cd8": round(partial_spearman(d["A_kill"], d["A_resist"], d["cd8_identity"]), 3),
}

# verdicts
def verdict(r): return "orthogonal" if abs(r) < 0.5 else "ENTANGLED"
res["verdicts_axis_axis"] = {k: verdict(v) for k, v in pairs.items()}
res["verdicts_vs_magnitude"] = {k: ("ok(<0.3)" if abs(v) < 0.3 else "PROXY(>0.3)") for k, v in vs_mag.items()}

# Marson pseudobulk cross-system comparison
try:
    mpb = pd.read_csv(MARSON_PB)
    mcols = {c.lower(): c for c in mpb.columns}
    def col(*names):
        for n in names:
            if n in mcols: return mcols[n]
        return None
    cp, ck, cr = col("a_persist","persist"), col("a_kill","kill"), col("a_resist","resist")
    if cp and ck and cr:
        res["marson_pseudobulk"] = {
            "persist__kill": round(float(spearmanr(mpb[cp], mpb[ck])[0]), 3),
            "persist__resist": round(float(spearmanr(mpb[cp], mpb[cr])[0]), 3),
            "kill__resist": round(float(spearmanr(mpb[ck], mpb[cr])[0]), 3),
            "columns_used": [cp, ck, cr],
        }
    else:
        res["marson_pseudobulk"] = {"note": f"columns not matched; available={list(mpb.columns)}"}
except Exception as e:
    res["marson_pseudobulk"] = {"error": str(e)}

json.dump(res, open(f"{OUTDIR}/iec_celllevel_result.json", "w"), indent=2)
d[["Norm_Patient_Name","orig_ident","Person_source_General","A_persist","A_kill","A_resist","cd8_identity","magnitude"]].to_csv(f"{OUTDIR}/iec_axis_scores_celllevel.csv", index=False)

print("\n==== IEC cell-level (CAR-T atlas, n={}) ====".format(A.n_obs))
print("axis-axis Spearman:", pairs)
print("  verdicts:", res["verdicts_axis_axis"])
print("axis vs magnitude:", vs_mag, res["verdicts_vs_magnitude"])
print("axis vs CD8-identity:", vs_cd8)
print("CD8 guard:", res["cd8_guard"])
print("Marson pseudobulk:", res.get("marson_pseudobulk"))
print("[write] iec_celllevel_result.json + iec_axis_scores_celllevel.csv")
