# Controllability Profile v2 — scientific result

**Status:** exploratory evolutionary analysis  
**Authorization:** formula, axes and gates reopened by PI on 2026-07-12  
**Boundary:** v1 remains an auditable baseline; v2 is not yet independent replication

## What changed

The project no longer treats controllability as a universal scalar. The v2 object is a profile:

1. effect reach;
2. precision conditional on reach, separately for every functional axis;
3. repeatability conditional on reach;
4. context-transport evidence for each component;
5. Pareto status and a descriptive archetype.

There is deliberately no `ISCI_v2_score`. A gene can be precise with modest reach, broadly moving
but imprecise, or highly repeatable without controlling the supported axis. Those distinctions are
scientific results, not noise to average away.

## Condition transport: the new strongest result

The Marson h5ad was reconstructed into 1,236 genes observed in Rest, Stim8hr and Stim48hr. This is
98.1% of the v1 detectable population and includes all 13 benchmark positives. For each held-out
condition, residualization, scaling and model fitting used only the other two conditions. Positive
identity was permuted within the same matched blocks across all three conditions.

| component | mean ΔAUPRC | 95% block CI | permutation p | BH q | condition gains (Rest / Stim8 / Stim48) | verdict |
|---|---:|---:|---:|---:|---:|---|
| **Th2 precision** | **+0.174** | **[+0.091,+0.364]** | **0.0020** | **0.016** | +0.112 / +0.254 / +0.155 | **SUPPORTED_EXPLORATORY** |
| Th1 precision | +0.101 | [+0.029,+0.254] | 0.0280 | 0.112 | +0.081 / +0.140 / +0.082 | DIRECTIONAL_UNCERTAIN |
| Repeatability | +0.069 | [−0.024,+0.207] | 0.0859 | 0.229 | +0.136 / +0.041 / +0.032 | DIRECTIONAL_UNCERTAIN |
| Exhaustion-like precision | +0.048 | [−0.040,+0.211] | 0.133 | 0.266 | all positive | DIRECTIONAL_UNCERTAIN |
| CD4-CTL precision | +0.046 | [−0.028,+0.190] | 0.197 | 0.315 | all positive | DIRECTIONAL_UNCERTAIN |
| TCR activation precision | +0.021 | [−0.010,+0.098] | 0.270 | 0.360 | Stim8 slightly negative | CONTEXT_DEPENDENT |
| Memory stem-like precision | −0.002 | [−0.045,+0.038] | 0.625 | 0.625 | mixed | UNSUPPORTED |
| Treg precision | −0.003 | [−0.051,+0.082] | 0.566 | 0.625 | mixed | UNSUPPORTED |

Th2 is now supported by two different stress surfaces: it beats topology/expression-matched
pseudo-axes in T1 and transports across all three experimental conditions in T4 v2. This supports
an axis-conditioned property, not universal controllability. It remains exploratory because axis,
labels and conditions come from the same screen and share biological ontology.

## External targeted-panel replication: condition-specific result

The frozen GSE190604 analysis tested 69 CRISPRa targets (23 positive, 46 negative) in primary human
T cells. Raw counts were pseudobulked by target×well, effects used well-matched NO-TARGET controls,
and every outcome was evaluated with repeated out-of-fold fitting plus expression/cell-count overlap
weights. The four hypotheses used 1,000 gene bootstraps and 1,000 full nested label permutations.

| test | Δ weighted AUPRC | 95% bootstrap CI | permutation p | BH q | verdict |
|---|---:|---:|---:|---:|---|
| **Stimulated Th2 precision (primary)** | **+0.003** | **[−0.096,+0.099]** | **0.396** | **0.396** | **DIRECTIONAL_UNCERTAIN** |
| No-stim Th2 precision | +0.193 | [+0.057,+0.361] | 0.0070 | 0.028 | REPLICATED_EXPLORATORY |
| Stimulated Th1 precision | +0.128 | [−0.0001,+0.253] | 0.036 | 0.072 | DIRECTIONAL_UNCERTAIN |
| Stimulated repeatability | +0.059 | [−0.050,+0.194] | 0.090 | 0.120 | DIRECTIONAL_UNCERTAIN |

The primary prediction did not replicate: under stimulation, Th2 precision added essentially no
held-out label information beyond effect reach. The no-stim secondary passed its uncertainty and
multiplicity gates, providing external targeted-panel support for a **context-dependent** Th2
signal. It does not rescue the primary endpoint. Signed projections were retained as diagnostics,
but this CRISPRa-only panel cannot establish that higher absolute precision moves cells toward a
desirable state. The dataset is external to Marson but was a previously inspected targeted panel,
so this is not treated as untouched prospective replication.

### Target-paired interaction follow-up

The same 69 genes were then compared across contexts using a separately frozen, explicitly
post-result protocol. The paired interaction statistic was ΔAUPRC_no-stim − ΔAUPRC_stim = **+0.190**.
Its stratified paired-gene bootstrap interval excluded zero ([+0.046,+0.370]; 99.8% of bootstrap
contrasts positive), but the full within-gene context-exchange null did not cross the pre-specified
gate (p=0.091; null median +0.010). The verdict is **DIRECTIONAL_UNCERTAIN**.

