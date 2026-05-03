"""
World State Representation
==========================

Dataclasses for world state tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import numpy as np


@dataclass
class WorldState:
    """
    Complete world state at a point in time.
    """
    timestamp: datetime
    latent_state: np.ndarray  # Latent representation
    prediction_error: float  # How wrong was the last prediction
    surprise: float  # Normalized surprise (0-1)
    state_delta: Optional[np.ndarray] = None  # Change from last state
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "latent_state": self.latent_state.tolist(),
            "prediction_error": self.prediction_error,
            "surprise": self.surprise,
            "state_delta": self.state_delta.tolist() if self.state_delta is not None else None,
            "metadata": self.metadata
        }


@dataclass
class StateFeatures:
    """
    Extracted features from state for routing and decision-making.
    """
    uncertainty: float  # How uncertain is the state
    time_pressure: float  # How urgent is action
    irreversibility: float  # How reversible are actions
    complexity: float  # How complex is the situation
    novelty: float  # How novel/unfamiliar
    stakes: float  # How high are the stakes

    @classmethod
    def from_world_state(cls, state: WorldState) -> 'StateFeatures':
        """Extract features from world state."""
        # Uncertainty from prediction error
        uncertainty = min(state.prediction_error, 1.0)

        # Surprise indicates novelty
        novelty = state.surprise

        # Delta magnitude indicates complexity
        complexity = 0.5
        if state.state_delta is not None:
            complexity = min(float(np.linalg.norm(state.state_delta)) / 10.0, 1.0)

        # Defaults for others (would be computed from context in production)
        time_pressure = 0.5
        irreversibility = 0.5
        stakes = 0.5

        return cls(
            uncertainty=uncertainty,
            time_pressure=time_pressure,
            irreversibility=irreversibility,
            complexity=complexity,
            novelty=novelty,
            stakes=stakes
        )
