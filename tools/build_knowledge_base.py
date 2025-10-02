#!/usr/bin/env python3
"""Assemble knowledge base markdown from generated artifacts."""

import argparse
import json
import pathlib


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build knowledge base summary")
    parser.add_argument("--version-dir", required=True, type=pathlib.Path, help="Version directory")
    parser.add_argument("--output", required=True, type=pathlib.Path, help="Markdown output path")
    args = parser.parse_args()

    version_dir = args.version_dir.expanduser().resolve()
    if not version_dir.exists():
        parser.error(f"Version directory not found: {version_dir}")

    manual_structure = load_json(version_dir / "manual_structure.json")
    syntax_catalog = load_json(version_dir / "syntax_catalog.json")
    function_catalog = load_json(version_dir / "function_catalog.json")
    semantic_patterns = load_json(version_dir / "semantic_patterns.json")
    grammar_validation = load_json(version_dir / "grammar_validation.json")

    summary_lines = [
        f"# RealTest Language Knowledge Base (Version {version_dir.name})",
        "",
        "## Overview",
        f"- PDF source: `{version_dir / 'manual.pdf'}`",
        f"- Text extraction: `{version_dir / 'manual.txt'}`",
        f"- Manual structure & glossary: `{version_dir / 'manual_structure.json'}` ({len(manual_structure['sections'])} sections)",
        f"- Syntax catalog: `{version_dir / 'syntax_catalog.json'}` ({len(syntax_catalog)} items)",
        f"- Grammar spec: `{version_dir / 'realtest_grammar.json'}` + `{version_dir / 'realtest_grammar.lark'}` + `{version_dir / 'realtest_grammar.g4'}`",
        f"- Function catalog: `{version_dir / 'function_catalog.json'}` ({len(function_catalog)} entries)",
        f"- Semantic patterns: `{version_dir / 'semantic_patterns.json'}` ({len(semantic_patterns)} patterns)",
        f"- Grammar validation: `{version_dir / 'grammar_validation.json'}`",
        f"- Evaluation suite: `{version_dir / 'evaluation_suite.json'}`",
        "",
        "## Methodology",
        "1. Versioned the source manual and extracted deterministic text for processing.",
        "2. Parsed the manual headings into a full section index and glossary for grounding terminology.",
        "3. Catalogued structural constructs using both manual references and curated `samples/` scripts.",
        "4. Generated machine-readable grammar (JSON + Lark PEG) and validated it against all sample scripts.",
        "5. Compiled function/directive/statement metadata with cross-references to manual lines and sample usage.",
        "6. Captured semantic patterns linking natural-language descriptions to canonical RealTest snippets.",
        "7. Built an evaluation set of prompt_to_RTS cases for LLM regression testing.",
        "",
        "## Grammar Validation",
    ]

    results = grammar_validation.get("results", [])
    passed = sum(1 for item in results if item.get("valid"))
    total = len(results)
    summary_lines.append(f"- Parsed {passed}/{total} sample scripts successfully.")
    failures = [item for item in results if not item.get("valid")]
    if failures:
        summary_lines.append("- Failures:")
        for fail in failures:
            summary_lines.append(f"  - {fail['file']}: {fail['error']}")
    else:
        summary_lines.append("- All sample scripts parsed without errors.")

    summary_lines.extend(
        [
            "",
            "## Key Catalog Highlights",
            "- Syntax catalog entries cover sections (Import/Settings/Strategy/Library), directives (IncludeList, DataSource) and statements (EntrySetup, Quantity, Side, etc.).",
            "- Function catalog spans core indicators (`MA`, `ROC`, `ATR`), crossovers, universe directives, and sizing controls (Quantity, PositionSize, QtyType).",
            "",
            "## Semantic Patterns",
        ]
    )

    for entry in semantic_patterns:
        summary_lines.append(f"- **{entry['pattern']}** — {entry['description']}")

    summary_lines.extend(
        [
            "",
            "## Evaluation Suite",
            "- See `evaluation_suite.json` for prompt_to_RTS regression cases covering momentum filters, drawdown guards, and rotational momentum strategies.",
            "",
            "## Next Steps",
            "- Expand the function catalog by parsing the manual's appendix tables programmatically.",
            "- Add more domain-diverse `.rts` samples (e.g., futures, intraday) to stress-test the grammar.",
            "- Integrate the grammar validator and evaluation suite into CI to monitor LLM output quality.",
            "- Consider emitting additional formats (ANTLR `.g4`) from the Lark grammar for broader tooling support.",
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"Wrote knowledge base summary to {args.output}")


if __name__ == "__main__":
    main()
