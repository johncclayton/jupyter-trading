#!/usr/bin/env python3
"""Generate syntax catalog entries using manual text and sample RTS files."""

import argparse
import json
import pathlib
import re
from typing import Iterable, List

ENTRY_CONFIG = [
    {
        "name": "Notes Section",
        "type": "section",
        "pattern": r"^Notes\s*:",
        "description": "Optional free-form notes block at the top of a script.",
        "snippet": "Notes:\n    Strategy documentation goes here"
    },
    {
        "name": "Import Section",
        "type": "section",
        "pattern": r"^Import\s*:",
        "description": "Configures data import sources before testing.",
        "snippet": "Import:\n    DataSource: Yahoo\n    IncludeList: SPY,TLT"
    },
    {
        "name": "Settings Section",
        "type": "section",
        "pattern": r"^Settings\s*:",
        "description": "Global defaults for dates, bar size, and files.",
        "snippet": "Settings:\n    StartDate: 2010-01-01\n    EndDate: Latest\n    BarSize: Daily"
    },
    {
        "name": "Parameters Section",
        "type": "section",
        "pattern": r"^Parameters\s*:",
        "description": "Defines named parameter values for later reference.",
        "snippet": "Parameters:\n    allocSPY: 30\n    allocTLT: 40"
    },
    {
        "name": "Data Section",
        "type": "section",
        "pattern": r"^Data\s*:",
        "description": "Derived series and auxiliary calculations available to strategies.",
        "snippet": "Data:\n    SPY_MA200: MA(C, 200)\n    TrendOk: C > SPY_MA200"
    },
    {
        "name": "Strategy Section",
        "type": "section",
        "pattern": r"^Strategy\s*:",
        "description": "Trading rules, universe, and sizing for a given approach.",
        "snippet": "Strategy: TrendFollow\n    EntrySetup: C > MA(C, 200)\n    ExitRule: C < MA(C, 200)"
    },
    {
        "name": "Scan Section",
        "type": "section",
        "pattern": r"^Scan\s*:",
        "description": "Configures a screening workflow without portfolio simulation.",
        "snippet": "Scan:\n    Filter: Universe"
    },
    {
        "name": "ScanSettings Section",
        "type": "section",
        "pattern": r"^ScanSettings\s*:",
        "description": "Overrides defaults specifically for scan runs.",
        "snippet": "ScanSettings:\n    MaxPositions: 50"
    },
    {
        "name": "Template Section",
        "type": "section",
        "pattern": r"^Template\s*:",
        "description": "Defines a reusable block such as a TradeList or shared strategy setup.",
        "snippet": "Template: trades\n    TradeList: trades.csv"
    },
    {
        "name": "Benchmark Section",
        "type": "section",
        "pattern": r"^Benchmark\s*:",
        "description": "Sets benchmark series used for performance comparison.",
        "snippet": "Benchmark:\n    Symbol: SPY"
    },
    {
        "name": "Charts Section",
        "type": "section",
        "pattern": r"^Charts\s*:",
        "description": "Configures chart panes for visualization output.",
        "snippet": "Charts:\n    Price: C"
    },
    {
        "name": "Include Section",
        "type": "section",
        "pattern": r"^Include\s*:",
        "description": "Inserts another script at this location before parsing.",
        "snippet": "Include: ?scriptpath?\\common.rts"
    },
    {
        "name": "OrderSettings Section",
        "type": "section",
        "pattern": r"^OrderSettings\s*:",
        "description": "Adjusts order generation rules for the test run.",
        "snippet": "OrderSettings:\n    OrdersMode: Basket"
    },
    {
        "name": "StatsGroup Section",
        "type": "section",
        "pattern": r"^StatsGroup\s*:",
        "description": "Groups related performance statistics for reporting.",
        "snippet": "StatsGroup: Core\n    Include: CAGR,MaxDD"
    },
    {
        "name": "TestData Section",
        "type": "section",
        "pattern": r"^TestData\s*:",
        "description": "Provides synthetic or cached data feeds for testing.",
        "snippet": "TestData:\n    Source: cached_results.rtd"
    },
    {
        "name": "TestScan Section",
        "type": "section",
        "pattern": r"^TestScan\s*:",
        "description": "Declares scan inputs used when executing in Test mode.",
        "snippet": "TestScan:\n    Include: default_scan"
    },
    {
        "name": "TestSettings Section",
        "type": "section",
        "pattern": r"^TestSettings\s*:",
        "description": "Overrides global settings when running Test mode comparisons.",
        "snippet": "TestSettings:\n    StartDate: 2018-01-01"
    },
    {
        "name": "OptimizeSettings Section",
        "type": "section",
        "pattern": r"^OptimizeSettings\s*:",
        "description": "Configures optimization sweeps and objective ranking.",
        "snippet": "OptimizeSettings:\n    OptSortResults: Descending"
    },
    {
        "name": "WalkForward Section",
        "type": "section",
        "pattern": r"^WalkForward\s*:",
        "description": "Defines walk-forward evaluation windows and offsets.",
        "snippet": "WalkForward:\n    Length: 3 Months"
    },
    {
        "name": "StratData Section",
        "type": "section",
        "pattern": r"^StratData\s*:",
        "description": "Declares derived series scoped to a single strategy.",
        "snippet": "StratData:\n    TrendOk: C > MA(C, 200)"
    },
    {
        "name": "Combined Section",
        "type": "section",
        "pattern": r"^Combined\s*:",
        "description": "Aggregates results from multiple test runs or accounts.",
        "snippet": "Combined:\n    Include: Core,Edge"
    },
    {
        "name": "Library Section",
        "type": "section",
        "pattern": r"^Library\s*:",
        "description": "Reusable formulas shared across strategies.",
        "snippet": "Library:\n    FastROC(len) := ROC(C, len)\n    SlowMA(len) := MA(C, len)"
    },
    {
        "name": "DataSource Setting",
        "type": "statement",
        "pattern": r"DataSource\s*:",
        "description": "Identifies the import data source (e.g., Yahoo, Norgate).",
        "snippet": "Import:\n    DataSource: Yahoo"
    },
    {
        "name": "IncludeList Statement",
        "type": "directive",
        "pattern": r"IncludeList\s*:",
        "description": "Restricts processing to listed symbols or watchlists.",
        "snippet": "Import:\n    IncludeList: SPY,TLT,GLD"
    },
    {
        "name": "BarSize Setting",
        "type": "setting",
        "pattern": r"BarSize\s*:",
        "description": "Sets the bar aggregation for the current context.",
        "snippet": "Settings:\n    BarSize: Monthly"
    },
    {
        "name": "Universe Statement",
        "type": "statement",
        "pattern": r"Universe\s*:",
        "description": "Defines which symbols a strategy can trade.",
        "snippet": "Strategy: CoreRotation\n    Universe: IncludeList('core_etfs')"
    },
    {
        "name": "EntrySetup Rule",
        "type": "statement",
        "pattern": r"EntrySetup\s*:",
        "description": "Boolean condition required to consider a trade.",
        "snippet": "Strategy: Momentum\n    EntrySetup: C > MA(C, 200)"
    },
    {
        "name": "EntryScore Rule",
        "type": "statement",
        "pattern": r"EntryScore\s*:",
        "description": "Ranking metric applied to qualified symbols.",
        "snippet": "Strategy: Rotation\n    EntryScore: ROC(C, 63)"
    },
    {
        "name": "EntrySkip Statement",
        "type": "statement",
        "pattern": r"EntrySkip\s*:",
        "description": "Pauses new entries while condition is true.",
        "snippet": "Strategy: Guarded\n    EntrySkip: MarketDrawdown > 0.15"
    },
    {
        "name": "ExitRule Statement",
        "type": "statement",
        "pattern": r"ExitRule\s*:",
        "description": "Exit trigger for open positions.",
        "snippet": "Strategy: Momentum\n    ExitRule: C < MA(C, 100)"
    },
    {
        "name": "ExitStop Statement",
        "type": "statement",
        "pattern": r"ExitStop\s*:",
        "description": "Defines protective stop price.",
        "snippet": "Strategy: Momentum\n    ExitStop: EntryPrice * 0.9"
    },
    {
        "name": "Quantity Statement",
        "type": "statement",
        "pattern": r"Quantity\s*:",
        "description": "Specifies share or value sizing per trade.",
        "snippet": "Strategy: AllWeather\n    Quantity: Item(\"alloc{?}\", ?symbol)"
    },
    {
        "name": "QtyType Statement",
        "type": "statement",
        "pattern": r"QtyType\s*:",
        "description": "Determines interpretation of quantity (e.g., Percent, Shares).",
        "snippet": "Strategy: AllWeather\n    QtyType: Percent"
    },
    {
        "name": "Side Statement",
        "type": "statement",
        "pattern": r"Side\s*:",
        "description": "Declares long or short bias for a strategy.",
        "snippet": "Strategy: AllWeather\n    Side: Long"
    }
]


