from pathlib import Path

from scripts.run_crispritz_s0 import (
    canonical_target_rows,
    load_runtime_remediation,
    parse_peak_rss_kib,
    sha256,
)


def test_canonical_target_rows_sorts_nonempty_rows_without_deduplicating(tmp_path: Path) -> None:
    """Order differences may be normalized, but repeated engine rows must remain visible."""

    targets = tmp_path / "targets.txt"
    targets.write_text("z-row\n\na-row\nz-row\n")

    assert canonical_target_rows(targets) == ["a-row", "z-row", "z-row"]


def test_resource_parser_and_hash_are_deterministic(tmp_path: Path) -> None:
    """The audit report must capture GNU time output and content identity exactly."""

    resource_log = tmp_path / "resource.txt"
    resource_log.write_text("Maximum resident set size (kbytes): 12345\n")
    payload = tmp_path / "payload.txt"
    payload.write_text("T-CTRL\n")

    assert parse_peak_rss_kib(resource_log) == 12345
    assert sha256(payload) == "474313f7adb11d41086ddd142601a68ef1d17709dbc69cb56caf11c24d6f1c0a"


def test_runtime_remediation_requires_an_auditable_contract(tmp_path: Path) -> None:
    """A compatibility intervention cannot enter the report as an unstructured note."""

    record = tmp_path / "runtime-remediation.json"
    record.write_text(
        """{
  "id": "remove_incompatible_legacy_bytecode",
  "reason": "Python cache incompatibility",
  "scope": "cached bytecode only",
  "removed_legacy_pyc_count": 3,
  "source_commit": "24b893ecb0c2354d5c76697e116d2febe1ee6265"
}
"""
    )

    payload = load_runtime_remediation(record)

    assert payload["removed_legacy_pyc_count"] == 3
