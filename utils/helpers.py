"""
Shared utility functions module.
Contains common helper functions used across the application.
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime


def generate_uuid() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())


def format_error_response(message: str, status_code: int = 400) -> tuple:
    """
    Format an error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        
    Returns:
        tuple: (response_dict, status_code)
    """
    return {"error": message}, status_code


def format_success_response(data: Any, message: Optional[str] = None, status_code: int = 200) -> tuple:
    """
    Format a success response.
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code
        
    Returns:
        tuple: (response_dict, status_code)
    """
    response = {"data": data}
    if message:
        response["message"] = message
    return response, status_code


def jsonify_error(message: str, status_code: int = 400):
    """
    Create a JSON error response with proper status code.
    
    Args:
        message: Error message
        status_code: HTTP status code
        
    Returns:
        Flask Response tuple: (jsonify(response_dict), status_code)
    """
    from flask import jsonify
    return jsonify({"error": message}), status_code


def jsonify_success(data: Any, message: Optional[str] = None, status_code: int = 200):
    """
    Create a JSON success response with proper status code.
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code
        
    Returns:
        Flask Response tuple: (jsonify(response_dict), status_code)
    """
    from flask import jsonify
    response = {"data": data}
    if message:
        response["message"] = message
    return jsonify(response), status_code


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO format datetime string to datetime object.
    
    Args:
        dt_str: ISO format datetime string
        
    Returns:
        datetime object or None
    """
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None

