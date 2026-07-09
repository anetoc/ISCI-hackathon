#!/usr/bin/env python
"""RNA <-> protein cross-layer controller check (multiomic architecture, EXEC).

Applies the SAME controllership operator to the CITE protein layer and tests concordance with
the RNA layer. Two cases:
  * Frangieh: RNA was EVALUABLE (near-miss). Build the protein immune-evasion axis the same way
    (IFNγ - Control in control cells, over the ADT panel), score per-perturbation protein
    axis-specificity S_prot, test (a) recovery of canonical IFN/APM positives at the protein
    level and (b) cross-layer concordance Spearman(S_rna, S_prot).
  * Papalexi: RNA was NOT-EVALUABLE (no baseline axis). Its NATIVE readout is surface PD-L1
    protein -> test whether the protein layer recovers PD-L1 regulators (native-layer rescue).
CPU only. No new large data (protein h5ads are 25 MB / 1 MB).
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
import anndata as ad
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.metrics import roc_auc_score, average_precision_score

REPO = Path("/mnt/dados2/abel-tsc/repo")
DATA = Path("/mnt/dados2/abel-tsc/data_public/external_perturb")
OUT = REPO / "outputs" / "external_tcell"
MIN_CELLS = 25

def clr(X):
    """centered-log-ratio ADT normalization (cells x proteins), pseudocount 1."""
    X = np.asarray(X, float) + 1.0
    return np.log(X) - np.log(X).mean(1, keepdims=True)

def load(fn):
    A = ad.read_h5ad(DATA / fn)
    X = A.X.toarray() if hasattr(A.X, "toarray") else np.asarray(A.X)
    return A, clr(X)

# ---------------- Frangieh: RNA<->protein concordance ----------------
def frangieh():
    A, Xc = load("FrangiehIzar2021_protein.h5ad")
    o = A.obs
    prot = np.array(A.var_names)
    isotype = np.array([("IgG" in p) for p in prot])       # drop isotype controls from axis
    keep = ~isotype
    tgt = o["perturbation"].astype(str).values
    cond = o["perturbation_2"].astype(str).values
    # protein immune-evasion axis = IFNγ - Control in control cells (same recipe as RNA)
    cm = tgt == "control"
    ax = Xc[cm & (cond == "IFNγ")][:, keep].mean(0) - Xc[cm & (cond == "Control")][:, keep].mean(0)
    # per-target protein effect within IFNγ (target - control), S_prot, magnitude_prot
    rows = []
    for t in np.unique(tgt):
        if t == "control":
            continue
        m = (tgt == t) & (cond == "IFNγ")
        c = cm & (cond == "IFNγ")
        if m.sum() < MIN_CELLS:
            continue
        eff = Xc[m][:, keep].mean(0) - Xc[c][:, keep].mean(0)
        Mp = float(np.linalg.norm(eff))
        Sp = float(abs(np.dot(eff, ax) / (np.linalg.norm(eff) * np.linalg.norm(ax) + 1e-12)))
        # signed shift on the canonical MHC-I/PD-L1 surface axis
        surf = np.array([p in ("HLA_A", "HLA_E", "CD274") for p in prot[keep]])
        shift = float(eff[surf].mean())
        rows.append({"gene": t, "M_prot": Mp, "S_prot": Sp, "surf_shift": shift, "n_cells": int(m.sum())})
    P = pd.DataFrame(rows).set_index("gene")

    # join RNA-layer scores (from EXEC-2)
    rna = pd.read_csv(OUT / "frangieh_perturbcite_scores.csv").set_index("gene")
    J = P.join(rna[["magnitude", "S", "C", "detectable"]].rename(columns={"magnitude": "M_rna", "S": "S_rna", "C": "C_rna"}), how="inner")

    canon = ["B2M", "CD274", "HLA-A", "HLA-B", "HLA-C", "HLA-E", "IFNGR1", "IFNGR2", "IRF3", "JAK1", "JAK2", "STAT1", "TAPBP"]
    J["is_pos"] = J.index.isin(canon)
    pos = J[J.is_pos]; neg = J[~J.is_pos]

    def auroc(col, sign=1):
        y = J["is_pos"].astype(int).values
        s = sign * J[col].values
        return float(roc_auc_score(y, s)), float(average_precision_score(y, s))

    res = {"dataset": "Frangieh (RNA<->protein)", "n_targets_joined": int(len(J)), "n_pos": int(J.is_pos.sum()),
           # protein-layer recovery of canonical positives (|surf_shift| large & negative for MHC-I loss)
           "protein_recovery_absSurfShift_AUROC_AUPRC": auroc("surf_shift", sign=-1),  # positives DROP surface MHC-I
           "protein_recovery_Sprot_AUROC_AUPRC": auroc("S_prot", sign=1),
           # cross-layer concordance
           "spearman_Srna_Sprot": float(spearmanr(J["S_rna"], J["S_prot"])[0]),
           "spearman_Crna_absSurfShift": float(spearmanr(J["C_rna"], J["surf_shift"].abs())[0]),
           "pos_surf_shift_median": float(pos["surf_shift"].median()),
           "neg_surf_shift_median": float(neg["surf_shift"].median()),
           "pos_vs_neg_surfshift_MW_p": float(mannwhitneyu(pos["surf_shift"], neg["surf_shift"]).pvalue),
           "top5_protein_controllers_by_absSurfShift": list(J["surf_shift"].abs().sort_values(ascending=False).head(5).index),
           }
    J.to_csv(OUT / "frangieh_crosslayer_scores.csv")
    return res

# ---------------- Papalexi: native-layer (PD-L1) rescue ----------------
def papalexi():
    A, Xc = load("PapalexiSatija2021_eccite_protein.h5ad")
    o = A.obs
    prot = list(A.var_names)
    pdl1 = prot.index("PDL1")
    gene = o["perturbation"].astype(str).str.replace(r"g\d+$", "", regex=True).values
    ctrl = gene == "control"
    base = Xc[ctrl, pdl1].mean()
    rows = []
    for g in np.unique(gene):
        if g == "control":
            continue
        m = gene == g
        if m.sum() < MIN_CELLS:
            continue
        rows.append({"gene": g, "pdl1_shift": float(Xc[m, pdl1].mean() - base), "n_cells": int(m.sum())})
    P = pd.DataFrame(rows).set_index("gene")
    canon = {"IFNGR1", "IFNGR2", "JAK1", "JAK2", "STAT1", "STAT2", "STAT3", "STAT5A", "IRF1", "IRF7",
             "NFKBIA", "CMTM6", "MARCH8", "UBE2L6", "PDCD1LG2", "CD274", "SPI1"}
    P["is_pos"] = P.index.isin(canon)
    y = P["is_pos"].astype(int).values
    # PD-L1 regulators reduce surface PD-L1 -> large negative shift; recover by -shift
    res = {"dataset": "Papalexi (native protein PD-L1)", "n_targets": int(len(P)), "n_pos": int(P.is_pos.sum()),
           "pdl1_recovery_AUROC": float(roc_auc_score(y, -P["pdl1_shift"].values)),
           "pdl1_recovery_AUPRC": float(average_precision_score(y, -P["pdl1_shift"].values)),
           "pos_pdl1_shift_median": float(P[P.is_pos]["pdl1_shift"].median()),
           "neg_pdl1_shift_median": float(P[~P.is_pos]["pdl1_shift"].median()),
           "MW_p_pos_vs_neg": float(mannwhitneyu(P[P.is_pos]["pdl1_shift"], P[~P.is_pos]["pdl1_shift"]).pvalue),
           "top5_pdl1_reducers": list(P["pdl1_shift"].sort_values().head(5).index),
           "note": "RNA layer was NOT-EVALUABLE (circular axis); native protein readout (PD-L1) gives a clean functional recovery test.",
           }
    P.to_csv(OUT / "papalexi_protein_scores.csv")
    return res

if __name__ == "__main__":
    out = {"frangieh": frangieh(), "papalexi": papalexi()}
    json.dump(out, open(OUT / "cross_layer_result.json", "w"), indent=2, default=str)
    print(json.dumps(out, indent=2, default=str))
