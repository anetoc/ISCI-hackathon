# Project pending register

**Snapshot:** 2026-07-14 after immutable release closeout. **Scope:** current T-CTRL/ISCI repository and
the prospective donor-panel path. This register distinguishes unfinished work from completed negative results. A `FAIL`,
`NULL`, `UNSUPPORTED` or `NOT-EVALUABLE` verdict is not automatically a pending task.

Priority definitions:

- **P0:** blocks the prospective experiment or a currently validated scientific release;
- **P1:** engineering/release debt that should close before a durable public release;
- **P2:** valuable scientific extension that does not block the current claim;
- **EXTERNAL:** needs a new runtime, wet-lab, controlled-access data or maintainer authorization.

## P0 — prospective guide and donor experiment

| ID | Pending point | Current evidence | Close condition | Dependency |
|---|---|---|---|---|
| OT-02 | Execute S1 priority search for TNFRSF9/TBX21 | S0 passed; ten candidates are packaged: four current + six fallbacks | Two deterministic mismatch-only full-reference runs | `GCF_000001405.40` files |
| OT-03 | Derive versioned RefSeq annotation BED | Annotation release is selected but `BLOCKED_DERIVATION_NOT_EXECUTED` | BED conversion method, row-count checks and SHA-256 committed | NCBI annotation download |
| OT-04 | Execute S2 full 78-candidate search | Full input exists; engine remains unexecuted | Two deterministic reference-only runs and reviewed summary | OT-02 |
| OT-05 | Execute S3 bulge sensitivity | Parameters are frozen at 4 mismatches, 1 DNA and 1 RNA bulge | Indexed run completed twice; delta versus S2 reported | OT-04 + indexed genome |
| GD-01 | Resolve `PAPOLG-1` low source support | Only 1 exact read in 1 well; all other 53 guides source-confirmed | Independent authoritative sequence confirmation or frozen replacement | Source/library evidence |
| GD-02 | Review CRISPRa TSS placement and on-target suitability | Current sequence flags are structural only | Versioned TSS distance/on-target evidence per retained guide | OT-03 and final candidate set |
| GD-03 | Complete cloning/vector compatibility | No BsmBI flag is only a screen, not construct validation | Oligo adapters, U6 constraints and vector-specific QC reviewed | Final guide candidates |
| GD-04 | Freeze replacements before prospective outcomes | Zero automatic substitutions; TNFRSF9/TBX21 are highest priority | Independent review records final manifest and rationale before data inspection | OT-02–05, GD-01–03 |
| EXP-01 | Run donor-resolved prospective validation | Public reuse cannot confirm the context interaction; GSE190604 donors are mixed | At least four donor-resolved paired samples, frozen endpoints and guide-level support | Final synthesis-ready panel + wet-lab |
| EXP-02 | Adjudicate the context-interaction claim | Current target-paired estimate is directional but swap-null p=0.091 | Pre-specified donor-level interaction analysis and reproducibility gate | EXP-01 |

Primary artifacts: `config/off_target_pilot.yaml`, `reports/OFF_TARGET_PILOT_PROTOCOL.md`,
`outputs/decomposition_v2/off_target_pilot_contract.json`, and
`reports/DONOR_RESOLVED_CONTEXT_VALIDATION_PLAN.md`.

## Hackathon submission — completed

The Researcher Track project was submitted with the following public artifacts:

- repository: https://github.com/anetoc/ISCI-hackathon;
- interactive demo: https://anetoc.github.io/ISCI-hackathon/;
- narrated video: https://youtu.be/7Rz4PpmQZuI.

This status is author-confirmed. The private platform receipt and internal recording, rehearsal and
form-production notes are intentionally not committed to the public research repository.

## P1 — reproducibility, quality and release

No P1 release blocker remains. The immutable `v0.1.0` release is public and archived at
<https://doi.org/10.5281/zenodo.21348207>.

## P2 — scientific extensions, not blockers

