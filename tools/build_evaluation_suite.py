#!/usr/bin/env python3
"""Create LLM evaluation suite prompts for RealTest."""

import argparse
import json
import pathlib

EVAL_CASES = [
    {
        "prompt": "Create a RealTest strategy that buys when close is above the 200-day average and sells when it falls below.",
        "expected": "Settings:\n    StartDate: 2010-01-01\n\nStrategy: MomentumFilter\n    EntrySetup: C > MA(C, 200)\n    ExitRule: C < MA(C, 200)",
        "references": [
            "semantic_patterns.json:Momentum Filter",
            "function_catalog.json:MA",
            "syntax_catalog.json:EntrySetup Rule"
        ],
        "notes": "Baseline momentum filter translation."
    },
    {
        "prompt": "Build a drawdown guard that skips entries if the market has dropped more than 15 percent from its 1-year high.",
        "expected": "Data:\n    MarketDrawdown: (Highest(C, 252) - C) / Highest(C, 252)\n\nStrategy: GuardedEntries\n    EntrySetup: C > MA(C, 100)\n    EntrySkip: MarketDrawdown > 0.15",
        "references": [
            "semantic_patterns.json:Drawdown Guard",
            "function_catalog.json:Highest",
            "function_catalog.json:EntrySkip"
        ],
        "notes": "Ensures derived data works with EntrySkip."
    },
    {
        "prompt": "Write a rotational ETF strategy that ranks candidates by 3-month momentum and holds the top three symbols.",
        "expected": "Settings:\n    MaxEntries: 3\n\nStrategy: Rotation\n    Universe: IncludeList('core_etfs')\n    EntrySetup: C > MA(C, 150)\n    EntryScore: ROC(C, 63)",
        "references": [
            "semantic_patterns.json:Rank And Allocate",
            "function_catalog.json:EntryScore",
            "function_catalog.json:ROC"
        ],
        "notes": "Tests rank-based allocation flow."
    }
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build evaluation suite JSON")
    parser.add_argument("--version-dir", required=True, type=pathlib.Path, help="Version directory")
    parser.add_argument("--output", required=True, type=pathlib.Path, help="Output JSON path")
    args = parser.parse_args()

    payload = {
        "runner": "Apply prompts sequentially to the target LLM and compare generated RTS output against expected semantics (structure + key statements).",
        "cases": EVAL_CASES,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} with {len(EVAL_CASES)} cases")


if __name__ == "__main__":
    main()
