# A magnitude-conditional controllability signal defines an immune-scoped property of T-cell state, decomposes into a multi-axis engagement capacity, and returns an honest null against CAR-T clinical response

**Running title:** Conditional controllability of T-cell state

**Authors:** Abel Costa¹ · with an autonomous analysis agent (Claude Science)

¹ Instituto D'Or de Pesquisa e Ensino (IDOR), Rio de Janeiro, Brazil — hematology / onco-hematology

**Correspondence:** anetoc@users.noreply.github.com

**Preprint / code:** https://github.com/anetoc/ISCI-hackathon (reproduce with `make reproduce-core`)

---

## Abstract

**Background.** Genome-scale perturbation of primary human T cells now makes it possible to ask not
merely which genes *move* cell state, but which genes *control* it. The obstacle is that hit-calling
in perturbation screens is dominated by effect magnitude: a gene that shifts many transcripts is
easy to call a regulator, whether or not it controls a specific state axis. No agreed operational
definition separates a controller from a large, diffuse disturbance.

**Methods.** Using a genome-scale Perturb-seq atlas in primary human CD4+ T cells (33,983
perturbation × condition profiles, 10,282 genes), we define controllership *conditional on
magnitude*: within perturbations of matched effect size, we score axis-specificity (how
concentrated a perturbation's effect is on a defined state axis) and cross-donor coherence (how
reproducible that effect is across donors), residualize both against magnitude, and combine them
into `ISCI_orthogonal`. We benchmark regulator recovery against a trivial effect-magnitude baseline
using **expression/power-matched negatives**, bootstrap the gain, and test the property on four
independent perturbation systems. We then decompose the immune-engagement phenotype into candidate
axes (Immune Engagement Capacity, IEC) at single-cell pseudobulk resolution, and test whether any
axis predicts CAR-T clinical response on a >1-million-cell, 87-patient atlas under honest
leave-one-study-out cross-validation.

**Results.** The magnitude-conditional signal nearly **doubles regulator recovery** within the
detectable set (AUPRC 0.722 vs 0.415 for magnitude), is orthogonal to magnitude by construction
(Spearman ρ = +0.02), and the bootstrap gain is **+0.229 AUPRC (95% CI [0.072, 0.405], P>0 =
99.6%)**. It survives leakage controls, replicates on independent structural positives, and
replicates across all three culture conditions. Tested across four perturbation systems the
property is **immune-scoped**: it holds in the Marson CD4+ anchor (PASS), shows the same directional
signal under an opposite modality (CRISPRa; underpowered near-miss), and fails in two non-immune
screens (K562, RPE1). Decomposing the phenotype, **persistence is a clean axis** while killing and
resistance stay partly entangled (≈2.5 separable axes). **No IEC axis predicts CAR-T response**
under leave-one-study-out CV: the best axis collapses from patient-out AUROC 0.643 to study-out
0.533 (CI includes 0.5), and a trivial CD8-fraction baseline beats every axis — the patient-level
signal was per-study batch structure, not transportable biology.

**Conclusions.** A magnitude-deconfounded controllability signal is a real, falsifiable,
immune-scoped property of T-cell state, distinct from effect size and from network topology. It
decomposes into a measurable multi-axis engagement capacity but is *not*, at current power, a CAR-T
response biomarker. We report the clinical result as a well-powered negative rather than an
un-transportable positive.

**Keywords:** Perturb-seq · T-cell state · controllability · CAR-T · exhaustion · persistence ·
cross-study validation · effect-magnitude confound

---

## 1. Introduction

Chimeric antigen receptor (CAR) T-cell therapy and T-cell engagers have transformed the treatment
of B-cell malignancies, yet a substantial fraction of patients relapse, and the determinants of
durable response remain incompletely predictable from the infused product. A central hypothesis is
that response is governed by the *state* of the T cells — their position along axes of stem-like
persistence, cytotoxic function, and exhaustion/resistance — and that the genes controlling
movement along these axes are the levers for engineering better products. Realizing this hypothesis
requires two things the field has only recently acquired: the ability to perturb T-cell state at
genome scale, and a principled way to tell a *controller* of state from a gene that merely
correlates with it.

