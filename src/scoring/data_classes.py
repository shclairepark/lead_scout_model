"""
Data classes for Intent Scoring.

Structures for score results and configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum


class IntentLabel(Enum):
    """Intent classification labels."""
    HIGH = "high"       # Ready to buy / hot lead
    MEDIUM = "medium"   # Engagement detected / warm lead
    LOW = "low"         # Low activity / cold lead


@dataclass
class IntentScore:
    """
    Result of intent scoring calculation.
    
    Attributes:
        score: Composite score (0-100)
        label: High/Medium/Low label
        signals_score: Score derived from raw signals
        recency_factor: Impact of signal timing
        committee_factor: Impact of multiple decision makers
        breakdown: Detailed component breakdown
    """
    score: float
    label: IntentLabel
    signals_score: float
    recency_factor: float = 1.0
    committee_factor: float = 1.0
    breakdown: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "score": self.score,
            "label": self.label.value,
            "signals_score": self.signals_score,
            "recency_factor": self.recency_factor,
            "committee_factor": self.committee_factor,
            "breakdown": self.breakdown,
        }


@dataclass
class ScoringConfig:
    """
    Configuration for Intent Scoring.
    """
    # Base scores for different signal types
    signal_weights: Dict[str, float] = field(default_factory=lambda: {
        "content_engagement": 10.0,    # Like/Share
        "profile_visit": 15.0,         # Viewed your profile
        "funding_round": 40.0,         # Signal of budget/growth
        "role_change": 25.0,           # Signal of new authority
        "event_attendance": 20.0,      # Signal of interest
        "demo_request": 70.0,          # Explicit high intent
        "pricing_page_visit": 35.0,    # High intent behavior
    })
    
    # Modifiers for signal strength (e.g. share > like)
    action_modifiers: Dict[str, float] = field(default_factory=lambda: {
        "like": 1.0,
        "comment": 2.0,
        "share": 3.0,
        "visit": 1.0,
    })
    
    # Recency decay half-life in hours
    decay_half_life_hours: float = 72.0  # 3 days
    
    # Multiplier for buying committee detection
    committee_multiplier: float = 1.5
    
    # Thresholds for intent labels
    high_threshold: float = 70.0
    medium_threshold: float = 30.0
