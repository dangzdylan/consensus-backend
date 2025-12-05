"""
Round model module.
Defines the Round data model for tracking voting rounds.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class Round:
    """
    Round model representing a voting round in a lobby.
    
    Attributes:
        round_id: Unique identifier for the round
        lobby_id: ID of the lobby
        round_number: Round number (1-indexed)
        category: Activity category for this round
        status: Round status (active, completed, tiebreaker)
        selected_option_id: ID of the selected option (if consensus reached)
        is_tiebreaker: Whether this is a tiebreaker round
        parent_round_id: ID of the parent round (if tiebreaker)
        created_at: Timestamp when the round was created
        completed_at: Timestamp when the round was completed
    """
    
    def __init__(
        self,
        round_id: str,
        lobby_id: str,
        round_number: int,
        category: str,
        status: str = "active",  # active, completed, tiebreaker
        selected_option_id: Optional[str] = None,
        is_tiebreaker: bool = False,
        parent_round_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        self.round_id = round_id
        self.lobby_id = lobby_id
        self.round_number = round_number
        self.category = category
        self.status = status
        self.selected_option_id = selected_option_id
        self.is_tiebreaker = is_tiebreaker
        self.parent_round_id = parent_round_id
        self.created_at = created_at or datetime.utcnow()
        self.completed_at = completed_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Round instance to dictionary."""
        return {
            "round_id": self.round_id,
            "lobby_id": self.lobby_id,
            "round_number": self.round_number,
            "category": self.category,
            "status": self.status,
            "selected_option_id": self.selected_option_id,
            "is_tiebreaker": self.is_tiebreaker,
            "parent_round_id": self.parent_round_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "completed_at": self.completed_at.isoformat() if isinstance(self.completed_at, datetime) else self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Round":
        """Create Round instance from dictionary."""
        return cls(
            round_id=data.get("round_id") or data.get("id"),
            lobby_id=data.get("lobby_id"),
            round_number=data.get("round_number", 1),
            category=data.get("category", "Food"),
            status=data.get("status", "active"),
            selected_option_id=data.get("selected_option_id"),
            is_tiebreaker=bool(data.get("is_tiebreaker", False)),
            parent_round_id=data.get("parent_round_id"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at")
        )

