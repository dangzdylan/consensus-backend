"""
Option model module.
Defines the Option data model for swiping/voting options.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class Option:
    """
    Option model representing an activity/restaurant option for voting.
    
    Attributes:
        option_id: Unique identifier for the option
        lobby_id: ID of the lobby this option belongs to
        round_number: Which voting round this option is for (1-indexed)
        category: Activity category (Food, Recreation, Nature, Arts, Social)
        name: Name of the option
        location: Location coordinates (latitude, longitude)
        distance: Distance in miles (optional)
        image_url: Image URL (optional)
        hours: Opening hours {open: int, close: int, days: [0-6]} (optional)
        address: Address string (optional)
        created_at: Timestamp when the option was created
    """
    
    def __init__(
        self,
        option_id: str,
        lobby_id: str,
        round_number: int,
        category: str,
        name: str,
        location: Dict[str, float],
        distance: Optional[float] = None,
        image_url: Optional[str] = None,
        hours: Optional[Dict[str, Any]] = None,
        address: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.option_id = option_id
        self.lobby_id = lobby_id
        self.round_number = round_number
        self.category = category
        self.name = name
        self.location = location
        self.distance = distance
        self.image_url = image_url
        self.hours = hours
        self.address = address
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Option instance to dictionary."""
        return {
            "id": self.option_id,
            "option_id": self.option_id,
            "lobby_id": self.lobby_id,
            "round_number": self.round_number,
            "category": self.category,
            "name": self.name,
            "location": self.location,
            "distance": self.distance,
            "image": self.image_url,
            "image_url": self.image_url,
            "hours": self.hours,
            "address": self.address,
            "time": self._format_time(),  # For frontend compatibility
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    def _format_time(self) -> str:
        """Format time for display (placeholder - would use hours data)."""
        # This would calculate based on hours or round_number
        return "12:00 PM"  # Placeholder
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Option":
        """Create Option instance from dictionary."""
        return cls(
            option_id=data.get("option_id") or data.get("id"),
            lobby_id=data.get("lobby_id"),
            round_number=data.get("round_number", 1),
            category=data.get("category", "Food"),
            name=data.get("name", ""),
            location=data.get("location", {}),
            distance=data.get("distance"),
            image_url=data.get("image_url") or data.get("image"),
            hours=data.get("hours"),
            address=data.get("address"),
            created_at=data.get("created_at")
        )

