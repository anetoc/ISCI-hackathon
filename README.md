# ISCI — Immune-State Controllability Index

**Built with Claude: Life Sciences** hackathon (Researcher Track) — genome-scale Perturb-seq in primary human CD4+ T cells → clinically projectable controllability scores for CAR-T and bispecific/T-cell engager resistance.

> Private repo during the event → MIT open-source submission by Jul 13, 2026.  
> **Build environment:** Claude for Life Sciences (CPU-local, Mac 24GB).

## Thesis

Genome-scale perturbation maps tell us which genes *change* T-cell state, but not which genes *control* it in a reproducible, structurally grounded, and clinically actionable way. **ISCI** separates **controllers** from **associates** using five components (all benchmarked under **leave-one-out axes**):

| Component | Meaning |
|-----------|---------|
| **M** | Directional movement along functional axes |
| **R** | Reproducibility (cross-donor / cross-guide) |
| **D** | Continuous network influence (connector-grounded GRN) |
| **A** | pert2state linear concordance (also mandatory baseline) |
| **S** | Magnitude-residualized geometric coherence (Shesha) |

**Headline:** auditable causal index + clinical bridge — not raw stability alone.

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/execution_plan.json](docs/execution_plan.json) | **Approved phased plan** from Claude Science (D0–D4) |
| [docs/method.md](docs/method.md) | ISCI spec with C1–C8 peer-review fixes |
| [docs/benchmark.md](docs/benchmark.md) | LOO ablation design + ground-truth tiers |
| [docs/related_work.md](docs/related_work.md) | Literature, datasets, connectors |
| [docs/plan.md](docs/plan.md) | Full strategic plan (D0–D6) |
| [docs/claude_science_prompt.md](docs/claude_science_prompt.md) | Master prompt (initial critique; fixes now in method.md) |

## Primary data (not in git — download locally)

```bash
aws s3 cp --no-sign-request \
  s3://genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.DE_stats.h5ad \
  data/

aws s3 cp --no-sign-request \
  s3://genome-scale-tcell-perturb-seq/marson2025_data/GWCD4i.pseudobulk_merged.h5ad \
  data/
```

## Setup

```bash
uv sync   # Python 3.11+
```

## Minimum submission (D0–D2)

LOO benchmark + ranked gene table + **central ablation figure** (ISCI vs pert2state vs DE magnitude).

## Stretch (D4)

ISCI signature on Functional CAR-T atlas (phenotype floor) → outcome test if powered.

## Author

Abel Costa — hematologist / onco-hematologist, IDOR (São Paulo)

## License

MIT — see [LICENSE](LICENSE).
