"""
JEPA World Model Demonstration
===============================

Shows how JEPA tracks latent state and predicts future states.

Author: John Fizer
"""

import numpy as np
import sys
sys.path.append('..')

from sarai.core.world_model.jepa import JEPAWorldModel
from sarai.safety.logging import ComprehensiveLogger


def demonstrate_jepa():
    """Demonstrate JEPA world modeling."""

    print("=" * 80)
    print("JEPA WORLD MODEL DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize
    logger = ComprehensiveLogger("./demo_logs")
    jepa = JEPAWorldModel(
        embedding_dim=768,
        latent_dim=256,
        logger=logger
    )

    print("✅ JEPA initialized")
    print(f"   Embedding dim: 768, Latent dim: 256")
    print()

    # Simulate a sequence of observations
    print("📊 Simulating observation sequence...")
    print()

    observations = [
        ("calm", np.random.randn(768) * 0.5),
        ("calm", np.random.randn(768) * 0.5 + 0.1),
        ("calm", np.random.randn(768) * 0.5 + 0.2),
        ("SUDDEN CHANGE", np.random.randn(768) * 2.0),  # Big change
        ("stabilizing", np.random.randn(768) * 1.0),
        ("stabilizing", np.random.randn(768) * 0.8),
    ]

    for i, (label, embedding) in enumerate(observations, 1):
        print(f"Observation {i}: {label}")

        # Update JEPA
        state = jepa.update(embedding, metadata={"label": label})

        # Show results
        print(f"  Prediction Error: {state.prediction_error:.4f}")
        print(f"  Surprise: {state.surprise:.4f}")

        if state.surprise > 0.7:
            print(f"  🚨 HIGH SURPRISE - Something unexpected!")
        elif state.surprise > 0.5:
            print(f"  ⚠️  Moderate surprise")
        else:
            print(f"  ✓  Low surprise - as expected")

        print()

    # Show statistics
    print("=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)

    stats = jepa.get_stats()
    print(f"Total observations: {stats['state_history_length']}")
    print(f"Average prediction error: {stats['avg_prediction_error']:.4f}")
    print(f"Average surprise: {stats['avg_surprise']:.4f}")
    print()

    # State features
    features = jepa.get_state_features()
    print("EXTRACTED STATE FEATURES:")
    print(f"  Uncertainty: {features.uncertainty:.2f}")
    print(f"  Novelty: {features.novelty:.2f}")
    print(f"  Complexity: {features.complexity:.2f}")
    print()

    print("✅ JEPA demonstration complete!")
    print()


if __name__ == "__main__":
    demonstrate_jepa()
