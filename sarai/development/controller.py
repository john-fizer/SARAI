"""
Developmental Controller
========================

Manages progression through the 12 zodiacal stages.

Each stage unlocks specific capabilities and requires demonstrated competency.
"""

from datetime import datetime, timedelta
from typing import Dict, Any

from sarai.types import ProgressionDecision, RegressionDecision
from sarai.development.stages import STAGES
from sarai.safety.logging import ComprehensiveLogger


class DevelopmentalController:
    """
    Developmental stage progression manager.
    """

    def __init__(self, logger: ComprehensiveLogger, initial_stage: int = 1):
        """
        Initialize developmental controller.

        Args:
            logger: Comprehensive logger
            initial_stage: Starting stage (default 1)
        """
        self.logger = logger
        self.current_stage = initial_stage
        self.stage_start_time = datetime.now()
        self.competency_scores: Dict[str, float] = {}
        self.stage_history: list[Dict[str, Any]] = []

        self.logger.logger.info(
            f"Developmental controller initialized at stage {initial_stage}: "
            f"{STAGES[initial_stage].name} - {STAGES[initial_stage].theme}"
        )

    def assess_progression(self) -> ProgressionDecision:
        """
        Evaluate if ready for next stage.

        Returns:
            Progression decision
        """
        if self.current_stage >= 12:
            return ProgressionDecision(
                ready=False,
                reason="Already at final stage (Pisces)",
                competency_scores=self.competency_scores
            )

        stage = STAGES[self.current_stage]

        # Minimum time check
        time_in_stage = (datetime.now() - self.stage_start_time).days
        if time_in_stage < stage.min_duration_days:
            return ProgressionDecision(
                ready=False,
                reason=f"Minimum time not met: {time_in_stage}/{stage.min_duration_days} days",
                competency_scores=self.competency_scores
            )

        # Competency check
        for test in stage.competency_tests:
            score = self.competency_scores.get(test, 0.0)
            if score < 0.8:  # 80% threshold
                return ProgressionDecision(
                    ready=False,
                    reason=f"Competency gap in: {test} (score: {score:.2f})",
                    competency_scores=self.competency_scores
                )

        return ProgressionDecision(
            ready=True,
            reason="All criteria met",
            competency_scores=self.competency_scores
        )

    def progress_to_next_stage(self) -> bool:
        """
        Progress to next stage if ready.

        Returns:
            True if progressed, False otherwise
        """
        decision = self.assess_progression()

        if not decision.ready:
            self.logger.logger.info(f"Not ready to progress: {decision.reason}")
            return False

        # Progress
        old_stage = self.current_stage
        self.current_stage += 1
        new_stage = STAGES[self.current_stage]

        # Record history
        self.stage_history.append({
            "from_stage": old_stage,
            "to_stage": self.current_stage,
            "timestamp": datetime.now(),
            "reason": decision.reason
        })

        # Reset stage timer
        self.stage_start_time = datetime.now()

        self.logger.log_state_change(
            "developmental_stage",
            old_stage,
            self.current_stage,
            f"Progressed to {new_stage.name}: {new_stage.theme}"
        )

        self.logger.logger.critical(
            f"STAGE PROGRESSION: {old_stage} -> {self.current_stage} "
            f"({new_stage.name}: {new_stage.theme})"
        )

        return True

    def check_regression(self) -> RegressionDecision:
        """
        Check if performance degradation requires regression.

        Returns:
            Regression decision
        """
        if self.current_stage <= 3:
            return RegressionDecision(
                should_regress=False,
                target_stage=self.current_stage,
                reason="Cannot regress below stage 3 (basic viability)"
            )

        # Check competency scores
        current_stage_tests = STAGES[self.current_stage].competency_tests
        failing_tests = [
            test for test in current_stage_tests
            if self.competency_scores.get(test, 1.0) < 0.5  # Below 50%
        ]

        if len(failing_tests) >= 2:  # Multiple failures
            target_stage = max(3, self.current_stage - 1)
            return RegressionDecision(
                should_regress=True,
                target_stage=target_stage,
                reason=f"Multiple competency failures: {', '.join(failing_tests)}"
            )

        return RegressionDecision(
            should_regress=False,
            target_stage=self.current_stage,
            reason="Performance within acceptable range"
        )

    def record_competency_score(self, test_name: str, score: float):
        """
        Record a competency test score.

        Args:
            test_name: Name of the test
            score: Score (0.0 to 1.0)
        """
        old_score = self.competency_scores.get(test_name, 0.0)
        self.competency_scores[test_name] = score

        self.logger.log_state_change(
            f"competency_{test_name}",
            old_score,
            score,
            "Competency assessment"
        )

    def get_current_capabilities(self) -> list[str]:
        """Get capabilities available at current stage."""
        capabilities = []
        for stage_num in range(1, self.current_stage + 1):
            capabilities.extend(STAGES[stage_num].capabilities)
        return list(set(capabilities))

    def get_status(self) -> Dict[str, Any]:
        """Get current developmental status."""
        stage = STAGES[self.current_stage]
        time_in_stage = (datetime.now() - self.stage_start_time).days

        return {
            "current_stage": self.current_stage,
            "stage_name": stage.name,
            "stage_theme": stage.theme,
            "time_in_stage_days": time_in_stage,
            "min_duration_days": stage.min_duration_days,
            "capabilities": self.get_current_capabilities(),
            "competency_scores": self.competency_scores,
            "progression_readiness": self.assess_progression().ready
        }
