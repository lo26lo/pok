#!/usr/bin/env python3
"""
Code Profiler - Analyzes Python files for common performance issues
====================================================================

Scans the codebase and identifies potential performance bottlenecks:
- Nested loops
- Repeated file I/O
- Large list comprehensions
- Unoptimized image processing

Usage:
    python tests/test_code_profiling.py
    python tests/test_code_profiling.py --module core/augmentation.py
"""

import sys
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
import argparse


class CodeProfiler:
    """Analyzes Python code for performance issues"""
    
    def __init__(self):
        self.issues = []
        
    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a single Python file"""
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        issues = {
            'file': filepath,
            'nested_loops': [],
            'file_io_in_loops': [],
            'large_comprehensions': [],
            'pixel_loops': [],
            'score': 0
        }
        
        # 1. Detect nested loops
        in_loop = False
        loop_indent = 0
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            
            if stripped.startswith('for ') and ':' in stripped:
                if in_loop and indent > loop_indent:
                    issues['nested_loops'].append({
                        'line': i,
                        'code': line.strip()
                    })
                    issues['score'] += 10
                in_loop = True
                loop_indent = indent
            elif stripped and not stripped.startswith('#') and indent <= loop_indent:
                in_loop = False
        
        # 2. Detect file I/O in loops
        io_patterns = ['cv2.imread', 'cv2.imwrite', 'open(', 'pd.read_excel', 'yaml.safe_load']
        for i, line in enumerate(lines, 1):
            # Check if line is in a loop (simple heuristic)
            if any(pattern in line for pattern in io_patterns):
                # Look back for 'for' statement
                for j in range(max(0, i-10), i):
                    if 'for ' in lines[j] and ':' in lines[j]:
                        issues['file_io_in_loops'].append({
                            'line': i,
                            'code': line.strip()
                        })
                        issues['score'] += 5
                        break
        
        # 3. Detect large list comprehensions
        comp_pattern = r'\[[^\]]{100,}\sfor\s'
        matches = re.finditer(comp_pattern, content)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues['large_comprehensions'].append({
                'line': line_num,
                'code': match.group()[:80] + '...'
            })
            issues['score'] += 3
        
        # 4. Detect pixel-level loops (critical performance issue)
        pixel_pattern = r'for\s+\w+\s+in\s+range\([^)]*(?:width|height|w|h)\)'
        matches = re.finditer(pixel_pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            # Check if there's a nested loop within next 5 lines
            next_lines = lines[line_num:line_num+5]
            if any('for ' in l and 'range' in l for l in next_lines):
                issues['pixel_loops'].append({
                    'line': line_num,
                    'code': lines[line_num-1].strip() if line_num > 0 else ''
                })
                issues['score'] += 20  # Critical issue
        
        return issues
    
    def analyze_directory(self, directory: str, exclude_optimized: bool = True) -> List[Dict]:
        """Analyze all Python files in a directory"""
        results = []
        
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            if '__pycache__' in root or '.venv' in root or 'obsolete' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    # Skip optimized files if requested
                    if exclude_optimized and 'optimized' in file:
                        continue
                    
                    filepath = os.path.join(root, file)
                    result = self.analyze_file(filepath)
                    if result and result['score'] > 0:
                        results.append(result)
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def print_report(self, results: List[Dict]):
        """Print formatted report"""
        print("\n" + "="*70)
        print("🔍 CODE PERFORMANCE ANALYSIS REPORT")
        print("="*70)
        
        if not results:
            print("\n✅ No significant performance issues detected!")
            print("    All files look optimized!")
            return
        
        print(f"\n📊 Found {len(results)} files with potential issues\n")
        
        for idx, result in enumerate(results, 1):
            filename = os.path.basename(result['file'])
            score = result['score']
            
            # Determine severity
            if score >= 20:
                severity = "🔴 CRITICAL"
            elif score >= 10:
                severity = "🟡 HIGH"
            else:
                severity = "🟢 MEDIUM"
            
            print(f"{idx}. {severity} - {filename} (Score: {score})")
            print(f"   Path: {result['file']}")
            
            if result['pixel_loops']:
                print(f"\n   ⚠️  PIXEL-LEVEL LOOPS (Very Slow!):")
                for issue in result['pixel_loops'][:3]:
                    print(f"      Line {issue['line']}: {issue['code'][:60]}")
            
            if result['nested_loops']:
                print(f"\n   🔄 NESTED LOOPS:")
                for issue in result['nested_loops'][:3]:
                    print(f"      Line {issue['line']}: {issue['code'][:60]}")
            
            if result['file_io_in_loops']:
                print(f"\n   💾 FILE I/O IN LOOPS:")
                for issue in result['file_io_in_loops'][:3]:
                    print(f"      Line {issue['line']}: {issue['code'][:60]}")
            
            if result['large_comprehensions']:
                print(f"\n   📦 LARGE COMPREHENSIONS:")
                for issue in result['large_comprehensions'][:2]:
                    print(f"      Line {issue['line']}: {issue['code'][:60]}")
            
            print()
        
        print("="*70)
        print("\n💡 Recommendations:")
        print("   1. Check if optimized version exists (*_optimized.py)")
        print("   2. Use NumPy vectorization for pixel loops")
        print("   3. Move file I/O outside loops when possible")
        print("   4. Use batch processing for large datasets")
        print("\n📖 See docs/PERFORMANCE_GUIDE.md for detailed optimization tips")
        print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Profile code for performance issues")
    parser.add_argument("--module", type=str, help="Specific module to analyze")
    parser.add_argument("--directory", type=str, default="core", help="Directory to scan")
    parser.add_argument("--include-optimized", action="store_true", 
                       help="Include *_optimized.py files in analysis")
    args = parser.parse_args()
    
    profiler = CodeProfiler()
    
    if args.module:
        # Analyze single file
        print(f"🔍 Analyzing: {args.module}")
        result = profiler.analyze_file(args.module)
        if result:
            profiler.print_report([result])
        else:
            print(f"❌ Could not analyze: {args.module}")
    else:
        # Analyze directory
        print(f"🔍 Scanning directory: {args.directory}")
        results = profiler.analyze_directory(
            args.directory, 
            exclude_optimized=not args.include_optimized
        )
        profiler.print_report(results)


if __name__ == "__main__":
    main()
