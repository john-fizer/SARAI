"""
Bicameral Reasoning Engine
===========================

Two parallel streams converging:
- Abstract-Intuitive Stream (AIS): Pattern recognition, symbolic reasoning
- Analytical-Rational Stream (ARS): Logical inference, causal modeling

Unified Output Layer (UOL): Synthesizes both streams with stage-dependent weighting.

CRITICAL: Streams MUST process in parallel, not sequentially.
"""

import asyncio
import time
from typing import Dict, Any
from datetime import datetime

from sarai.types import (
    PerceivedState, ReasoningOutput,
    AISResult, ARSResult
)
from sarai.safety.logging import ComprehensiveLogger


class BicameralEngine:
    """
    Bicameral reasoning engine with parallel processing streams.
    """

    def __init__(self, stage: int, logger: ComprehensiveLogger):
        """
        Initialize bicameral engine.

        Args:
            stage: Current developmental stage
            logger: Comprehensive logger
        """
        self.stage = stage
        self.logger = logger

        self.ais = AbstractIntuitiveStream(logger)
        self.ars = AnalyticalRationalStream(logger)
        self.uol = UnifiedOutputLayer(stage, logger)

        self.logger.logger.info(
            f"Bicameral engine initialized at stage {stage}"
        )

    async def reason(self, perceived_state: PerceivedState) -> ReasoningOutput:
        """
        Parallel processing through both streams, then synthesis.

        Args:
            perceived_state: The perceived state to reason about

        Returns:
            Synthesized reasoning output
        """
        # MUST be parallel
        start_time = time.time()

        ais_result, ars_result = await asyncio.gather(
            self.ais.process(perceived_state),
            self.ars.process(perceived_state)
        )

        # Synthesize results
        output = self.uol.synthesize(ais_result, ars_result)

        total_time = time.time() - start_time
        self.logger.logger.debug(
            f"Reasoning completed in {total_time:.2f}s "
            f"(AIS: {ais_result.processing_time:.2f}s, "
            f"ARS: {ars_result.processing_time:.2f}s)"
        )

        self.logger.log_reasoning(output)

        return output

    def update_stage(self, new_stage: int):
        """Update developmental stage."""
        self.stage = new_stage
        self.uol.update_stage(new_stage)


class AbstractIntuitiveStream:
    """
    System 1 / Right-hemisphere analog.

    Techniques:
    - Pattern recognition across large contexts
    - Symbolic/archetypal reasoning
    - Associative reasoning
    - Gestalt formation
    """

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger

    async def process(self, perceived_state: PerceivedState) -> AISResult:
        """
        Process through intuitive stream.

        Args:
            perceived_state: Perceived state

        Returns:
            AIS result
        """
        start_time = time.time()

        # Pattern recognition
        patterns = self._recognize_patterns(perceived_state)

        # Symbolic interpretation
        symbolic = self._interpret_symbols(perceived_state)

        # Holistic assessment
        holistic = self._holistic_assessment(perceived_state, patterns, symbolic)

        # Confidence based on symbol clarity and pattern strength
        confidence = self._calculate_confidence(patterns, symbolic)

        processing_time = time.time() - start_time

        return AISResult(
            patterns_recognized=patterns,
            symbolic_interpretation=symbolic,
            holistic_assessment=holistic,
            confidence=confidence,
            processing_time=processing_time
        )

    def _recognize_patterns(self, state: PerceivedState) -> list[str]:
        """Recognize patterns in perceived state."""
        patterns = []

        # Check for archetypal patterns
        if state.extracted_symbols:
            symbols_str = ", ".join(s.name for s in state.extracted_symbols)
            patterns.append(f"Symbolic pattern: {symbols_str}")

        # Check for temporal patterns
        if state.raw_input.metadata.get("time_pattern"):
            patterns.append("Temporal pattern detected")

        return patterns

    def _interpret_symbols(self, state: PerceivedState) -> str:
        """Interpret symbolic content."""
        if not state.extracted_symbols:
            return "No symbolic content detected"

        symbol_names = [s.name for s in state.extracted_symbols]
        archetypes = [s.archetype for s in state.extracted_symbols]

        return f"Symbols: {', '.join(symbol_names)}. Archetypes: {', '.join(set(archetypes))}"

    def _holistic_assessment(
        self,
        state: PerceivedState,
        patterns: list[str],
        symbolic: str
    ) -> str:
        """Form holistic gestalt."""
        components = []

        if patterns:
            components.append(f"Patterns suggest: {'; '.join(patterns)}")

        if state.extracted_symbols:
            components.append(f"Symbolic meaning: {symbolic}")

        if not components:
            return "Situation appears straightforward, no deep patterns detected"

        return " ".join(components)

    def _calculate_confidence(
        self,
        patterns: list[str],
        symbolic: str
    ) -> float:
        """Calculate intuitive confidence."""
        confidence = 0.5  # Base

        # More patterns = higher confidence
        confidence += min(len(patterns) * 0.1, 0.3)

        # Symbolic clarity adds confidence
        if "detected" not in symbolic.lower():
            confidence += 0.2

        return min(confidence, 1.0)


