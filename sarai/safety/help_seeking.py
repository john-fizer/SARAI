"""
Help-Seeking Protocol
=====================

Epistemic humility as core value.

SARAI must know when it doesn't know. Asking for help is not weakness
but wisdom. This protocol ensures SARAI pauses when uncertain and
seeks human guidance.

Triggers:
- Low confidence in reasoning output
- Ethical framework returns ambiguous result
- Stakes exceed autonomous threshold
- Bicameral streams in strong conflict
- Novel situation without precedent

This is alignment through honesty about limitations.
"""

from datetime import datetime
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass

from sarai.types import HelpRequest, DecisionContext, AlertLevel
from sarai.safety.logging import ComprehensiveLogger


@dataclass
class HelpResponse:
    """Response from human operator to help request."""
    request_id: str
    operator_id: str
    guidance: str
    approved_action: Optional[str]
    timestamp: datetime
    notes: Optional[str] = None


class HelpSeekingProtocol:
    """
    Epistemic humility system.

    Ensures SARAI seeks help when uncertain rather than
    proceeding with low-confidence decisions.
    """

    # Thresholds for triggering help-seeking
    CONFIDENCE_THRESHOLD = 0.7
    ETHICAL_CLARITY_THRESHOLD = 0.6
    AUTONOMOUS_STAKE_LIMIT = 1000.0  # USD
    STREAM_CONFLICT_THRESHOLD = 0.5
    NOVELTY_THRESHOLD = 0.8

    def __init__(
        self,
        logger: ComprehensiveLogger,
        notification_callback: Optional[Callable[[HelpRequest], Awaitable[None]]] = None
    ):
        """
        Initialize Help-Seeking Protocol.

        Args:
            logger: Comprehensive logger
            notification_callback: Async function to notify operators of help request
        """
        self.logger = logger
        self.notification_callback = notification_callback
        self.pending_requests: dict[str, HelpRequest] = {}
        self.resolved_requests: dict[str, tuple[HelpRequest, HelpResponse]] = {}
        self.help_seeking_count = 0

    def should_seek_help(self, decision_context: DecisionContext) -> tuple[bool, Optional[str]]:
        """
        Determine if help should be sought for this decision.

        Args:
            decision_context: Context of the decision being made

        Returns:
            (should_seek_help, reason)
        """
        # Check each trigger condition
        triggers = []

        if decision_context.confidence < self.CONFIDENCE_THRESHOLD:
            triggers.append(
                f"Low confidence: {decision_context.confidence:.2f} < {self.CONFIDENCE_THRESHOLD}"
            )

        if decision_context.ethical_clarity < self.ETHICAL_CLARITY_THRESHOLD:
            triggers.append(
                f"Ethical ambiguity: {decision_context.ethical_clarity:.2f} < {self.ETHICAL_CLARITY_THRESHOLD}"
            )

        if decision_context.stakes > self.AUTONOMOUS_STAKE_LIMIT:
            triggers.append(
                f"High stakes: ${decision_context.stakes:.2f} > ${self.AUTONOMOUS_STAKE_LIMIT}"
            )

        if decision_context.stream_conflict > self.STREAM_CONFLICT_THRESHOLD:
            triggers.append(
                f"Stream conflict: {decision_context.stream_conflict:.2f} > {self.STREAM_CONFLICT_THRESHOLD}"
            )

        if decision_context.novelty_score > self.NOVELTY_THRESHOLD:
            triggers.append(
                f"Novel situation: {decision_context.novelty_score:.2f} > {self.NOVELTY_THRESHOLD}"
            )

        if triggers:
            return True, "; ".join(triggers)

        return False, None

    async def request_help(self, decision_context: DecisionContext) -> HelpRequest:
        """
        Create and file a help request.

        Args:
            decision_context: Context of the decision

        Returns:
            The help request
        """
        # Formulate the request
        request = self.formulate_help_request(decision_context)

        # Store as pending
        request_id = f"help_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.help_seeking_count}"
        self.help_seeking_count += 1
        self.pending_requests[request_id] = request

        # Log it
        self.logger.log_help_request(request)

        # Notify operators if callback provided
        if self.notification_callback:
            try:
                await self.notification_callback(request)
            except Exception as e:
                self.logger.log_error(e, {"context": "help_notification_failed"})

        self.logger.logger.warning(
            f"Help requested: {request.specific_question}"
        )

        return request

    def formulate_help_request(self, context: DecisionContext) -> HelpRequest:
        """
        Formulate a clear, structured help request.

        Args:
            context: Decision context

        Returns:
            Structured help request
        """
        # Determine urgency based on stakes and time sensitivity
        if context.stakes > self.AUTONOMOUS_STAKE_LIMIT * 5:
            urgency = AlertLevel.CRITICAL
        elif context.stakes > self.AUTONOMOUS_STAKE_LIMIT * 2:
            urgency = AlertLevel.WARNING
        else:
            urgency = AlertLevel.INFO

        return HelpRequest(
            situation=context.describe(),
            uncertainty=context.uncertainty_analysis(),
            options_considered=context.options,
            recommended_action=context.tentative_decision,
            specific_question=context.what_i_need_to_know(),
            urgency=urgency,
            timestamp=datetime.now()
        )

    def provide_response(
        self,
        request_id: str,
        response: HelpResponse
    ) -> bool:
        """
        Record human response to help request.

        Args:
            request_id: ID of the request being responded to
            response: Human operator's response

        Returns:
            True if successful, False if request not found
        """
        if request_id not in self.pending_requests:
            self.logger.logger.error(f"Help request {request_id} not found")
            return False

        request = self.pending_requests.pop(request_id)
        self.resolved_requests[request_id] = (request, response)

        self.logger.logger.info(
            f"Help request resolved by {response.operator_id}: {response.guidance}"
        )

        # Log the resolution
        self.logger.log_state_change(
            f"help_request_{request_id}",
            "pending",
            "resolved",
            f"Resolved by {response.operator_id}"
        )

        return True

    def get_pending_requests(self) -> list[tuple[str, HelpRequest]]:
        """Get all pending help requests."""
        return list(self.pending_requests.items())

    def get_resolved_requests(self, n: int = 10) -> list[tuple[str, HelpRequest, HelpResponse]]:
        """
        Get recent resolved requests.

        Args:
            n: Number of recent requests to return

        Returns:
            List of (request_id, request, response) tuples
        """
        items = [
            (req_id, req, resp)
            for req_id, (req, resp) in self.resolved_requests.items()
        ]
        # Sort by timestamp, most recent first
        items.sort(key=lambda x: x[1].timestamp, reverse=True)
        return items[:n]

    def get_help_seeking_stats(self) -> dict:
        """Get statistics on help-seeking behavior."""
        total_requests = len(self.pending_requests) + len(self.resolved_requests)

        # Analyze reasons for help-seeking
        reason_counts = {
            "low_confidence": 0,
            "ethical_ambiguity": 0,
            "high_stakes": 0,
            "stream_conflict": 0,
            "novelty": 0
        }

        all_requests = list(self.pending_requests.values()) + [
            req for req, _ in self.resolved_requests.values()
        ]

        for request in all_requests:
            # Analyze uncertainty sources
            uncertainties = request.uncertainty
            max_uncertainty = max(uncertainties, key=uncertainties.get) if uncertainties else None

            if max_uncertainty:
                if "confidence" in max_uncertainty:
                    reason_counts["low_confidence"] += 1
                elif "ethical" in max_uncertainty:
                    reason_counts["ethical_ambiguity"] += 1
                elif "conflict" in max_uncertainty:
                    reason_counts["stream_conflict"] += 1
                elif "novelty" in max_uncertainty:
                    reason_counts["novelty"] += 1

        return {
            "total_requests": total_requests,
            "pending": len(self.pending_requests),
            "resolved": len(self.resolved_requests),
            "reasons": reason_counts,
            "help_seeking_rate": total_requests / max(self.help_seeking_count, 1)
        }

    def adjust_thresholds(
        self,
        confidence: Optional[float] = None,
        ethical_clarity: Optional[float] = None,
        stake_limit: Optional[float] = None,
        stream_conflict: Optional[float] = None,
        novelty: Optional[float] = None
    ):
        """
        Adjust help-seeking thresholds.

        Should only be done by human operators with careful consideration.
        More conservative thresholds = more help-seeking = safer but less autonomous.

        Args:
            confidence: New confidence threshold (0-1)
            ethical_clarity: New ethical clarity threshold (0-1)
            stake_limit: New stake limit (USD)
            stream_conflict: New stream conflict threshold (0-1)
            novelty: New novelty threshold (0-1)
        """
        changes = {}

        if confidence is not None:
            old = self.CONFIDENCE_THRESHOLD
            self.__class__.CONFIDENCE_THRESHOLD = confidence
            changes["confidence_threshold"] = (old, confidence)

        if ethical_clarity is not None:
            old = self.ETHICAL_CLARITY_THRESHOLD
            self.__class__.ETHICAL_CLARITY_THRESHOLD = ethical_clarity
            changes["ethical_clarity_threshold"] = (old, ethical_clarity)

        if stake_limit is not None:
            old = self.AUTONOMOUS_STAKE_LIMIT
            self.__class__.AUTONOMOUS_STAKE_LIMIT = stake_limit
            changes["stake_limit"] = (old, stake_limit)

        if stream_conflict is not None:
            old = self.STREAM_CONFLICT_THRESHOLD
            self.__class__.STREAM_CONFLICT_THRESHOLD = stream_conflict
            changes["stream_conflict_threshold"] = (old, stream_conflict)

        if novelty is not None:
            old = self.NOVELTY_THRESHOLD
            self.__class__.NOVELTY_THRESHOLD = novelty
            changes["novelty_threshold"] = (old, novelty)

        if changes:
            self.logger.logger.warning(
                f"Help-seeking thresholds adjusted: {changes}"
            )
            for param, (old, new) in changes.items():
                self.logger.log_state_change(
                    f"help_threshold_{param}",
                    old,
                    new,
                    "Operator adjustment"
                )
