# ISCI method — magnitude-conditional T-cell controllership

**Status:** frozen for the hackathon release. The authoritative result wording and estimand
hierarchy live in [`reports/result_lock.md`](../reports/result_lock.md). T-CTRL is the public
experience; ISCI is the method and provenance namespace.

## Scientific question

Perturbation screens naturally reward genes with large transcriptomic effects. That does not prove
that a gene controls a functional cell state. ISCI therefore does not ask whether a composite score
beats magnitude. It asks:

> After effect magnitude is already known, do state precision and biological repeatability add
> information for identifying canonical T-cell-state regulators?

The answer is evaluated as an incremental test, **M → M+C**, not as an unrestricted target-ranking
claim.

## Inputs

The supported pipeline accepts a versioned [`DatasetSpec v1`](dataset_spec.md) describing one of:

- precomputed per-perturbation controller features;
- long-form CSV or Parquet perturbation effects;
- an effect-matrix H5AD;
- pooled cell-by-feature H5AD with matched controls; or
- arrayed single-guide H5AD.

Every dataset declares its perturbation, condition and replicate semantics. Public source,
accession, license, checksum and data classification are required provenance. Raw large datasets
remain outside Git.

## Frozen functional axes

`config/axes.yaml` defines seven signed CD4+ T-cell programs: activation/TCR, Th1, Th2,
exhaustion-like, memory/stem-like, CD4-CTL/cytotoxic and Treg. Axis vectors are unit normalized.

When a benchmark-positive gene is itself an axis marker, that marker is removed before the gene is
scored. This leave-one-marker-out reconstruction prevents a label from winning because its own name
was embedded in the axis.

## Features

For perturbation `g`, context `c` and frozen axis `a`:

### Magnitude M

`M(g,c)` measures how far the perturbation moves the expression profile. For canonical long effects
the reusable pipeline uses the RMS of the mean standardized-effect vector; the Marson locked
analysis also carries native effect/power covariates such as total DE genes, target expression,
guide count and cell support.

Magnitude is a confounder and a required baseline. It is not called controllership.

### State specificity

The signed projection of the perturbation-effect vector onto each frozen axis records direction.
Specificity summarizes whether the effect concentrates along a recognizable state program rather
than spreading diffusely across many unrelated genes. The primary controller feature uses the
strongest absolute leave-one-marker-out axis projection; signed projections remain available for
biological interpretation.

### Reproducibility

Reproducibility measures agreement across independent biological units. Donors are the preferred
replicate; guide-level or well-level agreement may support the estimate but cannot inflate the
biological sample size. If the declared dataset lacks the replicate structure required for the
claim, the pipeline returns `NOT-EVALUABLE` rather than imputing agreement.

### Magnitude-conditional controllership C

Specificity and reproducibility are residualized against magnitude using only the relevant training
partition. Their residuals are percentile ranked, and the supported score is:

```text
ISCI_orthogonal(g) = mean(
    percentile(residual_specificity(g)),
    percentile(residual_reproducibility(g))
)
```

The public ranking is restricted to `detectable_effect == True`, defined at the frozen dataset
median unless the DatasetSpec declares a pre-approved alternative. The detectable-effect gate
prevents a technically orthogonal but biologically negligible perturbation from being promoted.

## Benchmark contract

1. Freeze axes, positives, exclusions, matching covariates and seed before adjudication.
2. Select negatives from the same perturbation screen, matched on expression and statistical power
   variables such as target expression, guide count, cell support and condition.
3. Reconstruct leave-one-marker-out axes.
4. Compare a magnitude-only model with magnitude plus controllership features.
5. Report AUPRC gain as primary because positives are rare; precision@20/50 and rank stability are
   supporting metrics, while AUROC is secondary.
6. Bootstrap the matched comparison and repeat every learnable operation inside grouped
   out-of-fold evaluation.
7. Keep full-sample, OOF, descriptive and cross-system estimands visibly separate.

The canonical implementation is split between:

- `isci/feature_extraction.py` — magnitude, LOO specificity and replicate features;
- `isci/analysis_runner.py` — dataset execution and conditional ranking;
- `isci/decomposition.py` and `isci/panel_validation.py` — fitted residualization and OOF tests;
- `skills/isci-controllership/kernel.py` — compact reference statistics used by the locked
  Marson reproduction path.

## Verdict contract

- **PASS:** the prespecified direction and every required gate are satisfied.
- **FAIL:** the claim is evaluable and a directional or required gate is violated.
- **NULL:** the claim is evaluable but no supported incremental signal is present.
- **NOT-EVALUABLE:** a required input or structural gate is absent; no biological conclusion is
  forced.

The method does not convert a controller score into therapeutic desirability. Mechanistic,
targetability, clinical-response and foundation-model analyses are separate evidence overlays.

## Provenance and deterministic execution

Each promoted result records Git SHA, data SHA-256, axes SHA-256, timestamp, command, configuration
and seed. The supported commands are:

```bash
uv run isci validate path/to/dataset.yaml
uv run isci inspect path/to/dataset.yaml
uv run isci pipeline path/to/dataset.yaml
```

The complete release gate is `make hackathon-package`; the test-only gate is
`make hackathon-check`.

## Historical method

The initial D0/D1 design attempted `R·S·geomean(M,D,A)` and an earlier rank product. It lost to the
magnitude baseline under native matched negatives and was rejected. Its minimal evidence is kept in
[`archive/d0/`](../archive/d0/) so the correction remains auditable without shipping deprecated
modules in the Python wheel.

