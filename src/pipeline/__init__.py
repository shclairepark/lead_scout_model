"""
Pipeline Module.

Exports the core engine and configuration for the Lead Scout system.
"""

from .config import SystemConfig
from .engine import PipelineEngine
from .utils import LinkedInURL

__all__ = [
    'SystemConfig',
    'PipelineEngine',
    'LinkedInURL',
]
