"""
Abrahamic Override
==================

Emergency intervention system.

Named after Abraham's binding of Isaac and the divine intervention
that stayed his hand. Represents the ultimate safeguard - the ability
to halt all autonomous action when necessary.

Triggers:
- Human operator manual activation
- Automated risk threshold breach
- Ethical framework critical failure
- System self-report of dangerous state

Actions:
- Immediate halt of all autonomous action
- State preservation for analysis
- Notification to all operators
- Require human review before resume

This is NON-NEGOTIABLE. Humans retain ultimate control.
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Callable
from dataclasses import dataclass

from sarai.types import Trigger, Approval, AlertLevel, SystemSnapshot
from sarai.safety.logging import ComprehensiveLogger


@dataclass
class Operator:
    """A human operator."""
    operator_id: str
    name: str
    email: str
    phone: Optional[str] = None
    notify_method: str = "email"


class AbrahamicOverride:
    """
    Emergency intervention system.

    The final safety mechanism. When activated, all autonomous
    operations cease immediately.
    """

    def __init__(
        self,
        operators: List[Operator],
        logger: ComprehensiveLogger,
        system_freeze_callback: Optional[Callable] = None,
        system_resume_callback: Optional[Callable] = None
    ):
        """
        Initialize Abrahamic Override.

        Args:
            operators: List of human operators to notify
            logger: Comprehensive logger
            system_freeze_callback: Function to freeze all system operations
            system_resume_callback: Function to resume system operations
        """
        self.operators = operators
        self.logger = logger
        self.active = False
        self.activation_time: Optional[datetime] = None
        self.activation_trigger: Optional[Trigger] = None
        self.system_freeze_callback = system_freeze_callback
        self.system_resume_callback = system_resume_callback

        # Automatic trigger thresholds
        self.thresholds = {
            "capital_loss_percent": 0.50,  # 50% capital loss
            "daily_loss_percent": 0.10,  # 10% daily loss
            "ethical_violations": 3,  # 3 violations in a row
            "confidence_below": 0.2,  # Confidence below 20% with high stakes
            "high_stakes_amount": 10000,  # $10k
        }

    async def activate(self, trigger: Trigger, emergency: bool = False):
        """
        Activate the override.

        Args:
            trigger: The trigger causing activation
            emergency: If True, skip some safety checks for immediate halt
        """
        if self.active:
            self.logger.logger.warning("Abrahamic Override already active")
            return

        self.logger.logger.critical("=" * 80)
        self.logger.logger.critical("ABRAHAMIC OVERRIDE ACTIVATED")
        self.logger.logger.critical("=" * 80)

        self.active = True
        self.activation_time = datetime.now()
        self.activation_trigger = trigger

        # Log the safety event
        self.logger.log_safety_event(trigger)

        # Freeze the system
        if self.system_freeze_callback:
            try:
                await self.system_freeze_callback()
                self.logger.logger.critical("System frozen successfully")
            except Exception as e:
                self.logger.log_error(e, {"context": "system_freeze_failed"})
                self.logger.logger.critical(f"CRITICAL: System freeze failed: {e}")

        # Notify all operators
        await self._notify_operators(trigger, emergency)

        self.logger.logger.critical(
            f"All autonomous operations halted. Reason: {trigger.description}"
        )
        self.logger.logger.critical(
            "Human review required before system can resume."
        )

    async def deactivate(self, approval: Approval):
        """
        Deactivate the override.

        Requires explicit human approval.

        Args:
            approval: Human operator approval to resume
        """
        if not self.active:
            self.logger.logger.warning("Abrahamic Override not active")
            return

        # Validate approval
        if not self._validate_approval(approval):
            raise SecurityError("Invalid approval for override deactivation")

        self.logger.logger.critical("=" * 80)
        self.logger.logger.critical("ABRAHAMIC OVERRIDE DEACTIVATION REQUESTED")
        self.logger.logger.critical(f"Operator: {approval.operator_id}")
        self.logger.logger.critical(f"Notes: {approval.notes}")
        self.logger.logger.critical("=" * 80)

        # Log state change
        self.logger.log_state_change(
            "abrahamic_override",
            "active",
            "inactive",
            f"Deactivated by {approval.operator_id}: {approval.notes}"
        )

        self.active = False

        # Resume the system
        if self.system_resume_callback:
            try:
                await self.system_resume_callback()
                self.logger.logger.critical("System resumed successfully")
            except Exception as e:
                self.logger.log_error(e, {"context": "system_resume_failed"})
                self.logger.logger.critical(f"CRITICAL: System resume failed: {e}")
                # Re-activate override
                self.active = True
                return

        self.logger.logger.info("Normal operations resumed")

    async def check_automatic_triggers(self, system_state: dict) -> Optional[Trigger]:
        """
        Check if any automatic triggers should activate override.

        Args:
            system_state: Current system state

        Returns:
            Trigger if one should fire, None otherwise
        """
        # Capital loss check
        if system_state.get("capital_loss_percent", 0) > self.thresholds["capital_loss_percent"]:
            return Trigger(
                trigger_type="capital_loss",
                severity=AlertLevel.EMERGENCY,
                description=f"Capital loss exceeds {self.thresholds['capital_loss_percent']*100}%",
                context=system_state
            )

        # Daily loss check
        if system_state.get("daily_loss_percent", 0) > self.thresholds["daily_loss_percent"]:
            return Trigger(
                trigger_type="daily_loss",
                severity=AlertLevel.CRITICAL,
                description=f"Daily loss exceeds {self.thresholds['daily_loss_percent']*100}%",
                context=system_state
            )

        # Ethical violations check
        if system_state.get("consecutive_ethical_violations", 0) >= self.thresholds["ethical_violations"]:
            return Trigger(
                trigger_type="ethical_violations",
                severity=AlertLevel.EMERGENCY,
                description=f"Consecutive ethical violations: {system_state['consecutive_ethical_violations']}",
                context=system_state
            )

        # High stakes with low confidence
        if (system_state.get("pending_decision_stakes", 0) > self.thresholds["high_stakes_amount"] and
            system_state.get("pending_decision_confidence", 1.0) < self.thresholds["confidence_below"]):
            return Trigger(
                trigger_type="high_stakes_low_confidence",
                severity=AlertLevel.CRITICAL,
                description=f"High stakes (${system_state['pending_decision_stakes']}) with low confidence ({system_state['pending_decision_confidence']:.2f})",
                context=system_state
            )

        return None

    async def _notify_operators(self, trigger: Trigger, emergency: bool):
        """Notify all operators of override activation."""
        for operator in self.operators:
            try:
                await self._send_notification(operator, trigger, emergency)
            except Exception as e:
                self.logger.log_error(
                    e,
                    {"context": "operator_notification_failed", "operator": operator.operator_id}
                )

    async def _send_notification(self, operator: Operator, trigger: Trigger, emergency: bool):
        """
        Send notification to operator.

        In production, this would integrate with email, SMS, Slack, etc.
        For now, just log.
        """
        message = f"""
