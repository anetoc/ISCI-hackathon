# ADR-001: Use T-CTRL as the public name and ISCI as the scientific method

## Status

Accepted

## Date

2026-07-12

## Context

The repository, Python package, CLI, frozen result, evidence tables and scientific reports were
built under the name ISCI (Immune-State Controllability Index). ISCI is precise inside the project,
but it is an opaque acronym for an asynchronous hackathon judge who must understand the biological
question within minutes.

The existing interactive decision map already uses T-CTRL. That name communicates the subject
(T cells) and the scientific question (control) without requiring the audience to learn the method
before understanding the value.

Renaming the Python package, CLI, repository and frozen artifacts immediately before submission
would create broken links, provenance drift and unnecessary release risk.

## Decision

Use a two-layer naming architecture:

- **T-CTRL** is the public, judge-facing experience and narrative.
- **ISCI (Immune-State Controllability Index)** remains the scientific method, Python package,
  command-line interface and provenance namespace behind T-CTRL.
- Keep the repository name `ISCI-hackathon` through submission so existing links and evidence
  remain stable.
- Introduce both names together on every high-level public surface: “T-CTRL, powered by ISCI.”
- Do not introduce CCI, IEC, T-REMAP or TSC as additional brands in judge-stage copy. Describe
  their evidence function in plain language and retain the original terminology only in technical
  reports, filenames and stable scientific identifiers.
- Do not reinterpret or rename frozen scientific metrics. Columns such as `ISCI_orthogonal` retain
  their existing names.

## Alternatives considered

### Keep ISCI as the only public name

- Advantage: no terminology transition.
- Rejected: the acronym does not explain the biological question to a mixed scientific audience.

### Rename everything to T-CTRL

- Advantage: a single memorable name everywhere.
- Rejected for the hackathon release: package, CLI, figures, manifests and result locks would need a
  high-risk migration with no scientific benefit.

### Lead with CCI

- Advantage: names the Conditional Controllability Invariant directly.
- Rejected: CCI is a tested scientific property and cross-system extension, not the complete product
  or workflow.

## Consequences

- Judges encounter a clear biological promise before technical vocabulary.
- Scientists retain stable code, metric and provenance identifiers.
- Judges need to learn one product name and one method name; the evidence archive can remain
  historically complete without becoming part of the presentation vocabulary.
- Some surfaces legitimately show both names; this is an intentional product/method distinction,
  not a partial rename.
- A post-hackathon package or repository rename can be evaluated separately, with redirects and a
  migration plan.
