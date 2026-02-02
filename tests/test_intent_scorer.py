"""
Tests for Agent 2.5A: Intent Scorer

TDD Specs from Agents.md:
- Test 1: Recency Decay
- Test 2: Signal Strength Multipliers
- Test 3: Buying Committee Detection
- Test 4: Composite Intent Score
"""

import pytest
from datetime import datetime, timedelta

from src.scoring import IntentScorer, IntentScore, ScoringConfig
from src.scoring.data_classes import IntentLabel
from src.signals import SignalEvent, SignalType, SignalSource
from src.enrichment import EnrichedLead, EnrichedCompany


class TestRecencyDecay:
    """Test 1: Recency Decay."""
    
    def setup_method(self):
        self.scorer = IntentScorer()
    
    def test_recency_decay_calculation(self):
        """Input: Signal from 1 hour ago, Signal from 72 hours ago
        Expected: weight(1hr) > weight(72hr)
        """
        now = datetime.now()
        recent_ts = now - timedelta(hours=1)
        old_ts = now - timedelta(hours=72)
        
        recent_decay = self.scorer._calculate_decay(recent_ts)
        old_decay = self.scorer._calculate_decay(old_ts)
        
        # Decay at 1 hour should be near 1.0
        assert recent_decay > 0.95
        
        # Decay at 72 hours (half-life) should be 0.5
        assert abs(old_decay - 0.5) < 0.01
        
        # Recent should be stronger than old
        assert recent_decay > old_decay
    
    def test_recency_impacts_score(self):
        """Same signal should have lower score if older."""
        now = datetime.now()
        
        recent_signal = SignalEvent(
            type=SignalType.PROFILE_VISIT,
            user_id="u1",
            timestamp=now - timedelta(hours=1),
            source=SignalSource.LINKEDIN,
        )
        
        old_signal = SignalEvent(
            type=SignalType.PROFILE_VISIT,
            user_id="u1",
            timestamp=now - timedelta(hours=72),
            source=SignalSource.LINKEDIN,
        )
        
        recent_score = self.scorer.calculate_intent_score([recent_signal])
        old_score = self.scorer.calculate_intent_score([old_signal])
        
        assert recent_score.score > old_score.score


class TestSignalStrengthMultipliers:
    """Test 2: Signal Strength Multipliers."""
    
    def setup_method(self):
        self.scorer = IntentScorer()
    
    def test_signal_weights(self):
        """Different signal types have different weights."""
        now = datetime.now()
        
        # Profile visit (Base weight 8.0)
        visit = SignalEvent(
            type=SignalType.PROFILE_VISIT,
            user_id="u1",
            timestamp=now,
            source=SignalSource.LINKEDIN,
        )
        
        # Funding round (Base weight 15.0)
        funding = SignalEvent(
            type=SignalType.FUNDING_ROUND,
            user_id="c1",
            timestamp=now,
            source=SignalSource.CRUNCHBASE,
        )
        
        visit_score = self.scorer.calculate_intent_score([visit])
        funding_score = self.scorer.calculate_intent_score([funding])
        
        assert funding_score.score > visit_score.score
    
    def test_action_modifiers(self):
        """Action type (like vs share) modifies score."""
        now = datetime.now()
        
        like = SignalEvent(
            type=SignalType.CONTENT_ENGAGEMENT,
            user_id="u1",
            timestamp=now,
            source=SignalSource.LINKEDIN,
            data={"event_type": "like"},  # Modifier 1.0
        )
        
        share = SignalEvent(
            type=SignalType.CONTENT_ENGAGEMENT,
            user_id="u1",
            timestamp=now,
            source=SignalSource.LINKEDIN,
            data={"event_type": "share"},  # Modifier 3.0
        )
        
        like_score = self.scorer.calculate_intent_score([like])
        share_score = self.scorer.calculate_intent_score([share])
        
        # Share should be 3x stronger than like (base weights equal)
        # Allow small margin for floating point
        ratio = share_score.score / like_score.score
        assert 2.9 < ratio < 3.1


