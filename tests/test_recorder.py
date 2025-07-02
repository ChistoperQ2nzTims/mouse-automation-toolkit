#!/usr/bin/env python3
"""
Unit tests for the MouseRecorder module.
"""

import unittest
import tempfile
import os
import json
import time
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recorder import MouseRecorder, MouseAction


class TestMouseAction(unittest.TestCase):
    """Test the MouseAction dataclass."""
    
    def test_mouse_action_creation(self):
        """Test creating a MouseAction."""
        action = MouseAction(
            timestamp=1.0,
            action_type='click',
            x=100,
            y=200,
            button='left',
            pressed=True
        )
        
        self.assertEqual(action.timestamp, 1.0)
        self.assertEqual(action.action_type, 'click')
        self.assertEqual(action.x, 100)
        self.assertEqual(action.y, 200)
        self.assertEqual(action.button, 'left')
        self.assertTrue(action.pressed)
    
    def test_mouse_action_defaults(self):
        """Test MouseAction with default values."""
        action = MouseAction(
            timestamp=2.0,
            action_type='move',
            x=50,
            y=75
        )
        
        self.assertEqual(action.timestamp, 2.0)
        self.assertEqual(action.action_type, 'move')
        self.assertEqual(action.x, 50)
        self.assertEqual(action.y, 75)
        self.assertIsNone(action.button)
        self.assertIsNone(action.pressed)


class TestMouseRecorder(unittest.TestCase):
    """Test the MouseRecorder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recorder = MouseRecorder()
    
    def tearDown(self):
        """Clean up after tests."""
        self.recorder.cleanup()
    
    def test_recorder_initialization(self):
        """Test recorder initialization."""
        self.assertFalse(self.recorder.is_recording)
        self.assertEqual(len(self.recorder.actions), 0)
        self.assertIsNone(self.recorder.start_time)
    
    def test_start_stop_recording(self):
        """Test basic start/stop recording functionality."""
        # Start recording
        self.recorder.start_recording()
        self.assertTrue(self.recorder.is_recording)
        self.assertIsNotNone(self.recorder.start_time)
        
        # Stop recording
        actions = self.recorder.stop_recording()
        self.assertFalse(self.recorder.is_recording)
        self.assertIsInstance(actions, list)
    
    def test_recording_stats(self):
        """Test recording statistics."""
        # Add some sample actions
        self.recorder.actions = [
            MouseAction(0.0, 'click', 100, 100, 'left', True),
            MouseAction(0.1, 'click', 100, 100, 'left', False),
            MouseAction(0.5, 'move', 200, 200),
            MouseAction(1.0, 'scroll', 200, 200, scroll_direction='up', scroll_amount=3)
        ]
        
        stats = self.recorder.get_recording_stats()
        
        self.assertEqual(stats['action_count'], 4)
        self.assertEqual(stats['click_count'], 2)
        self.assertEqual(stats['move_count'], 1)
        self.assertEqual(stats['scroll_count'], 1)
        self.assertEqual(stats['duration'], 1.0)
    
    def test_save_load_actions(self):
        """Test saving and loading actions to/from file."""
        # Create sample actions
        actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.5, 'click', 100, 100, 'left', True),
            MouseAction(0.6, 'click', 100, 100, 'left', False)
        ]
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            self.recorder.save_to_file(temp_filename, actions)
            
            # Verify file exists and has content
            self.assertTrue(os.path.exists(temp_filename))
            
            # Load actions back
            loaded_actions = self.recorder.load_from_file(temp_filename)
            
            # Verify loaded actions match original
            self.assertEqual(len(loaded_actions), len(actions))
            
            for original, loaded in zip(actions, loaded_actions):
                self.assertEqual(original.timestamp, loaded.timestamp)
                self.assertEqual(original.action_type, loaded.action_type)
                self.assertEqual(original.x, loaded.x)
                self.assertEqual(original.y, loaded.y)
                self.assertEqual(original.button, loaded.button)
                self.assertEqual(original.pressed, loaded.pressed)
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_remove_duplicate_actions(self):
        """Test duplicate action removal."""
        actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.1, 'move', 100, 100),  # Duplicate move
            MouseAction(0.2, 'move', 200, 200),
            MouseAction(0.3, 'click', 200, 200, 'left', True),
            MouseAction(0.4, 'click', 200, 200, 'left', False)
        ]
        
        filtered = self.recorder._remove_duplicate_actions(actions)
        
        # Should remove the duplicate move action
        self.assertEqual(len(filtered), 4)
        self.assertEqual(filtered[0].x, 100)
        self.assertEqual(filtered[1].x, 200)  # Second move should be kept
    
    def test_empty_actions_save_load(self):
        """Test handling of empty actions list."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            # Test saving empty list
            self.recorder.save_to_file(temp_filename, [])
            
            # Should create file but indicate no actions
            self.assertTrue(os.path.exists(temp_filename))
            
            # Test loading empty file
            loaded = self.recorder.load_from_file(temp_filename)
            self.assertEqual(len(loaded), 0)
        
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_invalid_file_handling(self):
        """Test handling of invalid files."""
        # Test loading non-existent file
        with self.assertRaises(FileNotFoundError):
            self.recorder.load_from_file("non_existent_file.json")
        
        # Test loading invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_filename = f.name
        
        try:
            with self.assertRaises(json.JSONDecodeError):
                self.recorder.load_from_file(temp_filename)
        finally:
            os.unlink(temp_filename)
    
    @patch('time.time')
    def test_timing_calculation(self, mock_time):
        """Test timestamp calculation during recording."""
        # Mock time progression
        mock_time.side_effect = [1000.0, 1000.5, 1001.0]  # start_time, first_action, second_action
        
        self.recorder.start_recording()
        
        # Simulate mouse actions
        self.recorder._on_click(100, 200, Mock(name='left'), True)
        self.recorder._on_move(150, 250)
        
        actions = self.recorder.stop_recording()
        
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].timestamp, 0.5)  # 1000.5 - 1000.0
        self.assertEqual(actions[1].timestamp, 1.0)  # 1001.0 - 1000.0


class TestRecorderIntegration(unittest.TestCase):
    """Integration tests for the recorder."""
    
    def test_full_workflow(self):
        """Test a complete record-save-load-replay workflow."""
        recorder = MouseRecorder()
        
        try:
            # Create sample actions
            sample_actions = [
                MouseAction(0.0, 'move', 100, 100),
                MouseAction(0.5, 'click', 100, 100, 'left', True),
                MouseAction(0.6, 'click', 100, 100, 'left', False),
                MouseAction(1.0, 'move', 200, 200),
                MouseAction(1.5, 'scroll', 200, 200, scroll_direction='up', scroll_amount=3)
            ]
            
            # Save to file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_filename = f.name
            
            recorder.save_to_file(temp_filename, sample_actions)
            
            # Load from file
            loaded_actions = recorder.load_from_file(temp_filename)
            
            # Verify integrity
            self.assertEqual(len(loaded_actions), len(sample_actions))
            
            # Check statistics
            stats = recorder.get_recording_stats()
            self.assertEqual(stats['action_count'], 0)  # No actions in recorder itself
            
            # Manually set actions for stats test
            recorder.actions = loaded_actions
            stats = recorder.get_recording_stats()
            self.assertEqual(stats['action_count'], 5)
            self.assertEqual(stats['click_count'], 2)
            self.assertEqual(stats['move_count'], 2)
            self.assertEqual(stats['scroll_count'], 1)
            
            # Clean up
            os.unlink(temp_filename)
            
        finally:
            recorder.cleanup()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)