# The 4D controllability decision framework (C → G → T → L)

The project's mature deliverable is not a ranking but a **decision framework** that keeps four
questions separate and never collapses them into one therapeutic super-score:

| Dimension | Question | Source |
|-----------|----------|--------|
| **C — Controller** | Does the gene control a T-state axis independent of magnitude? | ISCI_orthogonal + axis-specificity + donor coherence (Marson CD4+ RNA) |
| **G — Convergence** | Does perturbing it push toward a desirable phenotype? | signed module-reversal / therapeutic convergence (independent 3rd axis) |
| **T — Targetability** | Is it manipulable with acceptable safety? | druggability tier + intervention direction + penalty flags (descriptive) |
| **L — Clinical relevance** | Does the axis matter in patients? | capped at L1: the cross-study CAR-T response test was a **well-powered NULL** |

**Why a tree, not a weighted score.** Averaging C/G/T/L into one number would repeat the original ISCI
mistake (the full multiplicative index lost to magnitude). The framework instead assigns a **decision
class** by logic:

```
if controller high and convergence unfavorable      -> E: wrong-way controller (mechanism, not target)
elif dangerous (essential/DNA-repair/TCR-proximal)   -> D: dangerous rheostat (control/avoid)
elif controller high and convergence favorable       -> B: engineering candidate
elif controller high and convergence neutral         -> C: probe-only biology
elif controller low and convergence favorable        -> F: phenotype-associated, weak controller
```

## Decision-class counts (n=1260 detectable-set genes)

| Decision class | n |
|---|---|
| F — Phenotype-associated, weak controller | 646 |
| C — Probe-only biology | 561 |
| C — Probe-only biology (controls axis, direction unclear) | 17 |
| D — Dangerous rheostat (control/avoid) | 15 |
| B — Engineering candidate (favorable + controllable) | 12 |
| E — Wrong-way controller (mechanism, not target) | 9 |

## The headline the framework produces

> **Not every controller is a target. Not every targetable gene is safe. Not every biological axis is
> clinically predictive. This framework adjudicates all four — and returns FAIL/NULL when the evidence
> does not support a claim.**

The concrete exemplar is **IRF1**: the #1 controller by ISCI_orthogonal, yet negative convergence
(pushes the wrong way) — a mechanism, not a target. See Figure `controller_convergence_quadrant.png`.

## Top-12 decision cards

### IRF1
- **Controller:** top-controller (rank 1, ISCI_orthogonal 0.951)
- **Convergence:** unfavorable (-0.207)
- **Targetability:** D_dangerous_rheostat, tier no_chembl_target, titratable — flags: tumor-suppressor(KD-oncogenic-risk)
- **Clinical relevance:** L1 (axis literature) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **E — Wrong-way controller (mechanism, not target)**
- **Best next experiment:** positive control for axis specificity (do NOT engineer toward)
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### IKBKB
- **Controller:** top-controller (rank 2, ISCI_orthogonal 0.949)
- **Convergence:** favorable (+0.170)
- **Targetability:** D_dangerous_rheostat, tier clinical_drug, transient_inhibition — flags: TCR/signaling-proximal
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **D — Dangerous rheostat (control/avoid)**
- **Best next experiment:** transient titration + phospho-flow only (dangerous NF-κB rheostat)
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### BCLAF1
- **Controller:** top-controller (rank 3, ISCI_orthogonal 0.924)
- **Convergence:** favorable (+0.154)
- **Targetability:** C_probe_only, tier chembl_target, titratable
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **B — Engineering candidate (favorable + controllable)**
- **Best next experiment:** CRISPRi probe; RNA/splicing mechanism readout
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### TFAP4
- **Controller:** top-controller (rank 4, ISCI_orthogonal 0.922)
- **Convergence:** favorable (+0.489)
- **Targetability:** C_probe_only, tier no_chembl_target, titratable
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **B — Engineering candidate (favorable + controllable)**
- **Best next experiment:** CRISPRa/i in primary T; effector-expansion readout
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### CYB561D2
- **Controller:** top-controller (rank 5, ISCI_orthogonal 0.917)
- **Convergence:** unfavorable (-0.160)
- **Targetability:** C_probe_only, tier no_chembl_target, titratable
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **E — Wrong-way controller (mechanism, not target)**
- **Best next experiment:** probe only; wrong-way convergence, mechanism unclear
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### PDCD5
- **Controller:** top-controller (rank 6, ISCI_orthogonal 0.913)
- **Convergence:** favorable (+0.205)
- **Targetability:** C_probe_only, tier chembl_target, titratable
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **B — Engineering candidate (favorable + controllable)**
- **Best next experiment:** CRISPRi probe; apoptosis/differentiation readout
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### ZC3H12A
- **Controller:** top-controller (rank 7, ISCI_orthogonal 0.908)
- **Convergence:** neutral (+0.124)
- **Targetability:** C_probe_only, tier no_chembl_target, transient_inhibition
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **C — Probe-only biology (controls axis, direction unclear)**
- **Best next experiment:** transient inhibition + mRNA-decay (SLAM-seq) readout; Regnase-1 CAR-T literature
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### STAT6
- **Controller:** top-controller (rank 8, ISCI_orthogonal 0.906)
- **Convergence:** neutral (-0.062)
- **Targetability:** C_probe_only, tier chembl_target, titratable
- **Clinical relevance:** L1 (axis literature) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **C — Probe-only biology (controls axis, direction unclear)**
- **Best next experiment:** axis positive control (Th2); titratable, direction context-dependent
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### RCOR1
- **Controller:** top-controller (rank 9, ISCI_orthogonal 0.903)
- **Convergence:** favorable (+0.902)
- **Targetability:** A_manufacturing_modulation, tier no_chembl_target, transient_inhibition
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **B — Engineering candidate (favorable + controllable)**
- **Best next experiment:** CRISPRi / titrated inhibitor; persistence-vs-exhaustion readout (manufacturing)
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### PRKDC
- **Controller:** top-controller (rank 10, ISCI_orthogonal 0.902)
- **Convergence:** favorable (+0.430)
- **Targetability:** D_dangerous_rheostat, tier clinical_drug, transient_inhibition — flags: broadly-essential
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **D — Dangerous rheostat (control/avoid)**
- **Best next experiment:** transient inhibition only; broadly essential / DNA-repair risk
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### SETDB1
- **Controller:** top-controller (rank 11, ISCI_orthogonal 0.899)
- **Convergence:** neutral (+0.027)
- **Targetability:** A_manufacturing_modulation, tier chembl_target, transient_inhibition
- **Clinical relevance:** L1 (axis literature) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **C — Probe-only biology (controls axis, direction unclear)**
- **Best next experiment:** CRISPRi probe; chromatin/manufacturing modulation
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status

### TWF1
- **Controller:** top-controller (rank 12, ISCI_orthogonal 0.896)
- **Convergence:** neutral (+0.116)
- **Targetability:** C_probe_only, tier no_chembl_target, titratable
- **Clinical relevance:** L0 (no direct clinical evidence) (cross-study CAR-T response = well-powered NULL)
- **Decision class:** **C — Probe-only biology (controls axis, direction unclear)**
- **Best next experiment:** probe; cytoskeleton/synapse axis, persistence link
- **Do-not-claim:** therapeutic recommendation; clinical biomarker status


*Clinical relevance is capped at L1 for every gene: no IEC axis is a transportable CAR-T response
biomarker under leave-one-study-out CV (best axis AUROC 0.533, CD8 fraction beats all). Targetability
is experimental triage, not a treatment list. Nothing here is medical advice.*
