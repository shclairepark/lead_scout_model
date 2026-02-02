"""
Automated Engagement Pipeline (Block 3.5)

This module handles automated outreach decisions and message generation:
- HighIntentFilter: Agent 3.5A - Gates outreach based on score & criteria
- ConversationStarter: Agent 3.5B - Generates contextual messages
- EngagementDecision, OutreachMessage: Data classes
"""

from .data_classes import (
    EngagementDecision,
    OutreachMessage,
    EngagementConfig,
    EngagementPriority,
)
from .intent_filter import HighIntentFilter
from .conversation_starter import ConversationStarter

__all__ = [
    'EngagementDecision',
    'OutreachMessage',
    'EngagementConfig',
    'EngagementPriority',
    'HighIntentFilter',
    'ConversationStarter',
]
