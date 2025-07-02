#!/usr/bin/env python3
"""
Unit tests for CoordinateTransformer module

Tests the coordinate transformation functionality including translation,
scaling, rotation, mirroring, and batch operations.
"""

import unittest
import math
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.transformer import CoordinateTransformer
except ImportError:
    print("Warning: Could not import CoordinateTransformer. Some tests may be skipped.")
    CoordinateTransformer = None


class TestCoordinateTransformer(unittest.TestCase):
    """Test cases for CoordinateTransformer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        if CoordinateTransformer is None:
            self.skipTest("CoordinateTransformer not available")
        
        self.transformer = CoordinateTransformer()
        
        # Sample actions for testing
        self.sample_actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 200, 'y': 100, 'button': 'left', 'timestamp': 1.0},
            {'type': 'click', 'x': 200, 'y': 200, 'button': 'right', 'timestamp': 2.0},
            {'type': 'click', 'x': 100, 'y': 200, 'button': 'left', 'timestamp': 3.0},
        ]
    
    def test_initialization(self):
        """Test transformer initialization"""
        self.assertEqual(len(self.transformer.transformation_history), 0)
    
    def test_translate_basic(self):
        """Test basic translation"""
        x, y = self.transformer.translate(100, 200, 50, 30)
        self.assertEqual(x, 150)
        self.assertEqual(y, 230)
    
    def test_translate_negative_offset(self):
        """Test translation with negative offset"""
        x, y = self.transformer.translate(100, 200, -25, -40)
        self.assertEqual(x, 75)
        self.assertEqual(y, 160)
    
    def test_scale_basic(self):
        """Test basic scaling"""
        x, y = self.transformer.scale(100, 200, 2.0, 0.5)
        self.assertEqual(x, 200)
        self.assertEqual(y, 100)
    
    def test_scale_with_origin(self):
        """Test scaling with custom origin"""
        x, y = self.transformer.scale(100, 200, 2.0, 2.0, origin=(50, 50))
        self.assertEqual(x, 150)  # (100-50)*2 + 50 = 150
        self.assertEqual(y, 350)  # (200-50)*2 + 50 = 350
    
    def test_rotate_90_degrees(self):
        """Test 90-degree rotation"""
        x, y = self.transformer.rotate(100, 0, 90)
        self.assertAlmostEqual(x, 0, places=10)
        self.assertAlmostEqual(y, 100, places=10)
    
    def test_rotate_180_degrees(self):
        """Test 180-degree rotation"""
        x, y = self.transformer.rotate(100, 100, 180)
        self.assertAlmostEqual(x, -100, places=10)
        self.assertAlmostEqual(y, -100, places=10)
    
    def test_rotate_with_pivot(self):
        """Test rotation with custom pivot point"""
        x, y = self.transformer.rotate(200, 100, 90, pivot=(100, 100))
        self.assertAlmostEqual(x, 100, places=10)
        self.assertAlmostEqual(y, 200, places=10)
    
    def test_mirror_horizontal(self):
        """Test horizontal mirroring"""
        x, y = self.transformer.mirror(100, 200, 'horizontal', center=(0, 150))
        self.assertEqual(x, 100)  # x unchanged
        self.assertEqual(y, 100)  # 2*150 - 200 = 100
    
    def test_mirror_vertical(self):
        """Test vertical mirroring"""
        x, y = self.transformer.mirror(100, 200, 'vertical', center=(150, 0))
        self.assertEqual(x, 200)  # 2*150 - 100 = 200
        self.assertEqual(y, 200)  # y unchanged
    
    def test_mirror_both(self):
        """Test mirroring both axes"""
        x, y = self.transformer.mirror(100, 200, 'both', center=(150, 150))
        self.assertEqual(x, 200)  # 2*150 - 100 = 200
        self.assertEqual(y, 100)  # 2*150 - 200 = 100
    
    def test_mirror_invalid_axis(self):
        """Test mirroring with invalid axis"""
        with self.assertRaises(ValueError):
            self.transformer.mirror(100, 200, 'invalid')
    
    def test_get_bounding_box_empty(self):
        """Test bounding box calculation with empty actions"""
        bbox = self.transformer.get_bounding_box([])
        expected = {
            'min_x': 0, 'min_y': 0, 'max_x': 0, 'max_y': 0,
            'width': 0, 'height': 0, 'center_x': 0, 'center_y': 0
        }
        self.assertEqual(bbox, expected)
    
    def test_get_bounding_box_with_actions(self):
        """Test bounding box calculation with sample actions"""
        bbox = self.transformer.get_bounding_box(self.sample_actions)
        
        self.assertEqual(bbox['min_x'], 100)
        self.assertEqual(bbox['min_y'], 100)
        self.assertEqual(bbox['max_x'], 200)
        self.assertEqual(bbox['max_y'], 200)
        self.assertEqual(bbox['width'], 100)
        self.assertEqual(bbox['height'], 100)
        self.assertEqual(bbox['center_x'], 150)
        self.assertEqual(bbox['center_y'], 150)
    
    def test_create_transformation_configs(self):
        """Test creation of transformation configurations"""
        # Translation
        trans = self.transformer.create_translation_transform(10, 20)
        self.assertEqual(trans['type'], 'translate')
        self.assertEqual(trans['offset_x'], 10)
        self.assertEqual(trans['offset_y'], 20)
        
        # Scaling
        scale = self.transformer.create_scale_transform(2.0, 1.5, (100, 100))
        self.assertEqual(scale['type'], 'scale')
        self.assertEqual(scale['scale_x'], 2.0)
        self.assertEqual(scale['scale_y'], 1.5)
        self.assertEqual(scale['origin'], (100, 100))
        
        # Rotation
        rotate = self.transformer.create_rotation_transform(45, (50, 50))
        self.assertEqual(rotate['type'], 'rotate')
        self.assertEqual(rotate['angle'], 45)
        self.assertEqual(rotate['pivot'], (50, 50))
        
        # Mirror
        mirror = self.transformer.create_mirror_transform('horizontal', (200, 200))
        self.assertEqual(mirror['type'], 'mirror')
        self.assertEqual(mirror['axis'], 'horizontal')
        self.assertEqual(mirror['center'], (200, 200))
    
    def test_transform_actions_translation(self):
        """Test transforming actions with translation"""
        transformations = [self.transformer.create_translation_transform(50, 30)]
        result = self.transformer.transform_actions(self.sample_actions, transformations)
        
        self.assertEqual(len(result), len(self.sample_actions))
        
        # Check first action
        self.assertEqual(result[0]['x'], 150)  # 100 + 50
        self.assertEqual(result[0]['y'], 130)  # 100 + 30
        self.assertEqual(result[0]['type'], 'click')
        self.assertEqual(result[0]['button'], 'left')
    
    def test_transform_actions_scaling(self):
        """Test transforming actions with scaling"""
        origin = (150, 150)  # Center of bounding box
        transformations = [self.transformer.create_scale_transform(2.0, 0.5, origin)]
        result = self.transformer.transform_actions(self.sample_actions, transformations)
        
        # First action: (100, 100) -> ((100-150)*2 + 150, (100-150)*0.5 + 150) = (50, 125)
        self.assertEqual(result[0]['x'], 50)
        self.assertEqual(result[0]['y'], 125)
    
    def test_transform_actions_chained(self):
        """Test transforming actions with chained transformations"""
        transformations = [
            self.transformer.create_translation_transform(-150, -150),  # Move to origin
            self.transformer.create_scale_transform(2.0, 2.0),         # Scale 2x
            self.transformer.create_rotation_transform(90),            # Rotate 90°
            self.transformer.create_translation_transform(300, 300)    # Move to new position
        ]
        
        result = self.transformer.transform_actions(self.sample_actions, transformations)
        
        # Check that transformation was applied
        self.assertEqual(len(result), len(self.sample_actions))
        self.assertNotEqual(result[0]['x'], self.sample_actions[0]['x'])
        self.assertNotEqual(result[0]['y'], self.sample_actions[0]['y'])
    
    def test_transform_actions_non_click(self):
        """Test transforming actions with non-click actions"""
        actions_with_move = self.sample_actions + [
            {'type': 'move', 'x': 300, 'y': 300, 'timestamp': 4.0}
        ]
        
        transformations = [self.transformer.create_translation_transform(100, 100)]
        result = self.transformer.transform_actions(actions_with_move, transformations)
        
        # Click actions should be transformed
        self.assertEqual(result[0]['x'], 200)  # 100 + 100
        
        # Non-click actions should be unchanged
        self.assertEqual(result[-1]['x'], 300)  # Move action unchanged
        self.assertEqual(result[-1]['type'], 'move')
    
    def test_fit_to_screen(self):
        """Test fitting actions to screen bounds"""
        # Create actions that exceed screen bounds
        large_actions = [
            {'type': 'click', 'x': 0, 'y': 0, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 2000, 'y': 1500, 'button': 'left', 'timestamp': 1.0},
        ]
        
        # Fit to 1920x1080 screen with 50px margin
        result = self.transformer.fit_to_screen(large_actions, 1920, 1080, margin=50)
        
        # Check that all actions are within bounds
        for action in result:
            if action['type'] == 'click':
                self.assertGreaterEqual(action['x'], 50)
                self.assertLessEqual(action['x'], 1870)  # 1920 - 50
                self.assertGreaterEqual(action['y'], 50)
                self.assertLessEqual(action['y'], 1030)  # 1080 - 50
    
    def test_fit_to_screen_no_scaling_needed(self):
        """Test fitting to screen when actions already fit"""
        result = self.transformer.fit_to_screen(self.sample_actions, 1920, 1080, margin=50)
        
        # Actions should be translated but not scaled (they already fit)
        bbox = self.transformer.get_bounding_box(result)
        self.assertGreaterEqual(bbox['min_x'], 50)
        self.assertGreaterEqual(bbox['min_y'], 50)
    
    def test_transformation_history(self):
        """Test transformation history tracking"""
        self.assertEqual(len(self.transformer.get_transformation_history()), 0)
        
        # Apply some transformations
        transformations = [self.transformer.create_translation_transform(10, 20)]
        self.transformer.transform_actions(self.sample_actions, transformations)
        
        history = self.transformer.get_transformation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['transformations'], transformations)
        
        # Apply more transformations
        more_transformations = [self.transformer.create_scale_transform(2.0, 2.0)]
        self.transformer.transform_actions(self.sample_actions, more_transformations)
        
        history = self.transformer.get_transformation_history()
        self.assertEqual(len(history), 2)
    
    def test_clear_transformation_history(self):
        """Test clearing transformation history"""
        # Add some history
        transformations = [self.transformer.create_translation_transform(10, 20)]
        self.transformer.transform_actions(self.sample_actions, transformations)
        
        # Clear history
        self.transformer.clear_transformation_history()
        self.assertEqual(len(self.transformer.get_transformation_history()), 0)
    
    def test_preview_transformation(self):
        """Test transformation preview functionality"""
        transformations = [
            self.transformer.create_translation_transform(100, 50),
            self.transformer.create_scale_transform(1.5, 1.5)
        ]
        
        preview = self.transformer.preview_transformation(self.sample_actions, transformations)
        
        self.assertIn('original_bbox', preview)
        self.assertIn('transformed_bbox', preview)
        self.assertIn('sample_points', preview)
        self.assertIn('total_actions', preview)
        
        # Check that sample points are provided
        self.assertGreater(len(preview['sample_points']), 0)
        self.assertEqual(preview['total_actions'], len(self.sample_actions))
        
        # Check that transformation was actually previewed
        orig_bbox = preview['original_bbox']
        trans_bbox = preview['transformed_bbox']
        self.assertNotEqual(orig_bbox['center_x'], trans_bbox['center_x'])


class TestCoordinateTransformerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for CoordinateTransformer"""
    
    def setUp(self):
        """Set up test fixtures"""
        if CoordinateTransformer is None:
            self.skipTest("CoordinateTransformer not available")
        
        self.transformer = CoordinateTransformer()
    
    def test_zero_scale_factor(self):
        """Test scaling with zero scale factor"""
        x, y = self.transformer.scale(100, 200, 0, 1)
        self.assertEqual(x, 0)
        self.assertEqual(y, 200)
    
    def test_negative_scale_factor(self):
        """Test scaling with negative scale factor"""
        x, y = self.transformer.scale(100, 200, -1, -0.5, origin=(50, 50))
        self.assertEqual(x, 0)    # (100-50)*(-1) + 50 = 0
        self.assertEqual(y, -25)  # (200-50)*(-0.5) + 50 = -25
    
    def test_very_small_rotation(self):
        """Test rotation with very small angle"""
        x, y = self.transformer.rotate(100, 0, 0.001)
        self.assertAlmostEqual(x, 100, places=3)
        self.assertAlmostEqual(y, 0.001745, places=5)  # ~0.001 * pi/180 * 100
    
    def test_large_rotation_angle(self):
        """Test rotation with angle > 360 degrees"""
        # 450° should be equivalent to 90°
        x1, y1 = self.transformer.rotate(100, 0, 450)
        x2, y2 = self.transformer.rotate(100, 0, 90)
        self.assertAlmostEqual(x1, x2, places=10)
        self.assertAlmostEqual(y1, y2, places=10)
    
    def test_empty_actions_list(self):
        """Test transformations with empty actions list"""
        transformations = [self.transformer.create_translation_transform(10, 20)]
        result = self.transformer.transform_actions([], transformations)
        self.assertEqual(len(result), 0)
    
    def test_actions_without_coordinates(self):
        """Test transformations with actions missing coordinates"""
        malformed_actions = [
            {'type': 'other', 'timestamp': 0.0},  # No x, y coordinates
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 1.0}
        ]
        
        transformations = [self.transformer.create_translation_transform(10, 20)]
        result = self.transformer.transform_actions(malformed_actions, transformations)
        
        # Should handle gracefully - first action passed through, second transformed
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'other')
        self.assertEqual(result[1]['x'], 110)  # 100 + 10
    
    def test_unknown_transformation_type(self):
        """Test handling of unknown transformation type"""
        unknown_transform = {'type': 'unknown', 'param': 'value'}
        result = self.transformer.transform_actions(
            [{'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0}],
            [unknown_transform]
        )
        
        # Should handle gracefully and leave coordinates unchanged
        self.assertEqual(result[0]['x'], 100)
        self.assertEqual(result[0]['y'], 100)
    
    def test_precision_preservation(self):
        """Test that coordinate precision is preserved appropriately"""
        # Test with floating point coordinates
        actions = [{'type': 'click', 'x': 100.123, 'y': 200.456, 'button': 'left', 'timestamp': 0.0}]
        
        transformations = [self.transformer.create_translation_transform(0.001, 0.002)]
        result = self.transformer.transform_actions(actions, transformations)
        
        # Result should be rounded to integers as per implementation
        self.assertIsInstance(result[0]['x'], int)
        self.assertIsInstance(result[0]['y'], int)
        self.assertEqual(result[0]['x'], 100)  # 100.124 rounded
        self.assertEqual(result[0]['y'], 200)  # 200.458 rounded


class TestCoordinateTransformerIntegration(unittest.TestCase):
    """Integration tests for CoordinateTransformer"""
    
    def setUp(self):
        """Set up test fixtures"""
        if CoordinateTransformer is None:
            self.skipTest("CoordinateTransformer not available")
        
        self.transformer = CoordinateTransformer()
    
    def test_complex_pattern_transformation(self):
        """Test transforming a complex pattern of actions"""
        # Create a circular pattern
        center_x, center_y = 300, 300
        radius = 50
        actions = []
        
        for i in range(8):
            angle = i * (360 / 8)
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            
            actions.append({
                'type': 'click',
                'x': int(x),
                'y': int(y),
                'button': 'left',
                'timestamp': i * 0.5
            })
        
        # Apply complex transformation
        transformations = [
            self.transformer.create_translation_transform(-center_x, -center_y),  # Center on origin
            self.transformer.create_scale_transform(2.0, 2.0),                   # Scale up
            self.transformer.create_rotation_transform(45),                      # Rotate
            self.transformer.create_translation_transform(400, 400)              # Move to new position
        ]
        
        result = self.transformer.transform_actions(actions, transformations)
        
        # Verify transformation was applied
        self.assertEqual(len(result), len(actions))
        
        # Check that points are now around (400, 400) with larger radius
        result_bbox = self.transformer.get_bounding_box(result)
        self.assertAlmostEqual(result_bbox['center_x'], 400, places=0)
        self.assertAlmostEqual(result_bbox['center_y'], 400, places=0)
        self.assertGreater(result_bbox['width'], 100)  # Should be larger than original
    
    def test_reversible_transformations(self):
        """Test that certain transformations can be reversed"""
        original_actions = [
            {'type': 'click', 'x': 100, 'y': 200, 'button': 'left', 'timestamp': 0.0}
        ]
        
        # Apply transformation
        forward_transform = [self.transformer.create_translation_transform(50, 30)]
        transformed = self.transformer.transform_actions(original_actions, forward_transform)
        
        # Apply reverse transformation
        reverse_transform = [self.transformer.create_translation_transform(-50, -30)]
        restored = self.transformer.transform_actions(transformed, reverse_transform)
        
        # Should be back to original (within rounding)
        self.assertEqual(restored[0]['x'], original_actions[0]['x'])
        self.assertEqual(restored[0]['y'], original_actions[0]['y'])
    
    def test_transformation_order_matters(self):
        """Test that transformation order affects results"""
        actions = [{'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0}]
        
        # Order 1: Translate then scale
        transforms1 = [
            self.transformer.create_translation_transform(100, 100),  # Move to (200, 200)
            self.transformer.create_scale_transform(2.0, 2.0)        # Scale around origin
        ]
        result1 = self.transformer.transform_actions(actions, transforms1)
        
        # Order 2: Scale then translate
        transforms2 = [
            self.transformer.create_scale_transform(2.0, 2.0),       # Scale around origin
            self.transformer.create_translation_transform(100, 100)  # Then move
        ]
        result2 = self.transformer.transform_actions(actions, transforms2)
        
        # Results should be different
        self.assertNotEqual(result1[0]['x'], result2[0]['x'])
        self.assertNotEqual(result1[0]['y'], result2[0]['y'])


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCoordinateTransformer))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCoordinateTransformerEdgeCases))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCoordinateTransformerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)