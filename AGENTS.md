# T-CTRL / ISCI — repository rules

T-CTRL is the public, judge-facing experience. ISCI (Immune-State Controllability Index) is the
scientific method, Python package, CLI and provenance namespace behind it. Introduce both names on
high-level public surfaces as **“T-CTRL, powered by ISCI.”** Judge-stage copy must describe older
project concepts in plain language rather than introducing CCI, IEC, T-REMAP or TSC as additional
brands. Those historical terms remain valid inside the evidence archive. Keep metric and column
names stable.

## Sources of truth

Use these sources in this order when wording or numbers differ:

1. `reports/result_lock.md` — frozen scientific result and estimand hierarchy.
2. `reports/CLAIM_LEDGER.md` — adjudicated claims, scope and prohibited overclaims.
3. `docs/method.md` — mathematical and analytical method.
4. `config/axes.yaml` — frozen functional axes.
5. `config/hackathon_claims.yaml` — judge-demo presentation contract derived from the sources above.

Generated outputs, historical D0 files and exploratory reports never override this hierarchy.

## Locked scientific contract

For perturbations with a detectable effect:

- `M` is perturbation effect magnitude.
- `C` is controllership evidence: magnitude-residualized axis specificity plus cross-donor
  repeatability.
- `ISCI_orthogonal` is the mean rank percentile of those residualized controllership components.
- The authoritative test asks whether `C` adds regulator-recovery signal after `M` is already known:
  **M → M+C**.

The frozen result hierarchy is:

- Primary full-sample incremental gain: **+0.357 AUPRC**, 95% CI **[+0.117,+0.538]**.
- Leakage-free out-of-fold gain: **+0.215**, 95% CI **[+0.074,+0.560]**, permutation **p=0.010**.
- Descriptive full detectable-set ranking: **0.415→0.722**.
- Three-condition matched C-vs-M comparator: **+0.229 [0.072,0.405]**; this is not the primary
  estimand.

The historical D0 `rank_product(M_pos,Q,R)` score is deprecated. It may be retained only in an
explicitly labelled historical archive and must never be presented as the final method.

## Hard rules

1. Do not change `config/axes.yaml`, the positive sets, the formula or the claim gates without a
   dedicated scientific-review change that updates `docs/method.md`, `reports/result_lock.md` and
   tests together.
2. Benchmark negatives are native, expression/power matched; do not substitute GTEx or unmatched
   background genes.
3. Axis markers cannot count as benchmark wins without leave-one-marker-out reconstruction.
4. Every result table must carry `git_sha`, `data_sha256`, `axes_sha256`, timestamp and command.
5. Separate observed Perturb-seq evidence from literature, mechanistic and clinical hypotheses.
6. Do not claim a universal controller score, therapeutic target or validated biomarker.
7. `PASS`, `FAIL`, `NULL` and `NOT-EVALUABLE` are distinct valid outcomes; never convert missing
   inputs into a biological null.
8. Never commit raw `.h5ad`/`.h5mu`, credentials, environment files or raw clinical text.
9. Public surfaces are written in English. A Portuguese translation must live in a separately
   labelled file such as `README.pt-BR.md`.
10. Tests, lint, build, link checks and hackathon readiness must pass before release.
11. Judge-facing copy uses only “T-CTRL, powered by ISCI”; historical project acronyms belong in
    technical reports and must not be required to understand the demo.

## Reproducible commands

```bash
uv sync --extra dev --extra visualization
uv run pytest -q
uv run ruff check isci scripts tests
uv build
make hackathon-package
```

Heavy source datasets are public but intentionally not versioned. Dataset source, accession,
license and checksum requirements are documented in `data/README.md` and `docs/dataset_spec.md`.
