"""Resolve public GSE190604 guide IDs to source-observed Calabrese sequences."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator

import pandas as pd


GUIDE_PATTERN = re.compile(r"_([ACGT]{20})_r\d+$")
TARGET_PATTERN = re.compile(r"-\d+$")
DNA_COMPLEMENT = str.maketrans("ACGTN", "TGCAN")


def normalize_direct_capture_barcode(raw_sequence: str) -> str:
    """Convert a custom guide-library R1 barcode to the processed 10x orientation."""

    barcode = raw_sequence.strip()[:16].upper()
    if len(barcode) != 16 or not set(barcode) <= set("ACGTN"):
        raise ValueError("guide read 1 must contain a 16-base DNA barcode")
    # In these public guide FASTQs, bases 8-9 are the complement of the processed barcode.
    # Applying the deterministic transform avoids error-tolerant or nearest-barcode matching.
    return barcode[:7] + barcode[7:9].translate(DNA_COMPLEMENT) + barcode[9:]


def build_calabrese_candidates(
    screen_tables: dict[str, pd.DataFrame], target_genes: set[str]
) -> pd.DataFrame:
    """Extract unique same-target 20-mers and screen ranks from MAGeCK summaries."""

    rows: list[pd.DataFrame] = []
    required = {"sgrna", "Gene", "LFC"}
    for screen, table in screen_tables.items():
        missing = required - set(table.columns)
        if missing:
            raise ValueError(f"{screen} screen table missing columns: {sorted(missing)}")
        selected = table.loc[table["Gene"].astype(str).isin(target_genes), list(required)].copy()
        selected["sequence"] = selected["sgrna"].astype(str).str.extract(GUIDE_PATTERN)[0]
        if selected["sequence"].isna().any():
            raise ValueError(f"{screen} contains malformed Calabrese sgRNA identifiers")
        selected["LFC"] = pd.to_numeric(selected["LFC"], errors="raise")
        # r0/r1 rows can share a protospacer. Ranking the best observed row gives each unique
        # candidate one deterministic position and is used only for structural tie-breaking.
        unique = (
            selected.groupby(["Gene", "sequence"], observed=True, as_index=False)["LFC"]
            .max()
            .rename(columns={"Gene": "target", "LFC": "screen_max_lfc"})
            .sort_values(
                ["target", "screen_max_lfc", "sequence"],
                ascending=[True, False, True],
                kind="mergesort",
            )
        )
        unique["screen_rank"] = unique.groupby("target", observed=True).cumcount() + 1
        unique["screen"] = screen
        rows.append(unique)
    if not rows:
        raise ValueError("at least one screen table is required")
    return pd.concat(rows, ignore_index=True).sort_values(
        ["target", "screen", "screen_rank"], kind="mergesort"
    ).reset_index(drop=True)


def _fastq_records(path: Path) -> Iterator[tuple[str, str]]:
    """Yield complete FASTQ records and ignore only a final truncated partial record."""

    with path.open() as handle:
        while True:
            record = [handle.readline() for _ in range(4)]
            if not record[0]:
                return
            if not record[3]:
                return
            if not record[0].startswith("@") or not record[2].startswith("+"):
                raise ValueError(f"malformed FASTQ record in {path}")
            yield record[0].split()[0], record[1].strip().upper()


def extract_guide_sequence_evidence(
    guidecalls: pd.DataFrame,
    candidates: pd.DataFrame,
    *,
    read1_path: Path,
    read2_path: Path,
    well: int,
    panel_guide_ids: set[str],
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Aggregate exact same-target sequence matches without retaining cell-level data."""

    if not {"cell_barcode", "feature_call"} <= set(guidecalls.columns):
        raise ValueError("guide calls require cell_barcode and feature_call")
    if not {"target", "sequence"} <= set(candidates.columns):
        raise ValueError("candidates require target and sequence")
    if well < 1:
        raise ValueError("well must be positive")

    singleton = guidecalls[
        ~guidecalls["feature_call"].astype(str).str.contains("|", regex=False)
    ].copy()
    well_suffix = singleton["cell_barcode"].astype(str).str.rsplit("-", n=1)
    singleton = singleton[well_suffix.str[-1].eq(str(well))].copy()
    singleton["barcode"] = singleton["cell_barcode"].astype(str).str.rsplit("-", n=1).str[0]
    conflicting = singleton.groupby("barcode", observed=True)["feature_call"].nunique()
    if (conflicting > 1).any():
        raise ValueError("a processed barcode maps to multiple singleton guide IDs")
    barcode_to_guide = dict(zip(singleton["barcode"], singleton["feature_call"], strict=True))

    target_candidates = (
        candidates.groupby("target", observed=True)["sequence"].agg(lambda values: set(values))
    ).to_dict()
    counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    metrics = Counter()
    for (header1, sequence1), (header2, sequence2) in zip(
        _fastq_records(read1_path), _fastq_records(read2_path), strict=False
    ):
        metrics["read_pairs_examined"] += 1
        if header1 != header2:
            raise ValueError("read 1 and read 2 FASTQ records are not paired")
        normalized = normalize_direct_capture_barcode(sequence1)
        guide_id = barcode_to_guide.get(normalized)
        if guide_id is None or guide_id not in panel_guide_ids:
            continue
        metrics["panel_barcode_pairs"] += 1
        target = TARGET_PATTERN.sub("", str(guide_id))
        allowed = target_candidates.get(target, set())
        hits = {
            sequence2[start : start + 20]
            for start in range(max(0, len(sequence2) - 19))
            if sequence2[start : start + 20] in allowed
        }
        if hits:
            metrics["same_target_candidate_pairs"] += 1
        for sequence in hits:
            counts[(str(guide_id), sequence)] += 1

    rows = [
        {
            "guide_id": guide_id,
            "target": TARGET_PATTERN.sub("", guide_id),
            "sequence": sequence,
            "well": well,
            "exact_candidate_reads": count,
        }
        for (guide_id, sequence), count in sorted(counts.items())
    ]
    return pd.DataFrame(rows), dict(metrics)


