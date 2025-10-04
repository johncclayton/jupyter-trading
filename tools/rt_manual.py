"""CLI utilities for processing the RealTest manual.

Current subcommands:
- extract-text: convert a versioned manual PDF to normalized plain text.
- build-structure: derive section hierarchy and glossary candidates.

Place this module inside the `realtestextract` virtual environment to ensure
the required dependencies (notably `pypdf`) are available.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Callable

import re

from pypdf import PdfReader


DEFAULT_VERSIONS_DIR = Path("versions")


@dataclass(frozen=True)
class CLIContext:
    repo_root: Path
    versions_dir: Path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RealTest manual tooling")
    parser.add_argument(
        "--versions-dir",
        type=Path,
        default=DEFAULT_VERSIONS_DIR,
        help="Directory containing versioned manuals (default: versions)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser(
        "extract-text",
        help="Extract normalized text from a manual PDF",
    )
    extract_parser.add_argument(
        "--version",
        help="Version slug (defaults to latest version directory)",
    )
    extract_parser.add_argument(
        "--force",
        action="store_true",
        help="Write output even if manual.txt already matches the PDF",
    )

    # Placeholders for forthcoming functionality.
    structure_parser = subparsers.add_parser(
        "build-structure",
        help="Generate manual_structure.json from manual.txt",
    )
    structure_parser.add_argument(
        "--version",
        help="Version slug (defaults to latest version directory)",
    )

    catalog_parser = subparsers.add_parser(
        "build-function-catalog",
        help="Generate function_catalog.json from manual text",
    )
    catalog_parser.add_argument(
        "--version",
        help="Version slug (defaults to latest version directory)",
    )
    catalog_parser.add_argument(
        "--samples-dir",
        type=Path,
        default=Path("samples"),
        help="Directory containing RealTest sample scripts",
    )
    catalog_parser.add_argument(
        "--max-examples",
        type=int,
        default=3,
        help="Maximum sample snippets to attach to each entry (default: 3)",
    )

    return parser.parse_args(list(argv) if argv is not None else None)


def build_context(args: argparse.Namespace) -> CLIContext:
    repo_root = Path.cwd()
    versions_dir = args.versions_dir
    if not versions_dir.is_absolute():
        versions_dir = repo_root / versions_dir
    return CLIContext(repo_root=repo_root, versions_dir=versions_dir)


def discover_version_dir(ctx: CLIContext, version_slug: str | None) -> Path:
    if version_slug:
        target = ctx.versions_dir / version_slug
        if not target.is_dir():
            raise FileNotFoundError(f"Version directory not found: {target}")
        return target

    candidates = sorted(
        [path for path in ctx.versions_dir.glob("*" ) if path.is_dir()],
        key=lambda path: path.name,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"No version directories found in {ctx.versions_dir}")
    return candidates[0]


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    chunks = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        chunks.append(page_text.rstrip())
    return "\n\n".join(chunks)


def normalize_text(raw: str) -> str:
    # Collapse CRLF/CR to LF and trim trailing whitespace while preserving structure.
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    stripped_lines = [line.rstrip() for line in lines]
    normalized = "\n".join(stripped_lines)
    return normalized if normalized.endswith("\n") else normalized + "\n"


def hash_path(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manual_lines(manual_txt: Path) -> list[str]:
    return manual_txt.read_text(encoding="utf-8").splitlines()


def next_meaningful_line(lines: list[str], start_index: int) -> str | None:
    for idx in range(start_index + 1, len(lines)):
        candidate = lines[idx].strip()
        if not candidate:
            continue
        if candidate.isdigit():
            continue
        return candidate
    return None


HEADING_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\.\s+(.*\S)")


def extract_sections(lines: list[str]) -> list[dict[str, object]]:
    sections: list[dict[str, object]] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        match = HEADING_PATTERN.match(stripped)
        if not match:
            continue

        following = next_meaningful_line(lines, idx)
        if following and set(following) <= {"."}:
            # Table-of-contents entry; real section text has prose instead of dot leaders.
            continue

        number = match.group(1)
        title = match.group(2).strip()
        depth = number.count(".") + 1

        sections.append(
            {
                "number": number,
                "title": title,
                "depth": depth,
                "source_line": idx + 1,
            }
        )

    return sections


SECTION_NUMBER_PATTERN = re.compile(r"^\d+(?:\.\d+)*\.")


def extract_glossary(lines: list[str]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for idx, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped:
            continue

        is_bullet = stripped.startswith(("-", "•", "·")) or "·" in raw_line
        if not is_bullet:
            continue

        segments = [seg.strip() for seg in raw_line.split("·") if seg.strip()]
        if not segments:
            segments = [raw_line]

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
            segment = segment.lstrip("-•").strip()
            if " - " not in segment:
                continue

            term, definition = segment.split(" - ", 1)
            term = term.strip()
            definition = definition.strip()

            if not term or not definition:
                continue
            if SECTION_NUMBER_PATTERN.match(term):
                continue
            if term[0].isdigit():
                continue

            if len(definition) > 200:
                marker_match = re.search(
                    r"([a-z])((The|This|These|While|Please|As|In)\s)",
                    definition,
                )
                if marker_match:
                    definition = definition[: marker_match.start(2)].rstrip()

            entries.append(
                {
                    "term": term,
                    "definition": definition,
                    "source_line": idx + 1,
                }
            )

    return entries


def load_section_records(structure: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    stack: list[dict[str, object]] = []
    for raw in structure:
        depth = raw["depth"]
        while stack and stack[-1]["depth"] >= depth:
            stack.pop()

        record = {
            "number": raw["number"],
            "title": raw["title"],
            "depth": depth,
            "source_line": raw["source_line"],
            "index": len(records),
            "ancestors": [node["title"] for node in stack],
        }

        record["parent"] = stack[-1]["number"] if stack else None

        records.append(record)
        stack.append(record)

    return records


def section_content(record: dict[str, object], records: list[dict[str, object]], lines: list[str]) -> list[str]:
    start = int(record["source_line"]) - 1
    end = len(lines)
    for sibling in records[record["index"] + 1 :]:
        if sibling["depth"] <= record["depth"]:
            end = int(sibling["source_line"]) - 1
            break
    return lines[start:end]


SECTION_KEYWORDS = ["Category", "Description", "Example", "Notes", "See also", "Syntax", "Parameters"]


def parse_section_segments(content_lines: list[str]) -> dict[str, list[str]]:
    filtered: list[str] = []
    for line in content_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.isdigit():
            continue
        if set(stripped) <= {"."}:
            continue
        if re.match(r"^\d+\.\d+.*", stripped):
            continue
        filtered.append(stripped)

    if not filtered:
        return {}

    block = " ".join(filtered)
    block = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", block)
    block = re.sub(r"(?<=\))(?=[A-Z])", " ", block)
    block = re.sub(r"\s+", " ", block).strip()
    segments: dict[str, list[str]] = {}

    positions: list[tuple[int, str]] = []
    for keyword in SECTION_KEYWORDS:
        pattern = re.compile(rf"\b{keyword}\b", re.IGNORECASE)
        for match in pattern.finditer(block):
            positions.append((match.start(), keyword.lower()))

    if not positions:
        segments["raw"] = [block]
        return segments

    positions.sort()
    for idx, (pos, key) in enumerate(positions):
        next_pos = positions[idx + 1][0] if idx + 1 < len(positions) else len(block)
        value = block[pos + len(key) : next_pos].strip()
        if value:
            segments.setdefault(key, []).append(value)

    return segments


def derive_tokens(title: str) -> list[str]:
    parts = re.split(r"\bor\b|\band\b|/|,", title)
    tokens: list[str] = []
    for part in parts:
        token = part.strip()
        if not token:
            continue
        token = token.strip("()")
        if token:
            tokens.append(token)
    return tokens or [title]


def load_sample_files(samples_dir: Path) -> list[tuple[Path, list[str]]]:
    if not samples_dir.exists() or not samples_dir.is_dir():
        return []

    sample_files: list[tuple[Path, list[str]]] = []
    for path in sorted(samples_dir.rglob("*.rts")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
        sample_files.append((path, text.splitlines()))
    return sample_files


def find_sample_examples(
    tokens: list[str],
    samples: list[tuple[Path, list[str]]],
    repo_root: Path,
    limit: int,
) -> list[dict[str, object]]:
    if limit <= 0:
        return []

    results: list[dict[str, object]] = []
    lowered_tokens = [token.lower() for token in tokens if token]
    seen = 0
    for path, lines in samples:
        rel_path = path.relative_to(repo_root).as_posix()
        for idx, line in enumerate(lines):
            lowered_line = line.lower()
            if any(token in lowered_line for token in lowered_tokens):
                results.append(
                    {
                        "file": rel_path,
                        "line": idx + 1,
                        "code": line.strip(),
                    }
                )
                seen += 1
                if seen >= limit:
                    return results
                break
    return results


def sentence_trim(text: str, limit: int = 600) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    truncated = text[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return truncated + "…"


def normalize_segment(values: list[str] | None, limit: int = 600) -> str | None:
    if not values:
        return None
    merged = " ".join(values)
    return sentence_trim(merged, limit=limit)


def normalize_list_segment(values: list[str] | None) -> list[str]:
    if not values:
        return []
    text = " ".join(values)
    items = re.split(r"[,;]", text)
    cleaned: list[str] = []
    for item in items:
        token = item.strip()
        if not token:
            continue
        cleaned.append(token)
    return cleaned


def grammar_contains(token: str, grammar_text: str) -> bool:
    if not token:
        return False
    variants = {token, token.upper(), token.lower()}
    for variant in variants:
        if variant and variant in grammar_text:
            return True
    return False


def append_runlog(version_dir: Path, entry: dict) -> None:
    runlog_path = version_dir / "runlog.json"
    if runlog_path.exists():
        try:
            history = json.loads(runlog_path.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
        except json.JSONDecodeError:
            history = []
    else:
        history = []
    history.append(entry)
    runlog_path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")


def action_extract_text(ctx: CLIContext, args: argparse.Namespace) -> int:
    version_dir = discover_version_dir(ctx, args.version)
    manual_pdf = version_dir / "manual.pdf"
    if not manual_pdf.is_file():
        raise FileNotFoundError(f"Manual PDF not found: {manual_pdf}")

    manual_txt = version_dir / "manual.txt"

    extracted = extract_pdf_text(manual_pdf)
    normalized = normalize_text(extracted)

    existing = manual_txt.read_text(encoding="utf-8") if manual_txt.exists() else None
    if not args.force and existing is not None and existing == normalized:
        print(f"manual.txt already up to date for {version_dir.name}; skipping write")
        written = False
    else:
        manual_txt.write_text(normalized, encoding="utf-8")
        written = True

    pdf_hash = hash_path(manual_pdf)
    txt_hash = hash_path(manual_txt) if manual_txt.exists() else None

    append_runlog(
        version_dir,
        {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "action": "extract-text",
            "manual_pdf": manual_pdf.relative_to(ctx.repo_root).as_posix(),
            "manual_txt": manual_txt.relative_to(ctx.repo_root).as_posix(),
            "pdf_sha256": pdf_hash,
            "txt_sha256": txt_hash,
            "wrote_output": written,
        },
    )

    sample = "\n".join(normalized.splitlines()[:5])
    print(f"Extracted {'(unchanged)' if not written else '-> ' + manual_txt.name}")
    print(f"Characters: {len(normalized)}")
    print("Preview:")
    print(sample)
    return 0


def action_build_structure(ctx: CLIContext, args: argparse.Namespace) -> int:
    version_dir = discover_version_dir(ctx, args.version)
    manual_txt = version_dir / "manual.txt"
    if not manual_txt.is_file():
        raise FileNotFoundError(
            f"Manual text not found: {manual_txt}. Run 'extract-text' first."
        )

    lines = read_manual_lines(manual_txt)
    sections = extract_sections(lines)
    glossary = extract_glossary(lines)

    structure_path = version_dir / "manual_structure.json"
    payload = {
        "sections": sections,
        "glossary": glossary,
    }
    serialized = json.dumps(payload, indent=2) + "\n"

    existing = structure_path.read_text(encoding="utf-8") if structure_path.exists() else None
    if existing == serialized:
        wrote = False
    else:
        structure_path.write_text(serialized, encoding="utf-8")
        wrote = True

    append_runlog(
        version_dir,
        {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "action": "build-structure",
            "manual_txt": manual_txt.relative_to(ctx.repo_root).as_posix(),
            "manual_structure": structure_path.relative_to(ctx.repo_root).as_posix(),
            "section_count": len(sections),
            "glossary_count": len(glossary),
            "txt_sha256": hash_path(manual_txt),
            "wrote_output": wrote,
        },
    )

    print(f"Sections found: {len(sections)}")
    print(f"Glossary entries: {len(glossary)}")
    print(f"manual_structure.json {'updated' if wrote else 'unchanged'}")
    return 0


def action_build_function_catalog(ctx: CLIContext, args: argparse.Namespace) -> int:
    version_dir = discover_version_dir(ctx, args.version)
    manual_txt = version_dir / "manual.txt"
    structure_path = version_dir / "manual_structure.json"
    if not manual_txt.is_file():
        raise FileNotFoundError(
            f"Manual text not found: {manual_txt}. Run 'extract-text' first."
        )
    if not structure_path.is_file():
        raise FileNotFoundError(
            f"Structure file not found: {structure_path}. Run 'build-structure' first."
        )

    samples_dir = args.samples_dir
    if not samples_dir.is_absolute():
        samples_dir = ctx.repo_root / samples_dir

    max_examples = max(args.max_examples, 0)

    lines = read_manual_lines(manual_txt)
    structure_data = json.loads(structure_path.read_text(encoding="utf-8"))
    records = load_section_records(structure_data.get("sections", []))

    samples = load_sample_files(samples_dir)
    grammar_path = ctx.repo_root / "bnf" / "lark" / "realtest.lark"
    grammar_text = (
        grammar_path.read_text(encoding="utf-8")
        if grammar_path.exists()
        else ""
    )

    entries: list[dict[str, object]] = []
    for record in records:
        if record["depth"] < 3:
            continue
        if not record["number"].startswith("17.18."):
            continue

        content_lines = section_content(record, records, lines)
        segments = parse_section_segments(content_lines)

        tokens = derive_tokens(record["title"])
        name = tokens[0] if tokens else record["title"]
        aliases = [alias for alias in tokens[1:] if alias != name]

        category = normalize_segment(segments.get("category"))
        if not category and record["ancestors"]:
            category = record["ancestors"][-1]

        description = normalize_segment(segments.get("description"))
        if not description and "raw" in segments:
            description = normalize_segment(segments.get("raw"))

        example = normalize_segment(segments.get("example"), limit=400)
        notes = normalize_segment(segments.get("notes"))
        see_also = normalize_list_segment(segments.get("see also"))

        sample_examples = find_sample_examples(tokens, samples, ctx.repo_root, max_examples)
        grammar_match = any(grammar_contains(token, grammar_text) for token in tokens)

        entry = {
            "name": name,
            "title": record["title"],
            "aliases": aliases,
            "section": record["number"],
            "hierarchy": record["ancestors"],
            "category": category,
            "description": description,
            "example": example,
            "notes": notes,
            "see_also": see_also,
            "manual_refs": [
                {
                    "section": record["number"],
                    "title": record["title"],
                    "line": record["source_line"],
                }
            ],
            "sample_examples": sample_examples,
            "grammar_match": grammar_match,
        }

        entries.append(entry)

    merged: dict[str, dict[str, object]] = {}
    for entry in entries:
        key = entry["name"]
        existing = merged.get(key)
        if not existing:
            merged[key] = entry
            continue

        existing_aliases = set(existing.get("aliases", []))
        for alias in entry.get("aliases", []):
            if alias not in existing_aliases:
                existing_aliases.add(alias)
        existing["aliases"] = sorted(existing_aliases)

        existing["manual_refs"].extend(entry.get("manual_refs", []))

        existing_samples = existing.get("sample_examples", [])
        existing_samples.extend(entry.get("sample_examples", []))
        existing["sample_examples"] = existing_samples[: max_examples]

        existing["grammar_match"] = existing.get("grammar_match") or entry.get("grammar_match")

        if not existing.get("description") and entry.get("description"):
            existing["description"] = entry["description"]
        if not existing.get("example") and entry.get("example"):
            existing["example"] = entry["example"]
        if not existing.get("notes") and entry.get("notes"):
            existing["notes"] = entry["notes"]

    final_entries = sorted(merged.values(), key=lambda item: item["name"].lower())

    category_counts: dict[str, int] = {}
    grammar_hits = 0
    sample_hits = 0
    for item in final_entries:
        category_key = item.get("category") or "Uncategorized"
        category_counts[category_key] = category_counts.get(category_key, 0) + 1
        if item.get("grammar_match"):
            grammar_hits += 1
        if item.get("sample_examples"):
            sample_hits += 1

    summary = {
        "total_entries": len(final_entries),
        "category_counts": category_counts,
        "grammar_matches": grammar_hits,
        "entries_with_samples": sample_hits,
    }

    payload = {
        "version": version_dir.name,
        "generated_at": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "source_manual": manual_txt.relative_to(ctx.repo_root).as_posix(),
        "entries": final_entries,
        "summary": summary,
    }

    catalog_path = version_dir / "function_catalog.json"
    serialized = json.dumps(payload, indent=2) + "\n"
    existing = catalog_path.read_text(encoding="utf-8") if catalog_path.exists() else None
    wrote = serialized != existing
    if wrote:
        catalog_path.write_text(serialized, encoding="utf-8")

    append_runlog(
        version_dir,
        {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "action": "build-function-catalog",
            "manual_txt": manual_txt.relative_to(ctx.repo_root).as_posix(),
            "manual_structure": structure_path.relative_to(ctx.repo_root).as_posix(),
            "function_catalog": catalog_path.relative_to(ctx.repo_root).as_posix(),
            "entry_count": len(final_entries),
            "grammar_matches": grammar_hits,
            "entries_with_samples": sample_hits,
            "txt_sha256": hash_path(manual_txt),
            "structure_sha256": hash_path(structure_path),
            "wrote_output": wrote,
        },
    )

    print(f"Function catalog entries: {len(final_entries)}")
    print(f"Categories detected: {len(category_counts)}")
    print(f"Grammar matches: {grammar_hits}")
    print(
        f"Entries with sample snippets: {sample_hits}" +
        ("" if sample_hits else " (no matches found in samples)")
    )
    print(f"function_catalog.json {'updated' if wrote else 'unchanged'}")
    return 0


def action_not_implemented(command: str) -> Callable[[CLIContext, argparse.Namespace], int]:
    def runner(__ctx: CLIContext, __args: argparse.Namespace) -> int:
        raise NotImplementedError(f"Command '{command}' is not implemented yet")

    return runner


COMMANDS: dict[str, Callable[[CLIContext, argparse.Namespace], int]] = {
    "extract-text": action_extract_text,
    "build-structure": action_build_structure,
    "build-function-catalog": action_build_function_catalog,
}


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    ctx = build_context(args)

    try:
        handler = COMMANDS[args.command]
        return handler(ctx, args)
    except NotImplementedError as exc:
        print(exc, file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
