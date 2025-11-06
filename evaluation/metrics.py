"""
Evaluation metrics for Chat-SGP

Provides functions to calculate various evaluation metrics for optimization results.
"""

from typing import Dict, List, Any
import json


def calculate_cost_accuracy(predicted_cost: float, actual_cost: float) -> float:
    """
    Calculate cost prediction accuracy.
    
    Args:
        predicted_cost: Predicted cost value
        actual_cost: Actual cost value
    
    Returns:
        Accuracy as a percentage (0-100)
    """
    if actual_cost == 0:
        return 100.0 if predicted_cost == 0 else 0.0
    
    error = abs(predicted_cost - actual_cost) / actual_cost * 100
    return max(0.0, 100.0 - error)


def calculate_parsing_accuracy(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate parsing accuracy metrics.
    
    Args:
        results: List of result dictionaries with 'ops' and 'explanation' fields
    
    Returns:
        Dictionary with accuracy metrics
    """
    total = len(results)
    if total == 0:
        return {'total': 0, 'llm_parsing': 0.0, 'rule_based_parsing': 0.0}
    
    llm_count = sum(1 for r in results if r.get('ops', {}).get('explanation') == 'llm-with-icl')
    rule_based_count = sum(1 for r in results if r.get('ops', {}).get('explanation') == 'rule-based')
    
    return {
        'total': total,
        'llm_parsing': (llm_count / total * 100) if total > 0 else 0.0,
        'rule_based_parsing': (rule_based_count / total * 100) if total > 0 else 0.0
    }


def calculate_success_rate(results: List[Dict[str, Any]]) -> float:
    """
    Calculate success rate (percentage of successful optimizations).
    
    Args:
        results: List of result dictionaries with 'result' field containing 'status'
    
    Returns:
        Success rate as a percentage (0-100)
    """
    if not results:
        return 0.0
    
    successful = sum(
        1 for r in results 
        if r.get('result', {}).get('status') == 'optimal'
    )
    
    return (successful / len(results) * 100) if results else 0.0


def calculate_average_cost(results: List[Dict[str, Any]]) -> float:
    """
    Calculate average cost across all successful optimizations.
    
    Args:
        results: List of result dictionaries with 'result' field containing 'objective'
    
    Returns:
        Average cost, or 0.0 if no successful results
    """
    costs = [
        r.get('result', {}).get('objective', 0)
        for r in results
        if r.get('result', {}).get('status') == 'optimal'
    ]
    
    return sum(costs) / len(costs) if costs else 0.0


def generate_evaluation_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a comprehensive evaluation report.
    
    Args:
        results: List of result dictionaries from batch evaluation
    
    Returns:
        Dictionary with evaluation metrics
    """
    return {
        'total_questions': len(results),
        'success_rate': calculate_success_rate(results),
        'parsing_accuracy': calculate_parsing_accuracy(results),
        'average_cost': calculate_average_cost(results),
        'successful_count': sum(
            1 for r in results 
            if r.get('result', {}).get('status') == 'optimal'
        ),
        'failed_count': sum(
            1 for r in results 
            if r.get('result', {}).get('status') != 'optimal'
        )
    }

