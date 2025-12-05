"""
Result routes module.
Handles final match retrieval endpoints and itinerary generation.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from utils.helpers import format_error_response, format_success_response

result_bp = Blueprint("result", __name__)


@result_bp.route("/lobby/<lobby_id>/itinerary", methods=["GET"])
def get_itinerary(lobby_id):
    """
    Get the final itinerary with selected activities for a lobby.
    
    Args:
        lobby_id: Lobby ID
        
    Returns:
        JSON response with itinerary (selected activities in order)
    """
    try:
        # Get lobby
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        lobby = lobby_response.data[0]
        
        # Get all completed rounds with selected options
        rounds_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("status", "completed").order("round_number").execute()
        rounds = rounds_response.data if rounds_response.data else []
        
        # Get selected options for each round
        itinerary = []
        for round_data in rounds:
            selected_option_id = round_data.get("selected_option_id")
            if selected_option_id:
                option_response = supabase.table("options").select("*").eq("option_id", selected_option_id).execute()
                if option_response.data:
                    option = option_response.data[0]
                    itinerary.append({
                        "id": option.get("option_id"),
                        "option_id": option.get("option_id"),  # Include both for compatibility
                        "name": option.get("name"),
                        "category": option.get("category"),
                        "time": option.get("time", "12:00 PM"),  # Would calculate based on schedule
                        "duration": 1,  # Default 1 hour per activity
                        "hours": option.get("hours"),
                        "location": option.get("location"),
                        "address": option.get("address"),
                        "image": option.get("image_url"),
                        "image_url": option.get("image_url"),  # Include both for compatibility
                        "round_number": round_data.get("round_number")
                    })
        
        return jsonify(*format_success_response(
            {
                "lobby_id": lobby_id,
                "date": lobby.get("date"),
                "start_hour": lobby.get("start_hour"),
                "end_hour": lobby.get("end_hour"),
                "activities": itinerary,
                "count": len(itinerary)
            },
            f"Retrieved itinerary with {len(itinerary)} activities"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))

