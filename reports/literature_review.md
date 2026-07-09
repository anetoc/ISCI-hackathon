# Literature review — controllership, T-cell state, and the CAR-T translation gap

*Grounding review for the CCI/IEC project. Every citation below was retrieved and title-matched
against PubMed during this work; DOIs resolve to the named paper. Recent (2025–2026) items are
flagged as such. This is a synthesis, not an exhaustive survey — it maps where our contribution
sits and what it does and does not add.*

## 1. Genome-scale T-cell perturbation

The experimental substrate for this project — perturbing thousands of genes in primary human T
cells and reading out state by single-cell RNA-seq — matured over the last five years from the
Marson group and collaborators. Functional CRISPR screens first showed that gene networks
controlling human T-cell proliferation and identity can be dissected at scale, and that regulatory
T-cell identity has discrete, perturbable modulators
([Schmidt 2020](https://doi.org/10.1038/s41590-020-0784-4);
[Cortez 2020](https://doi.org/10.1038/s41586-020-2246-4)). The decisive methodological step was
pairing CRISPR activation and interference with single-cell readouts to decode *stimulation-
responsive* circuits — establishing that the same gene can be a controller or a bystander
depending on activation context ([Schmidt 2022](https://doi.org/10.1126/science.abj4008)). Most
recently, the field has moved from static screens to *dynamic* circuit control, showing that gene
programs governing T-cell rest versus activation are centrally coordinated rather than additively
wired ([Freitas 2024](https://doi.org/10.1038/s41586-024-08314-y)). This trajectory frames our
input data: a genome-scale Perturb-seq atlas in primary CD4+ T cells is now a stable enough
substrate to ask not just *which genes move state* but *which genes control it* — the distinction
our work formalizes.

The key unaddressed problem in this literature is that "hit-calling" in these screens is
dominated by effect size. A perturbation that shifts many genes is easy to call; whether that
shift reflects *control* of a state axis or merely a large, diffuse disturbance is rarely
separated. Our contribution is precisely this separation, and §4 below situates it against the
network-inference alternative.

## 2. T-cell state axes

The biology our axes encode is well established. Exhaustion is a distinct, epigenetically
enforced differentiation state, not simply loss of function: TOX was shown to transcriptionally
and epigenetically program CD8+ T-cell exhaustion, making it a state the cell is *driven into*
rather than a passive decline ([Khan 2019](https://doi.org/10.1038/s41586-019-1325-x)). This
matters for a controllership framework because it means exhaustion has dedicated regulators — the
kind of directional, axis-specific controllers our conditional test is designed to surface,
distinct from genes that merely correlate with the exhausted transcriptome.

The therapeutically desirable counter-axis — stem-like memory, persistence — is equally
program-driven, and recent work continues to identify transcription factors whose modulation
shifts CAR T cells toward durable intratumoral persistence, most recently through AP-1 family
rebalancing ([Chen 2026](https://doi.org/10.1126/sciimmunol.adw7685)). The recurring lesson across
this literature is that the axes we score — persistence, killing, exhaustion/resistance — are real,
separable biological programs with identifiable master regulators, which is the premise the
Immune Engagement Capacity (IEC) layer tests at single-cell resolution. Our pseudobulk finding
that persistence is a clean axis while killing and resistance stay partly entangled ("2.5 axes")
is a quantitative refinement of this qualitative picture, not a contradiction of it.

## 3. From association to control

A persistent gap in perturbation genomics is the absence of an agreed operational definition of a
*controller* that is not simply a high-effect gene. The network-inference community has proposed
one answer: infer a gene regulatory network, then apply control-theoretic criteria to nominate the
minimal set of driver nodes that can steer the system. CEFCON is the clearest recent instance —
it deciphers driver regulators of cell-fate decisions from single-cell data by combining GRN
inference with network-control principles ([Wang 2023](https://doi.org/10.1038/s41467-023-44103-3)).
This is the intellectual neighbor of our work, and the contrast is the point: CEFCON derives
control from *inferred* topology, whereas our Conditional Controllability Invariant (CCI) derives
it from *observed causal perturbation effects*, conditioning on magnitude rather than reconstructing
a graph. The two are complementary — an inferred-network prior and a magnitude-conditional
empirical test — but ours avoids the well-known fragility of GRN inference and is directly
falsifiable on held-out perturbation systems.

Our negative control result — that structural network centrality (PageRank, in-degree) adds
nothing over effect magnitude — is worth stating against this backdrop: it is a caution that
topology-derived "influence" can be magnitude-confounded unless explicitly deconfounded, which is
the same trap our conditional test is built to avoid.

### 3.1 The closest prior art: geometric coherence (Shesha)

The nearest neighbor to our core method is not a network-control paper but a very recent geometric
one. Raju (2026, arXiv 2604.16642) introduces *perturbation stability* (Sₚ), the directional
coherence of a perturbation measured as the mean cosine similarity between individual cells' shift
vectors and the mean perturbation direction. Across five CRISPR datasets, stability correlates
strongly with magnitude (Spearman ρ = 0.75–0.97), yet the discordant cases expose regulatory
architecture — pleiotropic regulators pay a "geometric tax" (large but incoherent shifts) — and Sₚ
provides *incremental* prediction of pathway activation and of split-half directional
reproducibility **after controlling for magnitude**. This is, in its general form, the same
diagnosis we make (magnitude is a confound; coherence conditional on magnitude carries real signal)
and it predates our work. We regard this as **convergent validation, not a threat**: two independent
groups identifying the same magnitude trap in the same year strengthens the phenomenon's
credibility. What remains distinct in our work is orthogonal to Shesha on four axes — (i) our
coherence is *cross-donor* reproducibility across human donors, not *cell-to-cell* coherence within
a perturbation; (ii) we add *axis-specificity* onto defined T-cell functional axes rather than
generic dispersion; (iii) we state and test an *immune-scoped falsifiable boundary* (PASS in immune,
FAIL in non-immune systems); and (iv) we separate controllership from therapeutic desirability and
report an honest clinical null. The correct positioning of our contribution is therefore not "we
discovered that magnitude is a confound" (Shesha and we found this convergently) but "we define a
cross-donor, axis-specific, immune-scoped controllability property and map its falsifiable
boundary."

## 4. Predicting perturbation outcomes: foundation models

A parallel line attacks the problem by learning, rather than testing. Perturbation-prediction
models such as GEARS predict the transcriptional outcome of novel, even combinatorial, genetic
perturbations by embedding genes in a learned graph
([Roohani 2024](https://doi.org/10.1038/s41587-023-01905-6)), and single-cell foundation models
such as scGPT learn general-purpose gene and cell representations from tens of millions of cells
([Cui 2024](https://doi.org/10.1038/s41592-024-02201-0)). These are powerful, but they answer a
different question than ours: they predict *what a perturbation does*, not *whether a gene controls
a state axis independent of how much it does*. Their relevance to our project is as an
**independent triangulation** — a foundation model that never saw our screen's regulator labels
provides an external, non-circular check on whether our top controllers occupy a distinguished
region of representation space. We scope this as a concordance test with matched negatives (never a
fine-tuning-on-labels exercise, which would manufacture the agreement), precisely because the
foundation-model literature has repeatedly shown that zero-shot and fine-tuned behavior can
diverge sharply.

## 5. Clinical translation gap

The motivation for the whole program is that CAR-T and T-cell-engager failure remains
incompletely predictable from the infusion product. Long-term follow-up confirms that a
substantial fraction of patients relapse, and clinical outcomes stratify with T-cell state
composition, but a transportable transcriptional *predictor* of response has been elusive. Our own
well-powered null — no IEC axis predicts CAR-T response under leave-one-study-out cross-validation
on a >1M-cell, 87-patient atlas — is consistent with a recurring methodological finding in this
space: apparent single-cohort predictors frequently reflect per-study batch structure rather than
transportable biology, and collapse when validation crosses studies. Reporting this as a
well-powered negative, rather than a leave-one-patient-out positive that would not survive
cross-study validation, is the honest posture the field increasingly demands. The clinical claim
our project makes is deliberately bounded: IEC is a descriptive, measurable multi-axis capacity,
not a validated response biomarker.

## 6. Where this project sits

Three sentences locate the contribution. First, the substrate (genome-scale T-cell Perturb-seq) is
mature enough to ask a controllership question, but the field lacks a magnitude-deconfounded
operational definition of control — which we supply as the CCI. Second, the biology of the axes
(exhaustion, stemness, persistence) is established, so the novel object is not the axes but the
*capacity* they jointly define and its falsifiable, immune-scoped controllability. Third, the
honest clinical null aligns with a growing recognition that cross-study validation is the correct
bar, and that a well-powered negative is a more useful contribution than an un-transportable
positive.

---

*Reference set retrieved via PubMed; most anchors were title-DOI paired from a single PubMed record,
and the scGPT and CellOracle DOIs were confirmed against their exact-title PubMed records (PMID
38409223 and the CellOracle Nature entry respectively) rather than a keyword first-hit. Anchors span the substrate,
the axis biology, the control-theoretic and foundation-model neighbors, and the translation gap.
The review is intentionally scoped to load-bearing anchors rather than an exhaustive bibliography;
additional recent primary papers surfaced in retrieval but are not cited where they would not change
the synthesis.*