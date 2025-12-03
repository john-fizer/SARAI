"""
Semantic Memory
===============

Factual knowledge as graph structure.

Stores:
- Facts and concepts
- Relationships between concepts
- General knowledge
- Abstractions

Uses graph structure (nodes and edges) for knowledge representation.
In production, would use Neo4j or similar graph database.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from sarai.types import Query
from sarai.safety.logging import ComprehensiveLogger


@dataclass
class Concept:
    """A concept node in semantic memory."""
    id: str
    label: str
    attributes: Dict[str, Any]
    strength: float = 1.0  # How well-established (0-1)


@dataclass
class Relation:
    """A relation edge in semantic memory."""
    source_id: str
    target_id: str
    relation_type: str
    attributes: Dict[str, Any]
    strength: float = 1.0


class SemanticMemory:
    """
    Semantic (knowledge) memory storage and retrieval.

    Implements a simple graph database for concepts and relations.
    """

    def __init__(self, storage_path: str, logger: ComprehensiveLogger):
        """
        Initialize semantic memory.

        Args:
            storage_path: Path for memory storage
            logger: Comprehensive logger
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logger

        # In-memory graph
        self.concepts: Dict[str, Concept] = {}
        self.relations: List[Relation] = []

        # Load from disk
        self._load_from_disk()

        self.logger.logger.info(
            f"Semantic memory initialized with {len(self.concepts)} concepts"
        )

    async def store_facts(self, facts: List[Dict[str, Any]]) -> List[str]:
        """
        Store factual knowledge.

        Each fact should have: subject, predicate, object

        Args:
            facts: List of facts to store

        Returns:
            List of concept IDs created/updated
        """
        concept_ids = []

        for fact in facts:
            subject = fact.get("subject")
            predicate = fact.get("predicate")
            obj = fact.get("object")

            if not all([subject, predicate, obj]):
                continue

            # Create/update concepts
            subject_id = self._get_or_create_concept(subject)
            object_id = self._get_or_create_concept(obj)

            # Create relation
            relation = Relation(
                source_id=subject_id,
                target_id=object_id,
                relation_type=predicate,
                attributes=fact.get("attributes", {})
            )
            self.relations.append(relation)

            concept_ids.extend([subject_id, object_id])

        # Save to disk
        self._save_to_disk()

        self.logger.logger.debug(f"Stored {len(facts)} facts")

        return concept_ids

    async def recall(self, query: Query) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge matching query.

        Args:
            query: The query

        Returns:
            List of relevant facts/concepts
        """
        results = []

        # Search concepts
        query_text = query.content.lower()

        for concept in self.concepts.values():
            if query_text in concept.label.lower():
                # Find relations involving this concept
                relations = self._get_relations_for_concept(concept.id)

                results.append({
                    "concept": concept,
                    "relations": relations,
                    "type": "concept"
                })

        # Search relations
        for relation in self.relations:
            if query_text in relation.relation_type.lower():
                results.append({
                    "relation": relation,
                    "source": self.concepts.get(relation.source_id),
                    "target": self.concepts.get(relation.target_id),
                    "type": "relation"
                })

        return results[:query.max_results]

    async def consolidate(self):
        """
        Consolidation during sleep.

        - Strengthen frequently accessed concepts
        - Prune weak, unused concepts
        - Merge duplicate concepts
        """
        # Prune weak concepts
        weak_threshold = 0.1
        to_remove = [
            cid for cid, concept in self.concepts.items()
            if concept.strength < weak_threshold
        ]

        for cid in to_remove:
            del self.concepts[cid]
            # Remove relations involving this concept
            self.relations = [
                r for r in self.relations
                if r.source_id != cid and r.target_id != cid
            ]

        self.logger.logger.info(
            f"Semantic consolidation: pruned {len(to_remove)} concepts"
        )

        self._save_to_disk()

    async def clear(self):
        """Clear all semantic knowledge."""
        self.concepts.clear()
        self.relations.clear()

        graph_file = self.storage_path / "graph.json"
        if graph_file.exists():
            graph_file.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            "total_concepts": len(self.concepts),
            "total_relations": len(self.relations),
            "avg_concept_strength": (
                sum(c.strength for c in self.concepts.values()) / len(self.concepts)
                if self.concepts else 0
            ),
            "relation_types": list(set(r.relation_type for r in self.relations))
        }

    def _get_or_create_concept(self, label: str) -> str:
        """Get existing concept or create new one."""
        # Check if concept exists
        for concept_id, concept in self.concepts.items():
            if concept.label.lower() == label.lower():
                # Strengthen existing concept
                concept.strength = min(concept.strength + 0.1, 1.0)
                return concept_id

        # Create new concept
        concept_id = f"concept_{len(self.concepts)}"
        self.concepts[concept_id] = Concept(
            id=concept_id,
            label=label,
            attributes={},
            strength=0.5  # Start at medium strength
        )

        return concept_id

    def _get_relations_for_concept(self, concept_id: str) -> List[Relation]:
        """Get all relations involving a concept."""
        return [
            r for r in self.relations
            if r.source_id == concept_id or r.target_id == concept_id
        ]

    def _load_from_disk(self):
        """Load graph from disk."""
        graph_file = self.storage_path / "graph.json"

        if not graph_file.exists():
            return

        try:
            with open(graph_file, 'r') as f:
                data = json.load(f)

                # Load concepts
                for concept_data in data.get("concepts", []):
                    concept = Concept(**concept_data)
                    self.concepts[concept.id] = concept

                # Load relations
                for relation_data in data.get("relations", []):
                    relation = Relation(**relation_data)
                    self.relations.append(relation)

        except Exception as e:
            self.logger.log_error(e, {"context": "loading semantic memory"})

    def _save_to_disk(self):
        """Save graph to disk."""
        graph_file = self.storage_path / "graph.json"

        try:
            data = {
                "concepts": [
                    {
                        "id": c.id,
                        "label": c.label,
                        "attributes": c.attributes,
                        "strength": c.strength
                    }
                    for c in self.concepts.values()
                ],
                "relations": [
                    {
                        "source_id": r.source_id,
                        "target_id": r.target_id,
                        "relation_type": r.relation_type,
                        "attributes": r.attributes,
                        "strength": r.strength
                    }
                    for r in self.relations
                ]
            }

            with open(graph_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.log_error(e, {"context": "saving semantic memory"})
