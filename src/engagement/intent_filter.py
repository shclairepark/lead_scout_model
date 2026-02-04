"""
Agent 3.5A: High Intent Filter

Gates automated outreach to only high-quality, high-intent leads:
- Checks Intent Score threshold
- Checks ICP Score threshold
- Applies exclusion rules (competitors, customers, etc.)
"""

from typing import Optional
from datetime import datetime

from .data_classes import (
    EngagementDecision, 
    EngagementPriority, 
    EngagementConfig 
)
from ..scoring.data_classes import IntentScore
from ..enrichment.data_classes import EnrichedLead


class HighIntentFilter:
    """
    High Intent Filter (Agent 3.5A)
    
    Decides IF we should engage a lead.
    """
    
    def __init__(self, config: Optional[EngagementConfig] = None):
        """Initialize with config."""
        self.config = config or EngagementConfig()
    
    def evaluate_lead(
        self,
        lead: EnrichedLead,
        intent_score: IntentScore,
        icp_score_val: float
    ) -> EngagementDecision:
        """
        Evaluate if a lead should be engaged.
        
        Args:
            lead: Enriched lead data (for company/domain checks)
            intent_score: Calculated intent result
            icp_score_val: ICP matching score (0-100)
            
        Returns:
            EngagementDecision (Boolean + Reason)
        """
        # 1. Check Exclusion Rules (Safety First)
        exclusion_reason = self._check_exclusions(lead)
        if exclusion_reason:
            return EngagementDecision(
                should_engage=False,
                priority=EngagementPriority.LOW,
                reason=f"Exclusion: {exclusion_reason}",
                decision_time=datetime.now().isoformat()
            )
        
        # 2. Check Scores
        intent_pass = intent_score.score >= self.config.min_intent_score
        icp_pass = icp_score_val >= self.config.min_icp_score
        
        if intent_pass and icp_pass:
            # Qualified Lead
            return EngagementDecision(
                should_engage=True,
                priority=EngagementPriority.HIGH,
                reason="High Intent + High ICP Match",
                decision_time=datetime.now().isoformat()
            )
            
        elif not icp_pass:
            return EngagementDecision(
                should_engage=False,
                priority=EngagementPriority.LOW,
                reason=f"ICP Score {icp_score_val} < {self.config.min_icp_score}",
                decision_time=datetime.now().isoformat()
            )
            
        else: # Intent not high enough
            return EngagementDecision(
                should_engage=False,
                priority=EngagementPriority.MEDIUM, # Nurture
                reason=f"Intent Score {intent_score.score} < {self.config.min_intent_score}",
                decision_time=datetime.now().isoformat()
            )
    
    def _check_exclusions(self, lead: EnrichedLead) -> Optional[str]:
        """Check if lead matches any exclusion rules."""
        if not lead.company or not lead.company.website:
            return None
        
        # Safety check: if company name is in competitor list
        company_name = lead.company.name.lower()
        
        # Check against competitors (name match)
        for competitor in self.config.competitors:
            if competitor.lower() in company_name:
                return "Competitor detected"
                
        # Check excluded domains
        if lead.company.website:
            domain = lead.company.website.lower()
            for excluded in self.config.excluded_domains:
                if excluded.lower() in domain:
                    return "Excluded domain"
                
        return None
