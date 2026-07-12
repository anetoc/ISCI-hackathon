# DatasetSpec v1 — bring a Perturb-seq dataset to ISCI

DatasetSpec is the versioned public boundary between an external dataset and the ISCI analysis
engine. It makes column meaning, evidence level, benchmark design and provenance explicit before a
large file is opened. The notebook and future CLI consume the same contract.

`config/datasets.yaml` remains the evidence registry for datasets already recomputed or aggregated
by the current runner. It is not the bring-your-own-data contract.

The machine-readable contract is `contracts/dataset_spec.schema.json`; the Python boundary is
`isci.dataset_spec`. CSV and Parquet inputs are physically inspected by
`isci.adapters.load_tabular_dataset`.

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

from isci import load_tabular_dataset

result = load_tabular_dataset(spec, repo_root=".")
print(result.inspection.to_dict())
result.table.head()
```

The included example is synthetic and exists only to verify the contract. It is not biological
evidence and must not enter the ISCI result tables. Its YAML declares donor-, guide- and
benchmark-capable inputs, but physical inspection correctly downgrades it to `DIAGNOSTIC_ONLY`
because it contains only 2 observed positives, 2 donors and 1 condition.

## Command-line interface

After `uv sync`, the same boundary is available without writing Python:

```bash
isci validate examples/dataset_spec/mini_long_effects.yaml
isci validate queued_dataset.yaml --structure-only
isci inspect examples/dataset_spec/mini_long_effects.yaml
isci inspect dataset.yaml \
  --report outputs/my_dataset/inspection.json \
  --canonical-output outputs/my_dataset/canonical.parquet
isci inspect effect_matrix.yaml --scan-values --block-rows 64
isci run long_effects.yaml --output-dir outputs/my_dataset
isci run effect_matrix.yaml --block-rows 32 --output-dir outputs/my_h5ad
```

Exit code `0` means the requested validation/inspection completed; `2` means the spec, YAML or
output request is invalid; `3` means the physical dataset is `NOT_EVALUABLE`. A diagnostic or
benchmark-ready dataset still exits `0` because the capability is reported explicitly and no
confirmatory verdict is implied.

For `anndata_effects`, inspection opens the H5AD with `backed="r"`. `--scan-values` walks both
declared layers in bounded observation blocks. The CLI deliberately refuses
`--canonical-output` for H5AD because materializing the full long table can exceed memory and disk;
Python consumers stream it instead:

```python
from isci import iter_anndata_effect_blocks

for block in iter_anndata_effect_blocks(spec, repo_root=".", block_rows=64):
    # Each block has perturbation metadata + feature + effect + standardized_effect.
    consume(block)
```

Non-finite values are preserved in the public stream. During `isci run`, they are excluded with
explicit source/exclusion counts in `feature_extraction_report.json`. H5AD groups are processed
contiguously and only `--block-rows` observations are read from the matrix at once; the report also
records the peak summary buffer.

## Scientific runner

`isci run` accepts tabular `long_effects`, H5AD `anndata_effects` and precomputed
`controller_features`. For effect inputs it first computes effect magnitude, marker-restricted LOO
axis specificity and donor/guide replicate coherence. Rows without sufficient axis coverage or
independent replication remain missing and are excluded explicitly from ranking. H5AD uses the
same feature extractor through a grouped bounded-memory stream. The runner then computes balanced
and magnitude-orthogonal rankings with the frozen `isci-controllership` kernel, matches negatives
within each condition, and runs conditional LR plus a fixed-score bootstrap when at least 8
positives and 15 negatives are available.

It writes:

```text
outputs/<dataset_id>/
├── controller_features.csv
├── axis_scores.csv
├── feature_extraction_report.json
├── controller_ranking.csv
├── condition_metrics.json
└── analysis_report.json
```

The report binds input, axes, Git, kernel and output hashes. Its biological verdict is always
`NOT_ISSUED`: the generic runner does not convert a descriptive AUPRC gain into a dataset-specific
scientific `PASS`. The bootstrap is explicitly labeled descriptive and is not presented as the
leakage-free OOF estimand used in the frozen Marson result.

## Physical tabular inspection

The CSV/Parquet adapter:

- resolves paths inside the repository root and blocks symlink escape;
- verifies a declared SHA-256 before interpreting values;
- reads only mapped columns and renames them to canonical logical names;
- excludes invalid required rows with an explicit count;
- rejects missing columns, mapping collisions and duplicate canonical keys;
- measures observed positives, negative pool, donors, guides and conditions;
- emits `CONFIRMATORY_READY`, `BENCHMARK_READY`, `DIAGNOSTIC_ONLY` or `NOT_EVALUABLE` from
  observed coverage.

`CONFIRMATORY_READY` requires at least 8 observed positives, 15 negatives, 6 donors per positive,
2 guides per positive and 2 conditions per positive. It is a dataset-readiness decision, not an
ISCI biological `PASS`.

## Path and privacy rules

- Contract paths are repository-relative. Absolute paths and `..` traversal are rejected.
- `provenance.source_url`, citation, license and data classification are required.
- DatasetSpec never uploads or opens data during config validation.
- Raw H5AD/H5MU files remain outside Git.
- `RESTRICTED` data may only be processed by an explicitly local adapter/runtime under the project
  privacy policy; the public notebook must use `PUBLIC` data.

## What comes next

The remaining portability gate is a smoke run on an independent public H5AD that was not used to
develop the adapter, followed by updating the researcher notebook to demonstrate the same public
`isci run` interface. This is external validation, not a change to the frozen ISCI method.
