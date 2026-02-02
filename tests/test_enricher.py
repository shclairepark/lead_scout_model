"""
Tests for Agent 1.5A: Lead Enricher

TDD Specs from Agents.md:
- Test 1: Company Enrichment
- Test 2: Contact Enrichment
- Test 3: Social Graph Analysis
"""

import pytest
from src.enrichment import LeadEnricher, EnrichedCompany, EnrichedContact, SocialGraph
from src.enrichment.data_classes import SeniorityLevel, Industry


class TestCompanyEnrichment:
    """Test 1: Company Enrichment."""
    
    def setup_method(self):
        self.enricher = LeadEnricher()
    
    def test_enrich_company_basic(self):
        """Input: LinkedIn company URL
        Expected: EnrichedCompany with size, industry, tech_stack[]
        """
        company = self.enricher.enrich_company(
            linkedin_url="https://linkedin.com/company/acme-tech",
            name="Acme Technologies",
            size=150,
            industry="SaaS",
            tech_stack=["Python", "React", "AWS"],
        )
        
        assert isinstance(company, EnrichedCompany)
        assert company.size == 150
        assert company.industry == Industry.SAAS
        assert company.tech_stack == ["Python", "React", "AWS"]
        assert company.company_id == "company:acme-tech"
    
    def test_enrich_company_industry_detection(self):
        """Test industry detection from string."""
        saas_company = self.enricher.enrich_company(
            linkedin_url="https://linkedin.com/company/saas-corp",
            industry="Software as a Service",
        )
        assert saas_company.industry == Industry.SAAS
        
        fintech_company = self.enricher.enrich_company(
            linkedin_url="https://linkedin.com/company/fintech-inc",
            industry="Financial Technology",
        )
        assert fintech_company.industry == Industry.FINTECH
    
    def test_enrich_company_name_extraction(self):
        """Test company name extraction from URL."""
        company = self.enricher.enrich_company(
            linkedin_url="https://linkedin.com/company/cool-startup-inc"
        )
        assert company.name == "Cool Startup Inc"
    
    def test_enrich_company_missing_url_raises_error(self):
        """Missing URL should raise ValueError."""
        with pytest.raises(ValueError, match="linkedin_url is required"):
            self.enricher.enrich_company(linkedin_url="")


class TestContactEnrichment:
    """Test 2: Contact Enrichment."""
    
    def setup_method(self):
        self.enricher = LeadEnricher()
    
    def test_enrich_contact_basic(self):
        """Input: LinkedIn profile URL
        Expected: EnrichedContact with email, phone, seniority_level
        """
        contact = self.enricher.enrich_contact(
            linkedin_url="https://linkedin.com/in/john-doe",
            name="John Doe",
            email="john@acme.com",
            phone="+1-555-0123",
            title="VP of Engineering",
        )
        
        assert isinstance(contact, EnrichedContact)
        assert contact.email == "john@acme.com"
        assert contact.phone == "+1-555-0123"
        assert contact.seniority_level == SeniorityLevel.VP
    
    def test_enrich_contact_seniority_detection(self):
        """Test seniority detection from title."""
        cto = self.enricher.enrich_contact(
            linkedin_url="https://linkedin.com/in/jane-cto",
            title="Chief Technology Officer",
        )
        assert cto.seniority_level == SeniorityLevel.C_LEVEL
        
        director = self.enricher.enrich_contact(
            linkedin_url="https://linkedin.com/in/bob-director",
            title="Director of Sales",
        )
        assert director.seniority_level == SeniorityLevel.DIRECTOR
        
        manager = self.enricher.enrich_contact(
            linkedin_url="https://linkedin.com/in/alice-manager",
            title="Product Manager",
        )
        assert manager.seniority_level == SeniorityLevel.MANAGER
    
    def test_enrich_contact_user_id_extraction(self):
        """Test user ID extraction from URL."""
        contact = self.enricher.enrich_contact(
            linkedin_url="https://linkedin.com/in/sarah-smith"
        )
        assert contact.user_id == "urn:li:person:sarah-smith"


class TestSocialGraphAnalysis:
    """Test 3: Social Graph Analysis."""
    
    def setup_method(self):
        self.enricher = LeadEnricher()
    
    def test_analyze_social_graph(self):
        """Input: Prospect LinkedIn ID
        Expected: SocialGraph with mutual_connections, shared_groups
        """
        social_graph = self.enricher.analyze_social_graph(
            user_id="urn:li:person:prospect123",
            mutual_connections=["Alice Chen", "Bob Smith", "Carol Johnson"],
            shared_groups=["SaaS Founders", "DevTools Community"],
        )
        
        assert isinstance(social_graph, SocialGraph)
        assert social_graph.mutual_connections == 3
        assert social_graph.mutual_connection_names == ["Alice Chen", "Bob Smith", "Carol Johnson"]
        assert social_graph.shared_groups == ["SaaS Founders", "DevTools Community"]
    
    def test_analyze_social_graph_empty(self):
        """Handle empty social graph."""
        social_graph = self.enricher.analyze_social_graph(
            user_id="urn:li:person:lonely-user"
        )
        
        assert social_graph.mutual_connections == 0
        assert social_graph.mutual_connection_names == []
        assert social_graph.shared_groups == []
    
    def test_analyze_social_graph_missing_user_raises_error(self):
        """Missing user_id should raise ValueError."""
        with pytest.raises(ValueError, match="user_id is required"):
            self.enricher.analyze_social_graph(user_id="")


class TestEnrichLead:
    """Test full lead enrichment."""
    
    def test_enrich_lead_complete(self):
        """Test full lead enrichment with all data."""
        enricher = LeadEnricher()
        
        lead = enricher.enrich_lead(
            user_id="urn:li:person:prospect123",
            linkedin_profile_url="https://linkedin.com/in/jane-cto",
            linkedin_company_url="https://linkedin.com/company/acme-tech",
            contact_data={
                "name": "Jane Smith",
                "email": "jane@acme.com",
                "title": "CTO",
            },
            company_data={
                "name": "Acme Technologies",
                "size": 200,
                "industry": "SaaS",
            },
            social_data={
                "mutual_connections": ["Alice", "Bob"],
                "shared_groups": ["Tech Leaders"],
            },
        )
        
        assert lead.user_id == "urn:li:person:prospect123"
        assert lead.contact is not None
        assert lead.contact.name == "Jane Smith"
        assert lead.company is not None
        assert lead.company.size == 200
        assert lead.social_graph is not None
        assert lead.social_graph.mutual_connections == 2
