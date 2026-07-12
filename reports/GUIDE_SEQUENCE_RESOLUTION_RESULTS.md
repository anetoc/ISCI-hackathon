# Prospective panel guide-sequence resolution results

**Verdict:** `SOURCE_IDENTITIES_RESOLVED_SYNTHESIS_BLOCKED`

## Result

All 54 prospective-panel guide IDs were linked to a unique, observed 20-nt Calabrese protospacer.
Fifty-three pass the source-identity gate of at least 10 exact candidate-read matches across at
least two independent wells. `PAPOLG-1` was observed once in one well and remains
`SOURCE_IDENTITY_LOW_SUPPORT`. There are no unresolved IDs, non-shadow ambiguities or duplicate
protospacers in the panel.

Source identity is not synthesis approval. All 54 guides remain blocked pending vector/cloning
compatibility, a versioned human reference and transcript/TSS choice, and sequence-specific
on-target/off-target evaluation.

## Evidence recovered

The resolver used the first 10 MiB compressed prefix of each R1/R2 guide FASTQ for no-stim wells
1–4, totaling 80 MiB rather than downloading the full guide-read study. Across 1,613,995 paired
reads, 75,084 mapped exactly to a prospective-panel cell barcode after the deterministic custom
barcode transform, and 34,515 contained a same-target Calabrese candidate.

| well | ENA run | read pairs examined | panel-barcode pairs | same-target candidate pairs |
|---:|---|---:|---:|---:|
| 1 | SRR17189067 | 345,283 | 11,243 | 2,015 |
| 2 | SRR17189068 | 422,561 | 23,406 | 12,519 |
| 3 | SRR17189069 | 427,794 | 25,458 | 14,376 |
| 4 | SRR17189070 | 418,357 | 14,977 | 5,605 |

The sequence mapping is supported by the authors' Calabrese CRISPRa MAGeCK summaries in Zenodo
record 5784651 and direct observations in ENA guide reads. The Supplementary Table S3 arrayed-guide
list was reviewed but deliberately not used as an ordinal mapping for Perturb-seq IDs.

## Basic sequence triage

Simple motif checks are flags, not off-target scores:

- 45 guides have no basic flag;
- 5 contain a five-base homopolymer;
- 3 have GC fraction above 80%;
- 1 has GC fraction below 25%;
- none contains a detected BsmBI recognition site under the current check.

These flags identify guides for focused review or backup design. They do not prove poor activity and
must not be used alone to replace a guide after outcome inspection.

## Reproducibility and privacy boundary

- `outputs/decomposition_v2/gse190604_calabrese_panel_candidates.csv` records compact source
  candidates and member hashes.
- `outputs/decomposition_v2/gse190604_guide_sequence_evidence.csv` contains only aggregate
  guide×sequence×well counts and source hashes.
- `outputs/decomposition_v2/prospective_donor_panel_sequences.csv` is the resolved manifest.
- `outputs/decomposition_v2/prospective_donor_panel_sequences.json` is the machine-readable verdict.
- Raw read names, cell barcodes and FASTQ fragments are not committed.

## Next gate

The next implementation slice is a sequence-QC and replacement shortlist followed by a real
off-target run. At the time of this result, the local workspace had neither a versioned human genome
reference nor an installed CRISPR off-target engine. This is an environment/setup boundary, not a
negative result. The reference build, transcript/TSS annotation and scoring thresholds must be
frozen before any guide is promoted or substituted.

