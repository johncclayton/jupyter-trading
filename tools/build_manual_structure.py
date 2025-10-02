#!/usr/bin/env python3
"""Build manual structure and glossary from RealTest PDF text."""

import argparse
import json
import pathlib
import re

GLOSSARY_TERMS = {
    "Settings": "Global parameters controlling dates, account configuration, and bar size.",
    "Data": "Section that defines derived series or imported references available to strategies.",
    "Strategy": "Block containing trading rules, universe, sizing, and entry/exit logic for one approach.",
    "Library": "Reusable formulas or helper items shared across strategies.",
    "EntrySetup": "Boolean condition required before a candidate symbol can be considered for entry.",
    "EntryScore": "Ranking metric applied to qualified symbols to determine trade priority.",
    "EntrySkip": "Condition that, when true, blocks new entries (e.g., during market drawdowns).",
    "ExitRule": "Boolean condition that, when true, triggers exit orders.",
    "ExitStop": "Protective stop price formula applied to open positions.",
    "IncludeList": "Directive that specifies which symbols or symbol lists to include in a test.",
    "BarSize": "Setting that chooses the timeframe aggregation (Daily, Weekly, Monthly, etc.).",
    "Extern": "Function for referencing data from alternate symbols or bar sizes inside formulas.",
    "MaxEntries": "Cap on the number of simultaneous positions a strategy may open.",
    "Universe": "Specification describing which symbols a strategy trades.",
    "PositionSize": "Expression that sets the sizing of new entries (shares or dollars).",
    "S.Equity": "Built-in series tracking cumulative equity for the current strategy."
}

HEADING_PATTERN = re.compile(r"^\s*(\d+(?:\.\d+)*)(?:\.)?\s+(.*\S)\s*$")


def parse_sections(lines: list[str]) -> list[dict]:
    sections: list[dict] = []
    seen_titles: set[str] = set()
    for idx, raw in enumerate(lines):
        line = raw.strip()
        match = HEADING_PATTERN.match(line)
        if not match:
            continue
        title = re.sub(r"\s+", " ", match.group(2)).strip()
        if not title:
            continue
        title_key = title.lower()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        sections.append(
            {
                "order": len(sections) + 1,
                "heading": match.group(1),
                "title": title,
                "source_line": idx + 1,
            }
        )
    return sections


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract manual headings and glossary entries")
    parser.add_argument("--manual", required=True, type=pathlib.Path, help="Path to manual.txt")
    parser.add_argument("--output", required=True, type=pathlib.Path, help="Destination JSON path")
    args = parser.parse_args()

    manual_path = args.manual.expanduser().resolve()
    if not manual_path.exists():
        parser.error(f"Manual not found: {manual_path}")

    lines = manual_path.read_text(encoding="utf-8").splitlines()
    sections = parse_sections(lines)
    glossary = [
        {"term": term, "definition": definition}
        for term, definition in GLOSSARY_TERMS.items()
    ]

    output = {"sections": sections, "glossary": glossary}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(
        f"Wrote {args.output} with {len(sections)} sections and {len(glossary)} glossary entries"
    )


if __name__ == "__main__":
    main()
