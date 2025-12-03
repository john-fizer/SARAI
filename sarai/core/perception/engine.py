"""
Perception Engine
=================

Multi-modal input processing calibrated to developmental stage.

Processes:
- Text via transformer encoding
- Numerical data with uncertainty quantification
- Symbolic patterns (archetypal recognition)

Stage-gated: early stages have narrow attention, later stages broader context.
"""

import numpy as np
from typing import Optional, List
from datetime import datetime

from sarai.types import (
    MultiModalInput, PerceivedState, AttentionScope, Symbol
)
from sarai.safety.logging import ComprehensiveLogger


class PerceptionEngine:
    """
    Multi-modal perception engine.

    Processes inputs through text, numerical, and symbolic channels.
    """

    def __init__(self, development_stage: int, logger: ComprehensiveLogger):
        """
        Initialize perception engine.

        Args:
            development_stage: Current developmental stage (1-12)
            logger: Comprehensive logger
        """
        self.stage = development_stage
        self.logger = logger

        self.logger.logger.info(
            f"Perception engine initialized at stage {development_stage}"
        )

    def perceive(self, input: MultiModalInput) -> PerceivedState:
        """
        Process input through all channels, filtered by developmental stage.

        Stage 1-3: Basic perception, limited context
        Stage 4-6: Emotional/pattern recognition added
        Stage 7-9: Relational and abstract layers
        Stage 10-12: Full holistic perception

        Args:
            input: Multi-modal input

        Returns:
            Perceived state
        """
        # Get attention scope for current stage
        attention_scope = self.get_attention_scope()

        # Process text if present
        encoded_text = None
        if input.text:
            encoded_text = self._encode_text(input.text, attention_scope)

        # Process numerical data if present
        processed_numerical = None
        if input.numerical:
            processed_numerical = self._process_numerical(input.numerical)

        # Extract symbols if stage allows
        extracted_symbols = []
        if self.stage >= 4 and attention_scope.symbolic_access:
            extracted_symbols = self._extract_symbols(input)

        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(
            encoded_text, processed_numerical, extracted_symbols
        )

        perceived_state = PerceivedState(
            raw_input=input,
            encoded_text=encoded_text,
            processed_numerical=processed_numerical,
            extracted_symbols=extracted_symbols,
            attention_scope=attention_scope,
            uncertainty=uncertainty,
            timestamp=datetime.now()
        )

        self.logger.log_perception(perceived_state)

        return perceived_state

    def get_attention_scope(self) -> AttentionScope:
        """
        Get attention scope based on developmental stage.

        Returns:
            Attention scope configuration
        """
        if self.stage <= 3:
            return AttentionScope(
                context_window=512,
                temporal_range=7,  # days
                abstraction_level=2,
                symbolic_access=False
            )
        elif self.stage <= 6:
            return AttentionScope(
                context_window=2048,
                temporal_range=30,
                abstraction_level=5,
                symbolic_access=True
            )
        elif self.stage <= 9:
            return AttentionScope(
                context_window=4096,
                temporal_range=90,
                abstraction_level=7,
                symbolic_access=True
            )
        else:  # 10-12
            return AttentionScope(
                context_window=8192,
                temporal_range=365,
                abstraction_level=10,
                symbolic_access=True
            )

    def _encode_text(self, text: str, scope: AttentionScope) -> np.ndarray:
        """
        Encode text to vector representation.

        In production: Use transformer model (BERT, etc.)
        Simplified: Random embeddings for now
        """
        # Truncate to context window
        truncated = text[:scope.context_window]

        # Simplified embedding (production would use actual transformer)
        # Return a dummy embedding vector
        embedding_dim = 768
        return np.random.randn(embedding_dim).astype(np.float32)

    def _process_numerical(
        self,
        numerical: dict[str, float]
    ) -> dict[str, float]:
        """
        Process numerical data with uncertainty quantification.

        Args:
            numerical: Dictionary of numerical values

        Returns:
            Processed numerical data
        """
        processed = {}

        for key, value in numerical.items():
            # Add uncertainty estimates (simplified)
            processed[key] = value
            processed[f"{key}_uncertainty"] = abs(value) * 0.05  # 5% uncertainty

        return processed

    def _extract_symbols(
        self,
        input: MultiModalInput
    ) -> List[Symbol]:
        """
        Extract symbolic/archetypal elements.

        In production: Sophisticated pattern matching
        Simplified: Keyword-based extraction
        """
        symbols = []

        if input.symbolic:
            for symbol_name in input.symbolic:
                symbols.append(Symbol(
                    name=symbol_name,
                    archetype="unknown",
                    confidence=0.7
                ))

        # Extract from text if present
        if input.text:
            archetypal_keywords = {
                "journey": "hero",
                "fall": "fall",
                "trial": "trial",
                "triumph": "victory",
                "loss": "tragedy",
                "return": "return"
            }

            text_lower = input.text.lower()
            for keyword, archetype in archetypal_keywords.items():
                if keyword in text_lower:
                    symbols.append(Symbol(
                        name=keyword,
                        archetype=archetype,
                        confidence=0.6
                    ))

        return symbols

    def _calculate_uncertainty(
        self,
        encoded_text: Optional[np.ndarray],
        processed_numerical: Optional[dict],
        extracted_symbols: List[Symbol]
    ) -> float:
        """Calculate overall perception uncertainty."""
        uncertainties = []

        # Text uncertainty (based on encoding confidence)
        if encoded_text is not None:
            # Simplified: variance of embedding
            uncertainties.append(float(np.std(encoded_text)))

        # Numerical uncertainty
        if processed_numerical:
            uncertainty_values = [
                v for k, v in processed_numerical.items()
                if "_uncertainty" in k
            ]
            if uncertainty_values:
                uncertainties.append(np.mean(uncertainty_values))

        # Symbol uncertainty
        if extracted_symbols:
            symbol_confidences = [s.confidence for s in extracted_symbols]
            uncertainties.append(1.0 - np.mean(symbol_confidences))

        if not uncertainties:
            return 0.5  # Default uncertainty

        return float(np.mean(uncertainties))

    def update_stage(self, new_stage: int):
        """Update developmental stage."""
        old_stage = self.stage
        self.stage = new_stage

        self.logger.log_state_change(
            "perception_stage",
            old_stage,
            new_stage,
            "Developmental progression"
        )
