#!/usr/bin/env python3
"""Compile RealTest functions, directives, and statements catalog."""

import argparse
import json
import pathlib
import re
from typing import Iterable, List

ENTRY_CONFIG = [
    {
        "name": "MA",
        "category": "function",
        "pattern": r"MA\s*\(",
        "signature": "MA(series, length)",
        "description": "Simple moving average across the specified lookback.",
        "snippet": "Data:\n    SPY_MA200: MA(C, 200)"
    },
    {
        "name": "ROC",
        "category": "function",
        "pattern": r"ROC\s*\(",
        "signature": "ROC(series, length)",
        "description": "Percentage rate of change over the lookback period.",
        "snippet": "Data:\n    Momentum63: ROC(C, 63)"
    },
    {
        "name": "CrossesAbove",
        "category": "function",
        "pattern": r"CrossesAbove\s*\(",
        "signature": "CrossesAbove(series1, series2)",
        "description": "True when series1 crosses from below to above series2.",
        "snippet": "Strategy: Trend\n    EntrySetup: CrossesAbove(C, MA(C, 50))"
    },
    {
        "name": "CrossesBelow",
        "category": "function",
        "pattern": r"CrossesBelow\s*\(",
        "signature": "CrossesBelow(series1, series2)",
        "description": "True when series1 crosses from above to below series2.",
        "snippet": "ExitRule: CrossesBelow(C, MA(C, 90))"
    },
    {
        "name": "Extern",
        "category": "function",
        "pattern": r"Extern\s*\(",
        "signature": "Extern(selector, expression)",
        "description": "Evaluates an expression on a different symbol or timeframe.",
        "snippet": "Data:\n    SPY_weekly: Extern(~Weekly, C)"
    },
    {
        "name": "Highest",
        "category": "function",
        "pattern": r"Highest\s*\(",
        "signature": "Highest(series, length)",
        "description": "Maximum value of a series over the window.",
        "snippet": "Data:\n    Peak252: Highest(C, 252)"
    },
    {
        "name": "Lowest",
        "category": "function",
        "pattern": r"Lowest\s*\(",
        "signature": "Lowest(series, length)",
        "description": "Minimum value of a series over the window.",
        "snippet": "Data:\n    Trough20: Lowest(C, 20)"
    },
    {
        "name": "ATR",
        "category": "function",
        "pattern": r"ATR\s*\(",
        "signature": "ATR(length)",
        "description": "Average True Range volatility indicator.",
        "snippet": "Data:\n    Volatility14: ATR(14)"
    },
    {
        "name": "EndOfMonth",
        "category": "function",
        "pattern": r"EndOfMonth",
        "signature": "EndOfMonth",
        "description": "Condition true on the last trading day of the month.",
        "snippet": "Strategy: AllWeather\n    EntrySetup: EndOfMonth"
    },
    {
        "name": "Item",
        "category": "function",
        "pattern": r"Item\s*\(",
        "signature": "Item(pattern, value)",
        "description": "Returns a formatted parameter or series entry (often used with Parameters section).",
        "snippet": "Quantity: Item(\"alloc{?}\", ?symbol)"
    },
    {
        "name": "IncludeList",
        "category": "directive",
        "pattern": r"IncludeList\s*:",
        "signature": "IncludeList: symbols | path | watchlist",
        "description": "Defines which symbols are included for import or strategy universe.",
        "snippet": "Import:\n    IncludeList: SPY,TLT,GLD"
    },
    {
        "name": "EntrySetup",
        "category": "strategy_statement",
        "pattern": r"EntrySetup\s*:",
        "signature": "EntrySetup: condition",
        "description": "Boolean condition required for entries.",
        "snippet": "Strategy: Momentum\n    EntrySetup: C > MA(C, 200)"
    },
    {
        "name": "EntryScore",
        "category": "strategy_statement",
        "pattern": r"EntryScore\s*:",
        "signature": "EntryScore: numeric_expression",
        "description": "Ranking score applied after EntrySetup is true.",
        "snippet": "Strategy: Rotation\n    EntryScore: ROC(C, 63)"
    },
    {
        "name": "EntrySkip",
        "category": "strategy_statement",
        "pattern": r"EntrySkip\s*:",
        "signature": "EntrySkip: condition",
        "description": "Skips new entries while condition remains true.",
        "snippet": "Strategy: Guarded\n    EntrySkip: MarketDrawdown > 0.15"
    },
    {
        "name": "ExitRule",
        "category": "strategy_statement",
        "pattern": r"ExitRule\s*:",
        "signature": "ExitRule: condition",
        "description": "Exit trigger for positions.",
        "snippet": "Strategy: Momentum\n    ExitRule: C < MA(C, 100)"
    },
    {
        "name": "ExitStop",
        "category": "strategy_statement",
        "pattern": r"ExitStop\s*:",
        "signature": "ExitStop: price_expression",
        "description": "Protective stop price for open positions.",
        "snippet": "Strategy: Momentum\n    ExitStop: EntryPrice * 0.9"
    },
    {
        "name": "PositionSize",
        "category": "strategy_statement",
        "pattern": r"PositionSize\s*:",
        "signature": "PositionSize: expression",
        "description": "Custom sizing logic based on equity or risk.",
        "snippet": "Strategy: VolAdjust\n    PositionSize: (0.01 * S.Equity) / ATR(14)"
    },
    {
        "name": "Quantity",
        "category": "strategy_statement",
        "pattern": r"Quantity\s*:",
        "signature": "Quantity: expression",
        "description": "Defines shares or value for each trade, often used with QtyType.",
        "snippet": "Strategy: AllWeather\n    Quantity: Item(\"alloc{?}\", ?symbol)"
    },
    {
        "name": "QtyType",
        "category": "strategy_statement",
        "pattern": r"QtyType\s*:",
        "signature": "QtyType: Shares|Percent|Value|Risk",
        "description": "Specifies how quantity statements should be interpreted.",
        "snippet": "Strategy: AllWeather\n    QtyType: Percent"
    },
    {
        "name": "Side",
        "category": "strategy_statement",
        "pattern": r"Side\s*:",
        "signature": "Side: Long|Short",
        "description": "Locks a strategy to long-only or short-only trades.",
        "snippet": "Strategy: AllWeather\n    Side: Long"
    },
    {
        "name": "MaxEntries",
        "category": "strategy_statement",
        "pattern": r"MaxEntries\s*:",
        "signature": "MaxEntries: integer",
        "description": "Caps how many new positions can be opened simultaneously.",
        "snippet": "Strategy: Rotation\n    MaxEntries: 3"
    }
]

