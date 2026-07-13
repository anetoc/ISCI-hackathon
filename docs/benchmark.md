# ISCI benchmark and leakage-control contract

This document describes the benchmark that supports the frozen T-CTRL/ISCI claim. Exact results
and wording are locked in [`reports/result_lock.md`](../reports/result_lock.md).

## Primary question

Among perturbations with detectable effects, do state specificity and cross-replicate
reproducibility improve recovery of canonical axis-defining T-cell regulators after effect
magnitude is already known?

The comparison is **magnitude M versus magnitude plus controllership C**. It is not the abandoned
question “does a composite index beat magnitude?”

## Positives and scope

The supported positive set contains canonical, axis-defining T-cell-state regulators. This is a
narrow mechanistic class, not every functional regulator. A separate external non-marker positive
set was evaluated and failed, establishing the upper boundary of the claim.

Positive definitions, exclusions and seeds are frozen before adjudication. Results from different
positive populations are never pooled or presented as the same estimand.

## Native matched negatives

Negatives come from the same perturbation screen and are matched on available expression/power
covariates, including target expression, guide count, target-cell support and condition. GTEx bulk
tissue, housekeeping lists and unmatched background genes are not valid primary negatives.

## Leave-one-marker-out axes

If gene `g` appears in a functional-axis signature, `g` is removed from that signature before its
effect is projected. A benchmark positive cannot win by defining its own evaluation axis.

## Metrics

| Metric | Role |
|---|---|
| AUPRC gain, M→M+C | Primary metric; positives are rare |
| Precision@20 and precision@50 | Supporting top-rank utility |
| Rank stability | Supporting robustness metric |
| AUROC | Secondary only |
| Conditional likelihood-ratio test | Tests feature information beyond magnitude |

The full-sample, out-of-fold, descriptive and cross-system matched comparisons answer different
questions and must remain separately labelled.

## Leakage-free evaluation

Inside every held-out fold, the pipeline refits:

1. negative matching or sample weighting;
2. magnitude residualization;
3. feature scaling/ranking;
4. component combination; and
5. the outcome model.

Donor, guide, condition or gene blocks are kept together when their dependence would otherwise
cross the train/test boundary. Permutations respect those same blocks.

## Required stress tests

- detectable-effect threshold sensitivity;
- removal of GATA3, TBX21, STAT6 and IRF1;
- external non-marker functional-regulator positives;
- condition-level replication without calling correlated conditions independent cohorts;
- non-immune and immune-lineage boundary datasets;
- explicit `NOT-EVALUABLE` outcomes when axis coverage or replication is absent.

## Frozen result hierarchy

| Estimand | Result | Interpretation |
|---|---:|---|
| Full-sample M→M+C | +0.357 AUPRC [0.117, 0.538] | Authoritative incremental test |
| Fully refit OOF | +0.215 [0.074, 0.560], p=0.010 | Conservative leakage-free estimate |
| Descriptive ranking | 0.415→0.722 | Point comparison on the detectable set |
| Three-condition matched C-vs-M | +0.229 [0.072, 0.405] | Cross-system comparator only |

## Prohibited interpretations

- universal controllability across genes or cell systems;
- therapeutic target nomination from controller rank alone;
- validated CAR-T response biomarker;
- independent replication when conditions share the same experiment;
- biological failure when required inputs were missing.
