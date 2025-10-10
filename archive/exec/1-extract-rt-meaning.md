# Detailed Plan for Plan 1: Extract and Understand RealTest Language

## Scope and Constraints
- Focus exclusively on the RealTest script language; ignore UI-only content unless it clarifies language semantics.
- Keep all generated paths relative to the repository root; enforce this in scripts and documentation.
- Place every new script under `tools/`; use the `realtestextract` virtual environment for Python work.
- Never modify files in `samples/`; treat them as read-only inputs.

## Step 1: Prepare Versioned Artifacts
1. Scan repository root for `RealTest*.pdf` files using `Path.glob` inside a helper script.
   - Reason: Ensure the workflow discovers manuals without hardcoding filenames.
2. Choose the newest manual by filesystem modified time and derive the version tag `YYYYMMDD-realtest-guide` from that timestamp.
   - Reason: Guarantees deterministic version directories that match the source document.
3. Create `versions/<version>/` if missing and move the selected PDF to `versions/<version>/manual.pdf` while copying it back to the repository root (warn if a manual already exists to avoid silent overwrites).
   - Reason: Centralizes artifacts per version, preserves provenance, and retains the reference copy for future diffs.
4. Verify `samples/` exists and contains at least one `.rts`; record any anomalies in a log message instead of altering the directory.
   - Reason: Downstream steps depend on sample scripts and the user forbids changes there.

## Step 2: Run Standardized Text Extraction
1. Implement a consolidated CLI in `tools/` (e.g., `tools/rt_manual.py`) with subcommands for extraction, structure building, and catalog generation, each taking `--version-dir`.
   - Reason: Ensures the manual is loaded and normalized once per invocation and keeps functionality discoverable in one entry point.
2. Inside the CLI, isolate shared helpers (manual discovery, text normalization, relative path validation) so downstream subcommands reuse the same logic.
   - Reason: Eliminates duplicated preprocessing and enforces the relative-path rule everywhere.
3. For the `extract-text` subcommand, use `pdfminer.high_level.extract_text` within the `realtestextract` venv to write UTF-8 output, normalizing newlines and trimming trailing whitespace without reflow.
   - Reason: Produces a faithful text copy while avoiding third-party binaries.
4. Write output to `versions/<version>/manual.txt`, overwriting only after successful extraction; on failure, exit non-zero and leave existing files untouched.
   - Reason: Protects prior results and makes reruns idempotent.
5. Add a smoke test mode that reports the number of extracted characters and first few headings.
   - Reason: Quick validation confirms that extraction produced non-empty, structured text.

## Step 3: Build Manual Structure and Glossary
1. Implement a `build-structure` subcommand within the shared CLI that reads the normalized text once and yields both headings and glossary entries.
   - Reason: Reuses the extraction foundation and keeps the workflow consistent.
2. Parse headings by detecting numbering patterns (e.g., `^\d+(\.\d+)*\s+`) and case-shifted all-caps sections; capture hierarchy depth for nesting.
   - Reason: Manual sections likely use numeric outlines; structured parsing enables accurate navigation.
3. Identify glossary candidates by scanning for lines matching `Term - definition` or glossary sections; allow configurable patterns to adjust as manual quirks surface.
   - Reason: Glossary content may use varied formatting, so pattern flexibility avoids repeated code edits.
4. Emit `versions/<version>/manual_structure.json` with two top-level arrays: `sections` (ordered list with title, depth, page reference if available) and `glossary` (term, definition, source line).
   - Reason: Standardizes downstream consumption for grammar work.
5. Include validation hooks that count sections and glossary entries, logging anomalies (e.g., zero matches) before writing output.
   - Reason: Early detection prevents propagating empty or malformed artifacts.

## Step 4: Compile Function, Directive, and Statement Catalog
1. Implement a `build-function-catalog` subcommand within the shared CLI, accepting `--samples-dir` (default `samples`) and reusing the parsed `manual_structure.json` to anchor sections.
   - Reason: Keeps every artifact behind the same entry point and enforces shared validation helpers.
2. Extract candidate language elements from the manual first, organised by section heuristics (e.g., the 17.17/17.18 hierarchy), capturing Category/Description/Example/Notes slices for review.
   - Reason: Builds a baseline catalog directly from the authoritative documentation.
3. Enrich each entry by scanning `.rts` samples for corroborating usage snippets, referencing files without modifying them, and merge deduplicated aliases.
   - Reason: Validates manual claims and surfaces constructs not explicitly documented.
4. Compare catalog names against the `bnf/lark/realtest.lark` grammar symbols and record whether each entry matches at least one grammar token.
   - Reason: Aligns the extracted catalog with the existing grammar and highlights drift.
5. Pull in supporting context such as watchlist references (from `watchlists.json`) and ancestor categories, normalizing entries into `versions/<version>/function_catalog.json` with run summary statistics written to `runlog.json`.
   - Reason: Produces a catalog ready for prompt assembly with provenance baked in.

## Step 5: Assemble LLM Prompt Assets
1. Script a prompt asset builder that consumes `manual_structure.json`, `manual.txt`, `function_catalog.json`, `watchlists.json`, and the grammar file to generate a concise cheat sheet of key functions (name, category, one-line description, sample snippet reference).
   - Reason: Provides a compact appendix for strategy synthesis while staying reproducible.
2. Generate a representative prompt template (Markdown or plain text) showing the recommended layout: system guidance, user slot, retrieved context sections (manual excerpt, grammar rules, catalog slice), and watchlist summary.
   - Reason: Demonstrates how to stitch the artifacts into an effective in-context message.
3. Add a Python utility (e.g., `tools/prompt_token_check.py`) that reports token counts for any assembled prompt, relying on a local tokenizer (tiktoken or fallback) and writing the result to stdout.
   - Reason: Ensures prompts stay within model context limits without manual estimation.
4. Store the cheat sheet, sample prompt, and validation report under `versions/<version>/prompt_assets/` (or similar) alongside a README explaining usage; skip vector/cosine index creation for now but note future expansion.
   - Reason: Keeps downstream consumers aligned on artifact locations and future plans.

## Verification and Handoff
- After each subcommand runs, review outputs and commit artifacts alongside their provenance (`metadata.json` or `runlog.json` entries); capture any manual adjustments separately.
- Confirm the CLI leaves the repository root copy of the manual untouched and does not alter forbidden paths such as `samples/`.
