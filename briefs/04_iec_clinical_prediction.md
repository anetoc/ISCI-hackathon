# Brief 04 — Does any IEC axis predict CAR-T response? (honest patient-level test)

**Goal:** test whether an Immune Engagement Capacity axis (A_persist, or the coupled
effector/exhaustion axis) predicts clinical response in the CAR-T atlas, with **honest
patient-level cross-validation**, against strong baselines. This is the highest-Impact and
highest-risk deliverable. **It has failed once before** (D4: T-state signature, CV-AUROC
~chance, on underpowered cohorts n=9/n=65). The atlas gives real power; a well-powered NULL
is itself a valid, publishable result. Read `reports/immune_engagement_capacity.md` first.

## PRECONDITION MET — Brief 03 verdict = EVALUABLE. Values below are VERIFIED from the download.
Gate confirmed (`outputs/cart_atlas/gate_result.json`): 455,370 cells × 48,740 genes;
IEC gene coverage 100%; within-patient label consistency perfect (0 patients with >1 value).
Atlas object: `data_public/cart/Atlas_integ_scArches_FINAL_V5.h5ad` — X = raw integer counts,
var_names = HGNC symbols, NO layers/scVI-latent (normalize/log1p yourself). Drop healthy-donor
and mouse cells (they carry no response label — already excluded by the label gate).

Verified column mapping (use exactly these):
- `PATIENT_COL` = **`Norm_Patient_Name`** (119 patients; 87 labeled)
- `STUDY_COL` = **`orig_ident`** (14 studies)
- `RESPONSE_COL` = **`Max_Response`** with **R = {CR, PR}** (60) vs **NR = {NR}** (27).
  Robustness variant (must agree): `Anytime_Response` (Yes=60 / No=27) — identical split.
- Verified counts: **n_patients = 87, n_responders = 60, n_nonresponders = 27**
- Disease + CRS/ICANS also present in `atlas_patient_response.csv` (`disease`, `CRS`, `ICANS`).

## Pre-registration (write this to the report BEFORE computing AUROC)
- **Unit of analysis = patient** (not cell). Aggregate cell-level axis scores to one value per
  patient (mean, and also fraction-of-cells-above-median as a robustness variant).
- **Primary predictor:** A_persist (the clean axis). **Secondary:** the effector/exhaustion
  axis (kill − resist, since they are coupled — see §3a). Test each SEPARATELY; do not average.
- **Cross-validation — TWO tiers, report BOTH; the stricter is the headline:**
  1. **leave-one-PATIENT-out** (group = `PATIENT_COL`) — necessary but NOT sufficient here.
  2. **leave-one-STUDY-out** (group = `STUDY_COL`) — **THE PRIMARY, DECISIVE test.** The gate
     showed response is severely study-confounded: only 5/9 labeled studies have both R and NR;
     22/27 NR come from just 2 studies (Deng 13, Haradvala 9); several studies are 100%
     responder (Sheih 4/0, Jordana 3/0, Melenhorst 2/0). So leave-patient-out can score well by
     memorizing per-study batch signatures = fake signal. **Only leave-study-out isolates
     biology from batch.** If leave-patient-out passes but leave-study-out collapses to chance,
     the verdict is NULL (batch, not biology) — state this explicitly.
  No cell from a test patient/study may appear in training. Report grouped CV-AUROC for both.
- **Baselines that must be beaten** (same CV):
  1. effect magnitude / total counts per patient,
  2. CD8 fraction (or CD8-identity score) per patient,
  3. cell-count / QC depth per patient,
  4. a null permutation (shuffle response labels across patients, 1000×) → empirical p.
- **Verdict rule (pre-set):** PASS only if the axis's **leave-one-STUDY-out** CV-AUROC beats
  ALL baselines AND its bootstrap 95% CI excludes 0.5 AND the permutation p < 0.05. A pass on
  leave-patient-out but not leave-study-out = NULL (batch). Anything else = NULL. State the
  number explicitly for BOTH CV tiers.
- **Disease stratum:** the atlas is NHL-dominated but mixed (ALL, etc. present). Report the
  primary within the dominant-disease stratum too, so response is not a disease proxy.

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