The first is now in hand. Functional CRISPR screens dissected the gene networks controlling human
T-cell proliferation and regulatory identity ([Schmidt 2020](https://doi.org/10.1038/s41590-020-0784-4);
[Cortez 2020](https://doi.org/10.1038/s41586-020-2246-4)); pairing CRISPR activation and
interference with single-cell readouts decoded stimulation-responsive circuits, showing that
control is context-dependent ([Schmidt 2022](https://doi.org/10.1126/science.abj4008)); and the
field has since moved to dynamic circuit control of T-cell rest and activation
([Freitas 2024](https://doi.org/10.1038/s41586-024-08314-y)). The biology of the target axes is
equally well established: exhaustion is an epigenetically enforced differentiation state with
dedicated master regulators such as TOX ([Khan 2019](https://doi.org/10.1038/s41586-019-1325-x)),
and persistence can be engineered by rebalancing transcription-factor programs
([Chen 2026](https://doi.org/10.1126/sciimmunol.adw7685)).

The second — a definition of controllership — is where this work contributes. The dominant failure
mode of perturbation hit-calling is that it is confounded by effect magnitude. In our data, known
T-cell regulators produce differential-expression effects roughly two orders of magnitude larger
than non-regulators (Mann–Whitney p = 2.6 × 10⁻¹⁰). Any score that correlates with effect size will
therefore "recover regulators" for a trivial reason, and will do so *by construction*. The
network-inference community offers one principled alternative — infer a gene regulatory network and
apply control-theoretic driver-selection, as in CEFCON
([Wang 2023](https://doi.org/10.1038/s41467-023-44103-3)) — but this inherits the fragility of GRN
inference. Foundation models such as GEARS ([Roohani 2024](https://doi.org/10.1038/s41587-023-01905-6))
and scGPT ([Cui 2024](https://doi.org/10.1038/s41592-024-02201-0)) predict *what a perturbation
does*, a different question than *whether a gene controls an axis independent of how much it does*.

We take a third path. We define controllership **conditional on magnitude**: among perturbations of
matched effect size, which produce effects that are *axis-specific* and *cross-donor reproducible*?
We show this signal is orthogonal to magnitude yet nearly doubles regulator recovery; that it
behaves as a falsifiable, immune-scoped property across four perturbation systems; that the
immune-engagement phenotype it scores decomposes into a measurable multi-axis capacity; and — the
result we most want to be believed because it is negative — that no axis of that capacity predicts
CAR-T clinical response once validation honestly crosses studies. Throughout, the analysis was
executed by an autonomous agent that repeatedly caught and corrected its own leakage and overclaims;
we treat that adversarial self-auditing as part of the method, not a footnote.

---

## 2. Methods

### 2.1 Data

The primary substrate is a genome-scale Perturb-seq atlas of primary human CD4+ T cells (Marson
laboratory; CZI-hosted). We use the differential-expression summary object (`DE_stats.h5ad`; shape
33,983 perturbation × condition profiles × 10,282 genes), which provides per-perturbation effect
layers (log fold-change, z-score, effect magnitude as number of differentially expressed genes) in
three culture conditions (Rest, Stim 8 h, Stim 48 h), together with donor-level correlation
statistics. Effect magnitude is defined per perturbation as the number of differentially expressed
genes (n-DE). For the external tests we use three additional perturbation systems: a CD4+ T-cell
CRISPRa screen (Schmidt GSE190604), a K562 CRISPRa differentiation screen (Norman/Weissman), and an
RPE1 essential-gene CRISPRi screen (Replogle). For the clinical test we use the Functional CAR-T
atlas (ML4BM-Lab / University of Navarra; Zenodo record 19066393; 455,370 CD3⁺CAR⁺ cells × 48,740
genes; 119 patients, 87 with response labels).

### 2.2 Conditional Controllability Invariant (CCI)

For each perturbation *g* and state axis *a* we compute two per-perturbation quantities:

- **Axis-specificity** S(g,a): the concentration of *g*'s transcriptional effect on the genes
  defining axis *a*, relative to its total effect (an enrichment/NES-style projection restricted to
  axis genes).
- **Cross-donor coherence** R(g): the reproducibility of *g*'s effect direction across donors.

Both are **residualized against effect magnitude** (regress out n-DE; keep the residual percentile),
yielding magnitude-orthogonal components. The primary score is

> `ISCI_orthogonal(g) = mean( residualized-percentile(S), residualized-percentile(R) )`,

evaluated only on perturbations with a **detectable effect** (n-DE ≥ dataset median), because
specificity and coherence are undefined for perturbations with no measurable effect. This
eligibility gate is pre-registered, not tuned.

### 2.3 Benchmark: expression-matched negatives

The single most important methodological choice is the negative set. Because known regulators are
high-magnitude, an unmatched positives-vs-rest comparison re-discovers magnitude. We therefore draw
negatives that are **expression/power-matched** to the positives on `n_cells_target` (and
`target_baseMean` where available) via a locked helper, typically 8 matched negatives per positive.
Regulator recovery is quantified as AUPRC of `ISCI_orthogonal` versus the DE-magnitude baseline on
the identical matched split. The AUPRC gain is bootstrapped (1,000 resamples) to a 95% CI and a
P(gain>0). Robustness controls: (i) leakage control — remove axis-marker genes from the positive set
and re-test; (ii) independent structural positives (ARID1A, INO80, IKZF1) not used to define axes;
(iii) replication across all three culture conditions.

### 2.4 Falsifiability across systems

The CCI is stated as a falsifiable, immune-scoped property: it should hold in immune perturbation
systems and fail in non-immune ones. Each dataset in a registry (`config/datasets.yaml`) carries a
**pre-registered expected verdict** keyed on its system label (immune vs non-immune). The same
magnitude-conditional test and matched-negative benchmark are applied to each; a PASS requires a
positive bootstrap gain with a lower CI above zero and a significant conditional likelihood-ratio
test.

### 2.5 Immune Engagement Capacity (IEC) axes

We define three candidate axes from curated marker gene sets — persistence (e.g. TCF7, SELL, IL7R,
CCR7, LEF1, BACH2, KLF2, FOXO1), killing (GZMB, PRF1, NKG7, GNLY, IFNG, FASLG), and
resistance/exhaustion (PDCD1, HAVCR2, LAG3, TIGIT, ENTPD1, BATF) — and score each per perturbation
at pseudobulk. Axis orthogonality is measured by pairwise Spearman correlation of axis scores across
perturbations in each condition. A functional-killing proxy (BEHAV3D organoid TEG co-culture) tests
whether a persistence-loaded latent factor also captures killing.

### 2.6 Mechanism decomposition

Two magnitude-guarded analyses probe mechanism without overclaiming. (i) **Curated-set enrichment:**
six pre-registered narrow T-cell gene sets are tested by rank-based Mann–Whitney along the
*continuous* `ISCI_orthogonal` score over all 2,520 detectable genes, with BH-FDR correction, and
each is re-tested against magnitude as a guard. (ii) **Signed perturbation→module graph:** for each
perturbation we compute the signed effect on each of six functional modules (Stim 48 h z-score
layer), and define a *therapeutic convergence* score as coherent movement in the clinically
desirable direction (R-modules up, NR-/toxicity-modules down). Convergence is correlated against
both `ISCI_orthogonal` and magnitude to establish independence.

### 2.7 Clinical test (leave-one-study-out)

On the CAR-T atlas we score each patient's infusion-product cells on each IEC axis (mean and
fraction-high summaries) and ask whether any axis predicts response (CR/PR vs NR). The decisive test
is **leave-one-study-out** cross-validation (train on all studies but one, predict the held-out
study), contrasted with the optimistic **leave-one-patient-out** CV. Significance is assessed by a
label-permutation null; a CD8-fraction compositional baseline is evaluated on the identical splits.
The clinical-null criterion is pre-registered: if the leave-study-out CI includes 0.5 and the
permutation p > 0.05, IEC is declared a descriptive capacity, not a response biomarker.

### 2.8 Reproducibility and provenance

Every output carries a provenance stamp (data SHA-256, conda environment, git SHA, random seed). The
validated method runs from one command (`make reproduce-core`) over the dataset registry. The
original five-component index (M·R·D·A·S) that lost to magnitude is **deprecated in place** and
retained only for provenance. All results and figures are reproduced from committed rankings and a
locked analysis skill.

---

## 3. Results

### 3.1 A magnitude-conditional signal nearly doubles regulator recovery

The framing problem is real and quantifiable: known regulators have roughly two orders of magnitude
more transcriptional effect than non-regulators (Mann–Whitney p = 2.6 × 10⁻¹⁰), so a magnitude
score recovers regulators trivially. When we control for this by drawing expression-matched
negatives, the original five-component index **loses** to the magnitude baseline (AUPRC 0.35 vs
0.41) — an honest negative that reset the project.

Conditioning on magnitude reverses the picture. Within the detectable set, `ISCI_orthogonal` —
built only from magnitude-residualized axis-specificity and cross-donor coherence — recovers
regulators at **AUPRC 0.722 versus 0.415 for magnitude**, while being orthogonal to magnitude by
construction (Spearman ρ = +0.02). The bootstrap gain is **+0.229 AUPRC (95% CI [0.072, 0.405],
P(gain>0) = 99.6%)**. Conditional likelihood-ratio tests confirm that both components add
information for regulator status *beyond* magnitude (axis-specificity coefficient +1.59, coherence
+1.17, both p < 10⁻⁴). The signal survives a leakage control (removing axis-marker regulators),
replicates on independent structural positives (ARID1A, INO80, IKZF1), and replicates across all
three culture conditions. The top-ranked candidates recover known regulators as a sanity check
(IRF1 #1, STAT6 #8, SETDB1 #11, GATA3 #14) and nominate candidates outside the label set (IKBKB,
BCLAF1, TFAP4, ZC3H12A/Regnase-1, RCOR1); we frame these as *candidate state-shift controllers under
a magnitude-controlled criterion*, not as validated therapeutic targets.

### 3.2 The property is immune-scoped and falsifiable

A signal that merely fit the anchor would not be a property. We therefore stated the CCI as a
falsifiable prediction — hold in immune systems, fail in non-immune ones — and tested four
perturbation systems with pre-registered expected verdicts (Figure 1).

![Figure 1. Four-system CCI scope. The magnitude-conditional controllability gain (ΔAUPRC, M→M+C) with 95% CIs across four perturbation systems: Marson CD4+ T (PASS), Schmidt CD4+ CRISPRa (directional near-miss), Norman K562 (non-immune, FAIL near-miss), Replogle RPE1 (non-immune, robust FAIL). The property holds in immune systems and fails in non-immune ones, demarcating a boundary rather than a universal claim.](../figures/cci_scope_4systems.png)

The Marson CD4+ anchor passes (ΔAUPRC +0.229 [0.072, 0.405]); the Schmidt CD4+ CRISPRa screen shows
the same directional signal under an opposite perturbation modality but is underpowered (+0.138
[−0.029, 0.434], n_pos = 10); and the two non-immune screens fail — K562 differentiation as a
near-miss whose residual signal comes from cross-guide reproducibility rather than axis-specificity
(+0.138, LR p = 0.013), and RPE1 proliferation as a robust FAIL (+0.060 [−0.013, 0.204], stable
across four variants). The ordering matches the pre-stated prediction: immune PASS > non-immune
differentiation near-miss > non-immune proliferation FAIL. The property is **immune-scoped** — a
demarcated boundary, not a universal law.

### 3.3 The phenotype decomposes into ~2.5 axes

If immune engagement is a capacity, its axes should be partly separable. At pseudobulk, persistence
is a **clean axis** (|ρ| < 0.08 with the other axes), but killing and resistance remain **entangled**
(ρ ≈ −0.45): about **2.5 separable axes, not 3** (Figure 2). We report the half rather than rounding
up. A BEHAV3D functional-killing proxy agrees that killing is its own axis — a persistence-loaded
latent factor loads ≈0 on functional killing — so the entanglement is a real feature of the
transcriptional readout, not an artifact of gene-set overlap.

![Figure 2. IEC axis orthogonality at pseudobulk. Pairwise correlation of persistence, killing, and resistance axis scores across perturbations (Stim 48 h). Persistence is orthogonal to both other axes (|ρ|<0.08) while killing and resistance are entangled (ρ≈−0.45), yielding ~2.5 separable axes.](../figures/iec_axis_orthogonality_pseudobulk.png)

### 3.4 Mechanism separates from magnitude

Broad GO/Reactome family membership among top hits does not survive FDR — an honest negative.
However, *narrow curated* T-cell gene sets tested rank-based along the continuous score, with a
magnitude guard, do (Figure 3). Four of six sets survive BH-FDR, and the guard is the informative
part: **NF-κB activation** (ISCI q = 0.017) and **Treg-brake/apoptosis** (q = 0.008) are enriched in
controllership but **not in magnitude** (magnitude Mann–Whitney p = 0.35 and 0.39) — the clean,
magnitude-independent finding. TCR-proximal phosphorylation and chromatin modifiers enrich in both
(TCR is the expected high-effect rheostat / positive control), and cytoskeleton/RNA-decay sets are
high-effect but not axis-specific. This is a mechanistic prioritization, not a claim of causal
family membership.

![Figure 3. Curated-set enrichment separates controllership from magnitude. Six pre-registered T-cell gene sets scored along the continuous ISCI_orthogonal (rank-based MWU, BH-FDR) versus a magnitude guard. NF-κB and Treg-brake sets enrich in controllership but not in magnitude (magnitude-independent controllers); TCR-proximal enriches in both (high-effect positive control).](../figures/curated_enrichment.png)

A signed perturbation→module graph replaces PPI centrality — which added nothing over magnitude —
with causal perturbation edges (Figure 4). Therapeutic convergence (coherent movement in the
desirable direction) is a **third, independent axis**: Spearman +0.24 versus controllership, +0.18
versus magnitude. The sharpest read is that the #1 controller **IRF1 has negative convergence
(−0.21)** — a strong, reproducible controller whose net effect runs *against* the therapeutic
direction. Controllership and therapeutic desirability are distinct, which is exactly why a naive
"top controller = target" reading is wrong.

![Figure 4. Signed perturbation→module graph. Each perturbation's signed effect on six functional modules; therapeutic convergence (desirable-direction movement) is independent of both controllership and magnitude. The top controller IRF1 points against the therapeutic direction.](../figures/signed_perturbation_graph.png)

The 70 top controllers are sorted into a safety-first decision board (A manufacturing modulation, 24;
B engineering candidates, 6; C probe-only, 18; D dangerous rheostats, 22). The overclaim guard is
structural: the two most drug-like genes, IKBKB and PRKDC, land in Category D (dangerous), so the
default reading is the safe one.

### 3.5 An honest clinical null

Finally, the translation test. Does any IEC axis predict CAR-T response at patient-level power? On
the Functional CAR-T atlas (87 response-labeled patients across 9 studies, 5 with both classes,
>1M cells), the answer is **no** (Figure 5). The best axis (persistence, mean summary) reaches
leave-one-patient-out AUROC 0.643 (permutation p = 0.006) but **collapses to leave-one-study-out
AUROC 0.533 [0.408, 0.650], permutation p = 0.14** — the CI includes 0.5. Every axis behaves the
same way, and a trivial **CD8-fraction compositional baseline (study-out AUROC 0.585) beats every
IEC axis**. The null replicates in an NHL-only stratum (n = 77) and an infusion-product-only subset
(n = 73).

![Figure 5. Well-powered clinical null. IEC axes do not predict CAR-T response under leave-one-study-out cross-validation. The persistence axis' apparent patient-out signal (0.643) collapses to chance across studies (0.533, CI includes 0.5); a CD8-fraction baseline outperforms every axis. The patient-level signal was per-study batch structure, not transportable biology.](../outputs/iec_clinical/iec_prediction.png)

The interpretation is unambiguous: the patient-out signal was **per-study batch structure, not
transportable biology**. Per the pre-registered criterion, IEC is a descriptive multi-axis capacity,
**not** a CAR-T response biomarker. This bounds the clinical claim and does not touch the locked CCI
core, which is a statement about perturbation biology, not patient outcome.

---

## 4. Discussion

We set out to separate genes that *control* T-cell state from genes that merely *move* it, and to do
so without smuggling effect magnitude back in through the ground truth. The central result is that a
magnitude-conditional signal — axis-specificity and cross-donor coherence, each residualized against
effect size — carries real, orthogonal information about regulator status, nearly doubling recovery
within the detectable set. The result is not that our score beats magnitude globally; it is the more
defensible conditional statement that, *among perturbations of matched effect size*, specificity and
reproducibility add signal. This distinction matters because it is what makes the claim
non-circular.

Three features distinguish this from neighboring approaches. First, unlike network-control methods
that derive driver nodes from an *inferred* GRN ([Wang 2023](https://doi.org/10.1038/s41467-023-44103-3)),
our controllership is read directly from *observed causal perturbation effects*, avoiding the
fragility of topology inference; our own negative control — structural centrality adds nothing over
magnitude — is a caution that inferred influence can be magnitude-confounded. Second, unlike
perturbation-prediction foundation models ([Roohani 2024](https://doi.org/10.1038/s41587-023-01905-6);
[Cui 2024](https://doi.org/10.1038/s41592-024-02201-0)) that predict what a perturbation does, we
ask whether a gene controls an axis independent of how much it does; we scope foundation-model
concordance as an *independent* triangulation with matched negatives, never as fine-tuning on our own
labels. Third, the property is stated to be **falsifiable** and is falsified where it should be: it
fails in non-immune systems, demarcating an immune-scoped boundary rather than a universal law.

The clinical null deserves emphasis because it is the result most vulnerable to motivated reasoning.
A leave-one-patient-out analysis would have handed us a "significant" persistence predictor
(AUROC 0.643, p = 0.006). Reporting that would have been wrong: the signal evaporates the moment
validation crosses studies, and a compositional CD8-fraction baseline outperforms it. This is the
recurring lesson of cross-study genomics — single-cohort predictors frequently encode batch
structure — and the honest posture is to report the well-powered negative. It bounds the
translational claim precisely: IEC is a measurable capacity worth characterizing, not a biomarker
ready for the clinic. For a hematologist, that boundary is the useful output: it says where the
transcriptional-state hypothesis does and does not currently pay off, and it points at
composition and cross-study design as the real obstacles.

Biologically, the decomposition into ~2.5 axes — persistence clean, killing and resistance entangled
— is consistent with exhaustion being a dedicated, epigenetically enforced program
([Khan 2019](https://doi.org/10.1038/s41586-019-1325-x)) rather than a simple loss of cytotoxicity,
and with persistence being a separable, engineerable axis
([Chen 2026](https://doi.org/10.1126/sciimmunol.adw7685)). The magnitude-independent enrichment of
NF-κB and Treg-brake mechanisms, and the finding that the top controller IRF1 points *against* the
therapeutic direction, together argue that controllership is a property of the regulatory wiring,
not a proxy for either effect size or clinical desirability.

### 4.1 Limitations

Positives are few (12–21 depending on set); the signal is bootstrap-stabilized and
cross-condition-replicated, but a fully independent external positive set remains future work. The
axes are defined from curated marker sets and are therefore only as good as those sets; the
foundation-model triangulation (scGPT gene-embedding concordance) and cell-level scVI confirmation
of the 2.5-axis structure are scoped but not yet executed. The clinical atlas, though large in cells,
has 87 labeled patients across 9 studies — well-powered for a leave-study-out null but not for
discovering a small transportable effect if one exists. The mechanism analyses are hypothesis-
generating prioritizations, not causal claims, and the decision board carries no therapeutic
recommendation. Finally, the CCI is demonstrated in CD4+ T cells; extension to CD8+ effector and
exhaustion trajectories is a natural next step.

### 4.2 Conclusion

A magnitude-deconfounded controllability signal is a real, falsifiable, immune-scoped property of
T-cell state — distinct from effect magnitude and from network topology, and reproducible across
donors, conditions, and independent positive sets. It decomposes into a measurable multi-axis
engagement capacity but is not, at current power, a CAR-T response biomarker. The most useful thing
this work does may be to draw that line honestly: it says which part of the state-controls-response
hypothesis is presently supported (controllership as perturbation biology) and which is not
(transcriptional-state prediction of clinical response across studies), and it hands the field a
one-command-reproducible, provenance-stamped test rather than a claim to be taken on trust.

---

## Data and code availability

All code, locked results, figures, and this manuscript are at
https://github.com/anetoc/ISCI-hackathon (reproduce with `make reproduce-core`). Primary data:
genome-scale CD4+ T-cell Perturb-seq (Marson laboratory, CZI-hosted). External systems: Schmidt
GSE190604, Norman/Weissman K562 (scPerturb), Replogle RPE1 (scPerturb). Clinical atlas: Functional
CAR-T atlas (Zenodo 19066393, DOI 10.5281/zenodo.17213452).

## Author contributions

A.C. conceived and directed the project, provided clinical and immunological framing, and made all
scientific decisions. An autonomous analysis agent (Claude Science) implemented the pipeline,
executed all computation, and performed adversarial self-auditing of leakage and overclaims under
A.C.'s direction.

## Acknowledgements

Built for the "Built with Claude: Life Sciences" hackathon (Researcher Track). We thank the Marson
laboratory and CZI for the T-cell Perturb-seq resource, and the ML4BM-Lab (University of Navarra)
for the open Functional CAR-T atlas.

## Competing interests

The author declares no competing interests.

## Clinical disclaimer

This is a computational research study. Nothing herein is medical advice or a validated clinical
biomarker. The clinical-response analysis is explicitly reported as a negative result; no axis
described here should be used to guide patient treatment. Clinical decisions must be made by a
qualified physician with full patient context.

---

## References

*All references were retrieved and title-matched against PubMed during this work; DOIs resolve to the
named papers.*

1. Schmidt R, et al. **CRISPR activation and interference screens decode stimulation responses in
   primary human T cells.** *Science* 2022. https://doi.org/10.1126/science.abj4008
2. Schmidt R, et al. **Functional CRISPR dissection of gene networks controlling human regulatory
   T cell identity.** *Nature Immunology* 2020. https://doi.org/10.1038/s41590-020-0784-4
3. Cortez JT, et al. **CRISPR screen in regulatory T cells reveals modulators of Foxp3.** *Nature*
   2020. https://doi.org/10.1038/s41586-020-2246-4
4. Freitas KA, et al. **Central control of dynamic gene circuits governs T cell rest and
   activation.** *Nature* 2024. https://doi.org/10.1038/s41586-024-08314-y
5. Khan O, et al. **TOX transcriptionally and epigenetically programs CD8⁺ T cell exhaustion.**
   *Nature* 2019. https://doi.org/10.1038/s41586-019-1325-x
6. Chen JW, et al. **Modulating AP-1 enables CAR T cells to establish an intratumoral persistence
   program.** *Science Immunology* 2026. https://doi.org/10.1126/sciimmunol.adw7685
7. Wang P, et al. **Deciphering driver regulators of cell fate decisions from single-cell
   transcriptomics data with CEFCON.** *Nature Communications* 2023.
   https://doi.org/10.1038/s41467-023-44103-3
8. Roohani Y, et al. **Predicting transcriptional outcomes of novel multigene perturbations with
   GEARS.** *Nature Biotechnology* 2024. https://doi.org/10.1038/s41587-023-01905-6
9. Cui H, et al. **scGPT: toward building a foundation model for single-cell multi-omics using
   generative AI.** *Nature Methods* 2024. https://doi.org/10.1038/s41592-024-02201-0

*A grounded narrative synthesis of this literature, with the project's position relative to each
strand, is in `reports/literature_review.md`.*