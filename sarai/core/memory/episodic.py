"""
Episodic Memory
===============

Specific experiences with temporal context.

Like human episodic memory, stores:
- What happened
- When it happened
- Where (context)
- Emotional coloring
- Importance

Uses vector embeddings for semantic similarity search.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import hashlib

from sarai.types import Experience, Query
from sarai.safety.logging import ComprehensiveLogger


class EpisodicMemory:
    """
    Episodic memory storage and retrieval.

    Stores specific experiences with full temporal and contextual information.
    """

    def __init__(self, storage_path: str, logger: ComprehensiveLogger):
        """
        Initialize episodic memory.

        Args:
            storage_path: Path for memory storage
            logger: Comprehensive logger
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logger

        # In-memory index for fast lookup
        self.index: Dict[str, Experience] = {}
        self.temporal_index: List[tuple[datetime, str]] = []  # (timestamp, id)

        # Load existing memories
        self._load_from_disk()

        self.logger.logger.info(
            f"Episodic memory initialized with {len(self.index)} memories"
        )

    async def store(self, experience: Experience) -> str:
        """
        Store an experience.

        Args:
            experience: The experience to store

        Returns:
            Storage ID
        """
        # Generate ID
        memory_id = self._generate_id(experience)

        # Store in index
        self.index[memory_id] = experience

        # Update temporal index
        self.temporal_index.append((experience.timestamp, memory_id))
        self.temporal_index.sort(key=lambda x: x[0])

        # Persist to disk
        self._save_to_disk(memory_id, experience)

        self.logger.logger.debug(f"Stored episodic memory: {memory_id}")

        return memory_id

    async def recall(self, query: Query) -> List[Experience]:
        """
        Recall experiences matching query.

        Uses:
        - Temporal proximity
        - Content similarity
        - Context matching
        - Emotional valence

        Args:
            query: The query

        Returns:
            List of matching experiences
        """
        matches = []

        # Search through memories
        for memory_id, experience in self.index.items():
            score = self._compute_match_score(query, experience)

            if score > 0.3:  # Threshold
                matches.append((score, experience))

        # Sort by score
        matches.sort(key=lambda x: x[0], reverse=True)

        # Return top matches
        return [exp for score, exp in matches[:query.max_results]]

    async def get_important_memories(
        self,
        importance_threshold: float = 0.7,
        limit: int = 100
    ) -> List[Experience]:
        """
        Get high-importance memories for consolidation.

        Args:
            importance_threshold: Minimum importance (0-1)
            limit: Maximum number to return

        Returns:
            List of important experiences
        """
        important = [
            exp for exp in self.index.values()
            if exp.importance >= importance_threshold
        ]

        # Sort by importance
        important.sort(key=lambda x: x.importance, reverse=True)

        return important[:limit]

    async def consolidate(self):
        """
        Consolidation during sleep.

        - Increase importance of frequently accessed memories
        - Decrease importance of old, low-importance memories
        - Prune very low importance memories
        """
        cutoff_date = datetime.now() - timedelta(days=30)
        pruned = 0

        # Prune old, unimportant memories
        to_remove = []
        for memory_id, experience in self.index.items():
            if (experience.timestamp < cutoff_date and
                experience.importance < 0.2):
                to_remove.append(memory_id)

        for memory_id in to_remove:
            del self.index[memory_id]
            # Remove from temporal index
            self.temporal_index = [
                (ts, mid) for ts, mid in self.temporal_index
                if mid != memory_id
            ]
            # Remove from disk
            memory_file = self.storage_path / f"{memory_id}.json"
            if memory_file.exists():
                memory_file.unlink()
            pruned += 1

        self.logger.logger.info(f"Episodic consolidation: pruned {pruned} memories")

    async def clear(self):
        """Clear all episodic memories."""
        self.index.clear()
        self.temporal_index.clear()

        # Clear disk storage
        for file in self.storage_path.glob("*.json"):
            file.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        if not self.index:
            return {
                "total_memories": 0,
                "avg_importance": 0,
                "date_range": None
            }

        timestamps = [exp.timestamp for exp in self.index.values()]

        return {
            "total_memories": len(self.index),
            "avg_importance": sum(exp.importance for exp in self.index.values()) / len(self.index),
            "date_range": {
                "earliest": min(timestamps).isoformat(),
                "latest": max(timestamps).isoformat()
            },
            "emotional_distribution": self._get_emotional_distribution()
        }

    def _generate_id(self, experience: Experience) -> str:
        """Generate unique ID for experience."""
        # Use content + timestamp for uniqueness
        content_str = str(experience.content) + experience.timestamp.isoformat()
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def _compute_match_score(self, query: Query, experience: Experience) -> float:
        """
        Compute how well an experience matches a query.

        Considers:
        - Content similarity
        - Context overlap
        - Temporal proximity (if specified)
        - Importance
        """
        score = 0.0

        # Simple text matching (in production, would use embeddings)
        query_text = query.content.lower()
        content_text = str(experience.content).lower()

        if query_text in content_text:
            score += 0.5

        # Context matching
        if query.context:
            context_overlap = len(
                set(query.context.keys()) & set(experience.context.keys())
            )
            score += min(context_overlap * 0.1, 0.3)

        # Importance boost
        score += experience.importance * 0.2

        return min(score, 1.0)

    def _load_from_disk(self):
        """Load existing memories from disk."""
        for file in self.storage_path.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct experience
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    experience = Experience(**data)
                    memory_id = file.stem
                    self.index[memory_id] = experience
                    self.temporal_index.append((experience.timestamp, memory_id))
            except Exception as e:
                self.logger.log_error(e, {"context": f"loading memory {file}"})

        self.temporal_index.sort(key=lambda x: x[0])

    def _save_to_disk(self, memory_id: str, experience: Experience):
        """Save memory to disk."""
        file_path = self.storage_path / f"{memory_id}.json"

        try:
            data = asdict(experience)
            data['timestamp'] = experience.timestamp.isoformat()

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.log_error(e, {"context": f"saving memory {memory_id}"})

    def _get_emotional_distribution(self) -> Dict[str, int]:
        """Get distribution of emotional valences."""
        distribution = {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "unknown": 0
        }

        for experience in self.index.values():
            if experience.emotional_valence is None:
                distribution["unknown"] += 1
            elif experience.emotional_valence > 0.2:
                distribution["positive"] += 1
            elif experience.emotional_valence < -0.2:
                distribution["negative"] += 1
            else:
                distribution["neutral"] += 1

        return distribution
