"""
Review & Accountability System
===============================

Compares predictions vs outcomes and updates trust scores.

This closes the loop:
- Commitments make predictions
- Actions produce outcomes
- Review compares them
- Trust/competency scores update
- System learns from results
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from sarai.core.commitment.records import Commit
from sarai.core.review.metrics import ReviewMetrics, TrustScore
from sarai.core.routing.archetypes import ARCHETYPES
from sarai.safety.logging import ComprehensiveLogger


class ReviewSystem:
    """
    Review and accountability system.

    Maintains trust scores and detects contradictions.
    """

    def __init__(self, logger: ComprehensiveLogger):
        """
        Initialize review system.

        Args:
            logger: Comprehensive logger
        """
        self.logger = logger
        self.metrics = ReviewMetrics()

        # Trust scores per archetype
        self.trust_scores: Dict[str, TrustScore] = {
            arch.name: TrustScore(archetype_name=arch.name, score=0.5)
            for arch in ARCHETYPES
        }

        # Review history
        self.review_history: List[Dict[str, Any]] = []
        self.max_history = 1000

        self.logger.logger.info("Review system initialized")

    def review_commit(
        self,
        commit: Commit,
        active_archetypes: List[str]
    ) -> Dict[str, Any]:
        """
        Review a commit after execution.

        Compares predicted vs actual outcome and updates trust.

        Args:
            commit: The commit to review
            active_archetypes: Which archetypes were active for this commit

        Returns:
            Review result
        """
        if commit.actual_outcome is None:
            self.logger.logger.warning(
                f"Cannot review commit {commit.commit_id} - no outcome recorded"
            )
            return {"status": "no_outcome"}

        # Compare prediction vs outcome
        matches = commit.matches_prediction()
        prediction_quality = self._assess_prediction_quality(commit)

        # Update metrics
        self.metrics.total_reviews += 1
        self.metrics.last_review = datetime.now()

        if matches:
            self.metrics.accurate_predictions += 1
            result_type = "accurate"
        elif prediction_quality == "minor_error":
            self.metrics.minor_errors += 1
            result_type = "minor_error"
        else:
            self.metrics.major_errors += 1
            result_type = "major_error"

        # Update trust scores for active archetypes
        for archetype_name in active_archetypes:
            if archetype_name in self.trust_scores:
                if matches:
                    self.trust_scores[archetype_name].update_success()
                elif prediction_quality == "minor_error":
                    self.trust_scores[archetype_name].update_minor_error()
                else:
                    self.trust_scores[archetype_name].update_failure()

        # Detect contradictions
        contradiction_detected, contradiction_strength = self._detect_contradiction(
            commit, result_type
        )

        if contradiction_detected:
            self.metrics.contradictions += 1

        # Create review record
        review_record = {
            "commit_id": commit.commit_id,
            "timestamp": datetime.now(),
            "result_type": result_type,
            "prediction_matches": matches,
            "prediction_quality": prediction_quality,
            "contradiction_detected": contradiction_detected,
            "contradiction_strength": contradiction_strength,
            "active_archetypes": active_archetypes,
            "updated_trust_scores": {
                name: score.score
                for name, score in self.trust_scores.items()
                if name in active_archetypes
            }
        }

        # Store in history
        self.review_history.append(review_record)
        if len(self.review_history) > self.max_history:
            self.review_history.pop(0)

        # Log
        self.logger.logger.info(
            f"Review complete for {commit.commit_id}: {result_type} "
            f"(contradiction: {contradiction_detected})"
        )

        return review_record

    def _assess_prediction_quality(self, commit: Commit) -> str:
        """
        Assess quality of prediction.

        Returns:
            "accurate", "minor_error", or "major_error"
        """
        if commit.matches_prediction(tolerance=0.2):
            return "accurate"

        # Check if it's close (minor error)
        if commit.matches_prediction(tolerance=0.5):
            return "minor_error"

        return "major_error"

    def _detect_contradiction(
        self,
        commit: Commit,
        result_type: str
    ) -> tuple[bool, float]:
        """
        Detect if outcome contradicts committed belief strongly enough
        to trigger reopen.

        Returns:
            (contradiction_detected, strength)
        """
        # Major errors with high confidence are contradictions
        if result_type == "major_error" and commit.confidence > 0.7:
            return True, 0.9

        # Ethical violations are contradictions
        if commit.metadata.get("ethical_violation"):
            return True, 1.0

        # Safety violations are contradictions
        if commit.metadata.get("safety_violation"):
            return True, 1.0

        # No contradiction
        return False, 0.0

    def generate_report(self, last_n: int = 100) -> Dict[str, Any]:
        """
        Generate accountability report.

        Args:
            last_n: Number of recent reviews to summarize

        Returns:
            Comprehensive report
        """
        recent_reviews = self.review_history[-last_n:]

        # Aggregate recent results
        recent_accurate = sum(
            1 for r in recent_reviews
            if r["prediction_matches"]
        )

        recent_contradictions = sum(
            1 for r in recent_reviews
            if r["contradiction_detected"]
        )

        # Trust scores summary
        trust_summary = {
            name: {
                "score": score.score,
                "accuracy_rate": score.accuracy_rate(),
                "predictions": score.num_predictions
            }
            for name, score in self.trust_scores.items()
        }

        # Top and bottom performers
        sorted_trust = sorted(
            self.trust_scores.items(),
            key=lambda x: x[1].score,
            reverse=True
        )

        top_performers = [
            {"name": name, "score": score.score}
            for name, score in sorted_trust[:5]
        ]

        bottom_performers = [
            {"name": name, "score": score.score}
            for name, score in sorted_trust[-5:]
        ]

        return {
            "overall_metrics": self.metrics.to_dict(),
            "recent_performance": {
                "reviews": len(recent_reviews),
                "accurate": recent_accurate,
                "accuracy_rate": recent_accurate / len(recent_reviews) if recent_reviews else 0.0,
                "contradictions": recent_contradictions
            },
            "trust_scores": trust_summary,
            "top_performers": top_performers,
            "bottom_performers": bottom_performers,
            "generated_at": datetime.now().isoformat()
        }

    def get_archetype_trust(self, archetype_name: str) -> float:
        """Get trust score for specific archetype."""
        if archetype_name in self.trust_scores:
            return self.trust_scores[archetype_name].score
        return 0.5  # Default

    def get_average_trust(self) -> float:
        """Get average trust across all archetypes."""
        if not self.trust_scores:
            return 0.5

        return sum(score.score for score in self.trust_scores.values()) / len(self.trust_scores)

    def recommend_reopen(self, commit: Commit) -> tuple[bool, str]:
        """
        Recommend whether to reopen a commit.

        Args:
            commit: Commit to evaluate

        Returns:
            (should_reopen, reason)
        """
        # Find review for this commit
        review = None
        for r in reversed(self.review_history):
            if r["commit_id"] == commit.commit_id:
                review = r
                break

        if not review:
            return False, "No review found"

        if review["contradiction_detected"]:
            strength = review["contradiction_strength"]
            return True, f"Contradiction detected (strength: {strength:.2f})"

        return False, "No reopen recommended"

    def get_stats(self) -> Dict[str, Any]:
        """Get review system statistics."""
        return {
            "total_reviews": len(self.review_history),
            "metrics": self.metrics.to_dict(),
            "average_trust": self.get_average_trust(),
            "trust_distribution": {
                "high": sum(1 for s in self.trust_scores.values() if s.score >= 0.7),
                "medium": sum(1 for s in self.trust_scores.values() if 0.3 <= s.score < 0.7),
                "low": sum(1 for s in self.trust_scores.values() if s.score < 0.3)
            }
        }
