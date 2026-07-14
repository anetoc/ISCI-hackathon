# CRISPRitz S0 installation-smoke result

**Verdict:** `PASS` for the installation control only. **Biological verdict:** `NOT_ISSUED`.
No project guide was assessed, replaced or approved for synthesis.

## What was tested

The official EMX1 control was searched twice against the UCSC hg38 chromosome-22 fixture with the
frozen SpCas9/NGG, mismatch-only, four-mismatch contract. Execution used CRISPRitz `2.7.0`,
Bioconda build `py39h2de1943_0`, package SHA-256
`88aa3073a76f8b74b2a869ecf921c59241cf19267df877bafc285b8620cfc215`.

GitHub Actions run [`29296855125`](https://github.com/anetoc/ISCI-hackathon/actions/runs/29296855125)
passed on Linux at commit `813fb0ae57b3f5faa516d2e3f16e0ff30d1c2e2e`.

## Acceptance evidence

- both engine invocations returned exit code `0`;
- both stderr streams were empty;
- all required target, profile and extended-profile files were non-empty;
- both runs contained seven canonical target rows;
- canonical target-row SHA-256 was identical across runs:
  `39b8b3d08f62298ec67d16964f94dc4ab50f1e98d8f66f902bdece110b2a2f75`;
- peak resident memory was `1,110,436` and `1,108,508` KiB;
- package, reference, inputs, outputs, commands, timestamp and Git revision are recorded.

Raw target-file hashes differ because CRISPRitz emitted the same rows in a different order. This is
the reason the preregistered gate compares canonical sorted rows without deduplicating them.

## Audited compatibility remediation

The exact Python 3.9 package contains 14 unversioned Azimuth bytecode caches compiled for an older
interpreter and does not cap NumPy before removal of `np.float`. The workflow therefore removes only
those incompatible caches and pins NumPy `1.23.5` and setuptools `70.3.0`. It does not modify source
files, models, binaries, inputs or scientific parameters. The intervention and the complete resolved
environment are committed with the result.

## Evidence files

- machine-readable verdict: `outputs/decomposition_v2/off_target_s0/s0_execution_report.json`;
- complete resolved environment: `outputs/decomposition_v2/off_target_s0/environment-explicit.txt`;
- raw engine outputs and resource logs: `outputs/decomposition_v2/off_target_s0/runs/`;
- runtime-remediation record and removed-cache hashes:
  `outputs/decomposition_v2/off_target_s0/runtime-remediation.json` and
  `outputs/decomposition_v2/off_target_s0/removed-legacy-pyc-sha256.txt`.

## Next boundary

S0 establishes that the pinned command surface works reproducibly. The next scientific-engineering
gate is S1: two full-reference, mismatch-only searches of all current and fallback candidates for
`TNFRSF9` and `TBX21` against `GCF_000001405.40`. Until S1 and the later review gates pass, no
sequence-specific off-target conclusion is available for the project guides.
