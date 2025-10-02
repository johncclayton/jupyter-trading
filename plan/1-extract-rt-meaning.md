# Plan 1: Extract and Understand RealTest Language

1. **Prepare Versioned Artifacts**  
   - Input: Repository root containing at least one `RealTest*.pdf`, populated `samples/` with `.rts` examples.  
   - Actions: Identify newest matching PDF by timestamp; derive version name `YYYYMMDD-realtest-guide`; create `versions/<version>/`; move PDF to `versions/<version>/manual.pdf`; ensure `samples/` exists.  
   - Output: `versions/<version>/manual.pdf`, ready-to-use `samples/` directory.

2. **Run Standardized Text Extraction**  
   - Input: `versions/<version>/manual.pdf`.  
   - Actions: Execute `python tools/extract_pdf_text.py versions/<version>/manual.pdf --output versions/<version>/manual.txt`; verify byte count > 0.  
   - Output: `versions/<version>/manual.txt` (UTF-8 plain text).

3. **Build Manual Structure and Glossary**  
   - Input: `versions/<version>/manual.txt`.  
   - Actions: `python tools/build_manual_structure.py --manual versions/<version>/manual.txt --output versions/<version>/manual_structure.json`; captures every heading and curated glossary terms.  
   - Output: `versions/<version>/manual_structure.json` (sections list + glossary array).

4. **Generate Syntax Catalog with Samples**  
   - Input: `versions/<version>/manual.txt`, `samples/*.rts`.  
   - Actions: `python tools/build_syntax_catalog.py --manual versions/<version>/manual.txt --samples samples --output versions/<version>/syntax_catalog.json`; records structural constructs with manual and sample references.  
   - Output: `versions/<version>/syntax_catalog.json`.

5. **Produce Grammar Spec and Lark Grammar**  
   - Input: `versions/<version>/syntax_catalog.json`.  
   - Actions: `python tools/build_grammar.py --version-dir versions/<version>/`; emits machine-readable JSON grammar plus `realtest_grammar.lark` (PEG/ANTLR-style).  
   - Outputs: `versions/<version>/realtest_grammar.json`, `versions/<version>/realtest_grammar.lark`.

6. **Compile Function, Directive, and Statement Catalog**  
   - Input: `versions/<version>/manual.txt`, `samples/*.rts`.  
   - Actions: `python tools/build_function_catalog.py --manual versions/<version>/manual.txt --samples samples --output versions/<version>/function_catalog.json`; aggregates signatures, descriptions, snippets, and cross-references.  
   - Output: `versions/<version>/function_catalog.json`.

7. **Map Semantic Strategy Patterns**  
   - Input: `versions/<version>/manual_structure.json`, `versions/<version>/function_catalog.json`, `samples/*.rts`.  
   - Actions: `python tools/build_semantic_patterns.py --version-dir versions/<version>/ --samples samples --output versions/<version>/semantic_patterns.json`; links natural-language motifs to canonical snippets.  
   - Output: `versions/<version>/semantic_patterns.json`.

8. **Validate Grammar Against Samples**  
   - Input: `versions/<version>/realtest_grammar.lark`, `samples/*.rts`.  
   - Actions: `python tools/validate_grammar.py --grammar versions/<version>/realtest_grammar.lark --samples samples --output versions/<version>/grammar_validation.json`; parses every sample file (no truncation) and records pass/fail diagnostics.  
   - Output: `versions/<version>/grammar_validation.json` + console summary.

9. **Create LLM Evaluation Suite**  
   - Input: `versions/<version>/semantic_patterns.json`, `versions/<version>/function_catalog.json`, `versions/<version>/realtest_grammar.json`.  
   - Actions: `python tools/build_evaluation_suite.py --version-dir versions/<version>/ --output versions/<version>/evaluation_suite.json`; prepares prompt_to_RTS regression cases with references.  
   - Output: `versions/<version>/evaluation_suite.json`.

10. **Assemble Knowledge Base Summary**  
   - Input: All prior outputs (`manual_structure.json`, `syntax_catalog.json`, `realtest_grammar.json`, `realtest_grammar.lark`, `realtest_grammar.g4`, `function_catalog.json`, `semantic_patterns.json`, `grammar_validation.json`, `evaluation_suite.json`).  
   - Actions: `python tools/build_knowledge_base.py --version-dir versions/<version>/ --output versions/<version>/knowledge_base.md`; compiles methodology, counts, references, and validation status.  
   - Output: `versions/<version>/knowledge_base.md` ready for review.

11. **CI Verification Hook**  
   - Input: `versions/<version>/` artifacts, `samples/`.  
   - Actions: `python tools/run_ci_checks.py --version-dir versions/<version>/ --samples samples`; runs grammar validation and confirms evaluation suite cases parse under the grammar.  
   - Output: CI-friendly pass/fail signal plus console summary of grammar/evaluation checks.
