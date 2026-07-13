# Local public-data workspace

Large source datasets are intentionally excluded from Git. This directory is only a local landing
zone for public inputs used by the reproducible pipeline.

## Marson CD4+ Perturb-seq anchor

```bash
aws s3 cp --no-sign-request \
  s3://genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.DE_stats.h5ad \
  data/

aws s3 cp --no-sign-request \
  s3://genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.pseudobulk_merged.h5ad \
  data/
```

The repository does not redistribute either file. Verify the dataset authors' current reuse terms
and the associated publication before downloading or redistributing source data. The project MIT
license applies to this repository's original software, not to third-party datasets.

## Required intake record

Before a new dataset can receive anything beyond a diagnostic run, record:

- source URL and stable accession;
- source citation and reuse/license terms;
- downloaded-file SHA-256;
- data classification;
- perturbation, condition, control and biological-replicate semantics; and
- the exact `DatasetSpec v1` file used by the CLI.

Example checksum command:

```bash
shasum -a 256 data/GWCD4i.DE_stats.h5ad
shasum -a 256 data/GWCD4i.pseudobulk_merged.h5ad
```

Committed result manifests carry data and axis hashes, but they are not a license grant for the
underlying source data. See [`docs/dataset_spec.md`](../docs/dataset_spec.md) and
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