def _leading_g_shadows(sequence_counts: dict[str, int]) -> set[str]:
    """Identify a 20-mer created by U6 leading-G addition to another candidate."""

    shadows: set[str] = set()
    sequences = set(sequence_counts)
    for original in sequences:
        if original.startswith("G"):
            continue
        shadow = "G" + original[:19]
        if shadow not in sequences:
            continue
        larger = max(sequence_counts[original], sequence_counts[shadow])
        if larger and abs(sequence_counts[original] - sequence_counts[shadow]) / larger <= 0.05:
            shadows.add(shadow)
    return shadows


def basic_sequence_flags(sequence: str) -> str:
    """Report simple synthesis flags without substituting for on/off-target validation."""

    flags = []
    gc_fraction = (sequence.count("G") + sequence.count("C")) / len(sequence)
    if "TTTT" in sequence:
        flags.append("POLY_T4")
    if any(base * 5 in sequence for base in "ACGT"):
        flags.append("HOMOPOLYMER_5")
    if gc_fraction < 0.25:
        flags.append("GC_LT_25_PERCENT")
    if gc_fraction > 0.80:
        flags.append("GC_GT_80_PERCENT")
    if "CGTCTC" in sequence or "GAGACG" in sequence:
        flags.append("BSMBI_SITE")
    return "|".join(flags) if flags else "NONE"


