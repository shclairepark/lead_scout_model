"""
Intent Scoring Engine (Block 2.5)

This module provides multi-factor intent scoring for leads:
- IntentScorer: Agent 2.5A - Calculate intent scores based on signals
- IntentScore, ScoringConfig: Data classes for scoring
"""

from .data_classes import IntentScore, ScoringConfig, IntentLabel
from .intent_scorer import IntentScorer

__all__ = [
    'IntentScore',
    'IntentLabel',
    'ScoringConfig',
    'IntentScorer',
]
