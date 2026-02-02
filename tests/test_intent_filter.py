"""
Tests for Agent 3.5A: High Intent Filter

TDD Specs from Agents.md:
- Test 1: Intent Threshold
- Test 2: ICP Threshold
- Test 3: Exclusion Rules
- Test 4: Qualified Lead
"""

import pytest
from src.engagement import (
    HighIntentFilter,
    EngagementConfig,
    EngagementDecision,
    EngagementPriority
)
from src.scoring import IntentScore, IntentLabel
from src.enrichment import EnrichedLead, EnrichedCompany


class TestHighIntentFilter:
    """Tests for High Intent Filter."""
    
    def setup_method(self):
        self.config = EngagementConfig(
            min_intent_score=70.0,
            min_icp_score=80.0,
            competitors=["CompetitorX"],
            excluded_domains=["exclude-me.com"]
        )
        self.filter = HighIntentFilter(config=self.config)
        
        # Base fixtures
        self.lead = EnrichedLead(
            user_id="u1",
            company=EnrichedCompany(company_id="c1", name="Acme Corp", website="acme.com")
        )
    
    def test_intent_threshold_failure(self):
        """Test 1: Intent Threshold failure."""
        decision = self.filter.evaluate_lead(
            lead=self.lead,
            intent_score=IntentScore(score=65.0, label=IntentLabel.MEDIUM, signals_score=65),
            icp_score_val=90.0  # ICP passes
        )
        
        assert decision.should_engage is False
        assert "Intent Score" in decision.reason
    
    def test_icp_threshold_failure(self):
        """Test 2: ICP Threshold failure."""
        decision = self.filter.evaluate_lead(
            lead=self.lead,
            intent_score=IntentScore(score=85.0, label=IntentLabel.HIGH, signals_score=85),
            icp_score_val=75.0  # ICP fails (needs 80)
        )
        
        assert decision.should_engage is False
        assert "ICP Score" in decision.reason
    
    def test_exclusion_rule_competitor(self):
        """Test 3: Exclusion Rules (Competitor)."""
        competitor_lead = EnrichedLead(
            user_id="u2",
            company=EnrichedCompany(company_id="c2", name="CompetitorX Inc", website="competitorx.com")
        )
        
        decision = self.filter.evaluate_lead(
            lead=competitor_lead,
            intent_score=IntentScore(score=90.0, label=IntentLabel.HIGH, signals_score=90),
            icp_score_val=90.0
        )
        
        assert decision.should_engage is False
        assert "Competitor detected" in decision.reason
    
    def test_exclusion_rule_domain(self):
        """Test Exclusion Rules (Domain)."""
        excluded_lead = EnrichedLead(
            user_id="u3",
            company=EnrichedCompany(company_id="c3", name="Bad Domain", website="sub.exclude-me.com")
        )
        
        decision = self.filter.evaluate_lead(
            lead=excluded_lead,
            intent_score=IntentScore(score=90.0, label=IntentLabel.HIGH, signals_score=90),
            icp_score_val=90.0
        )
        
        assert decision.should_engage is False
        assert "Excluded domain" in decision.reason
    
    def test_qualified_lead(self):
        """Test 4: Qualified Lead (Passes all checks)."""
        decision = self.filter.evaluate_lead(
            lead=self.lead,
            intent_score=IntentScore(score=85.0, label=IntentLabel.HIGH, signals_score=85),
            icp_score_val=90.0
        )
        
        assert decision.should_engage is True
        assert decision.priority == EngagementPriority.HIGH
        assert "High Intent + High ICP Match" in decision.reason
