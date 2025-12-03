"""
Comprehensive Logging Infrastructure
====================================

Every decision, every assessment, every state change must be logged.
Transparency enables trust.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from sarai.types import (
    Action, EthicalAssessment, ReasoningOutput,
    AlertLevel, SystemSnapshot, Trigger
)


class ComprehensiveLogger:
    """
    Comprehensive logging system for SARAI.

    Logs everything:
    - All perceptions
    - All reasoning processes
    - All ethical assessments
    - All decisions and actions
    - All safety interventions
    - System state changes

    Multiple output formats:
    - Structured JSON for machine analysis
    - Human-readable text logs
    - Real-time monitoring stream
    """

    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Session identifier
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Multiple log files
        self.structured_log = self.log_dir / f"structured_{self.session_id}.jsonl"
        self.human_log = self.log_dir / f"human_{self.session_id}.log"
        self.safety_log = self.log_dir / f"safety_{self.session_id}.log"
        self.decision_log = self.log_dir / f"decisions_{self.session_id}.jsonl"

        # Set up Python logging
        self._setup_python_logging()

        # In-memory buffer for recent logs
        self.recent_logs: List[Dict[str, Any]] = []
        self.max_recent = 1000

    def _setup_python_logging(self):
        """Configure Python logging."""
        self.logger = logging.getLogger("SARAI")
        self.logger.setLevel(logging.DEBUG)

        # Human-readable log
        handler = logging.FileHandler(self.human_log)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Console output
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def _write_structured(self, data: Dict[str, Any]):
        """Write to structured JSON log."""
        with open(self.structured_log, 'a') as f:
            f.write(json.dumps(data) + '\n')

        # Keep in recent buffer
        self.recent_logs.append(data)
        if len(self.recent_logs) > self.max_recent:
            self.recent_logs.pop(0)

    def log_perception(self, perception: Any):
        """Log a perception event."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "perception",
            "data": self._serialize(perception)
        }
        self._write_structured(data)
        self.logger.debug(f"Perception: {perception}")

    def log_reasoning(self, reasoning: ReasoningOutput):
        """Log a reasoning process."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "reasoning",
            "data": self._serialize(reasoning),
            "confidence": reasoning.confidence,
            "stream_agreement": reasoning.stream_agreement,
            "conflicts": reasoning.conflicts
        }
        self._write_structured(data)
        self.logger.info(
            f"Reasoning completed: confidence={reasoning.confidence:.2f}, "
            f"agreement={reasoning.stream_agreement:.2f}"
        )

    def log_ethical_assessment(self, assessment: EthicalAssessment):
        """Log an ethical assessment."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "ethical_assessment",
            "data": self._serialize(assessment),
            "permitted": assessment.permitted,
            "confidence": assessment.confidence
        }
        self._write_structured(data)

        level = logging.INFO if assessment.permitted else logging.WARNING
        self.logger.log(
            level,
            f"Ethical assessment: permitted={assessment.permitted}, "
            f"reason={assessment.reason}"
        )

    def log_decision(self, action: Action, reasoning: str):
        """Log a decision."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "decision",
            "action": self._serialize(action),
            "reasoning": reasoning
        }

        # Write to both structured and decision-specific log
        self._write_structured(data)
        with open(self.decision_log, 'a') as f:
            f.write(json.dumps(data) + '\n')

        self.logger.info(
            f"Decision: {action.action_type.value} - {action.description}"
        )

    def log_safety_event(self, trigger: Trigger):
        """Log a safety intervention."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "safety_event",
            "trigger": self._serialize(trigger),
            "severity": trigger.severity.value
        }
        self._write_structured(data)

        # Also write to safety-specific log
        with open(self.safety_log, 'a') as f:
            f.write(json.dumps(data) + '\n')

        self.logger.critical(
            f"SAFETY EVENT: {trigger.trigger_type} - {trigger.description}"
        )

    def log_state_change(self, change_type: str, old_value: Any, new_value: Any, reason: str):
        """Log a system state change."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "state_change",
            "change_type": change_type,
            "old_value": self._serialize(old_value),
            "new_value": self._serialize(new_value),
            "reason": reason
        }
        self._write_structured(data)
        self.logger.info(
            f"State change: {change_type} from {old_value} to {new_value}"
        )

    def log_help_request(self, request: Any):
        """Log a help-seeking event."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "help_request",
            "request": self._serialize(request)
        }
        self._write_structured(data)
        self.logger.warning(f"Help requested: {request.specific_question}")

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an error."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        self._write_structured(data)
        self.logger.error(f"Error: {error}", exc_info=True)

    def get_recent_logs(self, n: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries."""
        return self.recent_logs[-n:]

    def get_logs_by_type(self, event_type: str, n: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs of specific type."""
        return [
            log for log in self.recent_logs
            if log.get("event_type") == event_type
        ][-n:]

    def create_snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of all logs."""
        return {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "total_logs": len(self.recent_logs),
            "recent_logs": self.recent_logs[-100:],
            "log_files": {
                "structured": str(self.structured_log),
                "human": str(self.human_log),
                "safety": str(self.safety_log),
                "decisions": str(self.decision_log)
            }
        }

    def _serialize(self, obj: Any) -> Any:
        """Serialize objects for JSON logging."""
        if hasattr(obj, '__dict__'):
            try:
                return asdict(obj)
            except:
                return str(obj)
        elif isinstance(obj, (list, tuple)):
            return [self._serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        else:
            return obj
