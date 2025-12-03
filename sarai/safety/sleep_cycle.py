"""
Sleep Cycle
===========

Periodic dormancy for human review and recalibration.

Like biological sleep, this is when consolidation, review, and
adjustment occur. SARAI cannot operate 24/7 without rest.

The "loosening of bonds" - during sleep, humans can adjust parameters,
review decisions, and recalibrate the system.

Triggers:
- Scheduled (e.g., daily at specific time)
- Daily loss limit hit
- Operator initiated
- Self-initiated (system recognizes need for recalibration)

During sleep:
- All autonomous action halted
- Logs available for human review
- Model updates can be applied
- Configuration changes permitted
- Memory consolidation occurs
"""

import asyncio
from datetime import datetime, time, timedelta
from typing import Optional, Callable, Awaitable, Dict, Any, List
from dataclasses import dataclass, field

from sarai.safety.logging import ComprehensiveLogger


@dataclass
class Schedule:
    """Sleep schedule configuration."""
    daily_sleep_time: time = time(2, 0)  # 2 AM default
    min_sleep_duration_hours: float = 1.0
    max_sleep_duration_hours: float = 4.0
    allow_self_initiated: bool = True


@dataclass
class Changes:
    """Configuration changes during sleep."""
    parameter_updates: Dict[str, Any] = field(default_factory=dict)
    model_updates: List[str] = field(default_factory=list)
    calibration_adjustments: Dict[str, float] = field(default_factory=dict)
    notes: str = ""


@dataclass
class ReviewPackage:
    """Package of information for human review during sleep."""
    session_id: str
    sleep_start: datetime
    logs_summary: Dict[str, Any]
    metrics: Dict[str, Any]
    decisions: List[Dict[str, Any]]
    ethical_assessments: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    recommendations: List[str]


