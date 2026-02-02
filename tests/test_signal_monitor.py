"""
Tests for Agent 0A: LinkedIn Signal Monitor

TDD Specs from Agents.md:
- Test 1: Engagement Detection
- Test 2: Profile Visit Tracking  
- Test 3: Signal Aggregation
"""

import pytest
from datetime import datetime, timedelta
from src.signals import LinkedInSignalMonitor, SignalEvent
from src.signals.signal_event import SignalType, SignalSource


class TestEngagementDetection:
    """Test 1: Engagement Detection - Parse LinkedIn webhook payloads."""
    
    def setup_method(self):
        """Fresh monitor for each test."""
        self.monitor = LinkedInSignalMonitor()
    
    def test_parse_like_event(self):
        """Input: LinkedIn webhook payload (like event)
        Expected: Parsed SignalEvent with type='content_engagement', user_id, timestamp
        """
        payload = {
            "event_type": "like",
            "user_id": "urn:li:person:abc123",
            "post_id": "urn:li:post:xyz789",
            "timestamp": "2026-02-02T10:00:00",
        }
        
        signal = self.monitor.parse_engagement(payload)
        
        assert isinstance(signal, SignalEvent)
        assert signal.type == SignalType.CONTENT_ENGAGEMENT
        assert signal.user_id == "urn:li:person:abc123"
        assert signal.data["event_type"] == "like"
        assert signal.data["post_id"] == "urn:li:post:xyz789"
        assert signal.source == SignalSource.LINKEDIN
    
    def test_parse_comment_event_higher_strength(self):
        """Comments should have higher signal strength than likes."""
        like_payload = {
            "event_type": "like",
            "user_id": "user1",
            "post_id": "post1",
        }
        comment_payload = {
            "event_type": "comment",
            "user_id": "user2",
            "post_id": "post2",
        }
        
        like_signal = self.monitor.parse_engagement(like_payload)
        comment_signal = self.monitor.parse_engagement(comment_payload)
        
        assert comment_signal.strength > like_signal.strength
    
    def test_parse_share_event_highest_strength(self):
        """Shares should have highest signal strength."""
        payload = {
            "event_type": "share",
            "user_id": "user1",
            "post_id": "post1",
        }
        
        signal = self.monitor.parse_engagement(payload)
        
        assert signal.strength == 0.9  # Highest for shares
    
    def test_missing_required_fields_raises_error(self):
        """Missing required fields should raise ValueError."""
        with pytest.raises(ValueError, match="Missing required fields"):
            self.monitor.parse_engagement({"event_type": "like"})


class TestProfileVisitTracking:
    """Test 2: Profile Visit Tracking."""
    
    def setup_method(self):
        self.monitor = LinkedInSignalMonitor()
    
    def test_parse_profile_visit(self):
        """Input: Profile view notification
        Expected: SignalEvent with visitor LinkedIn URL, visit count, recency
        """
        payload = {
            "visitor_id": "urn:li:person:visitor123",
            "visitor_url": "https://linkedin.com/in/johndoe",
            "visit_count": 3,
            "timestamp": datetime.now().isoformat(),
        }
        
        signal = self.monitor.parse_profile_visit(payload)
        
        assert signal.type == SignalType.PROFILE_VISIT
        assert signal.user_id == "urn:li:person:visitor123"
        assert signal.data["visitor_url"] == "https://linkedin.com/in/johndoe"
        assert signal.data["visit_count"] == 3
        assert signal.data["recency"] == "today"
    
    def test_visit_count_affects_strength(self):
        """Higher visit count should increase signal strength."""
        single_visit = self.monitor.parse_profile_visit({
            "visitor_id": "user1",
            "visitor_url": "https://linkedin.com/in/test1",
            "visit_count": 1,
        })
        
        # Clear and create new monitor for fresh test
        monitor2 = LinkedInSignalMonitor()
        multiple_visits = monitor2.parse_profile_visit({
            "visitor_id": "user2",
            "visitor_url": "https://linkedin.com/in/test2",
            "visit_count": 5,
        })
        
        assert multiple_visits.strength > single_visit.strength
    
    def test_recency_categories(self):
        """Test recency categorization (today, this_week, older)."""
        # Today
        today_signal = self.monitor.parse_profile_visit({
            "visitor_id": "user1",
            "visitor_url": "https://linkedin.com/in/test",
            "timestamp": datetime.now().isoformat(),
        })
        assert today_signal.data["recency"] == "today"
        
        # This week (3 days ago)
        three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
        week_signal = LinkedInSignalMonitor().parse_profile_visit({
            "visitor_id": "user2",
            "visitor_url": "https://linkedin.com/in/test2",
            "timestamp": three_days_ago,
        })
        assert week_signal.data["recency"] == "this_week"


class TestSignalAggregation:
    """Test 3: Signal Aggregation over time window."""
    
    def setup_method(self):
        self.monitor = LinkedInSignalMonitor()
    
    def test_aggregate_signals_empty(self):
        """No signals returns empty aggregation."""
        result = self.monitor.aggregate_signals("nonexistent_user")
        
        assert result["signals"] == []
        assert result["frequency_score"] == 0.0
        assert result["total_count"] == 0
    
    def test_aggregate_signals_with_data(self):
        """Input: Multiple signals from same prospect over 7 days
        Expected: Aggregated signal timeline with frequency score
        """
        user_id = "urn:li:person:prospect123"
        
        # Add multiple signals
        for i in range(5):
            self.monitor.parse_engagement({
                "event_type": "like",
                "user_id": user_id,
                "post_id": f"post_{i}",
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
            })
        
        result = self.monitor.aggregate_signals(user_id, window_days=7)
        
        assert result["total_count"] == 5
        assert len(result["signals"]) == 5
        assert result["frequency_score"] > 0
        assert result["frequency_score"] <= 1.0
        assert "content_engagement" in result["signal_types"]
        assert result["latest_timestamp"] is not None
    
    def test_aggregate_excludes_old_signals(self):
        """Signals outside window should be excluded."""
        user_id = "urn:li:person:test"
        
        # Add old signal (30 days ago)
        old_timestamp = (datetime.now() - timedelta(days=30)).isoformat()
        self.monitor.parse_engagement({
            "event_type": "like",
            "user_id": user_id,
            "post_id": "old_post",
            "timestamp": old_timestamp,
        })
        
        # Add recent signal
        self.monitor.parse_engagement({
            "event_type": "comment",
            "user_id": user_id,
            "post_id": "new_post",
            "timestamp": datetime.now().isoformat(),
        })
        
        result = self.monitor.aggregate_signals(user_id, window_days=7)
        
        assert result["total_count"] == 1  # Only recent signal
    
    def test_frequency_score_increases_with_more_signals(self):
        """More signals should increase frequency score."""
        user1 = "user_few"
        user2 = "user_many"
        
        # 2 signals for user1
        for i in range(2):
            self.monitor.parse_engagement({
                "event_type": "like",
                "user_id": user1,
                "post_id": f"post_{i}",
            })
        
        # 10 signals for user2
        monitor2 = LinkedInSignalMonitor()
        for i in range(10):
            monitor2.parse_engagement({
                "event_type": "like",
                "user_id": user2,
                "post_id": f"post_{i}",
            })
        
        result1 = self.monitor.aggregate_signals(user1)
        result2 = monitor2.aggregate_signals(user2)
        
        assert result2["frequency_score"] > result1["frequency_score"]
