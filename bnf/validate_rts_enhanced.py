#!/usr/bin/env python3
"""
Enhanced RealTest Script Validator

This script validates all .rts files in the samples/ directory using the realtest.lark grammar.
It includes enhanced validation to ensure sections are being parsed correctly by comparing
section headers found via regex with those identified by the parser tree.

The enhanced validation helps catch:
1. Parser rules that incorrectly consume entire sections (like Notes consuming everything)
2. Missing or malformed section parsing rules
3. Incorrect section boundaries
"""

import sys
import re
from pathlib import Path
from lark import Lark, LarkError, Tree
from lark.exceptions import ParseError, LexError, UnexpectedInput
import argparse
from typing import List, Tuple, Set, Dict, Optional

# Top-level RealTest sections sourced from realtest.lark *_HEADER tokens
TOP_LEVEL_SECTION_NAMES: Tuple[str, ...] = (
    "Benchmark",
    "Charts",
    "Combined",
    "Data",
    "Graphs",
    "Import",
    "Include",
    "Library",
    "Namespace",
    "Notes",
    "OrderInclude",
    "OrderSettings",
    "Parameters",
    "Results",
    "Scan",
    "ScanInclude",
    "ScanSettings",
    "Settings",
    "Strategy",
    "Template",
    "TestData",
    "TestSettings",
    "Trades",
    "WalkForward",
)

SECTION_RULE_TO_NAME: Dict[str, str] = {
    "benchmark_section": "Benchmark",
    "charts_section": "Charts",
    "combined_section": "Combined",
    "data_section": "Data",
    "graphs_section": "Graphs",
    "import_section": "Import",
    "include_section": "Include",
    "library_section": "Library",
    "namespace_section": "Namespace",
    "notes_section": "Notes",
    "order_include_section": "OrderInclude",
    "order_settings_section": "OrderSettings",
    "parameters_section": "Parameters",
    "results_section": "Results",
    "scan_section": "Scan",
    "scan_include_section": "ScanInclude",
    "scan_settings_section": "ScanSettings",
    "settings_section": "Settings",
    "strategy_section": "Strategy",
    "template_section": "Template",
    "testdata_section": "TestData",
    "testsettings_section": "TestSettings",
    "trades_section": "Trades",
    "walkforward_section": "WalkForward",
}

SECTION_HEADER_PATTERN = re.compile(
    r"^\s*(" + "|".join(re.escape(name) for name in TOP_LEVEL_SECTION_NAMES) + r")\s*:"
)


def load_grammar(grammar_path_str="lark/realtest.lark"):
    """Load the Lark grammar from the specified path"""
    grammar_path = Path(grammar_path_str)
    if not grammar_path.exists():
        print(f"Error: Grammar file not found at {grammar_path}")
        sys.exit(1)
    
    try:
        with open(grammar_path, 'r', encoding='utf-8') as f:
            grammar_content = f.read()
        
        parser = Lark(grammar_content, 
                      debug=True,
                      start='start',
                      parser='earley')
        print(f"✓ Grammar loaded successfully from {grammar_path}")
        return parser
    except Exception as e:
        print(f"Error loading grammar: {e}")
        sys.exit(1)


def find_rts_files(samples_dir: Path):
    """Find all .rts files in the provided samples directory"""
    if not samples_dir.exists():
        print(f"Error: Samples directory not found at {samples_dir}")
        sys.exit(1)
    
    rts_files = list(samples_dir.glob("*.rts"))
    if not rts_files:
        print(f"No .rts files found in {samples_dir}")
        sys.exit(1)
    
    print(f"Found {len(rts_files)} .rts files in {samples_dir}")
    return sorted(rts_files)


def extract_sections_from_text(content: str) -> List[Tuple[str, int]]:
    """Extract top-level section headers from raw text via direct matching."""
    sections: List[Tuple[str, int]] = []
    for line_num, line in enumerate(content.splitlines(), 1):
        match = SECTION_HEADER_PATTERN.match(line)
        if match:
            sections.append((match.group(1), line_num))
    return sections


