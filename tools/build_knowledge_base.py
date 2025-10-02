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

    repo_root = pathlib.Path.cwd().resolve()

    def to_relative(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root))
        except ValueError:
            raise SystemExit(
                f"Path {path} is outside the repository root {repo_root}; cannot emit absolute paths."
            )

    version_dir = args.version_dir.expanduser().resolve()
    if not version_dir.exists():
        parser.error(f"Version directory not found: {version_dir}")

    manual_structure = load_json(version_dir / "manual_structure.json")
    syntax_catalog = load_json(version_dir / "syntax_catalog.json")
    function_catalog = load_json(version_dir / "function_catalog.json")
    semantic_patterns = load_json(version_dir / "semantic_patterns.json")
    grammar_validation = load_json(version_dir / "grammar_validation.json")

    manual_pdf = version_dir / "manual.pdf"
    manual_txt = version_dir / "manual.txt"
    manual_structure_path = version_dir / "manual_structure.json"
    syntax_catalog_path = version_dir / "syntax_catalog.json"
    grammar_path = version_dir / "realtest_grammar.lark"
    function_catalog_path = version_dir / "function_catalog.json"
    semantic_patterns_path = version_dir / "semantic_patterns.json"
    grammar_validation_path = version_dir / "grammar_validation.json"
    evaluation_suite_path = version_dir / "evaluation_suite.json"

    summary_lines = [
        f"# RealTest Language Knowledge Base (Version {version_dir.name})",
        "",
        "## Overview",
        f"- PDF source: `{to_relative(manual_pdf)}`",
        f"- Text extraction: `{to_relative(manual_txt)}`",
        f"- Manual structure & glossary: `{to_relative(manual_structure_path)}` ({len(manual_structure['sections'])} sections)",
        f"- Syntax catalog: `{to_relative(syntax_catalog_path)}` ({len(syntax_catalog)} items)",
        f"- Grammar spec: `{to_relative(grammar_path)}`",
        f"- Function catalog: `{to_relative(function_catalog_path)}` ({len(function_catalog)} entries)",
        f"- Semantic patterns: `{to_relative(semantic_patterns_path)}` ({len(semantic_patterns)} patterns)",
        f"- Grammar validation: `{to_relative(grammar_validation_path)}`",
        f"- Evaluation suite: `{to_relative(evaluation_suite_path)}`",
        "",
        "## Methodology",
        "1. Versioned the source manual and extracted deterministic text for processing.",
        "2. Parsed the manual headings into a full section index and glossary for grounding terminology.",
        "3. Catalogued structural constructs using both manual references and curated `samples/` scripts.",
        "4. Generated a Lark grammar constrained to enumerated top-level sections and validated it against all sample scripts.",
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
            "- Consider emitting additional formats (e.g., ANTLR) from the Lark grammar if downstream tooling requires them.",
        ]
    )

    output_path = args.output.expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"Wrote knowledge base summary to {to_relative(output_path)}")


if __name__ == "__main__":
    main()
