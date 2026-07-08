#!/usr/bin/env python
"""
Brief 01 — BEHAV3D (GSE172325) correlational proxy for the TSC P3 test.

Pre-registered (confirmed by Abel/Claude Science before any peeking):
  Primary dataset : 10T_vs_13T_exposed_TEGs (n=2444, near-balanced)
  Positive        : super-engaged ; Negative : never-engaged ; drop medium-exposed
                    from the primary test (kept only as an intermediate sanity check).
  Replication     : Pseudotime_TEGs (n=3296), same positive/negative definition.

Confounder guard (run + reported BEFORE the main test):
  1. Cross-tab Cell_type (CD8/CD4) vs engagement class.
     - Pseudotime has a real Cell_type label -> use it.
     - Exposed has NO Cell_type column -> expression-derived CD8 call (CD8A/CD8B > 0).
  2. CD8-identity score = z(CD8A,CD8B,GZMB,PRF1,NKG7) - z(CD4,IL7R) as a COMPETING baseline.
  3. If CD8 fraction differs > 2x between classes -> run the primary test twice:
     (a) all cells, (b) CD8-only stratum.

Verdict: PASS only if TSC beats BOTH the activation baseline AND the CD8-identity baseline
(CI on the AUROC/AUPRC difference excludes 0). Otherwise the honest finding is that the
signal is CD8-identity / activation, not killing capacity.

NO fabrication: labels are the authors' exp_condition; gene sets are the Marson modules
(config/axes.yaml, outputs/movability_gate.json) + a documented GO/Reactome synapse set.
"""
import gzip, json, warnings
import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve, precision_recall_curve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
sc.settings.verbosity = 0
RNG = np.random.default_rng(0)
DATA = "data/behav3d"
OUT = "outputs/behav3d_p3"

# ----------------------------------------------------------------------------
# Gene sets (see config/axes.yaml + outputs/movability_gate.json + report sec 3/4)
# ----------------------------------------------------------------------------
GS = {
    # L1 durable state = memory/stem  MINUS  exhaustion
    "memory_stem": ["TCF7", "SELL", "IL7R", "CCR7", "LEF1", "BACH2", "KLF2", "FOXO1", "ID3"],
    "exhaustion":  ["PDCD1", "HAVCR2", "LAG3", "TIGIT", "ENTPD1", "TOX", "TOX2", "BATF"],
    # L2 tissue access = migration / chemotaxis (Marson R_migration module)
    "migration":   ["CCR7", "SELL", "S1PR1", "ITGAL", "RHOA", "WASF2", "CORO1A", "CXCR3"],
    # L3 synapse assembly / cytoskeleton — assembled from GO/Reactome:
    #   immune synapse, actin cytoskeleton, TCR signaling, MTOC/adhesion (report sec 4.2)
    "synapse":     ["LCK", "LAT", "ZAP70", "PLCG1", "VAV1", "LCP2", "ITK", "FYN",
                    "WAS", "WASF2", "ARPC2", "ARPC3", "ACTR2", "ACTR3", "CORO1A",
                    "RHOA", "CDC42", "RAC2", "TLN1", "PXN", "MYH9", "CD2", "CD58"],
    # L4 serial killing (Marson R_killing module)
    "killing":     ["GZMB", "PRF1", "NKG7", "GNLY", "IFNG", "FASLG", "GZMA"],
    # Baseline 1: activation / effector magnitude (axes.yaml activation_tcr + th1_effector)
    "activation":  ["IL2", "IL2RA", "CD69", "TNF", "IRF4", "NR4A1",
                    "IFNG", "TBX21", "EOMES", "STAT1", "IRF1"],
    # Baseline 2 components: CD8-identity  (positive minus CD4 markers)
    "cd8_pos":     ["CD8A", "CD8B", "GZMB", "PRF1", "NKG7"],
    "cd4_pos":     ["CD4", "IL7R"],
}


def zscore(x):
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x - x.mean()


