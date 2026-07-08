# Literature gaps and the big-picture narrative

**Status: framing document.** Where ISCI/T-REMAP sits relative to the field, what
gap it fills, and the honest scope of the claim.

## The gap the field leaves open

The immune-resistance / CAR-T-failure literature is dominated by **association**:
markers (TOX, TCF7, FOXO1, exhaustion signatures) that *correlate* with outcome.
Two structural gaps:

1. **Control vs association is rarely separated at genome scale, with confounder
   control.** Perturb-seq gives causal effect vectors, but the obvious ranking
   (effect magnitude) is confounded — known regulators simply have larger effects,
   so any index tested *against* magnitude wins by construction. The valid question
   — does a feature add signal *conditional on* magnitude? — is under-asked. ISCI's
   magnitude-conditional test (AUPRC 0.722 vs 0.415 within the detectable set,
   Spearman with magnitude ≈ 0.02) is the direct answer.

2. **The field speaks in terminal-state markers; control often lives one layer up.**
   Our controllers lean toward **regulatory layers of state** — chromatin
   (KDM1A/RCOR1/SETDB1/USP22), RNA/post-transcriptional (Regnase-1/HNRNPM/IRF2BP1),
   the NF-κB/TCR activation window, and synapse/migration — not the classic
   exhaustion markers. Even though the family-enrichment test is a statistical
   negative with broad gene-sets, the *composition* points away from markers and
   toward state-stabilizing machinery. That reframing is the original contribution.

## The big-picture narrative (honest, no clinical over-claim)

> **T-cell controllership has two layers: a known TCR-signal-strength rheostat,
> and a magnitude-independent layer of reproducible, axis-specific state
> controllers enriched for chromatin, RNA, NF-κB output, and synapse/migration.
> ISCI separates control from association; T-REMAP turns controllers into a
> sensitivity/resistance reversal map. Early evidence says the sensitivity axis
> (memory-stem / migration / killing) is a replicable CAR-T-product signal, while
> resistance is compartment-, time-, and niche-dependent.**

The framework's contribution is methodological and mechanistic: a way to separate
**marker / magnitude / TCR-rheostat / specific controller / intervention
hypothesis** — not a cure claim.

## Prior positive and negative analyses we build on

- **Positive (literature):** TCR signal strength → fate (Front Immunol 2025);
  dasatinib/rest restores memory-like CAR-T (PMC8049103); LCK dispensable for CAR,
  its loss improves persistence (Cell Rep Med 2023); Regnase-1 deletion boosts
  CAR-T persistence.
- **Positive (ours):** ISCI recovers known regulators conditional on magnitude;
  sensitivity axis replicates direction in GSE208052 (R_memory_stem p=0.032).
- **Negative (ours, reported honestly):** D4 mean-signature does not predict CAR-T
  response (CV-AUROC 0.53); resistance axis does not replicate in the pre-infusion
  product; mechanistic-family enrichment is not FDR-significant with broad gene-sets;
  network/PageRank influence adds nothing over magnitude.

## Ways to further prove it (mapped to feasibility)

| Modality | What it would prove | Feasibility |
|---|---|---|
| Phospho-signaling | TCR controllers act at protein/signaling level | Post-submission (needs dataset) |
| More transcriptome cohorts | Direction replication breadth | Now (gate-limited) |
| Targetability (HPA/OT/ChEMBL) | Which controllers are tractable | Now (connectors) |
| Spatial | Resistance lives in a niche | IDOR / post-hackathon |
| Cell-level Marson (22M) | Intra-perturbation heterogeneity | Needs institutional compute |

## The one-sentence pitch

**From genes to mechanisms; from transcriptome to protein and niche; from a score
to an intervention map — with control separated from association at every step.**
