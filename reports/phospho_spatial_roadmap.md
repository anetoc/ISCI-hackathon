# Validation roadmap — phospho-signaling and spatial (future work, not executed here)

**Status: documented roadmap.** These are the two orthogonal validation layers
we did NOT execute for the submission, with the honest reason and the concrete plan.

## 1. Phospho-signaling validation (the natural test for the TCR reframe)

Our controllers are inferred from the **transcriptome**; TCR signal strength is a
**phosphorylation** event. If the TCR-rheostat reframe is right, the decisive
orthogonal validation is phospho, not RNA.

**Plan:**
- Mine a public CAR-T / TCR phosphoproteomics dataset (e.g. SILAC LC-MS/MS of
  CD19-CAR signaling; ProteomeXchange/PRIDE). Gate: comparable genes/conditions.
- Test whether our TCR-axis controllers (PLCG1, LAT, LCP2, VAV1, ZAP70, LCK)
  enrich in differential phosphorylation events — a protein-level confirmation
  that they are real signaling controllers, not transcriptional artifacts.
- Read-outs: pLCK, pZAP70, pLAT, pPLCγ1, pERK, pS6, pNF-κB p65.

**Why not now:** requires finding a phospho dataset with mappable
genes/conditions; the transcriptomic core stands on its own. High-value,
medium-feasibility — first post-submission target.

## 2. Spatial transcriptomics (mechanism localization, NOT prediction)

Spatial is about **tissue architecture / TME niche**; our data is dissociated
CD4+ perturbation. So spatial is not a clinical-prediction validation — it is a
question of *where in the tissue* the ISCI/T-REMAP modules localize.

**Plan (IDOR tissue or public DLBCL/MM Visium/Xenium/CosMx/GeoMx):**
- Score each spot/cell for the 6 modules.
- Distance-to-niche: proximity of R_killing/R_migration to the tumor–T interface;
  proximity of NR_Treg/NR_exhaustion/toxicity to suppressive (macrophage-rich,
  Treg-rich) niches.
- Ligand–receptor: PDCD1–CD274, TIGIT–PVR, CTLA4–CD80/86, CXCL9/10–CXCR3, TGFB, IL10.
- Three target figures: (1) sensitivity niche near tumor interface; (2) resistance
  niche in suppressive microenvironments; (3) controller localization co-mapping
  with the module it drives.

**Why not now:** no clean public dataset that matches our compartment, and IDOR
tissue is post-hackathon. The literature gap is real — few studies connect
*perturbational controllers* to *spatial resistance niches* — which makes this a
strong IDOR-led future direction rather than a rushed public scout.

## Compartment hypothesis these layers test

Both layers serve the central hypothesis emerging from the external validation:
**sensitivity is product/protein-visible; resistance emerges post-infusion, in
time and in the tissue niche.** Phospho tests the product/signaling side; spatial
tests the niche side.