def load_dataset(counts_gz, meta_gz, name):
    """Load genes x cells counts, align to metadata, return AnnData (cells x genes)."""
    print(f"\n[load] {name}: reading {counts_gz}")
    df = pd.read_csv(counts_gz, index_col=0)          # genes x cells
    df.index = df.index.astype(str).str.strip('"')
    df.columns = df.columns.astype(str).str.strip('"')
    meta = pd.read_csv(meta_gz, index_col=0)
    meta.index = meta.index.astype(str).str.strip('"')
    common = [c for c in df.columns if c in meta.index]
    print(f"[load] counts cells={df.shape[1]} genes={df.shape[0]} | meta cells={meta.shape[0]} | matched={len(common)}")
    X = df[common].T                                   # cells x genes
    ad = sc.AnnData(X.values.astype(np.float32),
                    obs=meta.loc[common].copy(),
                    var=pd.DataFrame(index=df.index))
    ad.obs_names = common
    ad.obs["n_counts"] = np.asarray(X.values.sum(1)).ravel()
    return ad


def score_modules(ad):
    """Normalize, log1p, score every gene set; build TSC and baselines. Report coverage."""
    ad.layers["counts"] = ad.X.copy()
    sc.pp.normalize_total(ad, target_sum=1e4)
    sc.pp.log1p(ad)
    cover = {}
    for k, genes in GS.items():
        present = [g for g in genes if g in ad.var_names]
        cover[k] = (len(present), len(genes), present)
        sc.tl.score_genes(ad, present, score_name=f"s_{k}", ctrl_size=50, random_state=0)
    o = ad.obs
    # L1..L4 loadings
    o["L1_state"] = zscore(o["s_memory_stem"]) - zscore(o["s_exhaustion"])
    o["L2_migration"] = zscore(o["s_migration"])
    o["L3_synapse"] = zscore(o["s_synapse"])
    o["L4_killing"] = zscore(o["s_killing"])
    # TSC = mean of z-scored L1..L4 (report sec 2: 'mean of z-scored loadings')
    o["TSC"] = np.mean(np.c_[zscore(o["L1_state"]), o["L2_migration"],
                             o["L3_synapse"], o["L4_killing"]], axis=1)
    # Baselines
    o["b_activation"] = zscore(o["s_activation"])
    o["b_cd8_identity"] = zscore(o["s_cd8_pos"]) - zscore(o["s_cd4_pos"])
    o["b_total_counts"] = zscore(np.log1p(o["n_counts"]))
    return cover


def diff_ci(y, sa, sb, n_boot=2000):
    """Bootstrap 95% CI on AUROC(a)-AUROC(b) and AUPRC(a)-AUPRC(b), paired resampling."""
    y = np.asarray(y); sa = np.asarray(sa); sb = np.asarray(sb)
    n = len(y)
    droc, dpr = [], []
    for _ in range(n_boot):
        idx = RNG.integers(0, n, n)
        yy = y[idx]
        if yy.sum() == 0 or yy.sum() == len(yy):
            continue
        droc.append(roc_auc_score(yy, sa[idx]) - roc_auc_score(yy, sb[idx]))
        dpr.append(average_precision_score(yy, sa[idx]) - average_precision_score(yy, sb[idx]))
    return (np.percentile(droc, [2.5, 97.5]), np.mean(droc),
            np.percentile(dpr, [2.5, 97.5]), np.mean(dpr))


