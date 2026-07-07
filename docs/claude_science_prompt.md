# Claude for Life Sciences — Master Prompt

Paste this when opening the seed repo in **Claude for Life Sciences**. Attach or point Claude to `docs/related_work.md`, `docs/method.md`, `docs/plan.md`, and `docs/benchmark.md`.

---

You are my scientific co-pilot for the **"Built with Claude: Life Sciences"** hackathon (Researcher Track, deadline **Jul 13, 9pm ET**). I am a hematologist / onco-hematologist (IDOR, Brazil). I am attaching my seed repo with these key documents:

- `docs/related_work.md` — literature review, datasets (5 layers), connectors, novelty gap
- `docs/method.md` — mathematical definition of ISCI (M/R/D/A/S)
- `docs/plan.md` — full phased plan D0–D6, architecture, compute feasibility
- `docs/benchmark.md` — ablation design and ground-truth benchmark
- `config/axes.yaml` — functional axis signatures (validate with IDOR)
- `isci/` — Python stubs (implement here with full provenance)

**Read all docs before answering.**

## PROJECT CONTEXT

- **Proposal:** ISCI (Immune-State Controllability Index) — separates genes that **CONTROL** T-cell state transitions (vs merely associated genes), combining:
  - **M** — directional movement along functional axes
  - **R** — reproducibility (cross-donor / cross-guide)
  - **D** — structural network control (GRN + FVS/MDS, CEFCON-style)
  - **A** — in-silico concordance (pert2state, CellOracle, GEARS)
  - **S** — target-state stability / attractor depth (**our differentiator**)
- **Primary dataset:** Marson genome-scale Perturb-seq in primary human CD4+ T cells  
  - CZI: `s3://genome-scale-tcell-perturb-seq/marson2025_data/`  
  - Code: `emdann/GWT_perturbseq_analysis_2025`  
  - Baseline: `emdann/pert2state_model`  
  - Use `GWCD4i.DE_stats.h5ad` (33,983 perturbation×condition, 10,282 genes; layers `zscore`/`log_fc`; obs `donor_correlation_hits_mean`, `guide_correlation_signif`) and `GWCD4i.pseudobulk_merged.h5ad`
- **Clinical focus:** immune reprogramming in hematologic malignancies — CAR-T failure/exhaustion and resistance to bispecifics / T-cell engagers
- **Compute:** Mac M4 Pro 24GB locally; HPC/Modal via Claude Science for heavy steps
- **Judging:** Impact 25%, Claude Use 25%, Depth 20%, Demo 30%; Gladstone prize = greatest potential to advance the field

## WHAT I WANT FROM YOU NOW (critical analysis, not just agreement)

1. **Hackathon fit:** Given the 4 judging criteria and Gladstone prize, where does this project win and where does it risk losing points? Be specific.
2. **TOOLS inventory:** List ALL tools, specialists, connectors, skills, and databases you have access to here that are useful for ISCI. For each, say which pipeline stage it serves (M/R/D/A/S, validation, clinical bridge, evidence cards). Flag tools I did NOT map in the docs.
3. **Gaps and issues:** Critique `method.md` and `related_work.md`. Where is the ISCI math fragile, circular, or non-identifiable? Where could the benchmark leak? What would a Nature Methods reviewer attack first?
4. **New datasets:** Beyond Marson, Belk, Schmidt, Frangieh, Haradhvala GSE151511, Functional CAR-T atlas, ProjecTILs — are there datasets in your 60+ databases for (a) defining axes, (b) external validation, (c) clinical bridge to CAR-T/bispecifics? Prioritize by 1-week feasibility.
5. **Method opportunities:** Perturbation foundation models, GRN inference, network control — what available here strengthens D, A, or S without blowing the deadline?
6. **Architecture and dev plan HERE:** How we build inside Claude Science — skill order, per-artifact provenance, local vs HPC/Modal, traceable evidence cards (claim → citation) per ranked gene. Detail `isci/` modules and end-to-end data flow.
7. **Phased execution (D0→D4):** Daily checkpoints until Jul 13; minimum submission (D0–D2) vs stretch.

## RESPONSE FORMAT

- **(A)** Verdict on strengths/risks  
- **(B)** Tool → stage table (highlight what I missed)  
- **(C)** Prioritized gap list with proposed fixes  
- **(D)** Prioritized new datasets  
- **(E)** Architecture + phased plan  

Be direct, cite the attached files, and tell me where you disagree with my plan.

## AFTER YOUR ANALYSIS

Proceed to implement **D0** (M + R + baselines + ground-truth benchmark) in `isci/`, with full provenance on every artifact. Use connectors for evidence cards — no hallucinated references.
