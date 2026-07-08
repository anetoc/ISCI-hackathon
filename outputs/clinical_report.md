# ISCI Clinical Bridge — CAR-T Response Report

**Scope.** Whether the T-cell-state controllers nominated by ISCI, or the T-state phenotypes they define, separate CAR-T responders from non-responders in the infusion product. This is the translational test that would connect a Perturb-seq controllership signal to patient outcome.

**Cohort.** Functional CAR-T single-cell atlas (Zenodo 19066393), infusion-product cells with a labeled clinical response: **117,233 cells across 70 patients (44 responders, 26 non-responders)**. Analysis at the **patient level** (patient-mean signatures / composition fractions) to avoid pseudoreplication; separation quantified by Mann–Whitney and by 5-fold cross-validated AUROC.

## Result: this bridge is a negative result

- **T-state signature scores (7 axes):** 0 of 7 significant at p < 0.05. The best axis (exhaustion-like) reached AUROC 0.61. Directions were biologically coherent — non-responders trended toward higher exhaustion and terminal-cytotoxic signal — but none survived as a predictor.
- **Cross-validated prediction:** signature-only AUROC 0.556, composition-only 0.518, combined 0.530 — **at chance** (cohort base rate 0.63).
- **Verdict:** patient-level mean T-state signatures **do not robustly predict CAR-T response** in this cohort.

## The one suggestive signal: Treg fraction

Of 11 cell-state compositions, only **regulatory T-cell fraction** separated the groups (uncorrected p = 0.040, AUROC 0.65): **non-responders carried roughly twice the Treg fraction in the infusion product** (6.4% vs 3.3%). This is directionally consistent with the immunosuppression hypothesis for CAR-T failure, but it is a **single uncorrected hit among 11 tests** and does not survive multiple-comparison correction. Treat it as hypothesis-generating, not as a biomarker.

## Interpretation for a hematologist

The honest reading is that a controllership signal derived from a CD4+ *in-vitro* Perturb-seq screen does **not** transfer to a clean prediction of CAR-T clinical response in this atlas. Two plausible reasons: (1) the outcome is driven by CD8/effector biology and tumor context not captured by CD4 TCR-stimulation axes; (2) the cohort (70 products) is underpowered for the effect sizes involved. The Treg-fraction observation is the only lead worth following, ideally in a larger cohort with product-composition QC.

**This negative is reported deliberately.** The methodological contribution of ISCI — that in-dataset controllability is magnitude-confounded and needs a magnitude-independent test — stands independently of the clinical bridge; the bridge simply shows that the *right* external outcome is hard to reach with current public data.

_Not medical advice; a research analysis of public data. Clinical decisions require a qualified clinician with full patient context._

_Artifacts: outputs/d4/d4_summary.json, response_separation.csv, composition_separation.csv._
