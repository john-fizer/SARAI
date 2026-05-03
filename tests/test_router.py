"""
Unit Tests for Relevance Router
================================

Author: John Fizer
"""

import unittest
import tempfile
import shutil

import sys
sys.path.append('..')

from sarai.core.routing.relevance_router import RelevanceRouter, ActivationResult
from sarai.core.routing.archetypes import ARCHETYPES, Archetype
from sarai.core.world_model.state import StateFeatures
from sarai.safety.logging import ComprehensiveLogger


class TestArchetypes(unittest.TestCase):
    """Test archetype definitions."""

    def test_archetype_count(self):
        """Test there are exactly 12 archetypes."""
        self.assertEqual(len(ARCHETYPES), 12)

    def test_archetype_ids(self):
        """Test archetype IDs are 1-12."""
        ids = [arch.id for arch in ARCHETYPES]
        self.assertEqual(ids, list(range(1, 13)))

    def test_archetype_names(self):
        """Test archetype names are unique."""
        names = [arch.name for arch in ARCHETYPES]
        self.assertEqual(len(names), len(set(names)))

    def test_zodiac_signs(self):
        """Test zodiac sign order."""
        expected_signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        signs = [arch.sign for arch in ARCHETYPES]
        self.assertEqual(signs, expected_signs)

    def test_archetype_structure(self):
        """Test each archetype has required fields."""
        for arch in ARCHETYPES:
            self.assertIsInstance(arch, Archetype)
            self.assertIsInstance(arch.id, int)
            self.assertIsInstance(arch.name, str)
            self.assertIsInstance(arch.sign, str)
            self.assertIsInstance(arch.theme, str)
            self.assertIsInstance(arch.keywords, list)
            self.assertGreater(len(arch.keywords), 0)


