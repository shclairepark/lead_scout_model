"""
Tests for the central PipelineEngine.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.pipeline import PipelineEngine, SystemConfig
from src.context import SenderProfile
from src.signals import SignalEvent
from src.enrichment import EnrichedLead

@pytest.fixture
def sender_profile():
    return SenderProfile(
        name="Test Sender",
        description="A great company",
        value_props=["Value"],
        target_industries=["tech"],
        target_roles=["ceo"]
    )

@pytest.fixture
def engine(sender_profile):
    return PipelineEngine(sender_profile)

class TestPipelineEngine:
    
    @patch('src.pipeline.engine.LeadEnricher')
    @patch('src.pipeline.engine.ICPMatcher')
    @patch('src.pipeline.engine.IntentScorer')
    @patch('src.pipeline.engine.SemanticMatcher')
    @patch('src.pipeline.engine.AttentionSignalWeighter')
    def test_process_lead_flow(self, mock_attn, mock_semantic, mock_intent, mock_icp, mock_enrich, engine):
        """Verify process_lead calls all components and aggregates results."""
        
        # Setup Mocks
        mock_enrich.return_value.enrich_lead.return_value = MagicMock(spec=EnrichedLead)
        
        mock_icp.return_value.calculate_icp_score.return_value = {
            'icp_score': 85.0, # High Generic
            'breakdown': {},
            'authority_level': 'decision_maker'
        }
        
        # Scorer Mock
        intent_res = MagicMock()
        intent_res.score = 50.0
        intent_res.label.value = "medium"
        mock_intent.return_value.calculate_intent_score.return_value = intent_res
        
        # Semantic Mock
        mock_semantic.return_value.calculate_fit_score.return_value = 0.9 # High Semantic
        
        # Attention Mock
        mock_attn.return_value.return_value = {MagicMock(spec=SignalEvent): 1.5}
        
        # Overwrite instances in engine with our mocks
        engine.enricher = mock_enrich.return_value
        engine.icp_matcher = mock_icp.return_value
        engine.scorer = mock_intent.return_value
        engine.semantic_matcher = mock_semantic.return_value
        engine.attention_weighter = mock_attn.return_value
        
        # Execute
        result = engine.process_lead("u1", {"name": "Test"}, [])
        
        # Assertions
        assert result['icp']['score'] == 85.0
        assert result['semantic']['score'] == 90.0 # 0.9 * 100
        assert result['intent']['score'] == 50.0
        # Decision Logic: Intent > 30 AND (ICP > 80 OR Semantic > 80)
        assert result['decision']['should_engage'] is True
        
    def test_decision_logic_low_intent(self, engine):
        """Test that low intent leads fail even if perfect fit."""
        # Using real components partly or mocking just the score values
        engine.scorer = MagicMock()
        engine.scorer.calculate_intent_score.return_value.score = 10.0 # Low
        
        engine.icp_matcher = MagicMock()
        engine.icp_matcher.calculate_icp_score.return_value = {'icp_score': 100.0, 'breakdown': {}, 'authority_level': 'high'}
        
        engine.semantic_matcher.calculate_fit_score = MagicMock(return_value=1.0)
        
        # Even with high fit, low intent should fail
        result = engine.process_lead("u1", {}, [])
        assert result['decision']['should_engage'] is False