def extract_sections_from_tree(tree: Tree) -> List[str]:
    """Extract ordered top-level section names from the parse tree."""
    sections: List[str] = []

    if not isinstance(tree, Tree):
        return sections

    for node in tree.children:
        if not isinstance(node, Tree):
            continue
        if node.data != "section":
            # Defensive fallback: handle grammars that skip the wrapper
            mapped = SECTION_RULE_TO_NAME.get(node.data)
            if mapped:
                sections.append(mapped)
            continue

        for child in node.children:
            if not isinstance(child, Tree):
                continue
            mapped = SECTION_RULE_TO_NAME.get(child.data)
            if mapped:
                sections.append(mapped)
                break

    return sections


def validate_section_parsing(
    manual_sections: List[Tuple[str, int]],
    tree_sections: List[str],
) -> Tuple[bool, List[str]]:
    """Validate that parser-derived sections match the manually extracted list."""
    issues: List[str] = []

    manual_names = [name for name, _ in manual_sections]

    if manual_names != tree_sections:
        issues.append(
            "Top-level sections mismatch. "
            f"Manual={manual_names} Parsed={tree_sections}"
        )

    manual_set = set(manual_names)
    tree_set = set(tree_sections)

    missing = sorted(manual_set - tree_set)
    extra = sorted(tree_set - manual_set)

    if missing:
        issues.append(f"Missing in parse tree: {missing}")
    if extra:
        issues.append(f"Unexpected in parse tree: {extra}")

    return len(issues) == 0, issues


def check_notes_section_consumption(content: str, tree: Tree) -> Tuple[bool, List[str]]:
    """
    Special check for Notes section to ensure it doesn't consume everything after it.
    Returns (is_valid, list_of_issues).
    """
    issues = []
    
    # Find Notes section in text
    lines = content.splitlines()
    notes_line = None
    for i, line in enumerate(lines):
        if re.match(r'^Notes\s*:', line.strip()):
            notes_line = i
            break
    
    if notes_line is None:
        return True, []  # No Notes section, nothing to check
    
    # Find all sections after Notes
    sections_after_notes = []
    for i in range(notes_line + 1, len(lines)):
        line = lines[i]
        match = SECTION_HEADER_PATTERN.match(line)
        if match:
            sections_after_notes.append((match.group(1), i + 1))
    
    if not sections_after_notes:
        return True, []  # No sections after Notes, which is fine
    
    # Check if these sections are properly parsed
    tree_sections = extract_sections_from_tree(tree)
    missing_sections = []
    
    for section_name, line_num in sections_after_notes:
        if section_name not in tree_sections:
            missing_sections.append(f"{section_name} (line {line_num})")
    
    if missing_sections:
        issues.append(f"Notes section may be consuming sections that follow it: {missing_sections}")
    
    return len(issues) == 0, issues


def dump_sections_and_tree(
    file_path: Path,
    manual_sections: List[Tuple[str, int]],
    tree_sections: List[str],
    tree: Tree,
):
    """Print manual vs parsed section lists and the parse tree for a file."""
    print(f"\n🔍 Section extraction for {file_path.name}")
    print("-" * 60)
    print("Manual sections (order preserved):")
    for name, line in manual_sections:
        print(f"  - {name} (line {line})")
    if not manual_sections:
        print("  (none)")

    print("\nParsed sections (order preserved):")
    if tree_sections:
        for name in tree_sections:
            print(f"  - {name}")
    else:
        print("  (none)")

    print("\nParse tree:")
    print("=" * 60)
    print(tree.pretty())
    print("=" * 60)


