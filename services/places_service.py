"""
Places service module.
Handles filtering and retrieving hardcoded places data.
"""

import math
from typing import List, Dict, Any, Optional
from data.places import ALL_PLACES, get_coords, parse_hours

# Map frontend categories to our data categories
CATEGORY_MAP = {
    "Food": "Food",
    "Recreation & Entertainment": "Recreation & Entertainment",
    "Nature": "Nature",
    "Arts": "Arts",
    "Social": "Social",
}


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in miles using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in miles
    """
    # Earth's radius in miles
    R = 3959.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance


def get_places_by_category_and_location(
    category: str,
    location: Dict[str, float],
    radius: float,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get places filtered by category and within radius of location.
    
    Args:
        category: Activity category (Food, Recreation & Entertainment, Nature, Arts, Social)
        location: Dictionary with 'latitude' and 'longitude'
        radius: Radius in miles
        limit: Maximum number of results (optional)
    
    Returns:
        List of places with distance calculated
    """
    # Map category
    mapped_category = CATEGORY_MAP.get(category, category)
    
    # Filter by category
    filtered_places = [p for p in ALL_PLACES if p.get("category") == mapped_category]
    
    # Get location coordinates
    center_lat = location.get("latitude")
    center_lon = location.get("longitude")
    
    if not center_lat or not center_lon:
        return []
    
    # Calculate distance for each place and filter by radius
    places_with_distance = []
    for place in filtered_places:
        # Get coordinates for this place
        place_coords = get_coords(place.get("address", ""), place.get("city", ""))
        place_lat = place_coords["latitude"]
        place_lon = place_coords["longitude"]
        
        # Calculate distance
        distance = calculate_distance(center_lat, center_lon, place_lat, place_lon)
        
        # Filter by radius
        if distance <= radius:
            place_copy = place.copy()
            place_copy["location"] = {"latitude": place_lat, "longitude": place_lon}
            place_copy["distance"] = round(distance, 2)
            place_copy["hours"] = parse_hours(place.get("hours", ""))
            places_with_distance.append(place_copy)
    
    # Sort by distance (closest first)
    places_with_distance.sort(key=lambda x: x.get("distance", float('inf')))
    
    # Apply limit if specified
    if limit:
        places_with_distance = places_with_distance[:limit]
    
    return places_with_distance


def format_place_as_option(place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a place dictionary to match the Option model structure.
    
    Args:
        place: Place dictionary from data
    
    Returns:
        Formatted option dictionary
    """
    return {
        "name": place.get("name", "Unknown"),
        "category": place.get("category", "Food"),
        "location": place.get("location", {}),
        "distance": place.get("distance"),
        "address": place.get("address", ""),
        "hours": place.get("hours", {}),
        "image_url": None,  # Can be added later
    }


def get_options_for_round(
    category: str,
    location: Dict[str, float],
    radius: float,
    count: int = 10
) -> List[Dict[str, Any]]:
    """
    Get formatted options for a voting round.
    
    Args:
        category: Activity category
        location: Lobby location
        radius: Search radius in miles
        count: Number of options to return
    
    Returns:
        List of formatted option dictionaries
    """
    places = get_places_by_category_and_location(category, location, radius, limit=count * 2)
    
    # Format as options
    options = [format_place_as_option(place) for place in places[:count]]
    
    return options

