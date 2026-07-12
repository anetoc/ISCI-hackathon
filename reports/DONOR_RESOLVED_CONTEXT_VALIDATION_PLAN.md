# Donor-resolved context validation decision and acquisition plan

**Decision:** do not download the full GSE190604 raw study locally for confirmatory inference.

## Why this is a no-go for confirmation

Official GEO metadata establish that the experiment used the same two blood donors across no-stim
and stimulated conditions, but mixed them 1:1 before loading four replicate wells per condition.
The committed processed matrix has no donor identifier, and well number is not donor identity.

The eight raw mRNA runs in SRP350148 report approximately 154.2 GB of downloads, versus 19.1 GB
free during intake. Raw deconvolution would therefore require external scratch infrastructure.
More importantly, it would resolve only two donors. That can test whether the direction agrees in
both individuals, but cannot estimate between-donor variation well enough to confirm a population
context interaction. The scientific return does not justify a local download or cloud spend as the
next confirmatory step.

## Acquisition outcome

The source-backed search completed on 2026-07-12 found six diagnostically useful datasets and no
confirmatory `GO`. The adjudication is recorded in `reports/DONOR_DATASET_ACQUISITION_REPORT.md` and
`outputs/decomposition_v2/donor_dataset_inventory.json`. In particular, the five-individual
CRAFTseq Th1/Treg experiment edits only one IL2RA variant and its cell-level IL2RA dataset is not in
the public Zenodo deposits. It cannot be used as a small external controller panel.

## Preferred acquisition target

Find or generate a CD4/T-cell perturbation dataset satisfying all gates below:

1. donor identity is explicit or recoverable in the released processed object;
2. the same donors contribute matched no-stim and stimulated arms;
3. perturbation and NO-TARGET/control cells are available in both arms;
4. at least six evaluable donors are present; 8–12 is preferred, with the final sample size set by
   simulation from pilot donor variance rather than by this heuristic;
5. at least eight frozen positive genes and fifteen frozen negatives pass coverage in each arm;
6. target, guide, donor, context and cell-count fields are documented;
7. raw clinical or participant identifiers are absent; pseudonymous donor IDs are sufficient.

Datasets failing gates 1–5 may be used for method development or descriptive diagnostics, not for
claim promotion.

## Prospective panel readiness

The outcome-blind design is now executable and versioned in
`outputs/decomposition_v2/prospective_donor_panel.csv` and its JSON summary. The primary inference
panel contains PRKD2, CD27, TRAF3IP2, PIK3AP1, GRAP, TNFRSF9, IL2RB and IL2RG plus all fifteen
frozen matched negatives. GATA3 and TBX21 are mechanistic sentinels outside the primary metric.
With two guide candidates per target and four non-targeting candidates, the design has 25 target
genes and 54 guide constructs.

At the default target of 50 usable cells per guide×donor×context and a conservative 60% combined
usable fraction, the planning scenarios are:

| donors | usable cells | captured cells | planning channels at 20k recovered cells |
|---:|---:|---:|---:|
| 8 | 43,200 | 72,000 | 4 |
| 10 | 54,000 | 90,000 | 5 |
| 12 | 64,800 | 108,000 | 6 |

The 20k channel capacity is a configurable costing unit, not a vendor guarantee. Oligo ordering
remains blocked because the local public artifact contains guide IDs but not validated protospacer
sequences. The sequence mapping, CRISPRa/vector compatibility, on-target activity and
sequence-specific off-target review must close before synthesis. The governing selection and
substitution rules are frozen in `reports/PROSPECTIVE_DONOR_PANEL_PROTOCOL.md`.

## Frozen analysis shape for a suitable dataset

- Build target×donor×context pseudobulk effects against donor/context-matched controls.
- Preserve the current axes and controller labels; do not revise them after dataset inspection.
- Use cross-classified held-out predictions: each test cell in the evaluation grid is both a held
  gene and a held donor. Training excludes that gene across all donors and that donor across all
  genes.
- Fit reach-only and reach-plus-residual-precision models inside training folds.
- Compute donor-specific `ΔAUPRC_no-stim − ΔAUPRC_stim` and a donor-weighted aggregate.
- Bootstrap donors outside genes, then genes within donor, preserving the paired contexts.
- Permute controller labels once per gene across every donor and exchange context within
  gene×donor for the interaction null.
- Report heterogeneity and leave-one-donor-out influence; no pooled-only verdict.

## Promotion gate

Promotion beyond `DIRECTIONAL_UNCERTAIN` requires all of:

- positive aggregate context contrast;
- donor-bootstrap interval above zero;
- gene-label and context-exchange permutation p<0.05;
- no single donor changes the sign of the aggregate when removed;
- at least 70% of evaluable donors have a positive contrast.

Multiplicity must include any additional axes or contexts opened in the same analysis family.

Pilot power sensitivity is generated with `scripts/plan_donor_context_power.py`. Its output is a
planning artifact only and cannot promote a claim because donor summaries cannot reproduce the
gene-label or within-gene×donor context-exchange nulls.

## Optional GSE190604 donor recovery

Genotype-based demultiplexing of GSE190604 remains a valid diagnostic only if temporary external
compute/storage is separately authorized. Its allowed conclusion is consistency or heterogeneity
between two recovered donor clusters. It cannot satisfy the promotion gate above and should not
delay acquisition of a donor-resolved multi-donor dataset.

## Sources

- NCBI GEO GSM5726254 and GSM5726258 extraction protocols: two donors mixed 1:1 per condition.
- NCBI SRA SRP350148: eight mRNA runs reporting 154.2 GB total download size.
- Machine-readable intake: `outputs/decomposition_v2/gse190604_intake.json`.