def validate_file(parser, file_path):
    """Validate a single .rts file using the parser with enhanced section checking"""
    content = None
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Try to parse the content
        tree = parser.parse(content)

        manual_sections = extract_sections_from_text(content)
        tree_sections = extract_sections_from_tree(tree)

        dump_sections_and_tree(file_path, manual_sections, tree_sections, tree)

        # Enhanced validation: check section parsing
        sections_valid, section_issues = validate_section_parsing(manual_sections, tree_sections)
        notes_valid, notes_issues = check_notes_section_consumption(content, tree)

        all_issues = section_issues + notes_issues
        enhanced_valid = sections_valid and notes_valid

        return True, None, content, tree, enhanced_valid, all_issues

    except FileNotFoundError:
        return False, f"File not found: {file_path}", content, None, False, []
    except (ParseError, LexError, UnexpectedInput) as e:
        return False, e, content, None, False, []
    except Exception as e:
        return False, e, content, None, False, []


def print_error_context(file_path, error, content):
    """Prints detailed error information and code context."""
    print(f"\nFile: {file_path}")
    
    if hasattr(error, 'line') and hasattr(error, 'column') and content:
        print(f"Error: {error}")
        lines = content.splitlines()
        err_line_index = error.line - 1
        
        start = max(0, err_line_index - 5)
        end = min(len(lines), err_line_index + 6)
        
        print("\n" + "-"*4 + " Code Context " + "-"*4)
        for i in range(start, end):
            line_num = i + 1
            prefix = f"{line_num:4d} > " if i == err_line_index else f"{line_num:4d} | "
            print(f"{prefix}{lines[i]}")
            if i == err_line_index:
                # Add a pointer to the column
                print(" " * (len(prefix) + error.column - 1) + "^")
        print("-" * 20)

    else:
        # Fallback for errors without line/column info
        print(f"Error: {error}")


def print_section_analysis(file_path: Path, content: str, tree: Tree):
    """Print detailed section analysis for debugging"""
    print(f"\n🔍 Section Analysis for {file_path.name}")
    print("=" * 60)
    
    # Get sections from text
    text_sections = extract_sections_from_text(content)
    print(f"Sections found in text ({len(text_sections)}):")
    for section_name, line_num in text_sections:
        print(f"  - {section_name} (line {line_num})")
    
    # Get sections from tree
    tree_sections = extract_sections_from_tree(tree)
    print(f"\nSections found in parse tree ({len(tree_sections)}):")
    for section_name in sorted(set(tree_sections)):
        count = tree_sections.count(section_name)
        count_str = f" (×{count})" if count > 1 else ""
        print(f"  - {section_name}{count_str}")
    
    print("=" * 60)


def find_last_successful_parse(parser, content):
    """Binary search to find the last successfully parsed content"""
    lines = content.splitlines(keepends=True)
    
    # Find the largest prefix that parses successfully
    left, right = 0, len(lines)
    last_good = 0
    last_tree = None
    
    while left <= right:
        mid = (left + right) // 2
        test_content = ''.join(lines[:mid])
        
        try:
            tree = parser.parse(test_content)
            last_good = mid
            last_tree = tree
            left = mid + 1
        except:
            right = mid - 1
    
    return last_good, ''.join(lines[:last_good]), last_tree


def count_section_in_text(content: str, section_name: str) -> int:
    """Count occurrences of a section in the text using regex."""
    pattern = rf'^{re.escape(section_name)}\s*:'
    return len(re.findall(pattern, content, re.MULTILINE))


def count_section_in_tree(tree: Tree, section_name: str) -> int:
    """Count occurrences of a section in the parse tree."""
    count = 0
    
    def walk_tree(node):
        nonlocal count
        if isinstance(node, Tree):
            # Check for specific section types
            if section_name == 'Notes' and node.data == 'notes_section':
                count += 1
            elif section_name == 'Parameters' and node.data == 'parameters_section':
                count += 1
            elif section_name == 'Charts' and node.data == 'charts_section':
                count += 1
            elif section_name == 'Benchmark' and node.data == 'benchmark_section':
                count += 1
            elif section_name == 'Strategy' and node.data == 'strategy_section':
                count += 1
            elif node.data == 'generic_section':
                # For generic sections, check the section name
                for child in node.children:
                    if hasattr(child, 'type') and child.type == 'SECTION_NAME' and str(child) == section_name:
                        count += 1
                        break
            
            # Recursively walk children
            for child in node.children:
                walk_tree(child)
    
    walk_tree(tree)
    return count