class TestBuyingCommitteeDetection:
    """Test 3: Buying Committee Detection."""
    
    def setup_method(self):
        self.scorer = IntentScorer()
        self.lead = EnrichedLead(
            user_id="urn:li:person:decision_maker",
            company=EnrichedCompany(company_id="company:acme", name="Acme"),
        )
    
    def test_committee_boost(self):
        """Input: Multiple engaged contacts from same company
        Expected: committee_boost = 1.5x
        """
        now = datetime.now()
        
        # Lead's own signal
        own_signal = SignalEvent(
            type=SignalType.PROFILE_VISIT,
            user_id="urn:li:person:decision_maker",
            timestamp=now,
            source=SignalSource.LINKEDIN,
            company_id="company:acme",
        )
        
        # Other colleagues' signals
        colleague_signals = [
            SignalEvent(
                type=SignalType.PROFILE_VISIT,
                user_id="urn:li:person:colleague1",
                timestamp=now,
                source=SignalSource.LINKEDIN,
                company_id="company:acme",
            ),
            SignalEvent(
                type=SignalType.CONTENT_ENGAGEMENT,
                user_id="urn:li:person:colleague2",
                timestamp=now,
                source=SignalSource.LINKEDIN,
                company_id="company:acme",
            )
        ]
        
        all_signals = [own_signal] + colleague_signals
        
        score = self.scorer.calculate_intent_score(
            signals=[own_signal],
            lead=self.lead,
            company_signals=all_signals
        )
        
        # Check committee factor applied
        assert score.committee_factor == 1.5  # 2 other colleagues = 1.5x
    
    def test_no_committee_boost(self):
        """No boost if only one person active."""
        now = datetime.now()
        
        own_signal = SignalEvent(
            type=SignalType.PROFILE_VISIT,
            user_id="urn:li:person:decision_maker",
            timestamp=now,
            source=SignalSource.LINKEDIN,
            company_id="company:acme",
        )
        
        score = self.scorer.calculate_intent_score(
            signals=[own_signal],
            lead=self.lead,
            company_signals=[own_signal]  # Only their own signal
        )
        
        assert score.committee_factor == 1.0


class TestCompositeIntentScore:
    """Test 4: Composite Intent Score."""
    
    def setup_method(self):
        self.scorer = IntentScorer()
    
    def test_composite_score_high_intent(self):
        """Test high intent scenario (HOT lead)."""
        now = datetime.now()
        
        signals = [
            # High value demo request
            SignalEvent(
                type=SignalType.EVENT_ATTENDANCE, # Demo request equiv
                user_id="u1",
                timestamp=now,
                source=SignalSource.LINKEDIN,
                data={"event_type": "demo_request"},
                strength=1.0,
            ),
            # Recent profile visit
            SignalEvent(
                type=SignalType.PROFILE_VISIT,
                user_id="u1",
                timestamp=now - timedelta(hours=2),
                source=SignalSource.LINKEDIN,
                strength=0.8,
            )
        ]
        
        # Update config to ensure demo request is weighted heavily
        self.scorer.config.signal_weights["event_attendance"] = 75.0
        
        result = self.scorer.calculate_intent_score(signals)
        
        assert result.label == IntentLabel.HIGH
        assert result.score > 70.0
    
    def test_composite_score_low_intent(self):
        """Test low intent scenario (Cold lead)."""
        now = datetime.now()
        
        signals = [
            # Old, weak signal
            SignalEvent(
                type=SignalType.CONTENT_ENGAGEMENT,
                user_id="u1",
                timestamp=now - timedelta(days=10), # Very old
                source=SignalSource.LINKEDIN,
                data={"event_type": "like"}, # Low weight
                strength=0.3,
            )
        ]
        
        result = self.scorer.calculate_intent_score(signals)
        
        assert result.label == IntentLabel.LOW
        assert result.score < 30.0
