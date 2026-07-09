# ISCI — 3-minute demo script

**Total: 3:00. One central figure, one honest story, one reusable lesson.**

---

### 0:00–0:25 — The question (hook)
> "Genome-scale Perturb-seq tells us which genes *change* a T cell's state. It does **not** tell us which genes *control* it. For CAR-T and T-cell engagers, that difference is everything — you want to engineer the controller, not chase a bystander. We built ISCI to separate the two, on Alex Marson's genome-scale CD4+ T-cell screen, entirely inside Claude for Life Sciences."

*(On screen: title + the Marson dataset, 33,983 perturbations × 10,282 genes.)*

### 0:25–1:05 — The honest failure (credibility)
> "Our first index failed — three times. It lost to a trivial baseline: just count how many genes a perturbation moves. When we dug in, the reason was subtle and important: **the ground truth is confounded by effect size.** Known regulators have about 99-fold larger effects, so *any* test of 'our index versus magnitude' is rigged. Magnitude wins by construction."

*(On screen: the three negatives, then the Mann–Whitney p = 2.6e-10 magnitude gap.)*

### 1:05–2:00 — The fix + the result (payoff)
> "The fix wasn't a fancier index — it was the right question. Instead of asking 'does our signal beat magnitude?', we asked 'does it add anything **conditional on** magnitude?' And there it was: among perturbations with the *same* effect size, real regulators produce effects that are more **state-specific** and more **reproducible across donors**. That orthogonal signal nearly **doubles** regulator recovery — AUPRC 0.41 to 0.64, bootstrap gain +0.23, positive in 99.6% of resamples."

*(On screen: the central figure — panel A the AUPRC jump with CIs, panel B the specificity separation p = 2.8e-6.)*

> "It survives every leakage control, and replicates across all three culture conditions."

### 2:00–2:35 — What it nominates + Claude's role
> "ISCI then ranks 2,520 genes. As a sanity check it recovers known regulators near the top — IRF1, STAT6, GATA3, SETDB1; as discovery it nominates candidates that are *not* in the label set — IKBKB in NF-κB signaling, ZC3H12A the RNA-degrading brake Regnase-1, the corepressor RCOR1 — each with an evidence card that cites PubMed and honestly flags when the literature is only tangential. Claude ran the whole pipeline: pulled the 17-gigabyte dataset, wrote and red-teamed the benchmark, caught its own leakage, fetched and fact-checked every citation, and welded a reproducibility manifest to every figure."

*(On screen: an evidence card + the provenance manifest.)*

### 2:35–3:00 — The lesson (impact)
> "We also tested the clinical bridge to CAR-T response — and report it as an honest negative. But the methodological result stands on its own: **in-dataset controllability benchmarks are magnitude-confounded, and only a conditional or external test can tell control from association.** That's a reusable caution for the whole perturbation-genomics field — and it's packaged as an open, reproducible Claude skill anyone can run."

*(On screen: repo + MIT license + skill.)*

---

**Recording notes:** screen-record the central figure zoom, the evidence-card markdown, and one `git log` scroll showing the timestamped commit history (New-Work-Only compliance). Keep narration at the pace above — it lands at ~470 words ≈ 3 min at 155 wpm.

---

## OPTIONAL extended panel — property, capacity, and the honest null (for a >3-min cut)

*Splice after 2:35 if making a longer video. Keeps the honest framing.*

> "The conditional result isn't just a Marson finding — it's a **property**. We tested it as a
> falsifiable prediction across four perturbation systems: it should hold in immune cells and
> fail outside. It does — PASS in Marson CD4+, a directional near-miss in a second T-cell screen,
> and honest FAILs in K562 and RPE1. We call it the **Conditional Controllability Invariant**, and
> it is immune-scoped by evidence, not by assumption.
>
> Around that locked core we asked a bigger question: is there a measurable **immune engagement
> capacity** — persistence, killing, resistance as separable axes? At single-cell pseudobulk,
> persistence is a clean axis but killing and resistance stay entangled — about **2.5 axes**, not
> 3, and we report the half. Then the hard test: does any axis predict CAR-T response in a
> 1-million-cell atlas — 87 response-labeled patients across 9 studies? Under honest
> leave-one-**study**-out cross-validation the answer is **no** — the patient-level signal
> collapses to chance, and a trivial CD8-fraction baseline beats every axis. We report that as a **well-powered null**, because a confounded
> positive would be worse than an honest negative.
>
> Finally, mechanism without overclaim: NF-κB and Treg-brake gene sets enrich in controllership
> *independent of* effect size; a signed perturbation graph shows therapeutic direction is a third
> axis — the #1 controller, IRF1, actually points the wrong way. And the 70 controllers are sorted
> into a safety-first board where the two most drug-like genes land in the **dangerous** category.
> Every layer carries its own scope line.
>
> \"One question a reviewer always asks: isn't this just the recent geometric-coherence work
> (Shesha)? We answer it quantitatively. On Frangieh we put all three coordinates side by side:
> Shesha's cell-to-cell coherence tracks effect magnitude almost perfectly — correlation 0.97,
> which actually replicates their own finding — while our two coordinates, cross-donor
> reproducibility and axis-specificity, sit in the magnitude-orthogonal plane. Same magnitude-trap
> diagnosis, different and complementary axis. And we are honest about the bound: remove the
> canonical master TFs from the positive set and the gain weakens — underpowered, not proven gone,
> and we say so."

*(On screen: the 4-system CCI forest plot, the IEC orthogonality heatmap, the leave-study-out
null figure, the curated-enrichment quadrants, the signed-graph heatmap.)*

**The one-line pitch for the whole project:**
> "One locked result — a magnitude-conditional controllability signal that nearly doubles
> regulator recovery — hardened into an immune-scoped **property**, extended into a multi-axis
> **capacity**, and stress-tested against a clinical outcome where we report an honest,
> well-powered null. Claude ran every step, caught its own leakage, and welded provenance to every
> figure."