# Version-pinned off-target pilot protocol

**Status:** protocol and inputs frozen before execution. S0 passed on 2026-07-14; S1–S3 remain
unexecuted. No project guide is replaced and no oligo is approved for synthesis.

## Question

Can CRISPRitz 2.7.0 deterministically enumerate reference-genome candidates for the project guide
panel under an explicit SpCas9/NGG contract before the search is expanded to bulges and functional
annotation?

This is a software and assay-engineering validation. It is not a biological-efficacy test and it
does not alter ISCI-core, axes, target membership, controller labels or completed claims.

## Frozen runtime

- engine: CRISPRitz `2.7.0`, upstream commit
  `24b893ecb0c2354d5c76697e116d2febe1ee6265`;
- distribution: Bioconda `linux-64`, build `py39h2de1943_0`;
- package SHA-256: `88aa3073a76f8b74b2a869ecf921c59241cf19267df877bafc285b8620cfc215`;
- scientific reference: `GCF_000001405.40` (`GRCh38.p14`);
- annotation release: `GCF_000001405.40-RS_2025_08`;
- CRISPR contract: CRISPRa, SpCas9, 20-nt protospacer, NGG PAM.

The official public Docker image is not used because its published image metadata predates the
2.7.0 release and does not provide a version-aligned immutable runtime. Bioconda publishes an
exact Linux package and checksum. The execution host remains external scratch Linux because local
disk capacity is insufficient for a safe full-reference run.

## Staged execution

### S0 — installation smoke test

Run the official CRISPRitz EMX1 test guide
`GAGTCCGAGCAGAAGAAGAANNN` against the official chromosome-22 installation fixture using the
official SpCas9 pattern `NNNNNNNNNNNNNNNNNNNNNGG 3` and four mismatches. This stage validates the
installed command surface only; its reference fixture cannot adjudicate project guides.

S0 subsequently passed in GitHub Actions run
[`29296855125`](https://github.com/anetoc/ISCI-hackathon/actions/runs/29296855125): two executions,
seven identical canonical target rows, empty stderr and all required profiles present. The frozen
pre-execution contract remains unchanged; the result and raw evidence are reported separately in
`reports/OFF_TARGET_S0_RESULTS.md` and `outputs/decomposition_v2/off_target_s0/`.

### S1 — priority reference search

Run all current and fallback candidates for `TNFRSF9` and `TBX21`, the two targets for which both
current guides entered technical review. Use the full frozen reference, mismatch-only search and a
four-mismatch ceiling. This is the smallest project-specific slice with the greatest replacement
risk.

### S2 — full reference search

Only after S1 passes, run all 78 candidates with the same mismatch-only settings. The stage expands
coverage without changing the decision rule.

### S3 — bulge sensitivity

Only after S2 passes, build the indexed reference and repeat the 78-candidate search with four
mismatches, one DNA bulge and one RNA bulge. S3 is a sensitivity layer; differences from S2 are
reported rather than used to silently change thresholds.

## Technical acceptance gate

Each stage must:

1. run twice with the exact package and input hashes recorded;
2. exit successfully without unexpected stderr;
3. produce non-empty target and profile artifacts;
4. produce identical target rows after canonical sorting across both runs;
5. record wall time, peak memory and disk use;
6. preserve raw engine output separately from derived summaries.

Passing these conditions yields `TECHNICAL_OFF_TARGET_RESULTS_READY_FOR_REVIEW`, not synthesis
approval. Biological promotion still requires CRISPRa/TSS placement, on-target assessment,
cloning/vector compatibility and independent review.

## Still blocked after this protocol

- derivation and hashing of the RefSeq annotation BED;
- annotation-category and score interpretation thresholds;
- variant-aware sensitivity;
- final guide replacement criteria based on combined on/off-target evidence;
- execution on an approved scratch host.

## Primary sources

- CRISPRitz 2.7.0 release:
  <https://github.com/pinellolab/CRISPRitz/releases/tag/v2.7.0>
- versioned Bioconda packages and checksums:
  <https://api.anaconda.org/release/bioconda/crispritz/2.7.0>
- official installation test and parameters:
  <https://raw.githubusercontent.com/pinellolab/CRISPRitz/master/test_scripts/auto_test_crispritz_docker.sh>
- official EMX1 control:
  <https://raw.githubusercontent.com/pinellolab/CRISPRitz/master/test_scripts/EMX1.sgRNA.txt>
- official SpCas9/NGG pattern:
  <https://raw.githubusercontent.com/pinellolab/CRISPRitz/master/test_scripts/20bp-NGG-SpCas9.txt>
