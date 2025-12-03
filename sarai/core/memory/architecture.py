"""
Memory Architecture
===================

Main coordinator for the four-layer memory system.
Manages storage, retrieval, and consolidation across all layers.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from sarai.types import Experience, Query, MemoryRecall
from sarai.core.memory.episodic import EpisodicMemory
from sarai.core.memory.semantic import SemanticMemory
from sarai.core.memory.procedural import ProceduralMemory
from sarai.core.memory.archetypal import ArchetypalMemory
from sarai.safety.logging import ComprehensiveLogger


class MemoryArchitecture:
    """
    Four-layer memory system coordinator.

    Handles storage, retrieval, and consolidation across:
    - Episodic (experiences)
    - Semantic (knowledge)
    - Procedural (skills)
    - Archetypal (symbols)
    """

    def __init__(self, logger: ComprehensiveLogger, storage_path: str = "./memory"):
        """
        Initialize memory architecture.

        Args:
            logger: Comprehensive logger
            storage_path: Base path for memory storage
        """
        self.logger = logger

        # Initialize all four layers
        self.episodic = EpisodicMemory(storage_path + "/episodic", logger)
        self.semantic = SemanticMemory(storage_path + "/semantic", logger)
        self.procedural = ProceduralMemory(storage_path + "/procedural", logger)
        self.archetypal = ArchetypalMemory(storage_path + "/archetypal", logger)

        # Cross-layer association tracking
        self.associations: Dict[str, List[str]] = {}

        self.logger.logger.info("Memory architecture initialized")

    async def store(self, experience: Experience) -> Dict[str, str]:
        """
        Store experience across appropriate layers.

        Automatically classifies what goes where and creates
        cross-layer associations.

        Args:
            experience: The experience to store

        Returns:
            Dictionary mapping layer names to storage IDs
        """
        storage_ids = {}

        # Always store in episodic (specific experience)
        episodic_id = await self.episodic.store(experience)
        storage_ids["episodic"] = episodic_id

        # Extract and store semantic knowledge
        semantic_facts = self._extract_semantic_facts(experience)
        if semantic_facts:
            semantic_ids = await self.semantic.store_facts(semantic_facts)
            storage_ids["semantic"] = semantic_ids

        # Check for procedural knowledge (skills, capabilities)
        if self._contains_procedural_knowledge(experience):
            procedural_id = await self.procedural.store_skill(experience)
            storage_ids["procedural"] = procedural_id

        # Extract archetypal patterns
        symbols = self._extract_symbols(experience)
        if symbols:
            archetypal_id = await self.archetypal.store_pattern(
                experience,
                symbols
            )
            storage_ids["archetypal"] = archetypal_id

        # Create cross-layer associations
        self._create_associations(storage_ids)

        self.logger.logger.debug(
            f"Experience stored across {len(storage_ids)} layers"
        )

        return storage_ids

    async def recall(
        self,
        query: Query,
        stage: int,
        cross_layer: bool = True
    ) -> MemoryRecall:
        """
        Retrieve memories across layers.

        Stage-gated: early stages have limited access to archetypal layer.

        Args:
            query: The memory query
            stage: Current developmental stage (1-12)
            cross_layer: Whether to use cross-layer associations

        Returns:
            MemoryRecall with results from relevant layers
        """
        results = []
        sources = []
        confidences = []

        # Query based on type or all layers
        if query.query_type == "episodic" or query.query_type == "all":
            episodic_results = await self.episodic.recall(query)
            results.extend(episodic_results)
            sources.extend(["episodic"] * len(episodic_results))
            confidences.extend([0.8] * len(episodic_results))

        if query.query_type == "semantic" or query.query_type == "all":
            semantic_results = await self.semantic.recall(query)
            results.extend(semantic_results)
            sources.extend(["semantic"] * len(semantic_results))
            confidences.extend([0.9] * len(semantic_results))

        if query.query_type == "procedural" or query.query_type == "all":
            procedural_results = await self.procedural.recall(query)
            results.extend(procedural_results)
            sources.extend(["procedural"] * len(procedural_results))
            confidences.extend([0.85] * len(procedural_results))

        # Archetypal access is stage-gated
        if (query.query_type == "archetypal" or query.query_type == "all") and stage >= 4:
            archetypal_results = await self.archetypal.recall(query, stage)
            results.extend(archetypal_results)
            sources.extend(["archetypal"] * len(archetypal_results))
            # Confidence increases with stage
            archetypal_confidence = min(0.5 + (stage / 12) * 0.4, 0.9)
            confidences.extend([archetypal_confidence] * len(archetypal_results))

        # Cross-layer retrieval if enabled
        if cross_layer and results:
            additional = await self._cross_layer_retrieval(results[0], sources[0])
            results.extend(additional["results"])
            sources.extend(additional["sources"])
            confidences.extend(additional["confidences"])

        # Calculate overall confidence
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return MemoryRecall(
            results=results[:query.max_results],
            confidence=overall_confidence,
            sources=sources[:query.max_results]
        )

    async def consolidate(self):
        """
        Memory consolidation during sleep cycle.

        - Strengthen important connections
        - Prune low-importance memories
        - Transfer episodic -> semantic where appropriate
        - Update archetypal patterns
        """
        self.logger.logger.info("Starting memory consolidation...")

        # Consolidate each layer
        await asyncio.gather(
            self.episodic.consolidate(),
            self.semantic.consolidate(),
            self.procedural.consolidate(),
            self.archetypal.consolidate()
        )

        # Transfer high-importance episodic memories to semantic
        important_episodes = await self.episodic.get_important_memories()
        for episode in important_episodes:
            facts = self._extract_semantic_facts(episode)
            if facts:
                await self.semantic.store_facts(facts)

        self.logger.logger.info("Memory consolidation complete")

    def _extract_semantic_facts(self, experience: Experience) -> List[Dict[str, Any]]:
        """
        Extract factual knowledge from experience.

        In production, this would use NLP and knowledge extraction.
        For now, simplified.
        """
        facts = []

        # Look for explicit facts in context
        if "facts" in experience.context:
            facts.extend(experience.context["facts"])

        # Extract from content if it's structured
        if isinstance(experience.content, dict):
            if "learned" in experience.content:
                facts.append({
                    "subject": experience.content.get("subject", "unknown"),
                    "predicate": "learned",
                    "object": experience.content["learned"]
                })

        return facts

    def _contains_procedural_knowledge(self, experience: Experience) -> bool:
        """Check if experience contains procedural knowledge."""
        # Check for skill-related keywords
        skill_indicators = ["learned how", "skill", "capability", "can now", "procedure"]

        content_str = str(experience.content).lower()
        return any(indicator in content_str for indicator in skill_indicators)

    def _extract_symbols(self, experience: Experience) -> List[str]:
        """
        Extract symbolic/archetypal elements from experience.

        In production, this would use sophisticated pattern matching.
        For now, simplified.
        """
        symbols = []

        # Check for archetypal keywords in context
        if "symbols" in experience.context:
            symbols.extend(experience.context["symbols"])

        # Check for emotional valence as symbolic indicator
        if experience.emotional_valence is not None:
            if experience.emotional_valence > 0.7:
                symbols.append("triumph")
            elif experience.emotional_valence < -0.7:
                symbols.append("trial")

        return symbols

    def _create_associations(self, storage_ids: Dict[str, str]):
        """Create cross-layer associations."""
        # Each storage ID can be associated with others from same experience
        for layer1, id1 in storage_ids.items():
            key = f"{layer1}:{id1}"
            if key not in self.associations:
                self.associations[key] = []

            for layer2, id2 in storage_ids.items():
                if layer1 != layer2:
                    self.associations[key].append(f"{layer2}:{id2}")

    async def _cross_layer_retrieval(
        self,
        initial_result: Any,
        source_layer: str
    ) -> Dict[str, List]:
        """
        Retrieve associated memories from other layers.

        Args:
            initial_result: The initial memory retrieved
            source_layer: Which layer it came from

        Returns:
            Dict with additional results, sources, and confidences
        """
        # Simplified - in production would use actual IDs
        return {
            "results": [],
            "sources": [],
            "confidences": []
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "episodic": self.episodic.get_stats(),
            "semantic": self.semantic.get_stats(),
            "procedural": self.procedural.get_stats(),
            "archetypal": self.archetypal.get_stats(),
            "cross_layer_associations": len(self.associations)
        }

    async def clear_all(self):
        """Clear all memories (use with caution)."""
        self.logger.logger.warning("Clearing all memories")
        await asyncio.gather(
            self.episodic.clear(),
            self.semantic.clear(),
            self.procedural.clear(),
            self.archetypal.clear()
        )
        self.associations.clear()
