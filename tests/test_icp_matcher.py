"""
Tests for Agent 1.5B: ICP Matcher

TDD Specs from Agents.md:
- Test 1: Company Size Match
- Test 2: Industry Alignment
- Test 3: Authority Detection
- Test 4: Overall ICP Score
"""

import pytest
from src.enrichment import (
    ICPMatcher,
    ICPConfig,
    EnrichedCompany,
    EnrichedContact,
    EnrichedLead,
)
from src.enrichment.data_classes import SeniorityLevel, Industry


class TestCompanySizeMatch:
    """Test 1: Company Size Match."""
    
    def setup_method(self):
        self.matcher = ICPMatcher()
    
    def test_size_perfect_match(self):
        """Input: Company with 150 employees, ICP range [50, 500]
        Expected: size_score = 1.0 (perfect match)
        """
        score = self.matcher.score_company_size(size=150, size_range=(50, 500))
        assert score == 1.0
    
    def test_size_at_boundaries(self):
        """Test size at exact boundaries."""
        # At minimum
        assert self.matcher.score_company_size(50, (50, 500)) == 1.0
        # At maximum
        assert self.matcher.score_company_size(500, (50, 500)) == 1.0
    
    def test_size_below_range(self):
        """Size below range gets partial score."""
        score = self.matcher.score_company_size(25, (50, 500))
        assert 0 < score < 1.0
        assert score == 0.5  # 25/50 = 0.5
    
    def test_size_above_range(self):
        """Size above range gets partial score."""
        score = self.matcher.score_company_size(1000, (50, 500))
        assert 0 < score < 1.0
        assert score == 0.5  # 500/1000 = 0.5
    
    def test_size_zero(self):
        """Zero size returns 0."""
        assert self.matcher.score_company_size(0) == 0.0


class TestIndustryAlignment:
    """Test 2: Industry Alignment."""
    
    def setup_method(self):
        self.matcher = ICPMatcher()
    
    def test_industry_match(self):
        """Input: SaaS company, ICP industries = ["SaaS", "FinTech"]
        Expected: industry_score = 1.0
        """
        score = self.matcher.score_industry(
            industry=Industry.SAAS,
            target_industries=["saas", "fintech"]
        )
        assert score == 1.0
    
    def test_industry_no_match(self):
        """Non-matching industry returns 0."""
        score = self.matcher.score_industry(
            industry=Industry.ECOMMERCE,
            target_industries=["saas", "fintech"]
        )
        assert score == 0.0
    
    def test_industry_case_insensitive(self):
        """Industry matching is case insensitive."""
        score = self.matcher.score_industry(
            industry=Industry.FINTECH,
            target_industries=["FINTECH", "SAAS"]
        )
        assert score == 1.0


class TestAuthorityDetection:
    """Test 3: Authority Detection."""
    
    def setup_method(self):
        self.matcher = ICPMatcher()
    
    def test_authority_vp(self):
        """Input: Title = "VP of Engineering"
        Expected: authority_level = "decision_maker", authority_score = 0.9
        """
        authority_level, authority_score = self.matcher.score_authority(
            title="VP of Engineering"
        )
        assert authority_level == "decision_maker"
        assert authority_score == 0.9
    
    def test_authority_c_level(self):
        """C-level should have highest score."""
        authority_level, authority_score = self.matcher.score_authority(
            title="Chief Technology Officer"
        )
        assert authority_level == "decision_maker"
        assert authority_score == 1.0
    
    def test_authority_director(self):
        """Director should be decision maker."""
        authority_level, authority_score = self.matcher.score_authority(
            title="Director of Sales"
        )
        assert authority_level == "decision_maker"
        assert authority_score == 0.8
    
    def test_authority_individual_contributor(self):
        """IC should be influencer with low score."""
        authority_level, authority_score = self.matcher.score_authority(
            title="Software Engineer"
        )
        assert authority_level == "influencer"
        assert authority_score == 0.3
    
    def test_authority_from_seniority_level(self):
        """Can use pre-detected seniority level."""
        authority_level, authority_score = self.matcher.score_authority(
            seniority_level=SeniorityLevel.VP
        )
        assert authority_level == "decision_maker"
        assert authority_score == 0.9


class TestOverallICPScore:
    """Test 4: Overall ICP Score."""
    
    def test_icp_score_ideal_lead(self):
        """Input: Fully enriched lead
        Expected: Weighted icp_score between 0-100
        """
        matcher = ICPMatcher(config=ICPConfig(
            size_range=(50, 500),
            target_industries=["saas"],
        ))
        
        company = EnrichedCompany(
            company_id="company:ideal",
            name="Ideal Company",
            size=200,
            industry=Industry.SAAS,
            funding_stage="series_b",
        )
        
        contact = EnrichedContact(
            user_id="urn:li:person:vp",
            name="VP of Sales",
            title="VP of Sales",
            seniority_level=SeniorityLevel.VP,
        )
        
        lead = EnrichedLead(
            user_id="urn:li:person:ideal",
            company=company,
            contact=contact,
        )
        
        result = matcher.calculate_icp_score(lead=lead)
        
        assert "icp_score" in result
        assert 0 <= result["icp_score"] <= 100
        assert result["icp_score"] >= 80  # High score for ideal lead
        assert "breakdown" in result
        assert result["authority_level"] == "decision_maker"
    
    def test_icp_score_poor_lead(self):
        """Poor fit lead should have low score."""
        matcher = ICPMatcher(config=ICPConfig(
            size_range=(50, 500),
            target_industries=["saas"],
        ))
        
        company = EnrichedCompany(
            company_id="company:poor",
            name="Poor Fit",
            size=10,  # Too small
            industry=Industry.ECOMMERCE,  # Wrong industry
        )
        
        contact = EnrichedContact(
            user_id="urn:li:person:ic",
            name="Engineer",
            title="Junior Developer",
            seniority_level=SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
        )
        
        lead = EnrichedLead(
            user_id="urn:li:person:poor",
            company=company,
            contact=contact,
        )
        
        result = matcher.calculate_icp_score(lead=lead)
        
        assert result["icp_score"] < 50  # Low score
        assert result["authority_level"] == "influencer"
    
    def test_icp_score_breakdown(self):
        """Verify breakdown includes all dimensions."""
        matcher = ICPMatcher()
        
        company = EnrichedCompany(
            company_id="company:test",
            name="Test Co",
            size=100,
            industry=Industry.SAAS,
        )
        
        result = matcher.calculate_icp_score(company=company)
        
        breakdown = result["breakdown"]
        assert "size" in breakdown
        assert "industry" in breakdown
        assert "tech_stack" in breakdown
        assert "funding" in breakdown
        assert "authority" in breakdown


class TestICPConfig:
    """Test ICP configuration."""
    
    def test_custom_config(self):
        """Test matcher with custom config."""
        config = ICPConfig(
            size_range=(100, 1000),
            target_industries=["fintech", "security"],
            target_tech_stack=["Python", "Kubernetes"],
            decision_maker_levels=["c_level", "vp"],
        )
        
        matcher = ICPMatcher(config=config)
        
        # Size 500 is in range
        assert matcher.score_company_size(500) == 1.0
        
        # Fintech matches
        assert matcher.score_industry(Industry.FINTECH) == 1.0
    
    def test_config_validation(self):
        """Test config weight validation."""
        valid_config = ICPConfig()
        assert valid_config.validate() is True
