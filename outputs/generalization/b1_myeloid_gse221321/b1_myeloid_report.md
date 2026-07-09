# B1 far-test — CCI in non-T immune (THP-1 macrophage, GSE221321): **NEAR-MISS**

> **Pre-registered** in `reports/PREREGISTRATION.md` (tier B1) *before* this run. Prediction: PASS
> (property is immune-wide). **Outcome: near-miss** — the immune-specific axis-specificity signal
> transfers, but the combined verdict grazes the PASS threshold on reproducibility power. Reported
> honestly, no goalpost-moving.

## Verdict: NEAR-MISS (formally FAIL by the strict CI-excludes-0 rule)

| metric | value | pre-registered PASS bar | met? |
|---|---|---|---|
| bootstrap ΔAUPRC (M→M+C) | **+0.166** [-0.006, +0.374] | CI excludes 0 | **no** (lower bound -0.006 grazes 0) |
| base → full AUPRC | 0.239 → 0.405 | — | nearly doubles |
| conditional LR p (C over M) | **0.00938** | < 0.05 | **yes** |
| Spearman(C, magnitude) | +0.104 | small | **yes** (orthogonal) |
| direction-aware (C higher in positives) | 0.787 vs 0.498 | pos > neg | **yes** |

**n:** positives = 21 canonical NF-κB/TLR regulators, negatives = 120
expression/power-matched, detectable set = 299 of 597
perturbations.

## The scientifically important part — component decomposition
- **Axis-specificity S: p = 6.7e-05** — highly significant. The component the whitepaper
  identifies as *the immune-specific part of controllership* **transfers from CD4+ T cells to
  myeloid cells.**
- **Reproducibility R: p = 0.47** — not significant here. This dataset has only **2
  biological replicates** (~45 cells/perturbation/replicate), so cross-replicate coherence is
  noise-dominated and underpowered — a *data* limitation, not a biology failure.
- This is the **mirror image of Norman K562** (non-immune differentiation), where the signal was
  carried by R (p=0.0009) and **not** S (p=0.17). Myeloid: **S yes, R no**. Non-immune differentiation:
  **R yes, S no**. The axis-selective component S tracks *immune* identity, not T-cell identity.

## Honest reading (pre-registered interpretation)
The pre-registration stated: PASS ⇒ immune-wide; FAIL ⇒ T-cell-scoped. The outcome is **neither a
clean PASS nor a clean FAIL**: the immune-specific axis-specificity signal is present and
significant in a non-T immune lineage (S p<1e-4, direction-correct, AUPRC nearly doubles, orthogonal
to magnitude), which **leans toward immune-wide scope**; but the combined `C` fails the strict CI
bar because its reproducibility component is underpowered at 2 replicates. The disciplined
conclusion: **the boundary is more likely immune-wide than T-cell-specific for the S component**,
pending a myeloid screen with more replicates to power R. A discordant/near result is a hypothesis,
not an error.

## What would settle it
A non-T immune Perturb-seq with ≥3–4 replicates (to power R), or the KO (Cas9) arm of the same study
as an independent modality (GSM6858447), or a DC/NK screen. Registered as the next B1 extension.

## Provenance
GSE221321 (Yao et al., *Nat Biotechnol* 2023) · GSM6858449 KD/CRISPRi conventional arm ·
66283 cells × 18017 genes · replicates
['Run_1', 'Run_2'] · axis = LPS/NF-κB inflammatory response · locked `kernel.py` helpers ·
CPU · seed 0 · zero-shot to our labels.
