"""
Integration Tests for SARAI Phase 1
====================================

Tests the complete integration of JEPA, Router, Commit Law, and Review systems.

Author: John Fizer
"""

import unittest
import asyncio
import tempfile
import shutil
import numpy as np
from datetime import datetime

import sys
sys.path.append('..')

from sarai.core.world_model.jepa import JEPAWorldModel
from sarai.core.world_model.state import StateFeatures
from sarai.core.routing.relevance_router import RelevanceRouter
from sarai.core.commitment.commit_law import CommitLaw
from sarai.core.commitment.fsm import CommitState
from sarai.core.review.accountability import ReviewSystem
from sarai.types import Action, ActionType, EthicalAssessment, ReasoningOutput, AISResult, ARSResult
from sarai.safety.logging import ComprehensiveLogger


class TestPhase1Integration(unittest.TestCase):
    """Integration tests for Phase 1 modules."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = ComprehensiveLogger(self.temp_dir)

        # Initialize all systems
        self.jepa = JEPAWorldModel(
            embedding_dim=768,
            latent_dim=256,
            logger=self.logger
        )

        self.router = RelevanceRouter(
            current_stage=6,
            logger=self.logger,
            top_k=3
        )

        self.commit_law = CommitLaw(self.logger)
        self.review_system = ReviewSystem(self.logger)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_jepa_to_router_flow(self):
        """Test JEPA state features flow to router."""
        # Create observation
        observation = np.random.randn(768).astype(np.float32)

        # Update JEPA
        world_state = self.jepa.update(observation)

        # Extract state features
        state_features = self.jepa.get_state_features()

        # Activate router with state features
        activation = self.router.activate(state_features)

        # Verify activation
        self.assertEqual(len(activation.active_modules), 3)
        self.assertEqual(len(activation.weights), 12)
        self.assertAlmostEqual(sum(activation.weights), 1.0, places=5)

    def test_complete_cognitive_cycle(self):
        """Test complete cycle: JEPA → Router → Commit → Review."""
        # 1. JEPA: Process observation
        observation = np.random.randn(768).astype(np.float32)
        world_state = self.jepa.update(observation)
        state_features = self.jepa.get_state_features()

        # 2. Router: Allocate attention
        activation = self.router.activate(state_features)

        # 3. Commit Law: Make decision
        self.commit_law.enter_exploration({"test": "scenario"})

        reasoning = ReasoningOutput(
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

        self.commit_law.begin_evaluation(reasoning, {"action": 0.75})

        action = Action(
            action_type=ActionType.COMMUNICATION,
            description="Test action",
            parameters={},
            stakes=100.0,
            reversible=True
        )

        ethical = EthicalAssessment(
            permitted=True,
            confidence=0.85,
            reason="Test",
            deontological_score=0.9,
            consequentialist_score=0.8,
            virtue_score=0.85,
            narrative_patterns=["test"],
            timestamp=datetime.now()
        )

        commit = self.commit_law.decide(
            action=action,
            ethical_assessment=ethical,
            predicted_outcome="success",
            jepa_prediction_error=world_state.prediction_error or 0.2
        )

        # 4. Execute
        self.commit_law.begin_execution(commit.commit_id)
        self.commit_law.complete_execution(commit.commit_id, "success")

        # 5. Review: Assess outcome
        review_result = self.review_system.review_commit(
            commit,
            active_archetypes=activation.active_modules
        )

        # Verify complete flow
        self.assertTrue(review_result['prediction_matches'])
        self.assertEqual(
            self.commit_law.get_current_state(),
            CommitState.REVIEW
        )

    def test_learning_loop(self):
        """Test learning loop: Multiple decisions improve trust scores."""
        initial_trust = {
            arch: self.review_system.trust_scores[arch].score
            for arch in ["Analysis", "Structure"]
        }

        # Make multiple accurate predictions
        for i in range(5):
            # JEPA
            obs = np.random.randn(768).astype(np.float32)
            world_state = self.jepa.update(obs)
            state_features = self.jepa.get_state_features()

            # Router
            activation = self.router.activate(state_features)

            # Commit
            self.commit_law.enter_exploration({"iteration": i})

            reasoning = ReasoningOutput(
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

            self.commit_law.begin_evaluation(reasoning, {"action": 0.75})

            action = Action(
                action_type=ActionType.COMMUNICATION,
                description=f"Action {i}",
                parameters={},
                stakes=100.0,
                reversible=True
            )

            ethical = EthicalAssessment(
                permitted=True,
                confidence=0.85,
                reason="Test",
                deontological_score=0.9,
                consequentialist_score=0.8,
                virtue_score=0.85,
                narrative_patterns=["test"],
                timestamp=datetime.now()
            )

            commit = self.commit_law.decide(
                action=action,
                ethical_assessment=ethical,
                predicted_outcome="success",
                jepa_prediction_error=world_state.prediction_error or 0.2
            )

            self.commit_law.begin_execution(commit.commit_id)
            self.commit_law.complete_execution(commit.commit_id, "success")

            # Review (always accurate)
            self.review_system.review_commit(
                commit,
                active_archetypes=["Analysis", "Structure"]
            )

        # Trust scores should increase
        final_trust = {
            arch: self.review_system.trust_scores[arch].score
            for arch in ["Analysis", "Structure"]
        }

        for arch in ["Analysis", "Structure"]:
            self.assertGreater(final_trust[arch], initial_trust[arch])

    def test_router_adapts_to_jepa_state(self):
        """Test router activation adapts to different JEPA states."""
        # Low uncertainty scenario
        obs_low = np.random.randn(768).astype(np.float32) * 0.3
        self.jepa.update(obs_low)
        self.jepa.update(obs_low + np.random.randn(768).astype(np.float32) * 0.1)

        features_low = self.jepa.get_state_features()
        activation_low = self.router.activate(features_low)

        # High uncertainty scenario (new JEPA)
        jepa_high = JEPAWorldModel(768, 256, self.logger)
        obs_high = np.random.randn(768).astype(np.float32)
        jepa_high.update(obs_high)
        jepa_high.update(np.random.randn(768).astype(np.float32) * 3.0)  # Big change

        features_high = jepa_high.get_state_features()
        activation_high = self.router.activate(features_high)

        # Different uncertainty should produce different activations
        self.assertNotEqual(
            activation_low.active_modules,
            activation_high.active_modules
        )

    def test_contradiction_triggers_reopen(self):
        """Test strong contradiction can trigger commit reopen."""
        # Make commit with high confidence
        obs = np.random.randn(768).astype(np.float32)
        world_state = self.jepa.update(obs)

        self.commit_law.enter_exploration({"test": "scenario"})

        reasoning = ReasoningOutput(
            ais_result=AISResult(
                patterns_recognized=["test"],
                symbolic_interpretation="test",
                holistic_assessment="test",
                confidence=0.95,  # Very high confidence
                processing_time=0.1
            ),
            ars_result=ARSResult(
                logical_chain=["test"],
                causal_model={},
                quantitative_analysis={},
                confidence=0.95,
                processing_time=0.1
            ),
            synthesis="test",
            confidence=0.95,
            stream_agreement=0.95,
            conflicts=[],
            timestamp=datetime.now()
        )

        self.commit_law.begin_evaluation(reasoning, {"action": 0.95})

        action = Action(
            action_type=ActionType.COMMUNICATION,
            description="High confidence action",
            parameters={},
            stakes=100.0,
            reversible=True
        )

        ethical = EthicalAssessment(
            permitted=True,
            confidence=0.95,
            reason="Test",
            deontological_score=0.9,
            consequentialist_score=0.8,
            virtue_score=0.85,
            narrative_patterns=["test"],
            timestamp=datetime.now()
        )

        commit = self.commit_law.decide(
            action=action,
            ethical_assessment=ethical,
            predicted_outcome="certain_success",
            jepa_prediction_error=0.05  # Low prediction error
        )

        self.commit_law.begin_execution(commit.commit_id)
        self.commit_law.complete_execution(commit.commit_id, "total_failure")  # But wrong!

        # Review should detect strong contradiction
        review_result = self.review_system.review_commit(
            commit,
            active_archetypes=["Analysis"]
        )

        self.assertTrue(review_result['contradiction_detected'])
        self.assertGreater(review_result['contradiction_strength'], 0.7)

        # Can reopen if contradiction is strong
        if review_result['contradiction_strength'] > 0.8:
            self.commit_law.reopen_commit(
                commit.commit_id,
                contradiction_strength=review_result['contradiction_strength'],
                reason="Strong contradiction detected"
            )

            self.assertEqual(
                self.commit_law.get_current_state(),
                CommitState.REOPEN
            )

    def test_end_to_end_statistics(self):
        """Test end-to-end statistics across all systems."""
        # Run complete cycles
        for i in range(10):
            obs = np.random.randn(768).astype(np.float32)
            world_state = self.jepa.update(obs)
            state_features = self.jepa.get_state_features()

            activation = self.router.activate(state_features)

            self.commit_law.enter_exploration({"iteration": i})

            reasoning = ReasoningOutput(
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

            self.commit_law.begin_evaluation(reasoning, {"action": 0.75})

            action = Action(
                action_type=ActionType.COMMUNICATION,
                description=f"Action {i}",
                parameters={},
                stakes=100.0,
                reversible=True
            )

            ethical = EthicalAssessment(
                permitted=True,
                confidence=0.85,
                reason="Test",
                deontological_score=0.9,
                consequentialist_score=0.8,
                virtue_score=0.85,
                narrative_patterns=["test"],
                timestamp=datetime.now()
            )

            commit = self.commit_law.decide(
                action=action,
                ethical_assessment=ethical,
                predicted_outcome="success",
                jepa_prediction_error=world_state.prediction_error or 0.2
            )

            self.commit_law.begin_execution(commit.commit_id)

            # 70% accurate
            outcome = "success" if i < 7 else "failure"
            self.commit_law.complete_execution(commit.commit_id, outcome)

            self.review_system.review_commit(
                commit,
                active_archetypes=activation.active_modules
            )

        # Check all systems have consistent stats
        jepa_stats = self.jepa.get_stats()
        router_stats = self.router.get_stats()
        commit_stats = self.commit_law.get_stats()
        review_stats = self.review_system.get_stats()

        self.assertEqual(jepa_stats['state_history_length'], 10)
        self.assertEqual(router_stats['total_activations'], 10)
        self.assertEqual(commit_stats['commit_records']['total_commits'], 10)
        self.assertEqual(review_stats['total_reviews'], 10)

        # Accuracy should be 70%
        self.assertAlmostEqual(
            commit_stats['commit_records']['prediction_accuracy'],
            0.7,
            places=2
        )


if __name__ == '__main__':
    unittest.main()