def evaluate(o, mask, label, tag):
    """Run TSC-vs-baselines evaluation on a subset. Returns a results dict."""
    sub = o.loc[mask]
    y = (sub["engaged_class"] == "super-engaged").astype(int).values
    print(f"\n=== EVAL [{tag}] {label}: n={len(sub)}  pos(super)={y.sum()}  neg(never)={len(y)-y.sum()}")
    scores = {"TSC": sub["TSC"].values,
              "activation": sub["b_activation"].values,
              "cd8_identity": sub["b_cd8_identity"].values,
              "total_counts": sub["b_total_counts"].values}
    res = {"tag": tag, "label": label, "n": int(len(sub)),
           "n_pos": int(y.sum()), "n_neg": int(len(y) - y.sum()), "metrics": {}}
    print(f"{'score':<14}{'AUROC':>8}{'AUPRC':>8}")
    for k, s in scores.items():
        auroc = roc_auc_score(y, s); auprc = average_precision_score(y, s)
        res["metrics"][k] = {"auroc": float(auroc), "auprc": float(auprc)}
        print(f"{k:<14}{auroc:>8.3f}{auprc:>8.3f}")
    # per-loading AUROC — shows WHICH loadings drive TSC up/down vs engagement
    print("  per-loading AUROC (super=pos):")
    res["loading_auroc"] = {}
    for L in ["L1_state", "L2_migration", "L3_synapse", "L4_killing"]:
        a = roc_auc_score(y, sub[L].values)
        res["loading_auroc"][L] = float(a)
        print(f"    {L:<14}{a:>8.3f}")
    print(f"\n  Bootstrap 95% CI on difference (TSC - baseline), n_boot=2000:")
    res["diff_vs"] = {}
    for b in ["activation", "cd8_identity", "total_counts"]:
        ci_roc, m_roc, ci_pr, m_pr = diff_ci(y, scores["TSC"], scores[b])
        excl = "excludes 0 ✔" if (ci_roc[0] > 0 or ci_roc[1] < 0) else "spans 0"
        res["diff_vs"][b] = {"dAUROC_mean": float(m_roc), "dAUROC_ci": [float(ci_roc[0]), float(ci_roc[1])],
                             "dAUPRC_mean": float(m_pr), "dAUPRC_ci": [float(ci_pr[0]), float(ci_pr[1])]}
        print(f"  TSC - {b:<13}: dAUROC={m_roc:+.3f} [{ci_roc[0]:+.3f},{ci_roc[1]:+.3f}] ({excl}) | "
              f"dAUPRC={m_pr:+.3f} [{ci_pr[0]:+.3f},{ci_pr[1]:+.3f}]")
    # Spearman TSC vs each baseline (orthogonality)
    res["spearman"] = {}
    print("  Spearman(TSC, baseline):")
    for b in ["activation", "cd8_identity", "total_counts"]:
        rho = spearmanr(sub["TSC"], sub[f"b_{b}"]).statistic
        res["spearman"][b] = float(rho)
        print(f"    TSC vs {b:<13}: rho={rho:+.3f}")
    return res


