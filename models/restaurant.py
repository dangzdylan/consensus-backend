"""
Restaurant model module.
Defines the Restaurant data model structure.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class Restaurant:
    """
    Restaurant model representing a restaurant/place to eat.
    
    Attributes:
        restaurant_id: Unique identifier for the restaurant
        name: Restaurant name
        address: Full address string
        location: Location coordinates (latitude, longitude)
        cuisine_type: Type of cuisine
        rating: Rating (typically 0-5)
        price_range: Price range (e.g., "$", "$$", "$$$", "$$$$")
        phone: Phone number (optional)
        image_url: Image URL (optional)
        yelp_id: Yelp business ID (optional)
        google_place_id: Google Places ID (optional)
        hours: Opening hours (optional)
        lobby_id: ID of the lobby this restaurant belongs to
        created_at: Timestamp when the restaurant was added
    """
    
    def __init__(
        self,
        restaurant_id: str,
        name: str,
        address: str,
        location: Dict[str, float],
        lobby_id: str,
        cuisine_type: Optional[str] = None,
        rating: Optional[float] = None,
        price_range: Optional[str] = None,
        phone: Optional[str] = None,
        image_url: Optional[str] = None,
        yelp_id: Optional[str] = None,
        google_place_id: Optional[str] = None,
        hours: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None
    ):
        self.restaurant_id = restaurant_id
        self.name = name
        self.address = address
        self.location = location
        self.cuisine_type = cuisine_type
        self.rating = rating
        self.price_range = price_range
        self.phone = phone
        self.image_url = image_url
        self.yelp_id = yelp_id
        self.google_place_id = google_place_id
        self.hours = hours
        self.lobby_id = lobby_id
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Restaurant instance to dictionary."""
        return {
            "restaurant_id": self.restaurant_id,
            "name": self.name,
            "address": self.address,
            "location": self.location,
            "cuisine_type": self.cuisine_type,
            "rating": self.rating,
            "price_range": self.price_range,
            "phone": self.phone,
            "image_url": self.image_url,
            "yelp_id": self.yelp_id,
            "google_place_id": self.google_place_id,
            "hours": self.hours,
            "lobby_id": self.lobby_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Restaurant":
        """Create Restaurant instance from dictionary."""
        return cls(
            restaurant_id=data.get("restaurant_id") or data.get("id"),
            name=data.get("name"),
            address=data.get("address"),
            location=data.get("location", {}),
            lobby_id=data.get("lobby_id"),
            cuisine_type=data.get("cuisine_type"),
            rating=data.get("rating"),
            price_range=data.get("price_range"),
            phone=data.get("phone"),
            image_url=data.get("image_url"),
            yelp_id=data.get("yelp_id"),
            google_place_id=data.get("google_place_id"),
            hours=data.get("hours"),
            created_at=data.get("created_at")
        )

