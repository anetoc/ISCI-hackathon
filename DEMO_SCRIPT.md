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

## OPTIONAL extended panel — T-REMAP (only for a >3-min cut)

*Splice after 2:35 if making a longer video. Keeps the honest framing.*

> "Building on the locked core, we inverted the question: instead of predicting response,
> we ask which perturbations push T cells *away from* clinical resistance programs. Every
> clinical module first passes a movability gate — its genes are actually moved by
> perturbations. The reversal score has a permutation null at p = 0.001, and after we
> residualize out both magnitude and TCR-shutdown, the trivial 'turn the TCR off' hits
> drop away and specific chromatin and RNA-state controllers — KDM1A, CREBBP, Regnase-1 —
> rise to the top. In an independent CAR-T cohort, the sensitivity axis replicates
> direction; the resistance axis does not, and we say so."

*(On screen: the mechanism map + the reversal heatmap + the confounder ledger.)*