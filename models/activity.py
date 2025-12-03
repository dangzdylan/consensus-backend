"""
Activity model module.
Defines the Activity data model structure.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class Activity:
    """
    Activity model representing an activity/place to do something.
    
    Attributes:
        activity_id: Unique identifier for the activity
        name: Activity/place name
        category: Category (e.g., "sports", "art", "museums", "parks", "concerts", "games", "shopping", "sightseeing")
        address: Full address string
        location: Location coordinates (latitude, longitude)
        rating: Rating (typically 0-5)
        price_range: Price range or cost information
        phone: Phone number (optional)
        image_url: Image URL (optional)
        hours: Opening hours (optional)
        requirements: Requirements (e.g., "id", "ticket") (optional)
        yelp_id: Yelp business ID (optional)
        google_place_id: Google Places ID (optional)
        lobby_id: ID of the lobby this activity belongs to
        created_at: Timestamp when the activity was added
    """
    
    def __init__(
        self,
        activity_id: str,
        name: str,
        category: str,
        address: str,
        location: Dict[str, float],
        lobby_id: str,
        rating: Optional[float] = None,
        price_range: Optional[str] = None,
        phone: Optional[str] = None,
        image_url: Optional[str] = None,
        hours: Optional[Dict[str, Any]] = None,
        requirements: Optional[List[str]] = None,
        yelp_id: Optional[str] = None,
        google_place_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.activity_id = activity_id
        self.name = name
        self.category = category
        self.address = address
        self.location = location
        self.rating = rating
        self.price_range = price_range
        self.phone = phone
        self.image_url = image_url
        self.hours = hours
        self.requirements = requirements or []
        self.yelp_id = yelp_id
        self.google_place_id = google_place_id
        self.lobby_id = lobby_id
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Activity instance to dictionary."""
        return {
            "activity_id": self.activity_id,
            "name": self.name,
            "category": self.category,
            "address": self.address,
            "location": self.location,
            "rating": self.rating,
            "price_range": self.price_range,
            "phone": self.phone,
            "image_url": self.image_url,
            "hours": self.hours,
            "requirements": self.requirements,
            "yelp_id": self.yelp_id,
            "google_place_id": self.google_place_id,
            "lobby_id": self.lobby_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Activity":
        """Create Activity instance from dictionary."""
        return cls(
            activity_id=data.get("activity_id") or data.get("id"),
            name=data.get("name"),
            category=data.get("category"),
            address=data.get("address"),
            location=data.get("location", {}),
            lobby_id=data.get("lobby_id"),
            rating=data.get("rating"),
            price_range=data.get("price_range"),
            phone=data.get("phone"),
            image_url=data.get("image_url"),
            hours=data.get("hours"),
            requirements=data.get("requirements", []),
            yelp_id=data.get("yelp_id"),
            google_place_id=data.get("google_place_id"),
            created_at=data.get("created_at")
        )

