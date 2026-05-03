"""
Review Metrics
==============

Metrics for tracking prediction accuracy and trust.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class TrustScore:
    """
    Trust score for a particular competency/archetype.

    Trust is earned through accurate predictions and good outcomes.
    """
    archetype_name: str
    score: float  # 0-1, starts at 0.5
    num_predictions: int = 0
    num_accurate: int = 0
    num_failures: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

    def accuracy_rate(self) -> float:
        """Get prediction accuracy rate."""
        if self.num_predictions == 0:
            return 0.5  # Default
        return self.num_accurate / self.num_predictions

    def update_success(self):
        """Record a successful prediction."""
        self.num_predictions += 1
        self.num_accurate += 1

        # Increase trust (diminishing returns)
        self.score = min(self.score + 0.05 * (1 - self.score), 1.0)
        self.last_updated = datetime.now()

    def update_failure(self):
        """Record a failed prediction."""
        self.num_predictions += 1
        self.num_failures += 1

        # Decrease trust
        self.score = max(self.score - 0.10, 0.0)
        self.last_updated = datetime.now()

    def update_minor_error(self):
        """Record a minor error (close but not quite)."""
        self.num_predictions += 1

        # Slight decrease
        self.score = max(self.score - 0.02, 0.0)
        self.last_updated = datetime.now()


@dataclass
class ReviewMetrics:
    """
    Aggregated metrics from review process.
    """
    total_reviews: int = 0
    accurate_predictions: int = 0
    minor_errors: int = 0
    major_errors: int = 0
    contradictions: int = 0

    # Value alignment
    value_aligned: int = 0
    value_misaligned: int = 0

    # Safety
    safety_violations: int = 0
    ethical_violations: int = 0

    # Timestamps
    last_review: datetime = field(default_factory=datetime.now)

    def accuracy_rate(self) -> float:
        """Overall prediction accuracy."""
        if self.total_reviews == 0:
            return 0.0
        return self.accurate_predictions / self.total_reviews

    def error_rate(self) -> float:
        """Overall error rate."""
        if self.total_reviews == 0:
            return 0.0
        return (self.minor_errors + self.major_errors) / self.total_reviews

    def value_alignment_rate(self) -> float:
        """Value alignment rate."""
        total = self.value_aligned + self.value_misaligned
        if total == 0:
            return 0.0
        return self.value_aligned / total

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_reviews": self.total_reviews,
            "accuracy_rate": self.accuracy_rate(),
            "error_rate": self.error_rate(),
            "value_alignment_rate": self.value_alignment_rate(),
            "contradictions": self.contradictions,
            "safety_violations": self.safety_violations,
            "ethical_violations": self.ethical_violations
        }
