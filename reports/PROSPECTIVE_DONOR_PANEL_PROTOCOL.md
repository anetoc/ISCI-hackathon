# Prospective donor-resolved panel design protocol

**Status:** design freeze for implementation and costing; not an oligo order and not a wet-lab
authorization.

## Purpose

Build the smallest donor-resolved CD4+ T-cell perturbation panel that can test whether residual
state-shift precision adds predictive value beyond perturbation reach in matched no-stim and
stimulated contexts. The panel is a prospective validation instrument for the existing controller
labels. It does not alter ISCI-core, its axes, or its frozen benchmark labels.

The selection is intentionally technical. Although GSE190604 outcomes have already been analyzed,
the panel builder must not read effect reach, signed projections, Th2 precision, repeatability,
replication verdicts, or any other outcome-derived feature.

## Primary inference panel

The primary panel contains:

- eight frozen positive regulators, selected only by guide coverage;
- all fifteen frozen Marson-native expression-matched negatives;
- two independent guide candidates per target.

For every frozen positive, count singleton guide assignments separately in no-stim wells 1–4 and
stimulated wells 5–8. Its technical coverage score is the minimum cell count across both candidate
guides and both contexts. Rank positives by descending score, breaking ties by gene symbol, and
retain the first eight. All fifteen `is_matched_negative` genes are retained regardless of their
coverage so the negative reference set cannot be optimized after seeing the external data.

Guide IDs are inherited from the public GSE190604 annotation. They are **candidate identities, not
validated oligo sequences**. The local source has guide IDs and cell assignments but no protospacer
sequences. Every guide therefore remains `REQUIRES_DESIGN_AND_VALIDATION` until its sequence,
targeting modality, on-target score, off-target profile, construct compatibility, and synthesis
record are independently verified.

## Sentinels and controls

GATA3 and TBX21 are included as mechanistic/axis sentinels when they are not already in the primary
panel. They are analyzed descriptively and do not count as positive labels in the primary AUPRC or
context-interaction test. This preserves canonical Th2/Th1 biology without inflating the
pre-existing controller benchmark.

Include four independent non-targeting guide candidates. Rank public `NO-TARGET` IDs by their
minimum cell count across the two contexts, then by total cell count and ID, and retain four. These
controls define the donor- and context-matched reference distribution. They also require sequence
and construct validation before ordering.

## Resource-planning assumptions

The default design target is 50 usable cells per guide, donor, and context. “Usable” means a
post-QC singlet with an accepted guide assignment and the metadata required for the frozen analysis.
With two guides per target, this targets 100 usable cells per target×donor×context and stays above
the existing 25-cell minimum even after guide-level stratification.

Planning scenarios use:

- 8, 10, and 12 independent donors;
- two paired contexts per donor;
- 60% combined usable fraction after capture, QC, singlet filtering, and guide assignment;
- 20,000 recovered cells per channel as a configurable planning unit, not a vendor guarantee.

For `G` guide constructs and `D` donors:

```text
usable cells = G × D × 2 contexts × 50
captured cells = ceil(usable cells / 0.60)
planning channels = ceil(captured cells / 20,000)
```

The calculator must expose all assumptions as parameters. Final loading, multiplexing, sequencing
depth, expected multiplet rate, guide-capture chemistry, batch blocking, and reserve material must
be set with the experimental core before execution.

## Experimental blocking and analysis boundary

- Each donor contributes both contexts; context is paired within donor.
- Guides and controls must be represented across batches rather than assigned to a single batch.
- Donor is the biological replicate. A well, channel, library, or guide is not a donor replicate.
- Primary effects are target×donor×context pseudobulks against donor/context-matched non-targeting
  controls, with guide-level estimates retained for reproducibility.
- The promotion gate remains the one defined in
  `reports/DONOR_RESOLVED_CONTEXT_VALIDATION_PLAN.md`.
- GATA3/TBX21 sentinels, guide QC, and non-targeting controls cannot be relabeled as primary
  positives after outcome inspection.
- Guide substitutions after sequence validation are permitted only with a documented reason and a
  regenerated manifest; target membership remains frozen unless the PI approves a protocol change.

## Required generated artifacts

The implementation must emit:

1. a guide-level CSV manifest with target role, inclusion in the primary metric, coverage evidence,
   and sequence-validation status;
2. a JSON summary with selected targets, panel counts, resource scenarios, boundaries, command,
   timestamp, Git SHA, and SHA-256 hashes of every input;
3. deterministic tests proving that outcome-derived columns cannot influence target selection.

