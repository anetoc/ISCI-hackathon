#!/usr/bin/env python
"""Resolve prospective-panel guide IDs from public Calabrese and guide-read evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from isci.guide_sequence_validation import (  # noqa: E402
    build_calabrese_candidates,
    extract_guide_sequence_evidence,
    resolve_guide_sequences,
)

DEFAULT_PANEL = ROOT / "outputs/decomposition_v2/prospective_donor_panel.csv"
DEFAULT_GUIDECALLS = ROOT / "data/external/gse190604/guidecalls.txt.gz"
DEFAULT_AXES = ROOT / "config/axes.yaml"
DEFAULT_CANDIDATES = ROOT / "outputs/decomposition_v2/gse190604_calabrese_panel_candidates.csv"
DEFAULT_EVIDENCE = ROOT / "outputs/decomposition_v2/gse190604_guide_sequence_evidence.csv"
DEFAULT_MANIFEST = ROOT / "outputs/decomposition_v2/prospective_donor_panel_sequences.csv"
DEFAULT_SUMMARY = ROOT / "outputs/decomposition_v2/prospective_donor_panel_sequences.json"
ZENODO_ARCHIVE_URL = (
    "https://zenodo.org/api/records/5784651/files/Genome-wide-screens.zip/content"
)
ENA_FASTQ_PREFIX = "https://ftp.sra.ebi.ac.uk/vol1/fastq"
SOURCE_BYTE_RANGE = "bytes=0-10485759"


def sha256(path: Path) -> str:
    """Hash source artifacts in bounded chunks."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decompress_gzip_prefix(source: Path, output: Path) -> None:
    """Decompress a deliberately truncated gzip prefix without requiring its final footer."""

    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    with source.open("rb") as compressed, output.open("wb") as decompressed:
        for chunk in iter(lambda: compressed.read(1024 * 1024), b""):
            decompressed.write(decompressor.decompress(chunk))


def ena_run_url(accession: str, mate: int) -> str:
    """Construct the ENA HTTPS path for the public SRR guide FASTQ."""

    stem = accession[:6]
    suffix = accession[-3:]
    return f"{ENA_FASTQ_PREFIX}/{stem}/{suffix}/{accession}/{accession}_{mate}.fastq.gz"


