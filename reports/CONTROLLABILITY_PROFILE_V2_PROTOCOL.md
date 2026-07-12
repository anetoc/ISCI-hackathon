# Controllability Profile v2 — evolutionary protocol

**Status:** ACTIVE / EVOLUTIONARY  
**PI authorization:** 2026-07-12 — formula, axes and gates may be revised  
**Relationship to v1:** v1 remains an auditable baseline, not a binding constraint

## Scientific objective

Replace the implicit assumption of one universal controllability scalar with an axis-specific
profile. For perturbation `g`, functional axis `a` and condition `c`, estimate:

- `E(g,c)`: effect reach = number of differentially expressed genes;
- `S(g,a,c)`: absolute NES-style projection on the unit-normalized axis, with the perturbed
  gene removed from the ruler;
- `R(g,c)`: cross-donor effect reproducibility;
- `S|E` and `R|E`: training-only rank residuals conditional on effect reach.

No component is assumed universal. A summary scalar may be displayed only after the component
profile and evidence status are visible.

## Slice A — Marson condition transport

Build one row per gene×condition from `GWCD4i.DE_stats.h5ad` for Rest, Stim8hr and Stim48hr.
Use all seven configured axes separately; do not select the best axis from controller labels.

For each held-out condition:

1. train residualization, scaling and logistic models on the other two conditions;
2. evaluate the same fixed expression/power-matched gene blocks in the held-out condition;
3. compare `E` with `E + S|E` for every axis and `E + R|E`;
4. keep positive identity fixed across conditions;
5. bootstrap complete gene blocks across all condition predictions;
6. permute positive identity within blocks, using the same reassignment in all conditions;
7. adjust across the eight planned components by BH-FDR.

This is context transport within one screen, not independent biological replication. Because the
v2 design follows inspection of v1/T1, it is exploratory until prospectively reproduced.

## Verdicts

- `SUPPORTED_EXPLORATORY`: mean gain positive, coefficient positive, block-bootstrap CI above zero,
  BH q<0.05, and all three held-condition gains positive;
- `CONTEXT_DEPENDENT`: mean gain positive but at least one held-condition gain is non-positive;
- `DIRECTIONAL_UNCERTAIN`: direction positive but CI or q gate fails;
- `UNSUPPORTED`: mean gain or coefficient non-positive;
- `NOT_EVALUABLE`: required data or block gate fails.

## Slice B — topology-conditional axis null

Replace rejection sampling for small/coexpressed axes with a label-blind conditional sampler that
matches expression deciles and correlation topology. Report sampler convergence and effective
sample size; do not force a verdict when the conditional null has inadequate support.

## Provenance and privacy

Every table carries git SHA, data and axes hashes, timestamp, command, seed and method version.
Only public perturbation-screen statistics are used; no PHI or raw clinical text enters the flow.
