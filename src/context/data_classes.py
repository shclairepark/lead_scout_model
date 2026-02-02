"""
Data classes for Context-Aware Scoring.

Defines the sender's profile (context) to match against leads.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class SenderProfile:
    """
    Profile of the entity sending the outreach (Training Data / Context).
    
    This context is used to:
    1. Calculate semantic fit with the Lead's industry/description.
    2. Determine which signals are relevant (via Attention).
    """
    name: str
    description: str
    value_props: List[str]
    target_industries: List[str]
    target_roles: List[str]
    
    # Embedding cache (simulated or real)
    # Shape: [d_model]
    embedding: Optional[np.ndarray] = None
    
    def get_embedding(self) -> np.ndarray:
        """
        Return the vector representation of this profile.
        If not set, returns a placeholder random vector for finding architecture reuse.
        """
        if self.embedding is None:
            # Placeholder: In prod, this would use a Transformer encoder
            # returning a 128-dim vector to match our model props
            self.embedding = np.random.rand(128).astype(np.float32)
        return self.embedding
