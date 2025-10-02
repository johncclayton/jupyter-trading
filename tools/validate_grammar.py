#!/usr/bin/env python3
"""Validate RealTest grammar against sample RTS files."""

import argparse
import json
import pathlib
import re
from typing import Iterable, Sequence

try:
    from lark import Lark, exceptions  # type: ignore
    ParserError = exceptions.LarkError
except ModuleNotFoundError:  # pragma: no cover - fallback path when Lark is absent
    Lark = None

    class ParserError(Exception):
        """Fallback parse exception when Lark is unavailable."""

        pass

    class _Exceptions:
        LarkError = ParserError

    exceptions = _Exceptions()


SECTION_DECL = re.compile(r"SECTION_NAME:\s*(?P<body>.+)")
QUOTED_NAME = re.compile(r'"([^\"]+)"')
SECTION_HEADER = re.compile(r"^(?P<name>[A-Za-z][A-Za-z0-9]*)\s*:")


class SimpleSectionParser:
    """Minimal parser matching the constrained top-level-section grammar."""

    def __init__(self, grammar_text: str) -> None:
        self.section_names = self._extract_sections(grammar_text)

    @staticmethod
    def _extract_sections(grammar_text: str) -> set[str]:
        for line in grammar_text.splitlines():
            match = SECTION_DECL.match(line)
            if match:
                return set(QUOTED_NAME.findall(match.group("body")))
        raise ValueError("SECTION_NAME declaration not found in grammar text")

    def parse(self, text: str) -> None:
        current_section = None
        in_block_comment = False
        for lineno, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.rstrip("\r")
            stripped = line.strip()
            if in_block_comment:
                if "*/" in line:
                    in_block_comment = False
                continue
            if not stripped:
                continue
            if stripped.startswith("//"):
                continue
            if stripped.startswith("/*"):
                if "*/" not in stripped:
                    in_block_comment = True
                continue
            if line[:1] in {" ", "\t"}:
                if current_section is None:
                    raise ParserError(f"Line {lineno}: indented text outside of a section")
                continue
            match = SECTION_HEADER.match(line)
            if match:
                name = match.group("name")
                if name not in self.section_names:
                    raise ParserError(f"Line {lineno}: unknown section '{name}'")
                current_section = name
                continue
            raise ParserError(f"Line {lineno}: unrecognized top-level content")


def load_parser(grammar_text: str):
    if Lark is not None:
        return Lark(grammar_text, start="start", parser="earley", maybe_placeholders=True)
    return SimpleSectionParser(grammar_text)


def parse_files(parser, files: Sequence[pathlib.Path]) -> list[dict]:
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
        except ParserError as exc:
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
    parser = load_parser(grammar_text)
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
