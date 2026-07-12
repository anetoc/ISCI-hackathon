# Cell-level H5AD preprocessing contract — draft v0

## Purpose

Convert a public cell-by-feature perturbation H5AD into the existing perturbation-by-feature
`anndata_effects` contract. This is an upstream evidence-construction step. It does not change the
frozen ISCI feature definitions, ranking kernel, axes, or verdict policy.

## Required declarations

An `anndata_cells` specification must declare:

1. the perturbation, guide, condition, donor or replicate, and sample columns in `obs`;
2. the control rule, including accepted labels and whether controls are shared or stratum-specific;
3. the source signal (`X` or a named layer) and whether it contains raw counts or normalized values;
4. minimum cells per perturbation-control stratum and minimum independent replicate units;
5. the pseudobulk normalization and contrast method;
6. the standardized-effect definition used as the primary signal;
7. doublet, multi-guide, low-quality, and missing-metadata exclusion rules;
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

## First implementation slice

Build metadata-only `isci preflight-cells dataset.yaml`. It should inspect `obs`, `var`, `X/layers`
and report whether the preprocessing contract is complete without loading the full matrix. Only
after that gate passes should pseudobulk effect construction be implemented.
