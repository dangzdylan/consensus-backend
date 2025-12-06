"""
Consensus routes module.
Handles game state, voting, and consensus logic.
"""

from flask import Blueprint, request, jsonify
from supabase_client import supabase
from utils.helpers import generate_uuid, jsonify_error, jsonify_success
from models.option import Option
from datetime import datetime
import random

consensus_bp = Blueprint("consensus", __name__)


def generate_mock_options(lobby_id, round_number, category):
    """Generate mock options for a round."""
    options = []
    
    if category == "Food":
        names = ["Burger King", "Sushi Place", "Pizza Hut", "Taco Bell", "McDonalds", "Thai Spice", "Indian Curry House", "The Sandwich Spot", "Pasta Palace", "Steakhouse"]
        base_img = "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&q=80"
    else:
        names = ["Movie Theater", "Park Walk", "Bowling Alley", "Karaoke", "Escape Room", "Museum", "Arcade", "Zoo", "Beach Trip", "Concert"]
        base_img = "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=500&q=80"
        
    selected = random.sample(names, min(5, len(names)))
    
    for i, name in enumerate(selected):
        option_id = generate_uuid()
        opt = {
            "option_id": option_id,
            "lobby_id": lobby_id,
            "round_number": round_number,
            "category": category,
            "name": name,
            "location": {"latitude": 37.7749 + (random.random() - 0.5) * 0.01, "longitude": -122.4194 + (random.random() - 0.5) * 0.01},
            "distance": round(random.random() * 5, 1),
            "image_url": base_img,
            "hours": {"open": 9, "close": 22},
            "address": f"{random.randint(100, 999)} Main St",
            "created_at": datetime.utcnow().isoformat()
        }
        options.append(opt)
    
    return options


