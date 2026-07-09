# Dataset feasibility scout — gaps 5/20 (CD8/CAR-T) and 12 (spatial)

Purpose: decide, before any heavy download, whether the two "external immune replication" gaps are
runnable inside the hackathon window. Verdict up front: **both are NOT-FEASIBLE-BY-DEADLINE** as a
drop-in CCI test; both are concrete Paper-2 targets. The reason is the same gate-first logic that
already caught Shirhut (no negative set) and Papalexi (no baseline) — a CCI test needs an effect
matrix + matched negatives + a clean functional axis, and none of the reachable public options
provide all three without multi-day integration.

## Gap 5/20 — CD8 / CAR-T Perturb-seq (the most translationally relevant)

Candidates scouted (public):

| Dataset | System | Why it does NOT drop in |
|---------|--------|--------------------------|
| Belk 2022 (GSE, genome-wide Tex screen + in vivo Perturb-seq) | mouse OT-I CD8 | mouse→human ortholog mapping; Perturb-seq arm is in-vivo TIL, few perturbations with per-gene effect |
| KLF2 / Differentiation-Space-Map (Science 2024) | mouse LCMV CD8 | ~40 TFs, mouse; in-vivo acute+chronic, no matched-negative structure ready |
| Chen 2021 in vivo scCRISPR (Nat Immunol) | mouse OT-I CD8 | 180 curated TFs + NTCs, mouse; effect matrix would need rebuild from raw |
| Legut 2022 orthogonal screens (Nature) | human CD8 | scRNA is targeted characterization of a few hits, not genome-scale Perturb-seq |
| BHLHE40 in-vitro Tex (GSE211015) | mouse | RNA/ATAC screen, not a per-gene single-cell effect matrix |

Conclusion: the clean human CD8/CAR-T Perturb-seq with (a) a per-perturbation effect matrix, (b)
expression-matched negatives, and (c) a defined functional axis does not exist off-the-shelf. The
mouse OT-I resources (Belk, Chen, KLF2) are the right Paper-2 target but require ortholog mapping and
effect-matrix construction — a multi-day job. **Verdict: NOT-FEASIBLE-BY-DEADLINE; highest-priority
Paper-2 external immune replication.**

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
