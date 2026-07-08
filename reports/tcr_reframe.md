# TCR signal strength: a biological rheostat AND a translational confounder

**Status: expansion analysis, built on the locked ISCI_orthogonal core.**

## The reframe

In the first T-REMAP pass we treated the TCR-proximal reversal hits
(PLCG1, LAT, VAV1, LCP2, CD3G, CD247, ZAP70, LCK) as a *confounder* and
residualized them out. The literature makes clear this was only half right.

TCR signal strength is the **best-established deterministic controller of
T-cell fate**: strong/sustained signals push cells toward short-lived
terminal effectors and, ultimately, exhaustion (higher PD-1/LAG-3), while
attenuated signals favor long-lived memory/stem-like states
(Front Immunol 2025, 10.3389/fimmu.2025.1562248; CD4 memory, PMC6126666;
Nur77/Bim epigenetic control, Cell Death Differ 2019).

So the correct framing is dual, not dismissive:

> **TCR signal strength is simultaneously (i) a real biological rheostat of
> T-cell state and (ii) a confounder of naive therapeutic interpretation —
> "knock the TCR machinery down" is not a target recommendation.**

## What our data shows (`figures/tcr_reframe_convergence.png`)

- **Panel A — the raw T-REMAP axis recovers the TCR signaling machinery.**
  The top of the raw reversal score is dominated by TCR-proximal genes.
  This is the rheostat: perturbing TCR-signal components shifts cells along
  the memory↔effector axis (raw reversal ↔ R_memory_stem module,
  Spearman |rho| = 0.43, p ~ 1e-58 across the detectable set).
- **Panel B — specific controllers survive full confounder control.**
  After residualizing reversal against magnitude + TCR-shutdown + stress +
  cell-cycle + mitochondrial + IFN (confounder ledger v2), a smaller set of
  genes persists: IRF2BP1, MED13, PDCD10, CXXC1, CCDC28B, WBP4, RBSN.
  Only 7/20 of the TCR-residualized top-20 survive into the fully-residualized
  top-20 — i.e. ~13 of the "specific reversers" were partly stress/IFN artifact.

## External clinical anchor (literature, NOT our result)

Our raw axis predicts: reduce TCR-proximal signaling → memory-like →
less exhaustion. That is exactly what the CAR-T clinic already shows:

- **Dasatinib / CAR "rest"** restores a memory-like phenotype and antitumor
  function in exhausted CAR-T via epigenetic remodeling (PMC8049103).
- **LCK is dispensable for CAR signaling** (though essential for the TCR);
  LCK-disrupted CAR-T show better memory/persistence and less exhaustion
  (Cell Rep Med 2023).
- **Regnase-1 / ZC3H12A**, which ISCI recovered independently as a top
  controller, is a validated CAR-T engineering target (its deletion boosts
  persistence).

This is *direction validation from the literature*, not a claim we prove here.

## Honest caveats

- The proxy axis measures the effect on **expression** of TCR-complex genes,
  not phosphorylation/signaling activity. TCR-proximal KDs even *raise*
  TCR-gene expression (compensatory feedback), so the convergence with the
  literature is at the level of **gene identity** (our top hits ARE the TCR
  machinery that dasatinib/rest/LCK-KO modulate), not the sign of the proxy.
  Phospho-signaling validation (pLCK/pZAP70/pLAT/pPLCγ1) is the natural next
  test — see the phospho roadmap.
- Marson effects are knockdowns; a high raw-axis score means *knocking a TCR
  component down* moves cells toward memory. The therapeutic reading
  (transient inhibition vs permanent KD) is titratable and context-dependent,
  never "delete the TCR."

## Artifacts

`results/tcr_axis_scores.parquet`, `results/module_reversal_scores_resid2.parquet`
(3 layers: raw / resid_TCR / resid_v2), `outputs/confounder_ledger_v2.json`,
`figures/tcr_reframe_convergence.png`.
