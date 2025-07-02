"""
Tests for the CoordinateTransformer module.
"""

import unittest
import math
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.recorder import MouseAction
from src.transformer import CoordinateTransformer


class TestCoordinateTransformer(unittest.TestCase):
    """Test CoordinateTransformer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CoordinateTransformer()
        self.transformer.set_screen_dimensions(1000, 800)
        
        # Create test actions
        self.test_actions = [
            MouseAction('click', 100, 100, 'left', delay=0.1),
            MouseAction('move', 200, 150, delay=0.2),
            MouseAction('click', 300, 200, 'right', delay=0.3)
        ]
        
    def test_set_screen_dimensions(self):
        """Test setting screen dimensions."""
        self.transformer.set_screen_dimensions(1920, 1080)
        self.assertEqual(self.transformer.screen_width, 1920)
        self.assertEqual(self.transformer.screen_height, 1080)
        
    def test_translate(self):
        """Test coordinate translation."""
        offset_x, offset_y = 50, -30
        translated = self.transformer.translate(self.test_actions, offset_x, offset_y)
        
        self.assertEqual(len(translated), len(self.test_actions))
        
        # Check coordinates
        self.assertEqual(translated[0].x, 100 + offset_x)  # 150
        self.assertEqual(translated[0].y, 100 + offset_y)  # 70
        self.assertEqual(translated[1].x, 200 + offset_x)  # 250
        self.assertEqual(translated[1].y, 150 + offset_y)  # 120
        self.assertEqual(translated[2].x, 300 + offset_x)  # 350
        self.assertEqual(translated[2].y, 200 + offset_y)  # 170
        
        # Check other properties preserved
        self.assertEqual(translated[0].action_type, 'click')
        self.assertEqual(translated[0].button, 'left')
        self.assertEqual(translated[1].action_type, 'move')
        self.assertEqual(translated[2].button, 'right')
        
    def test_scale(self):
        """Test coordinate scaling."""
        scale_x, scale_y = 2.0, 1.5
        center_x, center_y = 0, 0  # Scale from origin
        
        scaled = self.transformer.scale(self.test_actions, scale_x, scale_y, center_x, center_y)
        
        self.assertEqual(len(scaled), len(self.test_actions))
        
        # Check scaled coordinates
        self.assertEqual(scaled[0].x, int(100 * scale_x))  # 200
        self.assertEqual(scaled[0].y, int(100 * scale_y))  # 150
        self.assertEqual(scaled[1].x, int(200 * scale_x))  # 400
        self.assertEqual(scaled[1].y, int(150 * scale_y))  # 225
        
    def test_scale_with_center(self):
        """Test scaling with custom center point."""
        scale_x, scale_y = 2.0, 2.0
        center_x, center_y = 200, 150
        
        scaled = self.transformer.scale(self.test_actions, scale_x, scale_y, center_x, center_y)
        
        # First action: (100, 100) with center (200, 150)
        # Relative to center: (-100, -50)
        # Scaled: (-200, -100)
        # Back to absolute: (0, 50)
        self.assertEqual(scaled[0].x, 0)
        self.assertEqual(scaled[0].y, 50)
        
    def test_rotate(self):
        """Test coordinate rotation."""
        # Rotate 90 degrees around origin
        angle = 90
        center_x, center_y = 0, 0
        
        rotated = self.transformer.rotate(self.test_actions, angle, center_x, center_y)
        
        self.assertEqual(len(rotated), len(self.test_actions))
        
        # After 90-degree rotation: (x, y) -> (-y, x)
        # (100, 100) -> (-100, 100)
        self.assertEqual(rotated[0].x, -100)
        self.assertEqual(rotated[0].y, 100)
        
        # (200, 150) -> (-150, 200)
        self.assertEqual(rotated[1].x, -150)
        self.assertEqual(rotated[1].y, 200)
        
    def test_rotate_45_degrees(self):
        """Test 45-degree rotation for more precise testing."""
        angle = 45
        center_x, center_y = 0, 0
        
        rotated = self.transformer.rotate(self.test_actions, angle, center_x, center_y)
        
        # For (100, 100) rotated 45 degrees around origin:
        # x' = 100*cos(45°) - 100*sin(45°) = 100*(√2/2) - 100*(√2/2) = 0
        # y' = 100*sin(45°) + 100*cos(45°) = 100*(√2/2) + 100*(√2/2) = 100*√2 ≈ 141.42
        
        expected_x = int(100 * math.cos(math.radians(45)) - 100 * math.sin(math.radians(45)))
        expected_y = int(100 * math.sin(math.radians(45)) + 100 * math.cos(math.radians(45)))
        
        self.assertEqual(rotated[0].x, expected_x)
        self.assertEqual(rotated[0].y, expected_y)
        
    def test_mirror_horizontal(self):
        """Test horizontal mirroring."""
        mirrored = self.transformer.mirror_horizontal(self.test_actions)
        
        self.assertEqual(len(mirrored), len(self.test_actions))
        
        # Horizontal mirror: x' = screen_width - x
        self.assertEqual(mirrored[0].x, 1000 - 100)  # 900
        self.assertEqual(mirrored[0].y, 100)  # y unchanged
        self.assertEqual(mirrored[1].x, 1000 - 200)  # 800
        self.assertEqual(mirrored[1].y, 150)  # y unchanged
        
    def test_mirror_vertical(self):
        """Test vertical mirroring."""
        mirrored = self.transformer.mirror_vertical(self.test_actions)
        
        self.assertEqual(len(mirrored), len(self.test_actions))
        
        # Vertical mirror: y' = screen_height - y
        self.assertEqual(mirrored[0].x, 100)  # x unchanged
        self.assertEqual(mirrored[0].y, 800 - 100)  # 700
        self.assertEqual(mirrored[1].x, 200)  # x unchanged
        self.assertEqual(mirrored[1].y, 800 - 150)  # 650
        
    def test_get_bounds(self):
        """Test getting bounding box of actions."""
        min_x, min_y, max_x, max_y = self.transformer.get_bounds(self.test_actions)
        
        self.assertEqual(min_x, 100)
        self.assertEqual(min_y, 100)
        self.assertEqual(max_x, 300)
        self.assertEqual(max_y, 200)
        
    def test_get_bounds_empty(self):
        """Test getting bounds of empty action list."""
        bounds = self.transformer.get_bounds([])
        self.assertEqual(bounds, (0, 0, 0, 0))
        
    def test_normalize_to_bounds(self):
        """Test normalizing actions to target bounds."""
        target_width, target_height = 400, 300
        
        normalized = self.transformer.normalize_to_bounds(self.test_actions, target_width, target_height)
        
        # Check that normalized actions fit within target bounds
        norm_min_x, norm_min_y, norm_max_x, norm_max_y = self.transformer.get_bounds(normalized)
        
        # Should be centered and scaled to fit
        self.assertLessEqual(norm_max_x - norm_min_x, target_width)
        self.assertLessEqual(norm_max_y - norm_min_y, target_height)
        
    def test_chain_transforms(self):
        """Test chaining multiple transformations."""
        transforms = [
            ('translate', {'offset_x': 50, 'offset_y': 50}),
            ('scale', {'scale_x': 2.0, 'scale_y': 2.0}),
            ('translate', {'offset_x': -100, 'offset_y': -100})
        ]
        
        result = self.transformer.chain_transforms(self.test_actions, transforms)
        
        # Apply transforms manually to verify
        step1 = self.transformer.translate(self.test_actions, 50, 50)
        step2 = self.transformer.scale(step1, 2.0, 2.0)
        step3 = self.transformer.translate(step2, -100, -100)
        
        self.assertEqual(len(result), len(step3))
        
        for i in range(len(result)):
            self.assertEqual(result[i].x, step3[i].x)
            self.assertEqual(result[i].y, step3[i].y)
            
    def test_chain_transforms_unknown(self):
        """Test chaining with unknown transform."""
        transforms = [
            ('translate', {'offset_x': 10, 'offset_y': 10}),
            ('unknown_transform', {'param': 'value'}),
            ('scale', {'scale_x': 1.5, 'scale_y': 1.5})
        ]
        
        # Should not raise exception, just skip unknown transform
        result = self.transformer.chain_transforms(self.test_actions, transforms)
        
        # Should have applied translate and scale
        self.assertEqual(len(result), len(self.test_actions))
        
    def test_apply_matrix_transform(self):
        """Test applying custom transformation matrix."""
        # Identity matrix (no change)
        identity_matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        
        result = self.transformer.apply_matrix_transform(self.test_actions, identity_matrix)
        
        self.assertEqual(len(result), len(self.test_actions))
        
        for i in range(len(result)):
            self.assertEqual(result[i].x, self.test_actions[i].x)
            self.assertEqual(result[i].y, self.test_actions[i].y)
            
    def test_apply_matrix_transform_translation(self):
        """Test matrix transformation with translation."""
        # Translation matrix: translate by (10, 20)
        translation_matrix = np.array([
            [1, 0, 10],
            [0, 1, 20],
            [0, 0, 1]
        ])
        
        result = self.transformer.apply_matrix_transform(self.test_actions, translation_matrix)
        
        self.assertEqual(result[0].x, 100 + 10)  # 110
        self.assertEqual(result[0].y, 100 + 20)  # 120
        
    def test_apply_matrix_transform_invalid_size(self):
        """Test matrix transformation with invalid matrix size."""
        invalid_matrix = np.array([
            [1, 0],
            [0, 1]
        ])
        
        with self.assertRaises(ValueError):
            self.transformer.apply_matrix_transform(self.test_actions, invalid_matrix)
            
    def test_preserve_action_properties(self):
        """Test that transformations preserve non-coordinate properties."""
        translated = self.transformer.translate(self.test_actions, 10, 10)
        
        for i in range(len(translated)):
            original = self.test_actions[i]
            transformed = translated[i]
            
            # Coordinates should change
            self.assertNotEqual(transformed.x, original.x)
            self.assertNotEqual(transformed.y, original.y)
            
            # Other properties should be preserved
            self.assertEqual(transformed.action_type, original.action_type)
            self.assertEqual(transformed.button, original.button)
            self.assertEqual(transformed.timestamp, original.timestamp)
            self.assertEqual(transformed.delay, original.delay)


if __name__ == '__main__':
    unittest.main()