def find_first(pattern: str, lines: List[str]) -> str | None:
    regex = re.compile(pattern, re.IGNORECASE)
    for idx, line in enumerate(lines):
        if regex.search(line):
            return f"manual.txt:{idx + 1}"
    return None


def find_in_samples(pattern: str, files: Iterable[pathlib.Path]) -> list[str]:
    regex = re.compile(pattern, re.IGNORECASE)
    hits: list[str] = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines):
            if regex.search(line):
                hits.append(f"samples/{path.name}:{idx + 1}")
                break
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Build syntax catalog from manual and samples")
    parser.add_argument("--manual", required=True, type=pathlib.Path, help="Path to manual.txt")
    parser.add_argument("--samples", required=True, type=pathlib.Path, help="Directory containing .rts files")
    parser.add_argument("--output", required=True, type=pathlib.Path, help="Destination JSON path")
    args = parser.parse_args()

    manual_lines = args.manual.read_text(encoding="utf-8").splitlines()
    sample_files = sorted(args.samples.glob("*.rts"))

    catalog = []
    for entry in ENTRY_CONFIG:
        manual_hit = find_first(entry["pattern"], manual_lines)
        sample_hits = find_in_samples(entry["pattern"], sample_files)
        sources = []
        if manual_hit:
            sources.append(manual_hit)
        sources.extend(sample_hits)
        if not sources:
            sources.append("manual.txt:N/A")
        catalog.append(
            {
                "name": entry["name"],
                "type": entry["type"],
                "pattern": entry["pattern"],
                "description": entry["description"],
                "snippet": entry["snippet"],
                "sources": sources,
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} with {len(catalog)} entries using {len(sample_files)} samples")


if __name__ == "__main__":
    main()
