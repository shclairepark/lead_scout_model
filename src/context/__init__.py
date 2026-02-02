"""
Context-Aware Scoring Module.

This module implements semantic matching and adaptive scoring:
- SemanticMatcher: Reuses similarity utils for vector-based ICP fit.
- AttentionSignalWeighter: Reuses MultiHeadAttention for context-aware signal scoring.
"""

from .data_classes import SenderProfile
from .semantic_matcher import SemanticMatcher
from .signal_attention import AttentionSignalWeighter

__all__ = [
    'SenderProfile',
    'SemanticMatcher',
    'AttentionSignalWeighter',
]
