# The Conditional Controllability Invariant

**A candidate general property of perturbation genomics.**
*Status: defined here; tested for cross-dataset invariance in the companion generalization report.*

---

## 1. Motivation — from a score to a property

ISCI began as an index on one dataset (Marson genome-scale CD4+ Perturb-seq). Run
honestly, the index itself **lost** to a trivial effect-magnitude baseline, because
the ground truth (known regulators) is confounded by magnitude: known regulators
simply produce larger effects, so any test of "index vs magnitude" is rigged.

The result that survived is not an index but a **property of the data**: after you
condition on effect magnitude, there remains a reproducible, axis-specific signal
that distinguishes genes that *control* a cell-state transition from genes merely
*associated* with it. We call this the **Conditional Controllability Invariant (CCI)**
and ask whether it is a general property of perturbation screens, not a Marson artifact.

## 2. Formal definition

For a perturbation screen with per-perturbation differential-expression statistics,
define for each perturbed gene *g* acting on a functional state axis *a*:

- **Magnitude** `M(g)` — the size of the transcriptional effect (e.g. number of
  differentially expressed genes, or total effect norm). This is the confound.
- **Axis-specificity** `S(g,a)` — how concentrated the effect is on the functional
  state axis *a* versus diffuse across the transcriptome (an enrichment/projection,
  not a raw magnitude).
- **Reproducibility** `R(g)` — coherence of effect direction across independent
  replicates (donors, guides, or biological replicates).

Let `Sᵣ`, `Rᵣ` be `S` and `R` **residualized on `M`** (rank-regression, keep the
residual percentile). Define the controllership feature

> **`C(g) = mean( Sᵣ(g,a*), Rᵣ(g) )`**, over the best-matching axis `a*`,

restricted to perturbations with a **detectable effect** (`M` above the dataset
median), because `S` and `R` are undefined for effects indistinguishable from noise.

**The invariant is the claim that `C` carries information about controllership that
`M` does not.** Formally, for a labeled positive set *P* (known state regulators) and
a magnitude-**matched** negative set *N*:

> **CCI holds** ⇔ adding `C` to a magnitude-only model of `P-vs-N` membership yields a
> strictly positive conditional gain — significant conditional likelihood-ratio test
> AND bootstrap ΔAUPRC > 0 with high posterior mass — while `C` itself is
> approximately orthogonal to `M` (|Spearman(C, M)| small).

## 3. The null and the falsification criterion

The invariant is **falsifiable**. The null hypothesis is:

> **H₀:** conditional on magnitude, axis-specificity and reproducibility add nothing
> to regulator recovery — ΔAUPRC(magnitude → magnitude+C) = 0 and the conditional LR
> test is non-significant.

**CCI is falsified in a given system** if, with magnitude-matched negatives and a
credible regulator label set, the bootstrap ΔAUPRC 95% CI includes 0 **or** the
conditional LR test is non-significant. A system where H₀ holds is not a failure of
the method — it *defines the boundary of the property* and is reported as such.

Two guards against circularity (both mandatory):
1. **Leave-marker-out axes** — a regulator that is itself an axis-defining marker
   must be scored on an axis built *without* it, or the specificity is trivially self-fulfilling.
2. **Magnitude-matched negatives** — negatives must match positives on magnitude
   (and expression covariates), so the test cannot be won by magnitude leaking in.

## 4. Evidence in the anchoring system (Marson CD4+)

| Quantity | Value |
|---|---|
| Genes scored (detectable subset) | 1260 / 2520 |
| Known-regulator positives | 19 |
| Spearman(C, magnitude) | **+0.02** (orthogonal) |
| Authoritative pre-specified M→M+C | 0.539→0.896; **+0.357**, 95% CI [+0.117,+0.538], P(>0)=1.000 |
| Leakage-free OOF M→M+C | **+0.215**, 95% CI [+0.074,+0.560], permutation p=0.010 |
| Descriptive ranking-quality AUPRC | magnitude 0.415; orthogonal score **0.722** |
| Standardized matched C-vs-M aggregate | +0.229, 95% CI [0.072, 0.405], P(>0)=0.996 |
| Conditional LR test (specificity; coherence) | p < 1e-4; p < 1e-4 |
| Replication across culture conditions | Rest / Stim-8h / Stim-48h, all p < 1e-3 |
| Robustness | survives leave-marker-out; independent structural positives p=0.013 |

In the anchoring system the invariant **holds** and is orthogonal to magnitude.

## 5. Dataset-agnostic measurement protocol

To test CCI on **any** perturbation screen:

1. **Inputs (minimum):** a perturbation × gene effect matrix (log-FC or z-score),
   a replicate structure (≥2 donors/guides/replicates), one or more functional
   **state axes** (signed gene sets), and a **regulator label set** for that system.
2. **Harmonize gene space** to the measured genes; drop axes/labels with <3 measured members.
3. **Compute** `M`, `S(·,axis)`, `R` per perturbation; gate to the detectable subset (`M` ≥ median).
4. **Residualize** `S`, `R` on `M`; form `C`.
5. **Build magnitude-matched negatives** for the regulator positives (match on `M`
   + expression covariates, 5–8 per positive).
6. **Test:** conditional LR (`C` over `M`) and bootstrap ΔAUPRC(`M` → `M`+`C`).
7. **Verdict:** PASS if ΔAUPRC CI excludes 0 and LR significant; FAIL otherwise. Record
   the effect size regardless.

This protocol is implemented in the `isci-controllership` skill
(`expression_matched_negatives`, `conditional_lr_test`, `bootstrap_auprc_gain`,
`controllership_score`) and is what the generalization phase runs on each external dataset.

## 6. What would make CCI a genuine invariant

A property earns the name "invariant" only by holding across independent systems.
The generalization test therefore spans:

- **Near transfer (immune):** another immune Perturb-seq (e.g. T-cell CROP-seq,
  Perturb-CITE-seq) — same domain, independent lab/platform.
- **Far transfer (non-immune, decisive):** a genome-scale non-immune screen
  (e.g. K562 / RPE1) — if the same magnitude-conditional signal recovers known
  regulators in a completely different cell system, CCI is a property of
  perturbation biology, not of T cells.

The honest outcomes are three: (a) CCI holds broadly → a general invariant;
(b) CCI holds in immune systems but not elsewhere → a domain-scoped property;
(c) CCI is Marson-specific → a single-dataset finding. The generalization report
states which of these the data support.