| ID | Pending point | Why it matters | Close condition | Dependency |
|---|---|---|---|---|
| SCI-01 | Well-powered CD8/CAR-T perturbation replication (preregistered B2) | Tests whether axis-specificity transports beyond CD4+ | Frozen CCI protocol on a qualifying replicated dataset | Suitable public or prospective dataset |
| SCI-02 | Paired perturbation-to-function test (preregistered B3) | Directly tests killing/synapse function beyond transcription and CD8 identity | Held-out functional endpoint beats both required baselines | Controlled-access dbGaP or wet-lab |
| SCI-03 | Foundation-model triangulation | scGPT test is `NOT-EVALUABLE`, not a null | Obtain 44.6 GB pseudobulk + 16.8 GB DE data and run locked matched-negative test | External storage/compute |
| SCI-04 | Phospho-signaling validation | TCR control is fundamentally post-translational | Pre-specified pLCK/pZAP70/pLAT/pERK/pS6 time-course analysis | Public phospho dataset or wet-lab |
| SCI-05 | Spatial/niche localization | Localizes product-visible sensitivity versus post-infusion resistance | Compartment-aware spatial analysis with tumor–immune interfaces | Suitable spatial cohort |
| SCI-06 | Variant-aware off-target sensitivity | Reference-only enumeration misses population variants | Versioned variant panel and delta report, kept separate from primary search | OT-04/05 |
| SCI-07 | Independent off-target engine comparison | Detects engine-specific enumeration artifacts | Cas-OFFinder mismatch-only comparison on OpenCL-compatible host | Optional external runtime |
| SCI-08 | Formal cross-system heterogeneity test | Current scope map compares CIs but is not a formal invariant test | Pre-specified hierarchical/heterogeneity analysis across qualifying systems | More powered immune systems |

## Completed outcomes that must not be reopened as “pending”

- clinical CAR-T response prediction: completed, well-powered `NULL`;
- protein-layer magnitude-conditional CCI: completed `FAIL`;
- independent broad functional-regulator positive set: completed `FAIL`;
- exhaustion-like and CD4-CTL topology-conditional axes: completed `UNSUPPORTED`;
- stimulated GSE190604 Th2 replication: completed primary `FAIL`, with no-stim
  `REPLICATED-EXPLORATORY` only;
- myeloid B1 preregistered test: completed `NEAR-MISS`, not a PASS;
- primary-number cascade: synchronized and test-guarded as authoritative M→M+C `+0.357`, OOF
  `+0.215`, descriptive `0.415→0.722` and matched cross-system aggregate `+0.229`;
- curated mechanism enrichment, targetability board and signed perturbation graph: completed
  exploratory overlays;
- reproducibility wording: README and dossier now distinguish recomputed Marson summaries,
  aggregated heavy lanes and unavailable raw-data reruns;
- public release: PR #3 merged into `main`; repository, MIT license, CI and GitHub Pages are public;
- immutable archive: GitHub Release `v0.1.0` and Zenodo version DOI
  `10.5281/zenodo.21348207` published; concept DOI `10.5281/zenodo.21348206` reserved for the
  project across future versions;
- canonical legacy CCI provenance: completed; every result emitted by `run_cci.py` now carries Git,
  data, axes and config hashes, timestamp and command, with dashboard schema enforcement;
- roadmap synchronization, final automated overclaim audit and public submission: completed;
- repository-wide lint: completed; `ruff check .` passes, with explicit exclusions only for the
  immutable failed-D0 archive and the notebook's required local-import bootstrap;
- CRISPRitz S0 installation smoke: completed `PASS` in Actions run `29296855125`; both executions
  returned seven identical canonical target rows with empty stderr, while the biological verdict
  remains `NOT_ISSUED` because no project guide was tested;
- test warning debt: `152 passed` locally without emitted warnings on Python 3.13;
- TCR RescueMap: a separate Paper-2/multi-year program, not unfinished work required to close this
  repository.

## Recommended execution order

1. Run OT-02 on disposable Linux scratch using the frozen full reference.
2. Derive the annotation BED (OT-03), then run OT-04 and OT-05.
3. Close PAPOLG/TSS/vector review and freeze the final guide manifest.
4. Start EXP-01 only after guide promotion is frozen; treat SCI-01–08 as independent extensions.
