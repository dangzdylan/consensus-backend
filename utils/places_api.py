"""
Places API service module.
Handles fetching restaurants, activities, and other places from external APIs.
Supports Yelp Fusion API and Google Places API.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# API Configuration
YELP_API_KEY = os.getenv("YELP_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PREFERRED_API = os.getenv("PREFERRED_PLACES_API", "yelp")  # "yelp" or "google"

# API Endpoints
YELP_BASE_URL = "https://api.yelp.com/v3"
GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"


def miles_to_meters(miles: float) -> int:
    """Convert miles to meters for API calls."""
    return int(miles * 1609.34)


def fetch_restaurants_yelp(
    latitude: float,
    longitude: float,
    radius_miles: float,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch restaurants from Yelp Fusion API.
    
    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_miles: Search radius in miles
        limit: Maximum number of results (default 50)
        
    Returns:
        List of restaurant dictionaries
    """
    if not YELP_API_KEY:
        raise ValueError("YELP_API_KEY not set in environment variables")
    
    url = f"{YELP_BASE_URL}/businesses/search"
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}"
    }
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": miles_to_meters(radius_miles),
        "categories": "restaurants,food",
        "limit": min(limit, 50),  # Yelp max is 50
        "sort_by": "rating"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        restaurants = []
        for business in data.get("businesses", []):
            restaurant = {
                "name": business.get("name"),
                "address": ", ".join(business.get("location", {}).get("display_address", [])),
                "location": {
                    "latitude": business.get("coordinates", {}).get("latitude"),
                    "longitude": business.get("coordinates", {}).get("longitude")
                },
                "cuisine_type": ", ".join([cat.get("title", "") for cat in business.get("categories", [])]),
                "rating": business.get("rating"),
                "price_range": business.get("price", ""),
                "phone": business.get("display_phone"),
                "image_url": business.get("image_url"),
                "yelp_id": business.get("id"),
                "hours": business.get("hours", [{}])[0] if business.get("hours") else None
            }
            restaurants.append(restaurant)
        
        return restaurants
    except requests.exceptions.RequestException as e:
        raise Exception(f"Yelp API error: {str(e)}")


def fetch_restaurants_google(
    latitude: float,
    longitude: float,
    radius_miles: float,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch restaurants from Google Places API.
    
    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_miles: Search radius in miles
        limit: Maximum number of results (default 50)
        
    Returns:
        List of restaurant dictionaries
    """
    if not GOOGLE_PLACES_API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY not set in environment variables")
    
    # First, do a nearby search
    url = f"{GOOGLE_PLACES_BASE_URL}/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": miles_to_meters(radius_miles),
        "type": "restaurant",
        "key": GOOGLE_PLACES_API_KEY
    }
    
    restaurants = []
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Process results (Google returns up to 60 results across multiple pages)
        for place in data.get("results", [])[:limit]:
            # Get place details for more information
            place_id = place.get("place_id")
            details = _get_google_place_details(place_id) if place_id else {}
            
            restaurant = {
                "name": place.get("name"),
                "address": details.get("formatted_address") or place.get("vicinity", ""),
                "location": {
                    "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                    "longitude": place.get("geometry", {}).get("location", {}).get("lng")
                },
                "cuisine_type": ", ".join([t.replace("_", " ").title() for t in place.get("types", []) if t not in ["point_of_interest", "establishment"]]),
                "rating": place.get("rating"),
                "price_range": "$" * place.get("price_level", 0) if place.get("price_level") else None,
                "phone": details.get("formatted_phone_number"),
                "image_url": details.get("photos", [{}])[0].get("photo_reference") if details.get("photos") else None,
                "google_place_id": place_id,
                "hours": details.get("opening_hours", {})
            }
            restaurants.append(restaurant)
        
        return restaurants
    except requests.exceptions.RequestException as e:
        raise Exception(f"Google Places API error: {str(e)}")


def _get_google_place_details(place_id: str) -> Dict[str, Any]:
    """Get detailed information for a Google Place."""
    if not GOOGLE_PLACES_API_KEY:
        return {}
    
    url = f"{GOOGLE_PLACES_BASE_URL}/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_address,formatted_phone_number,opening_hours,photos,price_level",
        "key": GOOGLE_PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("result", {})
    except requests.exceptions.RequestException:
        return {}


def fetch_activities_yelp(
    latitude: float,
    longitude: float,
    radius_miles: float,
    categories: Optional[List[str]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch activities from Yelp Fusion API.
    
    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_miles: Search radius in miles
        categories: List of activity categories (e.g., ["parks", "museums", "arts"])
        limit: Maximum number of results (default 50)
        
    Returns:
        List of activity dictionaries
    """
    if not YELP_API_KEY:
        raise ValueError("YELP_API_KEY not set in environment variables")
    
    # Default categories for activities
    if not categories:
        categories = [
            "parks", "museums", "arts", "amusementparks", "zoos",
            "sports_clubs", "gyms", "theater", "musicvenues", "arcades",
            "shoppingcenters", "tours", "landmarks", "beaches"
        ]
    
    url = f"{YELP_BASE_URL}/businesses/search"
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}"
    }
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": miles_to_meters(radius_miles),
        "categories": ",".join(categories),
        "limit": min(limit, 50),
        "sort_by": "rating"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        activities = []
        for business in data.get("businesses", []):
            # Determine category from Yelp categories
            business_categories = [cat.get("alias", "") for cat in business.get("categories", [])]
            category = _map_yelp_category_to_activity_category(business_categories)
            
            activity = {
                "name": business.get("name"),
                "category": category,
                "address": ", ".join(business.get("location", {}).get("display_address", [])),
                "location": {
                    "latitude": business.get("coordinates", {}).get("latitude"),
                    "longitude": business.get("coordinates", {}).get("longitude")
                },
                "rating": business.get("rating"),
                "price_range": business.get("price", ""),
                "phone": business.get("display_phone"),
                "image_url": business.get("image_url"),
                "yelp_id": business.get("id"),
                "hours": business.get("hours", [{}])[0] if business.get("hours") else None
            }
            activities.append(activity)
        
        return activities
    except requests.exceptions.RequestException as e:
        raise Exception(f"Yelp API error: {str(e)}")


