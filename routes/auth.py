"""
Authentication routes module.
Handles user login and signup endpoints.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from utils.validators import validate_username
from utils.helpers import generate_uuid, jsonify_error, jsonify_success
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Create a new user account.
    
    Expected JSON body:
    {
        "username": "string"
    }
    
    Returns:
        JSON response with user data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify_error("Request body is required", 400)
        
        username = data.get("username")
        
        if not username:
            return jsonify_error("username is required", 400)
        
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify_error(error_msg, 400)
        
        # Check if username already exists
        try:
            username_check = supabase.table("users").select("*").eq("username", username).execute()
            if username_check.data:
                return jsonify_error("Username already exists", 409)
        except Exception as supabase_error:
            error_str = str(supabase_error)
            if "403" in error_str or "Forbidden" in error_str or "permission" in error_str.lower():
                return jsonify_error(
                    f"Database access denied: {error_str}. Please check your Supabase API key and ensure RLS is disabled or properly configured.",
                    403
                )
            pass
        
        # Create user
        user_id = generate_uuid()
        user_data = {
            "user_id": user_id,
            "username": username,
            "location": {},
            "current_lobby_id": None,
            "is_ready": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            user_response = supabase.table("users").insert(user_data).execute()
        except Exception as supabase_error:
            error_str = str(supabase_error)
            error_type = type(supabase_error).__name__
            error_msg = error_str
            
            if hasattr(supabase_error, 'message'):
                error_msg = supabase_error.message
            elif hasattr(supabase_error, 'args') and supabase_error.args:
                error_msg = str(supabase_error.args[0])
            
            status_code = 500
            if hasattr(supabase_error, 'code'):
                status_code = supabase_error.code
            elif hasattr(supabase_error, 'status_code'):
                status_code = supabase_error.status_code
            elif hasattr(supabase_error, 'status'):
                status_code = supabase_error.status
            
            if status_code == 403 or "403" in error_str or "Forbidden" in error_str or "permission" in error_str.lower():
                detailed_msg = f"Database access denied (Error Type: {error_type}). {error_msg}. Please check your Supabase API key and ensure RLS is disabled or properly configured."
                return jsonify_error(detailed_msg, 403)
            
            if "duplicate" in error_str.lower() or "unique" in error_str.lower() or "violates unique constraint" in error_str.lower():
                return jsonify_error("Username already exists", 409)
            
            return jsonify_error(
                f"Database error during user creation (Type: {error_type}): {error_msg}",
                status_code if status_code != 500 else 500
            )
        
        if not user_response.data:
            return jsonify_error("Failed to create user", 500)
        
        return jsonify_success(
            user_response.data[0],
            "User created successfully",
            201
        )
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error in signup: {error_type}: {error_msg}")
        print(traceback_str)
        
        return jsonify_error(
            f"Internal server error ({error_type}): {error_msg}",
            500
        )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user by username.
    
    Expected JSON body:
    {
        "username": "string"
    }
    
    Returns:
        JSON response with user data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify_error("Request body is required", 400)
        
        username = data.get("username")
        
        if not username:
            return jsonify_error("username is required", 400)
        
        # Find user by username
        try:
            user_response = supabase.table("users").select("*").eq("username", username).execute()
        except Exception as supabase_error:
            error_str = str(supabase_error)
            error_msg = error_str
            
            if hasattr(supabase_error, 'message'):
                error_msg = supabase_error.message
            elif hasattr(supabase_error, 'args') and supabase_error.args:
                error_msg = str(supabase_error.args[0])
            
            if "403" in error_str or "Forbidden" in error_str or "permission" in error_str.lower():
                return jsonify_error(
                    f"Database access denied: {error_msg}. Please check your Supabase API key and ensure RLS is disabled or properly configured.",
                    403
                )
            
            return jsonify_error(
                f"Database error during login: {error_msg}",
                500
            )
        
        if not user_response.data:
            return jsonify_error("User not found", 404)
        
        return jsonify_success(
            user_response.data[0],
            "Login successful"
        )
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error in login: {error_type}: {error_msg}")
        print(traceback_str)
        
        return jsonify_error(
            f"Internal server error ({error_type}): {error_msg}",
            500
        )
