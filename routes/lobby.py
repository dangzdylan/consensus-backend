"""
Lobby routes module.
Handles lobby creation and joining endpoints.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from models.lobby import Lobby
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
        "date": "MM/DD/YYYY",
        "start_hour": int (0-23),
        "end_hour": int (0-23),
        "activity_counts": {
            "Food": int,
            "Recreation & Entertainment": int,
            "Nature": int,
            "Arts": int,
            "Social": int
        },
        "max_members": int (optional, default 25)
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
        date = data.get("date")
        start_hour = data.get("start_hour")
        end_hour = data.get("end_hour")
        activity_counts = data.get("activity_counts", {})
        max_members = data.get("max_members", 25)
        
        if not host_id:
            return jsonify(*format_error_response("host_id is required", 400))
        
        if not location:
            return jsonify(*format_error_response("location is required", 400))
        
        if radius is None:
            return jsonify(*format_error_response("radius is required", 400))
        
        if not date:
            return jsonify(*format_error_response("date is required", 400))
        
        if start_hour is None:
            return jsonify(*format_error_response("start_hour is required", 400))
        
        if end_hour is None:
            return jsonify(*format_error_response("end_hour is required", 400))
        
        if not activity_counts or not isinstance(activity_counts, dict):
            return jsonify(*format_error_response("activity_counts is required and must be a dictionary", 400))
        
        # Validate location
        is_valid, error_msg = validate_location(location)
        if not is_valid:
            return jsonify(*format_error_response(error_msg, 400))
        
        # Validate radius
        is_valid, error_msg = validate_radius(radius)
        if not is_valid:
            return jsonify(*format_error_response(error_msg, 400))
        
        # Validate date format (MM/DD/YYYY)
        import re
        date_pattern = r'^(0[1-9]|1[0-2])\/(0[1-9]|[12][0-9]|3[01])\/\d{4}$'
        if not re.match(date_pattern, date):
            return jsonify(*format_error_response("date must be in MM/DD/YYYY format", 400))
        
        # Validate hours
        if not isinstance(start_hour, int) or not (0 <= start_hour <= 23):
            return jsonify(*format_error_response("start_hour must be an integer between 0 and 23", 400))
        
        if not isinstance(end_hour, int) or not (0 <= end_hour <= 23):
            return jsonify(*format_error_response("end_hour must be an integer between 0 and 23", 400))
        
        if start_hour >= end_hour:
            return jsonify(*format_error_response("end_hour must be after start_hour", 400))
        
        # Validate activity_counts
        total_activities = sum(activity_counts.values())
        if total_activities == 0:
            return jsonify(*format_error_response("At least one activity must be selected", 400))
        
        if total_activities > 10:
            return jsonify(*format_error_response("Maximum 10 activities allowed", 400))
        
        # Validate max_members
        if not isinstance(max_members, int) or max_members < 2 or max_members > 25:
            return jsonify(*format_error_response("max_members must be between 2 and 25", 400))
        
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
        
        # Ensure code is unique (4-6 characters)
        max_attempts = 10
        code = None
        for _ in range(max_attempts):
            temp_lobby = Lobby(
                lobby_id=lobby_id,
                host_id=host_id,
                location=location,
                radius=radius,
                date=date,
                start_hour=start_hour,
                end_hour=end_hour,
                activity_counts=activity_counts
            )
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
            date=date,
            start_hour=start_hour,
            end_hour=end_hour,
            activity_counts=activity_counts,
            max_members=max_members,
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
                "date": date,
                "start_hour": start_hour,
                "end_hour": end_hour,
                "activity_counts": activity_counts,
                "max_members": max_members,
                "user_ids": [host_id],
                "status": "waiting"
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
        
        # Check if lobby is joinable (waiting or voting status)
        lobby_status = lobby_data.get("status", "waiting")
        if lobby_status not in ["waiting", "voting"]:
            return jsonify(*format_error_response("Lobby is not accepting new members", 400))
        
        # Check if lobby is full
        current_members = len(lobby_data.get("user_ids", []))
        max_members = lobby_data.get("max_members", 25)
        if current_members >= max_members:
            return jsonify(*format_error_response("Lobby is full", 400))
        
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


@lobby_bp.route("/<lobby_id>/status", methods=["GET"])
def get_lobby_status(lobby_id):
    """
    Get lobby status including members and ready status.
    
    Args:
        lobby_id: Lobby ID
        
    Returns:
        JSON response with lobby status, members, and ready status
    """
    try:
        # Get lobby
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        lobby = lobby_response.data[0]
        user_ids = lobby.get("user_ids", [])
        
        # Get user details for members
        members = []
        for user_id in user_ids:
            user_response = supabase.table("users").select("user_id, username, is_ready").eq("user_id", user_id).execute()
            if user_response.data:
                user_data = user_response.data[0]
                members.append({
                    "id": user_id,
                    "name": user_data.get("username", "Unknown"),
                    "isReady": user_data.get("is_ready", False),
                    "isOwner": user_id == lobby.get("host_id")
                })
        
        all_ready = len(members) > 0 and all(m.get("isReady", False) for m in members)
        
        return jsonify(*format_success_response(
            {
                "lobby_id": lobby_id,
                "code": lobby.get("code"),
                "status": lobby.get("status", "waiting"),
                "members": members,
                "all_ready": all_ready,
                "max_members": lobby.get("max_members", 25),
                "current_members": len(members)
            },
            "Lobby status retrieved successfully"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@lobby_bp.route("/<lobby_id>/member/<user_id>/ready", methods=["POST"])
def set_member_ready(lobby_id, user_id):
    """
    Set a member's ready status.
    
    Expected JSON body:
    {
        "ready": true  // true for ready, false for not ready
    }
    
    Returns:
        JSON response with updated ready status
    """
    try:
        data = request.get_json()
        ready = data.get("ready", True) if data else True
        
        # Check if user is in lobby
        lobby_response = supabase.table("lobbies").select("user_ids").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        if user_id not in lobby_response.data[0].get("user_ids", []):
            return jsonify(*format_error_response("User is not in this lobby", 403))
        
        # Update user's ready status
        supabase.table("users").update({
            "is_ready": ready,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", user_id).execute()
        
        return jsonify(*format_success_response(
            {"user_id": user_id, "is_ready": ready},
            "Ready status updated successfully"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))

