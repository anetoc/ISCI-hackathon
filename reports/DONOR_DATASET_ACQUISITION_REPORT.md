# Donor-resolved perturbation dataset acquisition report

**Status:** `NO_PUBLIC_GO_IDENTIFIED`  
**Search date:** 2026-07-12  
**Machine-readable result:** `outputs/decomposition_v2/donor_dataset_inventory.json`

## Decision

No verified public dataset satisfies the frozen confirmatory gate: primary human T cells,
single-cell perturbation effects, donor-resolved matched contexts, the same perturbations and
controls in both contexts, at least six donors, and enough overlap with the frozen controller
labels. No large data download is authorized by this review.

## Candidate adjudication

| candidate | useful evidence | blocking boundary | decision |
|---|---|---|---|
| Schmidt, GSE190604 | exact CRISPRa panel; matched no-stim/stim; 23 positives and 46 negatives | two donors mixed 1:1; processed matrix has no donor identity | DIAGNOSTIC_ONLY, completed |
| Alda-Catalinas, E-MTAB-13324 | 250k primary CD4 CRISPRi profiles with non-targeting controls | one donor and one activated context | DIAGNOSTIC_ONLY |
| Ho, GSE297472/phs004072 | donor hashtags and primary CD4 scCRISPRi | three donors, one scCRISPRi context, sensitive donor-level data require controlled access | DIAGNOSTIC_ONLY |
| Chen, PRJDB16517 | 228-gene Perturb-icCITE-seq iTreg panel | one polarization context; donor metadata for the single-cell screen are not proven in the public article | DIAGNOSTIC_ONLY |
| Baglaenko CRAFTseq | five individuals and paired Th1/Treg editing | one IL2RA variant, below six donors; public Zenodo is software and the released dataset excludes IL2RA cells | DIAGNOSTIC_ONLY |
| speedingCARs, GSE214231 | 180 CAR constructs and scRNA-seq across three donors | constructs do not map to frozen gene labels; only standard CAR controls are unstimulated | DIAGNOSTIC_ONLY |

`DIAGNOSTIC_ONLY` means that a study can inform assay design, context biology or failure modes. It
does not mean that the dataset may be substituted into the confirmatory controller-recovery test.

## Strongest design lessons

1. GSE190604 proves that well replication cannot replace donor resolution.
2. CRAFTseq proves that individual-aware context effects are measurable, but a single edited locus
   cannot validate a controller-ranking property.
3. Large perturbation panels currently trade away donor count or matched contexts.
4. Multi-donor studies often expose donor-level sequencing only through controlled access, and
   controlled access alone does not repair an underpowered or single-context design.

## Recommended execution path

The next decisive step is a prospective targeted CRISPRa experiment rather than another broad
public-data reanalysis. Its computational design slice is now complete:

- frozen primary panel: PRKD2, CD27, TRAF3IP2, PIK3AP1, GRAP, TNFRSF9, IL2RB and IL2RG plus all
  fifteen matched negatives;
- GATA3 and TBX21 as mechanistic sentinels outside the primary metric;
- two guide candidates per target plus four non-targeting candidates, totaling 54 constructs;
- matched no-stim and stimulated arms for every donor;
- 8–12 donors as a planning range, with final n determined from pilot donor-contrast variance;
- target×guide×donor×context pseudobulk and on-target QC;
- cross-classified held-gene/held-donor evaluation defined in
  `reports/DONOR_RESOLVED_CONTEXT_VALIDATION_PLAN.md`.

The generated manifest and resource plan are
`outputs/decomposition_v2/prospective_donor_panel.csv` and
`outputs/decomposition_v2/prospective_donor_panel.json`. At 50 usable cells per
guide×donor×context and a 60% combined usable fraction, the 8/10/12-donor scenarios require
72,000/90,000/108,000 captured cells. These figures are planning assumptions, not assay-yield
guarantees.

The next gate is sequence resolution, not oligo ordering. Public GSE190604 guide IDs must be mapped
to authoritative protospacer sequences and pass CRISPRa/vector, on-target and sequence-specific
off-target validation. No sequence should be inferred from the identifier alone.

Until pilot donor-level variance exists, presenting a precise power-derived donor count would be
false precision. A power-planning utility is now implemented for the first real pilot:

```bash
python scripts/plan_donor_context_power.py \
  --input donor_contrasts.csv \
  --donor-counts 6,8,10,12,16 \
  --effect-scales 0.5,0.75,1.0
```

The input has exactly `donor,contrast` columns and requires at least four unique donors. The utility
models empirical residuals and effect shrinkage, then estimates the probability of passing the
donor-bootstrap, ≥70% positive-donor and leave-one-donor-out gates. It deliberately reports partial
gate power: gene-label and context-exchange permutations require gene×donor pilot data and are not
fabricated from donor summaries.

## Verified primary sources

- Schmidt GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE190604
- Alda-Catalinas BioStudies: https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-13324
- Ho article: https://www.nature.com/articles/s41588-025-02301-3
- Chen article: https://www.nature.com/articles/s41586-025-08795-5
- Baglaenko article and deposits: https://www.nature.com/articles/s41586-025-09313-3,
  https://zenodo.org/records/15425510, https://zenodo.org/records/15935857
- speedingCARs article: https://www.nature.com/articles/s41467-022-34141-8