class TestRelevanceRouter(unittest.TestCase):
    """Test Relevance Router functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = ComprehensiveLogger(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test router initializes correctly."""
        router = RelevanceRouter(
            current_stage=1,
            logger=self.logger,
            top_k=3
        )

        self.assertEqual(router.current_stage, 1)
        self.assertEqual(router.top_k, 3)
        self.assertEqual(router.total_activations, 0)

    def test_baseline_weights_stage_1(self):
        """Test baseline weights for stage 1."""
        router = RelevanceRouter(current_stage=1, logger=self.logger)
        baseline = router._get_baseline_weights()

        # Stage 1 archetype should have highest weight
        max_idx = baseline.argmax()
        self.assertEqual(max_idx, 0)  # Index 0 = Archetype 1

    def test_baseline_weights_stage_6(self):
        """Test baseline weights for stage 6."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)
        baseline = router._get_baseline_weights()

        # Stage 6 archetype should have highest weight
        max_idx = baseline.argmax()
        self.assertEqual(max_idx, 5)  # Index 5 = Archetype 6

    def test_baseline_weights_sum(self):
        """Test baseline weights sum to 1."""
        for stage in range(1, 13):
            router = RelevanceRouter(current_stage=stage, logger=self.logger)
            baseline = router._get_baseline_weights()
            self.assertAlmostEqual(baseline.sum(), 1.0, places=5)

    def test_dynamic_adjustment_high_uncertainty(self):
        """Test dynamic adjustment for high uncertainty."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)

        features = StateFeatures(
            uncertainty=0.9,  # High uncertainty
            novelty=0.3,
            complexity=0.3,
            time_pressure=0.3,
            irreversibility=0.3,
            stakes=0.3
        )

        dynamic = router._compute_dynamic_adjustment(features)

        # Memory (Cancer) should be boosted for high uncertainty
        memory_idx = 3  # Archetype 4 (Cancer/Memory)
        self.assertGreater(dynamic[memory_idx], 0.05)

    def test_dynamic_adjustment_high_novelty(self):
        """Test dynamic adjustment for high novelty."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)

        features = StateFeatures(
            uncertainty=0.3,
            novelty=0.9,  # High novelty
            complexity=0.3,
            time_pressure=0.3,
            irreversibility=0.3,
            stakes=0.3
        )

        dynamic = router._compute_dynamic_adjustment(features)

        # Innovation (Aquarius) should be boosted for high novelty
        innovation_idx = 10  # Archetype 11 (Aquarius/Innovation)
        self.assertGreater(dynamic[innovation_idx], 0.05)

    def test_activation_returns_correct_structure(self):
        """Test activation returns ActivationResult."""
        router = RelevanceRouter(current_stage=6, logger=self.logger, top_k=3)

        features = StateFeatures(
            uncertainty=0.5,
            novelty=0.5,
            complexity=0.5,
            time_pressure=0.5,
            irreversibility=0.5,
            stakes=0.5
        )

        result = router.activate(features)

        self.assertIsInstance(result, ActivationResult)
        self.assertEqual(len(result.active_modules), 3)
        self.assertEqual(len(result.weights), 12)
        self.assertGreater(result.compute_budget, 0)
        self.assertIsInstance(result.reasoning, str)

    def test_activation_weights_sum_to_one(self):
        """Test final weights sum to 1."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)

        features = StateFeatures(
            uncertainty=0.7,
            novelty=0.4,
            complexity=0.6,
            time_pressure=0.5,
            irreversibility=0.3,
            stakes=0.8
        )

        result = router.activate(features)

        self.assertAlmostEqual(sum(result.weights), 1.0, places=5)

    def test_top_k_selection(self):
        """Test top-k archetype selection."""
        for k in [1, 3, 5]:
            router = RelevanceRouter(current_stage=6, logger=self.logger, top_k=k)

            features = StateFeatures(uncertainty=0.5)
            result = router.activate(features)

            self.assertEqual(len(result.active_modules), k)

    def test_active_modules_are_top_weighted(self):
        """Test that active modules are the highest weighted."""
        router = RelevanceRouter(current_stage=6, logger=self.logger, top_k=3)

        features = StateFeatures(uncertainty=0.5)
        result = router.activate(features)

        # Get indices of top 3 weights
        top_indices = sorted(
            range(len(result.weights)),
            key=lambda i: result.weights[i],
            reverse=True
        )[:3]

        # Active modules should correspond to top weights
        active_names = result.active_modules
        expected_names = [ARCHETYPES[i].name for i in top_indices]

        self.assertEqual(set(active_names), set(expected_names))

    def test_compute_budget_scales_with_complexity(self):
        """Test compute budget increases with complexity."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)

        low_complexity = StateFeatures(complexity=0.2)
        high_complexity = StateFeatures(complexity=0.9)

        result_low = router.activate(low_complexity)
        result_high = router.activate(high_complexity)

        self.assertGreater(result_high.compute_budget, result_low.compute_budget)

    def test_update_stage(self):
        """Test stage update."""
        router = RelevanceRouter(current_stage=1, logger=self.logger)

        router.update_stage(6)
        self.assertEqual(router.current_stage, 6)

        # Baseline weights should change
        baseline = router._get_baseline_weights()
        max_idx = baseline.argmax()
        self.assertEqual(max_idx, 5)

    def test_activation_history_tracking(self):
        """Test activation history is tracked."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)

        features = StateFeatures(uncertainty=0.5)

        # Activate multiple times
        for _ in range(5):
            router.activate(features)

        self.assertEqual(router.total_activations, 5)
        self.assertEqual(len(router.activation_history), 5)

    def test_get_stats(self):
        """Test statistics retrieval."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)

        features = StateFeatures(uncertainty=0.5)

        # Activate multiple times
        for _ in range(10):
            router.activate(features)

        stats = router.get_stats()

        self.assertEqual(stats['current_stage'], 6)
        self.assertEqual(stats['total_activations'], 10)
        self.assertIn('most_activated', stats)
        self.assertIsInstance(stats['most_activated'], list)

    def test_most_activated_tracking(self):
        """Test most activated archetypes are tracked."""
        router = RelevanceRouter(current_stage=6, logger=self.logger, top_k=3)

        features = StateFeatures(uncertainty=0.5)

        # Activate multiple times
        for _ in range(5):
            router.activate(features)

        stats = router.get_stats()
        most_activated = stats['most_activated']

        # Should have entries
        self.assertGreater(len(most_activated), 0)

        # Each entry should have name and count
        for entry in most_activated:
            self.assertIn('name', entry)
            self.assertIn('count', entry)

    def test_memory_adjustment(self):
        """Test memory-based weight adjustment."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)

        memory_signals = {"Analysis": 0.8, "Structure": 0.6}
        adjustment = router._compute_memory_adjustment(memory_signals)

        # Analysis should have higher adjustment
        analysis_idx = 5  # Archetype 6 (Virgo/Analysis)
        self.assertGreater(adjustment[analysis_idx], 0.0)

    def test_different_stages_produce_different_weights(self):
        """Test that different stages produce different weight distributions."""
        features = StateFeatures(uncertainty=0.5)

        weights_by_stage = {}
        for stage in [1, 6, 12]:
            router = RelevanceRouter(current_stage=stage, logger=self.logger)
            result = router.activate(features)
            weights_by_stage[stage] = result.weights

        # Weights should be different across stages
        import numpy as np
        self.assertFalse(np.array_equal(weights_by_stage[1], weights_by_stage[6]))
        self.assertFalse(np.array_equal(weights_by_stage[6], weights_by_stage[12]))

    def test_reasoning_is_generated(self):
        """Test that reasoning is generated."""
        router = RelevanceRouter(current_stage=6, logger=self.logger)

        features = StateFeatures(uncertainty=0.8, complexity=0.7)
        result = router.activate(features)

        self.assertIsInstance(result.reasoning, str)
        self.assertGreater(len(result.reasoning), 0)


if __name__ == '__main__':
    unittest.main()
