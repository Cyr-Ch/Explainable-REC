"""Validation utilities for Chat-SGP"""
from typing import Dict, Any, List, Optional


def validate_question(question: str) -> tuple[bool, Optional[str]]:
    """
    Validate a question string
    
    Args:
        question: Question string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(question, str):
        return False, f"Question must be a string, got {type(question)}"
    
    if len(question.strip()) == 0:
        return False, "Question cannot be empty"
    
    if len(question) > 1000:
        return False, "Question is too long (max 1000 characters)"
    
    return True, None


def validate_operations(ops: List[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
    """
    Validate operations list
    
    Args:
        ops: List of operation dictionaries
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(ops, list):
        return False, f"Operations must be a list, got {type(ops)}"
    
    valid_ops = ['scale_series', 'shift_load']
    valid_targets = ['PV', 'Load', 'Pimp', 'Pexp']
    
    for i, op in enumerate(ops):
        if not isinstance(op, dict):
            return False, f"Operation {i} must be a dictionary"
        
        op_type = op.get('op')
        if op_type not in valid_ops:
            return False, f"Invalid operation type '{op_type}' at index {i}. Must be one of {valid_ops}"
        
        if op_type == 'scale_series':
            if 'target' not in op:
                return False, f"Operation {i} missing 'target' field"
            if op['target'] not in valid_targets:
                return False, f"Invalid target '{op['target']}' at index {i}. Must be one of {valid_targets}"
            if 'scale_pct' not in op:
                return False, f"Operation {i} missing 'scale_pct' field"
            if not isinstance(op['scale_pct'], (int, float)):
                return False, f"scale_pct must be a number at index {i}"
        
        elif op_type == 'shift_load':
            required_fields = ['percentage', 'from_hour', 'to_hour']
            for field in required_fields:
                if field not in op:
                    return False, f"Operation {i} missing '{field}' field"
            if not isinstance(op['percentage'], (int, float)):
                return False, f"percentage must be a number at index {i}"
            if not isinstance(op['from_hour'], int) or not (0 <= op['from_hour'] < 24):
                return False, f"from_hour must be an integer between 0 and 23 at index {i}"
            if not isinstance(op['to_hour'], int) or not (0 <= op['to_hour'] < 24):
                return False, f"to_hour must be an integer between 0 and 23 at index {i}"
    
    return True, None


def validate_optimization_result(result: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate optimization result
    
    Args:
        result: Optimization result dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(result, dict):
        return False, f"Result must be a dictionary, got {type(result)}"
    
    if 'status' not in result:
        return False, "Result missing 'status' field"
    
    valid_statuses = ['optimal', 'infeasible', 'unbounded', 'other', 'error']
    if result['status'] not in valid_statuses:
        return False, f"Invalid status '{result['status']}'. Must be one of {valid_statuses}"
    
    if 'objective' not in result:
        return False, "Result missing 'objective' field"
    
    if not isinstance(result['objective'], (int, float)):
        return False, "objective must be a number"
    
    return True, None

