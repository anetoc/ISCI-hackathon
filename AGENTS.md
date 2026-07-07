# ISCI Hackathon — Agent Rules (single specification for all tools)

Primary goal: a reproducible D0–D2 ISCI-core analysis for "Built with Claude:
Life Sciences" (Researcher Track). Headline deliverable = an auditable ranking of
**candidate state-shift controllers** in CD4+ T cells, benchmarked against strong
baselines under leakage controls.

## Sources of truth
- **Scientific**: Claude Science artifacts + reports; `docs/method.md`; `config/axes.yaml`.
- **Engineering**: this Git repository; tests must pass before merge.

## The ISCI-core contract (frozen unless PI approves)
```
M_signed(g,a,c) : signed directional movement of the perturbation effect vector
                  onto a frozen, unit-normalized functional axis (zscore primary,
                  log_fc as sensitivity). NES-style signed projection.
Q(g,c)          : causal/QC confidence — on-target KD, target expression, guide
                  count, off-target flags, sample support.
R(g,c)          : reproducibility across donors and guides.
C(g,a,c)        : OPTIONAL state-shift coherence across guide-/donor-pair effects
                  (from by_guide/by_donors), restricted to axis/top-state genes.
ISCI_core(g,a,c) = rank_product(M_signed_positive, Q, R, C_optional)
```
D-lite(g) and A/pert2state are **evidence overlays and benchmark comparators only** —
they MUST NOT alter the ISCI-core ranking unless explicitly approved by the PI.

## Hard rules
1. Do not change `config/axes.yaml` after freeze without a dedicated PR.
2. Do not change the ISCI-core formula without updating `docs/method.md` and tests.
3. Do not commit raw h5ad/h5mu files or large outputs (`.gitignore` enforces this).
4. No clinical-response claims unless cohort metadata AND endpoint are documented.
5. Separate observed Perturb-seq evidence from literature / mechanistic / clinical hypotheses.
6. Every result table carries: `git_sha`, `data_sha256`, `axes_sha256`, timestamp, command.
7. D / A / clinical overlays never enter ISCI-core unless explicitly approved.
8. Benchmark negatives are **Marson-native expression-matched** (target_baseMean,
   n_guides, n_cells_target, condition), NOT GTEx bulk tissue.
9. A gene that appears in an axis signature cannot count as a benchmark win without
   leave-one-marker-out (LOO axis reconstruction).
10. Primary benchmark metrics: precision@20/50, AUPRC, rank-stability. AUROC secondary
    (few true positives).

## Track ownership (surfaces; no two tools edit the same surface)
| Track | Surface | Tool |
|---|---|---|
| P0 Contracts/skeleton | pyproject, AGENTS.md, schemas, stubs, tests | Claude Code |
| P1 D0 science core | scripts/, data manifest, real scores, artifacts | **Claude Science** |
| P2 Package & tests | isci/ modules against fixtures, tests | Codex / Claude Code |
| P3 Benchmark & leak-control | baselines.py, validate.py, metrics | Codex |
| P4 Evidence cards | evidence.py, target cards | Claude Science + red-team |
| P5 Figures/report/demo | plotting.py, report.md, demo assets | Cursor + Claude Code |
| P6 Stretch | stability/network/clinical branches | optional |

Merge policy: formula/axes/ground-truth/schema/clinical-claim changes require PI sign-off.
Tests/CLI/docs/figures-from-existing-data: fast review. No automatic merges.
