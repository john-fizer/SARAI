"""
Unit Tests for Review & Accountability System
==============================================

Author: John Fizer
"""

import unittest
import tempfile
import shutil
from datetime import datetime

import sys
sys.path.append('..')

from sarai.core.review.accountability import ReviewSystem
from sarai.core.review.metrics import TrustScore, ReviewMetrics
from sarai.core.commitment.records import Commit
from sarai.safety.logging import ComprehensiveLogger


class TestTrustScore(unittest.TestCase):
    """Test TrustScore functionality."""

    def test_creation(self):
        """Test creating a trust score."""
        trust = TrustScore(
            archetype_name="Analysis",
            score=0.5,
            num_predictions=0
        )

        self.assertEqual(trust.archetype_name, "Analysis")
        self.assertEqual(trust.score, 0.5)
        self.assertEqual(trust.num_predictions, 0)

    def test_update_success(self):
        """Test updating trust score on success."""
        trust = TrustScore("Analysis", 0.5, 0)

        initial_score = trust.score
        trust.update_success()

        self.assertGreater(trust.score, initial_score)
        self.assertEqual(trust.num_predictions, 1)

    def test_update_failure(self):
        """Test updating trust score on failure."""
        trust = TrustScore("Analysis", 0.5, 0)

        initial_score = trust.score
        trust.update_failure()

        self.assertLess(trust.score, initial_score)
        self.assertEqual(trust.num_predictions, 1)

    def test_score_bounds_upper(self):
        """Test score doesn't exceed 1.0."""
        trust = TrustScore("Analysis", 0.95, 0)

        # Multiple successes
        for _ in range(10):
            trust.update_success()

        self.assertLessEqual(trust.score, 1.0)

    def test_score_bounds_lower(self):
        """Test score doesn't go below 0.0."""
        trust = TrustScore("Analysis", 0.05, 0)

        # Multiple failures
        for _ in range(10):
            trust.update_failure()

        self.assertGreaterEqual(trust.score, 0.0)

    def test_multiple_updates(self):
        """Test multiple updates."""
        trust = TrustScore("Analysis", 0.5, 0)

        # 2 successes, 1 failure
        trust.update_success()
        trust.update_success()
        trust.update_failure()

        self.assertEqual(trust.num_predictions, 3)


class TestReviewMetrics(unittest.TestCase):
    """Test ReviewMetrics functionality."""

    def test_creation(self):
        """Test creating review metrics."""
        metrics = ReviewMetrics(
            total_reviews=0,
            accurate_predictions=0,
            errors=0,
            contradictions=0
        )

        self.assertEqual(metrics.total_reviews, 0)
        self.assertEqual(metrics.accurate_predictions, 0)

    def test_accuracy_rate_calculation(self):
        """Test accuracy rate calculation."""
        metrics = ReviewMetrics(
            total_reviews=10,
            accurate_predictions=7,
            errors=3,
            contradictions=0
        )

        self.assertEqual(metrics.accuracy_rate(), 0.7)

    def test_accuracy_rate_with_no_reviews(self):
        """Test accuracy rate with no reviews."""
        metrics = ReviewMetrics(
            total_reviews=0,
            accurate_predictions=0,
            errors=0,
            contradictions=0
        )

        self.assertEqual(metrics.accuracy_rate(), 0.0)

    def test_error_rate_calculation(self):
        """Test error rate calculation."""
        metrics = ReviewMetrics(
            total_reviews=10,
            accurate_predictions=7,
            errors=3,
            contradictions=0
        )

        self.assertEqual(metrics.error_rate(), 0.3)


