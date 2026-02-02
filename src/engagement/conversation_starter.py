"""
Agent 3.5B: Conversation Starter

Generates contextual LinkedIn outreach messages based on detected signals.
- Signal-based personalization (hooks)
- Role-based value propositions
"""

from typing import List, Optional, Dict, Any

from .data_classes import OutreachMessage
from ..signals.signal_event import SignalEvent
from ..enrichment.data_classes import EnrichedLead, SeniorityLevel


class ConversationStarter:
    """
    Conversation Starter (Agent 3.5B)
    
    Generates personalized outreach messages using templates and signal context.
    """
    
    def generate_message(
        self,
        lead: EnrichedLead,
        signals: List[SignalEvent]
    ) -> OutreachMessage:
        """
        Generate a contextual outreach message.
        
        Args:
            lead: Enriched lead data
            signals: List of lead's recent signals
            
        Returns:
            OutreachMessage with body and subject
        """
        # 1. Select opening hook based on strongest recent signal
        primary_signal = sorted(signals, key=lambda s: s.strength, reverse=True)[0] if signals else None
        hook = self._get_opening_hook(primary_signal)
        
        # 2. Select value prop based on role/seniority
        role_context = self._get_value_proposition(lead)
        
        # 3. Assemble message
        first_name = lead.contact.name.split(" ")[0] if lead.contact and lead.contact.name else "there"
        company_name = lead.company.name if lead.company else "your company"
        
        body = (
            f"Hi {first_name},\n\n"
            f"{hook}\n\n"
            f"{role_context}\n\n"
            f"Worth a quick chat?\n\n"
            f"Best,"
        )
        
        return OutreachMessage(
            body=body,
            context_used={
                "signal_type": primary_signal.type.value if primary_signal else "none",
                "role_level": lead.contact.seniority_level.value if lead.contact else "unknown"
            }
        )
    
    def _get_opening_hook(self, signal: Optional[SignalEvent]) -> str:
        """Generate opening line based on signal."""
        if not signal:
            return "Saw we're both in the SaaS space."
            
        stype = signal.type.value
        data = signal.data or {}
        
        if stype == "content_engagement":
            action = data.get("event_type", "post")
            return f"Saw you {action}ed our recent post on LinkedIn."
            
        elif stype == "profile_visit":
            return "Thanks for stopping by my profile recently."
            
        elif stype == "funding_round":
            round_type = str(data.get("round_type", "")).replace("_", " ").title()
            return f"Huge congrats on the {round_type} funding round!"
            
        elif stype == "role_change":
            new_title = data.get("new_title", "new role")
            return f"Congrats on the new role as {new_title}!"
            
        elif stype == "event_attendance":
            event = data.get("event_name", "the event")
            return f"Saw you're also attending {event}."
            
        elif stype == "demo_request":
             return "Thanks for requesting a demo with us."
             
        return "I've been following your work at {company}."

    def _get_value_proposition(self, lead: EnrichedLead) -> str:
        """Generate value prop based on role."""
        if not lead.contact:
            return "We help companies scale their outbound efficiency."
            
        level = lead.contact.seniority_level
        
        if level in [SeniorityLevel.C_LEVEL, SeniorityLevel.VP]:
            # Strategic/ROI focus
            return "I help leaders automate their GTM motion to cut logical costs by 40% while doubling pipeline."
            
        elif level in [SeniorityLevel.DIRECTOR, SeniorityLevel.MANAGER]:
            # Operational/Efficiency focus
            return "We built a tool that automates signal collection so your team can focus on closing, not researching."
            
        else:
            # Functional/Utility focus
            return "Our platform handles the boring data entry parts of prospecting for you."
