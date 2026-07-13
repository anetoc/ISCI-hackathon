# GSE190604 target-paired context interaction protocol

**Status:** locked before computing the interaction statistic; executed without amendment

**Motivation boundary:** this follow-up was motivated by the already observed divergence between
the no-stim and stimulated Th2 tests. It is therefore a post-result explanatory test, not a formal
pre-registration or untouched replication.

## Question

Is the incremental controller-label information carried by Th2 precision larger without
stimulation than under stimulation in the same targeted CRISPRa panel?

## Population and pairing

- Use the committed `gse190604_features.parquet` without rebuilding axes, labels or eligibility.
- Include only genes with one finite no-stim row and one finite stimulated row.
- Preserve the positive/negative label and gene identity across both contexts.
- Require at least eight positive and fifteen negative complete gene pairs.
- The unit of resampling and context exchange is the gene, never a target×context row.

The official GEO protocols establish a paired biological design with two blood donors: cells were
split across conditions and the two donors were then mixed 1:1 before droplet loading. The processed
matrix does not carry donor identity, and each of the four wells is a replicate of the donor mixture,
not one donor. The current result therefore cannot be described as a donor-resolved interaction.

## Statistic

For each context, rerun the frozen overlap-weighted 5-fold/10-repeat OOF pipeline:

1. propensity overlap weights from baseline target expression and target cell count;
2. train-fold-only rank residualization of Th2 precision against effect reach;
3. comparison of `label ~ reach` against `label ~ reach + residual Th2 precision`;
4. overlap-weighted ΔAUPRC on held genes.

The paired interaction statistic is:

`T = ΔAUPRC_no-stim − ΔAUPRC_stim`.

The same seed and sorted gene order are used in both contexts, so fold membership is gene-paired.

## Uncertainty and null

- **CI:** 1,000 stratified paired-gene bootstraps. Each resample draws positive and negative genes
  with replacement and applies the identical sampled gene indices to both context prediction sets.
- **Null:** 1,000 within-gene context exchanges. For every permutation, independently swap the
  complete no-stim/stim feature bundle for each gene with probability 0.5, then rerun both nested
  OOF pipelines. Labels and positive count never change.
- **Permutation p:** one-sided `(1 + count(T_null >= T_observed)) / 1001` because the explanatory
  direction was fixed as no-stim greater than stimulated before computing this interaction.
- There is one interaction hypothesis, so no multiplicity adjustment is applied.

## Adjudication

- `POSTHOC_CONTEXT_SUPPORT`: `T > 0`, bootstrap CI lower bound above zero and swap p<0.05.
- `DIRECTIONAL_UNCERTAIN`: `T > 0` but at least one uncertainty gate fails.
- `UNSUPPORTED`: `T <= 0`.
- `NOT_EVALUABLE`: pair-count, finitude or class-count gate fails.

Even `POSTHOC_CONTEXT_SUPPORT` means only that the already observed GSE190604 divergence survives a
paired diagnostic. It does not establish a stimulation mechanism, donor-resolved transport,
therapeutic direction or independent replication.

## Executed result

All 69 targets formed complete pairs (23 positive, 46 negative). The no-stim minus stimulated
ΔAUPRC contrast was +0.190, with a paired-gene bootstrap interval of [+0.046,+0.370]. However,
90 of 1,000 context-swap null statistics were at least as large as observed, giving p=0.091 after
the finite-sample correction. The frozen verdict is therefore `DIRECTIONAL_UNCERTAIN`, not
`POSTHOC_CONTEXT_SUPPORT`.

The positive bootstrap interval says the contrast is stable to resampling the current target panel;
the non-significant exchange null says it is not yet sufficiently unusual under reassignment of
context within genes. These answer different uncertainty questions and neither result is discarded.
