#!/usr/bin/env python3
"""
RTS Grammar Issue Analyzer

This script provides detailed analysis of grammar parsing issues and suggestions
for fixing them. It's designed to help with iterative grammar development.
"""

import re
from pathlib import Path
from lark import Lark, Tree
import argparse


def load_grammar(grammar_path_str="lark/realtest.lark"):
    """Load the Lark grammar from the specified path"""
    grammar_path = Path(grammar_path_str)
    
    with open(grammar_path, 'r', encoding='utf-8') as f:
        grammar_content = f.read()
    
    parser = Lark(grammar_content, 
                  debug=True,
                  start='start',
                  parser='earley')
    return parser


def extract_sections_detailed(content: str):
    """Extract detailed section information"""
    section_pattern = r'^(Notes|Parameters|Import|Strategy|Data|Template|Settings|Charts|Include|Library|Scan|TestData|Combined|Benchmark|OptimizeSettings|OrderSettings|ScanSettings|TestSettings|WalkForward|StatsGroup|StratData|Namespace)\s*:\s*(.*?)$'
    
    sections = []
    lines = content.splitlines()
    
    for line_num, line in enumerate(lines, 1):
        match = re.match(section_pattern, line.strip())
        if match:
            section_name = match.group(1)
            section_value = match.group(2).strip() if match.group(2) else ""
            
            # Find the content that follows this section (until next section or EOF)
            content_lines = []
            for next_line_num in range(line_num, len(lines)):
                next_line = lines[next_line_num]
                # Check if this line starts a new section
                if next_line_num > line_num - 1 and re.match(section_pattern, next_line.strip()):
                    break
                content_lines.append(next_line)
            
            sections.append({
                'name': section_name,
                'value': section_value,
                'line': line_num,
                'full_line': line,
                'content_lines': content_lines[1:] if content_lines else [],  # Skip the section header itself
                'next_section_line': line_num + len(content_lines) if len(content_lines) < len(lines) - line_num + 1 else None
            })
    
    return sections


def extract_sections_from_tree(tree: Tree):
    """Extract section names from parse tree"""
    sections = []
    
    def walk_tree(node):
        if isinstance(node, Tree):
            if node.data == 'notes_section':
                sections.append('Notes')
            elif node.data == 'parameters_section':
                sections.append('Parameters')
            elif node.data == 'charts_section':
                sections.append('Charts')
            elif node.data == 'benchmark_section':
                sections.append('Benchmark')
            elif node.data == 'strategy_section':
                sections.append('Strategy')
            elif node.data == 'generic_section':
                for child in node.children:
                    if hasattr(child, 'type') and child.type == 'SECTION_NAME':
                        sections.append(str(child))
                        break
            
            for child in node.children:
                walk_tree(child)
    
    walk_tree(tree)
    return sections


def analyze_section_consumption(content: str, tree: Tree):
    """Analyze which sections might be consuming others"""
    text_sections = extract_sections_detailed(content)
    tree_sections = extract_sections_from_tree(tree)
    issues = []
    
    # Compare text vs tree section counts
    from collections import Counter
    text_counts = Counter(s['name'] for s in text_sections)
    tree_counts = Counter(tree_sections)
    
    # Find mismatches
    all_section_names = set(text_counts.keys()) | set(tree_counts.keys())
    for section_name in all_section_names:
        text_count = text_counts.get(section_name, 0)
        tree_count = tree_counts.get(section_name, 0)
        
        if text_count > tree_count:
            # More sections in text than in tree - likely consumption issue
            text_instances = [s for s in text_sections if s['name'] == section_name]
            
            if len(text_instances) > 1:
                issues.append({
                    'type': 'section_consumption',
                    'message': f"Section '{section_name}' appears {text_count} times in text but only {tree_count} times in parse tree",
                    'text_count': text_count,
                    'tree_count': tree_count,
                    'section_lines': [s['line'] for s in text_instances],
                    'suggestion': f"The first {section_name} section may be consuming subsequent {section_name} sections. Check section body termination rules."
                })
            else:
                issues.append({
                    'type': 'missing_section',
                    'message': f"Section '{section_name}' found in text but missing from parse tree",
                    'text_count': text_count,
                    'tree_count': tree_count,
                    'suggestion': f"The {section_name} section may not have a specific grammar rule, or it's being consumed by another section."
                })

    
    return issues


