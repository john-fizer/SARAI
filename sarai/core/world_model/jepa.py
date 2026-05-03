"""
JEPA World Model
================

Joint Embedding Predictive Architecture for maintaining world state
and predicting future states.

This is a self-supervised model that:
1. Encodes observations into latent space
2. Predicts next latent state
3. Computes prediction error (surprise)
4. Updates current state belief

NOT A GENERATIVE MODEL - predicts in representation space, not pixel/token space.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from sarai.core.world_model.state import WorldState, StateFeatures
from sarai.safety.logging import ComprehensiveLogger


class JEPAWorldModel(nn.Module):
    """
    Joint Embedding Predictive Architecture for world modeling.

    Maintains latent state and predicts next state from current state.
    Uses prediction error as a surprise signal for attention allocation.
    """

    def __init__(
        self,
        embedding_dim: int = 768,
        latent_dim: int = 256,
        logger: Optional[ComprehensiveLogger] = None
    ):
        """
        Initialize JEPA model.

        Args:
            embedding_dim: Input embedding dimension
            latent_dim: Latent state dimension
            logger: Optional logger
        """
        super().__init__()

        self.embedding_dim = embedding_dim
        self.latent_dim = latent_dim
        self.logger = logger

        # Encoder: embedding → latent state
        self.encoder = nn.Sequential(
            nn.Linear(embedding_dim, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, latent_dim),
            nn.LayerNorm(latent_dim)
        )

        # Predictor: latent state → next latent state
        self.predictor = nn.Sequential(
            nn.Linear(latent_dim, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, latent_dim),
            nn.LayerNorm(latent_dim)
        )

        # State tracking
        self.current_state: Optional[torch.Tensor] = None
        self.predicted_state: Optional[torch.Tensor] = None
        self.prediction_error: float = 0.0
        self.surprise: float = 0.0

        # History for learning
        self.state_history: list[WorldState] = []
        self.max_history = 100

        if self.logger:
            self.logger.logger.info(
                f"JEPA World Model initialized: "
                f"embedding_dim={embedding_dim}, latent_dim={latent_dim}"
            )

    def encode(self, embedding: np.ndarray) -> torch.Tensor:
        """
        Encode perception embedding to latent state.

        Args:
            embedding: Perception embedding (numpy array)

        Returns:
            Latent state tensor
        """
        # Handle batching
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)

        # Convert to tensor
        x = torch.from_numpy(embedding).float()

        # Encode
        with torch.no_grad():
            latent = self.encoder(x)

        return latent.squeeze(0)  # Remove batch dim

    def predict(self, state: torch.Tensor) -> torch.Tensor:
        """
        Predict next state from current state.

        Args:
            state: Current latent state

        Returns:
            Predicted next state
        """
        # Handle batching
        if state.ndim == 1:
            state = state.unsqueeze(0)

        with torch.no_grad():
            predicted = self.predictor(state)

        return predicted.squeeze(0)

    def compute_error(
        self,
        predicted: torch.Tensor,
        observed: torch.Tensor
    ) -> float:
        """
        Compute prediction error (MSE).

        Args:
            predicted: Predicted state
            observed: Observed state

        Returns:
            Prediction error (float)
        """
        error = torch.mean((predicted - observed) ** 2).item()
        return error

    def compute_surprise(self, prediction_error: float) -> float:
        """
        Convert prediction error to surprise signal (0-1).

        Uses sigmoid to map unbounded error to [0, 1].

        Args:
            prediction_error: Raw prediction error

        Returns:
            Surprise in [0, 1]
        """
        # Sigmoid with scaling
        surprise = 1.0 / (1.0 + np.exp(-5.0 * (prediction_error - 0.5)))
        return float(surprise)

    def update(
        self,
        observation_embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorldState:
        """
        Update world model with new observation.

        This is the main method called on each perception cycle.

        Args:
            observation_embedding: Embedding from perception engine
            metadata: Optional metadata about observation

        Returns:
            Updated world state
        """
        # Encode observation
        observed_state = self.encode(observation_embedding)

        # Compute prediction error if we have a previous state
        if self.current_state is not None:
            # We predicted this state last cycle
            if self.predicted_state is not None:
                self.prediction_error = self.compute_error(
                    self.predicted_state,
                    observed_state
                )
            else:
                self.prediction_error = 0.0

            # Compute state delta
            state_delta = (observed_state - self.current_state).detach().numpy()
        else:
            # First observation - no prediction to compare
            self.prediction_error = 0.0
            state_delta = None

        # Compute surprise
        self.surprise = self.compute_surprise(self.prediction_error)

        # Update current state
        self.current_state = observed_state

        # Predict next state
        self.predicted_state = self.predict(self.current_state)

        # Create world state
        world_state = WorldState(
            timestamp=datetime.now(),
            latent_state=self.current_state.detach().numpy(),
            prediction_error=self.prediction_error,
            surprise=self.surprise,
            state_delta=state_delta,
            metadata=metadata or {}
        )

        # Store in history
        self.state_history.append(world_state)
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)

        # Log
        if self.logger:
            self.logger.logger.debug(
                f"JEPA state updated: error={self.prediction_error:.4f}, "
                f"surprise={self.surprise:.4f}"
            )

        return world_state

    def get_state_features(self) -> StateFeatures:
        """
        Extract state features for routing.

        Returns:
            State features for decision-making
        """
        if not self.state_history:
            # No history yet, return defaults
            return StateFeatures(
                uncertainty=0.5,
                time_pressure=0.5,
                irreversibility=0.5,
                complexity=0.5,
                novelty=0.5,
                stakes=0.5
            )

        # Get latest state
        latest = self.state_history[-1]

        return StateFeatures.from_world_state(latest)

    def get_state_delta(self) -> Optional[np.ndarray]:
        """Get most recent state delta."""
        if self.state_history:
            return self.state_history[-1].state_delta
        return None

    def reset(self):
        """Reset world model state."""
        self.current_state = None
        self.predicted_state = None
        self.prediction_error = 0.0
        self.surprise = 0.0

        if self.logger:
            self.logger.logger.info("JEPA state reset")

    def save(self, path: str):
        """Save model weights."""
        torch.save({
            'encoder': self.encoder.state_dict(),
            'predictor': self.predictor.state_dict(),
            'embedding_dim': self.embedding_dim,
            'latent_dim': self.latent_dim
        }, path)

        if self.logger:
            self.logger.logger.info(f"JEPA model saved to {path}")

    def load(self, path: str):
        """Load model weights."""
        checkpoint = torch.load(path)
        self.encoder.load_state_dict(checkpoint['encoder'])
        self.predictor.load_state_dict(checkpoint['predictor'])

        if self.logger:
            self.logger.logger.info(f"JEPA model loaded from {path}")

    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics."""
        return {
            "current_prediction_error": self.prediction_error,
            "current_surprise": self.surprise,
            "state_history_length": len(self.state_history),
            "has_current_state": self.current_state is not None,
            "avg_prediction_error": (
                np.mean([s.prediction_error for s in self.state_history[-20:]])
                if len(self.state_history) > 0 else 0.0
            ),
            "avg_surprise": (
                np.mean([s.surprise for s in self.state_history[-20:]])
                if len(self.state_history) > 0 else 0.0
            )
        }
