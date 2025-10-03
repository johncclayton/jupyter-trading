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
3. Create `versions/<version>/` if missing and move the selected PDF to `versions/<version>/manual.pdf` (warn if a manual already exists to avoid silent overwrites).
   - Reason: Centralizes artifacts per version and preserves provenance.
4. Verify `samples/` exists and contains at least one `.rts`; record any anomalies in a log message instead of altering the directory.
   - Reason: Downstream steps depend on sample scripts and the user forbids changes there.

## Step 2: Run Standardized Text Extraction
1. Implement `tools/2-standard-text-extraction.py` with a CLI (`--version-dir` argument) that loads `versions/<version>/manual.pdf`.
   - Reason: Enables reuse for future manuals without code edits.
2. Inside the script, activate `realtestextract` venv when executed manually; document this requirement in module docstring.
   - Reason: Keeps dependencies isolated per prerequisite instructions.
3. Use `pdfminer.high_level.extract_text` (already shipped with pdfminer.six) to convert the PDF to UTF-8 text; normalize line endings and strip trailing whitespace without altering content order.
   - Reason: Produces a faithful text copy while avoiding third-party binaries.
4. Write output to `versions/<version>/manual.txt`, overwriting only after successful extraction; on failure, exit non-zero and leave existing files untouched.
   - Reason: Protects prior results and makes reruns idempotent.
5. Add a smoke test mode that reports the number of extracted characters and first few headings.
   - Reason: Quick validation confirms that extraction produced non-empty, structured text.

## Step 3: Build Manual Structure and Glossary
1. Create `tools/3-build-manual-structure.py` that accepts `--version-dir` and reads `manual.txt`.
   - Reason: Keeps tooling modular and reusable per version.
2. Parse headings by detecting numbering patterns (e.g., `^\d+(\.\d+)*\s+`) and case-shifted all-caps sections; capture hierarchy depth for nesting.
   - Reason: Manual sections likely use numeric outlines; structured parsing enables accurate navigation.
3. Identify glossary candidates by scanning for lines matching `Term - definition` or glossary sections; allow configurable patterns to adjust as manual quirks surface.
   - Reason: Glossary content may use varied formatting, so pattern flexibility avoids repeated code edits.
4. Emit `versions/<version>/manual_structure.json` with two top-level arrays: `sections` (ordered list with title, depth, page reference if available) and `glossary` (term, definition, source line).
   - Reason: Standardizes downstream consumption for grammar work.
5. Include validation hooks that count sections and glossary entries, logging anomalies (e.g., zero matches) before writing output.
   - Reason: Early detection prevents propagating empty or malformed artifacts.

## Step 4: Compile Function, Directive, and Statement Catalog
1. Build `tools/4-build-function-catalog.py` taking `--version-dir` plus optional `--samples-dir` (default `samples`).
   - Reason: Supports future sample sets without code tweaks.
2. Extract candidate language elements from `manual.txt` by keyword heuristics (`Function`, `Directive`, `Statement`) and known formatting (tables, bullet lists). Store raw snippets for manual review.
   - Reason: The manual likely documents syntax in context; capturing context aids classification.
3. Cross-reference `.rts` files using a lightweight parser or regex pass to confirm actual usage and gather examples per token.
   - Reason: Validates manual claims and surfaces constructs not explicitly documented.
4. Normalize entries into `versions/<version>/function_catalog.json` with fields: `name`, `category`, `description`, `manual_refs`, `sample_examples` (code excerpt + filename:line), and `notes` for ambiguities.
   - Reason: Creates a single source of truth required for grammar design.
5. Emit summary statistics (counts per category, unmatched tokens) so gaps are visible and can be addressed before grammar authoring.
   - Reason: Highlights remaining research work and prevents blind spots in the grammar effort.

## Verification and Handoff
- After each script runs, commit intermediate JSON/TXT artifacts to version control once reviewed; note any manual adjustments separately.
- Document command invocations in a short README section inside `versions/<version>/` for reproducibility.
- Confirm that no step touches files outside allowed directories (especially `samples/`).
