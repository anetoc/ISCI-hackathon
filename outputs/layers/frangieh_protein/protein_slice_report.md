# Brief 06 (Layer 1) — Frangieh protein controllership slice (totalVI, CPU)

**VERDICT: FAIL** for magnitude-conditional protein controllership — and the reason is itself the
finding: at the protein layer, the immune-evasion regulators' coherence is **fully explained by
effect magnitude** (zero magnitude-independent residual), so the CCI signal that exists in RNA does
**not** reproduce in the protein residual. The magnitude-independent controllership signal is an
RNA / cross-donor property; it collapses into magnitude at the protein layer (with this coarse
24-marker panel). Protein regulator identity is captured by **direct readout / magnitude**
(cross-layer surface-shift AUROC 0.90, `cross_layer_report.md`), not by a magnitude-conditional
residual. **The tensor slice is registered as FAIL**, honestly.

> ⚠️ Anti-overclaim note. The locked operator's `bootstrap_auprc_gain` first returned **ΔAUPRC
> +0.584 [0.26, 0.78]** and the naive verdict was "PASS". That gain is **direction-agnostic** (the
> logistic fit learns the sign of C_prot). Inspection showed positives have **lower** residual
> C_prot (median 0.059) than non-regulators (0.565) — the signal is **inverted** vs RNA/Marson,
> where controllers have *higher* residual coherence. A high AUPRC gain from an inverted feature is
> not a controllership PASS. The verdict logic was corrected to be **direction-aware** (a PASS
> requires positives higher on C). This is exactly the magnitude-trap-in-new-clothing the project
> exists to avoid; catching it is the point.

---

## Compute provenance
CPU only (`accelerator="cpu"`, `CUDA_VISIBLE_DEVICES=""` — the installed torch is a cu130 build and
the driver is 12.6, so CUDA is hidden; the RTX 6000's other users were untouched). totalVI on
**87,965 cells** (stratified subsample, cap 400/perturbation), RNA 4000 HVGs + 24 ADT, 200 epochs.
Step 0 GATE passed: RNA and protein share all 218,331 barcodes (true CITE-seq pairing).

## What was computed (locked operator, protein substrate)
- **Denoised protein** from totalVI (`get_normalized_expression`, n_samples=25) — never re-derived
  from RNA (independence guard).
- Per perturbation: **S_prot** (|cos| of protein effect with the IFNγ−Control leave-marker axis),
  **R_prot** (reproducibility across the 3 conditions), **M_prot** (protein effect magnitude);
  S_prot/R_prot residualized on M_prot → **C_prot**.
- Positives = canonical IFN/antigen-presentation regulators (8 detectable: HLA-B, IFNGR1, IFNGR2,
  IRF3, JAK1, JAK2, STAT1, TAPBP); 23 expression/power-matched negatives (locked helper).

## Result

| quantity | value | reading |
|---|---|---|
| ΔAUPRC (direction-agnostic) | +0.584 [0.26, 0.78] | large gain, but **inverted direction** |
| C_prot: positives vs negatives (median) | **0.059 vs 0.565** | positives are LOW-residual — inverted |
| direction | **INVERTED (positives lower)** | not a controllership PASS |
| Spearman(C_prot, magnitude) | 0.16 | residual is ~magnitude-orthogonal by construction |
| raw S_prot (positives) | ~0.94 (near ceiling) | protein effect is highly axis-specific... |
| ...but residual after magnitude | ~0 | ...because it is fully explained by magnitude |
| **controllership verdict** | **FAIL** | magnitude-conditional protein signal not supported |

## Incremental over RNA
Spearman(C_prot, C_rna) = **−0.32** and the LR "adds" only in the inverted direction — so protein
does **not** add a *positive* controllership layer over RNA. `adds_over_rna = False`.

## Why (mechanism of the negative)
The IFN/APM regulators produce **large, ceiling-level, highly-coherent** protein effects (KO of
B2M/JAK/STAT1/IFNGR collapses the whole surface MHC-I/PD-L1 program). On a **24-marker** panel, that
makes S_prot and R_prot saturate for exactly the high-magnitude positives, so residualizing against
magnitude leaves them with ~zero residual — while small-effect non-regulators retain noisy residual
coherence. The feature space is too coarse, and the effects too magnitude-dominated, for a
magnitude-*independent* residual to separate controllers in the positive direction.

## Honest takeaway (this is a real, useful negative)
- The **magnitude-independent controllership signal is not universal across layers**: it is an
  RNA / cross-donor-reproducibility property. At the protein layer here, regulator identity is
  magnitude / direct-readout, not a conditional residual. This *sharpens* the claim rather than
  weakening it — and it is consistent with the three-coherence result (Sₚ≈magnitude): coherence
  measured on a coarse/high-magnitude substrate tends to collapse onto magnitude.
- Scope caveat (already in the paper): Frangieh perturbs **melanoma** cells (evasion axis), not T-cell
  state — the protein layer here is tumor immune-evasion, a different axis from persistence/killing.
- The tensor gains an honest **PROTEIN FAIL** slice — the layer was tested, not assumed, and reported
  straight (like PageRank and the clinical null before it).

### Deliverables
- `protein_slice_report.md` (this file) · `protein_cci_result.json` (contract fields + direction +
  corrected verdict + the direction-agnostic auto value, for audit) · `protein_scores.csv` (per-gene
  S_prot/R_prot/resid/C_prot joined to C_rna) · `totalvi_model/` (saved) · `brief06.py` (reproducible,
  CPU, direction-aware verdict).