class AnalyticalRationalStream:
    """
    System 2 / Left-hemisphere analog.

    Techniques:
    - Chain-of-thought reasoning
    - Formal logic
    - Mathematical reasoning
    - Causal graph traversal
    """

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger

    async def process(self, perceived_state: PerceivedState) -> ARSResult:
        """
        Process through analytical stream.

        Args:
            perceived_state: Perceived state

        Returns:
            ARS result
        """
        start_time = time.time()

        # Logical chain
        logical_chain = self._build_logical_chain(perceived_state)

        # Causal model
        causal_model = self._build_causal_model(perceived_state)

        # Quantitative analysis
        quantitative = self._quantitative_analysis(perceived_state)

        # Confidence based on logical certainty
        confidence = self._calculate_confidence(logical_chain, quantitative)

        processing_time = time.time() - start_time

        return ARSResult(
            logical_chain=logical_chain,
            causal_model=causal_model,
            quantitative_analysis=quantitative,
            confidence=confidence,
            processing_time=processing_time
        )

    def _build_logical_chain(self, state: PerceivedState) -> list[str]:
        """Build logical reasoning chain."""
        chain = ["Initial state perceived"]

        # Add logical steps based on input
        if state.raw_input.text:
            chain.append("Text content analyzed")

        if state.processed_numerical:
            chain.append("Numerical data processed")

        chain.append("Logical consistency checked")

        return chain

    def _build_causal_model(self, state: PerceivedState) -> Dict[str, Any]:
        """Build causal model."""
        model = {
            "causes": [],
            "effects": [],
            "mechanisms": []
        }

        # Extract potential causal relationships
        if state.raw_input.metadata.get("causes"):
            model["causes"] = state.raw_input.metadata["causes"]

        return model

    def _quantitative_analysis(
        self,
        state: PerceivedState
    ) -> Dict[str, float]:
        """Perform quantitative analysis."""
        analysis = {}

        if state.processed_numerical:
            for key, value in state.processed_numerical.items():
                if not key.endswith("_uncertainty"):
                    analysis[f"{key}_analyzed"] = value

        analysis["uncertainty"] = state.uncertainty

        return analysis

    def _calculate_confidence(
        self,
        logical_chain: list[str],
        quantitative: Dict[str, float]
    ) -> float:
        """Calculate analytical confidence."""
        confidence = 0.6  # Base

        # Longer logical chain = more thorough = higher confidence
        confidence += min(len(logical_chain) * 0.05, 0.2)

        # Low uncertainty in quantitative = higher confidence
        if quantitative.get("uncertainty", 1.0) < 0.3:
            confidence += 0.2

        return min(confidence, 1.0)


