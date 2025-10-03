#!/usr/bin/env python3
"""Create the RealTest Lark grammar with section items and expressions."""

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
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%ignore WS_INLINE
%ignore /\\r/
%ignore /\\/\\*.*?\\*\\//s

COMMENT: /\\/\\/[^\\n]*/

start: element*

?element: section
        | commentline
        | blankline

section: SECTION_NAME ":" inline_section_value? COMMENT? NEWLINE section_body?
inline_section_value: value

section_body: section_entry*

section_entry: indented_statement
             | indented_comment
             | indented_text
             | blankline

indented_statement: INDENT statement COMMENT? NEWLINE
indented_comment: INDENT COMMENT NEWLINE
indented_text: INDENT TEXT_CONTENT NEWLINE

statement: assignment | bare_expression
assignment: assignment_target assignment_operator value?
assignment_operator: ":" | ":="
bare_expression: value

assignment_target: assignment_atom assignment_suffix*
assignment_atom: NAME
assignment_suffix: "." NAME
                | "(" parameter_list? ")"

parameter_list: NAME ("," NAME)*

value: expression_list | free_text
expression_list: expression ("," expression)*
free_text: TEXT_CONTENT

?expression: conditional
?conditional: logical_or ("?" expression ":" expression)?
?logical_or: logical_and (OR logical_and)*
?logical_and: comparison (AND comparison)*
?comparison: sum (COMPARISON_OP sum)*
?sum: sum ADD_OP term
     | term
?term: term MUL_OP power
     | power
?power: unary (POW_OP unary)*
?unary: ADD_OP unary
      | NOT unary
      | primary

?primary: atom trailer*
trailer: "." NAME
       | "[" expression "]"

?atom: function_call
     | aggregator_call
     | at_reference
     | symbol_reference
     | amp_reference
     | placeholder
     | literal
     | NAME
     | "(" expression ")"

function_call: NAME "(" argument_list? ")"
argument_list: argument ("," argument)* (",")?
argument: leading_break? expression
leading_break: (NEWLINE INDENT)+

aggregator_call: HASH_NAME aggregator_args
aggregator_args: "(" argument_list? ")" | argument

literal: NUMBER
       | STRING
       | DATE
       | TRUE
       | FALSE

at_reference: AT_REFERENCE
symbol_reference: SYMBOL_REFERENCE
amp_reference: AMP_REFERENCE
placeholder: PLACEHOLDER

blankline: (INDENT)? NEWLINE
commentline: COMMENT NEWLINE

INDENT.2: /(?m)^[ \\t]+/
WS_INLINE: /[ \\t]+/
TEXT_CONTENT: /[^\\r\\n]+?(?=\\s+\\/\\/|$)/
NUMBER: SIGNED_NUMBER
STRING: ESCAPED_STRING
DATE: /\\d{{4}}-\\d{{2}}-\\d{{2}}/
AT_REFERENCE: /@[A-Za-z_][A-Za-z0-9_]*/
SYMBOL_REFERENCE: /\\$(?:&?-?[A-Za-z0-9_]+)/
AMP_REFERENCE: /&-?[A-Za-z0-9_]+/
PLACEHOLDER: /\\?[A-Za-z_][A-Za-z0-9_]*\\?(?:[^\\s,\\r\\n]*)?/

AND: /(?i)and/
OR: /(?i)or/
NOT: /(?i)not/
TRUE: /(?i)true/
FALSE: /(?i)false/

COMPARISON_OP: "<>" | "==" | "!=" | ">=" | "<=" | "=" | ">" | "<"
ADD_OP: "+" | "-"
MUL_OP: "*" | "/" | "%"
POW_OP: "^"

HASH_NAME: /#[A-Za-z_][A-Za-z0-9_]*/
SECTION_NAME.3: {options}
NAME: /[A-Za-z_][A-Za-z0-9_]*/
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
