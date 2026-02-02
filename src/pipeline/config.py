"""
Pipeline Configuration.

Centralizes all system thresholds and settings.
"""

from dataclasses import dataclass

@dataclass
class SystemConfig:
    """Configuration for the Lead Scout Pipeline."""
    
    # Intent Scoring
    high_intent_threshold: float = 70.0
    medium_intent_threshold: float = 30.0
    
    # ICP Scoring
    icp_engage_threshold: float = 80.0  # Detailed match
    
    # Semantic/Context-Aware Scoring
    semantic_fit_threshold: float = 80.0
    
    # Hybrid Logic
    # If Intent > X AND (ICP > Y OR Semantic > Z)
    min_intent_for_engagement: float = 30.0
    
    # Decay Settings
    decay_half_life_hours: float = 168.0 # 7 days
