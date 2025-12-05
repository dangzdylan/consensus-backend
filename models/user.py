"""
User model module.
Defines the User data model structure.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class User:
    """
    User model representing a user in the Consensus application.
    
    Attributes:
        user_id: Unique identifier for the user
        username: User's username
        email: User's email address (optional, for backward compatibility)
        location: User's current location (latitude, longitude)
        current_lobby_id: ID of the lobby the user is currently in (if any)
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
    """
    
    def __init__(
        self,
        user_id: str,
        username: str,
        email: Optional[str] = None,
        location: Optional[Dict[str, float]] = None,
        current_lobby_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.location = location or {}
        self.current_lobby_id = current_lobby_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User instance to dictionary."""
        result = {
            "user_id": self.user_id,
            "username": self.username,
            "location": self.location,
            "current_lobby_id": self.current_lobby_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        # Only include email if it exists (for backward compatibility)
        if self.email:
            result["email"] = self.email
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create User instance from dictionary."""
        return cls(
            user_id=data.get("user_id") or data.get("id"),
            username=data.get("username"),
            email=data.get("email"),
            location=data.get("location"),
            current_lobby_id=data.get("current_lobby_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

