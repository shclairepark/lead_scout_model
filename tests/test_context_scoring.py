"""
Tests for Context-Aware Scoring components.
"""
import pytest
import numpy as np
import torch
from unittest.mock import MagicMock
from datetime import datetime

from src.context import SenderProfile, SemanticMatcher, AttentionSignalWeighter
from src.signals import SignalEvent, SignalType, SignalSource
from src.enrichment import EnrichedLead, EnrichedCompany, Industry

@pytest.fixture
def sender_profile():
    np.random.seed(42)  # Stable embedding
    return SenderProfile(
        name="TestSecurity",
        description="Cybersecurity for Enterprise",
        value_props=["Zero Trust", "AI Security"],
        target_industries=["security", "fintech"],
        target_roles=["CISO"]
    )

@pytest.fixture
def attention_weighter():
    torch.manual_seed(42)
    return AttentionSignalWeighter(embed_dim=128, num_heads=4)

class TestSemanticMatcher:
    
    def test_semantic_match_high(self, sender_profile):
        """Test high match for target industry."""
        matcher = SemanticMatcher(sender_profile)
        
        # Lead in Security industry (Target)
        lead = MagicMock(spec=EnrichedLead)
        lead.company = MagicMock(spec=EnrichedCompany)
        lead.company.industry = Industry.SECURITY
        
        score = matcher.calculate_fit_score(lead)
        # Should be high because simulations align target industries
        assert score > 0.7
        
    def test_semantic_match_low(self, sender_profile):
        """Test low match for unrelated industry."""
        matcher = SemanticMatcher(sender_profile)
        
        # Lead in Retail industry (Not Target)
        lead = MagicMock(spec=EnrichedLead)
        lead.company = MagicMock(spec=EnrichedCompany)
        lead.company.industry = Industry.ECOMMERCE
        
        score = matcher.calculate_fit_score(lead)
        # Should be lower (random noise vs aligned noise)
        # Note: Simulation Logic is probabilistic, but seeded roughly
        assert score < 0.8
        
class TestAttentionSignalWeighter:
    
    def test_attention_dimensions(self, sender_profile, attention_weighter):
        """Verify attention outputs weights for all signals."""
        signals = [
            SignalEvent(SignalType.DEMO_REQUEST, "u1", datetime.now(), SignalSource.LINKEDIN, {}),
            SignalEvent(SignalType.CONTENT_ENGAGEMENT, "u1", datetime.now(), SignalSource.LINKEDIN, {}),
        ]
        
        weights = attention_weighter(sender_profile, signals)
        
        assert len(weights) == 2
        assert SignalType.DEMO_REQUEST.value in [s.type.value for s in weights.keys()]
        
    def test_empty_signals(self, sender_profile, attention_weighter):
        """Handle empty signal list safely."""
        weights = attention_weighter(sender_profile, [])
        assert weights == {}

    def test_signal_weighing_logic(self, sender_profile, attention_weighter):
        """Verify high intent signals get varying weights."""
        signals = [
            # High Value Signal
            SignalEvent(SignalType.DEMO_REQUEST, "u1", datetime.now(), SignalSource.LINKEDIN, {}),
            # Low Value Signal
            SignalEvent(SignalType.PROFILE_VISIT, "u1", datetime.now(), SignalSource.LINKEDIN, {}),
        ]
        
        weights = attention_weighter(sender_profile, signals)
        
        # Extract weights
        demo_weight = next(w for s, w in weights.items() if s.type == SignalType.DEMO_REQUEST)
        visit_weight = next(w for s, w in weights.items() if s.type == SignalType.PROFILE_VISIT)
        
        # Current logic manually boosts DEMO_REQUEST in embedding, so it should attract more attention
        assert demo_weight != visit_weight
