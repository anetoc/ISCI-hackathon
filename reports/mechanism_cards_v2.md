# Mechanism cards v2 — with matched-null statistics and 3-layer T-REMAP

**Status: expansion, built on the locked ISCI_orthogonal core.** This version
adds (i) the family enrichment test against two matched nulls and (ii) the
three-layer T-REMAP residualization, so each card separates *descriptive family
membership* from *statistically-tested enrichment* and from *confounder-robust
reversal candidates*.

## Global honest read (must precede the cards)

- **Family enrichment is a HONEST NEGATIVE.** Using established GO/Hallmark/
  Reactome gene-sets to define families genome-wide, then a 1000× matched null,
  no family survives BH-FDR in either null. chromatin/tx is the only nominally
  enriched family (Null A fold 1.46, p=0.02) and it **attenuates** once
  TCR-shutdown is added to the matching (Null B fold 1.18, p=0.08). So the
  mechanistic families are a **descriptive, chromatin-leaning composition**, not
  a statistically over-represented signal. We report them as hypotheses, not
  claims.
- **The core is confounder-robust.** ISCI_orthogonal stays clean against all
  nine confounders in ledger v2 (max |Spearman| = 0.10, including stress,
  cell-cycle, mitochondrial, IFN). ISCI_combined remains magnitude-dominated
  (rho = 0.55) and is secondary.
- **Only 7/20 T-REMAP reversers survive full residualization.** The
  confounder-robust set is IRF2BP1, MED13, PDCD10, CXXC1, CCDC28B, WBP4, RBSN —
  the rest were partly stress/IFN artifact.

---

## Card 1 — Chromatin / transcription-state control
**Family (top-50):** RCOR1, SETDB1, HEXIM1, SAMD1, KDM1A, BRD9, CTBP1, USP22,
PHF8 and others (n=15, largest family). SETDB1 is a known regulator.
- **Enrichment:** obs 18; Null A fold 1.46 (p=0.02); Null B fold 1.18 (p=0.08); not FDR-significant.
- **Observed:** high donor-coherent axis-specificity; the family spans the full
  magnitude range (within-top-50 ISCI vs magnitude rho = −0.22), so it is not a
  magnitude proxy.
- **Confounder-robust reversers here:** CXXC1 (CpG-island / SETD1 complex),
  MED13 (Mediator kinase module) survive resid_v2.
- **Literature:** KDM1A/LSD1, RCOR1/CoREST, USP22/SAGA are validated chromatin
  state regulators; none are classic exhaustion markers — this is the novel angle.
- **Caveat:** family enrichment not FDR-significant; interpret as chromatin-leaning hypothesis.
- **Next experiment:** ATAC/CUT&RUN on the robust hits; phospho not applicable.

## Card 2 — NF-κB / TCR-activation window
**Family (top-50):** IKBKB, RBCK1, PTPRC, CD3D, CD3E (n=5).
- **Enrichment:** obs 10; Null A fold 1.27 (p=0.22); Null B fold 1.14 (p=0.28).
- **Observed / reframe:** this family sits at the heart of the TCR-rheostat
  reframe. The raw T-REMAP axis is dominated by TCR-proximal machinery
  (Card companion: tcr_reframe.md). After residualizing TCR-shutdown, **NFKB1
  survives as a specific reverser** while the pure TCR-complex members drop
  sharply (CD3D/CD3E fall out of the top).
- **Literature anchor:** dasatinib/rest (Weber et al., Science 2021, PMC8049103),
  LCK-KO CAR-T (Wu et al., Cell Rep Med 2023, PMID 36696897).
- **Intervention direction:** transient inhibition / titratable — NOT permanent KD
  (permanent TCR shutdown is a manufacturing/activation artifact, not a target).

## Card 3 — IFN / Th1 output
**Family (top-50):** IRF1, STAT6, GATA3 (known regulators) + TFAP4, IL2RB, KLF13 (n=6).
- **Enrichment:** obs 6; Null A fold 1.56 (p=0.12); Null B fold 1.16 (p=0.33).
- **Observed:** recovery of IRF1/STAT6/GATA3 is a **sanity control (validation,
  not discovery)** — these are axis-marker known regulators.
- **Caveat:** IFN-global is itself a confounder (reversal_raw rho = 0.17 in ledger v2);
  IFN-family reversal hits are down-weighted after resid_v2.

## Card 4 — RNA / post-transcriptional control
**Family (top-50):** BCLAF1, ZC3H12A/Regnase-1, HNRNPA1, HNRNPD, SMG8 (n=5). All novel.
- **Enrichment:** obs 10; Null A fold 1.02 (p=0.54) — NOT enriched beyond background.
- **Observed:** HNRNPM (an RNA-binding protein) tops the TCR-residualized reversal
  list; IRF2BP1 (transcriptional corepressor) is the #1 fully-residualized reverser.
- **Literature:** Regnase-1/ZC3H12A is a validated CAR-T engineering target
  (deletion boosts persistence) — recovered independently by ISCI.
- **Caveat:** RNA-level control inferred from steady-state effect vectors, not decay.

## Card 5 — Migration / synapse / killing + cytoskeleton
**Family (top-50):** TWF1, ARHGAP30, MYO9A + actin/synapse modules (n=3).
- **Enrichment:** obs 8; Null A fold 1.19 (p=0.35).
- **Observed:** this is the **sensitivity axis that replicated externally** —
  in CAR-T GSE208052, R_migration/R_killing/R_memory were higher in responders
  (R_memory_stem p=0.032, one-sided), concordant with that study's own
  killing/migration/actin finding.
- **Clinical read:** product-visible sensitivity axis.

## Card 6 — Treg / brake + apoptosis / survival
**Family (top-50):** NR4A3, PTEN, INPP5D (Treg/brake) + PDCD5, PRKDC, CASP3 (apoptosis) (n=6).
- **Enrichment:** Treg/brake obs 2, fold 2.43 (p=0.19, tiny n); apoptosis obs 18, fold 1.35 (p=0.06).
- **Observed:** PDCD10 survives resid_v2 as a robust reverser. The **resistance
  axis did NOT replicate externally** (GSE208052, 0/3 modules) — compartment-dependent.
- **Caveat:** apoptosis/stress is a confounder; apoptosis-family reversal hits are
  down-weighted after resid_v2. Honest negative on resistance replication.
