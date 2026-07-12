# Guide QC and replacement-shortlist protocol

**Status:** technical triage frozen before fallback generation. No current guide is replaced by this
protocol, and no oligo is approved for synthesis.

## Purpose

Prepare an auditable set of backup protospacers for guides that require additional review while
preserving the frozen target panel and prospective analysis. This is assay engineering, not a new
controller-ranking analysis.

## Review triggers

A current guide enters review when at least one condition is true:

- source identity is not `SOURCE_IDENTITY_CONFIRMED`;
- its 20-nt sequence contains `TTTT` or a five-base homopolymer;
- GC fraction is below 25% or above 80%;
- a BsmBI recognition site is present.

These are conservative screening flags. They do not prove that a guide is inactive, unsafe or
unclonable. A flagged guide stays in the current manifest until a validated replacement decision is
recorded.

## Fallback universe and ordering

For every target with at least one current guide in review:

1. use only same-target Calabrese candidates already present in the committed public source table;
2. exclude all protospacers already assigned to that target;
3. calculate the same basic sequence flags used for current guides;
4. rank candidates with no basic flag before flagged candidates;
5. break ties by best source-screen rank, then larger source-screen LFC, then sequence;
6. retain up to three candidates per target.

Guide-level source-screen evidence may order technical fallbacks because this choice is frozen
before prospective data collection. It cannot alter controller labels, ISCI-core, axes, target
membership or the interpretation of completed external replication results.

Replacement priority is `HIGH_ALL_CURRENT_GUIDES_REVIEW` when both current target guides trigger
review. It is `BACKUP_ONLY` when at least one current guide remains unflagged and source-confirmed.

## Off-target input contract

The generated screening package contains all 54 current guides plus the fallback shortlist with:

- target, role and current/fallback identity;
- 20-nt protospacer;
- intended modality `CRISPRa`;
- nuclease family `SpCas9` and PAM contract `NGG` inherited from the Calabrese/SAM system;
- source evidence and basic motif flags;
- explicit empty fields for reference build, transcript/TSS annotation and off-target result.

Reference build and transcript/TSS annotation must be selected in a dedicated, source-backed
decision before scoring. Empty fields are a blocking state, not permission to use a tool default.

## Promotion gate

A fallback may replace a current guide only after all of:

- authoritative same-target source identity;
- versioned human reference and annotation recorded;
- CRISPRa/TSS placement reviewed;
- genome-wide off-target search with documented mismatch, PAM and bulge settings;
- on-target assessment appropriate for CRISPRa;
- vector/cloning compatibility;
- independent review and regenerated panel manifest.

No prospective outcome may be inspected before the substitution decision is frozen.

