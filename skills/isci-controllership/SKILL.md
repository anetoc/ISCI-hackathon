---
name: isci-controllership
description: Separate genes that CONTROL a cell-state transition from genes merely ASSOCIATED with it, in Perturb-seq / perturbation screens. Use when you have per-perturbation differential-expression stats (effect magnitude, direction, cross-replicate reproducibility) and a set of functional state axes, and you want a controllership ranking that is NOT just an effect-size proxy. Implements the magnitude-CONDITIONAL test (the key fix): known regulators have far larger effects, so any index tested AGAINST magnitude is confounded; the valid question is whether a feature adds signal CONDITIONAL ON magnitude. Covers expression-matched negatives, leave-one-marker-out axes, conditional likelihood-ratio testing, bootstrap AUPRC gain, and a balanced controllership score. Keywords: Perturb-seq, CRISPR screen, controllability, driver genes, T-cell state, effect-magnitude confound, AUPRC, regulator recovery.
---

# ISCI — Immune-State Controllability Index

A method for ranking **controllers** of a cell-state transition from a perturbation
screen, and for testing that the ranking captures more than raw effect size.

## The core idea (read this first)

In a Perturb-seq screen, known regulators of a state have **much larger effects**
than bystanders (in the Marson CD4+ screen, ~99× more differential-expression genes;
Mann-Whitney p ~ 1e-10). So any benchmark of the form *"does my index beat effect
magnitude?"* is **rigged** — magnitude wins by construction, and a magnitude-orthogonal
signal will look worthless even when it is real.

**The valid question is CONDITIONAL:** *does a feature add signal for regulator status
CONDITIONAL ON effect magnitude?* Test it with a likelihood-ratio test of
`regulator ~ magnitude + feature` vs `regulator ~ magnitude`. Two features pass in the
Marson data and generalize as the recommended controllership signal:

- **axis-specificity** — how concentrated a perturbation's effect is on a functional
  state axis (vs diffuse). `max |cos(z, axis)| / ||z||`, residualized on magnitude.
- **cross-donor coherence** — whether the effect points the same way across donors
  (reproducibility), residualized on magnitude.

Network influence (PageRank/in-degree) and cross-guide coherence did **not** add
signal over magnitude here.

## Workflow

1. **Load** per-perturbation DE stats (a gene × condition table with an effect-magnitude
   column, a z-score/log-FC matrix, and cross-donor/guide reproducibility columns) and a
   set of state-axis marker sets.
2. **Build axes with leave-one-marker-out** (`build_axis_vectors(..., leave_one_out=g)`):
   when scoring gene `g`, remove `g` from every axis so a marker can't score high just for
   being a coordinate of its own ruler. This is the single most important leakage control.
3. **Expression-matched negatives** (`expression_matched_negatives`): for each positive,
   draw non-positives matched on expression/power covariates (baseline expression, cells
   per target). Random negatives inflate every metric — match them.
4. **Conditional LR test** (`conditional_lr_test`): does each candidate feature add over
   magnitude? Keep only features that pass.
5. **Bootstrap the AUPRC gain** (`bootstrap_auprc_gain`): resample positives+negatives,
   compare magnitude-only vs magnitude+features AUPRC. Report the gain and its 95% CI.
6. **Rank** (`controllership_score`): balanced geomean of percentile ranks of the
   passing components, or the magnitude-independent `orthogonal` score gated on
   detectable effect. Report both; be explicit which one the top-list reflects.

## Pitfalls (learned the hard way)

- **Do not** report a top-list from a magnitude-dominated aggregator and call it the
  orthogonal-signal result — check the magnitude-percentile spread of the top genes.
- **Do not** use GTEx / bulk-tissue negatives; use screen-native expression-matched ones.
- **Do not** trust a single global permutation null for all components — magnitude,
  network, and reproducibility need different nulls; prefer the conditional LR + bootstrap.
- **Cosine over ~10k genes is diluted** vs a small marker axis — restrict the projection
  to axis genes (NES-style enrichment) or the specificity signal vanishes.
- A CD4+ in-vitro screen will have **~0 effect** for CD8/exhaustion markers (TOX, TCF7):
  they are not benchmarkable there. Gate on detectable effect before ranking.

## Helpers (loaded into your kernel)

`conditional_lr_test`, `expression_matched_negatives`, `bootstrap_auprc_gain`,
`controllership_score` — the core controllership method.

For the T-REMAP extension (reverse-mapping clinical programs onto perturbations):
`movability_gate` (check a clinical module's genes are actually moved by perturbations before trying to reverse-map it — the gate that separates a viable module from an unreachable one) and `clinical_reversal_score` (ClinicalReversalScore = sensitivity-module push − resistance-module push per perturbation, with a permutation null over module identity). See `kernel.py`. All operate on plain pandas DataFrames / numpy arrays.
