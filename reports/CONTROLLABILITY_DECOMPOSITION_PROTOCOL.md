# Frozen protocol — operational decomposition of perturbational controllability

**Status:** FROZEN BEFORE EXECUTION  
**Frozen:** 2026-07-12 12:00 BRT  
**Branch:** `codex/controllability-decomposition`  
**Parent commit:** `d3c5874`  
**Scope:** post-hoc adversarial stress tests; does not replace the locked ISCI/CCI result  

## 1. Scientific question

Test whether perturbational controllability admits a useful operational decomposition into:

- effect reach `E`: perturbation-effect magnitude;
- axis precision `S|E`: axis-specificity residualized against `E`;
- repeatability `R|E`: donor/guide/replicate reproducibility residualized against `E`.

This protocol does **not** claim statistical factorization or mechanistic regimes. It estimates
component-support patterns and explicitly preserves uncertain and non-evaluable outcomes.

## 2. Shared rules

1. The frozen ranking and OOF result are immutable.
2. Gene is the independent evaluation unit.
3. Matching, residualization, scaling and model fitting occur inside training folds only.
4. Positives and their matched negatives form evaluation blocks.
5. A non-significant result is uncertain, not evidence of biological absence.
6. New results use `SUPPORT`, `DIRECTIONAL_UNCERTAIN`, `UNSUPPORTED`, or `NOT_EVALUABLE`.
7. New analyses are labeled post-hoc stress tests in every figure and report.
8. Seeds, input hashes, git SHA, command and timestamp are written to every result artifact.

## 3. T1 — adversarial axis null

### 3.1 Inputs

- `data/GWCD4i.DE_stats.h5ad`, layer `zscore`;
- `config/axes.yaml`;
- `results/final/isci_final_ranking.csv` for the frozen detectable set and canonical labels;
- `outputs/marson_obs_matching.parquet` for expression/power matching.

### 3.2 Unit and population

- Unit: perturbed gene.
- Population: frozen Marson detectable set.
- Positives: `known_regulator == True` within that set.
- Negatives: expression/power-matched within each training fold, using
  `target_baseMean` and `n_cells_target`, eight candidates per positive.

### 3.3 Real and pseudo axes

The real axes are loaded unchanged from `config/axes.yaml`. Generate exactly 200 pseudo-axes per
real axis with seed 20260712. Each pseudo-axis preserves:

- number of non-zero genes;
- number of positive and negative weights;
- empirical absolute-weight distribution;
- gene-expression decile distribution;
- mean absolute within-axis gene correlation within a tolerance of 20%.

Candidates failing these constraints after 1,000 attempts are rejected. The analysis is
`NOT_EVALUABLE` if fewer than 90% of the planned pseudo-axes are admissible. The number of
pseudo-axes must not be reduced after inspecting results.

### 3.4 Leakage-safe evaluation

Use grouped leave-one-positive-block-out evaluation. In every fold:

1. hold out one positive and its evaluation negatives;
2. select negatives using training data only;
3. fit rank residualization `S ~ E` on training genes only;
4. fit scaling and logistic models on training genes only;
5. evaluate held-out predictions;
6. repeat the identical procedure for the real and every pseudo-axis.

### 3.5 Estimand and null

For axis `a` and pseudo-axis `j`:

`gain(a) = AUPRC_OOF(E + Sr_a) - AUPRC_OOF(E)`

`theta_axis = gain(real) - median_j(gain(pseudo_j))`

The empirical p-value is `(1 + count(gain(pseudo) >= gain(real))) / (1 + n_pseudo)`.

### 3.6 Verdict

- `SUPPORT`: `theta_axis > 0`, real gain above the pseudo-axis 95th percentile, empirical
  `p < 0.05`, and the OOF component coefficient has the expected positive direction.
- `UNSUPPORTED`: any SUPPORT condition fails.
- `NOT_EVALUABLE`: pseudo-axis admissibility <90%, fewer than eight positives, or fewer than five
  admissible negatives per positive.