class SleepCycle:
    """
    Periodic dormancy system.

    Ensures regular human oversight and system maintenance.
    """

    def __init__(
        self,
        logger: ComprehensiveLogger,
        schedule: Schedule,
        dormancy_callback: Optional[Callable[[], Awaitable[None]]] = None,
        resume_callback: Optional[Callable[[], Awaitable[None]]] = None,
        memory_consolidation_callback: Optional[Callable[[], Awaitable[None]]] = None
    ):
        """
        Initialize Sleep Cycle.

        Args:
            logger: Comprehensive logger
            schedule: Sleep schedule configuration
            dormancy_callback: Function to call when entering sleep
            resume_callback: Function to call when exiting sleep
            memory_consolidation_callback: Function to consolidate memories during sleep
        """
        self.logger = logger
        self.schedule = schedule
        self.dormancy_callback = dormancy_callback
        self.resume_callback = resume_callback
        self.memory_consolidation_callback = memory_consolidation_callback

        self.in_sleep = False
        self.sleep_start: Optional[datetime] = None
        self.sleep_reason: Optional[str] = None
        self.sleep_count = 0
        self.last_sleep: Optional[datetime] = None

        # Track reasons for sleep
        self.sleep_history: List[Dict[str, Any]] = []

    async def check_scheduled_sleep(self) -> bool:
        """
        Check if it's time for scheduled sleep.

        Returns:
            True if should enter sleep, False otherwise
        """
        if self.in_sleep:
            return False

        now = datetime.now()

        # Check if we're at the scheduled time
        if now.time() >= self.schedule.daily_sleep_time:
            # Check if we've already slept today
            if self.last_sleep is None or self.last_sleep.date() < now.date():
                await self.enter_sleep("scheduled")
                return True

        return False

    async def check_triggers(self, system_state: Dict[str, Any]) -> bool:
        """
        Check if any triggers should initiate sleep.

        Args:
            system_state: Current system state

        Returns:
            True if sleep initiated, False otherwise
        """
        if self.in_sleep:
            return False

        # Daily loss limit
        if system_state.get("daily_loss_percent", 0) > 0.05:  # 5% daily loss
            await self.enter_sleep("daily_loss_limit")
            return True

        # Self-initiated if enabled
        if self.schedule.allow_self_initiated:
            if system_state.get("self_assessed_need_for_sleep", False):
                await self.enter_sleep("self_initiated")
                return True

        # Fatigue indicators
        if system_state.get("decisions_today", 0) > 100:  # High activity
            error_rate = system_state.get("recent_error_rate", 0)
            if error_rate > 0.15:  # 15% error rate suggests fatigue
                await self.enter_sleep("fatigue_detected")
                return True

        return False

    async def enter_sleep(self, reason: str):
        """
        Enter sleep state.

        Args:
            reason: Reason for entering sleep
        """
        if self.in_sleep:
            self.logger.logger.warning("Already in sleep state")
            return

        self.logger.logger.info("=" * 80)
        self.logger.logger.info("ENTERING SLEEP CYCLE")
        self.logger.logger.info(f"Reason: {reason}")
        self.logger.logger.info("=" * 80)

        self.in_sleep = True
        self.sleep_start = datetime.now()
        self.sleep_reason = reason
        self.sleep_count += 1

        # Log state change
        self.logger.log_state_change(
            "sleep_state",
            "active",
            "sleeping",
            reason
        )

        # Execute dormancy callback
        if self.dormancy_callback:
            try:
                await self.dormancy_callback()
                self.logger.logger.info("System entered dormancy successfully")
            except Exception as e:
                self.logger.log_error(e, {"context": "dormancy_callback_failed"})

        # Consolidate memories during sleep
        if self.memory_consolidation_callback:
            try:
                self.logger.logger.info("Consolidating memories...")
                await self.memory_consolidation_callback()
                self.logger.logger.info("Memory consolidation complete")
            except Exception as e:
                self.logger.log_error(e, {"context": "memory_consolidation_failed"})

        # Prepare review package
        review_package = await self.prepare_review_package()

        self.logger.logger.info(
            f"Review package prepared. Logs available for human review."
        )
        self.logger.logger.info(
            f"Sleep duration: {self.schedule.min_sleep_duration_hours}-{self.schedule.max_sleep_duration_hours} hours"
        )

        # Store in history
        self.sleep_history.append({
            "count": self.sleep_count,
            "start": self.sleep_start,
            "reason": reason,
            "review_package": review_package
        })

    async def exit_sleep(self, operator_changes: Optional[Changes] = None):
        """
        Exit sleep state and resume operations.

        Args:
            operator_changes: Optional changes made by operators during sleep
        """
        if not self.in_sleep:
            self.logger.logger.warning("Not in sleep state")
            return

        # Check minimum sleep duration
        if self.sleep_start:
            sleep_duration = (datetime.now() - self.sleep_start).total_seconds() / 3600
            if sleep_duration < self.schedule.min_sleep_duration_hours:
                self.logger.logger.warning(
                    f"Minimum sleep duration not met: {sleep_duration:.2f}/{self.schedule.min_sleep_duration_hours} hours"
                )
                return

        self.logger.logger.info("=" * 80)
        self.logger.logger.info("EXITING SLEEP CYCLE")
        self.logger.logger.info("=" * 80)

        # Apply operator changes if any
        if operator_changes:
            await self.apply_changes(operator_changes)

        # Update history
        if self.sleep_history:
            self.sleep_history[-1]["end"] = datetime.now()
            self.sleep_history[-1]["duration_hours"] = (
                (datetime.now() - self.sleep_start).total_seconds() / 3600
            )
            if operator_changes:
                self.sleep_history[-1]["changes_applied"] = operator_changes

        # Execute resume callback
        if self.resume_callback:
            try:
                await self.resume_callback()
                self.logger.logger.info("System resumed successfully")
            except Exception as e:
                self.logger.log_error(e, {"context": "resume_callback_failed"})
                # Don't exit sleep if resume fails
                return

        # Log state change
        self.logger.log_state_change(
            "sleep_state",
            "sleeping",
            "active",
            "Sleep cycle complete"
        )

        self.in_sleep = False
        self.last_sleep = self.sleep_start
        self.sleep_start = None
        self.sleep_reason = None

        self.logger.logger.info("Normal operations resumed")

    async def prepare_review_package(self) -> ReviewPackage:
        """
        Prepare comprehensive review package for human operators.

        Returns:
            ReviewPackage with logs, metrics, and recommendations
        """
        # Get recent logs
        recent_logs = self.logger.get_recent_logs(n=1000)

        # Calculate metrics
        metrics = self._calculate_metrics(recent_logs)

        # Get decisions
        decisions = self.logger.get_logs_by_type("decision", n=100)

        # Get ethical assessments
        assessments = self.logger.get_logs_by_type("ethical_assessment", n=100)

        # Get alerts
        alerts = [
            log for log in recent_logs
            if log.get("event_type") in ["safety_event", "error"]
        ]

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, alerts)

        return ReviewPackage(
            session_id=self.logger.session_id,
            sleep_start=self.sleep_start or datetime.now(),
            logs_summary={
                "total_logs": len(recent_logs),
                "by_type": self._count_by_type(recent_logs)
            },
            metrics=metrics,
            decisions=decisions,
            ethical_assessments=assessments,
            alerts=alerts,
            recommendations=recommendations
        )

    async def apply_changes(self, changes: Changes):
        """
        Apply operator changes during sleep.

        The "loosening of bonds" - parameters can be adjusted.

        Args:
            changes: Changes to apply
        """
        self.logger.logger.info("Applying operator changes:")
        self.logger.logger.info(f"Notes: {changes.notes}")

        # Log all changes
        for param, value in changes.parameter_updates.items():
            self.logger.log_state_change(
                f"parameter_{param}",
                "unknown",  # Don't know old value
                value,
                f"Operator adjustment during sleep: {changes.notes}"
            )

        for update in changes.model_updates:
            self.logger.logger.info(f"Model update: {update}")

        for param, adjustment in changes.calibration_adjustments.items():
            self.logger.logger.info(f"Calibration adjustment: {param} = {adjustment}")

    def _calculate_metrics(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics from logs."""
        decision_logs = [l for l in logs if l.get("event_type") == "decision"]
        error_logs = [l for l in logs if l.get("event_type") == "error"]

        return {
            "total_decisions": len(decision_logs),
            "total_errors": len(error_logs),
            "error_rate": len(error_logs) / max(len(decision_logs), 1),
            "avg_confidence": sum(
                l.get("confidence", 0) for l in logs
                if l.get("event_type") == "reasoning"
            ) / max(len([l for l in logs if l.get("event_type") == "reasoning"]), 1)
        }

    def _count_by_type(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count logs by event type."""
        counts = {}
        for log in logs:
            event_type = log.get("event_type", "unknown")
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts

    def _generate_recommendations(
        self,
        metrics: Dict[str, Any],
        alerts: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for operators."""
        recommendations = []

        # High error rate
        if metrics.get("error_rate", 0) > 0.1:
            recommendations.append(
                f"Error rate is elevated at {metrics['error_rate']:.1%}. "
                "Consider reviewing recent decisions and adjusting parameters."
            )

        # Low confidence
        if metrics.get("avg_confidence", 1.0) < 0.6:
            recommendations.append(
                f"Average confidence is low at {metrics['avg_confidence']:.2f}. "
                "System may need additional training or tighter constraints."
            )

        # Multiple alerts
        if len(alerts) > 10:
            recommendations.append(
                f"Multiple alerts detected ({len(alerts)}). Review alert patterns."
            )

        if not recommendations:
            recommendations.append("System performance within normal parameters.")

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """Get current sleep cycle status."""
        return {
            "in_sleep": self.in_sleep,
            "sleep_start": self.sleep_start.isoformat() if self.sleep_start else None,
            "sleep_reason": self.sleep_reason,
            "sleep_count": self.sleep_count,
            "last_sleep": self.last_sleep.isoformat() if self.last_sleep else None,
            "schedule": {
                "daily_sleep_time": self.schedule.daily_sleep_time.isoformat(),
                "min_duration_hours": self.schedule.min_sleep_duration_hours,
                "max_duration_hours": self.schedule.max_sleep_duration_hours
            },
            "sleep_history_count": len(self.sleep_history)
        }
