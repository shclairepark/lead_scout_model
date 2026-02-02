"""
Semantic Matcher (Context-Aware ICP).

Reuses:
- src.tokenizer.similarity: cosine_similarity
"""

from typing import List, Dict, Any, Optional
import numpy as np

from ..tokenizer.similarity import cosine_similarity
from .data_classes import SenderProfile
from ..enrichment.data_classes import EnrichedLead

class SemanticMatcher:
    """
    Calculates semantic fit between Sender and Lead.
    """
    
    def __init__(self, sender_profile: SenderProfile):
        self.sender = sender_profile
        
    def calculate_fit_score(self, lead: EnrichedLead) -> float:
        """
        Calculate semantic alignment between Sender and Lead.
        Returns score 0.0 to 1.0.
        """
        # 1. Get Sender Vector
        sender_vec = self.sender.get_embedding()
        
        # 2. Get Lead Vector
        # In a real system, we'd encode lead.company.description or industry
        # For this demo/reuse structure, we simulate a lead vector
        # influenced by their industry to show variance
        lead_vec = self._simulate_lead_embedding(lead)
        
        # 3. Calculate Similarity (REUSE)
        score = cosine_similarity(sender_vec, lead_vec)
        
        # Clip to 0-1 range (cosine can be -1 to 1)
        return float(max(0.0, score))
    
    def _simulate_lead_embedding(self, lead: EnrichedLead) -> np.ndarray:
        """
        Generate a mock embedding for the lead.
        In production, this would use the same Encoder as the Sender.
        """
        # Seed logic with industry string to get consistent "mock" vectors
        # If lead industry matches target, return vector closer to sender
        
        is_target_industry = False
        if lead.company and lead.company.industry:
            # Check string match
            ind_str = str(lead.company.industry.value)
            if ind_str in self.sender.target_industries:
                is_target_industry = True
                
        # If target industry, add noise to sender vector (high similarity)
        # If not, generate random vector (low similarity)
        if is_target_industry:
            noise = np.random.normal(0, 0.1, size=self.sender.get_embedding().shape)
            vec = self.sender.get_embedding() + noise
        else:
            vec = np.random.rand(128).astype(np.float32)
            
        return vec
