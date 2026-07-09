# RNA ↔ protein cross-layer controller check (multiomic architecture, first exercise)

**Result: the controllership operator runs on the CITE protein layer, RNA-called controllers concord
at the protein level, and the signal is strongest in each axis's *native* layer.** This is the first
concrete exercise of the `integration_architecture.md` thesis — on data already on disk, CPU only,
zero new large downloads. It is a **cross-layer concordance / native-layer confirmation**, NOT a new
magnitude-conditional CCI PASS (see honesty note §4).

---

## 1. Design

Same controllership logic, protein substrate (CLR-normalized ADT). Two complementary cases:

- **Frangieh** (RNA EVALUABLE, near-miss): build the protein immune-evasion axis the same way as RNA
  (IFNγ − Control in control cells, over the 24-ADT panel, isotypes dropped); per perturbation score
  the surface MHC-I/PD-L1 shift ({HLA_A, HLA_E, CD274}) and protein axis-specificity S_prot; then test
  (a) protein-layer recovery of the canonical IFN/antigen-presentation positives and (b) cross-layer
  concordance with the RNA scores (`frangieh_perturbcite_scores.csv`).
- **Papalexi** (RNA NOT-EVALUABLE — no baseline, circular axis): its native readout is **surface PD-L1
  protein**; test whether the protein layer recovers PD-L1 regulators (native-layer rescue).

## 2. Frangieh — RNA ↔ protein concordance (n=238 joined targets, 13 canonical positives)

| test | value |
|---|---|
| protein recovery of positives via surface MHC-I/PD-L1 shift | **AUROC 0.90, AUPRC 0.76** |
| positives vs negatives surface-shift (MW p) | **1.2 × 10⁻⁶** |
| positives median surface shift / negatives median | **−0.27 / +0.01** (positives lose surface MHC-I) |
| cross-layer concordance Spearman(S_rna, S_prot) | **+0.24** |
| top-5 protein controllers (|surface shift|) | **STAT1, CD274, B2M, IFNGR2, IFNGR1** |

The RNA-identified controllers produce the expected **protein** phenotype (loss of surface MHC-I /
PD-L1), the RNA and protein axis-specificities are positively concordant, and the top protein
controllers are exactly the canonical IFN/antigen-presentation machinery (B2M and STAT1/IFNGR are the
core MHC-I regulators). **The evasion axis is far cleaner in its native protein layer (AUROC 0.90) than
in RNA (near-miss +0.118)** — consistent with the architecture's claim that killing/evasion is a
protein phenotype. (Protein *axis-specificity* S_prot alone recovers weakly, AUROC 0.59 — the 24-marker
panel is too coarse for a cosine-specificity; the direct surface-shift readout is the informative one.)

## 3. Papalexi — native-layer rescue (n=25 targets, 15 canonical PD-L1 regulators)

| test | value |
|---|---|
| PD-L1 protein recovery of PD-L1 regulators | **AUROC 0.77, AUPRC 0.87** |
| positives vs negatives PD-L1 shift (MW p) | **0.025** |
| top-5 PD-L1 reducers | **JAK2, IFNGR2, IFNGR1, STAT1, CMTM6** |

RNA was NOT-EVALUABLE here (all cells IFN-treated → the only RNA axis is circular with the IFN-regulator
labels). Moving to the **native protein readout (surface PD-L1)** makes the same question cleanly
answerable: the known PD-L1 regulators reduce surface PD-L1, recovered at AUROC 0.77 — and the top hits
include **CMTM6**, the canonical PD-L1 protein stabilizer that is invisible to a purely transcriptional
axis. This is a direct demonstration of the "each axis has a native layer" principle: the layer, not
just the dataset, determines evaluability.

## 4. Honesty note (what this is / is not)

- **Is:** (i) proof the controllership operator is layer-agnostic (same recipe, protein substrate);
  (ii) cross-layer concordance — RNA-called controllers act at the protein level and rank top;
  (iii) native-layer confirmation — the evasion/PD-L1 axis is strongest where the biology lives.
- **Is NOT:** a new magnitude-conditional CCI PASS. These are **recovery** tests (AUROC of a functional
  protein readout for known regulators), not the full matched-negative + conditional-LR + bootstrap
  ΔAUPRC test. The protein recovery is partly *expected* biology (IFN-pathway KOs reduce IFN-induced
  surface proteins) — that is the point of a **confirmation**, not a discovery. The load-bearing new
  content is the **concordance** (ρ=0.24; top controllers shared) and the **native-layer rescue** of an
  otherwise not-evaluable dataset, not the magnitude of the AUROC.
- **Caveat:** cross-layer S_rna↔S_prot concordance is modest (0.24) and the protein panels are small
  (24 / 4 markers). A full cross-layer *CCI* (magnitude-matched negatives at the protein level, and the
  ≥2-layer concordance gate from `integration_architecture.md` §2.6) is the pre-registered next step;
  this is the feasibility-and-direction pass that shows it is worth building.

## 5. Architectural takeaway

The multiomic contract works: one operator, two layers, no kernel changes. The strongest immune-evasion
controllership signal in Frangieh lives in the **protein** layer (0.90), not RNA (near-miss); Papalexi is
**rescued** from NOT-EVALUABLE by its native PD-L1 readout. This motivates the `integration_architecture.md`
plan — per-layer CCI + late-fusion cross-layer concordance — and identifies the cheapest high-value
build: formalize a `cite_protein` adapter + the ≥2-layer concordance gate.

### Deliverables
- `cross_layer_report.md` (this file) · `cross_layer_result.json` · `frangieh_crosslayer_scores.csv`
  (per-target RNA+protein scores) · `papalexi_protein_scores.csv` · `cross_layer.py` (reproducible, CPU).
