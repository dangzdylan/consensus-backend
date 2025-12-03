"""
Authentication routes module.
Handles user login and signup endpoints.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from utils.validators import validate_email, validate_username
from utils.helpers import generate_uuid, format_error_response, format_success_response
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Create a new user account.
    
    Expected JSON body:
    {
        "username": "string",
        "email": "string",
        "password": "string" (optional for now, auth handled by Supabase)
    }
    
    Returns:
        JSON response with user data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(*format_error_response("Request body is required", 400))
        
        username = data.get("username")
        email = data.get("email")
        
        if not username:
            return jsonify(*format_error_response("username is required", 400))
        
        if not email:
            return jsonify(*format_error_response("email is required", 400))
        
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify(*format_error_response(error_msg, 400))
        
        # Validate email
        if not validate_email(email):
            return jsonify(*format_error_response("Invalid email format", 400))
        
        # Check if username or email already exists
        username_check = supabase.table("users").select("*").eq("username", username).execute()
        email_check = supabase.table("users").select("*").eq("email", email).execute()
        if username_check.data or email_check.data:
            return jsonify(*format_error_response("Username or email already exists", 409))
        
        # Create user
        user_id = generate_uuid()
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "location": {},
            "current_lobby_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        user_response = supabase.table("users").insert(user_data).execute()
        
        if not user_response.data:
            return jsonify(*format_error_response("Failed to create user", 500))
        
        return jsonify(*format_success_response(
            user_response.data[0],
            "User created successfully",
            201
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user (placeholder - actual auth handled by Supabase Auth).
    
    Expected JSON body:
    {
        "email": "string",
        "password": "string"
    }
    
    Returns:
        JSON response with user data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(*format_error_response("Request body is required", 400))
        
        email = data.get("email")
        
        if not email:
            return jsonify(*format_error_response("email is required", 400))
        
        # Find user by email
        user_response = supabase.table("users").select("*").eq("email", email).execute()
        
        if not user_response.data:
            return jsonify(*format_error_response("User not found", 404))
        
        return jsonify(*format_success_response(
            user_response.data[0],
            "Login successful"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))

