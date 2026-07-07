"""Traceable evidence cards per gene via PubMed / Open Targets connectors.

Every claim is tagged with a claim level so observation, mechanism, and clinical
hypothesis are never conflated (red-team requirement):

  observed_in_marson_perturbseq  — what the ISCI pipeline measured (this dataset)
  literature_supported           — a published finding, with PMID/DOI
  mechanistic_hypothesis         — a plausible mechanism, explicitly hypothetical
  clinical_hypothesis            — a testable clinical idea, NOT a prediction

Connector data (PubMed abstracts, Open Targets) is gathered in the repl kernel and
handed off as JSON; this module assembles cards from that evidence + ISCI scores.
Consensus/Cortellis are NOT available in Claude Science — sources are PubMed +
Open Targets + (optionally) the literature-review skill.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CLAIM_LEVELS = (
    "observed_in_marson_perturbseq",
    "literature_supported",
    "mechanistic_hypothesis",
    "clinical_hypothesis",
)


def build_evidence_card(
    gene: str,
    axis: str,
    isci_context: dict[str, Any],
    pubmed_articles: list[dict[str, Any]] | None = None,
    open_targets: dict[str, Any] | None = None,
    caveats: list[str] | None = None,
) -> dict:
    """Assemble one layered evidence card.

    Parameters
    ----------
    isci_context : {"isci_core_rank", "M_signed", "Q_score", "R_score",
                    "de_magnitude_rank", "n_downstream_rank", "movement_summary", ...}
                   — the OBSERVED layer, straight from the pipeline (no literature).
    pubmed_articles : list of {pmid, doi, title, abstract, journal, date} — each becomes
                      a literature_supported claim; NO claim without a citation.
    open_targets : optional {tractability, known_drugs, disease_assocs} dict.
    """
    observed = {
        "claim_level": "observed_in_marson_perturbseq",
        "isci_core_rank": isci_context.get("isci_core_rank"),
        "movement": isci_context.get("movement_summary"),
        "robustness": isci_context.get("robustness_summary"),
        "qc": isci_context.get("qc_summary"),
        "benchmark_context": {
            "isci_core_rank": isci_context.get("isci_core_rank"),
            "de_magnitude_rank": isci_context.get("de_magnitude_rank"),
            "n_downstream_rank": isci_context.get("n_downstream_rank"),
        },
    }
    literature = []
    for a in (pubmed_articles or []):
        if not (a.get("pmid") or a.get("doi")):
            continue  # Rule: no claim without citation
        literature.append({
            "claim_level": "literature_supported",
            "title": a.get("title"),
            "pmid": a.get("pmid"), "doi": a.get("doi"),
            "journal": a.get("journal"), "date": a.get("date"),
        })
    card = {
        "gene": gene,
        "axis": axis,
        "observed_perturbseq": observed,
        "literature_supported": literature,
        "mechanistic_annotation": open_targets or {},
        "clinical_hypothesis": {
            "claim_level": "clinical_hypothesis",
            "relevance": isci_context.get("clinical_relevance"),
            "not_for_clinical_decision": True,
        },
        "caveats": caveats or [
            "CD4+ primary T-cell CRISPRi perturbation context.",
            "Observed state-shift movement is not proof of patient response.",
        ],
        "citations": {
            "pubmed": [a.get("pmid") for a in literature if a.get("pmid")],
            "doi": [a.get("doi") for a in literature if a.get("doi")],
        },
    }
    return card


def _card_to_markdown(card: dict) -> str:
    g, axis = card["gene"], card["axis"]
    obs = card["observed_perturbseq"]
    lines = [
        f"# {g} — candidate state-shift controller ({axis})", "",
        "## Observed in Marson Perturb-seq (this analysis)",
        f"- ISCI-core rank: **{obs.get('isci_core_rank')}**",
        f"- Movement: {obs.get('movement')}",
        f"- Robustness: {obs.get('robustness')}",
        f"- QC: {obs.get('qc')}",
        f"- Benchmark context: DE-magnitude rank {obs['benchmark_context'].get('de_magnitude_rank')}, "
        f"n_downstream rank {obs['benchmark_context'].get('n_downstream_rank')}, "
        f"ISCI-core rank {obs['benchmark_context'].get('isci_core_rank')}", "",
        "## Literature support (cited)",
    ]
    if card["literature_supported"]:
        for lit in card["literature_supported"]:
            cite = f"PMID:{lit['pmid']}" if lit.get("pmid") else f"DOI:{lit.get('doi')}"
            lines.append(f"- *{lit.get('title')}* — {lit.get('journal')} ({lit.get('date')}) [{cite}]")
    else:
        lines.append("- (no cited literature retrieved)")
    lines += [
        "", "## Mechanistic annotation", f"```json\n{json.dumps(card['mechanistic_annotation'], indent=2)}\n```",
        "", "## Clinical hypothesis (hypothesis-generating; NOT a clinical prediction)",
        f"- Relevance: {card['clinical_hypothesis'].get('relevance')}",
        "- **Not for clinical decision-making.**",
        "", "## Caveats",
    ]
    lines += [f"- {c}" for c in card["caveats"]]
    return "\n".join(lines)


def write_evidence_report(cards: list[dict], out_dir: Path | str) -> list[Path]:
    """Write one markdown + JSON file per card under ``out_dir``. Returns written paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for card in cards:
        g = card["gene"]
        (out / f"{g}.json").write_text(json.dumps(card, indent=2))
        (out / f"{g}.md").write_text(_card_to_markdown(card))
        written += [out / f"{g}.json", out / f"{g}.md"]
    return written
