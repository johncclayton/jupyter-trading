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


def load_grammar():
    """Load the Lark grammar from realtest.lark"""
    grammar_path = Path("lark/realtest.lark")
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
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to parse the content
        tree = parser.parse(content)
        return True, None
        
    except FileNotFoundError:
        return False, f"File not found: {file_path}"
    except ParseError as e:
        return False, f"Parse error: {e}"
    except LexError as e:
        return False, f"Lexical error: {e}"
    except UnexpectedInput as e:
        return False, f"Unexpected input: {e}"
    except Exception as e:
        return False, f"Unknown error: {e}"


def main():
    """Main validation loop"""
    print("RealTest Script Validator")
    print("=" * 50)
    
    # Load the grammar
    parser = load_grammar()
    
    # Find all .rts files
    rts_files = find_rts_files()
    
    # Track results
    successful = []
    failed = []
    
    print(f"\nValidating {len(rts_files)} files...")
    print("-" * 50)
    
    # Validate each file
    for i, file_path in enumerate(rts_files, 1):
        print(f"[{i:3d}/{len(rts_files)}] {file_path.name}...", end=" ")
        
        success, error = validate_file(parser, file_path)
        
        if success:
            print("✓ PASS")
            successful.append(file_path)
        else:
            print("✗ FAIL")
            failed.append((file_path, error))
            # Print the first error in detail to help with debugging
            if len(failed) == 1:
                print(f"\nFirst error details:")
                print(f"File: {file_path}")
                print(f"Error: {error}")
                print()
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total files: {len(rts_files)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(rts_files)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(rts_files)*100:.1f}%)")
    
    if successful:
        print(f"\n✓ Successfully parsed files:")
        for file_path in successful:
            print(f"  - {file_path.name}")
    
    if failed:
        print(f"\n✗ Failed files:")
        for file_path, error in failed:
            print(f"  - {file_path.name}")
            # Show just the first line of the error to keep output manageable
            error_line = str(error).split('\n')[0]
            print(f"    Error: {error_line}")
        
        print(f"\nFirst failure to fix:")
        first_failed_file, first_error = failed[0]
        print(f"File: {first_failed_file}")
        print(f"Full error:\n{first_error}")
        
        # Show a few lines around the error location if it's a parse error
        if "line" in str(first_error).lower():
            try:
                with open(first_failed_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                print(f"\nFile content preview (first 20 lines):")
                for i, line in enumerate(lines[:20], 1):
                    print(f"{i:3d}: {line.rstrip()}")
            except Exception as e:
                print(f"Could not read file for preview: {e}")
    
    return len(failed) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)