# Project pending register

**Snapshot:** 2026-07-12. **Scope:** current ISCI/CCI repository and the prospective donor-panel
path. This register distinguishes unfinished work from completed negative results. A `FAIL`,
`NULL`, `UNSUPPORTED` or `NOT-EVALUABLE` verdict is not automatically a pending task.

Priority definitions:

- **P0:** blocks the prospective experiment or a scientifically consistent public copy;
- **P1:** engineering/release debt that should close before a durable public release;
- **P2:** valuable scientific extension that does not block the current claim;
- **EXTERNAL:** needs a new runtime, wet-lab, controlled-access data or maintainer authorization.

## P0 — prospective guide and donor experiment

| ID | Pending point | Current evidence | Close condition | Dependency |
|---|---|---|---|---|
| OT-01 | Execute CRISPRitz S0 installation smoke test | Versioned EMX1, PAM and engine package are frozen; `execution_status=NOT_EXECUTED` | Two deterministic S0 runs with hashes and resource log | External Linux scratch |
| OT-02 | Execute S1 priority search for TNFRSF9/TBX21 | Ten candidates packaged: four current + six fallbacks | Two deterministic mismatch-only full-reference runs | OT-01 + `GCF_000001405.40` files |
| OT-03 | Derive versioned RefSeq annotation BED | Annotation release is selected but `BLOCKED_DERIVATION_NOT_EXECUTED` | BED conversion method, row-count checks and SHA-256 committed | NCBI annotation download |
| OT-04 | Execute S2 full 78-candidate search | Full input exists; engine remains unexecuted | Two deterministic reference-only runs and reviewed summary | OT-02 |
| OT-05 | Execute S3 bulge sensitivity | Parameters are frozen at 4 mismatches, 1 DNA and 1 RNA bulge | Indexed run completed twice; delta versus S2 reported | OT-04 + indexed genome |
| GD-01 | Resolve `PAPOLG-1` low source support | Only 1 exact read in 1 well; all other 53 guides source-confirmed | Independent authoritative sequence confirmation or frozen replacement | Source/library evidence |
| GD-02 | Review CRISPRa TSS placement and on-target suitability | Current sequence flags are structural only | Versioned TSS distance/on-target evidence per retained guide | OT-03 and final candidate set |
| GD-03 | Complete cloning/vector compatibility | No BsmBI flag is only a screen, not construct validation | Oligo adapters, U6 constraints and vector-specific QC reviewed | Final guide candidates |
| GD-04 | Freeze replacements before prospective outcomes | Zero automatic substitutions; TNFRSF9/TBX21 are highest priority | Independent review records final manifest and rationale before data inspection | OT-01–05, GD-01–03 |
| EXP-01 | Run donor-resolved prospective validation | Public reuse cannot confirm the context interaction; GSE190604 donors are mixed | At least four donor-resolved paired samples, frozen endpoints and guide-level support | Final synthesis-ready panel + wet-lab |
| EXP-02 | Adjudicate the context-interaction claim | Current target-paired estimate is directional but swap-null p=0.091 | Pre-specified donor-level interaction analysis and reproducibility gate | EXP-01 |

Primary artifacts: `config/off_target_pilot.yaml`, `reports/OFF_TARGET_PILOT_PROTOCOL.md`,
`outputs/decomposition_v2/off_target_pilot_contract.json`, and
`reports/DONOR_RESOLVED_CONTEXT_VALIDATION_PLAN.md`.

## P0 — scientific consistency before public copy

| ID | Pending point | Current evidence | Close condition | Dependency |
|---|---|---|---|---|
| DOC-01 | Harmonize the primary-number cascade | `result_lock.md` makes M→M+C `+0.357` authoritative; README/ledger/dashboard often headline the distinct `+0.229` aggregate | Every public surface labels `+0.357`, `0.415→0.722`, `+0.229` and OOF `+0.215` as different estimands | Frozen `result_lock.md`; no formula change |
| DOC-02 | Synchronize roadmap statuses | `MASTER_ROADMAP.md` still calls several completed phases “HERE” | Roadmap points to this live register and completed phases match the claim ledger | Current committed artifacts |
| DOC-03 | Re-run claim/overclaim audit after synchronization | Current claim ledger is strong but predates the guide-pilot state and contains a stale preregistration sentence | README, paper, demo, ledger and dashboard agree on claims and boundaries | DOC-01/02 |

## P1 — reproducibility, quality and release

| ID | Pending point | Current evidence | Close condition | Dependency |
|---|---|---|---|---|
| ENG-01 | Make the reproduction claim exactly match the driver | `make reproduce-core` recomputes Marson from committed summaries and aggregates other heavy runs; it is not raw-data end-to-end for every dataset | README and pipeline report explicitly distinguish recompute, aggregate and unavailable-raw lanes; canonical outputs carry provenance | No scientific change |
| ENG-02 | Add provenance to every canonical CCI result | Canonical schema in `run_cci.py` omits data/config hashes while README says every output is stamped | Schema and dashboard accept provenance without changing verdicts | ENG-01 |
| ENG-03 | Pay down global lint debt | `ruff check .` currently reports 163 historical errors; touched guide-pilot files are clean | Scoped cleanup commits bring repository lint to zero or define explicit excludes | Separate engineering PRs |
| ENG-04 | Reduce test warning debt | Full suite passes but emits sklearn/scipy and pytest-asyncio deprecation warnings | Own warnings fixed or pinned/documented; third-party warnings explicitly bounded | Dependency review |
| REL-01 | Validate public package and links | MIT license and self-contained demo exist; the working branch is ahead of `origin/main` and has no remote head | Fresh clone reproduces documented smoke path; links and large-file boundary pass | DOC-01–03, ENG-01/02 |
| REL-02 | Push/merge the working branch | `codex/controllability-decomposition` has no remote head | Reviewable branch/PR exists and CI passes | User authorization; do not publish implicitly |
| REL-03 | Mint immutable release/DOI | Pre-registration records git SHA but no project release DOI | Tagged release archived by Zenodo; badges and ledger updated | Repository-owner GitHub/Zenodo authorization |

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
- curated mechanism enrichment, targetability board and signed perturbation graph: completed
  exploratory overlays;
- TCR RescueMap: a separate Paper-2/multi-year program, not unfinished work required to close this
  repository.

## Recommended execution order

1. Run OT-01 and OT-02 on disposable Linux scratch.
2. In parallel, close DOC-01 so the public scientific story uses the locked estimand hierarchy.
3. Derive the annotation BED (OT-03), then run OT-04 and OT-05.
4. Close PAPOLG/TSS/vector review and freeze the final guide manifest.
5. Perform a fresh-clone release rehearsal, then open a reviewable branch/PR.
6. Start EXP-01 only after guide promotion is frozen; treat SCI-01–08 as independent extensions.
