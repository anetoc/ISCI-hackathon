# Dataset feasibility scout — gaps 5/20 (CD8/CAR-T) and 12 (spatial)

Purpose: decide, before any heavy download, whether the two "external immune replication" gaps are
runnable inside the hackathon window. Verdict up front: **both are NOT-FEASIBLE-BY-DEADLINE** as a
drop-in CCI test; both are concrete Paper-2 targets. The reason is the same gate-first logic that
already caught Shirhut (no negative set) and Papalexi (no baseline) — a CCI test needs an effect
matrix + matched negatives + a clean functional axis, and none of the reachable public options
provide all three without multi-day integration.

## Gap 5/20 — CD8 / CAR-T Perturb-seq (the most translationally relevant)

Candidates scouted (public):

Candidates surfaced by a web_search for "CD8 T cell CRISPR Perturb-seq exhaustion GEO dataset"
(titles as returned; system/accession details NOT independently verified here and must be confirmed
against GEO before any Paper-2 download):

| Candidate (search-result title) | Why it does NOT drop in |
|----------------------------------|--------------------------|
| "Genome-wide CRISPR screens of T cell exhaustion identify chromatin remodeling factors that limit T cell persistence" (Belk, Cancer Cell 2022) | genome-wide exhaustion screen; the single-cell/Perturb-seq arm is not a ready per-perturbation effect matrix with matched negatives |
| "KLF2 maintains lineage fidelity and suppresses CD8 T cell exhaustion during acute LCMV infection" (Science) | in-vivo LCMV CD8; small TF set, no matched-negative structure ready |
| "In vitro modeling of CD8+ T cell exhaustion enables CRISPR screening to reveal a role for BHLHE40" (Science Immunology) | RNA/ATAC screen, not a per-gene single-cell effect matrix |
| "Transcriptional and epigenetic regulators of human CD8+ T cell function identified through orthogonal CRISPR screens" | human CD8, but scRNA is targeted characterization of hits, not genome-scale Perturb-seq |
| "Single-cell CRISPR screens in vivo map T cell fate regulomes in cancer" | in-vivo scCRISPR; effect matrix would need rebuild from raw |

Conclusion: none of these is a drop-in human CD8/CAR-T Perturb-seq with (a) a per-perturbation effect
matrix, (b) expression-matched negatives, and (c) a defined functional axis. Several are mouse and/or
in-vivo and would require ortholog mapping and effect-matrix construction from raw — a multi-day job,
and each accession/system label must be verified against GEO first. **Verdict:
NOT-FEASIBLE-BY-DEADLINE; highest-priority Paper-2 external immune replication.**

## Gap 12 — spatial (resistance-niche localization)

The scientific hypothesis (resistance modules localize to suppressive/post-infusion niches, while
persistence/sensitivity appear in product or effector interface) is sound but is a *localization*
study, not a CCI PASS/FAIL. It needs paired pre/post-CAR-T spatial transcriptomics with annotated
niches; public DLBCL/MM CAR-T spatial series with that pairing are scarce and would be exploratory
scoring, not adjudication. **Verdict: NOT-FEASIBLE-BY-DEADLINE; Paper-2 / prospective-cohort
companion.**

## What IS feasible now (done or briefed)
- Gap 2 (independent positive set): **DONE** — external functional-screen set FAILs, sharpest honest
  boundary (Fig 2c).
- Gap 13 (foundation-model triangulation): **briefed** for the machine (scGPT zero-shot embedding
  separation) — `briefs/07_scgpt_zeroshot_concordance.md`.
- Gaps 9 (phospho-flow) and 8/17 (prospective cohort): wet-lab / clinical — protocol stubs only,
  `reports/experimental_protocols_paper2.md`.
