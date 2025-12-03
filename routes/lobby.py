"""
Lobby routes module.
Handles lobby creation and joining endpoints.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from models.lobby import Lobby
from models.restaurant import Restaurant
from models.activity import Activity
from utils.validators import validate_location, validate_radius, validate_lobby_code
from utils.helpers import generate_uuid, format_error_response, format_success_response
from utils.places_api import fetch_restaurants, fetch_activities
from datetime import datetime

lobby_bp = Blueprint("lobby", __name__)


@lobby_bp.route("", methods=["POST"])
def create_lobby():
    """
    Create a new lobby.
    
    Expected JSON body:
    {
        "host_id": "user_id",
        "location": {"latitude": float, "longitude": float},
        "radius": float,
        "deck_type": "Where to Eat?" (optional)
    }
    
    Returns:
        JSON response with lobby data and join code
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(*format_error_response("Request body is required", 400))
        
        # Validate required fields
        host_id = data.get("host_id")
        location = data.get("location")
        radius = data.get("radius")
        deck_type = data.get("deck_type", "Where to Eat?")
        
        if not host_id:
            return jsonify(*format_error_response("host_id is required", 400))
        
        if not location:
            return jsonify(*format_error_response("location is required", 400))
        
        if radius is None:
            return jsonify(*format_error_response("radius is required", 400))
        
        # Validate location
        is_valid, error_msg = validate_location(location)
        if not is_valid:
            return jsonify(*format_error_response(error_msg, 400))
        
        # Validate radius
        is_valid, error_msg = validate_radius(radius)
        if not is_valid:
            return jsonify(*format_error_response(error_msg, 400))
        
        # Check if user exists
        user_response = supabase.table("users").select("*").eq("user_id", host_id).execute()
        if not user_response.data:
            return jsonify(*format_error_response("User not found", 404))
        
        # Check if user is already in a lobby
        user = user_response.data[0]
        if user.get("current_lobby_id"):
            return jsonify(*format_error_response("User is already in a lobby", 400))
        
        # Generate unique lobby ID and code
        lobby_id = generate_uuid()
        
        # Ensure code is unique
        max_attempts = 10
        code = None
        for _ in range(max_attempts):
            temp_lobby = Lobby(lobby_id=lobby_id, host_id=host_id, location=location, radius=radius, deck_type=deck_type)
            code = temp_lobby.code
            
            # Check if code already exists
            existing = supabase.table("lobbies").select("code").eq("code", code).execute()
            if not existing.data:
                break
        else:
            return jsonify(*format_error_response("Failed to generate unique lobby code", 500))
        
        # Create lobby object
        lobby = Lobby(
            lobby_id=lobby_id,
            host_id=host_id,
            location=location,
            radius=radius,
            deck_type=deck_type,
            code=code
        )
        
        # Insert lobby into database
        lobby_data = lobby.to_dict()
        lobby_response = supabase.table("lobbies").insert(lobby_data).execute()
        
        if not lobby_response.data:
            return jsonify(*format_error_response("Failed to create lobby", 500))
        
        # Fetch and store places dynamically based on deck_type
        places_count = 0
        try:
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            
            if deck_type == "Where to Eat?" or "eat" in deck_type.lower():
                # Fetch restaurants
                restaurants_data = fetch_restaurants(
                    latitude=latitude,
                    longitude=longitude,
                    radius_miles=radius,
                    limit=50
                )
                
                # Store restaurants in database
                for rest_data in restaurants_data:
                    restaurant_id = generate_uuid()
                    restaurant = Restaurant(
                        restaurant_id=restaurant_id,
                        name=rest_data.get("name", "Unknown"),
                        address=rest_data.get("address", ""),
                        location=rest_data.get("location", {}),
                        lobby_id=lobby_id,
                        cuisine_type=rest_data.get("cuisine_type"),
                        rating=rest_data.get("rating"),
                        price_range=rest_data.get("price_range"),
                        phone=rest_data.get("phone"),
                        image_url=rest_data.get("image_url"),
                        yelp_id=rest_data.get("yelp_id"),
                        google_place_id=rest_data.get("google_place_id"),
                        hours=rest_data.get("hours")
                    )
                    
                    restaurant_data = restaurant.to_dict()
                    supabase.table("restaurants").insert(restaurant_data).execute()
                    places_count += 1
            else:
                # Fetch activities
                activities_data = fetch_activities(
                    latitude=latitude,
                    longitude=longitude,
                    radius_miles=radius,
                    limit=50
                )
                
                # Store activities in database
                for act_data in activities_data:
                    activity_id = generate_uuid()
                    activity = Activity(
                        activity_id=activity_id,
                        name=act_data.get("name", "Unknown"),
                        category=act_data.get("category", "sightseeing"),
                        address=act_data.get("address", ""),
                        location=act_data.get("location", {}),
                        lobby_id=lobby_id,
                        rating=act_data.get("rating"),
                        price_range=act_data.get("price_range"),
                        phone=act_data.get("phone"),
                        image_url=act_data.get("image_url"),
                        hours=act_data.get("hours"),
                        yelp_id=act_data.get("yelp_id"),
                        google_place_id=act_data.get("google_place_id")
                    )
                    
                    activity_data = activity.to_dict()
                    supabase.table("activities").insert(activity_data).execute()
                    places_count += 1
        except Exception as e:
            # Log error but don't fail lobby creation if API fails
            # The lobby can still be created, places can be fetched later
            print(f"Warning: Failed to fetch places: {str(e)}")
        
        # Update user's current_lobby_id
        supabase.table("users").update({
            "current_lobby_id": lobby_id,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", host_id).execute()
        
        return jsonify(*format_success_response(
            {
                "lobby_id": lobby_id,
                "code": code,
                "location": location,
                "radius": radius,
                "deck_type": deck_type,
                "user_ids": [host_id],
                "places_fetched": places_count
            },
            "Lobby created successfully",
            201
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@lobby_bp.route("/join", methods=["POST"])
def join_lobby():
    """
    Join a lobby using a join code.
    
    Expected JSON body:
    {
        "code": "ABCD",
        "user_id": "user_id"
    }
    
    Returns:
        JSON response with lobby data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(*format_error_response("Request body is required", 400))
        
        code = data.get("code")
        user_id = data.get("user_id")
        
        if not code:
            return jsonify(*format_error_response("code is required", 400))
        
        if not user_id:
            return jsonify(*format_error_response("user_id is required", 400))
        
        # Validate code format
        if not validate_lobby_code(code):
            return jsonify(*format_error_response("Invalid lobby code format", 400))
        
        # Normalize code to uppercase
        code = code.upper()
        
        # Find lobby by code
        lobby_response = supabase.table("lobbies").select("*").eq("code", code).execute()
        
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        lobby_data = lobby_response.data[0]
        
        # Check if lobby is active
        if lobby_data.get("status") != "active":
            return jsonify(*format_error_response("Lobby is not active", 400))
        
        # Check if user exists
        user_response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not user_response.data:
            return jsonify(*format_error_response("User not found", 404))
        
        user = user_response.data[0]
        
        # Check if user is already in this lobby
        if user_id in lobby_data.get("user_ids", []):
            return jsonify(*format_error_response("User is already in this lobby", 400))
        
        # Check if user is in another lobby
        if user.get("current_lobby_id") and user.get("current_lobby_id") != lobby_data.get("lobby_id"):
            return jsonify(*format_error_response("User is already in another lobby", 400))
        
        # Add user to lobby
        user_ids = lobby_data.get("user_ids", [])
        if user_id not in user_ids:
            user_ids.append(user_id)
            
            # Update lobby
            supabase.table("lobbies").update({
                "user_ids": user_ids,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("lobby_id", lobby_data.get("lobby_id")).execute()
        
        # Update user's current_lobby_id
        supabase.table("users").update({
            "current_lobby_id": lobby_data.get("lobby_id"),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", user_id).execute()
        
        # Fetch updated lobby data
        updated_lobby = supabase.table("lobbies").select("*").eq("lobby_id", lobby_data.get("lobby_id")).execute()
        
        return jsonify(*format_success_response(
            updated_lobby.data[0] if updated_lobby.data else lobby_data,
            "Successfully joined lobby",
            200
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@lobby_bp.route("/<lobby_id>", methods=["GET"])
def get_lobby(lobby_id):
    """
    Get lobby details by ID.
    
    Args:
        lobby_id: Lobby ID
        
    Returns:
        JSON response with lobby data
    """
    try:
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", lobby_id).execute()
        
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        return jsonify(*format_success_response(lobby_response.data[0], "Lobby retrieved successfully"))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@lobby_bp.route("/user/<user_id>/current", methods=["GET"])
def get_user_current_lobby(user_id):
    """
    Get the current lobby for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with lobby data or null if user is not in a lobby
    """
    try:
        # Get user's current lobby ID
        user_response = supabase.table("users").select("current_lobby_id").eq("user_id", user_id).execute()
        
        if not user_response.data:
            return jsonify(*format_error_response("User not found", 404))
        
        current_lobby_id = user_response.data[0].get("current_lobby_id")
        
        if not current_lobby_id:
            return jsonify(*format_success_response(None, "User is not in any lobby"))
        
        # Get lobby details
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", current_lobby_id).execute()
        
        if not lobby_response.data:
            return jsonify(*format_success_response(None, "Lobby not found"))
        
        return jsonify(*format_success_response(lobby_response.data[0], "Current lobby retrieved successfully"))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@lobby_bp.route("/<lobby_id>/refresh-places", methods=["POST"])
def refresh_lobby_places(lobby_id):
    """
    Refresh places (restaurants/activities) for a lobby.
    Useful if places weren't fetched initially or need to be updated.
    
    Args:
        lobby_id: Lobby ID
        
    Returns:
        JSON response with number of places fetched
    """
    try:
        # Get lobby details
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", lobby_id).execute()
        
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        lobby_data = lobby_response.data[0]
        location = lobby_data.get("location")
        radius = lobby_data.get("radius")
        deck_type = lobby_data.get("deck_type", "Where to Eat?")
        
        if not location or not radius:
            return jsonify(*format_error_response("Lobby missing location or radius", 400))
        
        latitude = location.get("latitude")
        longitude = location.get("longitude")
        
        places_count = 0
        
        # Delete existing places for this lobby
        if deck_type == "Where to Eat?" or "eat" in deck_type.lower():
            supabase.table("restaurants").delete().eq("lobby_id", lobby_id).execute()
        else:
            supabase.table("activities").delete().eq("lobby_id", lobby_id).execute()
        
        # Fetch and store new places
        try:
            if deck_type == "Where to Eat?" or "eat" in deck_type.lower():
                # Fetch restaurants
                restaurants_data = fetch_restaurants(
                    latitude=latitude,
                    longitude=longitude,
                    radius_miles=radius,
                    limit=50
                )
                
                # Store restaurants in database
                for rest_data in restaurants_data:
                    restaurant_id = generate_uuid()
                    restaurant = Restaurant(
                        restaurant_id=restaurant_id,
                        name=rest_data.get("name", "Unknown"),
                        address=rest_data.get("address", ""),
                        location=rest_data.get("location", {}),
                        lobby_id=lobby_id,
                        cuisine_type=rest_data.get("cuisine_type"),
                        rating=rest_data.get("rating"),
                        price_range=rest_data.get("price_range"),
                        phone=rest_data.get("phone"),
                        image_url=rest_data.get("image_url"),
                        yelp_id=rest_data.get("yelp_id"),
                        google_place_id=rest_data.get("google_place_id"),
                        hours=rest_data.get("hours")
                    )
                    
                    restaurant_data = restaurant.to_dict()
                    supabase.table("restaurants").insert(restaurant_data).execute()
                    places_count += 1
            else:
                # Fetch activities
                activities_data = fetch_activities(
                    latitude=latitude,
                    longitude=longitude,
                    radius_miles=radius,
                    limit=50
                )
                
                # Store activities in database
                for act_data in activities_data:
                    activity_id = generate_uuid()
                    activity = Activity(
                        activity_id=activity_id,
                        name=act_data.get("name", "Unknown"),
                        category=act_data.get("category", "sightseeing"),
                        address=act_data.get("address", ""),
                        location=act_data.get("location", {}),
                        lobby_id=lobby_id,
                        rating=act_data.get("rating"),
                        price_range=act_data.get("price_range"),
                        phone=act_data.get("phone"),
                        image_url=act_data.get("image_url"),
                        hours=act_data.get("hours"),
                        yelp_id=act_data.get("yelp_id"),
                        google_place_id=act_data.get("google_place_id")
                    )
                    
                    activity_data = activity.to_dict()
                    supabase.table("activities").insert(activity_data).execute()
                    places_count += 1
        except Exception as e:
            return jsonify(*format_error_response(f"Failed to fetch places: {str(e)}", 500))
        
        return jsonify(*format_success_response(
            {"places_fetched": places_count},
            f"Successfully refreshed {places_count} places",
            200
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@lobby_bp.route("/<lobby_id>/places", methods=["GET"])
def get_lobby_places(lobby_id):
    """
    Get all places (restaurants or activities) for a lobby.
    
    Args:
        lobby_id: Lobby ID
        
    Returns:
        JSON response with list of places
    """
    try:
        # Get lobby details to determine deck type
        lobby_response = supabase.table("lobbies").select("deck_type").eq("lobby_id", lobby_id).execute()
        
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        deck_type = lobby_response.data[0].get("deck_type", "Where to Eat?")
        
        places = []
        
        if deck_type == "Where to Eat?" or "eat" in deck_type.lower():
            # Get restaurants
            restaurants_response = supabase.table("restaurants").select("*").eq("lobby_id", lobby_id).execute()
            if restaurants_response.data:
                places = restaurants_response.data
        else:
            # Get activities
            activities_response = supabase.table("activities").select("*").eq("lobby_id", lobby_id).execute()
            if activities_response.data:
                places = activities_response.data
        
        return jsonify(*format_success_response(
            {
                "places": places,
                "count": len(places),
                "deck_type": deck_type
            },
            f"Retrieved {len(places)} places"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))

