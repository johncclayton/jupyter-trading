# RealTest Language Knowledge Base (Version 20251002-realtest-guide)

## Overview
- PDF source: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\manual.pdf`
- Text extraction: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\manual.txt`
- Manual structure & glossary: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\manual_structure.json` (741 sections)
- Syntax catalog: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\syntax_catalog.json` (19 items)
- Grammar spec: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\realtest_grammar.json` + `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\realtest_grammar.lark` + `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\realtest_grammar.g4`
- Function catalog: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\function_catalog.json` (306 entries)
- Semantic patterns: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\semantic_patterns.json` (5 patterns)
- Grammar validation: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\grammar_validation.json`
- Evaluation suite: `C:\Users\johnc\src\jupyter-trading\versions\20251002-realtest-guide\evaluation_suite.json`

## Methodology
1. Versioned the source manual and extracted deterministic text for processing.
2. Parsed the manual headings into a full section index and glossary for grounding terminology.
3. Catalogued structural constructs using both manual references and curated `samples/` scripts.
4. Generated machine-readable grammar (JSON + Lark PEG) and validated it against all sample scripts.
5. Compiled function/directive/statement metadata with cross-references to manual lines and sample usage.
6. Captured semantic patterns linking natural-language descriptions to canonical RealTest snippets.
7. Built an evaluation set of prompt_to_RTS cases for LLM regression testing.

## Grammar Validation
- Parsed 112/112 sample scripts successfully.
- All sample scripts parsed without errors.

## Key Catalog Highlights
- Syntax catalog entries cover sections (Import/Settings/Strategy/Library), directives (IncludeList, DataSource) and statements (EntrySetup, Quantity, Side, etc.).
- Function catalog spans core indicators (`MA`, `ROC`, `ATR`), crossovers, universe directives, and sizing controls (Quantity, PositionSize, QtyType).

## Semantic Patterns
- **Momentum Filter** — Only trade when the asset trades above a long-term moving average or similar momentum condition.
- **Rank And Allocate** — Rank candidates by momentum (EntryScore) and allocate up to a defined number of positions.
- **Drawdown Guard** — Suspend entries while a drawdown metric exceeds a threshold.
- **Volatility Position Sizing** — Scale position size inversely to volatility (ATR) to target consistent risk.
- **Static Allocation** — Use Parameters and Item() to distribute capital across fixed-weight sleeves (All Weather style).

## Evaluation Suite
- See `evaluation_suite.json` for prompt_to_RTS regression cases covering momentum filters, drawdown guards, and rotational momentum strategies.

## Next Steps
- Expand the function catalog by parsing the manual's appendix tables programmatically.
- Add more domain-diverse `.rts` samples (e.g., futures, intraday) to stress-test the grammar.
- Integrate the grammar validator and evaluation suite into CI to monitor LLM output quality.
- Consider emitting additional formats (ANTLR `.g4`) from the Lark grammar for broader tooling support.
