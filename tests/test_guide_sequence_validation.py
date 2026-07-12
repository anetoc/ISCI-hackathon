from pathlib import Path

import pandas as pd

from isci.guide_sequence_validation import (
    build_replacement_shortlist,
    build_off_target_screening_input,
    build_calabrese_candidates,
    extract_guide_sequence_evidence,
    normalize_direct_capture_barcode,
    resolve_guide_sequences,
)


def write_fastq(path: Path, records: list[tuple[str, str]]) -> None:
    """Write the smallest valid FASTQ fixture needed by the streaming resolver."""

    path.write_text(
        "".join(f"@{name}\n{sequence}\n+\n{'I' * len(sequence)}\n" for name, sequence in records)
    )


def test_direct_capture_barcode_complements_only_bases_eight_and_nine():
    assert normalize_direct_capture_barcode("AAAAAAACAGGGGGGGEXTRA") == "AAAAAAAGTGGGGGGG"


def test_candidate_builder_deduplicates_replicates_and_ranks_sequences():
    screen = pd.DataFrame(
        {
            "sgrna": ["G1_AAAAAAAAAAAAAAAAAAAA_r0", "G1_AAAAAAAAAAAAAAAAAAAA_r1", "G1_CCCCCCCCCCCCCCCCCCCC_r0"],
            "Gene": ["G1", "G1", "G1"],
            "LFC": [1.0, 2.0, 1.5],
        }
    )
    candidates = build_calabrese_candidates({"IL2": screen}, {"G1"})
    assert candidates[["sequence", "screen_rank"]].to_dict("records") == [
        {"sequence": "AAAAAAAAAAAAAAAAAAAA", "screen_rank": 1},
        {"sequence": "CCCCCCCCCCCCCCCCCCCC", "screen_rank": 2},
    ]


def test_evidence_extraction_uses_exact_transformed_barcode(tmp_path):
    processed = "AAAAAAAGTGGGGGGG"
    raw = "AAAAAAACAGGGGGGG"
    guidecalls = pd.DataFrame(
        {"cell_barcode": [f"{processed}-1"], "feature_call": ["G1-1"]}
    )
    candidates = pd.DataFrame({"target": ["G1"], "sequence": ["ACGTACGTACGTACGTACGT"]})
    read1 = tmp_path / "r1.fastq"
    read2 = tmp_path / "r2.fastq"
    write_fastq(read1, [("READ.1", raw + "AAAA")])
    write_fastq(read2, [("READ.1", "PREFIX" + "ACGTACGTACGTACGTACGT" + "SUFFIX")])

    evidence, metrics = extract_guide_sequence_evidence(
        guidecalls,
        candidates,
        read1_path=read1,
        read2_path=read2,
        well=1,
        panel_guide_ids={"G1-1"},
    )
    assert evidence.iloc[0].to_dict() == {
        "guide_id": "G1-1",
        "target": "G1",
        "sequence": "ACGTACGTACGTACGTACGT",
        "well": 1,
        "exact_candidate_reads": 1,
    }
    assert metrics["same_target_candidate_pairs"] == 1


def test_resolution_removes_u6_leading_g_shadow_and_preserves_synthesis_gate():
    original = "TCGCCAAGTTCGGGACCGAC"
    shadow = "G" + original[:19]
    panel = pd.DataFrame(
        {
            "target": ["FOSL1", "PAPOLG"],
            "guide_id": ["FOSL1-2", "PAPOLG-1"],
            "sequence_status": ["REQUIRES_DESIGN_AND_VALIDATION"] * 2,
        }
    )
    candidates = pd.DataFrame(
        {
            "target": ["FOSL1", "FOSL1", "PAPOLG"],
            "sequence": [original, shadow, "TTAGGTCCCGGGAGGCTCCG"],
            "screen": ["IL2", "IL2", "IL2"],
            "screen_rank": [1, 3, 1],
        }
    )
    evidence = pd.DataFrame(
        {
            "guide_id": ["FOSL1-2", "FOSL1-2", "FOSL1-2", "FOSL1-2", "PAPOLG-1"],
            "sequence": [original, original, shadow, shadow, "TTAGGTCCCGGGAGGCTCCG"],
            "well": [1, 2, 1, 2, 3],
            "exact_candidate_reads": [50, 50, 51, 51, 1],
        }
    )
    resolved = resolve_guide_sequences(panel, evidence, candidates)
    fosl1 = resolved.loc[resolved["guide_id"] == "FOSL1-2"].iloc[0]
    papolg = resolved.loc[resolved["guide_id"] == "PAPOLG-1"].iloc[0]
    assert fosl1["protospacer_20nt"] == original
    assert fosl1["leading_g_shadows_removed"] == 1
    assert fosl1["source_identity_status"] == "SOURCE_IDENTITY_CONFIRMED"
    assert fosl1["synthesis_status"] == "BLOCKED_PENDING_ON_OFF_TARGET_AND_VECTOR_QC"
    assert papolg["source_identity_status"] == "SOURCE_IDENTITY_LOW_SUPPORT"
    assert papolg["synthesis_status"] == "BLOCKED_LOW_SOURCE_SUPPORT"


