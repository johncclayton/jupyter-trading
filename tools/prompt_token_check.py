"""Utility to estimate token length of prompt files.

Usage:
    python -m tools.prompt_token_check <path/to/prompt.txt> [--model gpt-4o-mini]

Falls back to a simple 4-characters-per-token heuristic if tiktoken is not
available for the requested model.
"""

from __future__ import annotations

import argparse
import importlib
import math
from pathlib import Path
from typing import Iterable

DEFAULT_MODEL = "gpt-4o-mini"


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt_path", type=Path, help="File containing the prompt text")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name for tokenization (default: {DEFAULT_MODEL})",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def load_prompt(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def count_tokens(prompt: str, model: str) -> tuple[int, str]:
    try:
        tiktoken = importlib.import_module("tiktoken")
    except ModuleNotFoundError:
        estimate = math.ceil(len(prompt) / 4)
        return estimate, "heuristic"  # Approximate assumption.

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(prompt)
    return len(tokens), "tiktoken"


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    prompt_text = load_prompt(args.prompt_path)
    token_count, method = count_tokens(prompt_text, args.model)
    print(f"Prompt: {args.prompt_path}")
    print(f"Model: {args.model}")
    print(f"Tokens ({method}): {token_count}")
    print(f"Characters: {len(prompt_text)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