def suggest_grammar_fixes(issues):
    """Provide specific suggestions for fixing grammar issues"""
    suggestions = []
    
    for issue in issues:
        if issue['type'] == 'notes_consumption':
            suggestions.append({
                'issue': issue['message'],
                'fix': """
Consider updating the NOTE_BLOCK regex pattern to be more restrictive:
Current: NOTE_BLOCK: /(?:[^\\r\\n]*\\r?\\n)+?(?=^[.a-zA-Z_@][a-zA-Z0-9_.@]*:|\\Z)/m
Suggested: NOTE_BLOCK: /(?:[^\\r\\n]*\\r?\\n)+?(?=^(?:Notes|Parameters|Import|Strategy|Data|Template|Settings|Charts|Include|Library|Scan|TestData|Combined|Benchmark|OptimizeSettings|OrderSettings|ScanSettings|TestSettings|WalkForward|StatsGroup|StratData|Namespace)\\s*:|\\Z)/m

This makes the lookahead pattern more specific to actual section names.
                """.strip()
            })
        
        elif issue['type'] == 'section_consumption':
            suggestions.append({
                'issue': issue['message'],
                'fix': f"""
The grammar may need better section boundary detection. Consider:
1. Using negative lookaheads in the section body rules
2. Making the section_item rules more restrictive
3. Ensuring section headers are not treated as key-value pairs within sections

For Strategy sections specifically, ensure that "Strategy:" lines are recognized as 
section boundaries rather than content within a strategy section.
                """.strip()
            })
    
    return suggestions


def main():
    parser = argparse.ArgumentParser(description="RTS Grammar Issue Analyzer")
    parser.add_argument("file", help="Path to .rts file to analyze")
    parser.add_argument("--grammar", default="lark/realtest.lark", help="Grammar file to use")
    parser.add_argument("--show-content", action="store_true", help="Show section content details")
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
    
    # Load content
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print(f"🔍 Grammar Issue Analysis: {file_path}")
    print("=" * 60)
    
    # Extract sections from text
    text_sections = extract_sections_detailed(content)
    print(f"📄 Sections found in text ({len(text_sections)}):")
    for section in text_sections:
        print(f"  Line {section['line']:2d}: {section['name']} = {section['value']}")
        if args.show_content and section['content_lines']:
            print(f"    Content: {len(section['content_lines'])} lines")
            for i, line in enumerate(section['content_lines'][:3]):  # Show first 3 lines
                print(f"      {i+1}: {line}")
            if len(section['content_lines']) > 3:
                print(f"      ... ({len(section['content_lines']) - 3} more lines)")
    print()
    
    # Parse with grammar
    try:
        grammar = load_grammar(args.grammar)
        tree = grammar.parse(content)
        print("✅ Parse successful!")
        
        # Analyze consumption issues
        issues = analyze_section_consumption(content, tree)
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} potential grammar issues:")
            for i, issue in enumerate(issues, 1):
                print(f"\n{i}. {issue['message']}")
                if 'suggestion' in issue:
                    print(f"   💡 {issue['suggestion']}")
            
            # Provide specific fix suggestions
            suggestions = suggest_grammar_fixes(issues)
            if suggestions:
                print(f"\n🔧 Suggested Grammar Fixes:")
                print("=" * 40)
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"\n{i}. Issue: {suggestion['issue']}")
                    print(f"   Fix:\n{suggestion['fix']}")
        else:
            print("\n✅ No grammar consumption issues detected!")
        
    except Exception as e:
        print(f"❌ Parse failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())