class TestReviewSystem(unittest.TestCase):
    """Test ReviewSystem functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = ComprehensiveLogger(self.temp_dir)
        self.review_system = ReviewSystem(self.logger)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test review system initializes correctly."""
        self.assertEqual(len(self.review_system.trust_scores), 12)

        # All trust scores start at 0.5
        for trust in self.review_system.trust_scores.values():
            self.assertEqual(trust.score, 0.5)

    def test_review_accurate_prediction(self):
        """Test reviewing accurate prediction."""
        commit = Commit(
            commit_id="test_001",
            timestamp=datetime.now(),
            state_claimed={"test": "value"},
            reasoning="Test reasoning",
            confidence=0.75,
            safety_cleared=True,
            ethics_approved=True,
            ethical_scores={"deontological": 0.9},
            predicted_outcome="success",
            jepa_prediction_error=0.2
        )

        commit.set_outcome("success")

        result = self.review_system.review_commit(
            commit,
            active_archetypes=["Analysis", "Structure"]
        )

        self.assertEqual(result['result_type'], 'accurate')
        self.assertTrue(result['prediction_matches'])
        self.assertFalse(result['contradiction_detected'])

        # Trust scores should increase
        for arch in ["Analysis", "Structure"]:
            self.assertGreater(
                self.review_system.trust_scores[arch].score,
                0.5
            )

    def test_review_prediction_error(self):
        """Test reviewing prediction error."""
        commit = Commit(
            commit_id="test_001",
            timestamp=datetime.now(),
            state_claimed={"test": "value"},
            reasoning="Test reasoning",
            confidence=0.75,
            safety_cleared=True,
            ethics_approved=True,
            ethical_scores={"deontological": 0.9},
            predicted_outcome="success",
            jepa_prediction_error=0.2
        )

        commit.set_outcome("failure")

        result = self.review_system.review_commit(
            commit,
            active_archetypes=["Analysis", "Structure"]
        )

        self.assertEqual(result['result_type'], 'error')
        self.assertFalse(result['prediction_matches'])

        # Trust scores should decrease
        for arch in ["Analysis", "Structure"]:
            self.assertLess(
                self.review_system.trust_scores[arch].score,
                0.5
            )

    def test_contradiction_detection(self):
        """Test contradiction detection."""
        commit = Commit(
            commit_id="test_001",
            timestamp=datetime.now(),
            state_claimed={"test": "value"},
            reasoning="Very confident reasoning",
            confidence=0.95,  # High confidence
            safety_cleared=True,
            ethics_approved=True,
            ethical_scores={"deontological": 0.9},
            predicted_outcome="success",
            jepa_prediction_error=0.1  # Low prediction error
        )

        commit.set_outcome("complete_failure")  # But wrong!

        result = self.review_system.review_commit(
            commit,
            active_archetypes=["Analysis"]
        )

        self.assertTrue(result['contradiction_detected'])
        self.assertGreater(result['contradiction_strength'], 0.0)

    def test_no_contradiction_low_confidence(self):
        """Test no contradiction on low confidence error."""
        commit = Commit(
            commit_id="test_001",
            timestamp=datetime.now(),
            state_claimed={"test": "value"},
            reasoning="Uncertain reasoning",
            confidence=0.4,  # Low confidence
            safety_cleared=True,
            ethics_approved=True,
            ethical_scores={"deontological": 0.9},
            predicted_outcome="success",
            jepa_prediction_error=0.6  # High prediction error
        )

        commit.set_outcome("failure")

        result = self.review_system.review_commit(
            commit,
            active_archetypes=["Analysis"]
        )

        # Might detect weak contradiction but should have low strength
        if result['contradiction_detected']:
            self.assertLess(result['contradiction_strength'], 0.5)

    def test_get_stats(self):
        """Test statistics retrieval."""
        # Create and review multiple commits
        for i in range(5):
            commit = Commit(
                commit_id=f"test_{i:03d}",
                timestamp=datetime.now(),
                state_claimed={"test": f"value_{i}"},
                reasoning="Test reasoning",
                confidence=0.75,
                safety_cleared=True,
                ethics_approved=True,
                ethical_scores={"deontological": 0.9},
                predicted_outcome="success",
                jepa_prediction_error=0.2
            )

            # 3 accurate, 2 errors
            outcome = "success" if i < 3 else "failure"
            commit.set_outcome(outcome)

            self.review_system.review_commit(
                commit,
                active_archetypes=["Analysis"]
            )

        stats = self.review_system.get_stats()

        self.assertEqual(stats['total_reviews'], 5)
        self.assertEqual(stats['metrics']['accurate_predictions'], 3)
        self.assertEqual(stats['metrics']['errors'], 2)
        self.assertAlmostEqual(stats['metrics']['accuracy_rate'], 0.6, places=2)

    def test_generate_report(self):
        """Test report generation."""
        # Create and review commits
        for i in range(10):
            commit = Commit(
                commit_id=f"test_{i:03d}",
                timestamp=datetime.now(),
                state_claimed={"test": f"value_{i}"},
                reasoning="Test reasoning",
                confidence=0.75,
                safety_cleared=True,
                ethics_approved=True,
                ethical_scores={"deontological": 0.9},
                predicted_outcome="success",
                jepa_prediction_error=0.2
            )

            outcome = "success" if i < 7 else "failure"
            commit.set_outcome(outcome)

            # Vary archetypes
            archetypes = ["Analysis"] if i % 2 == 0 else ["Structure"]
            self.review_system.review_commit(commit, active_archetypes=archetypes)

        report = self.review_system.generate_report(last_n=10)

        self.assertIn('recent_performance', report)
        self.assertIn('top_performers', report)
        self.assertIn('bottom_performers', report)

        # Recent performance
        recent = report['recent_performance']
        self.assertEqual(recent['reviews'], 10)
        self.assertEqual(recent['accurate'], 7)

        # Top and bottom performers
        self.assertGreater(len(report['top_performers']), 0)
        self.assertGreater(len(report['bottom_performers']), 0)

    def test_trust_score_persistence(self):
        """Test trust scores persist across multiple reviews."""
        initial_score = self.review_system.trust_scores["Analysis"].score

        # Multiple accurate predictions
        for i in range(5):
            commit = Commit(
                commit_id=f"test_{i:03d}",
                timestamp=datetime.now(),
                state_claimed={"test": f"value_{i}"},
                reasoning="Test reasoning",
                confidence=0.75,
                safety_cleared=True,
                ethics_approved=True,
                ethical_scores={"deontological": 0.9},
                predicted_outcome="success",
                jepa_prediction_error=0.2
            )

            commit.set_outcome("success")
            self.review_system.review_commit(
                commit,
                active_archetypes=["Analysis"]
            )

        final_score = self.review_system.trust_scores["Analysis"].score

        self.assertGreater(final_score, initial_score)
        self.assertEqual(
            self.review_system.trust_scores["Analysis"].num_predictions,
            5
        )

    def test_different_archetypes_independent(self):
        """Test different archetypes have independent trust scores."""
        # Accurate for Analysis
        commit1 = Commit(
            commit_id="test_001",
            timestamp=datetime.now(),
            state_claimed={"test": "value"},
            reasoning="Test reasoning",
            confidence=0.75,
            safety_cleared=True,
            ethics_approved=True,
            ethical_scores={"deontological": 0.9},
            predicted_outcome="success",
            jepa_prediction_error=0.2
        )
        commit1.set_outcome("success")
        self.review_system.review_commit(commit1, active_archetypes=["Analysis"])

        # Error for Structure
        commit2 = Commit(
            commit_id="test_002",
            timestamp=datetime.now(),
            state_claimed={"test": "value"},
            reasoning="Test reasoning",
            confidence=0.75,
            safety_cleared=True,
            ethics_approved=True,
            ethical_scores={"deontological": 0.9},
            predicted_outcome="success",
            jepa_prediction_error=0.2
        )
        commit2.set_outcome("failure")
        self.review_system.review_commit(commit2, active_archetypes=["Structure"])

        # Analysis should be higher than Structure
        self.assertGreater(
            self.review_system.trust_scores["Analysis"].score,
            self.review_system.trust_scores["Structure"].score
        )

    def test_review_history_tracking(self):
        """Test review history is tracked."""
        commit = Commit(
            commit_id="test_001",
            timestamp=datetime.now(),
            state_claimed={"test": "value"},
            reasoning="Test reasoning",
            confidence=0.75,
            safety_cleared=True,
            ethics_approved=True,
            ethical_scores={"deontological": 0.9},
            predicted_outcome="success",
            jepa_prediction_error=0.2
        )
        commit.set_outcome("success")

        self.review_system.review_commit(commit, active_archetypes=["Analysis"])

        self.assertEqual(len(self.review_system.review_history), 1)


if __name__ == '__main__':
    unittest.main()
