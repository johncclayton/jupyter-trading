#!/usr/bin/env python3
"""Validate RealTest grammar against sample RTS files."""

import argparse
import json
import pathlib
from typing import Iterable, Sequence

from lark import Lark, exceptions


def parse_files(parser: Lark, files: Sequence[pathlib.Path]) -> list[dict]:
    results: list[dict] = []
    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not text.endswith("\n"):
            text += "\n"
        try:
            parser.parse(text)
            results.append({"file": f"samples/{path.name}", "valid": True, "error": None})
        except exceptions.LarkError as exc:
            results.append(
                {
                    "file": f"samples/{path.name}",
                    "valid": False,
                    "error": str(exc).splitlines()[0],
                }
            )
    return results


def validate(grammar_path: pathlib.Path, samples_dir: pathlib.Path) -> list[dict]:
    grammar_text = grammar_path.read_text(encoding="utf-8")
    parser = Lark(grammar_text, start="start", parser="earley", maybe_placeholders=True)
    sample_files = sorted(samples_dir.glob("*.rts"))
    return parse_files(parser, sample_files)


def main() -> None:
    cli = argparse.ArgumentParser(description="Validate grammar against sample scripts")
    cli.add_argument("--grammar", required=True, type=pathlib.Path, help="Path to Lark grammar file")
    cli.add_argument("--samples", required=True, type=pathlib.Path, help="Directory with .rts samples")
    cli.add_argument("--output", required=True, type=pathlib.Path, help="Output JSON report path")
    args = cli.parse_args()

    results = validate(args.grammar, args.samples)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"results": results}, indent=2), encoding="utf-8")

    passed = sum(1 for r in results if r["valid"])
    total = len(results)
    print(f"Grammar validation: {passed}/{total} files parsed successfully")
    failures = [r for r in results if not r["valid"]]
    if failures:
        for item in failures:
            print(f"FAIL {item['file']}: {item['error']}")


if __name__ == "__main__":
    main()
