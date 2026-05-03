"""
Unit Tests for Commit Law FSM
==============================

Author: John Fizer
"""

import unittest
import tempfile
import shutil
from datetime import datetime

import sys
sys.path.append('..')

from sarai.core.commitment.commit_law import CommitLaw
from sarai.core.commitment.fsm import CommitState, VALID_TRANSITIONS
from sarai.core.commitment.records import Commit
from sarai.types import Action, ActionType, EthicalAssessment, ReasoningOutput, AISResult, ARSResult
from sarai.safety.logging import ComprehensiveLogger


class TestCommitState(unittest.TestCase):
    """Test FSM state definitions."""

    def test_all_states_exist(self):
        """Test all required states exist."""
        expected_states = [
            CommitState.EXPLORE,
            CommitState.EVALUATE,
            CommitState.COMMIT,
            CommitState.EXECUTE,
            CommitState.REVIEW,
            CommitState.REOPEN
        ]

        for state in expected_states:
            self.assertIsInstance(state, CommitState)

    def test_valid_transitions_defined(self):
        """Test valid transitions are defined for all states."""
        for state in CommitState:
            self.assertIn(state, VALID_TRANSITIONS)
            self.assertIsInstance(VALID_TRANSITIONS[state], list)


class TestCommit(unittest.TestCase):
    """Test Commit record functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_action = Action(
            action_type=ActionType.COMMUNICATION,
            description="Test action",
            parameters={},
            stakes=100.0,
            reversible=True
        )

        self.sample_ethical = EthicalAssessment(
            permitted=True,
            confidence=0.85,
            reason="Test reason",
            deontological_score=0.9,
            consequentialist_score=0.8,
            virtue_score=0.85,
            narrative_patterns=["test"],
            timestamp=datetime.now()
        )

    def test_commit_creation(self):
        """Test creating a commit."""
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

        self.assertEqual(commit.commit_id, "test_001")
        self.assertIsNone(commit.actual_outcome)
        self.assertFalse(commit.resolved)

    def test_hash_generation(self):
        """Test commit hash is generated."""
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

        self.assertIsNotNone(commit._hash)
        self.assertEqual(len(commit._hash), 64)  # SHA-256 hex = 64 chars

    def test_hash_immutability(self):
        """Test commit hash doesn't change."""
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

        original_hash = commit._hash

        # Set outcome (doesn't change hash of core fields)
        commit.set_outcome("actual_success")

        self.assertEqual(commit._hash, original_hash)

    def test_verify_integrity_valid(self):
        """Test integrity verification for valid commit."""
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

        self.assertTrue(commit.verify_integrity())

    def test_set_outcome(self):
        """Test setting actual outcome."""
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

        commit.set_outcome("actual_success")

        self.assertEqual(commit.actual_outcome, "actual_success")
        self.assertTrue(commit.resolved)
        self.assertGreater(len(commit.audit_log), 0)

    def test_matches_prediction(self):
        """Test prediction matching."""
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

        # Before outcome set
        self.assertFalse(commit.matches_prediction())

        # Matching outcome
        commit.set_outcome("success")
        self.assertTrue(commit.matches_prediction())

        # Different commit with non-matching outcome
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
        self.assertFalse(commit2.matches_prediction())

    def test_audit_log(self):
        """Test audit log is maintained."""
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

        initial_log_len = len(commit.audit_log)

        commit.set_outcome("success")

        self.assertGreater(len(commit.audit_log), initial_log_len)


