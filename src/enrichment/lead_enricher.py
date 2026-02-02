"""
Agent 1.5A: Lead Enricher

Enriches raw signals with comprehensive prospect data:
- Company enrichment (size, industry, tech stack)
- Contact enrichment (email, phone, seniority)
- Social graph analysis (mutual connections)
"""

from typing import Dict, Any, Optional, List
import re

from .data_classes import (
    EnrichedCompany,
    EnrichedContact,
    SocialGraph,
    EnrichedLead,
    SeniorityLevel,
    Industry,
)


class LeadEnricher:
    """
    Lead Enricher (Agent 1.5A)
    
    Enriches leads with company, contact, and social graph data.
    In production, this would integrate with APIs like:
    - Clearbit
    - Apollo
    - LinkedIn Sales Navigator
    - Crunchbase
    """
    
    # Industry keywords for detection
    INDUSTRY_KEYWORDS = {
        Industry.SAAS: ["saas", "software as a service", "cloud software", "subscription software"],
        Industry.FINTECH: ["fintech", "financial technology", "payments", "banking", "insurance tech"],
        Industry.HEALTHTECH: ["healthtech", "health tech", "medical", "healthcare", "biotech"],
        Industry.ECOMMERCE: ["ecommerce", "e-commerce", "retail", "marketplace", "shopping"],
        Industry.MARTECH: ["martech", "marketing technology", "advertising", "adtech"],
        Industry.DEVTOOLS: ["devtools", "developer tools", "developer platform", "api"],
        Industry.SECURITY: ["security", "cybersecurity", "infosec", "identity"],
        Industry.AI_ML: ["ai", "artificial intelligence", "machine learning", "ml", "data science"],
        Industry.ENTERPRISE: ["enterprise", "b2b", "business software"],
    }
    
    def __init__(self):
        """Initialize the enricher."""
        self._cache: Dict[str, Any] = {}
    
    def enrich_company(self, linkedin_url: str, **kwargs) -> EnrichedCompany:
        """
        Enrich company data from LinkedIn URL.
        
        Args:
            linkedin_url: LinkedIn company page URL
            **kwargs: Additional data to override/supplement:
                - name, size, industry, tech_stack, etc.
                
        Returns:
            EnrichedCompany with size, industry, tech_stack[]
        """
        if not linkedin_url:
            raise ValueError("linkedin_url is required")
        
        # Extract company ID from URL
        company_id = self._extract_company_id(linkedin_url)
        
        # In production: call enrichment API
        # For now, use provided kwargs or defaults
        name = kwargs.get("name", self._extract_name_from_url(linkedin_url))
        size = kwargs.get("size", 0)
        
        # Detect industry from keywords if provided
        industry_str = kwargs.get("industry", "")
        industry = self._detect_industry(industry_str) if industry_str else Industry.OTHER
        
        tech_stack = kwargs.get("tech_stack", [])
        if isinstance(tech_stack, str):
            tech_stack = [t.strip() for t in tech_stack.split(",")]
        
        return EnrichedCompany(
            company_id=company_id,
            name=name,
            size=size,
            industry=industry,
            tech_stack=tech_stack,
            revenue_estimate=kwargs.get("revenue_estimate"),
            funding_stage=kwargs.get("funding_stage"),
            linkedin_url=linkedin_url,
            website=kwargs.get("website"),
            headquarters=kwargs.get("headquarters"),
        )
    
    def enrich_contact(self, linkedin_url: str, **kwargs) -> EnrichedContact:
        """
        Enrich contact data from LinkedIn profile URL.
        
        Args:
            linkedin_url: LinkedIn profile URL
            **kwargs: Additional data:
                - name, email, phone, title, company_id
                
        Returns:
            EnrichedContact with email, phone, seniority_level
        """
        if not linkedin_url:
            raise ValueError("linkedin_url is required")
        
        # Extract user ID from URL
        user_id = self._extract_user_id(linkedin_url)
        
        # Detect seniority from title
        title = kwargs.get("title", "")
        seniority = self._detect_seniority(title) if title else SeniorityLevel.UNKNOWN
        
        return EnrichedContact(
            user_id=user_id,
            name=kwargs.get("name", ""),
            email=kwargs.get("email"),
            phone=kwargs.get("phone"),
            title=title,
            seniority_level=seniority,
            linkedin_url=linkedin_url,
            company_id=kwargs.get("company_id"),
        )
    
    def analyze_social_graph(
        self, 
        user_id: str,
        mutual_connections: Optional[List[str]] = None,
        shared_groups: Optional[List[str]] = None,
        **kwargs
    ) -> SocialGraph:
        """
        Analyze social graph for a prospect.
        
        Args:
            user_id: LinkedIn user ID
            mutual_connections: List of mutual connection names
            shared_groups: List of shared LinkedIn groups
            
        Returns:
            SocialGraph with mutual_connections, shared_groups
        """
        if not user_id:
            raise ValueError("user_id is required")
        
        mutual_connections = mutual_connections or []
        shared_groups = shared_groups or []
        
        return SocialGraph(
            user_id=user_id,
            mutual_connections=len(mutual_connections),
            mutual_connection_names=mutual_connections,
            shared_groups=shared_groups,
            second_degree_count=kwargs.get("second_degree_count", 0),
        )
    
    def enrich_lead(
        self,
        user_id: str,
        linkedin_profile_url: Optional[str] = None,
        linkedin_company_url: Optional[str] = None,
        contact_data: Optional[Dict[str, Any]] = None,
        company_data: Optional[Dict[str, Any]] = None,
        social_data: Optional[Dict[str, Any]] = None,
    ) -> EnrichedLead:
        """
        Create a fully enriched lead combining all data.
        
        Args:
            user_id: Unique lead identifier
            linkedin_profile_url: Profile URL for contact enrichment
            linkedin_company_url: Company URL for company enrichment
            contact_data: Additional contact data
            company_data: Additional company data
            social_data: Social graph data
            
        Returns:
            EnrichedLead with contact, company, and social_graph
        """
        contact = None
        company = None
        social_graph = None
        
        # Enrich contact if profile URL provided
        if linkedin_profile_url:
            contact = self.enrich_contact(
                linkedin_profile_url,
                **(contact_data or {})
            )
        
        # Enrich company if company URL provided
        if linkedin_company_url:
            company = self.enrich_company(
                linkedin_company_url,
                **(company_data or {})
            )
        
        # Analyze social graph if data provided
        if social_data:
            social_graph = self.analyze_social_graph(
                user_id=user_id,
                **social_data
            )
        
        return EnrichedLead(
            user_id=user_id,
            contact=contact,
            company=company,
            social_graph=social_graph,
        )
    
    def _extract_company_id(self, url: str) -> str:
        """Extract company ID from LinkedIn URL."""
        # Match patterns like /company/acme-corp or /company/12345
        match = re.search(r'/company/([^/?]+)', url)
        if match:
            return f"company:{match.group(1)}"
        return f"company:{url.split('/')[-1]}"
    
    def _extract_user_id(self, url: str) -> str:
        """Extract user ID from LinkedIn profile URL."""
        # Match patterns like /in/john-doe
        match = re.search(r'/in/([^/?]+)', url)
        if match:
            return f"urn:li:person:{match.group(1)}"
        return f"urn:li:person:{url.split('/')[-1]}"
    
    def _extract_name_from_url(self, url: str) -> str:
        """Extract a readable name from URL."""
        match = re.search(r'/company/([^/?]+)', url)
        if match:
            # Convert slug to name: acme-corp -> Acme Corp
            slug = match.group(1)
            return " ".join(word.capitalize() for word in slug.split("-"))
        return ""
    
    def _detect_industry(self, industry_str: str) -> Industry:
        """Detect industry from string description."""
        industry_lower = industry_str.lower()
        
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            if any(kw in industry_lower for kw in keywords):
                return industry
        
        return Industry.OTHER
    
    def _detect_seniority(self, title: str) -> SeniorityLevel:
        """Detect seniority level from job title."""
        title_lower = title.lower()
        
        # Check director first (before co-founder)
        if "director" in title_lower:
            return SeniorityLevel.DIRECTOR
        
        if any(t in title_lower for t in ["ceo", "cto", "cfo", "coo", "chief", "founder", "co-founder"]):
            return SeniorityLevel.C_LEVEL
        elif any(t in title_lower for t in ["vp", "vice president"]):
            return SeniorityLevel.VP
        elif any(t in title_lower for t in ["manager", "lead", "head"]):
            return SeniorityLevel.MANAGER
        else:
            return SeniorityLevel.INDIVIDUAL_CONTRIBUTOR