@consensus_bp.route("/lobby/<lobby_id>/start", methods=["POST"])
def start_game(lobby_id):
    """
    Start the game for a lobby.
    
    Expected JSON body:
    {
        "user_id": "host_user_id"
    }
    
    Returns:
        JSON response with updated lobby status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify_error("Request body is required", 400)
        
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify_error("user_id is required", 400)
        
        # Verify lobby and ownership
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify_error("Lobby not found", 404)
        
        lobby = lobby_response.data[0]
        if lobby.get("host_id") != user_id:
            return jsonify_error("Only the host can start the game", 403)
        
        # Initialize rounds if not present
        if not lobby.get("current_round"):
            # Get activity counts
            activity_counts = lobby.get("activity_counts", {})
            
            # Generate rounds
            rounds = []
            round_num = 1
            # Defined order
            valid_cats = ["Food", "Activity", "Arts", "Nature", "Social", "Recreation & Entertainment"]
            
            for cat in valid_cats:
                # Check for direct match or sloppy keys from frontend
                count = activity_counts.get(cat, 0)
                if count > 0:
                    for _ in range(count):
                        rounds.append({
                            "round_number": round_num, 
                            "category": cat, 
                            "status": "active" if round_num == 1 else "pending"
                        })
                        round_num += 1
            
            # Fallback
            if not rounds:
                rounds = [{"round_number": 1, "category": "Food", "status": "active"}]
            
            # Prepare batch data
            rounds_to_insert = []
            options_to_insert = []
            
            for r in rounds:
                round_id = generate_uuid()
                round_data = {
                    "round_id": round_id,
                    "lobby_id": lobby_id,
                    "round_number": r["round_number"],
                    "category": r["category"],
                    "status": r["status"],
                    "created_at": datetime.utcnow().isoformat()
                }
                rounds_to_insert.append(round_data)
                
                # Seed mock options
                mock_options = generate_mock_options(lobby_id, r["round_number"], r["category"])
                options_to_insert.extend(mock_options)
            
            # Execute batch inserts
            if rounds_to_insert:
                supabase.table("rounds").insert(rounds_to_insert).execute()
            
            if options_to_insert:
                supabase.table("options").insert(options_to_insert).execute()
            
            # Update lobby status
            supabase.table("lobbies").update({
                "status": "voting",
                "current_round": 1,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("lobby_id", lobby_id).execute()
        
        return jsonify_success(
            {"lobby_id": lobby_id, "status": "voting", "current_round": 1},
            "Game started successfully"
        )
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


@consensus_bp.route("/lobby/<lobby_id>/vote", methods=["POST"])
def submit_vote(lobby_id):
    """
    Submit a vote for an option.
    
    Expected JSON body:
    {
        "user_id": "string",
        "option_id": "string",
        "round_number": int,
        "vote": "like" | "dislike" | "superlike"
    }
    
    Returns:
        JSON response with vote confirmation
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify_error("Request body is required", 400)
        
        user_id = data.get("user_id")
        option_id = data.get("option_id")
        round_number = data.get("round_number")
        vote_type = data.get("vote")
        
        if not all([user_id, option_id, round_number, vote_type]):
            return jsonify_error("Missing required fields", 400)
        
        if vote_type not in ["like", "dislike", "superlike"]:
            return jsonify_error("Invalid vote type", 400)
        
        # Record vote
        vote_id = generate_uuid()
        vote_data = {
            "vote_id": vote_id,
            "lobby_id": lobby_id,
            "user_id": user_id,
            "option_id": option_id,
            "round_number": round_number,
            "vote": (vote_type in ["like", "superlike"]),
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            supabase.table("votes").insert(vote_data).execute()
        except Exception as vote_err:
             # Just in case unique constraint or something fails, though uuids are unique
             return jsonify_error(f"Failed to record vote: {str(vote_err)}", 500)
        
        return jsonify_success(vote_data, "Vote submitted successfully", 201)
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


@consensus_bp.route("/lobby/<lobby_id>/round/<int:round_number>/status", methods=["GET"])
def get_round_status(lobby_id, round_number):
    """
    Get status of a specific round, including consensus check.
    
    Args:
        lobby_id: Lobby ID
        round_number: Round number
        
    Returns:
        JSON response with round status and consensus result if any
    """
    try:
        # Get round
        round_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not round_response.data:
            return jsonify_error("Round not found", 404)
        
        round_data = round_response.data[0]
        
        # Check for consensus (simplified logic)
        # Get all votes for this round
        votes_response = supabase.table("votes").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        votes = votes_response.data if votes_response.data else []
        
        # Count votes per option
        option_scores = {}
        for vote in votes:
            opt_id = vote.get("option_id")
            v_type = vote.get("vote")
            score = 1 if v_type else -1
            option_scores[opt_id] = option_scores.get(opt_id, 0) + score
        
        # Determine if consensus reached (e.g., all members voted, or high score threshold)
        consensus_reached = False
        winning_option_id = None
        
        print(f"DEBUG: Votes count: {len(votes)}")
        print(f"DEBUG: Option scores: {option_scores}")

        if option_scores:
            best_option = max(option_scores.items(), key=lambda x: x[1])
            print(f"DEBUG: Best option: {best_option}")
            
            if best_option[1] > 0: # Threshold logic
                winning_option_id = best_option[0]
                consensus_reached = True
                print(f"DEBUG: Consensus reached! Winner: {winning_option_id}")
            else:
                print(f"DEBUG: Best score {best_option[1]} <= 0, no consensus")
        else:
             print("DEBUG: No option scores calculated")
        
        return jsonify_success(
            {
                "round_id": round_data.get("round_id"),
                "status": round_data.get("status"),
                "consensus_reached": consensus_reached,
                "winning_option_id": winning_option_id,
                "scores": option_scores
            },
            "Round status retrieved successfully"
        )
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


@consensus_bp.route("/lobby/<lobby_id>/waiting", methods=["GET"])
def get_waiting_status(lobby_id):
    """
    Get waiting status to see who has finished voting for the current round.
    
    Args:
        lobby_id: Lobby ID
        
    Returns:
        JSON response with list of finished users
    """
    try:
        # Get lobby to know current round and members
        lobby_response = supabase.table("lobbies").select("*").eq("lobby_id", lobby_id).execute()
        if not lobby_response.data:
            return jsonify_error("Lobby not found", 404)
        
        lobby = lobby_response.data[0]
        current_round = lobby.get("current_round")
        user_ids = lobby.get("user_ids", [])
        
        if not current_round:
             return jsonify_success(
                {"status": "waiting_to_start", "users_finished": []},
                "Lobby has not started"
            )

        # Get all available options for this round to know how many to vote on
        rounds_response = supabase.table("rounds").select("round_id").eq("lobby_id", lobby_id).eq("round_number", current_round).execute()
        
        # Check rounds exist
        rounds = rounds_response.data if rounds_response.data else []
        if not rounds:
             return jsonify_success(
                {"status": "no_round", "users_finished": []},
                "Round not found"
            )
            
        # Inspect options count
        options_response = supabase.table("options").select("option_id").eq("lobby_id", lobby_id).eq("round_number", current_round).execute()
        option_ids = [o.get("option_id") for o in (options_response.data if options_response.data else [])]
        
        users_finished = []
        users_waiting = []
        
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
        
        return jsonify_success(
            {
                "current_round": current_round,
                "total_users": len(user_ids),
                "users_finished": users_finished,
                "users_waiting": users_waiting_usernames,  # Return usernames instead of IDs
                "all_finished": all_finished,
                "total_rounds": len(rounds)
            },
            "Waiting status retrieved successfully"
        )
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


@consensus_bp.route("/lobby/<lobby_id>/round/<int:round_number>/options", methods=["GET"])
def get_round_options(lobby_id, round_number):
    """
    Get options for a specific round, including round metadata.
    
    Args:
        lobby_id: Lobby ID
        round_number: Round number
        
    Returns:
        JSON response with round details and list of options
    """
    try:
        # Get round details first
        round_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        
        round_info = {}
        if round_response.data:
            round_info = round_response.data[0]
        else:
            # If round doesn't exist (edge case), try to infer or return minimal info
            round_info = {"category": "Unknown", "round_number": round_number}

        options_response = supabase.table("options").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        
        fetched_options = []
        if options_response.data:
            fetched_options = [Option.from_dict(opt).to_dict() for opt in options_response.data]

        response_data = {
            "round": round_info,
            "options": fetched_options
        }
        
        return jsonify_success(response_data, f"Retrieved {len(fetched_options)} options for round {round_number}")
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


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
            return jsonify_error("Request body is required", 400)
        
        options_data = data.get("options", [])
        
        if not options_data or not isinstance(options_data, list):
            return jsonify_error("options must be a non-empty array", 400)
        
        # Verify round exists
        round_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not round_response.data:
            return jsonify_error("Round not found", 404)
        
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
        
        return jsonify_success(
            {
                "options": added_options,
                "count": len(added_options)
            },
            f"Added {len(added_options)} options to round {round_number}"
        )
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)


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
            return jsonify_error("Request body is required", 400)
        
        selected_option_id = data.get("selected_option_id")
        user_id = data.get("user_id")
        
        if not selected_option_id:
            return jsonify_error("selected_option_id is required", 400)
        
        # Get round
        round_response = supabase.table("rounds").select("*").eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not round_response.data:
            return jsonify_error("Round not found", 404)
        
        round_data = round_response.data[0]
        
        # Verify option exists
        option_response = supabase.table("options").select("*").eq("option_id", selected_option_id).eq("lobby_id", lobby_id).eq("round_number", round_number).execute()
        if not option_response.data:
            return jsonify_error("Option not found for this round", 404)
        
        # Update round status
        supabase.table("rounds").update({
            "status": "completed",
            "selected_option_id": selected_option_id,
            "completed_at": datetime.utcnow().isoformat()
            # removed updated_at as it doesn't exist in rounds table
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
                # removed updated_at as it doesn't exist in rounds table
                }).eq("round_id", next_round.get("round_id")).execute()
                
                # Update lobby current_round
                supabase.table("lobbies").update({
                    "current_round": next_round_number,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("lobby_id", lobby_id).execute()
        
        return jsonify_success(
            {
                "round_number": round_number,
                "selected_option_id": selected_option_id,
                "all_rounds_completed": all_completed,
                "next_round": round_number + 1 if not all_completed else None
            },
            "Round completed successfully"
        )
        
    except Exception as e:
        return jsonify_error(f"Internal server error: {str(e)}", 500)
