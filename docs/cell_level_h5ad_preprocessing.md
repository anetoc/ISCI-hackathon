# Cell-level H5AD preprocessing contract — v1

## Purpose

Convert a public cell-by-feature perturbation H5AD into the existing perturbation-by-feature
`anndata_effects` contract. This is an upstream evidence-construction step. It does not change the
frozen ISCI feature definitions, ranking kernel, axes, or verdict policy.

## Required declarations

An `anndata_cells` specification must declare:

1. the perturbation, guide, replicate, and optional condition/donor columns in `obs`, plus a real
   guide-count column for pooled designs;
2. the control rule, including accepted labels and the explicit logical fields used to match each
   perturbation to a shared or stratum-specific control pool;
3. the source signal (`X` or a named layer) and whether it contains raw counts or normalized values;
4. minimum cells per perturbation-control stratum and minimum independent replicate units;
5. the pseudobulk normalization and contrast method;
6. the standardized-effect definition used as the primary signal;
7. pooled multi-guide exclusion or an explicit arrayed single-guide design, plus any fixed
   guide-ID-to-target transformation required before leave-one-marker-out scoring;
8. the public source, license, input checksum, and data classification.

No field may be inferred silently when more than one plausible column or control label exists.

## Frozen transformation order

```text
cell-level H5AD
  → validate identities and exclusions
  → assign perturbation/control strata
  → aggregate cells within donor/replicate × guide × condition
  → compute perturbation minus matched-control effect
  → standardize within a predeclared comparison universe
  → write perturbation-by-feature H5AD
  → run existing anndata_effects adapter
```

The output observations represent independent effect vectors, not individual cells. Required
output metadata are `perturbation`, `condition`, and at least one independent replication field.
Guide-only coherence is diagnostic; confirmatory cross-donor coherence requires donor identity.

## Output contract

The preprocessing lane writes:

- `effects.h5ad`, with named `effect` and `standardized_effect` layers;
- `preprocessing_report.json`, with source/excluded cell counts and every threshold;
- input, output, axes-independent configuration, command, Git, and timestamp hashes;
- a generated DatasetSpec pointing to the effect artifact.

Raw H5AD files remain untracked. Reports must never contain raw clinical text, credentials, or
cell-level identifiers beyond aggregate counts and declared public column names.

## Stop gates

Return `NOT_EVALUABLE` instead of producing effects when:

- controls are absent or ambiguous;
- no donor/replicate field exists for a requested confirmatory run;
- any comparison lacks the declared minimum cells;
- multi-guide handling is undeclared;
- the source signal or normalization state is unknown;
- the standardization universe would be learned using benchmark labels.

## Implemented pipeline

`isci preflight-cells dataset.yaml` now inspects `obs`, `var`, `X/layers` in backed mode without
reading matrix values. It audits missing metadata and multi-guide exclusions, matches perturbation
and control cell support within declared strata, counts replicate- and donor-resolved ready units,
and emits `READY_FOR_EFFECT_CONSTRUCTION`, `DIAGNOSTIC_ONLY`, or `NOT_EVALUABLE`.

`isci build-effects dataset.yaml --output-dir outputs/<dataset>/effects` repeats that preflight and
only continues when `can_construct_effects=true`. For each eligible
condition/donor/replicate/guide stratum it:

1. rejects non-finite values and rejects fractional or negative values declared as raw counts;
2. aggregates raw counts and applies log1p counts-per-million, or averages a source explicitly
   declared as normalized;
3. subtracts the matched control pseudobulk from the perturbation pseudobulk;
4. standardizes each feature across perturbations within condition;
5. writes `effect` and `standardized_effect` layers plus aggregate observation metadata;
6. emits a generated `anndata_effects` DatasetSpec and a provenance-bound preprocessing report.

The source matrix is read in bounded cell-row blocks. A build can be `DIAGNOSTIC_EFFECTS_BUILT`
when donor coverage or other confirmatory evidence is absent. The downstream runner can still
return `FEATURE_EXTRACTION_NOT_EVALUABLE` when the measured features do not cover the frozen axes;
this is a safety property, not an execution error.
