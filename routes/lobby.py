"""
Lobby routes module.
Handles lobby creation, joining, and status updates.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from utils.helpers import generate_uuid, format_error_response, format_success_response, jsonify_error, jsonify_success
from utils.validators import validate_lobby_code
from datetime import datetime
import string
import random

lobby_bp = Blueprint("lobby", __name__)


def generate_lobby_code(length=6):
    """Generate a random alphanumeric lobby code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@lobby_bp.route("", methods=["POST"])
def create_lobby():
    """
    Create a new lobby.
    
    Expected JSON body:
    {
        "host_id": "string",
        "location": {"latitude": float, "longitude": float},
        "radius": float,
        "date": "string",
        "start_hour": int,
        "end_hour": int,
        "activity_counts": {"Food": 1, ...},
        "max_members": int
    }
    
    Returns:
        JSON response with lobby data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify_error("Request body is required", 400)
        
        required_fields = ["host_id", "location", "radius", "date", "start_hour", "end_hour", "activity_counts"]
        for field in required_fields:
            if field not in data:
                return jsonify_error(f"{field} is required", 400)
        
        # Destructure data
        host_id = data["host_id"]
        location = data["location"]
        radius = data["radius"]
        date_str = data["date"]
        start_hour = data["start_hour"]
        end_hour = data["end_hour"]
        activity_counts = data["activity_counts"]
        max_members = data.get("max_members", 25)
        
        # Validation checks
        if not isinstance(activity_counts, dict):
            return jsonify_error("activity_counts is required and must be a dictionary", 400)
        
        # ... Additional validations could go here ...
        
        # Generate unique code
        code = generate_lobby_code()
        # In production, check for collision
        
        lobby_id = generate_uuid()
        
        lobby_data = {
            "lobby_id": lobby_id,
            "code": code,
            "host_id": host_id,
            "location": location,
            "radius": radius,
            "date": date_str,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "activity_counts": activity_counts,
            "max_members": max_members,
            "status": "waiting",
            "current_round": 0,
            "user_ids": [host_id],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("lobbies").insert(lobby_data).execute()
        
        # Update user's current_lobby_id
        supabase.table("users").update({
            "current_lobby_id": lobby_id,
            "is_ready": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", host_id).execute()
        
        return jsonify_success(lobby_data, "Lobby created successfully")
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


@lobby_bp.route("/join", methods=["POST"])
def join_lobby():
    """
    Join an existing lobby using a code.
    
    Expected JSON body:
    {
        "code": "string",
        "user_id": "string"
    }
    
    Returns:
        JSON response with lobby data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify_error("Request body is required", 400)
        
        code = data.get("code")
        user_id = data.get("user_id")
        
        if not code:
            return jsonify_error("code is required", 400)
        
        if not user_id:
            return jsonify_error("user_id is required", 400)
        
        # Validate code format
        if not validate_lobby_code(code):
            return jsonify_error("Invalid lobby code format", 400)
        
        # Normalize code to uppercase
        code = code.upper()
        
        # Find lobby by code
        lobby_response = supabase.table("lobbies").select("*").eq("code", code).execute()
        
        if not lobby_response.data:
            return jsonify_error("Lobby not found", 404)
        
        lobby_data = lobby_response.data[0]
        
        # Check if lobby is joinable (only waiting status allows new members)
        lobby_status = lobby_data.get("status", "waiting")
        if lobby_status != "waiting":
            return jsonify_error("Lobby is not accepting new members", 400)
        
        # Check if lobby is full
        current_members = len(lobby_data.get("user_ids", []))
        max_members = lobby_data.get("max_members", 25)
        if current_members >= max_members:
            return jsonify_error("Lobby is full", 400)
        
        # Check if user exists
        user_response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not user_response.data:
            return jsonify_error("User not found", 404)
        
        user = user_response.data[0]
        
        # Check if user is already in this lobby
        if user_id in lobby_data.get("user_ids", []):
            return jsonify_error("User is already in this lobby", 400)
        
        # Check if user is in another lobby
        if user.get("current_lobby_id") and user.get("current_lobby_id") != lobby_data.get("lobby_id"):
            return jsonify_error("User is already in another lobby", 400)
        
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
        
        return jsonify_success(
            updated_lobby.data[0] if updated_lobby.data else lobby_data,
            "Successfully joined lobby",
            200
        )
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


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
            return jsonify_error("Lobby not found", 404)
        
        return jsonify_success(lobby_response.data[0], "Lobby retrieved successfully")
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


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
            return jsonify_error("User not found", 404)
        
        current_lobby_id = user_response.data[0].get("current_lobby_id")
        
        if not current_lobby_id:
            return jsonify_success(None, "User is not in any lobby")
        
        # Get lobby details
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", current_lobby_id).execute()
        
        if not lobby_response.data:
            return jsonify_success(None, "Lobby not found")
        
        return jsonify_success(lobby_response.data[0], "Current lobby retrieved successfully")
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


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
            return jsonify_error("Lobby not found", 404)
        
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
        
        return jsonify_success(
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
        )
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


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
            return jsonify_error("Lobby not found", 404)
        
        if user_id not in lobby_response.data[0].get("user_ids", []):
            return jsonify_error("User is not in this lobby", 403)
        
        # Update user's ready status
        supabase.table("users").update({
            "is_ready": ready,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", user_id).execute()
        
        return jsonify_success(
            {"user_id": user_id, "is_ready": ready},
            "Ready status updated successfully"
        )
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


@lobby_bp.route("/member/<user_id>/leave", methods=["POST"])
def leave_lobby(user_id):
    """
    Remove a user from their current lobby.
    
    Returns:
        JSON response with success message
    """
    try:
        # Get user's current lobby
        user_response = supabase.table("users").select("current_lobby_id").eq("user_id", user_id).execute()
        if not user_response.data:
            return jsonify_error("User not found", 404)
        
        current_lobby_id = user_response.data[0].get("current_lobby_id")
        
        if not current_lobby_id:
            return jsonify_success(None, "User is not in any lobby")
        
        # Get lobby details
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", current_lobby_id).execute()
        if not lobby_response.data:
            # Lobby doesn't exist but user thinks they are in it, clear user's state
            supabase.table("users").update({
                "current_lobby_id": None, 
                "is_ready": False,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).execute()
            return jsonify_success(None, "User state cleared (lobby not found)")
            
        lobby = lobby_response.data[0]
        user_ids = lobby.get("user_ids", [])
        
        # Remove user from lobby list
        if user_id in user_ids:
            user_ids.remove(user_id)
            supabase.table("lobbies").update({
                "user_ids": user_ids, 
                "updated_at": datetime.utcnow().isoformat()
            }).eq("lobby_id", current_lobby_id).execute()
            
        # Clear user's state
        supabase.table("users").update({
            "current_lobby_id": None,
            "is_ready": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", user_id).execute()
        
        return jsonify_success(None, "Successfully left lobby")
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)