IGNORE_NAMES = {
    "The",
    "This",
    "That",
    "These",
    "Those",
    "With",
    "When",
    "From",
    "Most",
    "Some",
    "Each",
    "Any",
    "Only",
    "While",
    "Also",
    "Into",
    "Your",
    "Their",
    "Which",
    "Where",
    "Over",
    "Under",
    "Before",
    "After",
    "Because",
    "Since",
    "Until",
    "Returns",
    "Sets",
    "Specifies",
    "Defines",
    "Provides",
    "Average",
}


def clean_text(text: str) -> str:
    text = text.replace("\uFFFD", " ")
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_sources(pattern: str, manual_lines: List[str], sample_files: Iterable[pathlib.Path], manual_override: str | None = None) -> list[str]:
    regex = re.compile(pattern, re.IGNORECASE)
    sources: list[str] = []
    if manual_override:
        sources.append(manual_override)
    else:
        for idx, line in enumerate(manual_lines):
            if regex.search(line):
                sources.append(f"manual.txt:{idx + 1}")
                break
    for path in sample_files:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines):
            if regex.search(line):
                sources.append(f"samples/{path.name}:{idx + 1}")
                break
    if not sources:
        sources.append("manual.txt:N/A")
    return sources


def auto_extract_manual_functions(manual_text: str) -> dict[str, dict]:
    functions: dict[str, dict] = {}

    pattern_with_args = re.compile(
        r"([A-Za-z][A-Za-z0-9_.]+)\(([^)]*)\)\s*-\s*([^\uFFFD\n]+)"
    )
    pattern_simple = re.compile(r"([A-Za-z][A-Za-z0-9_.]+)\s*-\s*([^\uFFFD\n]+)")

    for match in pattern_with_args.finditer(manual_text):
        name = match.group(1).strip()
        if name in IGNORE_NAMES:
            continue
        desc = clean_text(match.group(3))
        if not desc:
            continue
        args = match.group(2).strip()
        signature = f"{name}({args})" if args else f"{name}()"
        line = manual_text.count("\n", 0, match.start()) + 1
        functions.setdefault(
            name,
            {
                "signature": signature,
                "description": desc,
                "line": line,
            },
        )

    for match in pattern_simple.finditer(manual_text):
        name = match.group(1).strip()
        if name in functions or name in IGNORE_NAMES:
            continue
        if len(name) <= 2 and name.isupper():
            continue
        desc = clean_text(match.group(2))
        if not desc:
            continue
        line = manual_text.count("\n", 0, match.start()) + 1
        functions.setdefault(
            name,
            {
                "signature": f"{name}()",
                "description": desc,
                "line": line,
            },
        )

    return functions


def main() -> None:
    parser = argparse.ArgumentParser(description="Build function/directive catalog")
    parser.add_argument("--manual", required=True, type=pathlib.Path, help="manual.txt path")
    parser.add_argument("--samples", required=True, type=pathlib.Path, help="Directory with sample .rts files")
    parser.add_argument("--output", required=True, type=pathlib.Path, help="Destination JSON path")
    args = parser.parse_args()

    manual_text = args.manual.read_text(encoding="utf-8")
    manual_lines = manual_text.splitlines()
    sample_files = sorted(args.samples.glob("*.rts"))

    entries: dict[str, dict] = {}

    for cfg in ENTRY_CONFIG:
        sources = find_sources(cfg["pattern"], manual_lines, sample_files)
        entries[cfg["name"]] = {
            "name": cfg["name"],
            "category": cfg["category"],
            "signature": cfg["signature"],
            "description": cfg["description"],
            "snippet": cfg["snippet"],
            "sources": sources,
        }

    auto_functions = auto_extract_manual_functions(manual_text)

    for name, info in auto_functions.items():
        if name in entries:
            continue
        pattern = rf"\b{re.escape(name)}\b"
        manual_override = f"manual.txt:{info['line']}"
        sources = find_sources(pattern, manual_lines, sample_files, manual_override=manual_override)
        snippet = f"Data:\n    Example_{name}: {name}(...)"
        entries[name] = {
            "name": name,
            "category": "function",
            "signature": info["signature"],
            "description": info["description"],
            "snippet": snippet,
            "sources": sources,
        }

    ordered = [entries[key] for key in sorted(entries)]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ordered, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} with {len(ordered)} catalog entries")


if __name__ == "__main__":
    main()
