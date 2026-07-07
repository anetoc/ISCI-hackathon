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
    Build evidence card: ISCI score + PubMed + Open Targets + literature-review.

    No hallucinated references. Consensus is NOT available in Claude Science.
    """
    raise NotImplementedError("Implement in Claude Science build (D0+)")


def write_evidence_report(cards: list[dict], path: Path) -> None:
    """Write markdown/JSON evidence report for top-ranked genes."""
    raise NotImplementedError("Implement in Claude Science build (D0+)")