Thus the observed contrast is stable to resampling this target panel but is not yet rare enough
under context exchange. This increases the priority of a paired context experiment; it does not
establish a stimulation interaction. The original experiment used the same two blood donors across
conditions, mixed 1:1 before droplet loading, but the processed matrix has no donor identity. The
available analysis is therefore target-paired and donor-mixed, not donor-resolved.

## Topology-conditional null: resolving the previously non-evaluable axes

The original rejection sampler could not generate enough correlation-matched alternatives for
exhaustion-like or CD4-CTL. V2 separates ruler-topology rarity from controller-label recovery. A
constrained four-chain sampler excluded the real marker genes, preserved expression-decile counts
and sampled only within ±20% of the real mean absolute correlation.

| axis | topology vs 10,000 expression-matched sets | conditional samples | ESS / R-hat | real gain vs conditional null | p | verdict |
|---|---:|---:|---:|---:|---:|---|
| Exhaustion-like | percentile 100%; p<10⁻⁴ | 200/200 | 193 / 0.990 | +0.029 vs median −0.002 | 0.209 | UNSUPPORTED |
| CD4-CTL | percentile 100%; p<10⁻⁴ | 200/200 | 189 / 1.022 | +0.035 vs median +0.037 | 0.522 | UNSUPPORTED |

Both rulers are topologically exceptional: their genes are far more coexpressed than random
expression-matched sets. But once the null is conditioned on that exceptional topology, neither
ruler recovers benchmark controllers beyond comparable rulers. This is an important negative
result: **a biologically coherent marker set is not automatically a controller-discriminating
ruler**. The axes are now evaluable; their controller-recovery verdict is unsupported rather than
unknown.

## Non-scalar controller landscape

The profile contains 1,236 genes and 66 non-dominated genes on the three-dimensional Pareto front:
reach, Th2 precision conditional on reach, and repeatability conditional on reach.

| archetype | n | interpretation |
|---|---:|---|
| robust axis controller | 24 | high reach, high Th2 precision and high repeatability |
| precise + repeatable, lower reach | 61 | clean reproducible direction but not a broad perturbation |
| precise context controller | 225 | Th2-aligned, but reach or repeatability is limited |
| repeatable broad mover | 43 | strong/reproducible, but not Th2-specific |
| high-reach mover | 185 | large effect without sufficient conditional evidence |
| repeatable, low precision | 182 | stable effect on another or diffuse program |
| unresolved | 516 | no high component under the descriptive 75th-percentile cuts |

Known regulators occupy different regions, validating the need for profiles: GATA3 is a robust-axis
controller; IRF1, STAT6 and TBX21 are precise and repeatable with lower relative reach; ICOS and
PTPN2 are precise but less repeatable. Among non-benchmark genes, HEXIM1 is robust; IKBKB and ECSIT
are precise/repeatable with lower reach; BCLAF1 is maximally repeatable but has lower Th2 precision.
These are mechanistic phenotypes, not therapeutic recommendations.

## What we should claim now

> In the Marson CD4 perturbation screen, controller identity is better represented as an
> axis-specific profile than as one universal score. Th2-aligned precision adds information beyond
> effect reach, survives matched pseudo-axis stress testing, and transports across Rest, Stim8hr and
> Stim48hr under leakage-safe training. In an external targeted CRISPRa panel, this signal replicated
> only without stimulation; the stimulated primary endpoint was null-like. Other axes and contexts
> therefore retain distinct evidence states.

Do not claim statistical factorization, universal controllability, context-invariant replication,
clinical response prediction, therapeutic direction or therapeutic desirability.

## Highest-value next experiments

1. **Recover donor resolution:** the target-paired diagnostic was directional but missed its
   swap-null gate (p=0.091). Assess genotype-based demultiplexing from raw GSE190604 reads, then fit
   a donor-clustered context×precision interaction. Do not treat well number as donor identity.
2. **Independent Th2 replication:** freeze labels and overlap/matching rules before an untouched,
   broader polarization perturbation dataset; GSE190604 was targeted and previously inspected.
3. **Signed control:** separate direction from precision using KD/CRISPRa pairs or a signed rescue
   assay; absolute alignment cannot distinguish pushing toward from away from a state.
4. **Archetype panel:** validate 3–4 genes per profile class, not only the top scalar rank. Measure
   state-axis movement, donor reproducibility and on-target effect separately.

## Reproducibility

- features: `python scripts/build_marson_condition_features.py`
- condition transport: `python scripts/run_t4_condition_transport_v2.py --n-resamples 1000`
- profile: `python scripts/build_controllability_profile_v2.py`
- topology null: `python scripts/run_topology_null_v2.py --n-samples 200 --n-random 10000`
- external features: `python scripts/build_gse190604_features.py`
- external replication: `python scripts/run_gse190604_replication.py --n-resamples 1000 --n-repeats 10`
- paired context diagnostic: `python scripts/run_gse190604_context_interaction.py --n-resamples 1000 --n-repeats 10`
- figure: `python scripts/plot_controllability_profile_v2.py`
- machine-readable artifacts: `outputs/decomposition_v2/`

All tables carry code/data/axis hashes, command and timestamp. Only public perturbation statistics
were used; no PHI or raw clinical text entered the analysis.
