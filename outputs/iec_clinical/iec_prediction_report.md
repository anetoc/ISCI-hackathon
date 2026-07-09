# Brief 04 — Does any IEC axis predict CAR-T response? (patient-level CV)

**VERDICT: NULL (well-powered).** No IEC axis predicts CAR-T clinical response under the
pre-registered, decisive **leave-one-STUDY-out** cross-validation. The primary axis
**A_persist** reaches leave-study-out CV-AUROC **0.533** (bootstrap 95% CI **[0.408, 0.650]**,
includes 0.5; permutation **p = 0.138**), and it is **beaten by the CD8-fraction baseline
(0.585)**. The apparent signal under the weaker leave-one-patient-out CV (AUROC 0.643)
**collapses to chance under leave-study-out** — the textbook signature of **batch, not
biology**. This is a powered confirmation of the earlier D4 negative, and a valid result.

---

## 1. Pre-registration (fixed before computing any AUROC)

- **Unit of analysis = patient** (never cell; no cell-level AUROC headline → avoids
  pseudo-replication). Cell-level axis scores aggregated to one value per patient by **mean**
  (primary) and **fraction-of-cells-above-global-median** (robustness).
- **Predictors (tested separately, not averaged):** primary = **A_persist**
  = mean-z(memory/stem + migration + synapse); secondary = **A_eff_exh = A_kill − A_resist**
  (the coupled effector/exhaustion axis — kill and exhaustion-resistance entangle at ρ≈−0.45,
  `immune_engagement_capacity.md` §3a, so they are one axis, not two).
- **CV — two tiers, stricter is the headline:** (1) leave-one-**STUDY**-out (group `orig_ident`)
  = **PRIMARY/DECISIVE**; (2) leave-one-**PATIENT**-out (group `Norm_Patient_Name`) = secondary.
  No cell from a test patient/study appears in training. Pooled out-of-fold predictions → one
  AUROC per tier (single-class test folds still contribute their OOF predictions).
- **Baselines that must be beaten (same CV):** per-patient total counts (magnitude), CD8
  fraction, cell count (QC depth), mean n_features; plus a **label-permutation null** (shuffle
  response across patients, 1000×) → empirical p.
- **Verdict rule (pre-set):** PASS only if the axis's **leave-study-out** CV-AUROC beats ALL
  baselines AND its bootstrap 95% CI excludes 0.5 AND permutation p < 0.05. A pass on
  leave-patient-out but not leave-study-out = **NULL (batch)**. Anything else = NULL.
- **Multiple testing:** 2 axes × 2 aggregations = 4 tests; report all four, BH-adjust.
- **Disease stratum:** report the primary within the dominant NHL stratum too.
- **Compartment:** primary aggregates all labeled cells (per the pre-registration block);
  a **infusion-product-only** compartment is reported as a robustness check (the atlas mixes
  pre-infusion product and post-infusion cells).

## 2. Data & label (verified, Brief 03)

- `Atlas_integ_scArches_FINAL_V5.h5ad` — X = raw counts, normalized (`normalize_total` 1e4) +
  `log1p`, scored with `sc.tl.score_genes` (CPU). IEC gene coverage **100%** (memory_stem 9/9,
  migration 8/8, synapse 18/18, kill 7/7, exhaustion 9/9, CD8 2/2, CD4 1/1).
- Label = `Max_Response`, **R = {CR, PR}** vs **NR = {NR}**, patient-level (0 within-patient
  conflicts). **n = 87 patients (60 R / 27 NR), 263,928 labeled cells.** Healthy-donor and
  mouse cells carry no label and are excluded — **no label invented or imputed.**

## 3. Study confound (why leave-study-out is mandatory)

Patient-level `orig_ident` × response (labeled patients): only **5 / 9** studies contain both
R and NR; **22 / 27 NR come from just two studies** (Deng 13, Haradvala 9); several studies are
100 % responder (Sheih 4/0, Jordana 3/0, Melenhorst 2/0). So a model can score well under
leave-patient-out purely by **memorizing per-study batch signatures** = fake signal. Only
leave-study-out isolates biology from batch.

