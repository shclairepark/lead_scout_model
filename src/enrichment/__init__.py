"""
Lead Enrichment & ICP Matching Module (Block 1.5)

This module provides lead enrichment and ICP scoring:
- EnrichedCompany, EnrichedContact, SocialGraph: Data classes
- LeadEnricher: Agent 1.5A - Enrich leads with company/contact data
- ICPMatcher: Agent 1.5B - Score leads against Ideal Customer Profile
"""

from .data_classes import (
    EnrichedCompany,
    EnrichedContact,
    SocialGraph,
    ICPConfig,
    EnrichedLead,
    SeniorityLevel,
    Industry,
)
from .lead_enricher import LeadEnricher
from .icp_matcher import ICPMatcher

__all__ = [
    'EnrichedCompany',
    'EnrichedContact',
    'SocialGraph',
    'ICPConfig',
    'EnrichedLead',
    'SeniorityLevel',
    'Industry',
    'LeadEnricher',
    'ICPMatcher',
]
