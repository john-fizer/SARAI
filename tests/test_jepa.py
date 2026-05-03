"""
Unit Tests for JEPA World Model
================================

Author: John Fizer
"""

import unittest
import numpy as np
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.append('..')

from sarai.core.world_model.jepa import JEPAWorldModel
from sarai.core.world_model.state import WorldState, StateFeatures
from sarai.safety.logging import ComprehensiveLogger


class TestJEPAWorldModel(unittest.TestCase):
    """Test JEPA World Model functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = ComprehensiveLogger(self.temp_dir)
        self.jepa = JEPAWorldModel(
            embedding_dim=768,
            latent_dim=256,
            logger=self.logger
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test JEPA initializes correctly."""
        self.assertEqual(self.jepa.embedding_dim, 768)
        self.assertEqual(self.jepa.latent_dim, 256)
        self.assertIsNone(self.jepa.current_state)
        self.assertIsNone(self.jepa.predicted_state)
        self.assertEqual(len(self.jepa.state_history), 0)

    def test_encode(self):
        """Test encoding observation to latent state."""
        observation = np.random.randn(768).astype(np.float32)
        latent = self.jepa.encode(observation)

        self.assertEqual(latent.shape, (256,))
        self.assertIsInstance(latent, np.ndarray)

    def test_predict(self):
        """Test predicting next state."""
        state = np.random.randn(256).astype(np.float32)
        predicted = self.jepa.predict(state)

        self.assertEqual(predicted.shape, (256,))
        self.assertIsInstance(predicted, np.ndarray)

    def test_compute_error(self):
        """Test prediction error computation."""
        state1 = np.random.randn(256).astype(np.float32)
        state2 = np.random.randn(256).astype(np.float32)

        error = self.jepa.compute_error(state1, state2)

        self.assertIsInstance(error, float)
        self.assertGreaterEqual(error, 0.0)

    def test_first_update(self):
        """Test first observation update (no prediction yet)."""
        observation = np.random.randn(768).astype(np.float32)
        world_state = self.jepa.update(observation)

        self.assertIsInstance(world_state, WorldState)
        self.assertIsNone(world_state.prediction_error)
        self.assertEqual(world_state.surprise, 0.0)
        self.assertEqual(len(self.jepa.state_history), 1)

    def test_subsequent_updates(self):
        """Test updates after first observation."""
        # First update
        obs1 = np.random.randn(768).astype(np.float32)
        state1 = self.jepa.update(obs1)

        # Second update
        obs2 = np.random.randn(768).astype(np.float32)
        state2 = self.jepa.update(obs2)

        self.assertIsNotNone(state2.prediction_error)
        self.assertGreater(state2.surprise, 0.0)
        self.assertEqual(len(self.jepa.state_history), 2)

    def test_surprise_calculation(self):
        """Test surprise increases with prediction error."""
        obs1 = np.random.randn(768).astype(np.float32)
        self.jepa.update(obs1)

        # Small change (low surprise)
        obs2 = obs1 + np.random.randn(768).astype(np.float32) * 0.1
        state2 = self.jepa.update(obs2)

        # Large change (high surprise)
        obs3 = np.random.randn(768).astype(np.float32) * 5.0
        state3 = self.jepa.update(obs3)

        self.assertLess(state2.surprise, state3.surprise)

    def test_state_features_extraction(self):
        """Test extracting state features."""
        # Add some observations
        for _ in range(5):
            obs = np.random.randn(768).astype(np.float32)
            self.jepa.update(obs)

        features = self.jepa.get_state_features()

        self.assertIsInstance(features, StateFeatures)
        self.assertGreaterEqual(features.uncertainty, 0.0)
        self.assertLessEqual(features.uncertainty, 1.0)
        self.assertGreaterEqual(features.novelty, 0.0)
        self.assertLessEqual(features.novelty, 1.0)
        self.assertGreaterEqual(features.complexity, 0.0)
        self.assertLessEqual(features.complexity, 1.0)

    def test_get_stats(self):
        """Test statistics retrieval."""
        # Add observations
        for _ in range(10):
            obs = np.random.randn(768).astype(np.float32)
            self.jepa.update(obs)

        stats = self.jepa.get_stats()

        self.assertEqual(stats['state_history_length'], 10)
        self.assertIn('avg_prediction_error', stats)
        self.assertIn('avg_surprise', stats)
        self.assertGreater(stats['avg_prediction_error'], 0.0)

    def test_state_history_max_length(self):
        """Test state history doesn't exceed max length."""
        max_len = 100

        # Add more than max_len observations
        for _ in range(150):
            obs = np.random.randn(768).astype(np.float32)
            self.jepa.update(obs)

        self.assertLessEqual(len(self.jepa.state_history), max_len)

    def test_metadata_storage(self):
        """Test metadata is stored with world state."""
        obs = np.random.randn(768).astype(np.float32)
        metadata = {"test_key": "test_value", "number": 42}

        world_state = self.jepa.update(obs, metadata=metadata)

        self.assertEqual(world_state.metadata, metadata)

    def test_save_and_load(self):
        """Test saving and loading JEPA state."""
        # Add some observations
        observations = [np.random.randn(768).astype(np.float32) for _ in range(5)]
        for obs in observations:
            self.jepa.update(obs)

        # Save
        save_path = Path(self.temp_dir) / "jepa_test.pt"
        self.jepa.save(save_path)
        self.assertTrue(save_path.exists())

        # Create new JEPA and load
        jepa2 = JEPAWorldModel(
            embedding_dim=768,
            latent_dim=256,
            logger=self.logger
        )
        jepa2.load(save_path)

        # Verify state is preserved
        self.assertEqual(len(jepa2.state_history), len(self.jepa.state_history))

        # Test that loaded model works
        new_obs = np.random.randn(768).astype(np.float32)
        world_state = jepa2.update(new_obs)
        self.assertIsNotNone(world_state)

    def test_consistency_of_encoding(self):
        """Test that same input produces same encoding."""
        obs = np.random.randn(768).astype(np.float32)

        latent1 = self.jepa.encode(obs)
        latent2 = self.jepa.encode(obs)

        np.testing.assert_array_almost_equal(latent1, latent2)

    def test_prediction_error_is_zero_for_identical_states(self):
        """Test prediction error is zero for identical states."""
        state = np.random.randn(256).astype(np.float32)
        error = self.jepa.compute_error(state, state)

        self.assertAlmostEqual(error, 0.0, places=5)

    def test_latent_state_dimensionality(self):
        """Test latent state has correct dimensionality."""
        obs = np.random.randn(768).astype(np.float32)
        world_state = self.jepa.update(obs)

        self.assertEqual(world_state.latent_state.shape, (256,))
        if world_state.predicted_state is not None:
            self.assertEqual(world_state.predicted_state.shape, (256,))


class TestStateFeatures(unittest.TestCase):
    """Test StateFeatures dataclass."""

    def test_creation(self):
        """Test creating StateFeatures."""
        features = StateFeatures(
            uncertainty=0.5,
            novelty=0.3,
            complexity=0.7,
            time_pressure=0.4,
            irreversibility=0.2,
            stakes=0.6
        )

        self.assertEqual(features.uncertainty, 0.5)
        self.assertEqual(features.novelty, 0.3)
        self.assertEqual(features.complexity, 0.7)
        self.assertEqual(features.time_pressure, 0.4)
        self.assertEqual(features.irreversibility, 0.2)
        self.assertEqual(features.stakes, 0.6)

    def test_defaults(self):
        """Test default values."""
        features = StateFeatures()

        self.assertEqual(features.uncertainty, 0.0)
        self.assertEqual(features.novelty, 0.0)
        self.assertEqual(features.complexity, 0.0)
        self.assertEqual(features.time_pressure, 0.0)
        self.assertEqual(features.irreversibility, 0.0)
        self.assertEqual(features.stakes, 0.0)


if __name__ == '__main__':
    unittest.main()
