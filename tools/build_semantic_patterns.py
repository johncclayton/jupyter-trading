#!/usr/bin/env python3
"""Construct semantic trading patterns catalog."""

import argparse
import json
import pathlib
import re
from typing import Iterable, Sequence

PATTERN_CONFIG = [
    {
        "pattern": "Momentum Filter",
        "description": "Only trade when the asset trades above a long-term moving average or similar momentum condition.",
        "sample_patterns": [r"EntrySetup", r"MA\s*\("],
        "relatedFunctions": ["MA", "EntrySetup"],
        "snippet": "Strategy: MomentumFilter\n    EntrySetup: C > MA(C, 200)"
    },
    {
        "pattern": "Rank And Allocate",
        "description": "Rank candidates by momentum (EntryScore) and allocate up to a defined number of positions.",
        "sample_patterns": [r"EntryScore", r"MaxEntries"],
        "relatedFunctions": ["EntryScore", "ROC", "MaxEntries"],
        "snippet": "Strategy: RankAllocate\n    EntrySetup: C > MA(C, 150)\n    EntryScore: ROC(C, 63)\n    MaxEntries: 5"
    },
    {
        "pattern": "Drawdown Guard",
        "description": "Suspend entries while a drawdown metric exceeds a threshold.",
        "sample_patterns": [r"EntrySkip", r"Highest"],
        "relatedFunctions": ["Highest", "EntrySkip"],
        "snippet": "Data:\n    MarketDrawdown: (Highest(C, 252) - C) / Highest(C, 252)\nStrategy: GuardedEntries\n    EntrySkip: MarketDrawdown > 0.15"
    },
    {
        "pattern": "Volatility Position Sizing",
        "description": "Scale position size inversely to volatility (ATR) to target consistent risk.",
        "sample_patterns": [r"ATR", r"PositionSize"],
        "relatedFunctions": ["ATR", "PositionSize"],
        "snippet": "Strategy: VolAdjust\n    Volatility: ATR(14)\n    PositionSize: (0.01 * S.Equity) / Volatility"
    },
    {
        "pattern": "Static Allocation",
        "description": "Use Parameters and Item() to distribute capital across fixed-weight sleeves (All Weather style).",
        "sample_patterns": [r"Parameters", r"Item\s*\(", r"QtyType"],
        "relatedFunctions": ["Item", "Quantity", "QtyType"],
        "snippet": "Parameters:\n    allocSPY: 30\n    allocTLT: 40\nStrategy: AllWeather\n    Quantity: Item(\"alloc{?}\", ?symbol)\n    QtyType: Percent"
    }
]


def find_sources(patterns: Sequence[str], files: Iterable[pathlib.Path]) -> list[str]:
    hits: list[str] = []
    compiled = [re.compile(pat, re.IGNORECASE) for pat in patterns]
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines):
            if all(regex.search(line) for regex in compiled):
                hits.append(f"samples/{path.name}:{idx + 1}")
                break
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Build semantic patterns catalog")
    parser.add_argument("--version-dir", required=True, type=pathlib.Path, help="Version directory")
    parser.add_argument("--samples", required=True, type=pathlib.Path, help="Samples directory")
    parser.add_argument("--output", required=True, type=pathlib.Path, help="Destination JSON path")
    args = parser.parse_args()

    sample_files = sorted(args.samples.glob("*.rts"))

    entries = []
    for cfg in PATTERN_CONFIG:
        sources = find_sources(cfg["sample_patterns"], sample_files)
        if not sources:
            sources = ["samples:N/A"]
        entries.append(
            {
                "pattern": cfg["pattern"],
                "description": cfg["description"],
                "snippet": cfg["snippet"],
                "relatedFunctions": cfg["relatedFunctions"],
                "sources": sources,
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} with {len(entries)} patterns")


if __name__ == "__main__":
    main()