### 3.7 Interpretation boundary

T1 measures whether the biological ruler is more aligned with canonical labels than structurally
matched rulers. Because labels and axes share biological ontology, T1 is not independent controller
validation and cannot eliminate all circularity.

### 3.8 Runtime stop

Three hours wall time. Timeout yields `NOT_EVALUABLE`; parameters are not changed.

## 4. T2 — component-support transport map

### 4.1 Planned datasets

1. Marson CD4;
2. Schmidt CD4 CRISPRa;
3. THP-1 myeloid;
4. Norman K562;
5. Replogle RPE1.

A dataset enters the new analysis only if gene-level `E`, `S`, `R`, labels and admissible matching
covariates/negative blocks exist in committed artifacts. No raw h5ad recomputation is permitted for
T2 before submission.

### 4.2 Models and estimands

For each dataset and component, compare leakage-safe OOF models:

- precision: `y ~ E` versus `y ~ E + Sr`;
- repeatability: `y ~ E` versus `y ~ E + Rr`.

Primary estimand:

`deltaAUPRC_OOF = AUPRC_OOF(E + component_residual) - AUPRC_OOF(E)`

Report the standardized coefficient direction. A classical full-sample LR statistic may be emitted
only as an explicitly apparent diagnostic; it never determines the verdict.

### 4.3 Uncertainty and null

- CI: matched-block bootstrap of complete OOF prediction blocks, 1,000 resamples, seed 20260712.
- Permutation: within each block containing one positive and its matched negatives, uniformly
  reassign which gene is positive; rerun all training transformations and OOF prediction.
- Permutations: 1,000 per dataset/component, seed 20260712.
- Empirical `p_perm`: fraction of permuted `deltaAUPRC_OOF` at least as large as observed.
- Multiplicity: BH-FDR across the ten planned dataset/component `p_perm` values. Non-evaluable tests
  remain in the family with p-value 1.0.

### 4.4 Dataset/component gates

`NOT_EVALUABLE` if any applies:

- fewer than eight positives;
- fewer than five admissible negatives per positive;
- component coverage below 80%;
- fewer than two independent replicates for `R`;
- the required gene-level artifact is absent or requires raw-data recomputation.

### 4.5 Verdict

- `SUPPORTED`: coefficient direction positive, bootstrap CI entirely above zero and
  `q_perm_BH < 0.05`.
- `DIRECTIONAL_UNCERTAIN`: coefficient and point gain positive, but CI includes zero or
  `q_perm_BH >= 0.05`.
- `UNSUPPORTED`: coefficient or point gain is non-positive.
- `NOT_EVALUABLE`: a gate in section 4.4 fails.

No difference between `S` and `R` is claimed without a direct interaction/contrast test.

### 4.6 Runtime stop

Two hours wall time using committed artifacts only.

## 5. T4 — leave-one-condition-out transport gate

Audit for at most 90 minutes whether condition-level Marson `E`, `S`, `R`, labels and matching
covariates exist in reusable artifacts. If not, emit `NOT_EVALUABLE` and stop.

If admissible, train all transformations on two conditions and evaluate the third, rotating Rest,
Stim8 and Stim48. The primary estimand is the mean of the three out-of-condition `deltaAUPRC` values.

The null reassigns positive identity uniformly within each matched gene block, maintaining the same
gene reassignment across all three conditions. The test measures within-screen context transport,
not independent replication.

## 6. Outputs

- `outputs/decomposition/t1_axis_null.json`;
- `outputs/decomposition/t1_axis_null_scores.parquet`;
- `outputs/decomposition/t2_component_support.csv`;
- `outputs/decomposition/t2_component_support.json`;
- `outputs/decomposition/t4_condition_transport.json`;
- `figures/controllability_decomposition.png`;
- tests for fold isolation, block permutation, verdicts, provenance and deterministic seeds.

## 7. Global stop

All new science stops at **2026-07-13 14:00 BRT**. The remaining eight hours are reserved for
sanitization, reproducibility, narrative synchronization and demo recording.
