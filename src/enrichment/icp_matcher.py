"""
Agent 1.5B: ICP Matcher

Scores leads against your Ideal Customer Profile:
- Company size range matching
- Industry alignment
- Tech stack compatibility
- Funding stage validation
- Authority/decision-maker detection
"""

from typing import Dict, Any, Optional, List

from .data_classes import (
    EnrichedLead,
    EnrichedCompany,
    EnrichedContact,
    ICPConfig,
    SeniorityLevel,
    Industry,
)


class ICPMatcher:
    """
    ICP Matcher (Agent 1.5B)
    
    Calculates composite ICP scores for enriched leads.
    Each dimension is scored 0-1, then weighted to produce
    a final score between 0-100.
    """
    
    # Authority scores by seniority level
    AUTHORITY_SCORES = {
        SeniorityLevel.C_LEVEL: 1.0,
        SeniorityLevel.VP: 0.9,
        SeniorityLevel.DIRECTOR: 0.8,
        SeniorityLevel.MANAGER: 0.6,
        SeniorityLevel.INDIVIDUAL_CONTRIBUTOR: 0.3,
        SeniorityLevel.UNKNOWN: 0.2,
    }
    
    # Funding stage priority (later = higher score)
    FUNDING_SCORES = {
        "pre_seed": 0.3,
        "seed": 0.4,
        "series_a": 0.6,
        "series_b": 0.8,
        "series_c": 0.9,
        "series_d": 0.95,
        "ipo": 1.0,
        "public": 1.0,
    }
    
    def __init__(self, config: Optional[ICPConfig] = None):
        """
        Initialize the ICP Matcher.
        
        Args:
            config: ICP configuration. If None, uses defaults.
        """
        self.config = config or ICPConfig()
    
    def score_company_size(
        self, 
        size: int, 
        size_range: Optional[tuple] = None
    ) -> float:
        """
        Score company size against ICP range.
        
        Args:
            size: Number of employees
            size_range: Optional (min, max) tuple. Uses config if not provided.
            
        Returns:
            Score between 0.0 and 1.0
        """
        if size <= 0:
            return 0.0
        
        min_size, max_size = size_range or self.config.size_range
        
        # Perfect match if within range
        if min_size <= size <= max_size:
            return 1.0
        
        # Partial score for near-misses
        if size < min_size:
            # Score decreases as we get further below minimum
            ratio = size / min_size
            return max(0.0, ratio)
        else:
            # Score decreases as we get further above maximum
            ratio = max_size / size
            return max(0.0, ratio)
    
    def score_industry(
        self, 
        industry: Industry, 
        target_industries: Optional[List[str]] = None
    ) -> float:
        """
        Score industry alignment.
        
        Args:
            industry: Company's industry (Industry enum)
            target_industries: Optional list of target industry values
            
        Returns:
            Score: 1.0 if match, 0.0 if no match
        """
        targets = target_industries or self.config.target_industries
        
        # Convert Industry enum to string for comparison
        industry_value = industry.value if isinstance(industry, Industry) else str(industry)
        
        if industry_value in targets or industry_value.lower() in [t.lower() for t in targets]:
            return 1.0
        
        return 0.0
    
    def score_tech_stack(
        self,
        tech_stack: List[str],
        target_tech_stack: Optional[List[str]] = None
    ) -> float:
        """
        Score tech stack compatibility.
        
        Args:
            tech_stack: Company's tech stack
            target_tech_stack: Optional target technologies
            
        Returns:
            Score between 0.0 and 1.0 based on overlap
        """
        targets = target_tech_stack or self.config.target_tech_stack
        
        if not targets:
            # No tech requirements = neutral score
            return 0.5
        
        if not tech_stack:
            return 0.0
        
        # Calculate overlap ratio
        tech_lower = {t.lower() for t in tech_stack}
        targets_lower = {t.lower() for t in targets}
        
        overlap = len(tech_lower & targets_lower)
        return min(1.0, overlap / len(targets_lower))
    
    def score_funding(
        self,
        funding_stage: Optional[str],
        min_funding_stage: Optional[str] = None
    ) -> float:
        """
        Score funding stage.
        
        Args:
            funding_stage: Company's funding stage
            min_funding_stage: Minimum required stage
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not funding_stage:
            return 0.3  # Unknown funding = low score
        
        stage_key = funding_stage.lower().replace("-", "_").replace(" ", "_")
        stage_score = self.FUNDING_SCORES.get(stage_key, 0.4)
        
        # Check against minimum if specified
        min_stage = min_funding_stage or self.config.min_funding_stage
        if min_stage:
            min_key = min_stage.lower().replace("-", "_").replace(" ", "_")
            min_score = self.FUNDING_SCORES.get(min_key, 0.0)
            if stage_score < min_score:
                return 0.0
        
        return stage_score
    
    def score_authority(
        self,
        title: Optional[str] = None,
        seniority_level: Optional[SeniorityLevel] = None
    ) -> tuple:
        """
        Score authority level (decision-maker detection).
        
        Args:
            title: Job title (used if seniority_level not provided)
            seniority_level: Pre-detected seniority level
            
        Returns:
            Tuple of (authority_level: str, authority_score: float)
        """
        # Use provided seniority or detect from title
        if seniority_level:
            level = seniority_level
        elif title:
            level = self._detect_seniority(title)
        else:
            level = SeniorityLevel.UNKNOWN
        
        score = self.AUTHORITY_SCORES.get(level, 0.2)
        
        # Determine if decision maker
        is_decision_maker = level in [
            SeniorityLevel.C_LEVEL,
            SeniorityLevel.VP,
            SeniorityLevel.DIRECTOR,
        ]
        
        authority_label = "decision_maker" if is_decision_maker else "influencer"
        
        return authority_label, score
    
    def calculate_icp_score(
        self,
        lead: Optional[EnrichedLead] = None,
        company: Optional[EnrichedCompany] = None,
        contact: Optional[EnrichedContact] = None,
    ) -> Dict[str, Any]:
        """
        Calculate overall ICP score for a lead.
        
        Args:
            lead: EnrichedLead (preferred) or provide company/contact separately
            company: EnrichedCompany data
            contact: EnrichedContact data
            
        Returns:
            Dict with:
                - icp_score: Weighted score 0-100
                - breakdown: Individual dimension scores
                - authority_level: "decision_maker" or "influencer"
        """
        # Extract data from lead if provided
        if lead:
            company = lead.company or company
            contact = lead.contact or contact
        
        # Calculate individual scores
        size_score = 0.0
        industry_score = 0.0
        tech_score = 0.5
        funding_score = 0.3
        authority_label = "unknown"
        authority_score = 0.2
        
        if company:
            size_score = self.score_company_size(company.size)
            industry_score = self.score_industry(company.industry)
            tech_score = self.score_tech_stack(company.tech_stack)
            funding_score = self.score_funding(company.funding_stage)
        
        if contact:
            authority_label, authority_score = self.score_authority(
                title=contact.title,
                seniority_level=contact.seniority_level,
            )
        
        # Calculate weighted score
        weights = self.config.weights
        weighted_score = (
            size_score * weights.get("size", 0.2) +
            industry_score * weights.get("industry", 0.25) +
            tech_score * weights.get("tech_stack", 0.15) +
            funding_score * weights.get("funding", 0.15) +
            authority_score * weights.get("authority", 0.25)
        )
        
        # Convert to 0-100 scale
        icp_score = round(weighted_score * 100, 1)
        
        return {
            "icp_score": icp_score,
            "breakdown": {
                "size": round(size_score, 2),
                "industry": round(industry_score, 2),
                "tech_stack": round(tech_score, 2),
                "funding": round(funding_score, 2),
                "authority": round(authority_score, 2),
            },
            "authority_level": authority_label,
        }
    
    def _detect_seniority(self, title: str) -> SeniorityLevel:
        """Detect seniority level from job title."""
        title_lower = title.lower()
        
        # Check director first
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