def resolve_guide_sequences(
    panel: pd.DataFrame,
    evidence: pd.DataFrame,
    candidates: pd.DataFrame,
    *,
    min_exact_reads: int = 10,
    min_support_wells: int = 2,
    ambiguity_ratio: float = 0.20,
) -> pd.DataFrame:
    """Resolve one source sequence per guide while keeping synthesis approval blocked."""

    if not {"guide_id", "target"} <= set(panel.columns):
        raise ValueError("panel requires guide_id and target")
    if not {"guide_id", "sequence", "well", "exact_candidate_reads"} <= set(
        evidence.columns
    ):
        raise ValueError("evidence table is missing required columns")
    if not {"target", "sequence", "screen", "screen_rank"} <= set(candidates.columns):
        raise ValueError("candidate table is missing required columns")
    if min_exact_reads < 1 or min_support_wells < 1 or not 0 < ambiguity_ratio < 1:
        raise ValueError("invalid resolution thresholds")

    result = panel.copy()
    if "sequence_status" in result.columns:
        result = result.rename(columns={"sequence_status": "prior_sequence_status"})
    best_rank = candidates.groupby(["target", "sequence"], observed=True)[
        "screen_rank"
    ].min()
    screens = candidates.groupby(["target", "sequence"], observed=True)["screen"].agg(
        lambda values: "|".join(sorted(set(map(str, values))))
    )

    resolutions = []
    for row in result.itertuples(index=False):
        guide_id = str(row.guide_id)
        target = str(row.target)
        subset = evidence[evidence["guide_id"].astype(str) == guide_id].copy()
        counts = (
            subset.groupby("sequence", observed=True)["exact_candidate_reads"].sum().astype(int)
        ).to_dict()
        support_wells = (
            subset[subset["exact_candidate_reads"] > 0]
            .groupby("sequence", observed=True)["well"]
            .nunique()
            .astype(int)
            .to_dict()
        )
        shadows = _leading_g_shadows(counts)
        eligible = {sequence: count for sequence, count in counts.items() if sequence not in shadows}
        ranked = sorted(
            eligible.items(),
            key=lambda item: (
                -item[1],
                int(best_rank.get((target, item[0]), 10**9)),
                item[0],
            ),
        )

        sequence = ranked[0][0] if ranked else ""
        exact_reads = ranked[0][1] if ranked else 0
        wells = int(support_wells.get(sequence, 0)) if sequence else 0
        runner_count = ranked[1][1] if len(ranked) > 1 else 0
        ambiguous = bool(exact_reads and runner_count / exact_reads >= ambiguity_ratio)
        if not sequence:
            identity_status = "SOURCE_IDENTITY_UNRESOLVED"
            synthesis_status = "BLOCKED_SOURCE_IDENTITY"
        elif ambiguous:
            identity_status = "SOURCE_IDENTITY_AMBIGUOUS"
            synthesis_status = "BLOCKED_SOURCE_IDENTITY"
        elif exact_reads >= min_exact_reads and wells >= min_support_wells:
            identity_status = "SOURCE_IDENTITY_CONFIRMED"
            synthesis_status = "BLOCKED_PENDING_ON_OFF_TARGET_AND_VECTOR_QC"
        else:
            identity_status = "SOURCE_IDENTITY_LOW_SUPPORT"
            synthesis_status = "BLOCKED_LOW_SOURCE_SUPPORT"

        gc_fraction = (
            (sequence.count("G") + sequence.count("C")) / len(sequence) if sequence else float("nan")
        )
        resolutions.append(
            {
                "protospacer_20nt": sequence,
                "sequence_length": len(sequence),
                "gc_fraction": gc_fraction,
                "basic_sequence_flags": basic_sequence_flags(sequence) if sequence else "NOT_EVALUABLE",
                "exact_candidate_reads": exact_reads,
                "support_wells": wells,
                "runner_up_reads": runner_count,
                "leading_g_shadows_removed": len(shadows),
                "source_screens": str(screens.get((target, sequence), "")) if sequence else "",
                "best_source_screen_rank": (
                    int(best_rank.get((target, sequence)))
                    if sequence and (target, sequence) in best_rank.index
                    else pd.NA
                ),
                "source_identity_status": identity_status,
                "synthesis_status": synthesis_status,
            }
        )
    return pd.concat([result.reset_index(drop=True), pd.DataFrame(resolutions)], axis=1)


