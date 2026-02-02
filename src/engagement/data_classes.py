"""
Data classes for Automated Engagement.

Structures for engagement decisions and messages.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class EngagementPriority(Enum):
    """Priority for engagement queue."""
    HIGH = "high"       # Immediate outreach
    MEDIUM = "medium"   # Queue for review
    LOW = "low"         # Nurture / Do not contact


@dataclass
class EngagementConfig:
    """Configuration for engagement logic."""
    # Minimum scores to qualify for engagement
    min_intent_score: float = 70.0
    min_icp_score: float = 80.0
    
    # Exclusion rules
    excluded_domains: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    
    # Maximum processing batch size
    max_daily_messages: int = 50


@dataclass
class EngagementDecision:
    """
    Result of High Intent Filter evaluation.
    
    Attributes:
        should_engage: Whether outreach is recommended
        priority: Urgency of outreach
        reason: Explanation for decision (e.g., "Score > 70", "Competitor")
        decision_time: Timestamp of decision
    """
    should_engage: bool
    priority: EngagementPriority
    reason: str
    decision_time: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "should_engage": self.should_engage,
            "priority": self.priority.value,
            "reason": self.reason,
            "decision_time": self.decision_time,
        }


@dataclass
class OutreachMessage:
    """
    Generated outreach content.
    
    Attributes:
        subject: Message subject line (for email) or generic hook
        body: Main message content
        channel: Intended channel (linkedin, email)
        context_used: Which signals/data informed this message
    """
    body: str
    subject: Optional[str] = None
    channel: str = "linkedin"
    context_used: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subject": self.subject,
            "body": self.body,
            "channel": self.channel,
            "context_used": self.context_used,
        }
