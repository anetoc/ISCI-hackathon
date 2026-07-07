# ISCI — Immune-State Controllability Index

**Built with Claude: Life Sciences** hackathon (Researcher Track) — genome-scale Perturb-seq in primary human CD4+ T cells → clinically projectable controllability scores for CAR-T and bispecific/T-cell engager resistance.

> Private development repo during the event. Open-source MIT submission by Jul 13, 2026.

## Thesis

Genome-scale perturbation maps tell us which genes *change* T-cell state, but not which genes *control* it in a reproducible, structurally grounded, and clinically actionable way. **ISCI** separates **controllers** from **associates** using five components:

| Component | Meaning |
|-----------|---------|
| **M** | Directional movement along functional axes |
| **R** | Reproducibility (cross-donor / cross-guide) |
| **D** | Structural network control (GRN + FVS/MDS) |
| **A** | In-silico concordance (CellOracle / GEARS / pert2state) |
| **S** | Target-state stability / attractor depth *(novel)* |

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/plan.md](docs/plan.md) | Full phased plan (D0–D6), architecture, handoff |
| [docs/related_work.md](docs/related_work.md) | Literature review, datasets, connectors, novelty gap |
| [docs/method.md](docs/method.md) | ISCI mathematical specification |
| [docs/benchmark.md](docs/benchmark.md) | Ablation design and ground-truth benchmark |
| [docs/claude_science_prompt.md](docs/claude_science_prompt.md) | Master prompt for Claude for Life Sciences |

## Primary data (not in git — download locally)

```bash
aws s3 cp --no-sign-request \
  s3://genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.DE_stats.h5ad \
  data/

aws s3 cp --no-sign-request \
  s3://genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.pseudobulk_merged.h5ad \
  data/
```

Reference: [Marson lab Perturb-seq](https://virtualcellmodels.cziscience.com/dataset/genome-scale-tcell-perturb-seq) · code [`emdann/GWT_perturbseq_analysis_2025`](https://github.com/emdann/GWT_perturbseq_analysis_2025) · baseline [`emdann/pert2state_model`](https://github.com/emdann/pert2state_model)

## Setup

```bash
# Requires Python 3.11+ and uv (https://docs.astral.sh/uv/)
uv sync
```

## Package layout (seed stubs — implementation in Claude Science)

```
isci/           # M, R, D, A, S components + validation + evidence cards
config/axes.yaml
notebooks/01_isci_d0.ipynb
```

## Ambition ladder

- **D0** — M+R + baselines + ground-truth recovery (minimum submission)
- **D1** — + network control (D)
- **D2** — + stability (S) + ablation
- **D3** — external validation (Belk / Schmidt / Frangieh)
- **D4** — clinical bridge (CAR-T / bispecific cohorts) — gold for Impact
- **D5–D6** — multi-omics, foundation models, Claude Science skill

## Author

Abel Costa — hematologist / onco-hematologist, IDOR (São Paulo)

## License

MIT — see [LICENSE](LICENSE).
