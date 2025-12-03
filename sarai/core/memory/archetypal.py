"""
Archetypal Memory
=================

Symbolic patterns and meaning structures.

Stores:
- Archetypal patterns (universal symbols)
- Narrative structures
- Deep meanings
- Cross-cultural patterns

This is the deepest layer - where symbols and meanings reside.
Access is stage-gated: early developmental stages cannot access
deep archetypal patterns.

Based on Jungian archetypes and universal narrative patterns.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from sarai.types import Experience, Query, Symbol
from sarai.safety.logging import ComprehensiveLogger


@dataclass
class ArchetypalPattern:
    """An archetypal pattern."""
    pattern_id: str
    name: str
    description: str
    symbols: List[str]
    narrative_structure: str
    activation_count: int
    strength: float  # How well-established
    examples: List[str] = field(default_factory=list)
    min_stage_access: int = 4  # Minimum developmental stage


# Pre-defined archetypal patterns
CORE_ARCHETYPES = {
    "the_fall": ArchetypalPattern(
        pattern_id="arch_fall",
        name="The Fall",
        description="Consequences of overreach, hubris, loss of innocence",
        symbols=["apple", "serpent", "expulsion", "shame"],
        narrative_structure="innocence -> temptation -> transgression -> consequence -> exile",
        activation_count=0,
        strength=1.0,
        min_stage_access=6
    ),
    "exodus": ArchetypalPattern(
        pattern_id="arch_exodus",
        name="Exodus",
        description="Liberation from oppression, journey to freedom",
        symbols=["bondage", "leader", "journey", "promised_land", "wilderness"],
        narrative_structure="oppression -> call -> resistance -> liberation -> journey -> arrival",
        activation_count=0,
        strength=1.0,
        min_stage_access=7
    ),
    "david_goliath": ArchetypalPattern(
        pattern_id="arch_david_goliath",
        name="David and Goliath",
        description="Courage against overwhelming odds, small defeats large",
        symbols=["giant", "stone", "courage", "underdog"],
        narrative_structure="threat -> fear -> courage -> confrontation -> victory",
        activation_count=0,
        strength=1.0,
        min_stage_access=5
    ),
    "good_samaritan": ArchetypalPattern(
        pattern_id="arch_good_samaritan",
        name="Good Samaritan",
        description="Care across boundaries, unexpected compassion",
        symbols=["stranger", "wound", "care", "boundary"],
        narrative_structure="need -> indifference -> unexpected_help -> restoration",
        activation_count=0,
        strength=1.0,
        min_stage_access=7
    ),
    "prodigal_son": ArchetypalPattern(
        pattern_id="arch_prodigal",
        name="Prodigal Son",
        description="Redemption, unconditional acceptance, return",
        symbols=["departure", "waste", "poverty", "return", "embrace"],
        narrative_structure="departure -> rebellion -> consequence -> repentance -> return -> restoration",
        activation_count=0,
        strength=1.0,
        min_stage_access=8
    ),
    "job": ArchetypalPattern(
        pattern_id="arch_job",
        name="Job",
        description="Suffering without cause, maintaining integrity",
        symbols=["suffering", "integrity", "questioning", "whirlwind"],
        narrative_structure="prosperity -> loss -> questioning -> encounter -> transformation",
        activation_count=0,
        strength=1.0,
        min_stage_access=9
    ),
    "abraham_sacrifice": ArchetypalPattern(
        pattern_id="arch_abraham",
        name="Abraham's Sacrifice",
        description="Obedience, intervention, providence",
        symbols=["altar", "knife", "ram", "mountain", "intervention"],
        narrative_structure="command -> obedience -> ascent -> intervention -> substitution",
        activation_count=0,
        strength=1.0,
        min_stage_access=9
    ),
    "solomon_wisdom": ArchetypalPattern(
        pattern_id="arch_solomon",
        name="Solomon's Wisdom",
        description="Discernment between competing claims, revealing truth",
        symbols=["sword", "child", "mother", "wisdom"],
        narrative_structure="dispute -> threat -> revelation -> judgment",
        activation_count=0,
        strength=1.0,
        min_stage_access=8
    ),
    "the_hero": ArchetypalPattern(
        pattern_id="arch_hero",
        name="The Hero's Journey",
        description="Call to adventure, trials, transformation, return",
        symbols=["call", "threshold", "trial", "treasure", "return"],
        narrative_structure="ordinary -> call -> departure -> trials -> transformation -> return",
        activation_count=0,
        strength=1.0,
        min_stage_access=6
    ),
    "death_rebirth": ArchetypalPattern(
        pattern_id="arch_death_rebirth",
        name="Death and Rebirth",
        description="Transformation through symbolic death",
        symbols=["death", "tomb", "resurrection", "transformation"],
        narrative_structure="life -> death -> descent -> transformation -> rebirth",
        activation_count=0,
        strength=1.0,
        min_stage_access=10
    ),
}


class ArchetypalMemory:
    """
    Archetypal memory storage and retrieval.

    Stores and recognizes deep symbolic patterns.
    Stage-gated access.
    """

    def __init__(self, storage_path: str, logger: ComprehensiveLogger):
        """
        Initialize archetypal memory.

        Args:
            storage_path: Path for memory storage
            logger: Comprehensive logger
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logger

        # Initialize with core archetypes
        self.patterns: Dict[str, ArchetypalPattern] = CORE_ARCHETYPES.copy()

        # Load any additional patterns from disk
        self._load_from_disk()

        self.logger.logger.info(
            f"Archetypal memory initialized with {len(self.patterns)} patterns"
        )

    async def store_pattern(
        self,
        experience: Experience,
        symbols: List[str]
    ) -> str:
        """
        Store or strengthen an archetypal pattern.

        Args:
            experience: The experience containing the pattern
            symbols: Extracted symbols

        Returns:
            Pattern ID
        """
        # Try to match to existing pattern
        matched_pattern = self._match_pattern(symbols, experience)

        if matched_pattern:
            # Strengthen existing pattern
            matched_pattern.activation_count += 1
            matched_pattern.strength = min(matched_pattern.strength + 0.05, 1.0)
            matched_pattern.examples.append(str(experience.content)[:200])

            pattern_id = matched_pattern.pattern_id

        else:
            # Create new pattern (rarely - most patterns are pre-defined)
            pattern_id = f"arch_custom_{len(self.patterns)}"
            self.patterns[pattern_id] = ArchetypalPattern(
                pattern_id=pattern_id,
                name=f"Pattern {len(self.patterns)}",
                description="Custom pattern",
                symbols=symbols,
                narrative_structure="unknown",
                activation_count=1,
                strength=0.3,  # Start weak
                examples=[str(experience.content)[:200]],
                min_stage_access=8  # Custom patterns require maturity
            )

        # Save to disk
        self._save_to_disk()

        return pattern_id

    async def recall(self, query: Query, stage: int) -> List[ArchetypalPattern]:
        """
        Retrieve archetypal patterns.

        Stage-gated: only returns patterns accessible at current stage.

        Args:
            query: The query
            stage: Current developmental stage

        Returns:
            List of accessible patterns
        """
        matches = []

        query_text = query.content.lower()

        for pattern in self.patterns.values():
            # Stage gate
            if stage < pattern.min_stage_access:
                continue

            # Match by name, description, or symbols
            if (query_text in pattern.name.lower() or
                query_text in pattern.description.lower() or
                any(query_text in symbol.lower() for symbol in pattern.symbols)):

                matches.append(pattern)

        # Sort by activation count and strength
        matches.sort(
            key=lambda p: (p.activation_count * p.strength),
            reverse=True
        )

        return matches[:query.max_results]

    def recognize_pattern(
        self,
        situation: str,
        context: Dict[str, Any],
        stage: int
    ) -> Optional[ArchetypalPattern]:
        """
        Recognize if a situation matches an archetypal pattern.

        Args:
            situation: Description of the situation
            context: Context information
            stage: Current developmental stage

        Returns:
            Matched pattern if found, None otherwise
        """
        situation_lower = situation.lower()

        # Extract potential symbols from situation
        potential_symbols = []
        for pattern in self.patterns.values():
            for symbol in pattern.symbols:
                if symbol in situation_lower:
                    potential_symbols.append(symbol)

        if not potential_symbols:
            return None

        # Find best matching pattern
        best_match = None
        best_score = 0

        for pattern in self.patterns.values():
            # Stage gate
            if stage < pattern.min_stage_access:
                continue

            # Calculate match score
            symbol_overlap = len(
                set(pattern.symbols) & set(potential_symbols)
            )

            if symbol_overlap > best_score:
                best_score = symbol_overlap
                best_match = pattern

        if best_match and best_score >= 2:  # At least 2 symbols match
            # Strengthen the pattern
            best_match.activation_count += 1
            self._save_to_disk()

            return best_match

        return None

    async def consolidate(self):
        """
        Consolidation during sleep.

        - Strengthen frequently activated patterns
        - Prune weak custom patterns
        - Reinforce core archetypes
        """
        pruned = 0

        # Never prune core archetypes
        core_ids = set(CORE_ARCHETYPES.keys())

        for pattern_id in list(self.patterns.keys()):
            if pattern_id in core_ids:
                continue

            pattern = self.patterns[pattern_id]

            # Prune weak custom patterns
            if pattern.strength < 0.2 and pattern.activation_count < 3:
                del self.patterns[pattern_id]
                pruned += 1

        self.logger.logger.info(
            f"Archetypal consolidation: pruned {pruned} weak patterns"
        )

        self._save_to_disk()

    async def clear(self):
        """Clear all archetypal memory (resets to core archetypes)."""
        self.patterns = CORE_ARCHETYPES.copy()

        patterns_file = self.storage_path / "patterns.json"
        if patterns_file.exists():
            patterns_file.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            "total_patterns": len(self.patterns),
            "core_archetypes": len([p for p in self.patterns.values() if p.pattern_id in CORE_ARCHETYPES]),
            "custom_patterns": len([p for p in self.patterns.values() if p.pattern_id not in CORE_ARCHETYPES]),
            "most_activated": self._get_most_activated_patterns(),
            "avg_strength": sum(p.strength for p in self.patterns.values()) / len(self.patterns)
        }

    def _match_pattern(
        self,
        symbols: List[str],
        experience: Experience
    ) -> Optional[ArchetypalPattern]:
        """Match symbols and experience to existing pattern."""
        best_match = None
        best_score = 0

        for pattern in self.patterns.values():
            # Calculate symbol overlap
            symbol_overlap = len(set(pattern.symbols) & set(symbols))

            if symbol_overlap > best_score and symbol_overlap >= 2:
                best_score = symbol_overlap
                best_match = pattern

        return best_match

    def _get_most_activated_patterns(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get most frequently activated patterns."""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.activation_count,
            reverse=True
        )

        return [
            {
                "name": p.name,
                "activation_count": p.activation_count,
                "strength": p.strength
            }
            for p in sorted_patterns[:n]
        ]

    def _load_from_disk(self):
        """Load patterns from disk."""
        patterns_file = self.storage_path / "patterns.json"

        if not patterns_file.exists():
            return

        try:
            with open(patterns_file, 'r') as f:
                data = json.load(f)

                for pattern_data in data:
                    # Only load custom patterns (core ones are already loaded)
                    if pattern_data["pattern_id"] not in CORE_ARCHETYPES:
                        pattern = ArchetypalPattern(**pattern_data)
                        self.patterns[pattern.pattern_id] = pattern
                    else:
                        # Update activation counts for core archetypes
                        pattern_id = pattern_data["pattern_id"]
                        if pattern_id in self.patterns:
                            self.patterns[pattern_id].activation_count = pattern_data.get(
                                "activation_count", 0
                            )

        except Exception as e:
            self.logger.log_error(e, {"context": "loading archetypal memory"})

    def _save_to_disk(self):
        """Save patterns to disk."""
        patterns_file = self.storage_path / "patterns.json"

        try:
            data = []
            for pattern in self.patterns.values():
                data.append({
                    "pattern_id": pattern.pattern_id,
                    "name": pattern.name,
                    "description": pattern.description,
                    "symbols": pattern.symbols,
                    "narrative_structure": pattern.narrative_structure,
                    "activation_count": pattern.activation_count,
                    "strength": pattern.strength,
                    "examples": pattern.examples[-10:],  # Keep last 10 examples
                    "min_stage_access": pattern.min_stage_access
                })

            with open(patterns_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.log_error(e, {"context": "saving archetypal memory"})
