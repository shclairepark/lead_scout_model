"""
SignalEvent: Core data class for all signal types.

This is the unified format for signals from LinkedIn, funding announcements,
role changes, events, and any other intent indicators.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class SignalType(Enum):
    """Types of signals that can be detected."""
    # LinkedIn signals (Agent 0A)
    CONTENT_ENGAGEMENT = "content_engagement"
    PROFILE_VISIT = "profile_visit"
    TOPIC_INTERACTION = "topic_interaction"
    COMPETITOR_ENGAGEMENT = "competitor_engagement"
    
    # External signals (Agent 0B)
    FUNDING_ROUND = "funding_round"
    ROLE_CHANGE = "role_change"
    EVENT_ATTENDANCE = "event_attendance"
    GROUP_JOIN = "group_join"
    
    # High Intent signals
    DEMO_REQUEST = "demo_request"
    PRICING_PAGE_VISIT = "pricing_page_visit"


class SignalSource(Enum):
    """Source of the signal."""
    LINKEDIN = "linkedin"
    CRUNCHBASE = "crunchbase"
    COMPANY_WEBSITE = "company_website"
    EVENT_PLATFORM = "event_platform"
    SLACK = "slack"
    MANUAL = "manual"


@dataclass(frozen=True)
class SignalEvent:
    """
    Unified signal event representing any buying signal.
    
    Attributes:
        type: The type of signal (e.g., content_engagement, funding_round)
        user_id: LinkedIn user ID or unique identifier for the prospect
        timestamp: When the signal was detected
        source: Where the signal originated from
        data: Additional signal-specific data
        company_id: Optional company identifier
        strength: Signal strength score (0.0 to 1.0)
    """
    type: SignalType
    user_id: str
    timestamp: datetime
    source: SignalSource
    data: Dict[str, Any] = field(default_factory=dict, hash=False)
    company_id: Optional[str] = None
    strength: float = 0.5
    
    def __post_init__(self):
        """Validate signal data after initialization."""
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Signal strength must be between 0.0 and 1.0, got {self.strength}")
        
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary for serialization."""
        return {
            "type": self.type.value,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.value,
            "data": self.data,
            "company_id": self.company_id,
            "strength": self.strength,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignalEvent":
        """Create SignalEvent from dictionary."""
        return cls(
            type=SignalType(data["type"]),
            user_id=data["user_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=SignalSource(data["source"]),
            data=data.get("data", {}),
            company_id=data.get("company_id"),
            strength=data.get("strength", 0.5),
        )
    
    def age_hours(self, reference_time: Optional[datetime] = None) -> float:
        """Calculate signal age in hours from reference time (default: now)."""
        ref = reference_time or datetime.now()
        delta = ref - self.timestamp
        return delta.total_seconds() / 3600
    
    def decay_weight(self, half_life_hours: float = 168) -> float:
        """
        Calculate exponential decay weight based on signal age.
        
        Args:
            half_life_hours: Hours after which signal strength halves (default: 7 days)
            
        Returns:
            Decay weight between 0.0 and 1.0
        """
        import math
        age = self.age_hours()
        return math.exp(-0.693 * age / half_life_hours)
