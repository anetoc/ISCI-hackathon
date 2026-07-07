"""Traceable evidence cards per gene via PubMed / Consensus / Open Targets connectors."""

from __future__ import annotations

from pathlib import Path


def build_evidence_card(
    gene: str,
    isci_score: float,
    axis: str,
    claims: list[str],
) -> dict:
    """
    Build evidence card: ISCI empirical score + connector-sourced citations.

    No hallucinated references — every claim must map to a connector result or local data.
    """
    raise NotImplementedError("Implement in Claude Science build (D0+)")


def write_evidence_report(cards: list[dict], path: Path) -> None:
    """Write markdown/JSON evidence report for top-ranked genes."""
    raise NotImplementedError("Implement in Claude Science build (D0+)")
