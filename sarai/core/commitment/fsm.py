"""
Commit Finite State Machine
============================

FSM for commitment lifecycle:
EXPLORE → EVALUATE → COMMIT → EXECUTE → REVIEW → (REOPEN rare)
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


class CommitState(Enum):
    """States in the commit lifecycle."""
    EXPLORE = "explore"        # Gathering options
    EVALUATE = "evaluate"      # Scoring + gating
    COMMIT = "commit"          # Binding decision made
    EXECUTE = "execute"        # Action in progress
    REVIEW = "review"          # Outcome assessment
    REOPEN = "reopen"          # Rare contradiction detected


@dataclass
class StateTransition:
    """A state transition record."""
    from_state: CommitState
    to_state: CommitState
    timestamp: datetime
    reason: str
    metadata: Dict[str, Any]


class CommitFSM:
    """
    Finite state machine for commitment lifecycle.

    Enforces valid transitions and tracks state history.
    """

    # Valid transitions
    VALID_TRANSITIONS = {
        CommitState.EXPLORE: [CommitState.EVALUATE, CommitState.EXPLORE],
        CommitState.EVALUATE: [CommitState.COMMIT, CommitState.EXPLORE],
        CommitState.COMMIT: [CommitState.EXECUTE, CommitState.REOPEN],
        CommitState.EXECUTE: [CommitState.REVIEW],
        CommitState.REVIEW: [CommitState.EXPLORE, CommitState.REOPEN],
        CommitState.REOPEN: [CommitState.EXPLORE]
    }

    def __init__(self, initial_state: CommitState = CommitState.EXPLORE):
        """Initialize FSM."""
        self.current_state = initial_state
        self.transition_history: list[StateTransition] = []
        self.state_entry_time = datetime.now()

    def can_transition_to(self, target_state: CommitState) -> bool:
        """Check if transition to target state is valid."""
        return target_state in self.VALID_TRANSITIONS.get(self.current_state, [])

    def transition(
        self,
        target_state: CommitState,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Attempt to transition to target state.

        Returns:
            True if transition successful, False if invalid
        """
        if not self.can_transition_to(target_state):
            return False

        # Record transition
        transition = StateTransition(
            from_state=self.current_state,
            to_state=target_state,
            timestamp=datetime.now(),
            reason=reason,
            metadata=metadata or {}
        )

        self.transition_history.append(transition)
        self.current_state = target_state
        self.state_entry_time = datetime.now()

        return True

    def time_in_current_state(self) -> float:
        """Get seconds in current state."""
        return (datetime.now() - self.state_entry_time).total_seconds()

    def get_state_path(self) -> list[CommitState]:
        """Get path of states traversed."""
        path = [self.transition_history[0].from_state] if self.transition_history else []
        path.extend([t.to_state for t in self.transition_history])
        return path

    def reset(self):
        """Reset to initial state."""
        self.current_state = CommitState.EXPLORE
        self.transition_history = []
        self.state_entry_time = datetime.now()
