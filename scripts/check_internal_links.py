#!/usr/bin/env python3
"""Fail when a tracked Markdown file links to a missing repository path."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "data:", "#")


def tracked_markdown() -> list[Path]:
    """Ask Git for the public Markdown surface instead of scanning virtual environments."""

    output = subprocess.check_output(
        ["git", "ls-files", "*.md"], cwd=ROOT, text=True
    )
    return [ROOT / line for line in output.splitlines() if line]


def path_part(raw_target: str) -> str:
    """Remove an optional Markdown title and fragment from a local link target."""

    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target.split("#", 1)[0])


def broken_links() -> list[str]:
    """Return source locations for repository-relative targets that do not exist."""

    failures: list[str] = []
    for markdown_path in tracked_markdown():
        text = markdown_path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            raw_target = match.group(1).strip()
            if not raw_target or raw_target.startswith(EXTERNAL_PREFIXES):
                continue
            local_path = path_part(raw_target)
            if not local_path or "{{" in local_path or "}}" in local_path:
                continue
            resolved = (markdown_path.parent / local_path).resolve()
            if resolved.exists():
                continue
            line = text.count("\n", 0, match.start()) + 1
            relative_source = markdown_path.relative_to(ROOT)
            failures.append(f"{relative_source}:{line}: missing {raw_target}")
    return failures


def main() -> int:
    failures = broken_links()
    if failures:
        print("Broken internal Markdown links:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Internal Markdown links: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
