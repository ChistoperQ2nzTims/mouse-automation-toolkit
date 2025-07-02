#!/usr/bin/env python3
"""
Unit tests for MouseRecorder module

Tests the mouse action recording functionality including action recording,
file operations, and data validation.
"""

import unittest
import json
import tempfile
import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.recorder import MouseRecorder
except ImportError:
    print("Warning: Could not import MouseRecorder. Some tests may be skipped.")
    MouseRecorder = None


class TestMouseRecorder(unittest.TestCase):
    """Test cases for MouseRecorder class"""
    
    def setUp(self):
        """Set up test fixtures"""
        if MouseRecorder is None:
            self.skipTest("MouseRecorder not available")
        
        self.recorder = MouseRecorder()
        self.temp_file = None
    
    def tearDown(self):
        """Clean up after tests"""
        if self.temp_file and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)
    
    def test_initialization(self):
        """Test recorder initialization"""
        self.assertFalse(self.recorder.is_recording)
        self.assertEqual(len(self.recorder.actions), 0)
        self.assertIsNone(self.recorder.listener)
        self.assertIsNone(self.recorder.start_time)
        self.assertEqual(self.recorder.debounce_threshold, 0.1)
    
    def test_action_callback_setting(self):
        """Test setting action callback"""
        callback = Mock()
        self.recorder.set_action_callback(callback)
        self.assertEqual(self.recorder.on_action_callback, callback)
    
    def test_get_actions_empty(self):
        """Test getting actions when none recorded"""
        actions = self.recorder.get_actions()
        self.assertEqual(len(actions), 0)
        self.assertIsInstance(actions, list)
    
    def test_clear_actions(self):
        """Test clearing recorded actions"""
        # Add some mock actions
        self.recorder.actions = [{'test': 'action'}]
        self.recorder.clear_actions()
        self.assertEqual(len(self.recorder.actions), 0)
    
    @patch('src.recorder.mouse.Listener')
    def test_start_recording_success(self, mock_listener_class):
        """Test successful recording start"""
        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener
        
        result = self.recorder.start_recording()
        
        self.assertTrue(result)
        self.assertTrue(self.recorder.is_recording)
        self.assertIsNotNone(self.recorder.start_time)
        mock_listener.start.assert_called_once()
    
    def test_start_recording_already_recording(self):
        """Test starting recording when already recording"""
        self.recorder.is_recording = True
        result = self.recorder.start_recording()
        self.assertFalse(result)
    
    def test_stop_recording_not_recording(self):
        """Test stopping recording when not recording"""
        result = self.recorder.stop_recording()
        self.assertFalse(result)
    
    @patch('src.recorder.mouse.Listener')
    def test_stop_recording_success(self, mock_listener_class):
        """Test successful recording stop"""
        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener
        
        # Start recording first
        self.recorder.start_recording()
        
        # Stop recording
        result = self.recorder.stop_recording()
        
        self.assertTrue(result)
        self.assertFalse(self.recorder.is_recording)
        mock_listener.stop.assert_called_once()
    
    def test_click_action_creation(self):
        """Test creation of click action data"""
        # Mock the time and datetime
        with patch('src.recorder.time.time', return_value=123.5), \
             patch('src.recorder.datetime') as mock_datetime:
            
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            
            # Set up recorder state
            self.recorder.is_recording = True
            self.recorder.start_time = 123.0
            
            # Simulate click
            from pynput.mouse import Button
            self.recorder._on_click(100, 200, Button.left, True)
            
            # Check action was recorded
            actions = self.recorder.get_actions()
            self.assertEqual(len(actions), 1)
            
            action = actions[0]
            self.assertEqual(action['type'], 'click')
            self.assertEqual(action['x'], 100)
            self.assertEqual(action['y'], 200)
            self.assertEqual(action['button'], 'left')
            self.assertEqual(action['timestamp'], 0.5)  # 123.5 - 123.0
            self.assertEqual(action['absolute_time'], "2024-01-01T12:00:00")
    
    def test_debounce_functionality(self):
        """Test click debouncing"""
        with patch('src.recorder.time.time') as mock_time:
            # Set up time sequence
            times = [100.0, 100.05, 100.15]  # Second click within debounce, third outside
            mock_time.side_effect = times
            
            self.recorder.is_recording = True
            self.recorder.start_time = 100.0
            self.recorder.debounce_threshold = 0.1
            
            from pynput.mouse import Button
            
            # First click
            mock_time.return_value = times[0]
            self.recorder._on_click(100, 100, Button.left, True)
            
            # Second click (should be debounced)
            mock_time.return_value = times[1]
            self.recorder._on_click(100, 100, Button.left, True)
            
            # Third click (should be recorded)
            mock_time.return_value = times[2]
            self.recorder._on_click(100, 100, Button.left, True)
            
            # Should only have 2 actions (first and third)
            actions = self.recorder.get_actions()
            self.assertEqual(len(actions), 2)
    
    def test_save_to_file(self):
        """Test saving actions to file"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            self.temp_file = f.name
        
        # Add some test actions
        test_actions = [
            {
                'type': 'click',
                'x': 100,
                'y': 200,
                'button': 'left',
                'timestamp': 1.0,
                'absolute_time': '2024-01-01T12:00:00'
            }
        ]
        self.recorder.actions = test_actions
        
        # Save to file
        result = self.recorder.save_to_file(self.temp_file)
        self.assertTrue(result)
        
        # Verify file contents
        with open(self.temp_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('metadata', data)
        self.assertIn('actions', data)
        self.assertEqual(data['actions'], test_actions)
        self.assertEqual(data['metadata']['total_actions'], 1)
    
    def test_load_from_file(self):
        """Test loading actions from file"""
        # Create test data
        test_data = {
            'metadata': {
                'version': '1.0',
                'total_actions': 1
            },
            'actions': [
                {
                    'type': 'click',
                    'x': 150,
                    'y': 250,
                    'button': 'right',
                    'timestamp': 2.0,
                    'absolute_time': '2024-01-01T12:00:02'
                }
            ]
        }
        
        # Save test data to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(test_data, f)
            self.temp_file = f.name
        
        # Load from file
        result = self.recorder.load_from_file(self.temp_file)
        self.assertTrue(result)
        
        # Verify loaded actions
        actions = self.recorder.get_actions()
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['x'], 150)
        self.assertEqual(actions[0]['y'], 250)
        self.assertEqual(actions[0]['button'], 'right')
    
    def test_load_from_file_legacy_format(self):
        """Test loading actions from legacy format (direct array)"""
        # Create legacy test data (direct array of actions)
        test_data = [
            {
                'type': 'click',
                'x': 300,
                'y': 400,
                'button': 'middle',
                'timestamp': 3.0,
                'absolute_time': '2024-01-01T12:00:03'
            }
        ]
        
        # Save test data to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(test_data, f)
            self.temp_file = f.name
        
        # Load from file
        result = self.recorder.load_from_file(self.temp_file)
        self.assertTrue(result)
        
        # Verify loaded actions
        actions = self.recorder.get_actions()
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['x'], 300)
        self.assertEqual(actions[0]['button'], 'middle')
    
    def test_load_from_nonexistent_file(self):
        """Test loading from non-existent file"""
        result = self.recorder.load_from_file('nonexistent_file.json')
        self.assertFalse(result)
    
    def test_filter_duplicate_clicks(self):
        """Test filtering duplicate clicks"""
        # Create actions with duplicates
        test_actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.5},  # Duplicate
            {'type': 'click', 'x': 200, 'y': 200, 'button': 'left', 'timestamp': 2.0},  # Different
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 2.5},  # Same location, far time
        ]
        
        self.recorder.actions = test_actions
        
        # Filter with 1 second threshold
        removed_count = self.recorder.filter_duplicate_clicks(1.0)
        
        self.assertEqual(removed_count, 1)  # Should remove the duplicate at 0.5s
        
        actions = self.recorder.get_actions()
        self.assertEqual(len(actions), 3)
        
        # Check that the correct actions remain
        timestamps = [a['timestamp'] for a in actions]
        self.assertIn(0.0, timestamps)  # First should remain
        self.assertNotIn(0.5, timestamps)  # Duplicate should be removed
        self.assertIn(2.0, timestamps)  # Different location should remain
        self.assertIn(2.5, timestamps)  # Same location but far time should remain
    
    def test_get_recording_stats_empty(self):
        """Test getting statistics with no actions"""
        stats = self.recorder.get_recording_stats()
        
        expected_stats = {
            'total_actions': 0,
            'duration': 0,
            'clicks_per_second': 0,
            'button_distribution': {}
        }
        
        self.assertEqual(stats, expected_stats)
    
    def test_get_recording_stats_with_actions(self):
        """Test getting statistics with actions"""
        test_actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 200, 'y': 200, 'button': 'left', 'timestamp': 1.0},
            {'type': 'click', 'x': 300, 'y': 300, 'button': 'right', 'timestamp': 2.0},
            {'type': 'click', 'x': 400, 'y': 400, 'button': 'left', 'timestamp': 4.0},
        ]
        
        self.recorder.actions = test_actions
        stats = self.recorder.get_recording_stats()
        
        self.assertEqual(stats['total_actions'], 4)
        self.assertEqual(stats['duration'], 4.0)
        self.assertEqual(stats['clicks_per_second'], 1.0)  # 4 actions / 4 seconds
        self.assertEqual(stats['button_distribution'], {'left': 3, 'right': 1})


class TestMouseRecorderIntegration(unittest.TestCase):
    """Integration tests for MouseRecorder"""
    
    def setUp(self):
        """Set up test fixtures"""
        if MouseRecorder is None:
            self.skipTest("MouseRecorder not available")
        
        self.recorder = MouseRecorder()
    
    def test_full_recording_workflow(self):
        """Test complete recording workflow without actual mouse events"""
        # Test callback functionality
        recorded_actions = []
        
        def callback(action):
            recorded_actions.append(action)
        
        self.recorder.set_action_callback(callback)
        
        # Manually add actions (simulating recording)
        test_action = {
            'type': 'click',
            'x': 500,
            'y': 600,
            'button': 'left',
            'timestamp': 1.5,
            'absolute_time': '2024-01-01T12:00:01'
        }
        
        # Simulate the callback being called
        self.recorder.on_action_callback(test_action)
        
        # Check callback was called
        self.assertEqual(len(recorded_actions), 1)
        self.assertEqual(recorded_actions[0], test_action)
    
    def test_concurrent_access(self):
        """Test thread-safe access to actions"""
        import threading
        
        # Add initial actions
        for i in range(10):
            self.recorder.actions.append({
                'type': 'click',
                'x': i * 10,
                'y': i * 10,
                'button': 'left',
                'timestamp': i
            })
        
        # Function to add actions in thread
        def add_actions():
            for i in range(10, 20):
                with self.recorder.lock:
                    self.recorder.actions.append({
                        'type': 'click',
                        'x': i * 10,
                        'y': i * 10,
                        'button': 'right',
                        'timestamp': i
                    })
        
        # Function to read actions in thread
        def read_actions():
            for _ in range(5):
                actions = self.recorder.get_actions()
                self.assertIsInstance(actions, list)
                time.sleep(0.001)
        
        # Start threads
        thread1 = threading.Thread(target=add_actions)
        thread2 = threading.Thread(target=read_actions)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Check final state
        actions = self.recorder.get_actions()
        self.assertEqual(len(actions), 20)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMouseRecorder)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMouseRecorderIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)