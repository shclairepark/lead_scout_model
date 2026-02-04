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


from ..signals import SignalEvent
from ..enrichment import LeadEnricher, ICPMatcher
from ..scoring import IntentScorer
from ..engagement import HighIntentFilter, ConversationStarter
from ..context import SenderProfile, SemanticMatcher, AttentionSignalWeighter
from .config import SystemConfig
from .utils import LinkedInURL
import torch
import os
from ..model.lead_scout import LeadScoutModel
from ..tokenizer.sales_tokenizer import SalesTokenizer

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
        self.semantic_matcher = SemanticMatcher(sender_profile)
        self.attention_weighter = AttentionSignalWeighter()
        
        # Initialize Neural Model
        self.tokenizer = SalesTokenizer()
        self.model = None
        checkpoint_path = "checkpoints/lead_scout_best.pth"
        if os.path.exists(checkpoint_path):
            try:
                # Re-init model with correct dims (must match training script)
                self.model = LeadScoutModel(
                    vocab_size=len(self.tokenizer.vocab),
                    embed_dim=64, num_heads=2, num_layers=2, ff_dim=128
                )
                self.model.load_state_dict(torch.load(checkpoint_path))
                self.model.eval()
                logger.info("✅ LeadScout Neural Model Loaded")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
        
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
        
        # 4. Intent Scoring (Rule-Based + Neural)
        intent_result = self.scorer.calculate_intent_score(signals, lead)
        
        # Neural Inference
        neural_prob = 0.0
        if self.model:
            try:
                # Prepare inputs (similar to data/generate_training_data.py logic)
                # We map enriched lead data to tokenizer format
                # Note: enricher output structure is slightly different from tokenizer input expectation
                # We need to adapt it.
                lead_data_for_token = {
                    "months_in_role": 12, # Placeholder, enricher doesn't parse this yet
                    "funding_amount": 0,  # Placeholder
                    "own_views_3m": 0,
                    # We can try to map some real fields if available, otherwise defaults
                }
                
                # Check for funding in signals to populate context
                for s in signals:
                    if s.type.value == "funding_round":
                        lead_data_for_token["funding_amount"] = s.data.get("amount", 0)
                
                tokens, token_ids = self.tokenizer.tokenize_lead(lead_data_for_token, signals)
                input_tensor = torch.tensor([token_ids], dtype=torch.long)
                
                with torch.no_grad():
                    neural_prob = self.model(input_tensor).item() # 0.0 - 1.0
                    
                # Blend or Override? 
                # Let's simple average for now to be safe, or just use Neural if it's confident
                # For demo "Showcasing Model", let's replace the raw score part with Neural
                # intent_result.score = neural_prob * 100.0
                
            except Exception as e:
                logger.warning(f"Neural inference failed: {e}")
                
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
                "label": intent_result.label.value,
                "signals": len(signals),
                "neural_prob": neural_prob,
                "attention_weights": attention_weights
            },
            "decision": {
                "should_engage": should_engage,
                "reason": "Qualified" if should_engage else "Low Intent/Fit"
            },
            "draft": draft_message
        }
