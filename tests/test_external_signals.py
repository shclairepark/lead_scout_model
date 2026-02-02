"""
Tests for Agent 0B: External Signal Aggregator

TDD Specs from Agents.md:
- Test 1: Funding Detection
- Test 2: Role Change Detection
- Test 3: Event Signal
"""

import pytest
from datetime import datetime
from src.signals import ExternalSignalAggregator, SignalEvent
from src.signals.signal_event import SignalType, SignalSource


class TestFundingDetection:
    """Test 1: Funding Detection."""
    
    def setup_method(self):
        self.aggregator = ExternalSignalAggregator()
    
    def test_parse_funding_event(self):
        """Input: Crunchbase/LinkedIn funding announcement
        Expected: SignalEvent with company_id, funding_amount, round_type
        """
        payload = {
            "company_id": "company:acme-corp",
            "funding_amount": 10_000_000,
            "round_type": "series_a",
            "timestamp": "2026-02-01T12:00:00",
            "investor_names": ["Sequoia", "a16z"],
        }
        
        signal = self.aggregator.parse_funding_event(payload)
        
        assert isinstance(signal, SignalEvent)
        assert signal.type == SignalType.FUNDING_ROUND
        assert signal.company_id == "company:acme-corp"
        assert signal.data["funding_amount"] == 10_000_000
        assert signal.data["round_type"] == "series_a"
        assert signal.source == SignalSource.CRUNCHBASE
    
    def test_funding_round_strength_increases_with_stage(self):
        """Later funding rounds should have higher strength."""
        seed = self.aggregator.parse_funding_event({
            "company_id": "company1",
            "funding_amount": 1_000_000,
            "round_type": "seed",
        })
        
        aggregator2 = ExternalSignalAggregator()
        series_b = aggregator2.parse_funding_event({
            "company_id": "company2",
            "funding_amount": 50_000_000,
            "round_type": "series_b",
        })
        
        assert series_b.strength > seed.strength
    
    def test_funding_missing_fields_raises_error(self):
        """Missing required fields should raise ValueError."""
        with pytest.raises(ValueError, match="Missing required fields"):
            self.aggregator.parse_funding_event({
                "company_id": "company1",
                # Missing funding_amount and round_type
            })


class TestRoleChangeDetection:
    """Test 2: Role Change Detection."""
    
    def setup_method(self):
        self.aggregator = ExternalSignalAggregator()
    
    def test_parse_role_change(self):
        """Input: Job title update notification
        Expected: SignalEvent with new_title, previous_title, start_date
        """
        payload = {
            "user_id": "urn:li:person:jane123",
            "new_title": "VP of Engineering",
            "previous_title": "Director of Engineering",
            "start_date": "2026-01-15T00:00:00",
            "company_id": "company:techcorp",
        }
        
        signal = self.aggregator.parse_role_change(payload)
        
        assert signal.type == SignalType.ROLE_CHANGE
        assert signal.user_id == "urn:li:person:jane123"
        assert signal.data["new_title"] == "VP of Engineering"
        assert signal.data["previous_title"] == "Director of Engineering"
        assert signal.data["start_date"] == "2026-01-15T00:00:00"
        assert signal.source == SignalSource.LINKEDIN
    
    def test_role_seniority_detection(self):
        """Test seniority level detection from title."""
        c_level = self.aggregator.parse_role_change({
            "user_id": "user1",
            "new_title": "Chief Technology Officer",
        })
        assert c_level.data["seniority_level"] == "c_level"
        
        aggregator2 = ExternalSignalAggregator()
        vp = aggregator2.parse_role_change({
            "user_id": "user2",
            "new_title": "VP of Sales",
        })
        assert vp.data["seniority_level"] == "vp"
        
        aggregator3 = ExternalSignalAggregator()
        director = aggregator3.parse_role_change({
            "user_id": "user3",
            "new_title": "Director of Marketing",
        })
        assert director.data["seniority_level"] == "director"
    
    def test_c_level_higher_strength_than_ic(self):
        """C-level roles should have higher signal strength."""
        cto = self.aggregator.parse_role_change({
            "user_id": "user1",
            "new_title": "CTO",
        })
        
        aggregator2 = ExternalSignalAggregator()
        engineer = aggregator2.parse_role_change({
            "user_id": "user2",
            "new_title": "Software Engineer",
        })
        
        assert cto.strength > engineer.strength


class TestEventSignal:
    """Test 3: Event Signal."""
    
    def setup_method(self):
        self.aggregator = ExternalSignalAggregator()
    
    def test_parse_event_signal(self):
        """Input: Event registration webhook
        Expected: SignalEvent with event_name, event_type, attendee_id
        """
        payload = {
            "attendee_id": "urn:li:person:attendee456",
            "event_name": "SaaS Growth Summit 2026",
            "event_type": "conference",
            "timestamp": "2026-02-01T09:00:00",
            "company_id": "company:startupxyz",
        }
        
        signal = self.aggregator.parse_event_signal(payload)
        
        assert signal.type == SignalType.EVENT_ATTENDANCE
        assert signal.user_id == "urn:li:person:attendee456"
        assert signal.data["event_name"] == "SaaS Growth Summit 2026"
        assert signal.data["event_type"] == "conference"
        assert signal.data["attendee_id"] == "urn:li:person:attendee456"
        assert signal.source == SignalSource.EVENT_PLATFORM
    
    def test_conference_higher_strength_than_webinar(self):
        """Conference attendance should have higher strength than webinar."""
        conference = self.aggregator.parse_event_signal({
            "attendee_id": "user1",
            "event_name": "Tech Conference",
            "event_type": "conference",
        })
        
        aggregator2 = ExternalSignalAggregator()
        webinar = aggregator2.parse_event_signal({
            "attendee_id": "user2",
            "event_name": "Weekly Webinar",
            "event_type": "webinar",
        })
        
        assert conference.strength > webinar.strength
    
    def test_event_missing_fields_raises_error(self):
        """Missing required fields should raise ValueError."""
        with pytest.raises(ValueError, match="Missing required fields"):
            self.aggregator.parse_event_signal({
                "attendee_id": "user1",
                # Missing event_name and event_type
            })


class TestSignalsByCompany:
    """Test retrieving signals by company."""
    
    def test_get_signals_by_company(self):
        """Get all signals for a specific company."""
        aggregator = ExternalSignalAggregator()
        
        # Add signals for different companies
        aggregator.parse_funding_event({
            "company_id": "company:acme",
            "funding_amount": 5_000_000,
            "round_type": "seed",
        })
        aggregator.parse_role_change({
            "user_id": "user1",
            "new_title": "CTO",
            "company_id": "company:acme",
        })
        aggregator.parse_funding_event({
            "company_id": "company:other",
            "funding_amount": 10_000_000,
            "round_type": "series_a",
        })
        
        acme_signals = aggregator.get_signals_by_company("company:acme")
        
        assert len(acme_signals) == 2
        assert all(s.company_id == "company:acme" for s in acme_signals)
