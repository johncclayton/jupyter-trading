#!/usr/bin/env python3
"""Create the RealTest Lark grammar focused on top-level sections."""

import argparse
import json
import pathlib
from typing import Iterable

def extract_section_names(catalog: Iterable[dict]) -> list[str]:
    names: set[str] = set()
    for entry in catalog:
        if entry.get("type") != "section":
            continue
        pattern = entry.get("pattern", "")
        if not pattern.startswith("^"):
            continue
        remainder = pattern[1:]
        collected: list[str] = []
        for ch in remainder:
            if ch.isalnum() or ch == "_":
                collected.append(ch)
            else:
                break
        if collected:
            names.add("".join(collected))
    if not names:
        raise ValueError("No section entries found in syntax catalog")
    return sorted(names)


def build_lark_grammar(sections: Iterable[str]) -> str:
    options = " | ".join(f'"{name}"' for name in sections)
    return f"""%import common.NEWLINE
%ignore /\\r/
%ignore /\\/\\*.*?\\*\\//s

start: element*

?element: section
        | commentline
        | blankline

section: SECTION_NAME ":" inline_content? NEWLINE section_body?
inline_content: INLINE_TEXT

section_body: section_line+
section_line: INDENTED_TEXT NEWLINE

commentline: COMMENT_LINE NEWLINE
blankline: WS_INLINE? NEWLINE

SECTION_NAME: {options}
INLINE_TEXT: /[^\\r\\n]+/
INDENTED_TEXT: /[ \\t]+[^\\n]*/
COMMENT_LINE: /[ \\t]*\\/\\/[^\\n]*/
WS_INLINE: /[ \\t]+/
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RealTest Lark grammar")
    parser.add_argument("--version-dir", required=True, type=pathlib.Path, help="Version directory")
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

    catalog_path = version_dir / "syntax_catalog.json"
    if not catalog_path.exists():
        parser.error(f"Syntax catalog not found: {catalog_path}")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    section_names = extract_section_names(catalog)

    lark_text = build_lark_grammar(section_names).strip() + "\n"

    lark_path = version_dir / "realtest_grammar.lark"
    lark_path.write_text(lark_text, encoding="utf-8")
    print(f"Wrote {to_relative(lark_path)} with {len(section_names)} section rules")

    # Remove superseded grammar artifacts if present.
    for obsolete in ("realtest_grammar.json", "realtest_grammar.g4"):
        path = version_dir / obsolete
        if path.exists():
            path.unlink()
            print(f"Removed {to_relative(path)}")


if __name__ == "__main__":
    main()
