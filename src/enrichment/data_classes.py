"""
Data classes for Lead Enrichment & ICP Matching.

These classes represent enriched prospect data structured for
ICP scoring and automated engagement decisions.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class SeniorityLevel(Enum):
    """Seniority levels for authority detection."""
    C_LEVEL = "c_level"
    VP = "vp"
    DIRECTOR = "director"
    MANAGER = "manager"
    INDIVIDUAL_CONTRIBUTOR = "individual_contributor"
    UNKNOWN = "unknown"


class Industry(Enum):
    """Common industry verticals."""
    SAAS = "saas"
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    ECOMMERCE = "ecommerce"
    MARTECH = "martech"
    DEVTOOLS = "devtools"
    SECURITY = "security"
    AI_ML = "ai_ml"
    ENTERPRISE = "enterprise"
    OTHER = "other"


@dataclass
class EnrichedCompany:
    """
    Enriched company data.
    
    Attributes:
        company_id: Unique identifier (LinkedIn URN or domain)
        name: Company display name
        size: Number of employees
        industry: Primary industry vertical
        tech_stack: List of technologies used
        revenue_estimate: Estimated annual revenue (USD)
        funding_stage: Latest funding round
        linkedin_url: Company LinkedIn page URL
        website: Company website URL
        headquarters: Location (city, country)
    """
    company_id: str
    name: str
    size: int = 0
    industry: Industry = Industry.OTHER
    tech_stack: List[str] = field(default_factory=list)
    revenue_estimate: Optional[float] = None
    funding_stage: Optional[str] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    headquarters: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "company_id": self.company_id,
            "name": self.name,
            "size": self.size,
            "industry": self.industry.value,
            "tech_stack": self.tech_stack,
            "revenue_estimate": self.revenue_estimate,
            "funding_stage": self.funding_stage,
            "linkedin_url": self.linkedin_url,
            "website": self.website,
            "headquarters": self.headquarters,
        }


@dataclass
class EnrichedContact:
    """
    Enriched contact/prospect data.
    
    Attributes:
        user_id: Unique identifier (LinkedIn URN)
        name: Full name
        email: Verified email address
        phone: Phone number
        title: Job title
        seniority_level: Authority level
        linkedin_url: Profile URL
        company_id: Associated company ID
    """
    user_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    seniority_level: SeniorityLevel = SeniorityLevel.UNKNOWN
    linkedin_url: Optional[str] = None
    company_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "title": self.title,
            "seniority_level": self.seniority_level.value,
            "linkedin_url": self.linkedin_url,
            "company_id": self.company_id,
        }


@dataclass
class SocialGraph:
    """
    Social network analysis for a prospect.
    
    Attributes:
        user_id: Prospect identifier
        mutual_connections: Number of mutual 1st-degree connections
        mutual_connection_names: Names of mutual connections
        shared_groups: LinkedIn groups in common
        second_degree_count: 2nd-degree network size
    """
    user_id: str
    mutual_connections: int = 0
    mutual_connection_names: List[str] = field(default_factory=list)
    shared_groups: List[str] = field(default_factory=list)
    second_degree_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "mutual_connections": self.mutual_connections,
            "mutual_connection_names": self.mutual_connection_names,
            "shared_groups": self.shared_groups,
            "second_degree_count": self.second_degree_count,
        }


@dataclass
class ICPConfig:
    """
    Ideal Customer Profile configuration.
    
    Defines the criteria for scoring leads against your ICP.
    """
    # Company size range (min, max employees)
    size_range: tuple = (50, 500)
    
    # Target industries (list of Industry enums or strings)
    target_industries: List[str] = field(default_factory=lambda: ["saas", "fintech"])
    
    # Required/preferred tech stack
    target_tech_stack: List[str] = field(default_factory=list)
    
    # Minimum funding stage (seed, series_a, etc.)
    min_funding_stage: Optional[str] = None
    
    # Target seniority levels for decision makers
    decision_maker_levels: List[str] = field(
        default_factory=lambda: ["c_level", "vp", "director"]
    )
    
    # Score weights (must sum to 1.0)
    weights: Dict[str, float] = field(default_factory=lambda: {
        "size": 0.20,
        "industry": 0.25,
        "tech_stack": 0.15,
        "funding": 0.15,
        "authority": 0.25,
    })
    
    def validate(self) -> bool:
        """Validate that weights sum to 1.0."""
        total = sum(self.weights.values())
        return 0.99 <= total <= 1.01


@dataclass
class EnrichedLead:
    """
    Fully enriched lead combining all data.
    
    This is the main data structure passed to the ICP Matcher.
    """
    user_id: str
    contact: Optional[EnrichedContact] = None
    company: Optional[EnrichedCompany] = None
    social_graph: Optional[SocialGraph] = None
    icp_score: Optional[float] = None
    icp_breakdown: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "contact": self.contact.to_dict() if self.contact else None,
            "company": self.company.to_dict() if self.company else None,
            "social_graph": self.social_graph.to_dict() if self.social_graph else None,
            "icp_score": self.icp_score,
            "icp_breakdown": self.icp_breakdown,
        }