def build_replacement_shortlist(
    resolved_panel: pd.DataFrame,
    candidates: pd.DataFrame,
    *,
    candidates_per_target: int = 3,
) -> pd.DataFrame:
    """Rank same-target technical backups for targets with a current guide in review."""

    required_panel = {
        "guide_id",
        "target",
        "role",
        "protospacer_20nt",
        "basic_sequence_flags",
        "source_identity_status",
    }
    required_candidates = {
        "target",
        "sequence",
        "screen",
        "screen_rank",
        "screen_max_lfc",
    }
    if missing := required_panel - set(resolved_panel.columns):
        raise ValueError(f"resolved panel missing columns: {sorted(missing)}")
    if missing := required_candidates - set(candidates.columns):
        raise ValueError(f"candidate table missing columns: {sorted(missing)}")
    if candidates_per_target < 1:
        raise ValueError("candidates per target must be positive")

    panel = resolved_panel.copy()
    panel["needs_review"] = panel["source_identity_status"].ne(
        "SOURCE_IDENTITY_CONFIRMED"
    ) | panel["basic_sequence_flags"].ne("NONE")
    review_targets = panel.loc[panel["needs_review"], "target"].drop_duplicates()
    rows: list[dict[str, object]] = []
    for target in review_targets:
        current = panel[panel["target"] == target]
        triggers = current[current["needs_review"]]
        used_sequences = set(current["protospacer_20nt"].astype(str))
        source = candidates[
            (candidates["target"] == target)
            & ~candidates["sequence"].astype(str).isin(used_sequences)
        ].copy()
        if source.empty:
            continue
        source = (
            source.groupby(["target", "sequence"], observed=True, as_index=False)
            .agg(
                best_source_screen_rank=("screen_rank", "min"),
                max_source_screen_lfc=("screen_max_lfc", "max"),
                source_screens=("screen", lambda values: "|".join(sorted(set(values)))),
            )
        )
        source["basic_sequence_flags"] = source["sequence"].map(basic_sequence_flags)
        source["has_basic_flag"] = source["basic_sequence_flags"].ne("NONE")
        source = source.sort_values(
            [
                "has_basic_flag",
                "best_source_screen_rank",
                "max_source_screen_lfc",
                "sequence",
            ],
            ascending=[True, True, False, True],
            kind="mergesort",
        ).head(candidates_per_target)
        priority = (
            "HIGH_ALL_CURRENT_GUIDES_REVIEW"
            if len(triggers) == len(current)
            else "BACKUP_ONLY"
        )
        trigger_reasons = []
        for guide in triggers.itertuples(index=False):
            reasons = [str(guide.source_identity_status)]
            if guide.basic_sequence_flags != "NONE":
                reasons.append(str(guide.basic_sequence_flags))
            trigger_reasons.append(f"{guide.guide_id}:{'+'.join(reasons)}")
        for fallback_rank, candidate in enumerate(source.itertuples(index=False), start=1):
            rows.append(
                {
                    "target": target,
                    "role": "|".join(sorted(set(current["role"].astype(str)))),
                    "trigger_guide_ids": "|".join(triggers["guide_id"].astype(str)),
                    "trigger_reasons": "|".join(trigger_reasons),
                    "replacement_priority": priority,
                    "fallback_rank": fallback_rank,
                    "fallback_sequence": candidate.sequence,
                    "basic_sequence_flags": candidate.basic_sequence_flags,
                    "best_source_screen_rank": int(candidate.best_source_screen_rank),
                    "max_source_screen_lfc": float(candidate.max_source_screen_lfc),
                    "source_screens": candidate.source_screens,
                    "fallback_status": "REQUIRES_ON_OFF_TARGET_AND_VECTOR_QC",
                }
            )
    return pd.DataFrame(rows)


def build_off_target_screening_input(
    resolved_panel: pd.DataFrame,
    shortlist: pd.DataFrame,
    *,
    reference_build: str = "UNSELECTED",
    transcript_tss_annotation: str = "UNSELECTED",
    search_engine: str = "UNSELECTED",
    search_parameters: str = "UNSELECTED",
) -> pd.DataFrame:
    """Package current and fallback sequences with explicit versioned search decisions."""

    required_panel = {
        "guide_id",
        "target",
        "role",
        "protospacer_20nt",
        "basic_sequence_flags",
        "source_identity_status",
        "synthesis_status",
    }
    required_shortlist = {
        "target",
        "role",
        "replacement_priority",
        "fallback_rank",
        "fallback_sequence",
        "basic_sequence_flags",
        "fallback_status",
    }
    if missing := required_panel - set(resolved_panel.columns):
        raise ValueError(f"resolved panel missing columns: {sorted(missing)}")
    if missing := required_shortlist - set(shortlist.columns):
        raise ValueError(f"shortlist missing columns: {sorted(missing)}")

    rows: list[dict[str, object]] = []
    for guide in resolved_panel.itertuples(index=False):
        rows.append(
            {
                "candidate_id": str(guide.guide_id),
                "target": str(guide.target),
                "role": str(guide.role),
                "candidate_kind": "CURRENT_GUIDE",
                "protospacer_20nt": str(guide.protospacer_20nt),
                "basic_sequence_flags": str(guide.basic_sequence_flags),
                "source_identity_status": str(guide.source_identity_status),
                "replacement_priority": "CURRENT_MANIFEST",
                "pre_screen_status": str(guide.synthesis_status),
            }
        )
    for fallback in shortlist.itertuples(index=False):
        rows.append(
            {
                "candidate_id": f"{fallback.target}-FALLBACK-{fallback.fallback_rank}",
                "target": str(fallback.target),
                "role": str(fallback.role),
                "candidate_kind": "FALLBACK_CANDIDATE",
                "protospacer_20nt": str(fallback.fallback_sequence),
                "basic_sequence_flags": str(fallback.basic_sequence_flags),
                "source_identity_status": "CALABRESE_SOURCE_CANDIDATE",
                "replacement_priority": str(fallback.replacement_priority),
                "pre_screen_status": str(fallback.fallback_status),
            }
        )
    result = pd.DataFrame(rows)
    if result["candidate_id"].duplicated().any():
        raise RuntimeError("off-target candidate IDs must be unique")
    if not result["protospacer_20nt"].str.fullmatch(r"[ACGT]{20}").all():
        raise ValueError("every off-target candidate requires a 20-base DNA protospacer")

    result["modality"] = "CRISPRa"
    result["nuclease_family"] = "SpCas9"
    result["pam_contract"] = "NGG"
    decisions = {
        "reference_build": reference_build,
        "transcript_tss_annotation": transcript_tss_annotation,
        "search_engine": search_engine,
        "search_parameters": search_parameters,
    }
    if any(not value.strip() for value in decisions.values()):
        raise ValueError("off-target search decisions cannot be blank; use UNSELECTED")
    for field, value in decisions.items():
        result[field] = value
    if reference_build == "UNSELECTED" or transcript_tss_annotation == "UNSELECTED":
        status = "BLOCKED_REFERENCE_AND_ENGINE_NOT_FROZEN"
    elif search_engine == "UNSELECTED" or search_parameters == "UNSELECTED":
        status = "BLOCKED_ENGINE_AND_PARAMETERS_NOT_FROZEN"
    else:
        status = "READY_FOR_OFF_TARGET_RUN"
    result["off_target_status"] = status
    return result


