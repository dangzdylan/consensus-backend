# API Documentation for Home, Create Lobby, and Join Lobby Screens

This document describes all the backend APIs implemented for the screens assigned to Aakash:
- Home Screen
- Create Lobby Screen  
- Join Lobby Screen

## Base URL
All endpoints are prefixed with `/api`

## Authentication
Currently, endpoints require `user_id` to be passed in the request body. This can be enhanced later with JWT tokens or session management.

---

## Lobby Endpoints

### 1. Create Lobby
**Endpoint:** `POST /api/lobbies`

**Description:** Creates a new lobby and automatically fetches restaurants/activities from Yelp or Google Places API based on the location and radius.

**Request Body:**
```json
{
  "host_id": "user-uuid-here",
  "location": {
    "latitude": 37.8715,
    "longitude": -122.2730
  },
  "radius": 2.5,
  "deck_type": "Where to Eat?"  // Optional, defaults to "Where to Eat?"
}
```

**Response (201 Created):**
```json
{
  "data": {
    "lobby_id": "lobby-uuid",
    "code": "ABCD",
    "location": {
      "latitude": 37.8715,
      "longitude": -122.2730
    },
    "radius": 2.5,
    "deck_type": "Where to Eat?",
    "user_ids": ["user-uuid-here"],
    "places_fetched": 25
  },
  "message": "Lobby created successfully"
}
```

**Notes:**
- Automatically fetches and stores restaurants/activities from external APIs
- Generates a unique 4-character join code
- Sets the host as the first user in the lobby
- Updates the host's `current_lobby_id`

**Error Responses:**
- `400`: Missing required fields, invalid location/radius, user already in a lobby
- `404`: User not found
- `500`: Failed to create lobby or fetch places

---

### 2. Join Lobby
**Endpoint:** `POST /api/lobbies/join`

**Description:** Allows a user to join an existing lobby using a 4-character code.

**Request Body:**
```json
{
  "code": "ABCD",
  "user_id": "user-uuid-here"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "lobby_id": "lobby-uuid",
    "code": "ABCD",
    "host_id": "host-uuid",
    "user_ids": ["host-uuid", "user-uuid-here"],
    "location": {
      "latitude": 37.8715,
      "longitude": -122.2730
    },
    "radius": 2.5,
    "deck_type": "Where to Eat?",
    "status": "active"
  },
  "message": "Successfully joined lobby"
}
```

**Error Responses:**
- `400`: Missing code/user_id, invalid code format, user already in lobby, lobby not active
- `404`: Lobby or user not found
- `500`: Internal server error

---

### 3. Get Lobby Details
**Endpoint:** `GET /api/lobbies/<lobby_id>`

**Description:** Retrieves details of a specific lobby.

**Response (200 OK):**
```json
{
  "data": {
    "lobby_id": "lobby-uuid",
    "code": "ABCD",
    "host_id": "host-uuid",
    "user_ids": ["user1", "user2"],
    "location": {...},
    "radius": 2.5,
    "deck_type": "Where to Eat?",
    "status": "active"
  },
  "message": "Lobby retrieved successfully"
}
```

---

### 4. Get User's Current Lobby
**Endpoint:** `GET /api/lobbies/user/<user_id>/current`

**Description:** Gets the lobby the user is currently in (if any).

**Response (200 OK):**
```json
{
  "data": {
    "lobby_id": "lobby-uuid",
    "code": "ABCD",
    ...
  },
  "message": "Current lobby retrieved successfully"
}
```

**Response if not in lobby:**
```json
{
  "data": null,
  "message": "User is not in any lobby"
}
```

---

### 5. Get Lobby Places
**Endpoint:** `GET /api/lobbies/<lobby_id>/places`

**Description:** Retrieves all restaurants or activities for a lobby.

