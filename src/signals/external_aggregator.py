"""
Agent 0B: External Signal Aggregator

Monitors business signals beyond LinkedIn:
- Funding round announcements
- Role/job changes
- Event attendance
- Group membership changes
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

from .signal_event import SignalEvent, SignalType, SignalSource


class ExternalSignalAggregator:
    """
    External Signal Aggregator (Agent 0B)
    
    Parses external business signals from Crunchbase, company websites,
    event platforms, and other sources to detect buying intent.
    """
    
    # Funding round signal strengths (larger rounds = stronger signal)
    FUNDING_STRENGTHS = {
        "pre_seed": 0.4,
        "seed": 0.5,
        "series_a": 0.7,
        "series_b": 0.8,
        "series_c": 0.9,
        "series_d": 0.95,
        "ipo": 1.0,
    }
    
    # Role change signal strengths (seniority matters)
    ROLE_STRENGTHS = {
        "c_level": 0.9,
        "vp": 0.8,
        "director": 0.7,
        "manager": 0.5,
        "individual_contributor": 0.3,
    }
    
    def __init__(self):
        """Initialize the external signal aggregator."""
        self._signals: Dict[str, List[SignalEvent]] = defaultdict(list)
    
    def parse_funding_event(self, payload: Dict[str, Any]) -> SignalEvent:
        """
        Parse a funding round announcement.
        
        Args:
            payload: Funding event data containing:
                - company_id: Company identifier
                - funding_amount: Amount raised (numeric)
                - round_type: "seed" | "series_a" | "series_b" | etc.
                - timestamp: ISO format timestamp (optional)
                - investor_names: List of investors (optional)
                - source_url: Link to announcement (optional)
                
        Returns:
            SignalEvent with type=FUNDING_ROUND, company_id, amount, round
        """
        self._validate_required_fields(payload, ["company_id", "funding_amount", "round_type"])
        
        round_type = payload["round_type"].lower().replace("-", "_").replace(" ", "_")
        strength = self.FUNDING_STRENGTHS.get(round_type, 0.5)
        
        timestamp = self._parse_timestamp(payload.get("timestamp"))
        
        signal = SignalEvent(
            type=SignalType.FUNDING_ROUND,
            user_id=payload.get("user_id", f"company:{payload['company_id']}"),
            timestamp=timestamp,
            source=SignalSource.CRUNCHBASE,
            data={
                "funding_amount": payload["funding_amount"],
                "round_type": round_type,
                "investor_names": payload.get("investor_names", []),
                "source_url": payload.get("source_url"),
            },
            company_id=payload["company_id"],
            strength=strength,
        )
        
        self._signals[signal.user_id].append(signal)
        return signal
    
    def parse_role_change(self, payload: Dict[str, Any]) -> SignalEvent:
        """
        Parse a job title/role change notification.
        
        Args:
            payload: Role change data containing:
                - user_id: LinkedIn user URN or identifier
                - new_title: New job title
                - previous_title: Previous job title (optional)
                - start_date: When the new role started (optional)
                - company_id: New company identifier (optional)
                
        Returns:
            SignalEvent with type=ROLE_CHANGE, new_title, previous_title, start_date
        """
        self._validate_required_fields(payload, ["user_id", "new_title"])
        
        # Determine seniority level from title
        new_title_lower = payload["new_title"].lower()
        seniority = self._detect_seniority(new_title_lower)
        strength = self.ROLE_STRENGTHS.get(seniority, 0.5)
        
        # Parse start date or use current time
        start_date = payload.get("start_date")
        if start_date:
            timestamp = self._parse_timestamp(start_date)
        else:
            timestamp = self._parse_timestamp(payload.get("timestamp"))
        
        signal = SignalEvent(
            type=SignalType.ROLE_CHANGE,
            user_id=payload["user_id"],
            timestamp=timestamp,
            source=SignalSource.LINKEDIN,
            data={
                "new_title": payload["new_title"],
                "previous_title": payload.get("previous_title"),
                "start_date": start_date,
                "seniority_level": seniority,
            },
            company_id=payload.get("company_id"),
            strength=strength,
        )
        
        self._signals[payload["user_id"]].append(signal)
        return signal
    
    def parse_event_signal(self, payload: Dict[str, Any]) -> SignalEvent:
        """
        Parse an event registration or attendance signal.
        
        Args:
            payload: Event data containing:
                - attendee_id: User identifier
                - event_name: Name of the event
                - event_type: "conference" | "webinar" | "workshop" | "meetup"
                - timestamp: Registration/attendance time (optional)
                - company_id: Attendee's company (optional)
                
        Returns:
            SignalEvent with type=EVENT_ATTENDANCE, event_name, event_type, attendee_id
        """
        self._validate_required_fields(payload, ["attendee_id", "event_name", "event_type"])
        
        # Event type determines signal strength
        event_strengths = {
            "conference": 0.8,
            "workshop": 0.7,
            "webinar": 0.5,
            "meetup": 0.4,
        }
        
        event_type = payload["event_type"].lower()
        strength = event_strengths.get(event_type, 0.5)
        
        timestamp = self._parse_timestamp(payload.get("timestamp"))
        
        signal = SignalEvent(
            type=SignalType.EVENT_ATTENDANCE,
            user_id=payload["attendee_id"],
            timestamp=timestamp,
            source=SignalSource.EVENT_PLATFORM,
            data={
                "event_name": payload["event_name"],
                "event_type": event_type,
                "attendee_id": payload["attendee_id"],
            },
            company_id=payload.get("company_id"),
            strength=strength,
        )
        
        self._signals[payload["attendee_id"]].append(signal)
        return signal
    
    def get_signals_by_company(self, company_id: str) -> List[SignalEvent]:
        """Get all signals for a specific company."""
        all_signals = []
        for signals in self._signals.values():
            for signal in signals:
                if signal.company_id == company_id:
                    all_signals.append(signal)
        return sorted(all_signals, key=lambda s: s.timestamp, reverse=True)
    
    def clear_signals(self, user_id: Optional[str] = None) -> None:
        """Clear stored signals for a user or all users."""
        if user_id:
            self._signals[user_id] = []
        else:
            self._signals.clear()
    
    def _detect_seniority(self, title: str) -> str:
        """Detect seniority level from job title."""
        title_lower = title.lower()
        
        # Check director first (before co-founder to avoid false match)
        if "director" in title_lower:
            return "director"
        
        if any(t in title_lower for t in ["ceo", "cto", "cfo", "coo", "chief", "founder", "co-founder"]):
            return "c_level"
        elif any(t in title_lower for t in ["vp", "vice president"]):
            return "vp"
        elif any(t in title_lower for t in ["manager", "lead", "head"]):
            return "manager"
        else:
            return "individual_contributor"
    
    def _validate_required_fields(
        self, 
        payload: Dict[str, Any], 
        required: List[str]
    ) -> None:
        """Validate that required fields are present in payload."""
        missing = [f for f in required if f not in payload or payload[f] is None]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
    
    def _parse_timestamp(self, timestamp: Optional[str]) -> datetime:
        """Parse timestamp string or return current time."""
        if timestamp:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return datetime.now()
