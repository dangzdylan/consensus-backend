"""
Simple test script for testing Consensus backend endpoints.
Run this after starting the Flask server.
"""

import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:5001"

def print_response(response, title):
    """Print formatted response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_signup():
    """Test user signup."""
    print("\n🧪 Testing User Signup...")
    data = {
        "username": f"testuser_{uuid.uuid4().hex[:8]}"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
    print_response(response, "Signup Response")
    # Accept both 200 and 201 as success
    if response.status_code in [200, 201]:
        try:
            return response.json().get("data", {}).get("user_id")
        except:
            # If JSON parsing fails, try to extract user_id from response text
            return None
    return None

def test_create_lobby(user_id):
    """Test lobby creation."""
    print("\n🧪 Testing Create Lobby...")
    from datetime import datetime
    
    # Get today's date in MM/DD/YYYY format
    today = datetime.now()
    date_str = today.strftime("%m/%d/%Y")
    
    data = {
        "host_id": user_id,
        "location": {
            "latitude": 37.8715,  # Berkeley, CA
            "longitude": -122.2730
        },
        "radius": 2.5,
        "date": date_str,
        "start_hour": 10,  # 10 AM
        "end_hour": 18,    # 6 PM
        "activity_counts": {
            "Food": 2,
            "Recreation & Entertainment": 1,
            "Nature": 0,
            "Arts": 0,
            "Social": 0
        },
        "max_members": 10
    }
    response = requests.post(f"{BASE_URL}/api/lobbies", json=data)
    print_response(response, "Create Lobby Response")
    if response.status_code == 201:
        return response.json().get("data", {}).get("lobby_id"), response.json().get("data", {}).get("code")
    return None, None

def test_join_lobby(code, user_id):
    """Test joining a lobby."""
    print("\n🧪 Testing Join Lobby...")
    data = {
        "code": code,
        "user_id": user_id
    }
    response = requests.post(f"{BASE_URL}/api/lobbies/join", json=data)
    print_response(response, "Join Lobby Response")
    return response.status_code == 200

def test_get_lobby(lobby_id):
    """Test getting lobby details."""
    print("\n🧪 Testing Get Lobby...")
    response = requests.get(f"{BASE_URL}/api/lobbies/{lobby_id}")
    print_response(response, "Get Lobby Response")
    return response.status_code == 200

def test_get_user_current_lobby(user_id):
    """Test getting user's current lobby."""
    print("\n🧪 Testing Get User Current Lobby...")
    response = requests.get(f"{BASE_URL}/api/lobbies/user/{user_id}/current")
    print_response(response, "Get User Current Lobby Response")
    return response.status_code == 200

def test_error_cases():
    """Test error handling."""
    print("\n🧪 Testing Error Cases...")
    
    # Test invalid location
    print("\n--- Testing Invalid Location ---")
    data = {
        "host_id": "test-user-id",
        "location": {
            "latitude": 100,  # Invalid (> 90)
            "longitude": -122.2730
        },
        "radius": 2.5
    }
    response = requests.post(f"{BASE_URL}/api/lobbies", json=data)
    print_response(response, "Invalid Location Response")
    
    # Test invalid code
    print("\n--- Testing Invalid Code ---")
    data = {
        "code": "INVALID",
        "user_id": "test-user-id"
    }
    response = requests.post(f"{BASE_URL}/api/lobbies/join", json=data)
    print_response(response, "Invalid Code Response")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CONSENSUS BACKEND API TESTING")
    print("="*60)
    print("\n⚠️  Make sure the Flask server is running on http://127.0.0.1:5001")
    input("\nPress Enter to start testing...")
    
    # Test signup
    user_id = test_signup()
    if not user_id:
        print("\n❌ Signup failed. Please check your database setup.")
        return
    
    print(f"\n✅ Signup successful! User ID: {user_id}")
    
    # Test create lobby
    lobby_id, code = test_create_lobby(user_id)
    if not lobby_id:
        print("\n❌ Create lobby failed.")
        return
    
    print(f"\n✅ Lobby created with ID: {lobby_id}")
    print(f"✅ Join code: {code}")
    
    # Test get lobby
    test_get_lobby(lobby_id)
    
    # Test get user current lobby
    test_get_user_current_lobby(user_id)
    
    # Test join lobby (need another user)
    print("\n🧪 Testing Join Lobby (creating second user)...")
    user_id_2 = test_signup()
    if user_id_2:
        test_join_lobby(code, user_id_2)
    
    # Test error cases
    test_error_cases()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\n✅ Check the responses above to verify everything works correctly!")

if __name__ == "__main__":
    main()

