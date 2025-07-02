#!/usr/bin/env python3
"""
Unit tests for the CoordinateTransformer module.
"""

import unittest
import math
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from src.recorder import MouseAction
from src.transformer import CoordinateTransformer


class TestCoordinateTransformer(unittest.TestCase):
    """Test the CoordinateTransformer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CoordinateTransformer()
        
        # Create sample actions for testing
        self.sample_actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.5, 'click', 100, 100, 'left', True),
            MouseAction(0.6, 'click', 100, 100, 'left', False),
            MouseAction(1.0, 'move', 200, 200),
            MouseAction(1.5, 'click', 200, 200, 'left', True),
            MouseAction(1.6, 'click', 200, 200, 'left', False)
        ]
    
    def test_translation(self):
        """Test coordinate translation."""
        offset_x, offset_y = 50, 25
        
        translated = self.transformer.translate(self.sample_actions, offset_x, offset_y)
        
        # Check that all coordinates are translated correctly
        for original, translated_action in zip(self.sample_actions, translated):
            self.assertEqual(translated_action.x, original.x + offset_x)
            self.assertEqual(translated_action.y, original.y + offset_y)
            # Other properties should remain unchanged
            self.assertEqual(translated_action.timestamp, original.timestamp)
            self.assertEqual(translated_action.action_type, original.action_type)
            self.assertEqual(translated_action.button, original.button)
    
    def test_scaling(self):
        """Test coordinate scaling."""
        scale_x, scale_y = 2.0, 1.5
        
        scaled = self.transformer.scale(self.sample_actions, scale_x, scale_y)
        
        # Calculate expected center
        bounds = self.transformer._get_action_bounds(self.sample_actions)
        center_x = (bounds['min_x'] + bounds['max_x']) / 2
        center_y = (bounds['min_y'] + bounds['max_y']) / 2
        
        # Check scaling
        for original, scaled_action in zip(self.sample_actions, scaled):
            expected_x = int((original.x - center_x) * scale_x + center_x)
            expected_y = int((original.y - center_y) * scale_y + center_y)
            
            self.assertEqual(scaled_action.x, expected_x)
            self.assertEqual(scaled_action.y, expected_y)
    
    def test_rotation(self):
        """Test coordinate rotation."""
        angle_degrees = 90  # 90 degree rotation
        
        rotated = self.transformer.rotate(self.sample_actions, angle_degrees)
        
        # Calculate expected center
        bounds = self.transformer._get_action_bounds(self.sample_actions)
        center_x = (bounds['min_x'] + bounds['max_x']) / 2
        center_y = (bounds['min_y'] + bounds['max_y']) / 2
        
        # For 90 degree rotation: (x, y) -> (-y, x) relative to center
        angle_radians = math.radians(angle_degrees)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        for original, rotated_action in zip(self.sample_actions, rotated):
            rel_x = original.x - center_x
            rel_y = original.y - center_y
            
            expected_x = int(rel_x * cos_angle - rel_y * sin_angle + center_x)
            expected_y = int(rel_x * sin_angle + rel_y * cos_angle + center_y)
            
            self.assertEqual(rotated_action.x, expected_x)
            self.assertEqual(rotated_action.y, expected_y)
    
    def test_mirror_horizontal(self):
        """Test horizontal mirroring."""
        mirrored = self.transformer.mirror_horizontal(self.sample_actions)
        
        # Calculate mirror axis
        bounds = self.transformer._get_action_bounds(self.sample_actions)
        axis_x = (bounds['min_x'] + bounds['max_x']) / 2
        
        for original, mirrored_action in zip(self.sample_actions, mirrored):
            expected_x = int(2 * axis_x - original.x)
            
            self.assertEqual(mirrored_action.x, expected_x)
            self.assertEqual(mirrored_action.y, original.y)  # Y should remain unchanged
    
    def test_mirror_vertical(self):
        """Test vertical mirroring."""
        mirrored = self.transformer.mirror_vertical(self.sample_actions)
        
        # Calculate mirror axis
        bounds = self.transformer._get_action_bounds(self.sample_actions)
        axis_y = (bounds['min_y'] + bounds['max_y']) / 2
        
        for original, mirrored_action in zip(self.sample_actions, mirrored):
            expected_y = int(2 * axis_y - original.y)
            
            self.assertEqual(mirrored_action.x, original.x)  # X should remain unchanged
            self.assertEqual(mirrored_action.y, expected_y)
    
    def test_get_action_bounds(self):
        """Test bounding box calculation."""
        bounds = self.transformer._get_action_bounds(self.sample_actions)
        
        self.assertEqual(bounds['min_x'], 100)
        self.assertEqual(bounds['max_x'], 200)
        self.assertEqual(bounds['min_y'], 100)
        self.assertEqual(bounds['max_y'], 200)
    
    def test_empty_actions(self):
        """Test transformations with empty action lists."""
        empty_actions = []
        
        # All transformations should return empty lists
        self.assertEqual(len(self.transformer.translate(empty_actions, 10, 20)), 0)
        self.assertEqual(len(self.transformer.scale(empty_actions, 2, 2)), 0)
        self.assertEqual(len(self.transformer.rotate(empty_actions, 45)), 0)
        self.assertEqual(len(self.transformer.mirror_horizontal(empty_actions)), 0)
        self.assertEqual(len(self.transformer.mirror_vertical(empty_actions)), 0)
    
    def test_chain_transforms(self):
        """Test chaining multiple transformations."""
        transforms = [
            {'type': 'translate', 'offset_x': 50, 'offset_y': 25},
            {'type': 'scale', 'scale_x': 1.5, 'scale_y': 1.5},
            {'type': 'rotate', 'angle_degrees': 45}
        ]
        
        chained = self.transformer.chain_transforms(self.sample_actions, transforms)
        
        # Should have same number of actions
        self.assertEqual(len(chained), len(self.sample_actions))
        
        # Verify by applying transformations step by step
        step1 = self.transformer.translate(self.sample_actions, 50, 25)
        step2 = self.transformer.scale(step1, 1.5, 1.5)
        step3 = self.transformer.rotate(step2, 45)
        
        # Results should be the same
        for chained_action, step_action in zip(chained, step3):
            self.assertEqual(chained_action.x, step_action.x)
            self.assertEqual(chained_action.y, step_action.y)
    
    def test_fit_to_screen(self):
        """Test fitting actions to screen bounds."""
        screen_width, screen_height = 800, 600
        
        fitted = self.transformer.fit_to_screen(
            self.sample_actions, screen_width, screen_height, 
            maintain_aspect_ratio=True, margin=10
        )
        
        # Check that all actions fit within screen bounds (with margin)
        for action in fitted:
            self.assertGreaterEqual(action.x, 10)
            self.assertLessEqual(action.x, screen_width - 10)
            self.assertGreaterEqual(action.y, 10)
            self.assertLessEqual(action.y, screen_height - 10)
    
    def test_normalize_timing(self):
        """Test timing normalization."""
        target_duration = 5.0
        
        normalized = self.transformer.normalize_timing(self.sample_actions, target_duration)
        
        # Check that duration matches target
        if len(normalized) > 1:
            actual_duration = normalized[-1].timestamp - normalized[0].timestamp
            self.assertAlmostEqual(actual_duration, target_duration, places=2)
        
        # Check that relative timing is preserved
        if len(normalized) > 2:
            # Check that second action is still at 0.5/1.6 = 31.25% of total time
            relative_time = (normalized[1].timestamp - normalized[0].timestamp) / target_duration
            expected_relative = 0.5 / 1.6  # Original relative position
            self.assertAlmostEqual(relative_time, expected_relative, places=2)
    
    def test_transformation_info(self):
        """Test transformation information calculation."""
        # Apply a known transformation
        transformed = self.transformer.translate(self.sample_actions, 100, 50)
        
        info = self.transformer.get_transformation_info(self.sample_actions, transformed)
        
        # Check center shift
        self.assertAlmostEqual(info['center_shift']['x'], 100, places=1)
        self.assertAlmostEqual(info['center_shift']['y'], 50, places=1)
        
        # Check scale factors (should be 1.0 for translation)
        self.assertAlmostEqual(info['scale_factors']['x'], 1.0, places=2)
        self.assertAlmostEqual(info['scale_factors']['y'], 1.0, places=2)
        
        # Check area ratio (should be 1.0 for translation)
        self.assertAlmostEqual(info['area_ratio'], 1.0, places=2)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "numpy not available")
    def test_matrix_transformation(self):
        """Test custom matrix transformation."""
        # Identity matrix (should not change coordinates)
        identity_matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        
        transformed = self.transformer.apply_matrix_transform(self.sample_actions, identity_matrix)
        
        # Coordinates should remain unchanged
        for original, transformed_action in zip(self.sample_actions, transformed):
            self.assertEqual(original.x, transformed_action.x)
            self.assertEqual(original.y, transformed_action.y)
        
        # Test translation matrix
        translation_matrix = np.array([
            [1, 0, 50],
            [0, 1, 25],
            [0, 0, 1]
        ])
        
        transformed = self.transformer.apply_matrix_transform(self.sample_actions, translation_matrix)
        
        # Should be equivalent to translate(50, 25)
        expected = self.transformer.translate(self.sample_actions, 50, 25)
        for expected_action, transformed_action in zip(expected, transformed):
            self.assertEqual(expected_action.x, transformed_action.x)
            self.assertEqual(expected_action.y, transformed_action.y)
    
    @unittest.skipUnless(NUMPY_AVAILABLE, "numpy not available")
    def test_invalid_matrix(self):
        """Test handling of invalid transformation matrices."""
        # Wrong size matrix
        invalid_matrix = np.array([[1, 0], [0, 1]])
        
        with self.assertRaises(ValueError):
            self.transformer.apply_matrix_transform(self.sample_actions, invalid_matrix)
    
    def test_single_point_actions(self):
        """Test transformations with actions at a single point."""
        single_point_actions = [
            MouseAction(0.0, 'click', 100, 100, 'left', True),
            MouseAction(0.1, 'click', 100, 100, 'left', False)
        ]
        
        # Scaling should work even with single point
        scaled = self.transformer.scale(single_point_actions, 2.0, 2.0)
        self.assertEqual(len(scaled), 2)
        
        # Translation should work
        translated = self.transformer.translate(single_point_actions, 50, 25)
        self.assertEqual(translated[0].x, 150)
        self.assertEqual(translated[0].y, 125)
    
    def test_unknown_transformation_type(self):
        """Test handling of unknown transformation types in chain."""
        transforms = [
            {'type': 'unknown_transform', 'param': 123},
            {'type': 'translate', 'offset_x': 10, 'offset_y': 10}
        ]
        
        # Should skip unknown transformation and apply the valid one
        result = self.transformer.chain_transforms(self.sample_actions, transforms)
        
        # Should be equivalent to just the translation
        expected = self.transformer.translate(self.sample_actions, 10, 10)
        
        for expected_action, result_action in zip(expected, result):
            self.assertEqual(expected_action.x, result_action.x)
            self.assertEqual(expected_action.y, result_action.y)


class TestTransformerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CoordinateTransformer()
    
    def test_zero_scaling(self):
        """Test scaling with zero factors."""
        actions = [MouseAction(0.0, 'move', 100, 100)]
        
        # Zero scaling should work (though result may be unexpected)
        scaled = self.transformer.scale(actions, 0.0, 1.0)
        self.assertEqual(len(scaled), 1)
    
    def test_negative_scaling(self):
        """Test scaling with negative factors."""
        actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(1.0, 'move', 200, 200)
        ]
        
        # Negative scaling should flip coordinates
        scaled = self.transformer.scale(actions, -1.0, -1.0)
        self.assertEqual(len(scaled), 2)
        
        # Should be equivalent to 180-degree rotation around center
        rotated = self.transformer.rotate(actions, 180)
        
        # Results should be very close (within rounding error)
        for scaled_action, rotated_action in zip(scaled, rotated):
            self.assertAlmostEqual(scaled_action.x, rotated_action.x, delta=1)
            self.assertAlmostEqual(scaled_action.y, rotated_action.y, delta=1)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)