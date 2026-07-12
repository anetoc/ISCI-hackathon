# Operational decomposition of perturbational controllability

**Status:** post-hoc adversarial stress tests; frozen ISCI/CCI ranking unchanged  
**Protocol:** `reports/CONTROLLABILITY_DECOMPOSITION_PROTOCOL.md`  
**Executed:** 2026-07-12, seed 20260712

## Executive result

The scalar controller score is useful for ranking, but the new tests do not support treating its
precision component as universal. The strongest defensible reformulation is:

> Perturbational controllability is an operational profile with at least three measured dimensions:
> effect reach, axis precision conditional on reach, and repeatability conditional on reach. Axis
> precision is most clearly supported for the data-native Th1/Th2 polarization rulers in this
> screen; transport of individual dimensions remains directional but uncertain after planned
> multiplicity and artifact-readiness controls.

This is a narrower and more scientific claim than a universal factorization or a catalogue of
mechanistic controller regimes.

## T1 — adversarial axis null

Each real axis was compared with 200 planned pseudo-axes preserving size, sign counts, absolute
weights, expression-decile composition and mean absolute gene correlation within 20%. Evaluation
used leave-one-positive-block-out predictions with eight unique matched negatives per positive.

| axis | real OOF ΔAUPRC | pseudo median | empirical p | admissible | verdict |
|---|---:|---:|---:|---:|---|
| TCR activation | −0.003 | −0.008 | 0.458 | 200/200 | UNSUPPORTED |
| Th1 effector | +0.181 | −0.010 | 0.0199 | 200/200 | **SUPPORT** |
| Th2 | +0.253 | −0.009 | 0.0050 | 200/200 | **SUPPORT** |
| Exhaustion-like | — | — | — | 15/200 | NOT_EVALUABLE |
| Memory stem-like | +0.004 | −0.003 | 0.418 | 200/200 | UNSUPPORTED |
| CD4-CTL | — | — | — | 122/200 | NOT_EVALUABLE |
| Treg | −0.041 | +0.003 | 0.924 | 196/200 | UNSUPPORTED |

Interpretation: the result is axis-conditioned. The two supported rulers are the dense,
data-native polarization axes. This is evidence that their biological geometry adds label-aligned
information beyond effect reach and beyond structurally matched rulers. It is not independent
controller validation because the axes and labels still share biological ontology. Unsupported
axes must not be described as biologically irrelevant; they failed this specific incremental test.

The low pseudo-axis admissibility for exhaustion-like and CD4-CTL is itself a design diagnostic:
small, unusually coexpressed signatures may lack a sufficiently large exchangeable null under the
frozen 20% correlation constraint. That is a ruler-calibration limitation, not a negative result.

## T2 — component-support transport map

The family contained all ten planned dataset×component tests. Non-evaluable tests remained in the
BH family with p=1.0.

| dataset | component | OOF ΔAUPRC | 95% CI | permutation p | BH q | verdict |
|---|---|---:|---:|---:|---:|---|
| Marson CD4 | precision | +0.215 | [+0.094, +0.498] | 0.0070 | 0.070 | DIRECTIONAL_UNCERTAIN |
| Marson CD4 | repeatability | +0.074 | [−0.022, +0.311] | 0.0869 | 0.290 | DIRECTIONAL_UNCERTAIN |
| THP-1 myeloid | precision | +0.083 | [−0.030, +0.259] | 0.0370 | 0.185 | DIRECTIONAL_UNCERTAIN |
| THP-1 myeloid | repeatability | +0.004 | [−0.061, +0.080] | 0.415 | 1.000 | DIRECTIONAL_UNCERTAIN |
| Schmidt CD4 CRISPRa | both | — | — | — | 1.000 | NOT_EVALUABLE: only 15 unique negatives for 23 positives |
| Norman K562 | both | — | — | — | 1.000 | NOT_EVALUABLE: only 32 unique negatives for 13 positives |
| Replogle RPE1 | both | — | — | — | 1.000 | NOT_EVALUABLE: no gene-level artifact |

Marson precision reproduces the previous leakage-safe point gain (~+0.215), and its bootstrap CI is
above zero. It does not cross the new family-wise decision bar after BH correction. The scientifically
correct label is therefore directional uncertainty, not failure and not confirmation. THP-1 shows
the same qualitative precision-led pattern at smaller magnitude, with wider uncertainty.

## T4 — condition transport gate

**NOT_EVALUABLE.** The raw Marson h5ad contains Rest, Stim8hr and Stim48hr plus the necessary source
fields, but no reusable gene×condition artifact jointly contains E, S, R, labels and auditable
matching blocks/covariates. The protocol forbids silently converting a new raw-data reconstruction
into a reuse analysis. This is an artifact-readiness gap, not evidence against cross-condition
transport.

## Scientific packaging decision

Keep ISCI-core as the frozen ranking operator. Envelop the result with a **Controllability Profile**:

1. **Reach:** does the perturbation move the system at all?
2. **Precision:** conditional on reach, is movement aligned with a defensible functional ruler?
3. **Repeatability:** conditional on reach, is movement stable across donors/guides/replicates?
4. **Ruler eligibility:** can that functional axis support a valid exchangeable pseudo-axis null?
5. **Evidence status:** observed, directional-uncertain, unsupported or not evaluable.

The new concept worth carrying forward is not a second scalar. It is an axis-specific evidence card
that makes the model show where a controller claim comes from and when the ruler itself cannot be
stress-tested. The next confirmatory experiment should freeze an external label set and explicit
matched blocks prospectively, then test Th1/Th2 precision in a genuinely independent perturbation
system. Family-out and signed KD/CRISPRa tests remain deferred as specified.

## Reproducibility

- T1: `python scripts/run_t1_axis_null.py`
- T2: `python scripts/run_t2_decomposition.py --n-resamples 1000`
- T4: `python scripts/audit_t4_condition_transport.py`
- Figure: `python scripts/plot_decomposition.py`
- Machine-readable outputs: `outputs/decomposition/`

Every result table carries git SHA, data hashes, axes hash, timestamp, command and seed. Raw clinical
or participant-level text was neither used nor emitted.
