"""
Agent 0A: LinkedIn Signal Monitor

Continuously monitors buying signals from LinkedIn in real-time:
- Content engagement (likes, comments, shares)
- Profile visits
- Topic interactions
- Competitor content engagement
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

from .signal_event import SignalEvent, SignalType, SignalSource


class LinkedInSignalMonitor:
    """
    LinkedIn Signal Monitor (Agent 0A)
    
    Parses LinkedIn webhook payloads and aggregates signals
    to track prospect engagement over time.
    """
    
    def __init__(self):
        """Initialize the signal monitor with empty signal store."""
        # Store signals by user_id for aggregation
        self._signals: Dict[str, List[SignalEvent]] = defaultdict(list)
    
    def parse_engagement(self, payload: Dict[str, Any]) -> SignalEvent:
        """
        Parse a LinkedIn engagement event (like, comment, share).
        
        Args:
            payload: LinkedIn webhook payload containing:
                - event_type: "like" | "comment" | "share"
                - user_id: LinkedIn user URN
                - post_id: Post that was engaged with
                - timestamp: ISO format timestamp (optional)
                - user_name: Display name (optional)
                
        Returns:
            SignalEvent with type=CONTENT_ENGAGEMENT
            
        Raises:
            ValueError: If required fields are missing
        """
        self._validate_required_fields(payload, ["event_type", "user_id", "post_id"])
        
        # Determine signal strength based on engagement type
        engagement_strengths = {
            "like": 0.3,
            "comment": 0.7,
            "share": 0.9,
        }
        
        event_type = payload["event_type"]
        strength = engagement_strengths.get(event_type, 0.5)
        
        timestamp = self._parse_timestamp(payload.get("timestamp"))
        
        signal = SignalEvent(
            type=SignalType.CONTENT_ENGAGEMENT,
            user_id=payload["user_id"],
            timestamp=timestamp,
            source=SignalSource.LINKEDIN,
            data={
                "event_type": event_type,
                "post_id": payload["post_id"],
                "user_name": payload.get("user_name"),
            },
            company_id=payload.get("company_id"),
            strength=strength,
        )
        
        # Store signal for aggregation
        self._signals[payload["user_id"]].append(signal)
        
        return signal
    
    def parse_profile_visit(self, payload: Dict[str, Any]) -> SignalEvent:
        """
        Parse a LinkedIn profile view notification.
        
        Args:
            payload: Profile visit data containing:
                - visitor_id: LinkedIn user URN of visitor
                - visitor_url: LinkedIn profile URL
                - visit_count: Number of visits (optional, default 1)
                - timestamp: ISO format timestamp (optional)
                
        Returns:
            SignalEvent with type=PROFILE_VISIT, visitor URL, count, recency
        """
        self._validate_required_fields(payload, ["visitor_id", "visitor_url"])
        
        visit_count = payload.get("visit_count", 1)
        timestamp = self._parse_timestamp(payload.get("timestamp"))
        
        # Higher visit count = stronger signal
        strength = min(0.3 + (visit_count * 0.15), 1.0)
        
        # Calculate recency category
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
        if age_hours < 24:
            recency = "today"
        elif age_hours < 168:  # 7 days
            recency = "this_week"
        else:
            recency = "older"
        
        signal = SignalEvent(
            type=SignalType.PROFILE_VISIT,
            user_id=payload["visitor_id"],
            timestamp=timestamp,
            source=SignalSource.LINKEDIN,
            data={
                "visitor_url": payload["visitor_url"],
                "visit_count": visit_count,
                "recency": recency,
            },
            company_id=payload.get("company_id"),
            strength=strength,
        )
        
        self._signals[payload["visitor_id"]].append(signal)
        
        return signal
    
    def aggregate_signals(
        self, 
        user_id: str, 
        window_days: int = 7
    ) -> Dict[str, Any]:
        """
        Aggregate signals from a prospect over a time window.
        
        Args:
            user_id: LinkedIn user ID to aggregate signals for
            window_days: Number of days to look back (default 7)
            
        Returns:
            Aggregated signal data with:
                - signals: List of SignalEvent objects
                - frequency_score: Engagement frequency (0.0 to 1.0)
                - total_count: Number of signals
                - signal_types: Breakdown by type
                - latest_timestamp: Most recent signal
        """
        cutoff = datetime.now() - timedelta(days=window_days)
        
        # Filter signals within window
        user_signals = self._signals.get(user_id, [])
        recent_signals = [s for s in user_signals if s.timestamp >= cutoff]
        
        if not recent_signals:
            return {
                "signals": [],
                "frequency_score": 0.0,
                "total_count": 0,
                "signal_types": {},
                "latest_timestamp": None,
            }
        
        # Count by type
        type_counts: Dict[str, int] = defaultdict(int)
        for signal in recent_signals:
            type_counts[signal.type.value] += 1
        
        # Calculate frequency score (more signals = higher score, capped at 1.0)
        # Formula: 1 - e^(-count/5) gives diminishing returns
        import math
        frequency_score = 1 - math.exp(-len(recent_signals) / 5)
        
        # Sort by timestamp to get latest
        recent_signals.sort(key=lambda s: s.timestamp, reverse=True)
        
        return {
            "signals": recent_signals,
            "frequency_score": round(frequency_score, 3),
            "total_count": len(recent_signals),
            "signal_types": dict(type_counts),
            "latest_timestamp": recent_signals[0].timestamp,
        }
    
    def clear_signals(self, user_id: Optional[str] = None) -> None:
        """Clear stored signals for a user or all users."""
        if user_id:
            self._signals[user_id] = []
        else:
            self._signals.clear()
    
    def _validate_required_fields(
        self, 
        payload: Dict[str, Any], 
        required: List[str]
    ) -> None:
        """Validate that required fields are present in payload."""
        missing = [f for f in required if f not in payload or not payload[f]]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
    
    def _parse_timestamp(self, timestamp: Optional[str]) -> datetime:
        """Parse timestamp string or return current time."""
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return datetime.now()
