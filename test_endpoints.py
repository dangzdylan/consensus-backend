"""
Simple test script for testing Consensus backend endpoints.
Run this after starting the Flask server.
"""

import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:5000"

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
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
    print_response(response, "Signup Response")
    if response.status_code == 201:
        return response.json().get("data", {}).get("user_id")
    return None

def test_create_lobby(user_id):
    """Test lobby creation."""
    print("\n🧪 Testing Create Lobby...")
    data = {
        "host_id": user_id,
        "location": {
            "latitude": 37.8715,  # Berkeley, CA
            "longitude": -122.2730
        },
        "radius": 2.5,
        "deck_type": "Where to Eat?"
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

def test_get_lobby_places(lobby_id):
    """Test getting lobby places."""
    print("\n🧪 Testing Get Lobby Places...")
    response = requests.get(f"{BASE_URL}/api/lobbies/{lobby_id}/places")
    print_response(response, "Get Lobby Places Response")
    if response.status_code == 200:
        data = response.json().get("data", {})
        print(f"\n✅ Found {data.get('count', 0)} places")
        return True
    return False

def test_get_user_current_lobby(user_id):
    """Test getting user's current lobby."""
    print("\n🧪 Testing Get User Current Lobby...")
    response = requests.get(f"{BASE_URL}/api/lobbies/user/{user_id}/current")
    print_response(response, "Get User Current Lobby Response")
    return response.status_code == 200

def test_refresh_places(lobby_id):
    """Test refreshing lobby places."""
    print("\n🧪 Testing Refresh Places...")
    response = requests.post(f"{BASE_URL}/api/lobbies/{lobby_id}/refresh-places")
    print_response(response, "Refresh Places Response")
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
    print("\n⚠️  Make sure the Flask server is running on http://127.0.0.1:5000")
    input("\nPress Enter to start testing...")
    
    # Test signup
    user_id = test_signup()
    if not user_id:
        print("\n❌ Signup failed. Please check your database setup.")
        return
    
    # Test create lobby
    lobby_id, code = test_create_lobby(user_id)
    if not lobby_id:
        print("\n❌ Create lobby failed.")
        return
    
    print(f"\n✅ Lobby created with ID: {lobby_id}")
    print(f"✅ Join code: {code}")
    
    # Test get lobby
    test_get_lobby(lobby_id)
    
    # Test get places
    test_get_lobby_places(lobby_id)
    
    # Test get user current lobby
    test_get_user_current_lobby(user_id)
    
    # Test refresh places
    test_refresh_places(lobby_id)
    
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

