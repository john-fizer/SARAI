"""
Relevance Routing for SARAI
============================

Dynamic attention allocation across 12 archetypal competencies.
Maps zodiacal stages to archetype activation.
"""

from sarai.core.routing.relevance_router import RelevanceRouter
from sarai.core.routing.archetypes import Archetype, ARCHETYPES

__all__ = ["RelevanceRouter", "Archetype", "ARCHETYPES"]
