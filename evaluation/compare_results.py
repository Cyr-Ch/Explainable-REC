"""
Result comparison tool for Chat-SGP

Compares results from different runs or configurations.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd


def load_results(file_path: str) -> List[Dict[str, Any]]:
    """
    Load results from a JSONL file.
    
    Args:
        file_path: Path to JSONL file with results
    
    Returns:
        List of result dictionaries
    """
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def compare_results(
    results1: List[Dict[str, Any]],
    results2: List[Dict[str, Any]],
    label1: str = "Run 1",
    label2: str = "Run 2"
) -> Dict[str, Any]:
    """
    Compare two sets of results.
    
    Args:
        results1: First set of results
        results2: Second set of results
        label1: Label for first set
        label2: Label for second set
    
    Returns:
        Dictionary with comparison metrics
    """
    # Extract costs
    costs1 = [
        r.get('result', {}).get('objective', 0)
        for r in results1
        if r.get('result', {}).get('status') == 'optimal'
    ]
    costs2 = [
        r.get('result', {}).get('objective', 0)
        for r in results2
        if r.get('result', {}).get('status') == 'optimal'
    ]
    
    # Calculate statistics
    avg_cost1 = sum(costs1) / len(costs1) if costs1 else 0.0
    avg_cost2 = sum(costs2) / len(costs2) if costs2 else 0.0
    
    success_rate1 = sum(
        1 for r in results1 
        if r.get('result', {}).get('status') == 'optimal'
    ) / len(results1) * 100 if results1 else 0.0
    
    success_rate2 = sum(
        1 for r in results2 
        if r.get('result', {}).get('status') == 'optimal'
    ) / len(results2) * 100 if results2 else 0.0
    
    return {
        label1: {
            'average_cost': avg_cost1,
            'success_rate': success_rate1,
            'total_questions': len(results1),
            'successful': len(costs1)
        },
        label2: {
            'average_cost': avg_cost2,
            'success_rate': success_rate2,
            'total_questions': len(results2),
            'successful': len(costs2)
        },
        'difference': {
            'cost_difference': avg_cost2 - avg_cost1,
            'cost_difference_pct': ((avg_cost2 - avg_cost1) / avg_cost1 * 100) if avg_cost1 > 0 else 0.0,
            'success_rate_difference': success_rate2 - success_rate1
        }
    }


def compare_result_files(
    file1: str,
    file2: str,
    label1: Optional[str] = None,
    label2: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compare results from two JSONL files.
    
    Args:
        file1: Path to first results file
        file2: Path to second results file
        label1: Optional label for first file (defaults to filename)
        label2: Optional label for second file (defaults to filename)
    
    Returns:
        Dictionary with comparison metrics
    """
    results1 = load_results(file1)
    results2 = load_results(file2)
    
    label1 = label1 or Path(file1).stem
    label2 = label2 or Path(file2).stem
    
    return compare_results(results1, results2, label1, label2)

