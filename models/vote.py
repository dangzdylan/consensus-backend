"""
Vote model module.
Defines the Vote data model for tracking user votes.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class Vote:
    """
    Vote model representing a user's vote on an option.
    
    Attributes:
        vote_id: Unique identifier for the vote
        user_id: ID of the user who voted
        option_id: ID of the option being voted on
        lobby_id: ID of the lobby
        round_number: Which voting round (1-indexed)
        vote: True for yes, False for no
        created_at: Timestamp when the vote was cast
    """
    
    def __init__(
        self,
        vote_id: str,
        user_id: str,
        option_id: str,
        lobby_id: str,
        round_number: int,
        vote: bool,  # True = yes, False = no
        created_at: Optional[datetime] = None
    ):
        self.vote_id = vote_id
        self.user_id = user_id
        self.option_id = option_id
        self.lobby_id = lobby_id
        self.round_number = round_number
        self.vote = vote
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Vote instance to dictionary."""
        return {
            "vote_id": self.vote_id,
            "user_id": self.user_id,
            "option_id": self.option_id,
            "lobby_id": self.lobby_id,
            "round_number": self.round_number,
            "vote": self.vote,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vote":
        """Create Vote instance from dictionary."""
        return cls(
            vote_id=data.get("vote_id") or data.get("id"),
            user_id=data.get("user_id"),
            option_id=data.get("option_id"),
            lobby_id=data.get("lobby_id"),
            round_number=data.get("round_number", 1),
            vote=bool(data.get("vote", False)),
            created_at=data.get("created_at")
        )

