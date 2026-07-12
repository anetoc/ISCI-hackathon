# GSE190604 guide-sequence resolution protocol

**Status:** source-identity protocol frozen before the committed resolver output. This protocol
does not authorize oligo synthesis.

## Question

Can every guide ID in the prospective donor panel be linked to an observed 20-nt protospacer from
an authoritative public source without inferring a sequence from the `GENE-1` or `GENE-2` label?

## Source boundary

The article's Supplementary Table S3 lists arrayed validation guides. It is not a complete mapping
for the Perturb-seq library. The Methods state that Perturb-seq used the two selected Calabrese
screen guides for each target. Therefore, a Table S3 sequence must not be assigned to a Perturb-seq
ID merely because its gene and ordinal number match.

The resolution uses three public evidence layers:

1. the CRISPRa IL2 and IFNG sgRNA summary members in the authors' Zenodo record 5784651, which
   provide Calabrese protospacer sequences and screen evidence;
2. GSE190604 singleton guide calls, which link processed cell barcodes to `GENE-N` feature IDs;
3. the first 10 MiB compressed prefix of both guide FASTQs from each no-stim well, ENA runs
   SRR17189067 through SRR17189070, which provide direct sequence evidence without downloading the
   full approximately 40 GB guide subset for those wells.

Only aggregate guide×sequence×well counts may be committed. Raw read names, cell barcodes, FASTQ
fragments and donor-related records remain temporary and are deleted after validation.

## Barcode and sequence reconciliation

For every paired guide read:

1. take the first 16 bases of read 1;
2. complement bases 8 and 9 using one-based coordinates;
3. require an exact match to a singleton processed barcode in the corresponding well;
4. derive the target from the matched public feature ID;
5. scan read 2 for exact 20-mers present among Calabrese candidates for that same target;
6. aggregate unique candidate matches by guide ID, sequence and well.

The two-base complement is not an error-tolerant barcode search. Across all four sampled wells it
recovers the dominant deterministic mapping between the custom guide-library read and the processed
barcode. No Hamming-distance rescue is allowed.

The U6 cassette can add a leading G before a protospacer that does not begin with G. If two
Calabrese candidates occur as overlapping 20-mers in the same reads and one is `G + first 19 bases`
of the other, the leading-G shadow is removed and the original candidate is retained. Source screen
rank is used only as a deterministic tie-break after this structural rule; it cannot introduce a
sequence absent from the raw evidence.

## Resolution and synthesis states

- `SOURCE_IDENTITY_CONFIRMED`: one unique protospacer is observed and supported by at least 10
  exact candidate-read matches across at least two wells.
- `SOURCE_IDENTITY_LOW_SUPPORT`: one unique protospacer is observed but misses either evidence
  threshold. It remains resolved for traceability but requires targeted source confirmation before
  synthesis.
- `SOURCE_IDENTITY_AMBIGUOUS`: multiple non-shadow candidates remain tied or materially supported.
- `SOURCE_IDENTITY_UNRESOLVED`: no same-target Calabrese candidate is observed.

No guide may become `READY_FOR_SYNTHESIS` from source identity alone. Promotion requires all of:

- authoritative sequence identity;
- CRISPRa modality and pZR158/direct-capture cassette compatibility;
- current human reference build and transcript/TSS choice;
- sequence-specific on-target assessment;
- sequence-specific off-target assessment with documented thresholds;
- absence of disallowed cloning motifs or an approved mitigation;
- independent review of every low-support or substituted guide.

## Required artifacts

The implementation emits:

1. a compact public Calabrese candidate table with source hashes;
2. aggregate per-well raw evidence without cell barcodes or read identifiers;
3. a resolved panel manifest containing the original panel fields, protospacer, evidence counts,
   GC fraction, simple motif flags, source-identity state and synthesis state;
4. a JSON report with source URLs, byte ranges, hashes, rules, unresolved/ambiguous IDs and full
   provenance.

