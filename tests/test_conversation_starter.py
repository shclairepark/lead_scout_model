"""
Tests for Agent 3.5B: Conversation Starter

TDD Specs from Agents.md:
- Test 1: Signal-Based Personalization
- Test 2: Role-Based Messaging
"""

import pytest
from datetime import datetime

from src.engagement import ConversationStarter, OutreachMessage
from src.enrichment import EnrichedLead, EnrichedContact, EnrichedCompany, SeniorityLevel
from src.signals import SignalEvent, SignalType, SignalSource


class TestConversationStarter:
    """Tests for Conversation Starter."""
    
    def setup_method(self):
        self.starter = ConversationStarter()
        self.lead = EnrichedLead(
            user_id="u1",
            contact=EnrichedContact(
                user_id="u1", 
                name="Jane Doe", 
                seniority_level=SeniorityLevel.VP,
                title="VP of Sales"
            ),
            company=EnrichedCompany(company_id="c1", name="Acme")
        )
    
    def test_signal_based_personalization(self):
        """Test 1: Signal-Based Personalization (e.g. funding)."""
        signals = [
            SignalEvent(
                type=SignalType.FUNDING_ROUND,
                user_id="c1",
                timestamp=datetime.now(),
                source=SignalSource.CRUNCHBASE,
                data={"round_type": "series_a"},
                strength=0.9
            )
        ]
        
        message = self.starter.generate_message(self.lead, signals)
        
        # Check for personalized hook
        assert "Series A funding" in message.body
        assert message.context_used["signal_type"] == "funding_round"
    
    def test_engagement_personalization(self):
        """Test personalization for engagement signals."""
        signals = [
            SignalEvent(
                type=SignalType.CONTENT_ENGAGEMENT,
                user_id="u1",
                timestamp=datetime.now(),
                source=SignalSource.LINKEDIN,
                data={"event_type": "share"},
                strength=0.8
            )
        ]
        
        message = self.starter.generate_message(self.lead, signals)
        
        assert "share" in message.body
        assert "recent post" in message.body
    
    def test_role_based_messaging_executive(self):
        """Test 2: Role-Based Messaging (Executive)."""
        # Executive lead (VP) from setup
        signals = [
            SignalEvent(type=SignalType.PROFILE_VISIT, user_id="u1", timestamp=datetime.now(), source=SignalSource.LINKEDIN, strength=0.5)
        ]
        
        message = self.starter.generate_message(self.lead, signals)
        
        # Executive value prop: ROI/Strategic
        assert "cut logical costs" in message.body
        assert "doubling pipeline" in message.body
    
    def test_role_based_messaging_manager(self):
        """Test Role-Based Messaging (Manager)."""
        manager_lead = EnrichedLead(
            user_id="u2",
            contact=EnrichedContact(
                user_id="u2", 
                name="Bob Manager", 
                seniority_level=SeniorityLevel.MANAGER,
                title="Sales Manager"
            ),
            company=EnrichedCompany(company_id="c2", name="TechCo")
        )
        
        signals = [
            SignalEvent(type=SignalType.PROFILE_VISIT, user_id="u2", timestamp=datetime.now(), source=SignalSource.LINKEDIN, strength=0.5)
        ]
        
        message = self.starter.generate_message(manager_lead, signals)
        
        # Operational value prop
        assert "automates signal collection" in message.body
        assert "focus on closing" in message.body
    
    def test_default_fallback(self):
        """Test fallback when no strong signal."""
        message = self.starter.generate_message(self.lead, []) # Empty signals
        
        assert "Saw we're both in the SaaS space" in message.body
