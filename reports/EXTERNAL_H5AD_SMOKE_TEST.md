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

## Initial boundary verdict

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

## Effect construction and downstream gate

The same unchanged public file then ran through:

```bash
isci build-effects examples/dataset_spec/scperturb_cell_h5ad.yaml \
  --repo-root . \
  --output-dir tmp/external-smoke/papalexi_build_d1771a4 \
  --block-rows 64
```

The builder produced 207 matched-control effect rows across 4 proteins, with 0 invalid effect
values. There are fewer effect rows than the 216 preflight-eligible strata because the builder
retains only perturbation units that also pass the declared two-replicate requirement. The output
H5AD SHA-256 was
`b785698855586e9643cee068ef11e0c5ac1a3c053d5f67fbf969da43e00b664d`.

The generated DatasetSpec validated and reopened through the existing `anndata_effects` adapter as
`DIAGNOSTIC_ONLY`. Running the unchanged feature extractor produced 72 controller-feature rows but
0 ranking-eligible rows. Reproducibility was measurable for all 72 units after preserving replicate
identity; axis specificity was not measurable for any unit because the four proteins do not overlap
the frozen CD4+ axes sufficiently. Final status: **`FEATURE_EXTRACTION_NOT_EVALUABLE`**, biological
verdict **`NOT_ISSUED`**.

This is the intended behavior. The file proves that another researcher can supply a conventional
cell-level public H5AD and obtain audited effects. It cannot validate CD4+ T-cell controllership
because it is a THP-1 assay with only four proteins. The aggregate machine-readable record is
[`outputs/hackathon/cell_effect_build_smoke.json`](../outputs/hackathon/cell_effect_build_smoke.json);
raw H5AD and generated large artifacts remain outside Git.
