"""
Lobby routes module.
Handles lobby creation and joining endpoints.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from models.lobby import Lobby
from models.user import User
from utils.validators import validate_location, validate_radius, validate_lobby_code
from utils.helpers import generate_uuid, format_error_response, format_success_response
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
                "user_ids": [host_id]
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

