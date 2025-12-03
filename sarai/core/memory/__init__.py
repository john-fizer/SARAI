"""
Memory Architecture for SARAI
==============================

Four-layer memory system mirroring human cognitive architecture:

1. Episodic - Specific experiences with temporal context
2. Semantic - Factual knowledge as graph structure
3. Procedural - Encoded skills and capabilities
4. Archetypal - Symbolic patterns and meaning structures

Each layer has independent storage and retrieval, with cross-layer
associations enabling holistic recall.
"""

from sarai.core.memory.architecture import MemoryArchitecture
from sarai.core.memory.episodic import EpisodicMemory
from sarai.core.memory.semantic import SemanticMemory
from sarai.core.memory.procedural import ProceduralMemory
from sarai.core.memory.archetypal import ArchetypalMemory

__all__ = [
    "MemoryArchitecture",
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",
    "ArchetypalMemory",
]
