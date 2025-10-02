#!/usr/bin/env python3
"""Create RealTest grammar artifacts (JSON + Lark PEG + ANTLR)."""

import argparse
import json
import pathlib

GRAMMAR_JSON = {
    "nonterminals": [
        "script",
        "line",
        "statement",
        "keyvalue",
        "keyonly",
        "comment",
        "textline",
    ],
    "terminals": [
        "KEY",
        "VALUE",
        "WS",
        "COMMENT",
        "TEXT",
        "NEWLINE",
    ],
    "productions": [
        {
            "lhs": "script",
            "rhs": ["line*"],
            "description": "A RealTest script is parsed as a sequence of lines (each optional statement followed by a newline).",
        },
        {
            "lhs": "line",
            "rhs": ["statement?", "NEWLINE"],
            "description": "Lines may be blank (no statement) or contain one of the defined statements.",
        },
        {
            "lhs": "statement",
            "rhs": ["comment"],
            "description": "Comment lines begin with optional whitespace followed by // text.",
        },
        {
            "lhs": "statement",
            "rhs": ["keyvalue"],
            "description": "Key/value lines follow the pattern KEY : VALUE (value optional).",
        },
        {
            "lhs": "statement",
            "rhs": ["keyonly"],
            "description": "Section headers such as `Import:` with no inline value.",
        },
        {
            "lhs": "statement",
            "rhs": ["textline"],
            "description": "Free-form text lines (e.g., multi-line notes) without a colon.",
        },
        {
            "lhs": "keyvalue",
            "rhs": ["WS?", "KEY", "COLON", "WS?", "VALUE?"],
            "description": "Accepts optional leading spaces, colon delimiter, and trailing value payload.",
        },
        {
            "lhs": "keyonly",
            "rhs": ["WS?", "KEY", "COLON"],
            "description": "Handles section headers that rely on indentation for their body.",
        },
        {
            "lhs": "comment",
            "rhs": ["WS?", "COMMENT"],
            "description": "Whitespace followed by // comment text up to end of line.",
        },
        {
            "lhs": "textline",
            "rhs": ["WS?", "TEXT"],
            "description": "Lines without a colon are captured as TEXT after optional indentation.",
        },
    ],
    "notes": [
        "The PEG grammar is intentionally permissive, treating RealTest as a key/value language while preserving full line content in VALUE or TEXT tokens.",
        "Indentation semantics are not enforced; downstream tooling can interpret VALUE/TEXT strings for nested meaning.",
        "Both Lark (PEG) and ANTLR grammars are emitted for downstream tooling integration.",
    ],
}

LARK_GRAMMAR = r"""%import common.NEWLINE
%ignore /\r/

start: (line)*

line: statement? NEWLINE

?statement: comment
          | keyvalue
          | keyonly
          | textline

keyvalue: WS? KEY ":" WS? VALUE?
keyonly: WS? KEY ":"
comment: WS? COMMENT
textline: WS? TEXT

KEY: /[A-Za-z][A-Za-z0-9_.?]*/
VALUE: /[^\n]+/
TEXT: /[^:\n][^\n]*/
WS: /[ \t]+/
COMMENT: /\/\/[^\n]*/
"""

ANTLR_GRAMMAR = r"""grammar RealTest;

script  : line* EOF ;
line    : statement? NEWLINE ;

statement
        : comment
        | keyvalue
        | keyonly
        | textline
        ;

keyvalue: WS? KEY ':' WS? VALUE? ;
keyonly : WS? KEY ':' ;
textline: WS? TEXT ;
comment : WS? COMMENT ;

KEY     : [A-Za-z] [A-Za-z0-9_.?]* ;
VALUE   : ~[\r\n]+ ;
TEXT    : ~[:\r\n] ~[\r\n]* ;
COMMENT : '//' ~[\r\n]* ;
WS      : [ \t]+ -> skip ;
NEWLINE : '\r'? '\n' ;
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RealTest grammar artifacts")
    parser.add_argument("--version-dir", required=True, type=pathlib.Path, help="Version directory")
    args = parser.parse_args()

    version_dir = args.version_dir.expanduser().resolve()
    if not version_dir.exists():
        parser.error(f"Version directory not found: {version_dir}")

    json_path = version_dir / "realtest_grammar.json"
    lark_path = version_dir / "realtest_grammar.lark"
    antlr_path = version_dir / "realtest_grammar.g4"

    json_path.write_text(json.dumps(GRAMMAR_JSON, indent=2), encoding="utf-8")
    lark_path.write_text(LARK_GRAMMAR.strip() + "\n", encoding="utf-8")
    antlr_path.write_text(ANTLR_GRAMMAR.strip() + "\n", encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {lark_path}")
    print(f"Wrote {antlr_path}")


if __name__ == "__main__":
    main()