def fetch_activities_google(
    latitude: float,
    longitude: float,
    radius_miles: float,
    categories: Optional[List[str]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch activities from Google Places API.
    
    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_miles: Search radius in miles
        categories: List of activity types (e.g., ["park", "museum", "amusement_park"])
        limit: Maximum number of results (default 50)
        
    Returns:
        List of activity dictionaries
    """
    if not GOOGLE_PLACES_API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY not set in environment variables")
    
    # Default types for activities
    if not categories:
        categories = [
            "park", "museum", "amusement_park", "zoo", "aquarium",
            "stadium", "gym", "bowling_alley", "movie_theater", "night_club",
            "shopping_mall", "tourist_attraction", "beach"
        ]
    
    all_activities = []
    
    # Google Places requires one type per request, so we'll make multiple requests
    for category in categories[:5]:  # Limit to avoid too many API calls
        url = f"{GOOGLE_PLACES_BASE_URL}/nearbysearch/json"
        params = {
            "location": f"{latitude},{longitude}",
            "radius": miles_to_meters(radius_miles),
            "type": category,
            "key": GOOGLE_PLACES_API_KEY
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for place in data.get("results", []):
                place_id = place.get("place_id")
                details = _get_google_place_details(place_id) if place_id else {}
                
                activity = {
                    "name": place.get("name"),
                    "category": _map_google_type_to_activity_category(category),
                    "address": details.get("formatted_address") or place.get("vicinity", ""),
                    "location": {
                        "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                        "longitude": place.get("geometry", {}).get("location", {}).get("lng")
                    },
                    "rating": place.get("rating"),
                    "price_range": "$" * place.get("price_level", 0) if place.get("price_level") else None,
                    "phone": details.get("formatted_phone_number"),
                    "image_url": details.get("photos", [{}])[0].get("photo_reference") if details.get("photos") else None,
                    "google_place_id": place_id,
                    "hours": details.get("opening_hours", {})
                }
                all_activities.append(activity)
                
                if len(all_activities) >= limit:
                    break
            
            if len(all_activities) >= limit:
                break
        except requests.exceptions.RequestException as e:
            # Continue with other categories if one fails
            continue
    
    return all_activities[:limit]


def _map_yelp_category_to_activity_category(yelp_categories: List[str]) -> str:
    """Map Yelp categories to our activity categories."""
    category_mapping = {
        "parks": "parks",
        "museums": "museums",
        "arts": "art",
        "amusementparks": "games",
        "zoos": "sightseeing",
        "sports_clubs": "sports",
        "gyms": "sports",
        "theater": "art",
        "musicvenues": "concerts",
        "arcades": "games",
        "shoppingcenters": "shopping",
        "tours": "sightseeing",
        "landmarks": "sightseeing",
        "beaches": "sightseeing"
    }
    
    for yelp_cat in yelp_categories:
        for key, value in category_mapping.items():
            if key in yelp_cat.lower():
                return value
    
    return "sightseeing"  # Default category


def _map_google_type_to_activity_category(google_type: str) -> str:
    """Map Google Places types to our activity categories."""
    category_mapping = {
        "park": "parks",
        "museum": "museums",
        "amusement_park": "games",
        "zoo": "sightseeing",
        "aquarium": "sightseeing",
        "stadium": "sports",
        "gym": "sports",
        "bowling_alley": "games",
        "movie_theater": "art",
        "night_club": "concerts",
        "shopping_mall": "shopping",
        "tourist_attraction": "sightseeing",
        "beach": "sightseeing"
    }
    
    return category_mapping.get(google_type, "sightseeing")


def fetch_restaurants_mock(
    latitude: float,
    longitude: float,
    radius_miles: float,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Generate mock restaurant data for development/testing.
    Useful when API keys are not available.
    
    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_miles: Search radius in miles
        limit: Maximum number of results
        
    Returns:
        List of mock restaurant dictionaries
    """
    import random
    
    mock_restaurants = [
        {"name": "The Local Bistro", "cuisine_type": "American", "price_range": "$$"},
        {"name": "Sakura Sushi", "cuisine_type": "Japanese", "price_range": "$$$"},
        {"name": "Mama's Italian Kitchen", "cuisine_type": "Italian", "price_range": "$$"},
        {"name": "Taco Fiesta", "cuisine_type": "Mexican", "price_range": "$"},
        {"name": "Burger Palace", "cuisine_type": "American", "price_range": "$"},
        {"name": "Golden Dragon", "cuisine_type": "Chinese", "price_range": "$$"},
        {"name": "Le French Cafe", "cuisine_type": "French", "price_range": "$$$"},
        {"name": "Pizza Corner", "cuisine_type": "Italian", "price_range": "$"},
        {"name": "BBQ Smokehouse", "cuisine_type": "American", "price_range": "$$"},
        {"name": "Thai Garden", "cuisine_type": "Thai", "price_range": "$$"},
    ]
    
    restaurants = []
    for i, mock in enumerate(mock_restaurants[:min(limit, len(mock_restaurants))]):
        # Generate slightly offset coordinates within radius
        offset_lat = latitude + random.uniform(-0.01, 0.01) * (radius_miles / 5)
        offset_lng = longitude + random.uniform(-0.01, 0.01) * (radius_miles / 5)
        
        restaurant = {
            "name": mock["name"],
            "address": f"{random.randint(100, 9999)} Main St, City, State",
            "location": {
                "latitude": offset_lat,
                "longitude": offset_lng
            },
            "cuisine_type": mock["cuisine_type"],
            "rating": round(random.uniform(3.5, 5.0), 1),
            "price_range": mock["price_range"],
            "phone": f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "image_url": None,
            "yelp_id": None,
            "google_place_id": None,
            "hours": None
        }
        restaurants.append(restaurant)
    
    return restaurants


def fetch_restaurants(
    latitude: float,
    longitude: float,
    radius_miles: float,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch restaurants using the preferred API.
    Falls back to mock data if API keys are not configured.
    
    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_miles: Search radius in miles
        limit: Maximum number of results
        
    Returns:
        List of restaurant dictionaries (mock data if API keys not configured)
    """
    # Check if we should use mock data
    USE_MOCK = os.getenv("USE_MOCK_PLACES", "false").lower() == "true"
    
    if USE_MOCK:
        print("Using mock restaurant data (USE_MOCK_PLACES=true)")
        return fetch_restaurants_mock(latitude, longitude, radius_miles, limit)
    
    try:
        if PREFERRED_API.lower() == "google":
            if not GOOGLE_PLACES_API_KEY:
                print("Warning: GOOGLE_PLACES_API_KEY not set, using mock data")
                return fetch_restaurants_mock(latitude, longitude, radius_miles, limit)
            return fetch_restaurants_google(latitude, longitude, radius_miles, limit)
        else:
            if not YELP_API_KEY:
                print("Warning: YELP_API_KEY not set, using mock data")
                return fetch_restaurants_mock(latitude, longitude, radius_miles, limit)
            return fetch_restaurants_yelp(latitude, longitude, radius_miles, limit)
    except Exception as e:
        print(f"Warning: Failed to fetch restaurants: {str(e)}, using mock data")
        return fetch_restaurants_mock(latitude, longitude, radius_miles, limit)


def fetch_activities_mock(
    latitude: float,
    longitude: float,
    radius_miles: float,
    categories: Optional[List[str]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Generate mock activity data for development/testing.
    Useful when API keys are not available.
    
    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_miles: Search radius in miles
        categories: List of activity categories
        limit: Maximum number of results
        
    Returns:
        List of mock activity dictionaries
    """
    import random
    
    mock_activities = [
        {"name": "Central Park", "category": "parks"},
        {"name": "City Art Museum", "category": "museums"},
        {"name": "Riverside Trail", "category": "parks"},
        {"name": "Local Theater", "category": "art"},
        {"name": "Sports Complex", "category": "sports"},
        {"name": "Shopping District", "category": "shopping"},
        {"name": "Historic Landmark", "category": "sightseeing"},
        {"name": "Concert Hall", "category": "concerts"},
        {"name": "Adventure Park", "category": "games"},
        {"name": "Beach Boardwalk", "category": "sightseeing"},
    ]
    
    activities = []
    for i, mock in enumerate(mock_activities[:min(limit, len(mock_activities))]):
        # Generate slightly offset coordinates within radius
        offset_lat = latitude + random.uniform(-0.01, 0.01) * (radius_miles / 5)
        offset_lng = longitude + random.uniform(-0.01, 0.01) * (radius_miles / 5)
        
        activity = {
            "name": mock["name"],
            "category": mock["category"],
            "address": f"{random.randint(100, 9999)} Activity St, City, State",
            "location": {
                "latitude": offset_lat,
                "longitude": offset_lng
            },
            "rating": round(random.uniform(3.5, 5.0), 1),
            "price_range": random.choice(["Free", "$", "$$"]),
            "phone": f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "image_url": None,
            "yelp_id": None,
            "google_place_id": None,
            "hours": None
        }
        activities.append(activity)
    
    return activities


def fetch_activities(
    latitude: float,
    longitude: float,
    radius_miles: float,
    categories: Optional[List[str]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch activities using the preferred API.
    Falls back to mock data if API keys are not configured.
    
    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_miles: Search radius in miles
        categories: List of activity categories
        limit: Maximum number of results
        
    Returns:
        List of activity dictionaries (mock data if API keys not configured)
    """
    # Check if we should use mock data
    USE_MOCK = os.getenv("USE_MOCK_PLACES", "false").lower() == "true"
    
    if USE_MOCK:
        print("Using mock activity data (USE_MOCK_PLACES=true)")
        return fetch_activities_mock(latitude, longitude, radius_miles, categories, limit)
    
    try:
        if PREFERRED_API.lower() == "google":
            if not GOOGLE_PLACES_API_KEY:
                print("Warning: GOOGLE_PLACES_API_KEY not set, using mock data")
                return fetch_activities_mock(latitude, longitude, radius_miles, categories, limit)
            return fetch_activities_google(latitude, longitude, radius_miles, categories, limit)
        else:
            if not YELP_API_KEY:
                print("Warning: YELP_API_KEY not set, using mock data")
                return fetch_activities_mock(latitude, longitude, radius_miles, categories, limit)
            return fetch_activities_yelp(latitude, longitude, radius_miles, categories, limit)
    except Exception as e:
        print(f"Warning: Failed to fetch activities: {str(e)}, using mock data")
        return fetch_activities_mock(latitude, longitude, radius_miles, categories, limit)