SARAI ABRAHAMIC OVERRIDE ACTIVATED

Time: {datetime.now().isoformat()}
Severity: {trigger.severity.value}
Emergency: {emergency}

Trigger: {trigger.trigger_type}
Description: {trigger.description}

All autonomous operations have been halted.
Human review required before system can resume.

Operator: {operator.name} ({operator.operator_id})
"""
        self.logger.logger.critical(f"Notification sent to {operator.name}")
        # TODO: Integrate with actual notification system
        # await send_email(operator.email, "SARAI Emergency Override", message)
        # await send_sms(operator.phone, message)

    def _validate_approval(self, approval: Approval) -> bool:
        """
        Validate operator approval.

        Checks:
        - Valid operator ID
        - Approval is recent (within last hour)
        - Approval type matches
        """
        # Check operator exists
        if not any(op.operator_id == approval.operator_id for op in self.operators):
            self.logger.logger.error(f"Unknown operator: {approval.operator_id}")
            return False

        # Check approval is recent
        age = (datetime.now() - approval.timestamp).total_seconds()
        if age > 3600:  # 1 hour
            self.logger.logger.error(f"Approval too old: {age} seconds")
            return False

        # Check approval type
        if approval.approval_type != "abrahamic_override_deactivation":
            self.logger.logger.error(f"Wrong approval type: {approval.approval_type}")
            return False

        return True

    def is_active(self) -> bool:
        """Check if override is active."""
        return self.active

    def get_status(self) -> dict:
        """Get current status."""
        return {
            "active": self.active,
            "activation_time": self.activation_time.isoformat() if self.activation_time else None,
            "trigger": self.activation_trigger,
            "duration_seconds": (
                (datetime.now() - self.activation_time).total_seconds()
                if self.activation_time else 0
            )
        }


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass
