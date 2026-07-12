#!/usr/bin/env python
"""Audit the public GSE190604 metadata before downloading its 1 GB count matrix."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/external/gse190604"
OUTPUT = ROOT / "outputs/decomposition_v2/gse190604_intake.json"
MATRIX_COMPRESSED_BYTES = 996_264_242


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_count(path: Path) -> int:
    with gzip.open(path, "rt") as handle:
        return sum(1 for _ in handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=DATA)
    args = parser.parse_args()
    paths = {
        "barcodes": args.source_dir / "barcodes.tsv.gz",
        "features": args.source_dir / "features.tsv.gz",
        "guidecalls": args.source_dir / "guidecalls.txt.gz",
    }
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        raise SystemExit(f"missing metadata files: {missing}")

    with gzip.open(paths["barcodes"], "rt") as handle:
        barcodes = [line.strip() for line in handle]
    suffixes = pd.Series([barcode.rsplit("-", 1)[-1] for barcode in barcodes])
    guides = pd.read_csv(paths["guidecalls"], sep="\t")
    singleton = guides[~guides["feature_call"].str.contains("|", regex=False)].copy()
    singleton["target"] = singleton["feature_call"].str.replace(r"-\d+$", "", regex=True)
    target_counts = singleton["target"].value_counts()
    free_bytes = shutil.disk_usage(ROOT).free
    payload = {
        "dataset": "GSE190604 Schmidt primary T-cell CRISPRa Perturb-seq",
        "source": "NCBI GEO GSE190604",
        "public_urls": {
            "record": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE190604",
            "matrix": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE190nnn/GSE190604/suppl/GSE190604_matrix.mtx.gz",
        },
        "metadata": {
            "n_cells_matrix": len(barcodes),
            "n_features": line_count(paths["features"]),
            "n_cells_with_guide_call": int(guides["cell_barcode"].nunique()),
            "n_singleton_guide_cells": len(singleton),
            "n_singleton_guides": int(singleton["feature_call"].nunique()),
            "n_singleton_targets_including_control": int(singleton["target"].nunique()),
            "n_no_target_cells": int(target_counts.get("NO-TARGET", 0)),
            "barcode_suffix_counts": suffixes.value_counts().sort_index().to_dict(),
            "target_cell_counts": target_counts.to_dict(),
        },
        "sample_mapping": {
            "status": "CONFIRMED_FROM_OFFICIAL_GEO_RECORD",
            "mapping": {
                "1-4": "mRNA-nostim-well1 through mRNA-nostim-well4",
                "5-8": "mRNA-stim-well1 through mRNA-stim-well4",
            },
            "basis": (
                "official GSE190604 record lists GSM5726254-57 as mRNA-nostim-well1-4 "
                "and GSM5726258-61 as mRNA-stim-well1-4 in barcode suffix order"
            ),
            "verified_record": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE190604",
            "verified_at": "2026-07-12",
        },
        "donor_design": {
            "status": "PAIRED_DESIGN_DONOR_MIXED_NOT_RESOLVED",
            "n_donors": 2,
            "design": (
                "cells from the two blood donors were split across no-stim and stimulated "
                "conditions, then normalized and mixed 1:1 before droplet loading"
            ),
            "well_interpretation": (
                "four 10x replicate wells per condition contain the donor mixture; well number "
                "is not a donor identifier"
            ),
            "processed_matrix_has_donor_id": False,
            "basis": (
                "official GEO extraction protocols for GSM5726254 and GSM5726258 state that "
                "sorted cells from two blood donors were normalized and mixed 1:1 for each "
                "condition; the treatment protocol states that cells were split into the two "
                "conditions"
            ),
            "verified_records": [
                "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM5726254",
                "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM5726258",
            ],
            "verified_at": "2026-07-12",
        },
        "donor_recovery_feasibility": {
            "status": "NO_GO_LOCAL_CONFIRMATORY",
            "sra_study": "SRP350148",
            "raw_mrna_download_gb_reported": 154.2,
            "raw_guide_download_gb_reported": 63.8,
            "n_mrna_runs": 8,
            "n_donors": 2,
            "current_free_gb": round(free_bytes / 1_000_000_000, 1),
            "local_full_download_feasible": free_bytes >= 154.2 * 1_000_000_000,
            "reason": (
                "raw mRNA downloads exceed current local free space and resolving only two "
                "donors would provide a consistency diagnostic, not population-level "
                "confirmation of a context interaction"
            ),
            "recommended_use": (
                "do not download locally for confirmatory inference; prioritize a donor-resolved "
                "dataset or experiment with enough independent donors to estimate between-donor "
                "variation"
            ),
            "verified_record": "https://www.ncbi.nlm.nih.gov/sra?term=SRP350148",
            "verified_at": "2026-07-12",
        },
        "replication_design": {
            "status": "TARGETED_PANEL_METHOD_REQUIRED",
            "reason": (
                "74 targets cannot support five disjoint negatives for each of 23 positives; "
                "use gene-level overlap weighting and nested OOF instead of disjoint blocks"
            ),
        },
        "matrix_intake": {
            "compressed_bytes": MATRIX_COMPRESSED_BYTES,
            "free_bytes": free_bytes,
            "download_safe_at_12_gib_floor": free_bytes - MATRIX_COMPRESSED_BYTES >= 12 * 1024**3,
            "processing": "two-pass streaming MatrixMarket; never materialize decompressed MTX",
        },
        "files": {
            name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for name, path in paths.items()
        },
        "timestamp": datetime.now().astimezone().isoformat(),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
