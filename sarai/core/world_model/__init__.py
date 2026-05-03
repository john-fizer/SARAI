"""
JEPA World Model for SARAI
===========================

Joint Embedding Predictive Architecture that maintains latent state
and predicts future states.
"""

from sarai.core.world_model.jepa import JEPAWorldModel
from sarai.core.world_model.state import WorldState

__all__ = ["JEPAWorldModel", "WorldState"]