def add_provenance(table: pd.DataFrame, provenance: dict[str, str]) -> pd.DataFrame:
    """Attach the required artifact contract to every generated result table."""

    result = table.copy()
    for key, value in provenance.items():
        result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--guidecalls", type=Path, default=DEFAULT_GUIDECALLS)
    parser.add_argument("--axes", type=Path, default=DEFAULT_AXES)
    parser.add_argument("--screen-il2", type=Path, required=True)
    parser.add_argument("--screen-ifng", type=Path, required=True)
    parser.add_argument(
        "--run",
        action="append",
        nargs=4,
        metavar=("WELL", "ACCESSION", "R1_GZIP_PREFIX", "R2_GZIP_PREFIX"),
        required=True,
        help="repeat for each public guide run prefix",
    )
    parser.add_argument("--candidates-output", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--evidence-output", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--min-exact-reads", type=int, default=10)
    parser.add_argument("--min-support-wells", type=int, default=2)
    args = parser.parse_args()

    run_specs: list[tuple[int, str, Path, Path]] = []
    for well_text, accession, read1_text, read2_text in args.run:
        run_specs.append((int(well_text), accession, Path(read1_text), Path(read2_text)))
    wells = [well for well, *_ in run_specs]
    if len(wells) != len(set(wells)):
        raise SystemExit("each well may be specified only once")
    required = [
        args.panel,
        args.guidecalls,
        args.axes,
        args.screen_il2,
        args.screen_ifng,
        *[path for _, _, read1, read2 in run_specs for path in (read1, read2)],
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"missing sequence-resolution inputs: {missing}")

    panel = pd.read_csv(args.panel)
    guidecalls = pd.read_csv(args.guidecalls, sep="\t")
    panel_targets = set(panel["target"].astype(str))
    screen_tables = {
        "IL2": pd.read_csv(args.screen_il2, sep="\t"),
        "IFNG": pd.read_csv(args.screen_ifng, sep="\t"),
    }
    candidates = build_calabrese_candidates(screen_tables, panel_targets)
    source_hashes = {
        "IL2": sha256(args.screen_il2),
        "IFNG": sha256(args.screen_ifng),
    }
    source_members = {
        "IL2": "Genome-wide-screens/data/sgRNA_summaries/CRISPRa.IL2.sgrna_summary.txt",
        "IFNG": "Genome-wide-screens/data/sgRNA_summaries/CRISPRa.IFNG.sgrna_summary.txt",
    }
    candidates["source_archive_url"] = ZENODO_ARCHIVE_URL
    candidates["source_member"] = candidates["screen"].map(source_members)
    candidates["source_member_sha256"] = candidates["screen"].map(source_hashes)

    evidence_tables = []
    run_metrics = []
    with tempfile.TemporaryDirectory(prefix="gse190604-guide-resolution-") as temporary:
        temporary_root = Path(temporary)
        for well, accession, read1_prefix, read2_prefix in run_specs:
            read1 = temporary_root / f"{accession}_1.fastq"
            read2 = temporary_root / f"{accession}_2.fastq"
            decompress_gzip_prefix(read1_prefix, read1)
            decompress_gzip_prefix(read2_prefix, read2)
            evidence, metrics = extract_guide_sequence_evidence(
                guidecalls,
                candidates,
                read1_path=read1,
                read2_path=read2,
                well=well,
                panel_guide_ids=set(panel["guide_id"].astype(str)),
            )
            evidence["run_accession"] = accession
            evidence["source_byte_range"] = SOURCE_BYTE_RANGE
            evidence["read1_source_url"] = ena_run_url(accession, 1)
            evidence["read2_source_url"] = ena_run_url(accession, 2)
            evidence["read1_prefix_sha256"] = sha256(read1_prefix)
            evidence["read2_prefix_sha256"] = sha256(read2_prefix)
            evidence_tables.append(evidence)
            run_metrics.append(
                {
                    "well": well,
                    "run_accession": accession,
                    **metrics,
                    "read1_prefix_bytes": read1_prefix.stat().st_size,
                    "read2_prefix_bytes": read2_prefix.stat().st_size,
                    "read1_prefix_sha256": sha256(read1_prefix),
                    "read2_prefix_sha256": sha256(read2_prefix),
                }
            )
    evidence = pd.concat(evidence_tables, ignore_index=True)

    # Keep the original panel artifact contract under explicit names before attaching the new one.
    panel_provenance = {
        column: f"panel_{column}"
        for column in [
            "git_sha",
            "data_sha256",
            "axes_sha256",
            "timestamp",
            "command",
            "method_version",
        ]
        if column in panel.columns
    }
    resolved = resolve_guide_sequences(
        panel.rename(columns=panel_provenance),
        evidence,
        candidates,
        min_exact_reads=args.min_exact_reads,
        min_support_wells=args.min_support_wells,
    )

    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    timestamp = datetime.now().astimezone().isoformat()
    input_hashes = {
        str(path.resolve().relative_to(ROOT)) if path.resolve().is_relative_to(ROOT) else path.name: sha256(path)
        for path in required
    }
    # Tables carry one compact digest; the JSON summary retains the complete per-input mapping.
    input_hash_manifest = json.dumps(input_hashes, sort_keys=True)
    provenance = {
        "git_sha": git_sha,
        "data_sha256": hashlib.sha256(input_hash_manifest.encode()).hexdigest(),
        "axes_sha256": sha256(args.axes),
        "timestamp": timestamp,
        "command": shlex.join(["python", *sys.argv]),
        "method_version": "gse190604_guide_sequence_resolution_v1",
    }
    candidates = add_provenance(candidates, provenance)
    evidence = add_provenance(evidence, provenance)
    resolved = add_provenance(resolved, provenance)

    status_counts = resolved["source_identity_status"].value_counts().to_dict()
    synthesis_counts = resolved["synthesis_status"].value_counts().to_dict()
    duplicate_sequences = (
        resolved.loc[resolved["protospacer_20nt"].ne(""), "protospacer_20nt"]
        .value_counts()
        .loc[lambda values: values > 1]
        .to_dict()
    )
    payload = {
        "status": "SOURCE_IDENTITIES_RESOLVED_SYNTHESIS_BLOCKED",
        "panel": {
            "n_guides": int(resolved["guide_id"].nunique()),
            "source_identity_status_counts": status_counts,
            "synthesis_status_counts": synthesis_counts,
            "low_support_guides": resolved.loc[
                resolved["source_identity_status"] == "SOURCE_IDENTITY_LOW_SUPPORT", "guide_id"
            ].tolist(),
            "ambiguous_guides": resolved.loc[
                resolved["source_identity_status"] == "SOURCE_IDENTITY_AMBIGUOUS", "guide_id"
            ].tolist(),
            "unresolved_guides": resolved.loc[
                resolved["source_identity_status"] == "SOURCE_IDENTITY_UNRESOLVED", "guide_id"
            ].tolist(),
            "duplicate_protospacers": duplicate_sequences,
        },
        "evidence": {
            "screen_source": "Zenodo record 5784651 Calabrese CRISPRa MAGeCK summaries",
            "guide_source": "ENA public GSE190604 guide FASTQ prefixes",
            "source_byte_range_per_fastq": SOURCE_BYTE_RANGE,
            "run_metrics": run_metrics,
            "barcode_transform": "complement one-based bases 8 and 9, then exact match",
            "cell_level_data_committed": False,
        },
        "resolution_thresholds": {
            "min_exact_reads": args.min_exact_reads,
            "min_support_wells": args.min_support_wells,
            "source_identity_is_not_synthesis_approval": True,
        },
        "remaining_gates": [
            "targeted confirmation for low-support source identities",
            "confirm pZR158/direct-capture vector and cloning compatibility",
            "select current human reference build and target transcript/TSS",
            "run sequence-specific on-target and off-target assessment",
            "independent review before oligo ordering",
        ],
        "input_sha256": input_hashes,
        "provenance": provenance,
    }

    for path in [
        args.candidates_output,
        args.evidence_output,
        args.manifest_output,
        args.summary_output,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(args.candidates_output, index=False)
    evidence.to_csv(args.evidence_output, index=False)
    resolved.to_csv(args.manifest_output, index=False)
    args.summary_output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
