"""
End-to-End Pipeline Tests.

Runs the full refactored pipeline on synthetic data to verify 
overall system integration without mocking internal components.
"""
import pytest
from datetime import datetime
from src.pipeline import PipelineEngine, SystemConfig
from src.context import SenderProfile
from src.signals import SignalEvent, SignalType, SignalSource

class TestE2EPipeline:
    
    @pytest.fixture
    def setup_pipeline(self):
        profile = SenderProfile(
            name="E2ETestCorp",
            description="Deep Tech AI",
            value_props=["AGI", "Efficiency"],
            target_industries=["ai_ml"],
            target_roles=["cto"]
        )
        engine = PipelineEngine(profile)
        return engine

    def test_end_to_end_high_fit(self, setup_pipeline):
        """
        Scenario: High Fit (Tech Industry) + High Intent (Demo Request)
        Expectation: ENGAGE
        """
        engine = setup_pipeline
        
        # Lead Profile
        lead_data = {
            "full_name": "Alice Tech",
            "title": "CTO",
            "company_name": "AI Startup",
            "company_domain": "ai.example.com",
            "industry": "ai_ml",
            "company_size": 50
        }
        
        # Signals
        signals = [
            SignalEvent(SignalType.DEMO_REQUEST, "u2", datetime.now(), SignalSource.LINKEDIN, {}),
            SignalEvent(SignalType.FUNDING_ROUND, "u2", datetime.now(), SignalSource.LINKEDIN, {})
        ]
        
        # Execute
        result = engine.process_lead("u_e2e_1", lead_data, signals)
        
        # Verify
        assert result['decision']['should_engage'] is True
        assert result['intent']['score'] > 30
        assert result['draft'] is not None

    def test_end_to_end_low_fit(self, setup_pipeline):
        """
        Scenario: Low Fit (Agriculture) + Low Intent (Single Visit)
        Expectation: SKIP
        """
        engine = setup_pipeline
        
        # Lead Profile
        lead_data = {
            "full_name": "Bob Farmer",
            "title": "Manager",
            "company_name": "FarmCo",
            "company_domain": "farm.example.com",
            "industry": "agriculture",
            "company_size": 100
        }
        
        # Signals
        signals = [
            SignalEvent(SignalType.PRICING_PAGE_VISIT, "u3", datetime.now(), SignalSource.LINKEDIN, {})
        ]
        
        # Execute
        result = engine.process_lead("u_e2e_2", lead_data, signals)
        
        # Verify
        assert result['decision']['should_engage'] is False