def main():
    """Main validation loop"""
    arg_parser = argparse.ArgumentParser(description="Enhanced RealTest Script Validator")
    arg_parser.add_argument(
        "--early",
        action="store_true",
        help="Stop validation at the first file that fails to parse.",
    )
    arg_parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a single .rts file to validate.",
    )
    arg_parser.add_argument(
        "--grammar",
        type=str,
        default="lark/realtest.lark",
        help="Path to the grammar file to use (e.g., lark/realtest2.lark).",
    )
    arg_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed section analysis for all files.",
    )
    arg_parser.add_argument(
        "--section-check-only",
        action="store_true",
        help="Only perform section validation on files that parse successfully.",
    )
    arg_parser.add_argument(
        "--section-count",
        type=str,
        default=None,
        help="Count occurrences of a specific section name in text vs parse tree for all files.",
    )
    arg_parser.add_argument(
        "--samples-dir",
        type=str,
        default="samples",
        help="Directory containing .rts samples to validate (default: bnf/samples).",
    )
    args = arg_parser.parse_args()

    samples_dir = Path(args.samples_dir)

    # Handle section count mode
    if args.section_count:
        print(f"Section Count Analysis: {args.section_count}")
        print("=" * 50)
        
        # Load the grammar
        parser = load_grammar(args.grammar)
        
        # Find .rts file(s)
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File not found at {file_path}")
                sys.exit(1)
            rts_files = [file_path]
        else:
            rts_files = find_rts_files(samples_dir)
        
        print(f"Analyzing {len(rts_files)} files for '{args.section_count}' sections...")
        print("-" * 70)
        print(f"{'File':<30} {'Text':<5} {'Tree':<5} {'Status'}")
        print("-" * 70)
        
        total_text = 0
        total_tree = 0
        parse_failures = 0
        
        for file_path in rts_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                text_count = count_section_in_text(content, args.section_count)
                
                try:
                    tree = parser.parse(content)
                    tree_count = count_section_in_tree(tree, args.section_count)
                    status = "OK"
                except Exception as e:
                    tree_count = 0
                    status = "PARSE_FAIL"
                    parse_failures += 1
                
                print(f"{file_path.name:<30} {text_count:<5} {tree_count:<5} {status}")
                
                total_text += text_count
                total_tree += tree_count
                
            except Exception as e:
                print(f"{file_path.name:<30} ERROR {str(e)[:20]}")
        
        print("-" * 70)
        print(f"{'TOTAL':<30} {total_text:<5} {total_tree:<5} ({parse_failures} parse failures)")
        
        if total_text != total_tree:
            print(f"\n⚠️ Mismatch: {total_text} in text, {total_tree} in parse tree")
            sys.exit(1)
        else:
            print(f"\n✓ All {total_text} '{args.section_count}' sections accounted for!")
            sys.exit(0)

    print("Enhanced RealTest Script Validator")
    print("=" * 50)
    
    # Load the grammar
    parser = load_grammar(args.grammar)
    
    # Find .rts file(s)
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found at {file_path}")
            sys.exit(1)
        rts_files = [file_path]
        print(f"Found 1 file to validate: {file_path.name}")
    else:
        rts_files = find_rts_files(samples_dir)
    
    # Track results
    successful = []
    failed = []
    section_issues = []
    
    print(f"\nValidating {len(rts_files)} files...")
    print("-" * 50)
    
    # Validate each file
    for i, file_path in enumerate(rts_files, 1):
        print(f"[{i:3d}/{len(rts_files)}] {file_path.name}...", end=" ")
        
        success, error, content, tree, enhanced_valid, issues = validate_file(parser, file_path)
        
        if success:
            if enhanced_valid:
                print("✓ PASS")
                successful.append(file_path)
            else:
                print("⚠ PARSE OK, SECTION ISSUES")
                section_issues.append((file_path, issues))
            
            if args.verbose and tree:
                print_section_analysis(file_path, content, tree)
        else:
            print("✗ FAIL")
            failed.append((file_path, error, content))
            
            if args.early:
                print("\n--early flag set. Stopping at first error.")
                print_error_context(file_path, error, content)
                
                if content:
                    # Find last successful parse point
                    last_line, last_content, last_tree = find_last_successful_parse(parser, content)
                    
                    print(f"Last successfully parsed line: {last_line}")
                    
                    # Show the parse tree for the last successful content
                    if last_tree:
                        print("\nParse tree for last successful content:")
                        print("=" * 50)
                        print(last_tree.pretty())
                        print("=" * 50)
                    
                    print("Last successfully parsed content:")
                    print("-" * 30)

                    # Show last few lines of successful content
                    good_lines = last_content.splitlines()
                    start_show = max(0, len(good_lines) - 10)
                    for i, line in enumerate(good_lines[start_show:], start_show + 1):
                        print(f"{i:3d}: {line}")
                    
                    print("-" * 30)
                    print()
                    
                    # Show what comes next (the problematic part)
                    all_lines = content.splitlines()
                    if last_line < len(all_lines):
                        print("Next lines (where parsing fails):")
                        print("-" * 30)
                        end_show = min(len(all_lines), last_line + 10)
                        for i in range(last_line, end_show):
                            marker = ">>> " if i == last_line else "    "
                            print(f"{marker}{i+1:3d}: {all_lines[i]}")
                        print("-" * 30)
            
                sys.exit(1)
        
        # If only checking sections, skip parse failures
        if args.section_check_only and not success:
            continue

    # --- Summary Report ---
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    total_files = len(rts_files)
    success_count = len(successful)
    fail_count = len(failed)
    section_issue_count = len(section_issues)
    
    print(f"Total files: {total_files}")
    print(f"Parse successful: {success_count + section_issue_count} ({(success_count + section_issue_count)/total_files*100:.1f}%)")
    print(f"  - Clean parse: {success_count} ({success_count/total_files*100:.1f}%)")
    print(f"  - Section issues: {section_issue_count} ({section_issue_count/total_files*100:.1f}%)")
    print(f"Parse failed: {fail_count} ({fail_count/total_files*100:.1f}%)")
    
    if successful:
        print("\n✓ Clean files (no issues):")
        for file_path in successful:
            print(f"  - {file_path.name}")
    
    if section_issues:
        print("\n⚠ Files with section parsing issues:")
        for file_path, issues in section_issues:
            print(f"\n  - {file_path.name}:")
            for issue in issues:
                print(f"    * {issue}")

    if failed:
        print("\n✗ Failed files:")
        for file_path, error, content in failed:
            print(f"  - {file_path.name}")
            # Truncate long error messages in summary
            error_str = str(error).splitlines()[0]
            print(f"    Error: {error_str}")

        # Print details of the first failure if not using --early
        if not args.early and not args.section_check_only:
            print("\nFirst failure to fix:")
            first_fail_path, first_fail_error, first_fail_content = failed[0]
            print_error_context(first_fail_path, first_fail_error, first_fail_content)
        
        if not args.section_check_only:
            sys.exit(1)
    
    if section_issues and not failed:
        print(f"\n⚠ All files parse but {section_issue_count} have section issues that need attention.")
        sys.exit(1)
    
    if not failed and not section_issues:
        print("\n✨ All files parsed successfully with no section issues! ✨")
        sys.exit(0)


if __name__ == "__main__":
    main()
