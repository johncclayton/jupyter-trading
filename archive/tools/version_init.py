"""Create a new RealTest manual version directory.

This utility prepares a fresh `versions/<YYYYMMDD-realtest-guide>/` folder,
copies the latest RealTest manual into it, and records provenance metadata.

Usage (from repository root):
    python -m tools.version_init

Optional arguments allow overriding the detected manual or version directory,
but the defaults follow the conventions described in plan 0.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_PATTERN = "RealTest*.pdf"
VERSION_SUFFIX = "-realtest-guide"


@dataclass(frozen=True)
class VersionContext:
    repo_root: Path
    source_manual: Path
    version_slug: str
    version_dir: Path
    destination_manual: Path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manual",
        type=Path,
        help=f"Override detected manual (defaults to newest {DEFAULT_PATTERN})",
    )
    parser.add_argument(
        "--versions-dir",
        type=Path,
        default=Path("versions"),
        help="Directory that stores versioned manuals (default: versions)",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help=f"Glob used to discover manuals (default: {DEFAULT_PATTERN})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without creating or copying files",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def discover_manual(repo_root: Path, pattern: str) -> Path:
    candidates = sorted(
        repo_root.glob(pattern),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"No manuals matching {pattern!r} found in {repo_root}")
    return candidates[0]


def derive_version_slug(now: datetime) -> str:
    return now.date().strftime("%Y%m%d") + VERSION_SUFFIX


def build_context(args: argparse.Namespace) -> VersionContext:
    repo_root = Path.cwd()
    source_manual = args.manual.resolve() if args.manual else discover_manual(repo_root, args.pattern)

    if not source_manual.is_file():
        raise FileNotFoundError(f"Manual {source_manual} is not a file")

    try:
        source_manual.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("Manual must reside within the repository root") from exc

    now = datetime.now(timezone.utc)
    version_slug = derive_version_slug(now)
    version_root = (args.versions_dir if args.versions_dir.is_absolute() else repo_root / args.versions_dir)
    version_dir = version_root / version_slug

    return VersionContext(
        repo_root=repo_root,
        source_manual=source_manual,
        version_slug=version_slug,
        version_dir=version_dir,
        destination_manual=version_dir / "manual.pdf",
    )


def ensure_new_directory(ctx: VersionContext, *, dry_run: bool) -> None:
    if ctx.version_dir.exists():
        raise FileExistsError(f"Version directory already exists: {ctx.version_dir}")
    if dry_run:
        print(f"[dry-run] Would create {ctx.version_dir}")
    else:
        ctx.version_dir.mkdir(parents=True, exist_ok=False)


def copy_manual(ctx: VersionContext, *, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] Would copy {ctx.source_manual} -> {ctx.destination_manual}")
        return
    from shutil import copy2

    copy2(ctx.source_manual, ctx.destination_manual)


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_metadata(ctx: VersionContext, *, dry_run: bool) -> None:
    metadata_path = ctx.version_dir / "metadata.json"

    if dry_run:
        print(f"[dry-run] Would write metadata to {metadata_path}")
        return

    copied_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    relative_manual = ctx.source_manual.relative_to(ctx.repo_root)

    payload = {
        "version": ctx.version_slug,
        "source_manual": str(relative_manual.name),
        "source_relative_path": str(relative_manual),
        "copied_at": copied_at,
        "sha256": compute_sha256(ctx.destination_manual),
    }

    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        ctx = build_context(args)
        ensure_new_directory(ctx, dry_run=args.dry_run)
        copy_manual(ctx, dry_run=args.dry_run)
        write_metadata(ctx, dry_run=args.dry_run)
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not args.dry_run:
        print(f"Created version directory: {ctx.version_dir.relative_to(ctx.repo_root)}")
        print(f"Copied manual to: {ctx.destination_manual.relative_to(ctx.repo_root)}")
        print(
            "Wrote metadata to: "
            f"{(ctx.version_dir / 'metadata.json').relative_to(ctx.repo_root)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
