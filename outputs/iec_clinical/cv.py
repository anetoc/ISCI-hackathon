#!/usr/bin/env python
"""Brief 04 step 2 — honest patient-level CV response prediction.

Unit = patient. Primary CV = leave-one-STUDY-out (headline); leave-one-patient-out secondary.
Pooled out-of-fold predictions -> one AUROC. Bootstrap 95% CI + permutation p (1000x).
An axis PASSES only if leave-study-out AUROC beats ALL baselines AND boot CI excludes 0.5
AND perm-p < 0.05. Otherwise NULL.
"""
import json, sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

OUTDIR = "/mnt/dados2/abel-tsc/repo/outputs/iec_clinical"
RNG = np.random.default_rng(12345)
NPERM, NBOOT = 1000, 2000

AXES = {"A_persist": "A_persist", "A_eff_exh": "A_eff_exh"}      # primary, secondary
AGGS = ["mean", "frachi"]
BASELINES = ["b_total_counts", "b_cd8_frac", "b_n_cells", "b_n_features"]


def oof_predictions(X, y, groups):
    """Grouped leave-one-group-out; return out-of-fold predicted prob per sample."""
    X = np.asarray(X, float).reshape(-1, 1); y = np.asarray(y, int); groups = np.asarray(groups)
    pred = np.full(len(y), np.nan)
    for g in np.unique(groups):
        te = groups == g; tr = ~te
        ytr = y[tr]
        if len(np.unique(ytr)) < 2:                 # degenerate train fold -> predict prior
            pred[te] = ytr.mean() if len(ytr) else 0.5
            continue
        sc = StandardScaler().fit(X[tr])
        lr = LogisticRegression(max_iter=1000).fit(sc.transform(X[tr]), ytr)
        pred[te] = lr.predict_proba(sc.transform(X[te]))[:, 1]
    return pred


def pooled_auroc(pred, y):
    y = np.asarray(y, int)
    if len(np.unique(y)) < 2:
        return np.nan
    return roc_auc_score(y, pred)


def evaluate(x, y, groups, do_perm=True):
    pred = oof_predictions(x, y, groups)
    auc = pooled_auroc(pred, y)
    # bootstrap CI over patients (on OOF pairs)
    y = np.asarray(y, int); n = len(y); boots = []
    for _ in range(NBOOT):
        idx = RNG.integers(0, n, n)
        if len(np.unique(y[idx])) < 2:
            continue
        boots.append(roc_auc_score(y[idx], pred[idx]))
    ci = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))) if boots else (np.nan, np.nan)
    # permutation p: shuffle y across patients, redo full grouped CV
    p = np.nan
    if do_perm:
        ge = 0
        for _ in range(NPERM):
            yp = RNG.permutation(y)
            ap = pooled_auroc(oof_predictions(x, yp, groups), yp)
            if not np.isnan(ap) and ap >= auc:
                ge += 1
        p = (1 + ge) / (1 + NPERM)
    return {"auroc": float(auc), "ci": ci, "perm_p": float(p) if do_perm else None}


def run_compartment(tag, stratum=None):
    t = pd.read_csv(f"{OUTDIR}/patient_axis_scores_{tag}.csv")
    if stratum:
        t = t[t["disease"] == stratum].reset_index(drop=True)
    y = t["R"].values; study = t["study"].values; pid = t["patient_id"].values
    n_studies_both = int(((pd.crosstab(t.study, t.R).min(axis=1)) > 0).sum())
    out = {"tag": tag, "stratum": stratum or "all_disease",
           "n_patients": int(len(t)), "n_R": int(y.sum()), "n_NR": int((y == 0).sum()),
           "n_studies": int(t.study.nunique()), "n_studies_both_classes": n_studies_both,
           "tests": {}, "baselines": {}}
    # axes x aggregations = 4 tests, both CV tiers
    for axname, col in AXES.items():
        for agg in AGGS:
            feat = t[f"{col}__{agg}"].values
            key = f"{axname}__{agg}"
            out["tests"][key] = {
                "leave_study_out": evaluate(feat, y, study),
                "leave_patient_out": evaluate(feat, y, pid),
            }
    # baselines (leave-study-out is what the axis must beat; also patient-out for completeness)
    for b in BASELINES:
        feat = t[b].values
        out["baselines"][b] = {
            "leave_study_out": evaluate(feat, y, study, do_perm=False),
            "leave_patient_out": evaluate(feat, y, pid, do_perm=False),
        }
    return out


results = {}
for tag in ["all", "infusionproduct"]:
    print(f"[run] compartment={tag}", flush=True)
    results[tag] = run_compartment(tag)
# NHL stratum on the primary compartment
print("[run] NHL stratum (all compartment)", flush=True)
results["all_NHL"] = run_compartment("all", stratum="NHL")

json.dump(results, open(f"{OUTDIR}/cv_results.json", "w"), indent=2, default=str)

# ---- console summary + verdict ----
def summarize(res, label):
    print(f"\n==== {label}: n={res['n_patients']} ({res['n_R']}R/{res['n_NR']}NR), "
          f"studies={res['n_studies']} (both-class={res['n_studies_both_classes']}) ====")
    base_lso = {b: res['baselines'][b]['leave_study_out']['auroc'] for b in BASELINES}
    print("  baselines (leave-study-out AUROC):", {k: round(v, 3) for k, v in base_lso.items()})
    best_base = max(base_lso.values())
    for key, d in res['tests'].items():
        lso = d['leave_study_out']; lpo = d['leave_patient_out']
        print(f"  {key:22s} LSO AUROC={lso['auroc']:.3f} CI[{lso['ci'][0]:.3f},{lso['ci'][1]:.3f}] "
              f"permp={lso['perm_p']:.3f} | LPO AUROC={lpo['auroc']:.3f}")
    return best_base

for tag, label in [("all", "PRIMARY compartment=ALL"), ("all_NHL", "NHL stratum"),
                   ("infusionproduct", "ROBUSTNESS compartment=Infusion_Product")]:
    summarize(results[tag], label)

# Verdict on primary axis (A_persist, mean agg), primary compartment (all), leave-study-out
res = results["all"]; prim = res["tests"]["A_persist__mean"]["leave_study_out"]
best_base = max(res['baselines'][b]['leave_study_out']['auroc'] for b in BASELINES)
verdict = ("PASS" if (prim["auroc"] > best_base and prim["ci"][0] > 0.5 and prim["perm_p"] < 0.05) else "NULL")
print(f"\n#### PRIMARY VERDICT (A_persist mean, leave-study-out): {verdict}")
print(f"     AUROC={prim['auroc']:.3f} CI[{prim['ci'][0]:.3f},{prim['ci'][1]:.3f}] permp={prim['perm_p']:.3f} "
      f"| best baseline LSO AUROC={best_base:.3f}")
json.dump({"verdict": verdict, "primary": prim, "best_baseline_lso": best_base},
          open(f"{OUTDIR}/verdict.json", "w"), indent=2, default=str)
print("[done]")