## 4. Result — the 4-test table (primary compartment = all labeled cells, n=87)

| axis · aggregation | **leave-STUDY-out** AUROC [95% CI] | perm-p | BH-q | leave-patient-out AUROC |
|---|---|---|---|---|
| **A_persist · mean** (PRIMARY) | **0.533 [0.408, 0.650]** | 0.138 | 0.228 | 0.643 |
| A_persist · frac-hi | 0.576 [0.455, 0.699] | 0.075 | 0.228 | 0.633 |
| A_eff_exh · mean | 0.507 [0.366, 0.636] | 0.228 | 0.228 | 0.535 |
| A_eff_exh · frac-hi | 0.520 [0.393, 0.649] | 0.214 | 0.228 | 0.544 |

**Baselines (leave-study-out AUROC):** CD8 fraction **0.585**, cell count 0.491, mean
n_features 0.277, total counts 0.258. The best baseline (CD8 fraction) **exceeds every IEC
axis**.

**Every leave-study-out CI includes 0.5; every permutation p > 0.05 (min 0.075); every BH-q =
0.228.** No axis passes any of the three PASS criteria.

## 5. The decisive finding — batch, not biology

For A_persist, leave-**patient**-out AUROC = 0.643 but leave-**study**-out = 0.533; A_persist·
frac-hi 0.633 → 0.576. The ~0.10 AUROC that the weaker CV shows **evaporates** when whole
studies are held out. Per the pre-registered rule, a signal that survives leave-patient-out but
not leave-study-out **is batch structure**, not a transportable biological predictor. That is
exactly what happened here.

## 6. Robustness — same NULL everywhere

- **NHL stratum (n=77, 51 R / 26 NR):** A_persist·mean leave-study-out **0.489** [0.349, 0.624],
  perm-p 0.300 — NULL; so the (weak, LPO-only) signal was not even a within-disease effect.
- **Infusion-product compartment (n=73, 47 R / 26 NR):** A_persist·mean leave-study-out
  **0.516** [0.379, 0.652], perm-p 0.172 — NULL. Restricting to the pre-infusion product (the
  clinically actionable predictor compartment) does not rescue any axis.
- Full numbers in `cv_results.json`.

## 7. Honest verdict

**NULL, at power.** With 87 labeled patients (60 R / 27 NR) — far more than the underpowered
prior attempt (D4: n=9 / n=65, `immune_engagement_capacity.md` §3) — **no IEC axis predicts
CAR-T response** under honest leave-one-study-out CV; all axes lose to a CD8-fraction baseline,
all CIs include chance, all permutation tests are non-significant, and the only above-chance
numbers appear under the batch-permissive leave-patient-out CV and vanish under leave-study-out.

Per the IEC falsification criteria (§3, "Clinical null"), this outcome means **IEC is a
descriptive multi-axis capacity but NOT, on this evidence, a transcriptional response biomarker
for CAR-T** — and we say so plainly. This is a powered confirmation of the D4 negative, not a
failure to hide. It does not touch the locked, immune-scoped CCI controllership result; it
bounds the clinical-prediction claim, which the IEC report already carried an explicit negative
prior for.

### Caveats
- Transcriptome-only, from a heterogeneous 14-study public atlas; response definitions were
  harmonized by the atlas authors across studies. A NULL here does not exclude a signal in a
  single-protocol, prospectively-collected cohort with uniform timing.
- Response is disease- and study-structured; leave-study-out is the honest test but also the
  hardest, and with 9 studies (5 informative) power for a *small* true effect is limited — the
  CI half-width (~±0.12) bounds what could still be hiding.

### Deliverables
- `iec_prediction_report.md` (this file) · `patient_axis_scores_all.csv` +
  `patient_axis_scores_infusionproduct.csv` (per-patient axis scores + response + study) ·
  `iec_prediction.png` (leave-study-out AUROC vs baselines + A_persist by response) ·
  `cv_results.json`, `verdict.json`, `axis_gene_coverage.json` · `score_axes.py`, `cv.py`,
  `plot.py` (reproducible, CPU).
