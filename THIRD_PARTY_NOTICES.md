# Third-party data, software and media notices

The repository-level MIT license covers original T-CTRL/ISCI software and project-authored
documentation. It does not relicense third-party datasets, publications, trademarks or bundled
software.

## Public scientific datasets

Raw H5AD/H5MU and other large source datasets are not committed. Users download them directly from
their original repositories and remain responsible for the source terms, citation requirements and
any access restrictions. Dataset accessions and provenance requirements are documented in
[`data/README.md`](data/README.md), [`config/datasets.yaml`](config/datasets.yaml) and the
versioned [`DatasetSpec`](docs/dataset_spec.md).

Project-generated tables and figures are derived analyses. Their presence here does not grant new
rights over the underlying source data.

## Bundled browser assets

- `docs/tctrl_live_demo.html` contains a bundled Plotly.js runtime. Plotly.js is distributed under
  the MIT license; see the Plotly project for its full notice and source.
- `docs/hackathon_judge_demo.html` is generated only from repository-contained HTML, CSS,
  JavaScript, manifests and project figures; it does not embed the former machine-local text-layout
  runtime.

## Python dependencies

Python packages are resolved in `uv.lock` and retain their own licenses. They are dependencies, not
relicensed project source. The repository does not vendor their source trees.

## Publications and citations

Article titles, bibliographic metadata and short scientific summaries are citations or factual
references. Full publications are not redistributed by this repository.
