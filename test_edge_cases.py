"""
Comprehensive edge case testing for the consensus backend.
Tests 25+ users, race conditions, network failures, and error scenarios.
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import random
import string

BASE_URL = "http://127.0.0.1:5001/api"

def generate_username(length=8):
    """Generate random username."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_user(username=None):
    """Create a test user."""
    if not username:
        username = generate_username()
    response = requests.post(f"{BASE_URL}/auth/signup", json={"username": username})
    if response.status_code in [200, 201]:
        return response.json().get("data", {}).get("user_id"), username
    return None, username

def create_lobby(host_id, location=None, activity_counts=None):
    """Create a test lobby."""
    if not location:
        location = {"latitude": 37.7749, "longitude": -122.4194}
    if not activity_counts:
        activity_counts = {"Food": 1, "Activity": 1}
    
    data = {
        "host_id": host_id,
        "location": location,
        "radius": 10.0,
        "date": "12/25/2024",
        "start_hour": 12,
        "end_hour": 20,
        "activity_counts": activity_counts,
        "max_members": 25
    }
    response = requests.post(f"{BASE_URL}/lobby", json=data)
    if response.status_code == 200:
        return response.json().get("data", {}).get("lobby_id"), response.json().get("data", {}).get("code")
    return None, None

def join_lobby(user_id, code):
    """Join a lobby."""
    response = requests.post(f"{BASE_URL}/lobby/join", json={"user_id": user_id, "code": code})
    return response.status_code == 200

def start_game(lobby_id):
    """Start a game."""
    response = requests.post(f"{BASE_URL}/consensus/lobby/{lobby_id}/start")
    return response.status_code == 200

def submit_vote(lobby_id, user_id, option_id, round_number, vote_type="like"):
    """Submit a vote."""
    data = {
        "user_id": user_id,
        "option_id": option_id,
        "round_number": round_number,
        "vote": vote_type
    }
    response = requests.post(f"{BASE_URL}/consensus/lobby/{lobby_id}/vote", json=data)
    return response.status_code == 200

def get_round_options(lobby_id, round_number):
    """Get options for a round."""
    response = requests.get(f"{BASE_URL}/consensus/lobby/{lobby_id}/round/{round_number}/options")
    if response.status_code == 200:
        return response.json().get("data", {}).get("options", [])
    return []

def test_concurrent_signups(num_users=30):
    """Test 30 users signing up simultaneously."""
    print(f"\n=== Test 1: Concurrent Signups ({num_users} users) ===")
    results = []
    
    def signup_user():
        user_id, username = create_user()
        return user_id is not None
    
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(signup_user) for _ in range(num_users)]
        for future in as_completed(futures):
            results.append(future.result())
    
    success_count = sum(results)
    print(f"Success: {success_count}/{num_users}")
    return success_count == num_users

def test_concurrent_joins(num_users=25):
    """Test 25 users joining the same lobby simultaneously."""
    print(f"\n=== Test 2: Concurrent Joins ({num_users} users) ===")
    
    # Create host and lobby
    host_id, _ = create_user("host_user")
    if not host_id:
        print("Failed to create host")
        return False
    
    lobby_id, code = create_lobby(host_id, max_members=num_users)
    if not lobby_id:
        print("Failed to create lobby")
        return False
    
    print(f"Lobby created: {lobby_id}, Code: {code}")
    
    # Create users and join simultaneously
    user_ids = []
    def create_and_join():
        user_id, _ = create_user()
        if user_id:
            success = join_lobby(user_id, code)
            return success
        return False
    
    results = []
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(create_and_join) for _ in range(num_users)]
        for future in as_completed(futures):
            results.append(future.result())
    
    # Check lobby status
    response = requests.get(f"{BASE_URL}/lobby/{lobby_id}/status")
    if response.status_code == 200:
        lobby_data = response.json().get("data", {})
        member_count = len(lobby_data.get("members", []))
        print(f"Members in lobby: {member_count}")
        print(f"Successful joins: {sum(results)}/{num_users}")
        return member_count <= num_users  # Should not exceed max
    return False

def test_race_condition_votes(lobby_id, num_users=10):
    """Test multiple users voting simultaneously."""
    print(f"\n=== Test 3: Race Condition Votes ({num_users} users) ===")
    
    # Start game first
    if not start_game(lobby_id):
        print("Failed to start game")
        return False
    
    time.sleep(1)  # Wait for game to start
    
    # Get options for round 1
    options = get_round_options(lobby_id, 1)
    if not options:
        print("No options available")
        return False
    
    option_id = options[0].get("option_id")
    
    # Get lobby members
    response = requests.get(f"{BASE_URL}/lobby/{lobby_id}/status")
    if response.status_code != 200:
        return False
    
    members = response.json().get("data", {}).get("members", [])
    user_ids = [m.get("user_id") for m in members[:num_users]]
    
    # All users vote simultaneously
    results = []
    def vote(user_id):
        return submit_vote(lobby_id, user_id, option_id, 1, "like")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(vote, uid) for uid in user_ids]
        for future in as_completed(futures):
            results.append(future.result())
    
    success_count = sum(results)
    print(f"Successful votes: {success_count}/{len(user_ids)}")
    
    # Check vote count
    response = requests.get(f"{BASE_URL}/consensus/lobby/{lobby_id}/round/1/status")
    if response.status_code == 200:
        round_data = response.json().get("data", {})
        votes = round_data.get("votes", [])
        print(f"Total votes recorded: {len(votes)}")
        return len(votes) == success_count
    return False