**Response (200 OK):**
```json
{
  "data": {
    "places": [
      {
        "restaurant_id": "rest-uuid",
        "name": "Restaurant Name",
        "address": "123 Main St",
        "location": {
          "latitude": 37.8715,
          "longitude": -122.2730
        },
        "cuisine_type": "Italian",
        "rating": 4.5,
        "price_range": "$$",
        "image_url": "https://...",
        ...
      }
    ],
    "count": 25,
    "deck_type": "Where to Eat?"
  },
  "message": "Retrieved 25 places"
}
```

---

### 6. Refresh Lobby Places
**Endpoint:** `POST /api/lobbies/<lobby_id>/refresh-places`

**Description:** Manually refresh/refetch places for a lobby. Useful if places weren't fetched initially or need to be updated.

**Response (200 OK):**
```json
{
  "data": {
    "places_fetched": 30
  },
  "message": "Successfully refreshed 30 places"
}
```

---

## Dynamic Place Fetching

The system automatically fetches places from external APIs when a lobby is created:

### Supported APIs
- **Yelp Fusion API** (default/preferred)
- **Google Places API**

### Configuration
Set in `.env` file:
- `YELP_API_KEY` - Yelp Fusion API key
- `GOOGLE_PLACES_API_KEY` - Google Places API key  
- `PREFERRED_PLACES_API` - "yelp" or "google" (default: "yelp")

### How It Works
1. When a lobby is created with location and radius, the system:
   - Determines if it's a restaurant or activity lobby based on `deck_type`
   - Calls the appropriate API (Yelp or Google Places)
   - Fetches up to 50 places within the specified radius
   - Stores all places in the database (restaurants or activities table)
   - Returns the count of places fetched

2. Places are stored with:
   - Name, address, location coordinates
   - Rating, price range, cuisine/category
   - Image URLs, phone numbers, hours
   - External API IDs (for future reference)

3. The system works with **any location and radius** - no hardcoded data!

---

## Frontend Integration Notes

### CreateLobbyScreen
When user clicks "Continue", the frontend should:
1. Get user's current location (using React Native Location API)
2. Call `POST /api/lobbies` with:
   - `host_id`: Current user's ID
   - `location`: { latitude, longitude }
   - `radius`: Value from slider
   - `deck_type`: "Where to Eat?" (or selected deck type)
3. Navigate to SwipingScreen with the `lobby_id`

### JoinLobbyScreen  
When user clicks "Join", the frontend should:
1. Call `POST /api/lobbies/join` with:
   - `code`: 4-character code from CodeInput
   - `user_id`: Current user's ID
2. Navigate to SwipingScreen with the `lobby_id`

### HomeScreen
No API calls needed - just navigation.

---

## Error Handling

All endpoints return consistent error responses:
```json
{
  "error": "Error message here"
}
```

With appropriate HTTP status codes:
- `400`: Bad Request (validation errors, missing fields)
- `404`: Not Found (lobby/user doesn't exist)
- `409`: Conflict (user already exists, etc.)
- `500`: Internal Server Error

---

## Database Tables Required

### `lobbies`
- lobby_id (primary key)
- code (unique)
- host_id
- user_ids (array)
- location (jsonb: {latitude, longitude})
- radius
- deck_type
- status
- created_at
- updated_at

### `restaurants`
- restaurant_id (primary key)
- lobby_id (foreign key)
- name
- address
- location (jsonb: {latitude, longitude})
- cuisine_type
- rating
- price_range
- phone
- image_url
- yelp_id
- google_place_id
- hours (jsonb)
- created_at

### `activities`
- activity_id (primary key)
- lobby_id (foreign key)
- name
- category
- address
- location (jsonb: {latitude, longitude})
- rating
- price_range
- phone
- image_url
- yelp_id
- google_place_id
- hours (jsonb)
- requirements (array)
- created_at

### `users`
- user_id (primary key)
- username
- email
- location (jsonb)
- current_lobby_id (foreign key, nullable)
- created_at
- updated_at

