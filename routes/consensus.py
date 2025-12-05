"""
Consensus routes module.
Handles swipe/match cycle endpoints for the consensus process.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from models.vote import Vote
from models.round import Round
from models.option import Option
from services.places_service import get_options_for_round
from utils.helpers import generate_uuid, format_error_response, format_success_response
from datetime import datetime

consensus_bp = Blueprint("consensus", __name__)


@consensus_bp.route("/lobby/<lobby_id>/start", methods=["POST"])
def start_game(lobby_id):
    """
    Start the voting game for a lobby.
    Only the host can start the game.
    
    Args:
        lobby_id: Lobby ID
        
    Expected JSON body:
    {
        "user_id": "user_id"  # Must be the host
    }
    
    Returns:
        JSON response with game status
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id") if data else None
        
        if not user_id:
            return jsonify(*format_error_response("user_id is required", 400))
        
        # Get lobby
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        lobby = lobby_response.data[0]
        
        # Check if user is the host
        if lobby.get("host_id") != user_id:
            return jsonify(*format_error_response("Only the host can start the game", 403))
        
        # Check if lobby is in waiting status
        if lobby.get("status") != "waiting":
            return jsonify(*format_error_response("Game can only be started from waiting status", 400))
        
        # Check if all members are ready (in real app, track ready status)
        # For now, just check if there are members
        if len(lobby.get("user_ids", [])) < 1:
            return jsonify(*format_error_response("Lobby must have at least one member", 400))
        
        # Update lobby status to in_progress
        supabase.table("lobbies").update({
            "status": "in_progress",
            "current_round": 1,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("lobby_id", lobby_id).execute()
        
        # Create rounds based on activity_counts
        activity_counts = lobby.get("activity_counts", {})
        round_number = 1
        
        for category, count in activity_counts.items():
            if count > 0:
                for i in range(count):
                    round_id = generate_uuid()
                    round_data = Round(
                        round_id=round_id,
                        lobby_id=lobby_id,
                        round_number=round_number,
                        category=category,
                        status="active" if round_number == 1 else "pending"
                    ).to_dict()
                    
                    supabase.table("rounds").insert(round_data).execute()
                    round_number += 1
        
        return jsonify(*format_success_response(
            {"status": "in_progress", "current_round": 1},
            "Game started successfully"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@consensus_bp.route("/lobby/<lobby_id>/round/<int:round_number>/options", methods=["GET"])
def get_round_options(lobby_id, round_number):
    """
    Get options for a specific round.
    Automatically populates options if they don't exist yet.
    
    Args:
        lobby_id: Lobby ID
        round_number: Round number (1-indexed)
        
    Returns:
        JSON response with list of options
    """
    try:
        # Get round info
        round_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        
        if not round_response.data:
            return jsonify(*format_error_response("Round not found", 404))
        
        round_data = round_response.data[0]
        
        # Get options for this round
        options_response = supabase.table("options").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        
        options = options_response.data if options_response.data else []
        
        # If no options exist, automatically populate them
        if not options:
            # Get lobby to get location and radius
            lobby_response = supabase.table("lobbies").select("location, radius").eq("lobby_id", lobby_id).execute()
            if lobby_response.data:
                lobby = lobby_response.data[0]
                location = lobby.get("location", {})
                radius = lobby.get("radius", 2.5)
                category = round_data.get("category", "Food")
                
                # Get options from places service
                option_data_list = get_options_for_round(category, location, radius, count=10)
                
                # Insert options into database
                for opt_data in option_data_list:
                    option_id = generate_uuid()
                    option = Option(
                        option_id=option_id,
                        lobby_id=lobby_id,
                        round_number=round_number,
                        category=category,
                        name=opt_data.get("name", "Unknown"),
                        location=opt_data.get("location", {}),
                        distance=opt_data.get("distance"),
                        address=opt_data.get("address"),
                        hours=opt_data.get("hours"),
                        image_url=opt_data.get("image_url")
                    )
                    supabase.table("options").insert(option.to_dict()).execute()
                
                # Fetch the newly inserted options
                options_response = supabase.table("options").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
                options = options_response.data if options_response.data else []
        
        return jsonify(*format_success_response(
            {
                "round": round_data,
                "options": options,
                "count": len(options)
            },
            f"Retrieved {len(options)} options for round {round_number}"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@consensus_bp.route("/lobby/<lobby_id>/vote", methods=["POST"])
def submit_vote(lobby_id):
    """
    Submit a vote on an option.
    
    Expected JSON body:
    {
        "user_id": "user_id",
        "option_id": "option_id",
        "round_number": int,
        "vote": true  // true for yes, false for no
    }
    
    Returns:
        JSON response with vote confirmation
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(*format_error_response("Request body is required", 400))
        
        user_id = data.get("user_id")
        option_id = data.get("option_id")
        round_number = data.get("round_number")
        vote = data.get("vote")
        
        if not user_id:
            return jsonify(*format_error_response("user_id is required", 400))
        
        if not option_id:
            return jsonify(*format_error_response("option_id is required", 400))
        
        if round_number is None:
            return jsonify(*format_error_response("round_number is required", 400))
        
        if vote is None:
            return jsonify(*format_error_response("vote is required (true for yes, false for no)", 400))
        
        # Check if user is in the lobby
        lobby_response = supabase.table("lobbies").select("user_ids").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        if user_id not in lobby_response.data[0].get("user_ids", []):
            return jsonify(*format_error_response("User is not in this lobby", 403))
        
        # Check if option exists and belongs to this round
        option_response = supabase.table("options").select("*").eq("option_id", option_id).eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not option_response.data:
            return jsonify(*format_error_response("Option not found for this round", 404))
        
        # Check if user already voted on this option
        existing_vote = supabase.table("votes").select("*").eq("user_id", user_id).eq("option_id", option_id).eq("round_number", round_number).execute()
        
        vote_id = generate_uuid()
        
        if existing_vote.data:
            # Update existing vote
            supabase.table("votes").update({
                "vote": bool(vote),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("vote_id", existing_vote.data[0].get("vote_id")).execute()
        else:
            # Create new vote
            vote_data = Vote(
                vote_id=vote_id,
                user_id=user_id,
                option_id=option_id,
                lobby_id=lobby_id,
                round_number=round_number,
                vote=bool(vote)
            ).to_dict()
            
            supabase.table("votes").insert(vote_data).execute()
        
        return jsonify(*format_success_response(
            {"vote_id": vote_id, "vote": bool(vote)},
            "Vote submitted successfully"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@consensus_bp.route("/lobby/<lobby_id>/round/<int:round_number>/status", methods=["GET"])
def get_round_status(lobby_id, round_number):
    """
    Get the status of a voting round, including vote counts and consensus status.
    
    Args:
        lobby_id: Lobby ID
        round_number: Round number
        
    Returns:
        JSON response with round status, vote counts, and consensus info
    """
    try:
        # Get round
        round_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not round_response.data:
            return jsonify(*format_error_response("Round not found", 404))
        
        round_data = round_response.data[0]
        
        # Get lobby to get user count
        lobby_response = supabase.table("lobbies").select("user_ids").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        total_users = len(lobby_response.data[0].get("user_ids", []))
        
        # Get all votes for this round
        votes_response = supabase.table("votes").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        votes = votes_response.data if votes_response.data else []
        
        # Get options for this round
        options_response = supabase.table("options").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        options = options_response.data if options_response.data else []
        
        # Count votes per option (only yes votes count for consensus)
        option_vote_counts = {}
        user_votes = {}  # Track which users have voted
        
        for vote in votes:
            option_id = vote.get("option_id")
            user_id = vote.get("user_id")
            is_yes = vote.get("vote", False)
            
            user_votes[user_id] = True
            
            if is_yes:
                if option_id not in option_vote_counts:
                    option_vote_counts[option_id] = []
                option_vote_counts[option_id].append(user_id)
        
        # Check for consensus (all users voted yes on same option)
        consensus_option_id = None
        tied_options = []
        
        for option_id, voters in option_vote_counts.items():
            if len(voters) == total_users:
                if consensus_option_id is None:
                    consensus_option_id = option_id
                else:
                    # Multiple options with all yes votes = tie
                    tied_options = [consensus_option_id, option_id]
                    consensus_option_id = None
                    break
        
        # Check if all users have voted
        all_voted = len(user_votes) == total_users
        
        return jsonify(*format_success_response(
            {
                "round": round_data,
                "total_users": total_users,
                "users_voted": len(user_votes),
                "all_voted": all_voted,
                "option_vote_counts": {opt_id: len(voters) for opt_id, voters in option_vote_counts.items()},
                "consensus_reached": consensus_option_id is not None,
                "consensus_option_id": consensus_option_id,
                "is_tie": len(tied_options) > 0,
                "tied_options": tied_options
            },
            "Round status retrieved successfully"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@consensus_bp.route("/lobby/<lobby_id>/waiting", methods=["GET"])
def get_waiting_status(lobby_id):
    """
    Get waiting status - check which users have finished voting.
    
    Args:
        lobby_id: Lobby ID
        
    Returns:
        JSON response with waiting status and list of users still voting
    """
    try:
        # Get lobby
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify(*format_error_response("Lobby not found", 404))
        
        lobby = lobby_response.data[0]
        user_ids = lobby.get("user_ids", [])
        current_round = lobby.get("current_round", 1)
        
        # Get all rounds for this lobby
        rounds_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).order("round_number").execute()
        rounds = rounds_response.data if rounds_response.data else []
        
        # For each user, check if they've voted on all options in current round
        users_finished = []
        users_waiting = []
        
        # Get all options for current round
        options_response = supabase.table("options").select("option_id").eq("lobby_id", lobby_id).eq("round_number", current_round).execute()
        option_ids = [opt.get("option_id") for opt in (options_response.data if options_response.data else [])]
        
        # Get user details for username mapping
        users_data = {}
        if user_ids:
            users_response = supabase.table("users").select("user_id, username").in_("user_id", user_ids).execute()
            if users_response.data:
                users_data = {u.get("user_id"): u.get("username", "Unknown") for u in users_response.data}
        
        for user_id in user_ids:
            # Check if user voted on all options in current round
            votes_response = supabase.table("votes").select("option_id").eq("user_id", user_id).eq("lobby_id", lobby_id).eq("round_number", current_round).execute()
            voted_option_ids = [v.get("option_id") for v in (votes_response.data if votes_response.data else [])]
            
            # User is finished if they voted on all options (or if no options exist)
            if len(voted_option_ids) >= len(option_ids) or len(option_ids) == 0:
                users_finished.append(user_id)
            else:
                users_waiting.append(user_id)
        
        all_finished = len(users_waiting) == 0 and len(user_ids) > 0
        
        # Map user IDs to usernames for waiting users
        users_waiting_usernames = [users_data.get(uid, f"User {uid[:8]}") for uid in users_waiting]
        
        return jsonify(*format_success_response(
            {
                "current_round": current_round,
                "total_users": len(user_ids),
                "users_finished": users_finished,
                "users_waiting": users_waiting_usernames,  # Return usernames instead of IDs
                "all_finished": all_finished,
                "total_rounds": len(rounds)
            },
            "Waiting status retrieved successfully"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@consensus_bp.route("/lobby/<lobby_id>/round/<int:round_number>/options", methods=["POST"])
def add_round_options(lobby_id, round_number):
    """
    Add options to a round (for hardcoded data or API-fetched data).
    
    Expected JSON body:
    {
        "options": [
            {
                "name": "Option Name",
                "category": "Food",
                "location": {"latitude": float, "longitude": float},
                "distance": float,
                "image_url": "url",
                "hours": {"open": 11, "close": 22, "days": [0,1,2,3,4,5,6]},
                "address": "address string"
            }
        ]
    }
    
    Returns:
        JSON response with added options
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(*format_error_response("Request body is required", 400))
        
        options_data = data.get("options", [])
        
        if not options_data or not isinstance(options_data, list):
            return jsonify(*format_error_response("options must be a non-empty array", 400))
        
        # Verify round exists
        round_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not round_response.data:
            return jsonify(*format_error_response("Round not found", 404))
        
        round_data = round_response.data[0]
        
        # Add each option
        added_options = []
        for opt_data in options_data:
            option_id = generate_uuid()
            option = Option(
                option_id=option_id,
                lobby_id=lobby_id,
                round_number=round_number,
                category=opt_data.get("category", round_data.get("category", "Food")),
                name=opt_data.get("name", "Unknown"),
                location=opt_data.get("location", {}),
                distance=opt_data.get("distance"),
                image_url=opt_data.get("image_url"),
                hours=opt_data.get("hours"),
                address=opt_data.get("address")
            )
            
            option_dict = option.to_dict()
            supabase.table("options").insert(option_dict).execute()
            added_options.append(option_dict)
        
        return jsonify(*format_success_response(
            {
                "options": added_options,
                "count": len(added_options)
            },
            f"Added {len(added_options)} options to round {round_number}"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))


@consensus_bp.route("/lobby/<lobby_id>/round/<int:round_number>/complete", methods=["POST"])
def complete_round(lobby_id, round_number):
    """
    Mark a round as completed with a selected option.
    Only called when consensus is reached or tiebreaker resolved.
    
    Expected JSON body:
    {
        "selected_option_id": "option_id",
        "user_id": "user_id"  # Must be host or system
    }
    
    Returns:
        JSON response with completion status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(*format_error_response("Request body is required", 400))
        
        selected_option_id = data.get("selected_option_id")
        user_id = data.get("user_id")
        
        if not selected_option_id:
            return jsonify(*format_error_response("selected_option_id is required", 400))
        
        # Get round
        round_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not round_response.data:
            return jsonify(*format_error_response("Round not found", 404))
        
        round_data = round_response.data[0]
        
        # Verify option exists
        option_response = supabase.table("options").select("*").eq("option_id", selected_option_id).eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not option_response.data:
            return jsonify(*format_error_response("Option not found for this round", 404))
        
        # Update round status
        supabase.table("rounds").update({
            "status": "completed",
            "selected_option_id": selected_option_id,
            "completed_at": datetime.utcnow().isoformat()
        }).eq("round_id", round_data.get("round_id")).execute()
        
        # Check if all rounds are completed
        all_rounds = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).order("round_number").execute()
        rounds = all_rounds.data if all_rounds.data else []
        all_completed = all(r.get("status") == "completed" for r in rounds)
        
        if all_completed:
            # Update lobby status to completed
            supabase.table("lobbies").update({
                "status": "completed",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("lobby_id", lobby_id).execute()
        else:
            # Activate next round if it exists
            next_round_number = round_number + 1
            next_round = next((r for r in rounds if r.get("round_number") == next_round_number), None)
            if next_round and next_round.get("status") == "pending":
                supabase.table("rounds").update({
                    "status": "active"
                }).eq("round_id", next_round.get("round_id")).execute()
                
                # Update lobby current_round
                supabase.table("lobbies").update({
                    "current_round": next_round_number,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("lobby_id", lobby_id).execute()
        
        return jsonify(*format_success_response(
            {
                "round_number": round_number,
                "selected_option_id": selected_option_id,
                "all_rounds_completed": all_completed,
                "next_round": round_number + 1 if not all_completed else None
            },
            "Round completed successfully"
        ))
        
    except Exception as e:
        return jsonify(*format_error_response(f"Internal server error: {str(e)}", 500))

