"""
Pipeline Engine.

Orchestrates the entire lead processing flow:
1. Enrichment
2. Generic ICP Scoring
3. Semantic Scoring
4. Intent Scoring (with Attention)
5. Decision Making
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from ..signals import SignalEvent
from ..enrichment import LeadEnricher, ICPMatcher, EnrichedLead
from ..scoring import IntentScorer
from ..engagement import HighIntentFilter, ConversationStarter, EngagementDecision
from ..context import SenderProfile, SemanticMatcher, AttentionSignalWeighter
from .config import SystemConfig
from .utils import LinkedInURL

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PipelineEngine:
    """Core engine for processing leads through the Scout pipeline."""
    
    def __init__(self, sender_profile: SenderProfile, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()
        self.sender_profile = sender_profile
        
        # Initialize Agents
        self.enricher = LeadEnricher()
        self.icp_matcher = ICPMatcher() # Could pass config here if unified
        self.scorer = IntentScorer()
        self.intent_filter = HighIntentFilter()
        self.starter = ConversationStarter()
        
        # Context-Aware Components
        self.semantic_matcher = SemanticMatcher(sender_profile)
        self.attention_weighter = AttentionSignalWeighter()
        
    def process_lead(self, user_id: str, profile_data: Dict[str, Any], signals: List[SignalEvent]) -> Dict[str, Any]:
        """
        Run the full pipeline for a single lead.
        
        Returns a result dictionary with all scores and decision.
        """
        
        # 1. Enrichment
        # Construct company URL heuristic if missing
        company_url = profile_data.get('linkedin_url')
        if not company_url and profile_data.get('company_name'):
             company_url = LinkedInURL.company(profile_data['company_name'])
             
        lead = self.enricher.enrich_lead(
            user_id=user_id,
            linkedin_profile_url=profile_data.get('linkedin_url'),
            linkedin_company_url=company_url,
            contact_data={
                "name": profile_data.get('name', 'Unknown'),
                "title": profile_data.get('title', 'Unknown'),
            },
            company_data={
                "name": profile_data.get('company_name', 'Unknown'),
                "website": profile_data.get('company_domain'),
                "industry": profile_data.get("industry", "saas"), 
                "size": int(profile_data.get("company_size", 1))
            }
        )
        
        # 2. Generic ICP Scoring
        icp_result = self.icp_matcher.calculate_icp_score(lead)
        icp_score = icp_result['icp_score']
        
        # 3. Semantic Fit Scoring
        semantic_fit = self.semantic_matcher.calculate_fit_score(lead) * 100
        
        # 4. Intent Scoring & Attention
        intent_result = self.scorer.calculate_intent_score(signals, lead)
        attention_weights = self.attention_weighter(self.sender_profile, signals)
        
        # 5. Hybrid Decision Logic
        # "High Intent" check from generic scorer
        is_intent_qualified = intent_result.score > self.config.min_intent_for_engagement
        
        # "Good Fit" check: Either high Generic ICP OR High Semantic Match
        is_fit_qualified = (icp_score >= self.config.icp_engage_threshold) or \
                           (semantic_fit >= self.config.semantic_fit_threshold)
                           
        should_engage = is_intent_qualified and is_fit_qualified
        
        # Generate Draft if engaged
        draft_message = None
        if should_engage:
            draft_message = self.starter.generate_message(lead, signals)
            
        return {
            "lead": lead,
            "icp": {
                "score": icp_score,
                "breakdown": icp_result['breakdown'],
                "authority": icp_result['authority_level']
            },
            "semantic": {
                "score": semantic_fit
            },
            "intent": {
                "score": intent_result.score,
                "label": intent_result.label.value,
                "signals": len(signals),
                "attention_weights": attention_weights
            },
            "decision": {
                "should_engage": should_engage,
                "reason": "Qualified" if should_engage else "Low Intent/Fit"
            },
            "draft": draft_message
        }