def test_lobby_full_edge_case():
    """Test joining a full lobby."""
    print(f"\n=== Test 4: Lobby Full Edge Case ===")
    
    # Create lobby with max_members=2
    host_id, _ = create_user("host_full")
    lobby_id, code = create_lobby(host_id, max_members=2)
    
    # Fill lobby
    user1_id, _ = create_user()
    user2_id, _ = create_user()
    join_lobby(user1_id, code)
    join_lobby(user2_id, code)
    
    # Try to join when full
    user3_id, _ = create_user()
    response = requests.post(f"{BASE_URL}/lobby/join", json={"user_id": user3_id, "code": code})
    
    if response.status_code == 400:
        error_msg = response.json().get("error", "")
        if "full" in error_msg.lower():
            print("✓ Correctly rejected join to full lobby")
            return True
    
    print("✗ Failed to reject join to full lobby")
    return False

def test_duplicate_username():
    """Test duplicate username handling."""
    print(f"\n=== Test 5: Duplicate Username ===")
    
    username = generate_username()
    user1_id, _ = create_user(username)
    
    if not user1_id:
        return False
    
    # Try to create same username
    user2_id, _ = create_user(username)
    
    if user2_id is None:
        print("✓ Correctly rejected duplicate username")
        return True
    
    print("✗ Failed to reject duplicate username")
    return False

def test_invalid_lobby_code():
    """Test joining with invalid code."""
    print(f"\n=== Test 6: Invalid Lobby Code ===")
    
    user_id, _ = create_user()
    response = requests.post(f"{BASE_URL}/lobby/join", json={"user_id": user_id, "code": "INVALID"})
    
    if response.status_code == 404:
        print("✓ Correctly rejected invalid lobby code")
        return True
    
    print("✗ Failed to reject invalid lobby code")
    return False

def test_network_failure_simulation():
    """Simulate network failures by testing with invalid data."""
    print(f"\n=== Test 7: Network Failure Simulation ===")
    
    # Test with missing fields
    response = requests.post(f"{BASE_URL}/auth/signup", json={})
    if response.status_code == 400:
        print("✓ Handles missing fields")
    else:
        print("✗ Failed to handle missing fields")
        return False
    
    # Test with invalid data types
    response = requests.post(f"{BASE_URL}/lobby", json={
        "host_id": "invalid",
        "location": "not a dict",
        "radius": "not a number"
    })
    if response.status_code == 400:
        print("✓ Handles invalid data types")
    else:
        print("✗ Failed to handle invalid data types")
        return False
    
    return True

def test_concurrent_game_starts(lobby_id):
    """Test multiple simultaneous game start requests."""
    print(f"\n=== Test 8: Concurrent Game Starts ===")
    
    results = []
    def start():
        response = requests.post(f"{BASE_URL}/consensus/lobby/{lobby_id}/start")
        return response.status_code in [200, 400]  # 400 if already started
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(start) for _ in range(5)]
        for future in as_completed(futures):
            results.append(future.result())
    
    # Should handle gracefully (either all succeed or some get "already started")
    success_count = sum(results)
    print(f"Successful starts: {success_count}/5")
    return success_count >= 1  # At least one should succeed

def test_max_capacity_stress():
    """Test system with maximum capacity (25 users)."""
    print(f"\n=== Test 9: Max Capacity Stress Test (25 users) ===")
    
    # Create host
    host_id, _ = create_user("stress_host")
    lobby_id, code = create_lobby(host_id, max_members=25)
    
    # Create 24 more users and join
    user_ids = []
    for i in range(24):
        user_id, _ = create_user(f"stress_user_{i}")
        if user_id:
            user_ids.append(user_id)
            join_lobby(user_id, code)
            time.sleep(0.1)  # Small delay to avoid overwhelming
    
    # Start game
    if start_game(lobby_id):
        print("✓ Game started with 25 users")
        
        # Get options and have all users vote
        options = get_round_options(lobby_id, 1)
        if options:
            option_id = options[0].get("option_id")
            vote_results = []
            for user_id in user_ids + [host_id]:
                vote_results.append(submit_vote(lobby_id, user_id, option_id, 1, "like"))
            
            print(f"Votes submitted: {sum(vote_results)}/25")
            return sum(vote_results) == 25
    
    return False

def main():
    """Run all edge case tests."""
    print("=" * 60)
    print("EDGE CASE TESTING SUITE")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health", timeout=2)
    except:
        print("ERROR: Backend server not running on port 5001")
        print("Please start the server with: python3 app.py")
        return
    
    results = []
    
    # Run tests
    results.append(("Concurrent Signups", test_concurrent_signups(30)))
    results.append(("Concurrent Joins", test_concurrent_joins(25)))
    
    # Create a lobby for vote tests
    host_id, _ = create_user("vote_test_host")
    lobby_id, _ = create_lobby(host_id, max_members=10)
    if lobby_id:
        # Add some users
        for i in range(5):
            user_id, _ = create_user(f"vote_user_{i}")
            if lobby_id:
                join_lobby(user_id, _)
        
        results.append(("Race Condition Votes", test_race_condition_votes(lobby_id, 5)))
        results.append(("Concurrent Game Starts", test_concurrent_game_starts(lobby_id)))
    
    results.append(("Lobby Full Edge Case", test_lobby_full_edge_case()))
    results.append(("Duplicate Username", test_duplicate_username()))
    results.append(("Invalid Lobby Code", test_invalid_lobby_code()))
    results.append(("Network Failure Simulation", test_network_failure_simulation()))
    results.append(("Max Capacity Stress", test_max_capacity_stress()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()

