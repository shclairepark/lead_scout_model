"""
Signal Collection Module (Block 0)

This module provides real-time signal collection for lead scoring:
- SignalEvent: Core data class for all signal types
- LinkedInSignalMonitor: Agent 0A - LinkedIn engagement signals
- ExternalSignalAggregator: Agent 0B - Funding, role changes, events
"""

from .signal_event import SignalEvent, SignalType, SignalSource
from .linkedin_monitor import LinkedInSignalMonitor
from .external_aggregator import ExternalSignalAggregator

__all__ = [
    'SignalEvent',
    'SignalType',
    'SignalSource',
    'LinkedInSignalMonitor', 
    'ExternalSignalAggregator',
]