def build_off_target_pilot_manifest(
    screening_input: pd.DataFrame,
    replacement_shortlist: pd.DataFrame,
) -> pd.DataFrame:
    """Select the highest-risk project guides for the first version-pinned search."""

    required_screening = {
        "candidate_id",
        "target",
        "role",
        "candidate_kind",
        "protospacer_20nt",
        "basic_sequence_flags",
        "reference_build",
        "transcript_tss_annotation",
        "off_target_status",
    }
    required_shortlist = {"target", "replacement_priority"}
    if missing := required_screening - set(screening_input.columns):
        raise ValueError(f"screening input missing columns: {sorted(missing)}")
    if missing := required_shortlist - set(replacement_shortlist.columns):
        raise ValueError(f"replacement shortlist missing columns: {sorted(missing)}")

    priority_targets = sorted(
        replacement_shortlist.loc[
            replacement_shortlist["replacement_priority"].eq(
                "HIGH_ALL_CURRENT_GUIDES_REVIEW"
            ),
            "target",
        ]
        .astype(str)
        .unique()
    )
    if not priority_targets:
        raise ValueError("pilot requires at least one high-priority replacement target")

    pilot = screening_input[
        screening_input["target"].astype(str).isin(priority_targets)
    ].copy()
    if pilot.empty:
        raise ValueError("screening input has no candidates for high-priority targets")
    if pilot["candidate_id"].duplicated().any():
        raise ValueError("pilot candidate IDs must be unique")
    if pilot["protospacer_20nt"].duplicated().any():
        raise ValueError("pilot protospacers must be unique for deterministic result mapping")
    if not pilot["protospacer_20nt"].astype(str).str.fullmatch(r"[ACGT]{20}").all():
        raise ValueError("pilot candidates require 20-base DNA protospacers")
    if pilot["reference_build"].eq("UNSELECTED").any():
        raise ValueError("pilot requires a frozen reference build")
    if pilot["transcript_tss_annotation"].eq("UNSELECTED").any():
        raise ValueError("pilot requires a frozen annotation release")

    pilot["crispritz_guide"] = pilot["protospacer_20nt"].astype(str) + "NNN"
    pilot["pilot_stage"] = "S1_PRIORITY_REFERENCE_SEARCH"
    pilot["pilot_status"] = "READY_INPUT_EXECUTION_NOT_RUN"
    columns = [
        "candidate_id",
        "target",
        "role",
        "candidate_kind",
        "protospacer_20nt",
        "crispritz_guide",
        "basic_sequence_flags",
        "reference_build",
        "transcript_tss_annotation",
        "off_target_status",
        "pilot_stage",
        "pilot_status",
    ]
    return pilot[columns].sort_values(
        ["target", "candidate_kind", "candidate_id"], kind="mergesort"
    ).reset_index(drop=True)
