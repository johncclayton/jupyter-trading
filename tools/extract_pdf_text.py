#!/usr/bin/env python3
"""Extract full text from a PDF into a UTF-8 text file.

Usage:
    python extract_pdf_text.py input.pdf [--output output.txt]

The script reads every page with pypdf and writes concatenated text to the
specified output path (defaults to the input path with a .txt suffix).
"""

import argparse
import pathlib
import sys

from pypdf import PdfReader


def extract_text(pdf_path: pathlib.Path) -> str:
    reader = PdfReader(str(pdf_path))
    chunks = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            chunks.append(text)
    return "".join(chunks)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Extract PDF text to UTF-8 file")
    parser.add_argument("pdf", type=pathlib.Path, help="Path to the PDF file")
    parser.add_argument(
        "--output",
        "-o",
        type=pathlib.Path,
        help="Destination text file (defaults to input with .txt extension)",
    )
    args = parser.parse_args(argv)

    repo_root = pathlib.Path.cwd().resolve()

    def to_relative(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root))
        except ValueError:
            raise SystemExit(
                f"Path {path} is outside the repository root {repo_root}; cannot emit absolute paths."
            )

    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        parser.error(f"PDF not found: {pdf_path}")

    output_path = args.output
    if output_path is None:
        output_path = pdf_path.with_suffix(".txt")
    else:
        output_path = output_path.expanduser().resolve()
        if output_path.is_dir():
            output_path = output_path / pdf_path.with_suffix(".txt").name

    text = extract_text(pdf_path)
    output_path.write_text(text, encoding="utf-8")
    print(
        f"Extracted {len(text)} characters from {to_relative(pdf_path)} -> {to_relative(output_path)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