def main():
    results = {}
    coverage = {}
    per_cell = []

    # ---- PRIMARY: exposed ----
    adE = load_dataset(f"{DATA}/GSE172325_10T_vs_13T_exposed_TEGs_counts.csv.gz",
                       f"{DATA}/GSE172325_10T_vs_13T_exposed_TEGs_metadata.csv.gz", "exposed")
    coverage["exposed"] = score_modules(adE)
    oE = adE.obs
    oE["engaged_class"] = oE["exp_condition"]
    # exposed lacks Cell_type -> expression-derived CD8 call
    counts = adE.layers["counts"]
    cd8a = np.asarray(counts[:, adE.var_names.get_loc("CD8A")]).ravel() if "CD8A" in adE.var_names else np.zeros(adE.n_obs)
    cd8b = np.asarray(counts[:, adE.var_names.get_loc("CD8B")]).ravel() if "CD8B" in adE.var_names else np.zeros(adE.n_obs)
    oE["cd8_expr_call"] = np.where((cd8a > 0) | (cd8b > 0), "CD8+", "CD8-")

    # ---- REPLICATION attempt: pseudotime -> NOT-EVALUABLE (barcode namespace collision) ----
    # The pre-registered replication (Pseudotime_TEGs, n=3296) has NO valid count matrix on GEO:
    #   * GSE172325_Pseudotime_TEGs_counts.csv.gz shares 7664/7664 barcodes with the Non_exposed
    #     matrix (it is the non-exposed counts) -> only 254 spurious matches to pseudotime meta.
    #   * The 1516 pseudotime-meta barcodes that "match" the EXPOSED counts are well-ID collisions
    #     across independent plate layouts, NOT the same cells: the same well ID carries
    #     CONTRADICTORY engagement labels between the two metadata files (proven below).
    # Joining on these barcodes would attach WRONG expression to cells -> we refuse and report
    # the replication as NOT-EVALUABLE (per CLAUDE.md hard rule 1: no fabricated labels/joins).
    print("\n" + "#" * 78 + "\n# REPLICATION (pseudotime) — NOT-EVALUABLE: barcode namespace collision\n" + "#" * 78)
    pse_meta = pd.read_csv(f"{DATA}/GSE172325_Pseudotime_TEGs_metadata.csv.gz", index_col=0)
    pse_meta.index = pse_meta.index.astype(str).str.strip('"')
    shared = [b for b in pse_meta.index if b in oE.index]
    contradict = pd.crosstab(oE.loc[shared, "exp_condition"], pse_meta.loc[shared, "exp_condition"])
    print(f"pseudotime-meta cells matching exposed-COUNTS barcodes: {len(shared)}/{len(pse_meta)}")
    print("Same barcode, exposed label (rows) vs pseudotime label (cols) — should be diagonal if same cells:")
    print(contradict.to_string())
    # off-diagonal mass = proof of collision (e.g. exposed super-engaged -> pseudo never-engaged)
    results["replication"] = {
        "verdict": "NOT-EVALUABLE",
        "reason": "No GEO count matrix corresponds to the Pseudotime engagement metadata; "
                  "well-ID barcodes collide across independent experiments (same ID, contradictory "
                  "engagement labels), so any expression join is invalid.",
        "pseudo_counts_is_nonexposed": True,
        "n_pseudo_meta": int(len(pse_meta)),
        "n_spurious_match_exposed_counts": int(len(shared)),
        "label_contradiction_crosstab": contradict.to_dict(),
    }

    # ---------- CONFOUNDER GUARD (report FIRST) ----------
    print("\n" + "#" * 78 + "\n# CONFOUNDER GUARD: Cell_type (CD8/CD4) vs engagement class\n" + "#" * 78)
    guard = {}

    def cd8_frac(df, cd8col, cls, is_cd8):
        s = df.loc[df["engaged_class"] == cls, cd8col].astype(str)
        pos = int(s.map(is_cd8).sum())
        return pos, len(s), (pos / len(s) if len(s) else float("nan"))

    # exposed (expression-derived CD8 call)
    print("\n[exposed] expression-derived CD8 call (CD8A/CD8B>0); NO author Cell_type column")
    ct = pd.crosstab(oE["engaged_class"], oE["cd8_expr_call"])
    print(ct.to_string())
    is8 = lambda v: v == "CD8+"
    fs = cd8_frac(oE, "cd8_expr_call", "super-engaged", is8); fn = cd8_frac(oE, "cd8_expr_call", "never-engaged", is8)
    ratio_E = fs[2] / fn[2] if fn[2] else float("nan")
    print(f"  CD8+ frac  super-engaged={fs[2]:.3f} ({fs[0]}/{fs[1]}) | never-engaged={fn[2]:.3f} ({fn[0]}/{fn[1]}) | ratio={ratio_E:.2f}x")
    guard["exposed"] = {"source": "expression-derived (CD8A/CD8B>0)", "crosstab": ct.to_dict(),
                        "cd8frac_super": fs[2], "cd8frac_never": fn[2], "ratio": ratio_E}
    results["confounder_guard"] = guard

    heavy_conf_E = (ratio_E > 2 or ratio_E < 0.5)
    print(f"\n  Heavy CD8/CD4 confound (>2x)?  exposed={heavy_conf_E}")

    # ---------- PRIMARY TEST ----------
    print("\n" + "#" * 78 + "\n# PRIMARY TEST — exposed (super vs never)\n" + "#" * 78)
    prim = oE["engaged_class"].isin(["super-engaged", "never-engaged"])
    results["exposed_all"] = evaluate(oE, prim, "exposed super-vs-never (all cells)", "exposed_all")
    # CD8-stratified (per guard rule 3) — always report, decisive if heavy confound
    cd8_mask = prim & (oE["cd8_expr_call"] == "CD8+")
    if cd8_mask.sum() > 30 and (oE.loc[cd8_mask, "engaged_class"] == "super-engaged").sum() > 5:
        results["exposed_cd8only"] = evaluate(oE, cd8_mask, "exposed super-vs-never (CD8+ stratum)", "exposed_cd8only")

    # ---------- intermediate sanity: TSC & activation ordering never < medium < super ----------
    print("\n[sanity] mean score by class (activation expected never<medium<super):")
    order = {}
    for sc_name in ["TSC", "b_activation"]:
        means = oE.groupby("engaged_class")[sc_name].mean().to_dict()
        order[sc_name] = {k: float(v) for k, v in means.items()}
        print(f"  {sc_name}: " + " | ".join(f"{k}={v:+.3f}" for k, v in sorted(means.items(), key=lambda x: x[1])))
    results["score_by_class"] = order

    # ---------- write per-cell CSV (exposed = the only evaluable dataset) ----------
    cols = ["engaged_class", "TSC", "L1_state", "L2_migration", "L3_synapse", "L4_killing",
            "b_activation", "b_cd8_identity", "b_total_counts", "n_counts"]
    dfE = oE[cols].copy(); dfE.insert(0, "dataset", "exposed"); dfE["cd8"] = oE["cd8_expr_call"].values
    dfE.to_csv(f"{OUT}/behav3d_tsc_scores.csv")
    print(f"\n[write] {OUT}/behav3d_tsc_scores.csv ({len(dfE)} cells)")

    results["coverage"] = {ds: {k: {"present": v[0], "total": v[1]} for k, v in cov.items()}
                           for ds, cov in coverage.items()}
    with open(f"{OUT}/behav3d_p3_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"[write] {OUT}/behav3d_p3_results.json")

    # ---------- figure ----------
    make_figure(oE, results)
    return results


def make_figure(oE, results):
    COL = {"TSC": "#E45756", "activation": "#54A24B", "cd8_identity": "#4C78A8", "total_counts": "#B0B0B0"}
    fig, ax = plt.subplots(1, 4, figsize=(20, 4.6))
    m = oE["engaged_class"].isin(["super-engaged", "never-engaged"])
    sub = oE.loc[m]; y = (sub["engaged_class"] == "super-engaged").astype(int).values
    scoremap = {"TSC": sub["TSC"], "activation": sub["b_activation"],
                "cd8_identity": sub["b_cd8_identity"], "total_counts": sub["b_total_counts"]}
    # (0) TSC distribution by class
    a = ax[0]
    for cls, c in [("never-engaged", "#4C78A8"), ("medium-exposed", "#B0B0B0"), ("super-engaged", "#E45756")]:
        v = oE.loc[oE["engaged_class"] == cls, "TSC"]
        if len(v):
            a.hist(v, bins=40, alpha=0.55, label=cls, color=c, density=True)
    a.set_title("exposed: TSC by engagement"); a.set_xlabel("TSC score"); a.legend(fontsize=8)
    # (1) ROC
    a = ax[1]
    for k, s in scoremap.items():
        fpr, tpr, _ = roc_curve(y, s); a.plot(fpr, tpr, color=COL[k], lw=1.8, label=f"{k} ({roc_auc_score(y, s):.2f})")
    a.plot([0, 1], [0, 1], "k--", lw=0.7); a.set_title("ROC (super vs never)")
    a.set_xlabel("FPR"); a.set_ylabel("TPR"); a.legend(fontsize=8)
    # (2) PR
    a = ax[2]
    for k, s in scoremap.items():
        pr, rc, _ = precision_recall_curve(y, s); a.plot(rc, pr, color=COL[k], lw=1.8, label=f"{k} ({average_precision_score(y, s):.2f})")
    a.axhline(y.mean(), color="k", ls="--", lw=0.7); a.set_title("PR (super vs never)")
    a.set_xlabel("Recall"); a.set_ylabel("Precision"); a.legend(fontsize=8)
    # (3) per-loading AUROC bars (why TSC fails)
    a = ax[3]
    la = results["exposed_all"]["loading_auroc"]
    ks = list(la.keys()); vals = [la[k] for k in ks]
    bars = a.barh(ks, vals, color=["#E45756" if v < 0.5 else "#54A24B" for v in vals])
    a.axvline(0.5, color="k", ls="--", lw=0.8); a.set_xlim(0, 1)
    a.set_title("per-loading AUROC (super=pos)"); a.set_xlabel("AUROC")
    for b, v in zip(bars, vals):
        a.text(v + 0.01 if v < 0.85 else v - 0.12, b.get_y() + b.get_height() / 2, f"{v:.2f}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/behav3d_p3.png", dpi=130)
    print(f"[write] {OUT}/behav3d_p3.png")


if __name__ == "__main__":
    main()
