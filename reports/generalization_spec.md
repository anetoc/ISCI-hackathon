# Generalization Spec — applying the CCI test to any Perturb-seq

Operational companion to `conditional_controllability_invariant.md`. This is the
per-dataset checklist the generalization tracks follow, with explicit gates so we
never download heavy data we can't use and never fabricate labels.

## Minimum viable dataset (the intake gate)

A candidate dataset is **admissible** only if ALL hold:

| Requirement | Why | FAIL action |
|---|---|---|
| Perturbation × gene effect matrix (or cell-level → pseudobulk DE) | the substrate | drop dataset |
| ≥2 independent replicates (donor/guide/rep) per perturbation | `R` needs replication | drop, or use guide-level if available |
| At least one credible **state axis** (signed gene set) for the system | `S` needs a target axis | drop or import axis from literature |
| A **regulator label set** (known controllers) for that cell system | the positives for AUPRC | drop — do NOT invent labels |
| Fits CPU-local (≤~20 GB working) OR pseudobulk/DE-stat form available | 24 GB local constraint | mark GATED → institutional machine |

The label + axis requirements are the hard ones. Without a credible regulator set
for the system, the test has no positives and is **not run** — reported as
"admissible data, no label set," not forced.

## Feasibility gate (before heavy download)

1. Read GEO/Zenodo/scPerturb metadata only (sizes, structure).
2. Estimate working memory: cell-level h5ad ≫ 20 GB → require pseudobulk/DE-stat form
   or defer to the institutional machine.
3. Confirm replicate structure and label availability **from metadata** before pulling data.
4. Only then download.

## Axis and label sourcing per system

- **Immune (near):** reuse T-cell state axes (memory / effector / exhaustion /
  Treg) where the cell type matches; regulator labels from the same curated
  immune-regulator sets used in Marson, intersected with measured genes.
- **Non-immune (far):** state axes must be system-appropriate (e.g. proliferation,
  stress, lineage programs for K562/RPE1); regulator labels from an
  orthogonal source (e.g. essential/known-TF sets, or the dataset's own validated hits).
  If no clean axis+label pair exists, the far test is reported as **not evaluable**,
  which is itself informative about the property's reach.

## PASS / FAIL / NOT-EVALUABLE per dataset

For each admissible dataset, run the CCI protocol and assign exactly one verdict:

- **PASS** — bootstrap ΔAUPRC(M → M+C) 95% CI excludes 0 **and** conditional LR p<0.05,
  with |Spearman(C,M)| small. The invariant holds in this system.
- **FAIL** — CI includes 0 or LR non-significant. The invariant does **not** hold here;
  record ΔAUPRC and the boundary this defines.
- **NOT-EVALUABLE** — admissible data but no credible axis+label pair, or gated on
  compute. No verdict; state the blocker.

## Cross-dataset synthesis

Collect (dataset, system, n_pos, n_neg, ΔAUPRC, CI, LR p, Spearman(C,M), verdict) into
one table. The **invariance figure** plots ΔAUPRC with CI per system beside Marson.
The property's scope is read directly off the verdicts:

- PASS in immune + PASS in non-immune → **general invariant**.
- PASS in immune only → **immune-scoped property**.
- PASS in Marson only → **single-dataset finding** (honest fallback).

No result is spun: a narrow scope is a real, publishable boundary on the property.
