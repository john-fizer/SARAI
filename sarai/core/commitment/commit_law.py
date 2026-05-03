"""
Commit Law
==========

The binding mechanism that converts evaluated options into committed reality.

"Commit creates time, identity, and accountability."

This is NOT just decision-making. A commitment:
1. Creates a binding claim about reality
2. Generates predictions to be verified
3. Establishes accountability for outcomes
4. Can be reopened only under strict conditions

The Commit Law prevents:
- Endless deliberation (decision paralysis)
- Responsibility diffusion (no one accountable)
- Prediction-free action (no learning loop)
- Contradiction accumulation (epistemic debt)
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from sarai.core.commitment.fsm import CommitFSM, CommitState
from sarai.core.commitment.records import Commit, CommitRecord
from sarai.types import Action, EthicalAssessment, ReasoningOutput
from sarai.safety.logging import ComprehensiveLogger


class CommitLaw:
    """
    Enforcement of binding commitments.

    Manages the FSM and creates immutable commit records.
    """

    def __init__(self, logger: ComprehensiveLogger):
        """
        Initialize Commit Law.

        Args:
            logger: Comprehensive logger
        """
        self.logger = logger
        self.fsm = CommitFSM()
        self.records = CommitRecord()

        # Current evaluation context (before commit)
        self.current_options: List[Dict[str, Any]] = []
        self.current_scores: Dict[str, float] = {}
        self.current_reasoning: Optional[ReasoningOutput] = None

        self.logger.logger.info("Commit Law initialized")

    def enter_exploration(self, context: Dict[str, Any]):
        """
        Enter exploration phase.

        Args:
            context: Context for exploration
        """
        success = self.fsm.transition(
            CommitState.EXPLORE,
            "Beginning exploration",
            {"context": context}
        )

        if success:
            self.current_options = []
            self.logger.logger.debug("Entered EXPLORE state")

    def add_option(self, option: Dict[str, Any]):
        """Add an option to current exploration."""
        if self.fsm.current_state != CommitState.EXPLORE:
            self.logger.logger.warning(
                f"Cannot add option in {self.fsm.current_state.value} state"
            )
            return

        self.current_options.append(option)

    def begin_evaluation(
        self,
        reasoning: ReasoningOutput,
        scores: Dict[str, float]
    ):
        """
        Begin evaluation of options.

        Args:
            reasoning: Reasoning output from bicameral engine
            scores: Value scores for options
        """
        success = self.fsm.transition(
            CommitState.EVALUATE,
            "Evaluating options",
            {
                "num_options": len(self.current_options),
                "reasoning_confidence": reasoning.confidence
            }
        )

        if success:
            self.current_reasoning = reasoning
            self.current_scores = scores
            self.logger.logger.debug("Entered EVALUATE state")

    def decide(
        self,
        action: Action,
        ethical_assessment: EthicalAssessment,
        predicted_outcome: Any,
        jepa_prediction_error: float
    ) -> Optional[Commit]:
        """
        Make a binding commitment.

        This is the critical step where evaluation becomes commitment.

        Args:
            action: The action being committed to
            ethical_assessment: Ethical evaluation results
            predicted_outcome: What we expect to happen
            jepa_prediction_error: Current JEPA prediction error

        Returns:
            Commit object if successful, None if commitment rejected
        """
        if self.fsm.current_state != CommitState.EVALUATE:
            self.logger.logger.error(
                f"Cannot commit from {self.fsm.current_state.value} state"
            )
            return None

        # Check if commitment should be made
        if not self._should_commit(ethical_assessment):
            self.logger.logger.warning("Commitment blocked by safety/ethics")
            # Return to exploration
            self.fsm.transition(
                CommitState.EXPLORE,
                "Commitment blocked, returning to exploration"
            )
            return None

        # Create commit
        commit_id = str(uuid.uuid4())[:8]

        commit = Commit(
            commit_id=commit_id,
            timestamp=datetime.now(),
            state_claimed={
                "action_type": action.action_type.value,
                "action_description": action.description,
                "action_parameters": action.parameters
            },
            reasoning=self.current_reasoning.synthesis if self.current_reasoning else "No reasoning recorded",
            confidence=self.current_reasoning.confidence if self.current_reasoning else 0.5,
            safety_cleared=True,  # Checked by _should_commit
            ethics_approved=ethical_assessment.permitted,
            ethical_scores={
                "deontological": ethical_assessment.deontological_score,
                "consequentialist": ethical_assessment.consequentialist_score,
                "virtue": ethical_assessment.virtue_score
            },
            predicted_outcome=predicted_outcome,
            jepa_prediction_error=jepa_prediction_error,
            metadata={
                "stream_agreement": self.current_reasoning.stream_agreement if self.current_reasoning else 0.5,
                "conflicts": self.current_reasoning.conflicts if self.current_reasoning else []
            }
        )

        # Add to records
        self.records.add_commit(commit)

        # Transition to COMMIT state
        success = self.fsm.transition(
            CommitState.COMMIT,
            f"Committed to: {action.description}",
            {"commit_id": commit_id}
        )

        if success:
            commit.add_audit_entry("Commitment created")
            self.logger.log_decision(action, commit.reasoning)
            self.logger.logger.info(
                f"Commitment {commit_id} created: {action.description}"
            )

        return commit

    def begin_execution(self, commit_id: str):
        """
        Begin executing a commitment.

        Args:
            commit_id: ID of commit being executed
        """
        commit = self.records.get_commit(commit_id)
        if not commit:
            self.logger.logger.error(f"Commit {commit_id} not found")
            return

        success = self.fsm.transition(
            CommitState.EXECUTE,
            f"Executing commit {commit_id}",
            {"commit_id": commit_id}
        )

        if success:
            commit.add_audit_entry("Execution started")
            self.logger.logger.debug(f"Executing commit {commit_id}")

    def complete_execution(
        self,
        commit_id: str,
        actual_outcome: Any
    ):
        """
        Complete execution and record outcome.

        Args:
            commit_id: ID of commit
            actual_outcome: What actually happened
        """
        commit = self.records.get_commit(commit_id)
        if not commit:
            self.logger.logger.error(f"Commit {commit_id} not found")
            return

        # Record outcome
        commit.set_outcome(actual_outcome)

        # Transition to REVIEW
        success = self.fsm.transition(
            CommitState.REVIEW,
            f"Reviewing outcome for {commit_id}",
            {
                "commit_id": commit_id,
                "outcome_matches": commit.matches_prediction()
            }
        )

        if success:
            self.logger.logger.info(
                f"Commit {commit_id} execution complete. "
                f"Match: {commit.matches_prediction()}"
            )

    def reopen_commit(
        self,
        commit_id: str,
        reason: str,
        contradiction_strength: float
    ) -> bool:
        """
        Reopen a commit due to contradiction.

        This is RARE and serious. Only happens when:
        - Strong evidence contradicts committed belief
        - Outcome radically differs from prediction
        - Ethical violation detected post-hoc

        Args:
            commit_id: ID of commit to reopen
            reason: Why reopening
            contradiction_strength: How strong the contradiction (0-1)

        Returns:
            True if reopened, False if denied
        """
        commit = self.records.get_commit(commit_id)
        if not commit:
            self.logger.logger.error(f"Commit {commit_id} not found")
            return False

        # Check reopen policy
        if commit.reopen_policy == "never":
            self.logger.logger.warning(
                f"Commit {commit_id} has 'never' reopen policy"
            )
            return False

        if contradiction_strength < commit.reopen_threshold:
            self.logger.logger.info(
                f"Contradiction strength {contradiction_strength:.2f} "
                f"below threshold {commit.reopen_threshold:.2f}"
            )
            return False

        # Attempt transition to REOPEN
        success = self.fsm.transition(
            CommitState.REOPEN,
            f"Reopening due to: {reason}",
            {
                "commit_id": commit_id,
                "contradiction_strength": contradiction_strength
            }
        )

        if success:
            commit.add_audit_entry(
                f"REOPENED: {reason} (strength: {contradiction_strength:.2f})"
            )
            self.logger.logger.critical(
                f"COMMIT REOPENED: {commit_id} - {reason}"
            )

        return success

    def _should_commit(self, ethical_assessment: EthicalAssessment) -> bool:
        """
        Check if commitment should be made.

        Args:
            ethical_assessment: Ethical evaluation

        Returns:
            True if should commit, False otherwise
        """
        # Ethics must approve
        if not ethical_assessment.permitted:
            self.logger.logger.warning(
                f"Ethics blocked: {ethical_assessment.reason}"
            )
            return False

        # Confidence should be reasonable (if we have reasoning)
        if self.current_reasoning and self.current_reasoning.confidence < 0.3:
            self.logger.logger.warning(
                f"Confidence too low: {self.current_reasoning.confidence:.2f}"
            )
            return False

        return True

    def get_current_state(self) -> CommitState:
        """Get current FSM state."""
        return self.fsm.current_state

    def get_state_path(self) -> List[CommitState]:
        """Get path through states."""
        return self.fsm.get_state_path()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            "current_state": self.fsm.current_state.value,
            "time_in_state": self.fsm.time_in_current_state(),
            "total_transitions": len(self.fsm.transition_history),
            "commit_records": self.records.get_stats(),
            "state_path": [s.value for s in self.get_state_path()]
        }
