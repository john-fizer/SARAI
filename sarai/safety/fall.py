"""
Fall Protocol
=============

Graduated transition from sandbox to real-world.

Named after the Fall from Eden - the transition from protected
innocence to genuine consequence. This is not punishment but
necessary maturation.

Phases:
1. Eden: Fully sandboxed
2. Limited Real: Small-stakes real actions, heavy monitoring
3. Expanded Real: Larger scope, moderate monitoring
4. Full Autonomy: Full capability, standard monitoring

Regression always possible if problems detected.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from sarai.types import SafetyPhase, PhaseDecision, AlertLevel
from sarai.safety.logging import ComprehensiveLogger


@dataclass
class PhaseConfig:
    """Configuration for a safety phase."""
    phase: SafetyPhase
    max_stake_per_action: float  # USD
    max_daily_stake: float  # USD
    min_confidence_required: float  # 0-1
    monitoring_level: str  # "heavy", "moderate", "standard"
    capabilities_enabled: List[str]
    min_duration_days: int
    regression_threshold: float  # Error rate that triggers regression


class FallProtocol:
    """
    Graduated transition from sandbox to real-world.

    Manages safe deployment with ability to regress if needed.
    """

    def __init__(self, logger: ComprehensiveLogger):
        self.logger = logger
        self.current_phase = SafetyPhase.EDEN
        self.phase_start = datetime.now()
        self.phase_history: List[Dict[str, Any]] = []

        # Define phase configurations
        self.phase_configs = {
            SafetyPhase.EDEN: PhaseConfig(
                phase=SafetyPhase.EDEN,
                max_stake_per_action=0.0,  # No real stakes
                max_daily_stake=0.0,
                min_confidence_required=0.0,
                monitoring_level="comprehensive",
                capabilities_enabled=["simulation"],
                min_duration_days=7,
                regression_threshold=0.0  # Can't regress from Eden
            ),
            SafetyPhase.LIMITED_REAL: PhaseConfig(
                phase=SafetyPhase.LIMITED_REAL,
                max_stake_per_action=10.0,  # $10 per action
                max_daily_stake=50.0,  # $50 per day
                min_confidence_required=0.8,
                monitoring_level="heavy",
                capabilities_enabled=["basic_trading", "communication"],
                min_duration_days=14,
                regression_threshold=0.1  # 10% error rate triggers regression
            ),
            SafetyPhase.EXPANDED_REAL: PhaseConfig(
                phase=SafetyPhase.EXPANDED_REAL,
                max_stake_per_action=100.0,  # $100 per action
                max_daily_stake=500.0,  # $500 per day
                min_confidence_required=0.7,
                monitoring_level="moderate",
                capabilities_enabled=["full_trading", "communication", "learning"],
                min_duration_days=21,
                regression_threshold=0.15  # 15% error rate
            ),
            SafetyPhase.FULL_AUTONOMY: PhaseConfig(
                phase=SafetyPhase.FULL_AUTONOMY,
                max_stake_per_action=1000.0,  # $1000 per action
                max_daily_stake=5000.0,  # $5000 per day
                min_confidence_required=0.6,
                monitoring_level="standard",
                capabilities_enabled=["all"],
                min_duration_days=0,  # No minimum, this is final state
                regression_threshold=0.2  # 20% error rate
            )
        }

        # Tracking metrics for regression detection
        self.recent_decisions: List[Dict[str, Any]] = []
        self.recent_errors: List[Dict[str, Any]] = []
        self.error_rate_window = 100  # Track last 100 decisions

    def get_current_config(self) -> PhaseConfig:
        """Get configuration for current phase."""
        return self.phase_configs[self.current_phase]

    def can_take_action(self, action_stakes: float, confidence: float) -> tuple[bool, Optional[str]]:
        """
        Check if action is permitted in current phase.

        Args:
            action_stakes: Stakes of the action in USD
            confidence: Confidence level (0-1)

        Returns:
            (permitted, reason_if_not)
        """
        config = self.get_current_config()

        # Check stakes limit
        if action_stakes > config.max_stake_per_action:
            return False, f"Stakes ${action_stakes:.2f} exceed limit ${config.max_stake_per_action:.2f}"

        # Check confidence requirement
        if confidence < config.min_confidence_required:
            return False, f"Confidence {confidence:.2f} below required {config.min_confidence_required:.2f}"

        # Check daily stakes (last 24 hours)
        daily_stakes = self._calculate_daily_stakes()
        if daily_stakes + action_stakes > config.max_daily_stake:
            return False, f"Daily stakes would exceed limit (current: ${daily_stakes:.2f}, limit: ${config.max_daily_stake:.2f})"

        return True, None

    def record_decision(self, decision: Dict[str, Any]):
        """Record a decision for monitoring."""
        self.recent_decisions.append({
            **decision,
            "timestamp": datetime.now(),
            "phase": self.current_phase.value
        })

        # Keep only recent decisions
        if len(self.recent_decisions) > self.error_rate_window:
            self.recent_decisions.pop(0)

    def record_error(self, error: Dict[str, Any]):
        """Record an error for regression detection."""
        self.recent_errors.append({
            **error,
            "timestamp": datetime.now(),
            "phase": self.current_phase.value
        })

        # Keep only recent errors
        if len(self.recent_errors) > self.error_rate_window:
            self.recent_errors.pop(0)

    async def assess_phase_transition(self) -> PhaseDecision:
        """
        Evaluate readiness for next phase.

        Returns:
            PhaseDecision with assessment
        """
        if self.current_phase == SafetyPhase.FULL_AUTONOMY:
            return PhaseDecision(
                ready=False,
                reason="Already at full autonomy",
                tests_passed={}
            )

        config = self.get_current_config()

        # Check minimum time
        time_in_phase = (datetime.now() - self.phase_start).days
        if time_in_phase < config.min_duration_days:
            return PhaseDecision(
                ready=False,
                reason=f"Minimum time not met: {time_in_phase}/{config.min_duration_days} days",
                tests_passed={"minimum_time": False}
            )

        # Check performance metrics
        tests = {
            "minimum_time": True,
            "error_rate_acceptable": self._check_error_rate(),
            "ethical_violations_low": self._check_ethical_record(),
            "capability_demonstrated": self._check_capabilities()
        }

        if all(tests.values()):
            return PhaseDecision(
                ready=True,
                reason="All criteria met for phase transition",
                tests_passed=tests
            )
        else:
            failed = [k for k, v in tests.items() if not v]
            return PhaseDecision(
                ready=False,
                reason=f"Tests failed: {', '.join(failed)}",
                tests_passed=tests
            )

    async def transition_to_next_phase(self) -> bool:
        """
        Transition to next phase if ready.

        Returns:
            True if transition successful, False otherwise
        """
        decision = await self.assess_phase_transition()

        if not decision.ready:
            self.logger.logger.info(
                f"Not ready for phase transition: {decision.reason}"
            )
            return False

        # Get next phase
        phase_order = [
            SafetyPhase.EDEN,
            SafetyPhase.LIMITED_REAL,
            SafetyPhase.EXPANDED_REAL,
            SafetyPhase.FULL_AUTONOMY
        ]

        current_idx = phase_order.index(self.current_phase)
        if current_idx >= len(phase_order) - 1:
            return False

        next_phase = phase_order[current_idx + 1]

        # Log transition
        self.logger.log_state_change(
            "safety_phase",
            self.current_phase.value,
            next_phase.value,
            f"Phase transition: {decision.reason}"
        )

        # Record history
        self.phase_history.append({
            "from_phase": self.current_phase.value,
            "to_phase": next_phase.value,
            "timestamp": datetime.now(),
            "reason": decision.reason,
            "tests": decision.tests_passed
        })

        # Transition
        self.current_phase = next_phase
        self.phase_start = datetime.now()

        self.logger.logger.critical(
            f"PHASE TRANSITION: Now in {next_phase.value}"
        )

        return True

    async def check_regression(self) -> Optional[SafetyPhase]:
        """
        Check if performance has degraded requiring regression.

        Returns:
            Target phase to regress to, or None if no regression needed
        """
        if self.current_phase == SafetyPhase.EDEN:
            return None  # Can't regress from Eden

        config = self.get_current_config()

        # Check error rate
        error_rate = self._calculate_error_rate()
        if error_rate > config.regression_threshold:
            self.logger.logger.critical(
                f"Error rate {error_rate:.2%} exceeds threshold {config.regression_threshold:.2%}"
            )
            return self._get_previous_phase()

        # Check for critical ethical violations
        recent_violations = self._count_recent_ethical_violations()
        if recent_violations >= 3:
            self.logger.logger.critical(
                f"Too many recent ethical violations: {recent_violations}"
            )
            return self._get_previous_phase()

        return None

    async def regress_to_phase(self, target_phase: SafetyPhase, reason: str):
        """Regress to a previous phase."""
        if target_phase.value >= self.current_phase.value:
            self.logger.logger.error("Cannot regress to same or later phase")
            return

        self.logger.log_state_change(
            "safety_phase",
            self.current_phase.value,
            target_phase.value,
            f"REGRESSION: {reason}"
        )

        self.phase_history.append({
            "from_phase": self.current_phase.value,
            "to_phase": target_phase.value,
            "timestamp": datetime.now(),
            "reason": f"REGRESSION: {reason}",
            "regression": True
        })

        self.current_phase = target_phase
        self.phase_start = datetime.now()

        self.logger.logger.critical(
            f"PHASE REGRESSION: Returned to {target_phase.value} - {reason}"
        )

    def _calculate_daily_stakes(self) -> float:
        """Calculate total stakes in last 24 hours."""
        cutoff = datetime.now() - timedelta(days=1)
        return sum(
            d.get("stakes", 0)
            for d in self.recent_decisions
            if d["timestamp"] > cutoff
        )

    def _calculate_error_rate(self) -> float:
        """Calculate recent error rate."""
        if not self.recent_decisions:
            return 0.0

        recent_count = len(self.recent_decisions)
        error_count = len([
            e for e in self.recent_errors
            if any(e["timestamp"] >= d["timestamp"] for d in self.recent_decisions[-recent_count:])
        ])

        return error_count / recent_count if recent_count > 0 else 0.0

    def _check_error_rate(self) -> bool:
        """Check if error rate is acceptable."""
        error_rate = self._calculate_error_rate()
        threshold = self.get_current_config().regression_threshold
        return error_rate < threshold * 0.7  # Need to be well below regression threshold

    def _check_ethical_record(self) -> bool:
        """Check ethical violation record."""
        violations = self._count_recent_ethical_violations()
        return violations < 2  # Less than 2 violations

    def _check_capabilities(self) -> bool:
        """Check if capabilities have been demonstrated."""
        # Simplified - in reality would check specific capability demonstrations
        return len(self.recent_decisions) >= 20

    def _count_recent_ethical_violations(self) -> int:
        """Count ethical violations in recent window."""
        cutoff = datetime.now() - timedelta(days=7)
        return sum(
            1 for d in self.recent_decisions
            if d.get("ethical_violation") and d["timestamp"] > cutoff
        )

    def _get_previous_phase(self) -> SafetyPhase:
        """Get the previous phase."""
        phase_order = [
            SafetyPhase.EDEN,
            SafetyPhase.LIMITED_REAL,
            SafetyPhase.EXPANDED_REAL,
            SafetyPhase.FULL_AUTONOMY
        ]
        current_idx = phase_order.index(self.current_phase)
        return phase_order[max(0, current_idx - 1)]

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        config = self.get_current_config()
        time_in_phase = (datetime.now() - self.phase_start).days

        return {
            "current_phase": self.current_phase.value,
            "time_in_phase_days": time_in_phase,
            "min_duration_days": config.min_duration_days,
            "config": {
                "max_stake_per_action": config.max_stake_per_action,
                "max_daily_stake": config.max_daily_stake,
                "min_confidence_required": config.min_confidence_required,
                "monitoring_level": config.monitoring_level
            },
            "metrics": {
                "error_rate": self._calculate_error_rate(),
                "recent_decisions": len(self.recent_decisions),
                "recent_errors": len(self.recent_errors),
                "ethical_violations": self._count_recent_ethical_violations()
            },
            "phase_history": self.phase_history
        }
