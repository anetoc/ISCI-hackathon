# DatasetSpec v1 — bring a Perturb-seq dataset to ISCI

DatasetSpec is the versioned public boundary between an external dataset and the ISCI analysis
engine. It makes column meaning, evidence level, benchmark design and provenance explicit before a
large file is opened. The notebook and future CLI consume the same contract.

`config/datasets.yaml` remains the evidence registry for datasets already recomputed or aggregated
by the current runner. It is not the bring-your-own-data contract.

The machine-readable contract is `contracts/dataset_spec.schema.json`; the Python boundary is
`isci.dataset_spec`. CSV and Parquet inputs are physically inspected by
`isci.adapters.load_tabular_dataset`. Cell-level H5AD metadata are inspected by
`isci.adapters.preflight_anndata_cells`.

## Supported inputs in v1

DatasetSpec v1 supports perturbation-level evidence and an audited preprocessing lane for
cell-level H5AD. The lane performs metadata preflight first and only then converts declared cell
signals into matched-control pseudobulk effects.

| `input.layout` | Physical format | Required mapping | Intended use |
|---|---|---|---|
| `anndata_cells` | H5AD | `perturbation`, `guide`, `replicate`; `guide_count` for pooled designs; explicit `preprocessing` | Backed preflight and matched-control pseudobulk construction |
| `anndata_effects` | H5AD | `perturbation`; `input.layers.effect`; `input.layers.standardized_effect` | Perturbation-by-feature effect matrices |
| `long_effects` | CSV or Parquet | `perturbation`, `feature`, `effect`, `standardized_effect` | Portable long-form perturbation effects |
| `controller_features` | CSV or Parquet | `perturbation`, `magnitude`, `specificity`, `reproducibility` | Compute-light analysis from precomputed controller features |

`anndata_cells` does not make raw expression directly rankable. It first validates controls,
replication, guide multiplicity and cell support without reading `X`. `isci build-effects` then
reads the declared signal in bounded row blocks and produces an ordinary `anndata_effects`
artifact. That generated artifact must still satisfy axis coverage and reproducibility gates.

Pooled screens declare `multi_guide_policy: exclude` and map a real guide-count column. Arrayed
single-guide screens instead declare `not_applicable_arrayed` and omit `mapping.guide_count`.
`preprocessing.control.match_on` states whether controls are matched by condition, donor and/or
replicate; an empty list explicitly requests one global control pool. If a source stores guide IDs
such as `ZAP70_1` where the target gene is `ZAP70`, the fixed
`strip_trailing_guide_number` transform preserves the guide ID while exposing the correct target
for leave-one-marker-out scoring.

## Capability is conservative

The validator reports the strongest analysis tier declared by the spec:

- `CONFIRMATORY_DECLARED`: benchmark plus condition-, guide- and donor-resolved mappings are
  declared. This is not yet a confirmatory biological verdict.
- `BENCHMARK_DECLARED`: a leakage-controlled benchmark is declared, but full reproducibility
  metadata is absent.
- `PREPROCESSING_DECLARED`: a cell-level preprocessing contract is complete enough for physical
  metadata preflight; no effect matrix exists yet.
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
isci pipeline dataset.yaml --output-dir outputs/my_dataset/pipeline --block-rows 32
isci validate examples/dataset_spec/mini_long_effects.yaml
isci validate examples/dataset_spec/scperturb_cell_h5ad.yaml --structure-only
isci preflight-cells cell_dataset.yaml --report outputs/my_dataset/preflight.json
isci build-effects cell_dataset.yaml --output-dir outputs/my_dataset/effects --block-rows 64
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

`isci pipeline` is the default reusable entry point. For `anndata_cells`, it runs contract
validation → metadata preflight → matched-control effect construction → generated-spec validation
→ frozen analysis. Other layouts go directly from validation to the same analysis runner. It writes:

```text
outputs/<dataset_id>/pipeline/
├── pipeline_report.json
├── effects/                  # cell-level inputs only
│   ├── effects.h5ad
│   ├── dataset.effects.yaml
│   └── preprocessing_report.json
└── run/
    ├── controller_features.csv
    ├── axis_scores.csv
    ├── feature_extraction_report.json
    ├── controller_ranking.csv
    ├── condition_metrics.json
    └── analysis_report.json
```

The combined report keeps the raw-source hash separate from the generated-effect hash. A stopped
stage remains visible and returns exit code `3`; the pipeline never converts a stop gate into a
negative biological result.

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

`anndata_effects` means a perturbation-by-feature effect matrix, not a conventional cell-by-gene
AnnData object. Cell-level inputs require the separately specified preprocessing contract in
[`cell_level_h5ad_preprocessing.md`](cell_level_h5ad_preprocessing.md); the runner never interprets
raw expression `X` as a perturbation effect.

For `anndata_cells`, `isci inspect` returns `USE_PREFLIGHT_CELLS` and `isci run` returns
`CELL_PREPROCESSING_REQUIRED`. `isci preflight-cells` is the required first operation. Exit code
`0` means at least one perturbation-condition is ready for diagnostic effect construction; the
report separately identifies whether donor-resolved coverage is sufficient. `isci build-effects`
repeats that preflight, enforces the declared source-value constraints, and writes:

```text
outputs/<dataset_id>/effects/
├── effects.h5ad
├── dataset.effects.yaml
└── preprocessing_report.json
```

The generated spec is the hand-off to `isci inspect` and `isci run`. A successful build is an
engineering and preprocessing result, not a biological verdict.

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

The broad-RNA arrayed path is now exercised on an independent public Jurkat screen. The next
scientific step is a donor-resolved primary T-cell H5AD with broad gene coverage and a compatible
public license. It must be selected by predeclared eligibility, not because its outcome is favorable.
