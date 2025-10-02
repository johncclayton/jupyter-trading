#!/usr/bin/env python3
"""Run CI checks for RealTest knowledge base artifacts."""

import argparse
import json
import pathlib
import sys

from lark import Lark, exceptions

from validate_grammar import validate


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def check_evaluation(grammar_path: pathlib.Path, evaluation_path: pathlib.Path) -> list[str]:
    issues: list[str] = []
    grammar_text = grammar_path.read_text(encoding="utf-8")
    parser = Lark(grammar_text, start="start", parser="earley", maybe_placeholders=True)

    data = json.loads(evaluation_path.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    if not cases:
        issues.append("Evaluation suite contains no cases")
        return issues

    for idx, case in enumerate(cases, start=1):
        prompt = case.get("prompt")
        expected = case.get("expected")
        if not prompt or not expected:
            issues.append(f"Case {idx} missing prompt or expected output")
            continue
        try:
            parser.parse(ensure_trailing_newline(expected))
        except exceptions.LarkError as exc:
            issues.append(f"Case {idx} expected snippet failed to parse: {exc}")
    return issues


def main() -> None:
    cli = argparse.ArgumentParser(description="Run grammar validation and evaluation sanity checks")
    cli.add_argument("--version-dir", required=True, type=pathlib.Path, help="Version directory")
    cli.add_argument("--samples", required=True, type=pathlib.Path, help="Samples directory")
    args = cli.parse_args()

    version_dir = args.version_dir.expanduser().resolve()
    samples_dir = args.samples.expanduser().resolve()

    grammar_path = version_dir / "realtest_grammar.lark"
    evaluation_path = version_dir / "evaluation_suite.json"

    if not grammar_path.exists():
        raise SystemExit(f"Grammar file not found: {grammar_path}")
    if not evaluation_path.exists():
        raise SystemExit(f"Evaluation suite not found: {evaluation_path}")

    results = validate(grammar_path, samples_dir)
    passed = sum(1 for r in results if r["valid"])
    total = len(results)
    print(f"Grammar validation summary: {passed}/{total} samples parsed")
    failures = [r for r in results if not r["valid"]]
    if failures:
        for item in failures:
            print(f"FAIL {item['file']}: {item['error']}")
        raise SystemExit("Grammar validation failures detected")

    issues = check_evaluation(grammar_path, evaluation_path)
    if issues:
        for issue in issues:
            print(f"EVAL ERROR: {issue}")
        raise SystemExit("Evaluation suite issues detected")

    print("CI checks completed successfully.")


if __name__ == "__main__":
    main()