class TestCommitLaw(unittest.TestCase):
    """Test Commit Law FSM functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = ComprehensiveLogger(self.temp_dir)
        self.commit_law = CommitLaw(self.logger)

        self.sample_action = Action(
            action_type=ActionType.COMMUNICATION,
            description="Test action",
            parameters={},
            stakes=100.0,
            reversible=True
        )

        self.sample_ethical = EthicalAssessment(
            permitted=True,
            confidence=0.85,
            reason="Test reason",
            deontological_score=0.9,
            consequentialist_score=0.8,
            virtue_score=0.85,
            narrative_patterns=["test"],
            timestamp=datetime.now()
        )

        self.sample_reasoning = ReasoningOutput(
            ais_result=AISResult(
                patterns_recognized=["test"],
                symbolic_interpretation="test",
                holistic_assessment="test",
                confidence=0.75,
                processing_time=0.1
            ),
            ars_result=ARSResult(
                logical_chain=["test"],
                causal_model={},
                quantitative_analysis={},
                confidence=0.75,
                processing_time=0.1
            ),
            synthesis="test",
            confidence=0.75,
            stream_agreement=0.8,
            conflicts=[],
            timestamp=datetime.now()
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test CommitLaw initializes in EXPLORE state."""
        self.assertEqual(
            self.commit_law.get_current_state(),
            CommitState.EXPLORE
        )

    def test_enter_exploration(self):
        """Test entering exploration."""
        context = {"situation": "test"}
        self.commit_law.enter_exploration(context)

        self.assertEqual(
            self.commit_law.get_current_state(),
            CommitState.EXPLORE
        )

    def test_add_option(self):
        """Test adding option during exploration."""
        self.commit_law.enter_exploration({"test": "context"})

        option = {"action": "test_option"}
        self.commit_law.add_option(option)

        # Verify option was added (internal state)
        self.assertIn(option, self.commit_law._current_options)

    def test_begin_evaluation(self):
        """Test transitioning to evaluation."""
        self.commit_law.enter_exploration({"test": "context"})

        self.commit_law.begin_evaluation(
            self.sample_reasoning,
            {"option_1": 0.7}
        )

        self.assertEqual(
            self.commit_law.get_current_state(),
            CommitState.EVALUATE
        )

    def test_decide_creates_commit(self):
        """Test decide creates commit and transitions to COMMIT."""
        self.commit_law.enter_exploration({"test": "context"})
        self.commit_law.begin_evaluation(
            self.sample_reasoning,
            {"option_1": 0.7}
        )

        commit = self.commit_law.decide(
            action=self.sample_action,
            ethical_assessment=self.sample_ethical,
            predicted_outcome="success",
            jepa_prediction_error=0.2
        )

        self.assertIsNotNone(commit)
        self.assertIsInstance(commit, Commit)
        self.assertEqual(
            self.commit_law.get_current_state(),
            CommitState.COMMIT
        )

    def test_begin_execution(self):
        """Test transitioning to execution."""
        self.commit_law.enter_exploration({"test": "context"})
        self.commit_law.begin_evaluation(self.sample_reasoning, {"option_1": 0.7})

        commit = self.commit_law.decide(
            self.sample_action,
            self.sample_ethical,
            "success",
            0.2
        )

        self.commit_law.begin_execution(commit.commit_id)

        self.assertEqual(
            self.commit_law.get_current_state(),
            CommitState.EXECUTE
        )

    def test_complete_execution(self):
        """Test completing execution and transitioning to REVIEW."""
        self.commit_law.enter_exploration({"test": "context"})
        self.commit_law.begin_evaluation(self.sample_reasoning, {"option_1": 0.7})

        commit = self.commit_law.decide(
            self.sample_action,
            self.sample_ethical,
            "success",
            0.2
        )

        self.commit_law.begin_execution(commit.commit_id)
        self.commit_law.complete_execution(commit.commit_id, "actual_success")

        self.assertEqual(
            self.commit_law.get_current_state(),
            CommitState.REVIEW
        )

        # Verify outcome was set
        retrieved_commit = self.commit_law.get_commit(commit.commit_id)
        self.assertEqual(retrieved_commit.actual_outcome, "actual_success")
        self.assertTrue(retrieved_commit.resolved)

    def test_invalid_transition_raises_error(self):
        """Test invalid transition raises error."""
        # Try to execute before committing
        with self.assertRaises(ValueError):
            self.commit_law.begin_execution("nonexistent_id")

    def test_reopen_commit(self):
        """Test reopening a commit on strong contradiction."""
        self.commit_law.enter_exploration({"test": "context"})
        self.commit_law.begin_evaluation(self.sample_reasoning, {"option_1": 0.7})

        commit = self.commit_law.decide(
            self.sample_action,
            self.sample_ethical,
            "success",
            0.2
        )

        self.commit_law.begin_execution(commit.commit_id)
        self.commit_law.complete_execution(commit.commit_id, "total_failure")

        # Reopen with strong contradiction
        self.commit_law.reopen_commit(
            commit.commit_id,
            contradiction_strength=0.95,
            reason="Major prediction failure"
        )

        self.assertEqual(
            self.commit_law.get_current_state(),
            CommitState.REOPEN
        )

    def test_get_stats(self):
        """Test statistics retrieval."""
        # Make a complete cycle
        self.commit_law.enter_exploration({"test": "context"})
        self.commit_law.begin_evaluation(self.sample_reasoning, {"option_1": 0.7})

        commit = self.commit_law.decide(
            self.sample_action,
            self.sample_ethical,
            "success",
            0.2
        )

        self.commit_law.begin_execution(commit.commit_id)
        self.commit_law.complete_execution(commit.commit_id, "success")

        stats = self.commit_law.get_stats()

        self.assertEqual(stats['current_state'], "review")
        self.assertGreater(stats['total_transitions'], 0)
        self.assertIn('commit_records', stats)

    def test_commit_records_stats(self):
        """Test commit records statistics."""
        # Create multiple commits
        for i in range(3):
            self.commit_law.enter_exploration({"test": f"context_{i}"})
            self.commit_law.begin_evaluation(self.sample_reasoning, {"option_1": 0.7})

            commit = self.commit_law.decide(
                self.sample_action,
                self.sample_ethical,
                "success",
                0.2
            )

            self.commit_law.begin_execution(commit.commit_id)
            outcome = "success" if i < 2 else "failure"
            self.commit_law.complete_execution(commit.commit_id, outcome)

        stats = self.commit_law.get_stats()
        record_stats = stats['commit_records']

        self.assertEqual(record_stats['total_commits'], 3)
        self.assertEqual(record_stats['resolved'], 3)
        self.assertAlmostEqual(record_stats['prediction_accuracy'], 2/3, places=2)

    def test_commit_integrity_verification(self):
        """Test all commits maintain integrity."""
        self.commit_law.enter_exploration({"test": "context"})
        self.commit_law.begin_evaluation(self.sample_reasoning, {"option_1": 0.7})

        commit = self.commit_law.decide(
            self.sample_action,
            self.sample_ethical,
            "success",
            0.2
        )

        stats = self.commit_law.get_stats()
        self.assertTrue(stats['commit_records']['integrity_verified'])


if __name__ == '__main__':
    unittest.main()