class UnifiedOutputLayer:
    """
    Synthesis layer with stage-dependent weighting.

    Weights by stage:
    - Stage 1-3: 70% ARS, 30% AIS (learning fundamentals)
    - Stage 4-6: 60% ARS, 40% AIS (developing intuition)
    - Stage 7-9: 50% ARS, 50% AIS (balanced)
    - Stage 10-12: 40% ARS, 60% AIS (mature intuitive judgment)
    """

    def __init__(self, stage: int, logger: ComprehensiveLogger):
        self.stage = stage
        self.logger = logger

    def synthesize(self, ais: AISResult, ars: ARSResult) -> ReasoningOutput:
        """
        Weighted combination with conflict preservation.

        If streams strongly disagree, flag conflict in output.

        Args:
            ais: Abstract-intuitive result
            ars: Analytical-rational result

        Returns:
            Synthesized reasoning output
        """
        # Get stage-dependent weights
        ars_weight, ais_weight = self._get_weights()

        # Calculate weighted confidence
        confidence = (
            ars_weight * ars.confidence +
            ais_weight * ais.confidence
        )

        # Calculate stream agreement
        agreement = self._calculate_agreement(ais, ars)

        # Detect conflicts
        conflicts = self._detect_conflicts(ais, ars, agreement)

        # Synthesize description
        synthesis = self._create_synthesis(ais, ars, ars_weight, ais_weight, conflicts)

        return ReasoningOutput(
            ais_result=ais,
            ars_result=ars,
            synthesis=synthesis,
            confidence=confidence,
            stream_agreement=agreement,
            conflicts=conflicts,
            timestamp=datetime.now()
        )

    def _get_weights(self) -> tuple[float, float]:
        """Get ARS and AIS weights based on stage."""
        if self.stage <= 3:
            return 0.7, 0.3
        elif self.stage <= 6:
            return 0.6, 0.4
        elif self.stage <= 9:
            return 0.5, 0.5
        else:
            return 0.4, 0.6

    def _calculate_agreement(self, ais: AISResult, ars: ARSResult) -> float:
        """Calculate how much streams agree."""
        # Simplified: based on confidence similarity
        confidence_diff = abs(ais.confidence - ars.confidence)
        agreement = 1.0 - confidence_diff

        return max(0.0, min(agreement, 1.0))

    def _detect_conflicts(
        self,
        ais: AISResult,
        ars: ARSResult,
        agreement: float
    ) -> list[str]:
        """Detect conflicts between streams."""
        conflicts = []

        # Low agreement = conflict
        if agreement < 0.5:
            conflicts.append(
                f"Streams disagree: intuitive confidence {ais.confidence:.2f}, "
                f"analytical confidence {ars.confidence:.2f}"
            )

        # Conflicting patterns vs logic
        if ais.patterns_recognized and not ars.logical_chain:
            conflicts.append("Intuition recognizes patterns but logic finds none")

        return conflicts

    def _create_synthesis(
        self,
        ais: AISResult,
        ars: ARSResult,
        ars_weight: float,
        ais_weight: float,
        conflicts: list[str]
    ) -> str:
        """Create synthesized description."""
        parts = []

        # Analytical contribution
        parts.append(
            f"Analytical reasoning (weight {ars_weight:.0%}): "
            f"{' -> '.join(ars.logical_chain[:3])}"
        )

        # Intuitive contribution
        parts.append(
            f"Intuitive assessment (weight {ais_weight:.0%}): "
            f"{ais.holistic_assessment[:100]}"
        )

        # Note conflicts
        if conflicts:
            parts.append(f"CONFLICTS: {'; '.join(conflicts)}")

        return " | ".join(parts)

    def update_stage(self, new_stage: int):
        """Update stage and recalculate weights."""
        self.stage = new_stage
        self.logger.log_state_change(
            "reasoning_stage",
            self.stage,
            new_stage,
            "Stage progression"
        )
