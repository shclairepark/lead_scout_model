"""
Attention-Based Signal Weighter.

Reuses:
- src.model.attention: MultiHeadAttention
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List

from ..model.attention import MultiHeadAttention
from .data_classes import SenderProfile
from ..signals.signal_event import SignalEvent

class AttentionSignalWeighter(nn.Module):
    """
    Uses Multi-Head Attention to weight signals based on Sender Context.
    
    Q: Sender Context (Who we are)
    K: Signal Features (What happened)
    V: Signal Features (What happened)
    
    Output: Weighted attention scores indicating signal relevance.
    """
    
    def __init__(self, embed_dim: int = 128, num_heads: int = 4):
        super().__init__()
        self.embed_dim = embed_dim
        
        # REUSE: MultiHeadAttention from existing model codebase
        self.attention = MultiHeadAttention(embed_dim=embed_dim, num_heads=num_heads)
        
        # Projection for mixing raw signal strength
        self.norm = nn.LayerNorm(embed_dim)
        
    def forward(self, sender_profile: SenderProfile, signals: List[SignalEvent]):
        """
        Calculate context-aware weights for a list of signals.
        """
        if not signals:
            return {}
            
        # 1. Prepare Query (Sender Context)
        # Shape: [1, 1, embed_dim] (Batch=1, Seq=1)
        sender_vec = torch.tensor(sender_profile.get_embedding()).float().view(1, 1, -1)
        
        # 2. Prepare Keys/Values (Signals)
        # We need to embed signals into vectors.
        # For this reuse demo, we'll assign random vectors but stable by signal type
        signal_vecs = []
        for sig in signals:
            vec = self._embed_signal(sig, sender_profile)
            signal_vecs.append(vec)
            
        # Shape: [1, num_signals, embed_dim]
        files_tensor = torch.stack(signal_vecs).view(1, len(signals), -1)
        
        # 3. Apply Multi-Head Attention (REUSE)
        # Q = Sender, K=V = Signals
        # We want to know how much Sender attends to each Signal
        # Note: Standard attention is typically Self-Attention (Q=K=V) or Cross-Attention.
        # Here we do Cross-Attention: Q=Sender, KV=Signals.
        
        # However, MHA implementation in src.model might assume Q=K=V if passed only one input?
        # Let's check signature. 
        # forward(x, mask) -> creates Q, K, V from x.
        # The existing MHA is Self-Attention implementation (calculates Q,K,V from same x).
        
        # To reuse SELF-ATTENTION for this purpose, we can concatenate:
        # Input = [Sender_Token, Signal_1, Signal_2, ...]
        # Then we look at the attention weights of Sender_Token -> Signal_N
        
        combined_input = torch.cat([sender_vec, files_tensor], dim=1)
        # Shape: [1, 1 + num_signals, embed_dim]
        
        # Run MHA
        output, attn_weights_avg = self.attention(combined_input)
        
        # attn_weights_avg shape: [1, seq_len, seq_len]
        # We care about row 0 (Sender) attending to cols 1..N (Signals)
        
        # Extract weights: [1, 0, 1:] -> First batch, First row (Sender), All signal columns
        signal_weights = attn_weights_avg[0, 0, 1:]
        
        # Normalize to valid scores (e.g. 0-100 modifier)
        # Detach and convert to list
        weights_list = signal_weights.detach().tolist()
        
        # Map back to signals
        result = {}
        for i, sig in enumerate(signals):
            # Scale up for readability (e.g. 1.0 -> 100% relevance)
            # Attention sums to 1.0, so if there are many signals, values will be small.
            # We multiply by len(signals) to get 'relative lift'
            relevance = weights_list[i] * len(signals)
            result[sig] = relevance
            
        return result

    def _embed_signal(self, signal: SignalEvent, profile: SenderProfile) -> torch.Tensor:
        """
        Embed a signal into vector space.
        Heuristic: If signal type matches target roles/industries, align with Sender.
        """
        # Base random vector
        np.random.seed(int(signal.timestamp.timestamp())) # Stable random
        vec = np.random.rand(self.embed_dim).astype(np.float32)
        
        # Check heuristics for semantic alignment
        is_relevant_role = False
        if signal.data:
            # Check if job title in signal matches target roles
            # (In reality we'd need Contact data linked to signal, here we simplify)
            pass
            
        # Manually boost vector alignment if signal type is high value
        # This simulates "learning" that these signals are important
        if signal.type.value in ["demo_request", "funding_round"]:
             # Add sender embedding to signal embedding to force high dot product (high attention)
             vec += profile.get_embedding()
             
        # Normalize
        vec = vec / (np.linalg.norm(vec) + 1e-9)
        return torch.tensor(vec).float()
