"""
Relevance Router
================

Dynamic attention allocation across 12 archetypal competencies.

Functions as the "Thalamus" - allocating computational resources
to relevant modes of cognition based on current context.

Inputs:
- JEPA state features (uncertainty, novelty, complexity)
- Developmental stage (baseline)
- Memory signals

Outputs:
- Archetype weights (12-dimensional)
- Active modules (top-k)
- Compute budget allocation
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from sarai.core.routing.archetypes import ARCHETYPES, Archetype, get_archetype_by_stage
from sarai.core.world_model.state import StateFeatures
from sarai.safety.logging import ComprehensiveLogger


@dataclass
class ActivationResult:
    """Result of archetype activation."""
    weights: np.ndarray  # 12-dim activation vector
    active_modules: List[str]  # Top-k archetype names
    compute_budget: Dict[str, float]  # Archetype -> budget
    reasoning: str  # Why these activations


class RelevanceRouter:
    """
    Allocates attention to relevant archetypes based on context.

    The router performs a key cognitive function: deciding what modes
    of thinking are relevant right now.

    This prevents:
    - Trying to use all competencies at once (cognitive overload)
    - Missing relevant perspectives (blind spots)
    - Wasting resources on irrelevant processing
    """

    def __init__(
        self,
        current_stage: int,
        logger: Optional[ComprehensiveLogger] = None,
        top_k: int = 3
    ):
        """
        Initialize relevance router.

        Args:
            current_stage: Current developmental stage (1-12)
            logger: Optional logger
            top_k: Number of top archetypes to activate
        """
        self.current_stage = current_stage
        self.logger = logger
        self.top_k = top_k
        self.archetypes = ARCHETYPES

        # Activation history
        self.activation_history: List[ActivationResult] = []
        self.max_history = 100

        if self.logger:
            self.logger.logger.info(
                f"Relevance Router initialized at stage {current_stage}"
            )

    def activate(
        self,
        state_features: StateFeatures,
        memory_signals: Optional[Dict[str, Any]] = None
    ) -> ActivationResult:
        """
        Compute archetype activation weights.

        Args:
            state_features: Features from JEPA world state
            memory_signals: Optional signals from memory recall

        Returns:
            Activation result with weights and active modules
        """
        # 1. Get baseline weights from developmental stage
        baseline = self._get_baseline_weights()

        # 2. Compute dynamic adjustments from state features
        dynamic = self._compute_dynamic_adjustment(state_features)

        # 3. Compute memory-based adjustments
        memory = self._compute_memory_adjustment(memory_signals or {})

        # 4. Combine (weighted average)
        weights = (
            baseline * 0.5 +  # Developmental baseline
            dynamic * 0.3 +   # Context-driven
            memory * 0.2      # Memory-driven
        )

        # 5. Normalize
        weights = self._normalize(weights)

        # 6. Get top-k active modules
        active_indices = np.argsort(weights)[-self.top_k:][::-1]
        active_modules = [self.archetypes[i].name for i in active_indices]

        # 7. Allocate compute budget proportionally
        compute_budget = {
            self.archetypes[i].name: float(weights[i])
            for i in range(12)
        }

        # 8. Generate reasoning
        reasoning = self._generate_reasoning(
            active_modules, weights, state_features
        )

        # Create result
        result = ActivationResult(
            weights=weights,
            active_modules=active_modules,
            compute_budget=compute_budget,
            reasoning=reasoning
        )

        # Store in history
        self.activation_history.append(result)
        if len(self.activation_history) > self.max_history:
            self.activation_history.pop(0)

        # Log
        if self.logger:
            self.logger.logger.debug(
                f"Router activated: {', '.join(active_modules)} "
                f"(weights: {weights[active_indices]})"
            )

        return result

    def _get_baseline_weights(self) -> np.ndarray:
        """
        Baseline weights based on developmental stage.

        All stages up to current get baseline activation.
        Current stage gets maximum activation.

        Returns:
            12-dimensional weight vector
        """
        weights = np.zeros(12)

        # All completed stages get baseline
        for i in range(min(self.current_stage, 12)):
            # Progressive activation: later stages build on earlier
            weights[i] = 0.3 + (i / 12) * 0.4  # 0.3 to 0.7

        # Current stage gets maximum activation
        if self.current_stage <= 12:
            weights[self.current_stage - 1] = 1.0

        return weights

    def _compute_dynamic_adjustment(
        self,
        features: StateFeatures
    ) -> np.ndarray:
        """
        Dynamic adjustment based on JEPA state features.

        Different situations call for different modes of cognition.

        Args:
            features: State features (uncertainty, complexity, etc.)

        Returns:
            12-dimensional adjustment vector
        """
        weights = np.ones(12) * 0.3  # Baseline

        # High uncertainty → boost analytical archetypes
        if features.uncertainty > 0.6:
            weights[5] += 0.4  # Analysis (Virgo)
            weights[9] += 0.3  # Structure (Capricorn)
            weights[2] += 0.2  # Communication (Gemini) - gather info

        # High novelty → boost adaptive/exploratory archetypes
        if features.novelty > 0.6:
            weights[7] += 0.4  # Transformation (Scorpio)
            weights[10] += 0.3  # Innovation (Aquarius)
            weights[8] += 0.2  # Meaning (Sagittarius) - make sense

        # High complexity → boost integrative archetypes
        if features.complexity > 0.6:
            weights[6] += 0.3  # Relationship (Libra) - balance
            weights[11] += 0.4  # Unity (Pisces) - holistic view
            weights[9] += 0.2  # Structure (Capricorn) - organize

        # High stakes → boost careful/protective archetypes
        if features.stakes > 0.7:
            weights[3] += 0.3  # Memory (Cancer) - learn from past
            weights[5] += 0.3  # Analysis (Virgo) - be precise
            weights[9] += 0.2  # Structure (Capricorn) - plan carefully

        # High time pressure → boost decisive archetypes
        if features.time_pressure > 0.7:
            weights[0] += 0.4  # Initiative (Aries) - act now
            weights[4] += 0.2  # Expression (Leo) - commit
            weights[7] += 0.2  # Transformation (Scorpio) - cut through

        # High irreversibility → boost careful archetypes
        if features.irreversibility > 0.7:
            weights[3] += 0.3  # Memory (Cancer) - precedent
            weights[5] += 0.4  # Analysis (Virgo) - scrutinize
            weights[6] += 0.2  # Relationship (Libra) - consider impact

        return weights

    def _compute_memory_adjustment(
        self,
        memory_signals: Dict[str, Any]
    ) -> np.ndarray:
        """
        Adjustment based on memory recall.

        Memories can indicate which modes were successful before.

        Args:
            memory_signals: Signals from memory system

        Returns:
            12-dimensional adjustment vector
        """
        weights = np.ones(12) * 0.5  # Neutral baseline

        # If memories indicate past success with certain archetypes
        if "successful_archetypes" in memory_signals:
            for arch_name in memory_signals["successful_archetypes"]:
                # Boost that archetype
                for i, arch in enumerate(self.archetypes):
                    if arch.name == arch_name:
                        weights[i] += 0.3

        # If memories indicate failures
        if "failed_archetypes" in memory_signals:
            for arch_name in memory_signals["failed_archetypes"]:
                # Reduce that archetype
                for i, arch in enumerate(self.archetypes):
                    if arch.name == arch_name:
                        weights[i] -= 0.2

        # Clip to valid range
        weights = np.clip(weights, 0.1, 1.0)

        return weights

    def _normalize(self, weights: np.ndarray) -> np.ndarray:
        """
        Normalize weights to sum to 1.

        Args:
            weights: Raw weights

        Returns:
            Normalized weights
        """
        total = np.sum(weights)
        if total > 0:
            return weights / total
        else:
            # Fall back to uniform if all zero
            return np.ones(12) / 12.0

    def _generate_reasoning(
        self,
        active_modules: List[str],
        weights: np.ndarray,
        features: StateFeatures
    ) -> str:
        """
        Generate human-readable reasoning for activation.

        Args:
            active_modules: Top active archetypes
            weights: Full weight vector
            features: State features

        Returns:
            Reasoning string
        """
        parts = [f"Activated: {', '.join(active_modules)}"]

        # Add context reasons
        reasons = []

        if features.uncertainty > 0.6:
            reasons.append("high uncertainty calls for analysis")

        if features.novelty > 0.6:
            reasons.append("novel situation requires adaptation")

        if features.complexity > 0.6:
            reasons.append("complexity needs integration")

        if features.stakes > 0.7:
            reasons.append("high stakes demand care")

        if features.time_pressure > 0.7:
            reasons.append("time pressure requires decisiveness")

        if reasons:
            parts.append(f"because {', '.join(reasons)}")

        # Add developmental context
        current_archetype = get_archetype_by_stage(self.current_stage)
        parts.append(f"(stage: {current_archetype.sign})")

        return " ".join(parts)

    def update_stage(self, new_stage: int):
        """Update developmental stage and recalculate baselines."""
        old_stage = self.current_stage
        self.current_stage = new_stage

        if self.logger:
            self.logger.log_state_change(
                "router_stage",
                old_stage,
                new_stage,
                "Developmental progression"
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        if not self.activation_history:
            return {
                "total_activations": 0,
                "current_stage": self.current_stage,
                "most_activated": []
            }

        # Count activations by archetype
        activation_counts = {arch.name: 0 for arch in self.archetypes}

        for result in self.activation_history:
            for module in result.active_modules:
                activation_counts[module] += 1

        # Get top activated
        most_activated = sorted(
            activation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_activations": len(self.activation_history),
            "current_stage": self.current_stage,
            "most_activated": [
                {"name": name, "count": count}
                for name, count in most_activated
            ],
            "avg_active_modules": (
                sum(len(r.active_modules) for r in self.activation_history)
                / len(self.activation_history)
            )
        }