def test_replacement_shortlist_prefers_clean_same_target_candidates():
    resolved = pd.DataFrame(
        {
            "guide_id": ["G1-1", "G1-2", "G2-1", "G2-2"],
            "target": ["G1", "G1", "G2", "G2"],
            "role": ["PRIMARY_POSITIVE"] * 4,
            "protospacer_20nt": [
                "GGGGGAAAAAAAAAAAAAAA",
                "TTTTACGTACGTACGTACGT",
                "ACGTACGTACGTACGTACGT",
                "TGCATGCATGCATGCATGCA",
            ],
            "basic_sequence_flags": ["HOMOPOLYMER_5", "POLY_T4", "NONE", "NONE"],
            "source_identity_status": ["SOURCE_IDENTITY_CONFIRMED"] * 4,
        }
    )
    candidates = pd.DataFrame(
        {
            "target": ["G1", "G1", "G1", "G2"],
            "sequence": [
                "CCCCCAAAAAAAAAAAAAAA",
                "ACACACACACACACACACAC",
                "CACACACACACACACACACA",
                "GAGAGAGAGAGAGAGAGAGA",
            ],
            "screen": ["IL2", "IL2", "IFNG", "IL2"],
            "screen_rank": [1, 2, 3, 1],
            "screen_max_lfc": [3.0, 2.0, 1.0, 5.0],
        }
    )
    shortlist = build_replacement_shortlist(resolved, candidates, candidates_per_target=2)
    assert shortlist["target"].unique().tolist() == ["G1"]
    assert shortlist["fallback_sequence"].tolist() == [
        "ACACACACACACACACACAC",
        "CACACACACACACACACACA",
    ]
    assert shortlist["replacement_priority"].eq(
        "HIGH_ALL_CURRENT_GUIDES_REVIEW"
    ).all()


def test_off_target_input_keeps_reference_and_engine_blocked():
    resolved = pd.DataFrame(
        {
            "guide_id": ["G1-1"],
            "target": ["G1"],
            "role": ["PRIMARY_POSITIVE"],
            "protospacer_20nt": ["ACGTACGTACGTACGTACGT"],
            "basic_sequence_flags": ["NONE"],
            "source_identity_status": ["SOURCE_IDENTITY_CONFIRMED"],
            "synthesis_status": ["BLOCKED_PENDING_ON_OFF_TARGET_AND_VECTOR_QC"],
        }
    )
    shortlist = pd.DataFrame(
        {
            "target": ["G1"],
            "role": ["PRIMARY_POSITIVE"],
            "replacement_priority": ["BACKUP_ONLY"],
            "fallback_rank": [1],
            "fallback_sequence": ["CACACACACACACACACACA"],
            "basic_sequence_flags": ["NONE"],
            "fallback_status": ["REQUIRES_ON_OFF_TARGET_AND_VECTOR_QC"],
        }
    )
    screening = build_off_target_screening_input(resolved, shortlist)
    assert screening["candidate_kind"].tolist() == [
        "CURRENT_GUIDE",
        "FALLBACK_CANDIDATE",
    ]
    assert screening["reference_build"].eq("UNSELECTED").all()
    assert screening["search_engine"].eq("UNSELECTED").all()
    assert screening["off_target_status"].eq(
        "BLOCKED_REFERENCE_AND_ENGINE_NOT_FROZEN"
    ).all()


def test_off_target_input_can_freeze_reference_without_claiming_engine_readiness():
    resolved = pd.DataFrame(
        {
            "guide_id": ["G1-1"],
            "target": ["G1"],
            "role": ["PRIMARY_POSITIVE"],
            "protospacer_20nt": ["ACGTACGTACGTACGTACGT"],
            "basic_sequence_flags": ["NONE"],
            "source_identity_status": ["SOURCE_IDENTITY_CONFIRMED"],
            "synthesis_status": ["BLOCKED_PENDING_ON_OFF_TARGET_AND_VECTOR_QC"],
        }
    )
    shortlist = pd.DataFrame(
        columns=[
            "target",
            "role",
            "replacement_priority",
            "fallback_rank",
            "fallback_sequence",
            "basic_sequence_flags",
            "fallback_status",
        ]
    )
    screening = build_off_target_screening_input(
        resolved,
        shortlist,
        reference_build="GCF_000001405.40_GRCh38.p14",
        transcript_tss_annotation="GCF_000001405.40-RS_2025_08",
    )
    assert screening["reference_build"].eq("GCF_000001405.40_GRCh38.p14").all()
    assert screening["transcript_tss_annotation"].eq(
        "GCF_000001405.40-RS_2025_08"
    ).all()
    assert screening["search_engine"].eq("UNSELECTED").all()
    assert screening["off_target_status"].eq(
        "BLOCKED_ENGINE_AND_PARAMETERS_NOT_FROZEN"
    ).all()
