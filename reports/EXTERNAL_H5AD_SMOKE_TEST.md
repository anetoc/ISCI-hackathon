# External H5AD smoke test

Date: 2026-07-12
Purpose: test the portability boundary of the generic H5AD path with a public file that was not
used to develop the adapter.

## Source and integrity

- Repository: scPerturb Zenodo record [10044268](https://zenodo.org/records/10044268)
- File: `PapalexiSatija2021_eccite_protein.h5ad`
- License declared by the record: CC-BY-4.0
- Download size: 1,191,551 bytes
- Expected MD5: `07290242b0e835c9474bb816de9cda45`
- Observed MD5: `07290242b0e835c9474bb816de9cda45`
- Data classification: PUBLIC

The file was downloaded only to `tmp/external-smoke/` and is not a release artifact or Git input.

## Backed inspection

- Shape: 20,729 cells × 4 proteins
- Features: CD86, PDL1, PDL2, CD366
- Useful observation metadata include `hto`, `guide_id`, `perturbation`, `celltype`,
  `perturbation_type`, and QC counts.
- The H5AD contains cell-level measurements in `X`; it does not contain the declared
  perturbation-level `effect` and `standardized_effect` layers required by
  `input.layout=anndata_effects`.

## Verdict

**PREPROCESSING_REQUIRED — not a biological failure.**

The current H5AD runner is complete for perturbation-by-feature effect matrices. A typical public
scPerturb H5AD is instead cell-by-feature input and must first define controls, biological strata,
pseudobulk aggregation, contrasts, and standardization. Treating `X` as an effect matrix would mix
cell abundance, baseline expression, library size, and perturbation response.

This protein-only THP-1 dataset is not an external validation of CD4+ T-cell controllership. It is
an interface smoke test that exposed the next portability contract.

## Metadata preflight result

After implementing `isci preflight-cells`, the unchanged public file was evaluated with the
declared control label `control`, replicate column `hto`, guide column `guide_id`, and guide-count
column `nperts`:

- input SHA-256: `e1e293c75dfebe09301bf32093703cfd5f50c17d6fb53144d8213e52e0e4e150`;
- 20,729 eligible cells and 2,386 observed control cells;
- 98 non-control perturbations across 5 replicate labels;
- 216 perturbation/control strata passed the 25-cell threshold;
- 120 strata were explicitly underpowered;
- 72 perturbation units passed the two-replicate threshold;
- 0 donor-resolved units because donor identity is absent.

Final preflight status: **`DIAGNOSTIC_ONLY` with `can_construct_effects=true`**. Matrix values were
not scanned and the biological verdict remained `NOT_ISSUED`.

## Implemented boundary and required next adapter

The metadata-only `anndata_cells` preflight is now implemented under the preprocessing contract in
[`docs/cell_level_h5ad_preprocessing.md`](../docs/cell_level_h5ad_preprocessing.md). It does not read
`X` or create effects. The remaining adapter must emit an ordinary `anndata_effects` artifact and
provenance report, so the frozen feature extraction and conditional ranking code remain unchanged.
