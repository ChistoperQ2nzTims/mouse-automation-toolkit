"""
Test for CoordinateTransformer functionality.
"""

import unittest
import math
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from recorder import MouseAction
from transformer import CoordinateTransformer


class TestCoordinateTransformer(unittest.TestCase):
    """Test cases for CoordinateTransformer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CoordinateTransformer()
        
        # Create test actions forming a square
        self.test_actions = [
            MouseAction(100, 100, "left", 0.0),
            MouseAction(200, 100, "left", 1.0),
            MouseAction(200, 200, "left", 2.0),
            MouseAction(100, 200, "left", 3.0),
        ]
    
    def test_translate(self):
        """Test translation transformation."""
        offset_x, offset_y = 50, 75
        translated = self.transformer.translate(self.test_actions, offset_x, offset_y)
        
        self.assertEqual(len(translated), len(self.test_actions))
        
        for i, action in enumerate(translated):
            expected_x = self.test_actions[i].x + offset_x
            expected_y = self.test_actions[i].y + offset_y
            
            self.assertEqual(action.x, expected_x)
            self.assertEqual(action.y, expected_y)
            self.assertEqual(action.button, self.test_actions[i].button)
            self.assertEqual(action.timestamp, self.test_actions[i].timestamp)
    
    def test_scale(self):
        """Test scaling transformation."""
        scale_x, scale_y = 2.0, 1.5
        center_x, center_y = 150, 150
        
        scaled = self.transformer.scale(self.test_actions, scale_x, scale_y, center_x, center_y)
        
        self.assertEqual(len(scaled), len(self.test_actions))
        
        # Check first point (100, 100)
        # Relative to center: (-50, -50)
        # Scaled: (-100, -75)
        # Back to absolute: (50, 75)
        self.assertEqual(scaled[0].x, 50)
        self.assertEqual(scaled[0].y, 75)
        
        # Check second point (200, 100)
        # Relative to center: (50, -50)
        # Scaled: (100, -75)
        # Back to absolute: (250, 75)
        self.assertEqual(scaled[1].x, 250)
        self.assertEqual(scaled[1].y, 75)
    
    def test_rotate(self):
        """Test rotation transformation."""
        angle = 90  # 90 degrees clockwise
        center_x, center_y = 150, 150
        
        rotated = self.transformer.rotate(self.test_actions, angle, center_x, center_y)
        
        self.assertEqual(len(rotated), len(self.test_actions))
        
        # For 90-degree rotation: (x, y) -> (y, -x) relative to center
        # Point (100, 100) relative to (150, 150) is (-50, -50)
        # Rotated: (-50, 50)
        # Back to absolute: (100, 200)
        self.assertEqual(rotated[0].x, 100)
        self.assertEqual(rotated[0].y, 200)
    
    def test_mirror_horizontal(self):
        """Test horizontal mirroring."""
        axis_x = 150
        
        mirrored = self.transformer.mirror_horizontal(self.test_actions, axis_x)
        
        self.assertEqual(len(mirrored), len(self.test_actions))
        
        # Point (100, 100) mirrored around x=150 becomes (200, 100)
        self.assertEqual(mirrored[0].x, 200)
        self.assertEqual(mirrored[0].y, 100)
        
        # Point (200, 100) mirrored around x=150 becomes (100, 100)
        self.assertEqual(mirrored[1].x, 100)
        self.assertEqual(mirrored[1].y, 100)
    
    def test_mirror_vertical(self):
        """Test vertical mirroring."""
        axis_y = 150
        
        mirrored = self.transformer.mirror_vertical(self.test_actions, axis_y)
        
        self.assertEqual(len(mirrored), len(self.test_actions))
        
        # Point (100, 100) mirrored around y=150 becomes (100, 200)
        self.assertEqual(mirrored[0].x, 100)
        self.assertEqual(mirrored[0].y, 200)
        
        # Point (100, 200) mirrored around y=150 becomes (100, 100)
        self.assertEqual(mirrored[3].x, 100)
        self.assertEqual(mirrored[3].y, 100)
    
    def test_get_bounding_box(self):
        """Test bounding box calculation."""
        min_x, min_y, max_x, max_y = self.transformer.get_bounding_box(self.test_actions)
        
        self.assertEqual(min_x, 100)
        self.assertEqual(min_y, 100)
        self.assertEqual(max_x, 200)
        self.assertEqual(max_y, 200)
    
    def test_get_center_point(self):
        """Test center point calculation."""
        center_x, center_y = self.transformer.get_center_point(self.test_actions)
        
        self.assertEqual(center_x, 150)  # (100 + 200) / 2
        self.assertEqual(center_y, 150)  # (100 + 200) / 2
    
    def test_bounding_box_empty_actions(self):
        """Test bounding box with empty actions list."""
        min_x, min_y, max_x, max_y = self.transformer.get_bounding_box([])
        
        self.assertEqual((min_x, min_y, max_x, max_y), (0, 0, 0, 0))
    
    def test_center_point_empty_actions(self):
        """Test center point with empty actions list."""
        center_x, center_y = self.transformer.get_center_point([])
        
        self.assertEqual((center_x, center_y), (0, 0))
    
    def test_fit_to_screen(self):
        """Test fit to screen transformation."""
        screen_width, screen_height = 800, 600
        margin = 50
        
        fitted = self.transformer.fit_to_screen(self.test_actions, screen_width, screen_height, margin)
        
        self.assertEqual(len(fitted), len(self.test_actions))
        
        # Check that all points are within screen bounds with margin
        for action in fitted:
            self.assertGreaterEqual(action.x, margin)
            self.assertGreaterEqual(action.y, margin)
            self.assertLessEqual(action.x, screen_width - margin)
            self.assertLessEqual(action.y, screen_height - margin)
    
    def test_fit_to_screen_empty_actions(self):
        """Test fit to screen with empty actions."""
        fitted = self.transformer.fit_to_screen([], 800, 600)
        self.assertEqual(len(fitted), 0)
    
    def test_transformation_chain(self):
        """Test applying a chain of transformations."""
        transformations = [
            {"type": "translate", "params": {"offset_x": 100, "offset_y": 50}},
            {"type": "scale", "params": {"scale_x": 2.0, "scale_y": 2.0, "center_x": 250, "center_y": 200}},
            {"type": "rotate", "params": {"angle": 45, "center_x": 250, "center_y": 200}},
        ]
        
        result = self.transformer.apply_transformation_chain(self.test_actions, transformations)
        
        self.assertEqual(len(result), len(self.test_actions))
        
        # The result should be different from original
        self.assertNotEqual(result[0].x, self.test_actions[0].x)
        self.assertNotEqual(result[0].y, self.test_actions[0].y)
    
    def test_transformation_chain_unknown_type(self):
        """Test transformation chain with unknown transformation type."""
        transformations = [
            {"type": "unknown_transform", "params": {"some_param": 123}},
            {"type": "translate", "params": {"offset_x": 10, "offset_y": 20}},
        ]
        
        result = self.transformer.apply_transformation_chain(self.test_actions, transformations)
        
        # Should still apply the known transformation
        self.assertEqual(len(result), len(self.test_actions))
        self.assertEqual(result[0].x, self.test_actions[0].x + 10)
        self.assertEqual(result[0].y, self.test_actions[0].y + 20)
    
    def test_transformation_preserves_metadata(self):
        """Test that transformations preserve action metadata."""
        translated = self.transformer.translate(self.test_actions, 10, 20)
        
        for i, action in enumerate(translated):
            self.assertEqual(action.button, self.test_actions[i].button)
            self.assertEqual(action.timestamp, self.test_actions[i].timestamp)
            self.assertEqual(action.action_type, self.test_actions[i].action_type)
    
    def test_rotation_90_degrees(self):
        """Test 90-degree rotation with specific expected values."""
        # Single point for precise testing
        actions = [MouseAction(100, 50, "left", 0.0)]
        center_x, center_y = 50, 50
        
        rotated = self.transformer.rotate(actions, 90, center_x, center_y)
        
        # Point (100, 50) relative to (50, 50) is (50, 0)
        # After 90-degree rotation: (0, -50)
        # Back to absolute: (50, 0)
        self.assertEqual(rotated[0].x, 50)
        self.assertEqual(rotated[0].y, 0)
    
    def test_scaling_with_zero_dimensions(self):
        """Test scaling when actions have zero width or height."""
        # All actions at same x coordinate
        actions = [
            MouseAction(100, 100, "left", 0.0),
            MouseAction(100, 200, "left", 1.0),
        ]
        
        scaled = self.transformer.scale(actions, 2.0, 2.0, 100, 150)
        
        # Should still work, just scale the y dimension
        self.assertEqual(len(scaled), 2)
        self.assertEqual(scaled[0].x, 100)  # No change in x
        self.assertEqual(scaled[0].y, 50)   # Scaled y


if __name__ == '__main__':
    unittest.main()