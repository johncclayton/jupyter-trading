#!/usr/bin/env python3
"""
RealTest Script Validator

This script validates all .rts files in the samples/ directory using the realtest.lark grammar.
It will report parsing errors to help iteratively refine the grammar.
"""

import os
import sys
from pathlib import Path
from lark import Lark, LarkError
from lark.exceptions import ParseError, LexError, UnexpectedInput
import argparse


def load_grammar(grammar_path_str="lark/realtest.lark"):
    """Load the Lark grammar from the specified path"""
    grammar_path = Path(grammar_path_str)
    if not grammar_path.exists():
        print(f"Error: Grammar file not found at {grammar_path}")
        sys.exit(1)
    
    try:
        with open(grammar_path, 'r', encoding='utf-8') as f:
            grammar_content = f.read()
        
        parser = Lark(grammar_content, start='start', parser='earley')
        print(f"✓ Grammar loaded successfully from {grammar_path}")
        return parser
    except Exception as e:
        print(f"Error loading grammar: {e}")
        sys.exit(1)


def find_rts_files():
    """Find all .rts files in the samples/ directory"""
    samples_dir = Path("samples")
    if not samples_dir.exists():
        print(f"Error: Samples directory not found at {samples_dir}")
        sys.exit(1)
    
    rts_files = list(samples_dir.glob("*.rts"))
    if not rts_files:
        print(f"No .rts files found in {samples_dir}")
        sys.exit(1)
    
    print(f"Found {len(rts_files)} .rts files in {samples_dir}")
    return sorted(rts_files)


def validate_file(parser, file_path):
    """Validate a single .rts file using the parser"""
    content = None
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to parse the content
        parser.parse(content)
        return True, None, None
        
    except FileNotFoundError:
        return False, f"File not found: {file_path}", None
    except (ParseError, LexError, UnexpectedInput) as e:
        return False, e, content
    except Exception as e:
        return False, e, content


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


def main():
    """Main validation loop"""
    parser = argparse.ArgumentParser(description="RealTest Script Validator")
    parser.add_argument(
        "--early",
        action="store_true",
        help="Stop validation at the first file that fails to parse.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a single .rts file to validate.",
    )
    parser.add_argument(
        "--grammar",
        type=str,
        default="lark/realtest.lark",
        help="Path to the grammar file to use (e.g., lark/realtest2.lark).",
    )
    args = parser.parse_args()

    print("RealTest Script Validator")
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
        rts_files = find_rts_files()
    
    # Track results
    successful = []
    failed = []
    
    print(f"\nValidating {len(rts_files)} files...")
    print("-" * 50)
    
    # Validate each file
    for i, file_path in enumerate(rts_files, 1):
        print(f"[{i:3d}/{len(rts_files)}] {file_path.name}...", end=" ")
        
        success, error, content = validate_file(parser, file_path)
        
        if success:
            print("✓ PASS")
            successful.append(file_path)
        else:
            print("✗ FAIL")
            failed.append((file_path, error, content))
            if args.early:
                print("\n--early flag set. Stopping at first error.")
                print_error_context(file_path, error, content)
                sys.exit(1)

    # --- Summary Report ---
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    total_files = len(rts_files)
    success_count = len(successful)
    fail_count = len(failed)
    
    print(f"Total files: {total_files}")
    print(f"Successful: {success_count} ({success_count/total_files*100:.1f}%)")
    print(f"Failed: {fail_count} ({fail_count/total_files*100:.1f}%)")
    
    if successful and fail_count > 0:
        print("\n✓ Successfully parsed files:")
        for file_path in successful:
            print(f"  - {file_path.name}")

    if failed:
        print("\n✗ Failed files:")
        for file_path, error, content in failed:
            print(f"  - {file_path.name}")
            # Truncate long error messages in summary
            error_str = str(error).splitlines()[0]
            print(f"    Error: {error_str}")

        # Print details of the first failure if not using --early
        if not args.early:
            print("\nFirst failure to fix:")
            first_fail_path, first_fail_error, first_fail_content = failed[0]
            print_error_context(first_fail_path, first_fail_error, first_fail_content)
        
        sys.exit(1)
    else:
        print("\n✨ All files parsed successfully! ✨")
        sys.exit(0)


if __name__ == "__main__":
    main()