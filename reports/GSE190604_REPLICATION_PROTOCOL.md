# GSE190604 targeted-panel replication protocol

**Status:** locked before raw matrix analysis  
**Dataset:** Schmidt et al. primary human T-cell CRISPRa Perturb-seq, GSE190604  
**Scope:** external to Marson; targeted-panel reanalysis, not a new unseen dataset

## Primary question

Does Th2-axis precision add controller-label information beyond effect reach in stimulated primary
T cells when expression/power overlap is handled without impossible disjoint matching blocks?

## Population and labels

- Singleton-guide cells and NO-TARGET controls only.
- Pseudobulk per target×well; minimum 25 cells and at least three of four wells per context.
- Contexts: no-stim wells 1–4 and stimulated wells 5–8, confirmed on the official GEO record.
- Positive labels are frozen from committed `near_immune_scores.csv`; all other eligible targeted
  genes are negatives. Labels are not revised after raw feature inspection.

## Feature construction

- Raw counts aggregated per target×well, then log1p counts per million.
- Effect vector = target profile minus well-matched NO-TARGET profile.
- Reach `E` = L2 norm of the mean effect vector.
- Axis precision = absolute projection on the unchanged Marson axis with leave-target-out.
- Repeatability = mean pairwise well correlation over the 2,000 most moved genes.
- Signed projections are emitted for direction analysis but do not determine the primary verdict.

## Targeted-panel overlap design

The panel has 74 targets, so five disjoint negatives per positive are impossible. Use 5-fold,
10-repeat stratified OOF. In every fold:

1. estimate positive-label propensity from baseline target expression and target cell count;
2. derive overlap weights (`positive: 1-p`, `negative: p`), clipped at 0.05–0.95;
3. fit rank residualization, scaling and the outcome models on training genes only;
4. compare `label ~ E` with `label ~ E + Th2_precision|E` on held genes.

## Tests

- **Primary:** stimulated Th2 precision.
- **Secondary:** no-stim Th2 precision; stimulated Th1 precision; stimulated repeatability.
- CI: 1,000 stratified gene bootstraps of OOF predictions.
- Null: 1,000 label permutations preserving positive count, rerunning the full nested pipeline.
- BH-FDR is reported across all four tests. The primary verdict additionally reports its raw
  permutation p because it was designated before matrix analysis.

## Verdict

- `REPLICATED_EXPLORATORY`: gain and coefficient positive, CI above zero, primary permutation
  p<0.05 and BH q<0.05.
- `DIRECTIONAL_UNCERTAIN`: direction positive but an uncertainty gate fails.
- `UNSUPPORTED`: gain or coefficient non-positive.
- `NOT_EVALUABLE`: fewer than eight positives, fewer than fifteen negatives, insufficient wells or
  non-finite overlap features.

The strongest allowed conclusion is external targeted-panel replication of an axis-conditioned
signal. This does not establish universality, therapeutic direction or clinical efficacy.
