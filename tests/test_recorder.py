"""
Test for MouseRecorder functionality.
"""

import unittest
import tempfile
import os
import json
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from recorder import MouseRecorder, MouseAction


class TestMouseRecorder(unittest.TestCase):
    """Test cases for MouseRecorder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recorder = MouseRecorder()
    
    def test_mouse_action_creation(self):
        """Test MouseAction creation and serialization."""
        action = MouseAction(100, 200, "left", 1.5)
        
        self.assertEqual(action.x, 100)
        self.assertEqual(action.y, 200)
        self.assertEqual(action.button, "left")
        self.assertEqual(action.timestamp, 1.5)
        self.assertEqual(action.action_type, "click")
    
    def test_mouse_action_to_dict(self):
        """Test MouseAction to_dict method."""
        action = MouseAction(150, 250, "right", 2.5)
        data = action.to_dict()
        
        expected = {
            "x": 150,
            "y": 250,
            "button": "right",
            "timestamp": 2.5,
            "action_type": "click"
        }
        
        self.assertEqual(data, expected)
    
    def test_mouse_action_from_dict(self):
        """Test MouseAction from_dict method."""
        data = {
            "x": 300,
            "y": 400,
            "button": "middle",
            "timestamp": 3.5,
            "action_type": "click"
        }
        
        action = MouseAction.from_dict(data)
        
        self.assertEqual(action.x, 300)
        self.assertEqual(action.y, 400)
        self.assertEqual(action.button, "middle")
        self.assertEqual(action.timestamp, 3.5)
        self.assertEqual(action.action_type, "click")
    
    def test_recorder_initialization(self):
        """Test recorder initial state."""
        self.assertFalse(self.recorder.is_recording)
        self.assertEqual(len(self.recorder.actions), 0)
        self.assertIsNone(self.recorder.start_time)
    
    def test_add_manual_actions(self):
        """Test adding actions manually."""
        action1 = MouseAction(100, 100, "left", 0.0)
        action2 = MouseAction(200, 200, "right", 1.0)
        
        self.recorder.actions = [action1, action2]
        actions = self.recorder.get_actions()
        
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].x, 100)
        self.assertEqual(actions[1].button, "right")
    
    def test_clear_actions(self):
        """Test clearing actions."""
        action = MouseAction(50, 50, "left", 0.5)
        self.recorder.actions = [action]
        
        self.assertEqual(len(self.recorder.actions), 1)
        
        self.recorder.clear_actions()
        
        self.assertEqual(len(self.recorder.actions), 0)
    
    def test_save_and_load_file(self):
        """Test saving and loading actions to/from file."""
        # Create test actions
        actions = [
            MouseAction(100, 100, "left", 0.0),
            MouseAction(200, 200, "right", 1.0),
            MouseAction(300, 300, "middle", 2.0)
        ]
        self.recorder.actions = actions
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            self.recorder.save_to_file(temp_filename)
            
            # Verify file exists and contains valid JSON
            self.assertTrue(os.path.exists(temp_filename))
            
            with open(temp_filename, 'r') as f:
                data = json.load(f)
            
            self.assertIn('actions', data)
            self.assertIn('metadata', data)
            self.assertEqual(len(data['actions']), 3)
            
            # Load into new recorder
            new_recorder = MouseRecorder()
            new_recorder.load_from_file(temp_filename)
            
            loaded_actions = new_recorder.get_actions()
            self.assertEqual(len(loaded_actions), 3)
            self.assertEqual(loaded_actions[0].x, 100)
            self.assertEqual(loaded_actions[1].button, "right")
            self.assertEqual(loaded_actions[2].timestamp, 2.0)
        
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_remove_duplicate_actions(self):
        """Test removing duplicate actions."""
        # Create actions with some duplicates
        actions = [
            MouseAction(100, 100, "left", 0.0),
            MouseAction(100, 100, "left", 0.05),  # Duplicate (within tolerance)
            MouseAction(200, 200, "left", 1.0),
            MouseAction(200, 200, "left", 1.05),  # Duplicate (within tolerance)
            MouseAction(300, 300, "left", 2.0),
        ]
        self.recorder.actions = actions
        
        removed_count = self.recorder.remove_duplicate_actions(tolerance=0.1)
        
        self.assertEqual(removed_count, 2)
        self.assertEqual(len(self.recorder.actions), 3)
        
        # Check that the remaining actions are the first ones
        remaining = self.recorder.get_actions()
        self.assertEqual(remaining[0].timestamp, 0.0)
        self.assertEqual(remaining[1].timestamp, 1.0)
        self.assertEqual(remaining[2].timestamp, 2.0)
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        # Should not raise exception, just print message
        self.recorder.load_from_file("nonexistent_file.json")
        self.assertEqual(len(self.recorder.actions), 0)
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_filename = f.name
        
        try:
            # Should not raise exception, just print message
            self.recorder.load_from_file(temp_filename)
            self.assertEqual(len(self.recorder.actions), 0)
        
        finally:
            os.unlink(temp_filename)


if __name__ == '__main__':
    unittest.main()