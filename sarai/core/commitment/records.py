"""
Commit Records
==============

Immutable records of commitments made by SARAI.
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class Commit:
    """
    An immutable commitment record.

    Once created, this represents a binding belief/decision/policy
    that SARAI has made.
    """
    commit_id: str
    timestamp: datetime
    state_claimed: Dict[str, Any]  # What is being committed to
    reasoning: str  # Why this commitment
    confidence: float  # Confidence in this commitment (0-1)

    # Gating results
    safety_cleared: bool
    ethics_approved: bool
    ethical_scores: Dict[str, float]

    # Predictions
    predicted_outcome: Any
    jepa_prediction_error: float

    # Actual results (filled in later)
    actual_outcome: Optional[Any] = None
    outcome_timestamp: Optional[datetime] = None

    # Policy
    reopen_policy: str = "only_on_contradiction"
    reopen_threshold: float = 0.8  # Contradiction strength needed

    # Audit trail
    audit_log: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Generate hash for immutability verification."""
        if not hasattr(self, '_hash'):
            self._hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute hash of core commitment fields."""
        # Hash the immutable parts
        core = {
            "commit_id": self.commit_id,
            "timestamp": self.timestamp.isoformat(),
            "state_claimed": json.dumps(self.state_claimed, sort_keys=True),
            "reasoning": self.reasoning,
            "confidence": self.confidence
        }

        content = json.dumps(core, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify commit hasn't been tampered with."""
        return self._hash == self._compute_hash()

    def add_audit_entry(self, entry: str):
        """Add entry to audit log."""
        timestamp = datetime.now().isoformat()
        self.audit_log.append(f"[{timestamp}] {entry}")

    def set_outcome(self, outcome: Any):
        """Record actual outcome (can only be set once)."""
        if self.actual_outcome is not None:
            raise ValueError("Outcome already set - commits are immutable")

        self.actual_outcome = outcome
        self.outcome_timestamp = datetime.now()
        self.add_audit_entry(f"Outcome recorded: {outcome}")

    def matches_prediction(self, tolerance: float = 0.2) -> bool:
        """Check if outcome matches prediction (within tolerance)."""
        if self.actual_outcome is None:
            return False

        # Simplified comparison
        # In production, would use more sophisticated matching
        try:
            if isinstance(self.predicted_outcome, (int, float)) and isinstance(self.actual_outcome, (int, float)):
                diff = abs(self.predicted_outcome - self.actual_outcome)
                expected_range = abs(self.predicted_outcome) * tolerance
                return diff <= expected_range
            else:
                # For non-numeric, use equality
                return self.predicted_outcome == self.actual_outcome
        except:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.outcome_timestamp:
            data['outcome_timestamp'] = self.outcome_timestamp.isoformat()
        data['hash'] = self._hash
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Commit':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('outcome_timestamp'):
            data['outcome_timestamp'] = datetime.fromisoformat(data['outcome_timestamp'])

        # Remove hash before creating (will be recomputed)
        data.pop('hash', None)

        return cls(**data)


class CommitRecord:
    """
    Record keeper for all commitments.

    Maintains immutable history of all commits.
    """

    def __init__(self):
        """Initialize record keeper."""
        self.commits: Dict[str, Commit] = {}
        self.commit_sequence: List[str] = []

    def add_commit(self, commit: Commit):
        """Add a new commit to the record."""
        if commit.commit_id in self.commits:
            raise ValueError(f"Commit {commit.commit_id} already exists")

        self.commits[commit.commit_id] = commit
        self.commit_sequence.append(commit.commit_id)

    def get_commit(self, commit_id: str) -> Optional[Commit]:
        """Get commit by ID."""
        return self.commits.get(commit_id)

    def get_recent_commits(self, n: int = 10) -> List[Commit]:
        """Get n most recent commits."""
        recent_ids = self.commit_sequence[-n:]
        return [self.commits[cid] for cid in recent_ids]

    def get_commits_by_confidence(self, min_confidence: float = 0.8) -> List[Commit]:
        """Get commits above confidence threshold."""
        return [
            c for c in self.commits.values()
            if c.confidence >= min_confidence
        ]

    def get_unresolved_commits(self) -> List[Commit]:
        """Get commits without outcomes."""
        return [
            c for c in self.commits.values()
            if c.actual_outcome is None
        ]

    def verify_all_integrity(self) -> bool:
        """Verify integrity of all commits."""
        return all(c.verify_integrity() for c in self.commits.values())

    def get_stats(self) -> Dict[str, Any]:
        """Get commit statistics."""
        total = len(self.commits)
        if total == 0:
            return {
                "total_commits": 0,
                "avg_confidence": 0.0,
                "resolution_rate": 0.0
            }

        resolved = sum(1 for c in self.commits.values() if c.actual_outcome is not None)
        matches = sum(
            1 for c in self.commits.values()
            if c.actual_outcome is not None and c.matches_prediction()
        )

        return {
            "total_commits": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "resolution_rate": resolved / total,
            "prediction_accuracy": matches / resolved if resolved > 0 else 0.0,
            "avg_confidence": sum(c.confidence for c in self.commits.values()) / total,
            "integrity_verified": self.verify_all_integrity()
        }
