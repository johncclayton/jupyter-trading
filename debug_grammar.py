#!/usr/bin/env python3
"""
Grammar Debugging Helper

This script helps debug grammar parsing issues by showing detailed section boundaries
and parse tree analysis.
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


def extract_sections_with_positions(content: str):
    """Extract section headers with their exact positions in the text"""
    section_pattern = r'^(Notes|Parameters|Import|Strategy|Data|Template|Settings|Charts|Include|Library|Scan|TestData|Combined|Benchmark|OptimizeSettings|OrderSettings|ScanSettings|TestSettings|WalkForward|StatsGroup|StratData|Namespace)\s*:\s*(.*?)$'
    
    sections = []
    lines = content.splitlines()
    
    for line_num, line in enumerate(lines, 1):
        match = re.match(section_pattern, line.strip())
        if match:
            section_name = match.group(1)
            section_value = match.group(2).strip() if match.group(2) else ""
            sections.append({
                'name': section_name,
                'value': section_value,
                'line': line_num,
                'full_line': line
            })
    
    return sections


def analyze_parse_tree_sections(tree: Tree, content: str):
    """Analyze parse tree sections and map them to line ranges"""
    lines = content.splitlines()
    sections_info = []
    
    def walk_tree(node, depth=0):
        indent = "  " * depth
        
        if isinstance(node, Tree):
            if node.data.endswith('_section'):
                section_type = node.data.replace('_section', '').title()
                
                # Try to determine the line range for this section
                # This is approximate since Lark doesn't provide exact position info
                section_info = {
                    'type': section_type,
                    'tree_node': node.data,
                    'children_count': len(node.children),
                    'depth': depth
                }
                
                # Try to extract section name for generic sections
                if node.data == 'generic_section':
                    for child in node.children:
                        if hasattr(child, 'type') and child.type == 'SECTION_NAME':
                            section_info['name'] = str(child)
                            break
                
                sections_info.append(section_info)
                print(f"{indent}📂 {section_type} Section ({node.data})")
                
                # Show children structure
                for i, child in enumerate(node.children):
                    if hasattr(child, 'type'):
                        print(f"{indent}  [{i}] Token: {child.type} = {repr(str(child)[:50])}")
                    elif isinstance(child, Tree):
                        print(f"{indent}  [{i}] Tree: {child.data}")
                        walk_tree(child, depth + 2)
                    else:
                        print(f"{indent}  [{i}] Other: {repr(str(child)[:50])}")
            else:
                # Continue walking for non-section nodes
                for child in node.children:
                    walk_tree(child, depth)
    
    print("🌳 Parse Tree Section Analysis:")
    print("=" * 60)
    walk_tree(tree)
    print("=" * 60)
    
    return sections_info


def main():
    parser = argparse.ArgumentParser(description="Grammar Debugging Helper")
    parser.add_argument("file", help="Path to .rts file to analyze")
    parser.add_argument("--grammar", default="lark/realtest.lark", help="Grammar file to use")
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
    
    # Load content
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print(f"🔍 Analyzing: {file_path}")
    print("=" * 60)
    
    # Extract sections from text
    text_sections = extract_sections_with_positions(content)
    print(f"📄 Sections found in text ({len(text_sections)}):")
    for section in text_sections:
        print(f"  Line {section['line']:2d}: {section['name']} = {section['value']}")
    print()
    
    # Parse with grammar
    try:
        grammar = load_grammar(args.grammar)
        tree = grammar.parse(content)
        print("✅ Parse successful!")
        print()
        
        # Analyze parse tree
        tree_sections = analyze_parse_tree_sections(tree, content)
        
        # Compare
        print("🔄 Comparison:")
        text_names = [s['name'] for s in text_sections]
        tree_names = [s.get('name', s['type']) for s in tree_sections]
        
        print(f"Text sections: {text_names}")
        print(f"Tree sections: {tree_names}")
        
        # Count differences
        from collections import Counter
        text_counts = Counter(text_names)
        tree_counts = Counter(tree_names)
        
        print("\n📊 Section counts:")
        all_sections = set(text_counts.keys()) | set(tree_counts.keys())
        for section in sorted(all_sections):
            text_count = text_counts.get(section, 0)
            tree_count = tree_counts.get(section, 0)
            status = "✅" if text_count == tree_count else "❌"
            print(f"  {status} {section}: text={text_count}, tree={tree_count}")
        
    except Exception as e:
        print(f"❌ Parse failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())