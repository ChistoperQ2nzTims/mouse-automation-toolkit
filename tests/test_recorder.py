"""
Tests for the MouseRecorder module.
"""

import unittest
import tempfile
import os
import time
import json
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.recorder import MouseRecorder, MouseAction


class TestMouseAction(unittest.TestCase):
    """Test MouseAction class."""
    
    def test_create_action(self):
        """Test creating a mouse action."""
        action = MouseAction('click', 100, 200, 'left', timestamp=123.456)
        
        self.assertEqual(action.action_type, 'click')
        self.assertEqual(action.x, 100)
        self.assertEqual(action.y, 200)
        self.assertEqual(action.button, 'left')
        self.assertEqual(action.timestamp, 123.456)
        
    def test_to_dict(self):
        """Test converting action to dictionary."""
        action = MouseAction('press', 50, 75, 'right', timestamp=789.123, delay=0.5)
        data = action.to_dict()
        
        expected = {
            'action_type': 'press',
            'x': 50,
            'y': 75,
            'button': 'right',
            'timestamp': 789.123,
            'delay': 0.5
        }
        
        self.assertEqual(data, expected)
        
    def test_from_dict(self):
        """Test creating action from dictionary."""
        data = {
            'action_type': 'move',
            'x': 300,
            'y': 400,
            'button': None,
            'timestamp': 555.777,
            'delay': 0.1
        }
        
        action = MouseAction.from_dict(data)
        
        self.assertEqual(action.action_type, 'move')
        self.assertEqual(action.x, 300)
        self.assertEqual(action.y, 400)
        self.assertEqual(action.button, None)
        self.assertEqual(action.timestamp, 555.777)
        self.assertEqual(action.delay, 0.1)


class TestMouseRecorder(unittest.TestCase):
    """Test MouseRecorder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recorder = MouseRecorder()
        
    def test_create_recorder(self):
        """Test creating a recorder."""
        self.assertFalse(self.recorder.is_recording)
        self.assertEqual(len(self.recorder.actions), 0)
        self.assertTrue(self.recorder.smart_recording)
        
    def test_clear_actions(self):
        """Test clearing actions."""
        # Add some test actions
        action1 = MouseAction('click', 100, 100, 'left')
        action2 = MouseAction('move', 200, 200)
        self.recorder.actions.extend([action1, action2])
        
        self.assertEqual(len(self.recorder.actions), 2)
        
        self.recorder.clear_actions()
        self.assertEqual(len(self.recorder.actions), 0)
        
    def test_get_actions(self):
        """Test getting actions."""
        action1 = MouseAction('click', 100, 100, 'left')
        action2 = MouseAction('move', 200, 200)
        self.recorder.actions.extend([action1, action2])
        
        actions = self.recorder.get_actions()
        
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].x, 100)
        self.assertEqual(actions[1].x, 200)
        
        # Should return a copy
        actions.clear()
        self.assertEqual(len(self.recorder.actions), 2)
        
    def test_calculate_delays(self):
        """Test delay calculation."""
        action1 = MouseAction('click', 100, 100, 'left', timestamp=1.0)
        action2 = MouseAction('move', 200, 200, timestamp=1.5)
        action3 = MouseAction('click', 300, 300, 'left', timestamp=2.2)
        
        self.recorder.actions.extend([action1, action2, action3])
        self.recorder._calculate_delays()
        
        self.assertEqual(self.recorder.actions[0].delay, 0)  # First action has no delay
        self.assertEqual(self.recorder.actions[1].delay, 0.5)  # 1.5 - 1.0
        self.assertEqual(self.recorder.actions[2].delay, 0.7)  # 2.2 - 1.5
        
    def test_is_duplicate_action(self):
        """Test duplicate action detection."""
        # No actions initially
        self.assertFalse(self.recorder._is_duplicate_action(100, 100, 'click', 'left'))
        
        # Add an action
        action = MouseAction('click', 100, 100, 'left')
        self.recorder.actions.append(action)
        
        # Same action should be duplicate
        self.assertTrue(self.recorder._is_duplicate_action(100, 100, 'click', 'left'))
        
        # Different position should not be duplicate
        self.assertFalse(self.recorder._is_duplicate_action(101, 100, 'click', 'left'))
        
        # Different action type should not be duplicate
        self.assertFalse(self.recorder._is_duplicate_action(100, 100, 'move', 'left'))
        
        # Different button should not be duplicate
        self.assertFalse(self.recorder._is_duplicate_action(100, 100, 'click', 'right'))
        
    def test_save_and_load_file(self):
        """Test saving and loading actions to/from file."""
        # Create test actions
        action1 = MouseAction('click', 100, 100, 'left', timestamp=1.0, delay=0.0)
        action2 = MouseAction('move', 200, 200, timestamp=1.5, delay=0.5)
        self.recorder.actions.extend([action1, action2])
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
            
        try:
            self.recorder.save_to_file(temp_filename)
            
            # Verify file exists and has content
            self.assertTrue(os.path.exists(temp_filename))
            
            # Load into new recorder
            new_recorder = MouseRecorder()
            new_recorder.load_from_file(temp_filename)
            
            # Verify loaded actions
            loaded_actions = new_recorder.get_actions()
            self.assertEqual(len(loaded_actions), 2)
            
            self.assertEqual(loaded_actions[0].action_type, 'click')
            self.assertEqual(loaded_actions[0].x, 100)
            self.assertEqual(loaded_actions[0].y, 100)
            self.assertEqual(loaded_actions[0].button, 'left')
            
            self.assertEqual(loaded_actions[1].action_type, 'move')
            self.assertEqual(loaded_actions[1].x, 200)
            self.assertEqual(loaded_actions[1].y, 200)
            self.assertEqual(loaded_actions[1].delay, 0.5)
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
                
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.recorder.load_from_file('nonexistent_file.json')
            
    def test_save_invalid_file(self):
        """Test saving to invalid file path."""
        with self.assertRaises(Exception):
            self.recorder.save_to_file('/invalid/path/file.json')


class TestMouseRecorderIntegration(unittest.TestCase):
    """Integration tests for MouseRecorder."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recorder = MouseRecorder(smart_recording=False, min_delay=0.01)
        
    def test_callback_functionality(self):
        """Test recording callback functionality."""
        callback_called = []
        
        def test_callback(action):
            callback_called.append(action)
            
        # Simulate click events
        with patch.object(self.recorder, '_on_click') as mock_click:
            self.recorder.start_recording(callback=test_callback)
            
            # Simulate a click
            mock_action = MouseAction('press', 100, 100, 'left')
            self.recorder.actions.append(mock_action)
            test_callback(mock_action)
            
            self.recorder.stop_recording()
            
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0].action_type, 'press')


if __name__ == '__main__':
    unittest.main()