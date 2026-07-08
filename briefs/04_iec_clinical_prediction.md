# Brief 04 — Does any IEC axis predict CAR-T response? (honest patient-level test)

**Goal:** test whether an Immune Engagement Capacity axis (A_persist, or the coupled
effector/exhaustion axis) predicts clinical response in the CAR-T atlas, with **honest
patient-level cross-validation**, against strong baselines. This is the highest-Impact and
highest-risk deliverable. **It has failed once before** (D4: T-state signature, CV-AUROC
~chance, on underpowered cohorts n=9/n=65). The atlas gives real power; a well-powered NULL
is itself a valid, publishable result. Read `reports/immune_engagement_capacity.md` first.

## HARD PRECONDITION
**Run Brief 03 first and confirm its verdict is EVALUABLE.** Do not start Brief 04 until
`outputs/cart_atlas/atlas_structure_report.md` says patient-level response labels exist and
are mappable. Fill the placeholders below from Brief 03's verified `atlas_patient_response.csv`
and structure report — do NOT hardcode column names guessed here.

Placeholders to fill from Brief 03:
- `RESPONSE_COL` = <the verified per-patient response column>
- `RESPONSE_POS` / `RESPONSE_NEG` = <the responder / non-responder category labels>
- `PATIENT_COL` = <the patient-ID column>
- `STUDY_COL` = <the study/batch column>
- `n_patients`, `n_responders`, `n_nonresponders` = <verified counts>

## Pre-registration (write this to the report BEFORE computing AUROC)
- **Unit of analysis = patient** (not cell). Aggregate cell-level axis scores to one value per
  patient (mean, and also fraction-of-cells-above-median as a robustness variant).
- **Primary predictor:** A_persist (the clean axis). **Secondary:** the effector/exhaustion
  axis (kill − resist, since they are coupled — see §3a). Test each SEPARATELY; do not average.
- **Cross-validation: leave-ONE-PATIENT-out** (or stratified group-K-fold with `PATIENT_COL`
  as the group). No cell from a test patient may appear in training. Report grouped CV-AUROC.
- **Baselines that must be beaten** (same CV):
  1. effect magnitude / total counts per patient,
  2. CD8 fraction (or CD8-identity score) per patient,
  3. cell-count / QC depth per patient,
  4. a null permutation (shuffle response labels across patients, 1000×) → empirical p.
- **Verdict rule (pre-set):** PASS only if the axis's grouped CV-AUROC beats ALL baselines
  AND its bootstrap 95% CI (over patients) excludes 0.5 AND the permutation p < 0.05. Anything
  else = NULL. State the number explicitly.

## Confound & leakage guards (report each)
1. **Study confound:** cross-tab `STUDY_COL` × response at patient level. If responders and
   non-responders come from different studies, batch = response, and any signal is suspect.
   Report per-study CV-AUROC and, if feasible, leave-one-STUDY-out as the stricter test.
2. **Multiple testing:** 2 axes × 2 aggregations = 4 tests. Report all 4; apply Bonferroni/BH.
   Do not report only the best.
3. **Product-vs-patient:** if the atlas mixes infusion-product cells and post-infusion cells,
   restrict to the pre-registered compartment (whichever Brief 03 shows carries the label).

## Deliverables (commit)
- `outputs/iec_clinical/iec_prediction_report.md` — the pre-registration block, the 4-test
  table (axis × aggregation → grouped CV-AUROC, bootstrap CI, perm-p), all baselines, the
  study-confound cross-tab, and the explicit **PASS / NULL** verdict with the number.
- `outputs/iec_clinical/patient_axis_scores.csv` — per-patient axis scores + response + study.
- `outputs/iec_clinical/iec_prediction.png` — CV-AUROC per axis vs baselines, with CIs; and a
  patient-level axis-score-by-response strip/box plot.
- Commit: `IEC clinical: patient-level CV response prediction (PASS|NULL) vs baselines`.

## Honesty rules (CLAUDE.md)
- Never fabricate or impute a response label. If a patient lacks a label, drop them and report
  the effective n.
- Report the NULL if it is a NULL. Compare explicitly to the D4 prior negative — a powered
  confirmation of the negative is a real result, not a failure to be hidden.
- No cell-level AUROC headline (pseudo-replication). Patient is the unit. Always.
- If leave-one-study-out collapses the signal that leave-one-patient-out showed, the signal was
  batch — say so.
