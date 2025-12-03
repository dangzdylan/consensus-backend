"""
Input validation utilities module.
Contains helper functions for validating user input and data.
"""

import re
from typing import Dict, Any, Optional, Tuple


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_lobby_code(code: str) -> bool:
    """
    Validate lobby join code format.
    
    Args:
        code: Lobby code to validate (should be 4 alphanumeric characters)
        
    Returns:
        bool: True if code is valid, False otherwise
    """
    if not code or len(code) != 4:
        return False
    pattern = r'^[A-Z0-9]{4}$'
    return bool(re.match(pattern, code.upper()))


def validate_location(location: Dict[str, float]) -> Tuple[bool, Optional[str]]:
    """
    Validate location coordinates.
    
    Args:
        location: Dictionary with 'latitude' and 'longitude' keys
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(location, dict):
        return False, "Location must be a dictionary"
    
    lat = location.get("latitude")
    lng = location.get("longitude")
    
    if lat is None or lng is None:
        return False, "Location must contain 'latitude' and 'longitude'"
    
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return False, "Latitude and longitude must be numbers"
    
    if not (-90 <= lat <= 90):
        return False, "Latitude must be between -90 and 90"
    
    if not (-180 <= lng <= 180):
        return False, "Longitude must be between -180 and 180"
    
    return True, None


def validate_radius(radius: float) -> Tuple[bool, Optional[str]]:
    """
    Validate search radius.
    
    Args:
        radius: Radius in miles
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(radius, (int, float)):
        return False, "Radius must be a number"
    
    if radius < 0.1 or radius > 50:
        return False, "Radius must be between 0.1 and 50 miles"
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 30:
        return False, "Username must be at most 30 characters"
    
    pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(pattern, username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None

