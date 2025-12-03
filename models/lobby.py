"""
Lobby model module.
Defines the Lobby data model structure.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import secrets
import string


class Lobby:
    """
    Lobby model representing a consensus lobby.
    
    Attributes:
        lobby_id: Unique identifier for the lobby
        code: 4-character join code for the lobby
        host_id: User ID of the lobby host
        user_ids: List of user IDs in the lobby
        location: Central location (latitude, longitude)
        radius: Search radius in miles
        deck_type: Type of deck (e.g., "Where to Eat?", "What to Do?")
        status: Lobby status (e.g., "active", "completed", "cancelled")
        scheduled_time: Optional scheduled time for the consensus
        created_at: Timestamp when the lobby was created
        updated_at: Timestamp when the lobby was last updated
    """
    
    @staticmethod
    def generate_code(length: int = 4) -> str:
        """Generate a random alphanumeric code."""
        characters = string.ascii_uppercase + string.digits
        # Exclude ambiguous characters (0, O, I, 1)
        characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def __init__(
        self,
        lobby_id: str,
        host_id: str,
        location: Dict[str, float],
        radius: float,
        deck_type: str = "Where to Eat?",
        code: Optional[str] = None,
        user_ids: Optional[List[str]] = None,
        status: str = "active",
        scheduled_time: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.lobby_id = lobby_id
        self.code = code or self.generate_code()
        self.host_id = host_id
        self.user_ids = user_ids or [host_id]  # Host is automatically added
        self.location = location
        self.radius = radius
        self.deck_type = deck_type
        self.status = status
        self.scheduled_time = scheduled_time
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Lobby instance to dictionary."""
        return {
            "lobby_id": self.lobby_id,
            "code": self.code,
            "host_id": self.host_id,
            "user_ids": self.user_ids,
            "location": self.location,
            "radius": self.radius,
            "deck_type": self.deck_type,
            "status": self.status,
            "scheduled_time": self.scheduled_time.isoformat() if isinstance(self.scheduled_time, datetime) else self.scheduled_time,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lobby":
        """Create Lobby instance from dictionary."""
        return cls(
            lobby_id=data.get("lobby_id") or data.get("id"),
            host_id=data.get("host_id"),
            location=data.get("location", {}),
            radius=data.get("radius", 2.5),
            deck_type=data.get("deck_type", "Where to Eat?"),
            code=data.get("code"),
            user_ids=data.get("user_ids", []),
            status=data.get("status", "active"),
            scheduled_time=data.get("scheduled_time"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

