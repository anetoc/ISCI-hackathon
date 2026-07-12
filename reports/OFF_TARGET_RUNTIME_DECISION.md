# Off-target reference and runtime decision

**Status:** human reference and pilot engine/parameters frozen; no off-target search has been
executed.

## Decision

The off-target package will use the NCBI RefSeq human reference assembly
`GCF_000001405.40` (`GRCh38.p14`) and annotation `GCF_000001405.40-RS_2025_08`.
These identifiers are explicit package inputs rather than tool defaults.

The current Apple Silicon workstation is a `NO_GO` environment for the first full-genome run.
This is an infrastructure decision, not a biological result and not evidence that any guide is
safe or unsafe. A source-backed pilot is now frozen in `config/off_target_pilot.yaml` and
`reports/OFF_TARGET_PILOT_PROTOCOL.md`; execution and promotion thresholds remain blocked.

## Why this reference

The NCBI Datasets record identifies `GCF_000001405.40` as the current reference assembly
`GRCh38.p14`, paired with GenBank accession `GCA_000001405.29`. The same record identifies the
current RefSeq annotation release as `GCF_000001405.40-RS_2025_08`, released 2025-08-01. Freezing
both accession and annotation version prevents silent drift in genome and TSS interpretation.

Primary source:

- NCBI Datasets API, `GCF_000001405.40` dataset report, accessed 2026-07-12:
  <https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/GCF_000001405.40/dataset_report>

## Runtime evaluation

### Cas-OFFinder

Cas-OFFinder is a valid candidate for mismatch/PAM searches on a compatible host, but its official
runtime requires OpenCL. The current Mac has no detected OpenCL platform, and the latest official
release (`2.4.1`) publishes a macOS x86-64 binary rather than an Apple Silicon binary. Therefore it
is not selected for this workstation.

Sources:

- official Cas-OFFinder README: <https://github.com/snugel/cas-offinder>
- official latest release metadata: <https://api.github.com/repos/snugel/cas-offinder/releases/latest>

### CRISPRitz

CRISPRitz is the selected pilot engine for a disposable Linux scratch environment
because its documented surface includes mismatches, DNA/RNA bulges, variant-aware searches,
scoring and genomic annotation. The official Conda workflow is Linux-only; macOS is supported via
Docker. The current Docker image is amd64 and approximately 1.03 GB compressed, while the selected
human assembly is approximately 3.10 Gbp before indexes and outputs. With about 13 GiB free on this
workstation, running the full package locally creates avoidable disk and emulation risk.

Source refresh on 2026-07-12 found CRISPRitz `2.7.0` and versioned Bioconda builds for both
`linux-64` and `linux-aarch64`. The pilot pins the `linux-64` Python 3.9 build and its published
SHA-256. The Docker image remains excluded because its metadata predates the 2.7.0 release.

Sources:

- official CRISPRitz README: <https://github.com/pinellolab/CRISPRitz>
- official CRISPRitz 2.7.0 release:
  <https://github.com/pinellolab/CRISPRitz/releases/tag/v2.7.0>
- Bioconda 2.7.0 release metadata:
  <https://api.anaconda.org/release/bioconda/crispritz/2.7.0>
- official Docker image metadata:
  <https://hub.docker.com/v2/repositories/pinellolab/crispritz/tags/latest>

## Frozen boundary and next gate

- Frozen now: `GCF_000001405.40` / `GRCh38.p14` and
  `GCF_000001405.40-RS_2025_08`.
- Frozen for the technical pilot only: CRISPRitz 2.7.0, SpCas9/NGG, mismatch ceiling 4 and the
  staged one-DNA/one-RNA-bulge sensitivity run.
- Not frozen: annotation categories, score interpretation, variant-aware policy and guide
  promotion thresholds.
- No guide is promoted, replaced or approved for synthesis by this decision.
- Preferred next execution: the version-pinned CRISPRitz pilot on external Linux scratch,
  first with known positive controls and a small subset, followed by the 78-candidate package only
  after expected hits, deterministic output and resource use are verified.
- Cas-OFFinder remains a fallback on an OpenCL-compatible host for independent mismatch-only
  sensitivity comparison.
