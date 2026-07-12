# DatasetSpec v1 — bring a Perturb-seq dataset to ISCI

DatasetSpec is the versioned public boundary between an external dataset and the ISCI analysis
engine. It makes column meaning, evidence level, benchmark design and provenance explicit before a
large file is opened. The notebook and future CLI consume the same contract.

`config/datasets.yaml` remains the evidence registry for datasets already recomputed or aggregated
by the current runner. It is not the bring-your-own-data contract.

The machine-readable contract is `contracts/dataset_spec.schema.json`; the Python boundary is
`isci.dataset_spec`.

## Supported inputs in v1

DatasetSpec v1 supports perturbation-level evidence, not raw cell-by-gene count matrices.

| `input.layout` | Physical format | Required mapping | Intended use |
|---|---|---|---|
| `anndata_effects` | H5AD | `perturbation`; `input.layers.effect`; `input.layers.standardized_effect` | Perturbation-by-feature effect matrices |
| `long_effects` | CSV or Parquet | `perturbation`, `feature`, `effect`, `standardized_effect` | Portable long-form perturbation effects |
| `controller_features` | CSV or Parquet | `perturbation`, `magnitude`, `specificity`, `reproducibility` | Compute-light analysis from precomputed controller features |

Raw single-cell counts require dataset-specific pseudobulk, differential-expression and QC choices.
They are deliberately outside v1 until a validated preprocessor exists; accepting them now would
make the interface look more general than the scientific implementation.

## Capability is conservative

The validator reports the strongest analysis tier declared by the spec:

- `CONFIRMATORY_DECLARED`: benchmark plus condition-, guide- and donor-resolved mappings are
  declared. This is not yet a confirmatory biological verdict.
- `BENCHMARK_DECLARED`: a leakage-controlled benchmark is declared, but full reproducibility
  metadata is absent.
- `DIAGNOSTIC_ONLY`: effects can be analysed, but no independent positive benchmark is declared.
- `NOT_EVALUABLE`: the contract is invalid. No data should be opened and no biological verdict
  should be issued.

This is only a declaration-level capability. A future adapter must still inspect the real columns,
sample counts and values and may downgrade the dataset. It may never upgrade the dataset silently.

## Frozen scientific protections

DatasetSpec does not change ISCI-core or `config/axes.yaml`. Version 1 requires:

- standardized effects as the primary directional signal;
- raw effect/log-fold-change as sensitivity;
- leave-one-marker-out axis reconstruction;
- expression-matched negatives using target expression, guide count, target-cell support and
  condition whenever a benchmark is declared;
- a deterministic seed and at least 100 bootstrap repetitions.

## Minimal use

```python
from isci import load_dataset_spec, validate_dataset_spec
import yaml

path = "examples/dataset_spec/mini_long_effects.yaml"
raw = yaml.safe_load(open(path))
report = validate_dataset_spec(raw)
print(report.to_dict())

spec = load_dataset_spec(path, check_paths=True)
print(spec.dataset.id, spec.input.layout)
```

The included example is synthetic and exists only to verify the contract. It is not biological
evidence and must not enter the ISCI result tables.

## Path and privacy rules

- Contract paths are repository-relative. Absolute local paths are rejected.
- `provenance.source_url`, citation, license and data classification are required.
- DatasetSpec never uploads or opens data during config validation.
- Raw H5AD/H5MU files remain outside Git.
- `RESTRICTED` data may only be processed by an explicitly local adapter/runtime under the project
  privacy policy; the public notebook must use `PUBLIC` data.

## What comes next

The next implementation slice is the adapter boundary: validate the physical table/H5AD against
the declared mappings, emit a canonical perturbation-effect table, and return a structured
`NOT_EVALUABLE` report when required evidence is missing. The CLI and notebook should call that
adapter rather than contain dataset-specific branching.
