#!/usr/bin/env python3
"""
Unit tests for ActionPlayer module

Tests the mouse action playback functionality including action loading,
playback control, speed control, and validation.
"""

import unittest
import time
import threading
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.player import ActionPlayer
except ImportError:
    print("Warning: Could not import ActionPlayer. Some tests may be skipped.")
    ActionPlayer = None


class TestActionPlayer(unittest.TestCase):
    """Test cases for ActionPlayer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        if ActionPlayer is None:
            self.skipTest("ActionPlayer not available")
        
        self.player = ActionPlayer()
        
        # Sample actions for testing
        self.sample_actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 200, 'y': 150, 'button': 'right', 'timestamp': 1.0},
            {'type': 'click', 'x': 150, 'y': 200, 'button': 'left', 'timestamp': 2.5},
        ]
    
    def test_initialization(self):
        """Test player initialization"""
        self.assertFalse(self.player.is_playing)
        self.assertFalse(self.player.is_paused)
        self.assertFalse(self.player.should_stop)
        self.assertEqual(self.player.speed_multiplier, 1.0)
        self.assertFalse(self.player.loop_mode)
        self.assertTrue(self.player.safe_mode)
        self.assertEqual(self.player.current_action_index, 0)
    
    def test_callback_setting(self):
        """Test setting callback functions"""
        progress_callback = Mock()
        complete_callback = Mock()
        
        self.player.set_progress_callback(progress_callback)
        self.player.set_complete_callback(complete_callback)
        
        self.assertEqual(self.player.on_progress_callback, progress_callback)
        self.assertEqual(self.player.on_complete_callback, complete_callback)
    
    def test_load_actions_success(self):
        """Test successful action loading"""
        result = self.player.load_actions(self.sample_actions)
        self.assertTrue(result)
        self.assertEqual(len(self.player.actions), 3)  # All are click actions
        self.assertEqual(self.player.current_action_index, 0)
    
    def test_load_actions_filter_non_clicks(self):
        """Test loading actions filters out non-click actions"""
        mixed_actions = self.sample_actions + [
            {'type': 'move', 'x': 300, 'y': 300, 'timestamp': 3.0},
            {'type': 'scroll', 'x': 400, 'y': 400, 'timestamp': 4.0}
        ]
        
        result = self.player.load_actions(mixed_actions)
        self.assertTrue(result)
        self.assertEqual(len(self.player.actions), 3)  # Only click actions
    
    def test_load_actions_empty(self):
        """Test loading empty actions list"""
        result = self.player.load_actions([])
        self.assertTrue(result)
        self.assertEqual(len(self.player.actions), 0)
    
    def test_speed_setting(self):
        """Test speed multiplier setting with bounds checking"""
        # Normal speed
        self.player.set_speed(2.0)
        self.assertEqual(self.player.speed_multiplier, 2.0)
        
        # Minimum bound
        self.player.set_speed(0.05)
        self.assertEqual(self.player.speed_multiplier, 0.1)
        
        # Maximum bound
        self.player.set_speed(10.0)
        self.assertEqual(self.player.speed_multiplier, 5.0)
        
        # Negative value
        self.player.set_speed(-1.0)
        self.assertEqual(self.player.speed_multiplier, 0.1)
    
    def test_mode_settings(self):
        """Test various mode settings"""
        # Loop mode
        self.player.set_loop_mode(True)
        self.assertTrue(self.player.loop_mode)
        
        self.player.set_loop_mode(False)
        self.assertFalse(self.player.loop_mode)
        
        # Safe mode
        self.player.set_safe_mode(False)
        self.assertFalse(self.player.safe_mode)
        
        self.player.set_safe_mode(True)
        self.assertTrue(self.player.safe_mode)
        
        # Screen bounds
        self.player.set_screen_bounds(1920, 1080)
        self.assertEqual(self.player.screen_bounds, (1920, 1080))
    
    def test_play_without_actions(self):
        """Test playing without loaded actions"""
        result = self.player.play()
        self.assertFalse(result)
        self.assertFalse(self.player.is_playing)
    
    def test_play_while_already_playing(self):
        """Test playing while already playing"""
        self.player.load_actions(self.sample_actions)
        self.player.is_playing = True  # Simulate already playing
        
        result = self.player.play()
        self.assertFalse(result)
    
    @patch('src.player.threading.Thread')
    @patch('src.player.keyboard.Listener')
    def test_play_start_success(self, mock_keyboard_listener, mock_thread):
        """Test successful play start"""
        mock_listener = MagicMock()
        mock_keyboard_listener.return_value = mock_listener
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        self.player.load_actions(self.sample_actions)
        result = self.player.play()
        
        self.assertTrue(result)
        self.assertTrue(self.player.is_playing)
        self.assertFalse(self.player.is_paused)
        self.assertFalse(self.player.should_stop)
        
        # Verify thread and listener were started
        mock_thread_instance.start.assert_called_once()
        mock_listener.start.assert_called_once()
    
    def test_pause_not_playing(self):
        """Test pausing when not playing"""
        result = self.player.pause()
        self.assertFalse(result)
    
    def test_pause_toggle(self):
        """Test pause toggle functionality"""
        self.player.is_playing = True
        
        # First pause
        result = self.player.pause()
        self.assertTrue(result)
        self.assertTrue(self.player.is_paused)
        
        # Unpause
        result = self.player.pause()
        self.assertTrue(result)
        self.assertFalse(self.player.is_paused)
    
    def test_stop_not_playing(self):
        """Test stopping when not playing"""
        result = self.player.stop()
        self.assertFalse(result)
    
    def test_stop_while_playing(self):
        """Test stopping while playing"""
        self.player.is_playing = True
        self.player.current_action_index = 5
        
        result = self.player.stop()
        
        self.assertTrue(result)
        self.assertFalse(self.player.is_playing)
        self.assertFalse(self.player.is_paused)
        self.assertTrue(self.player.should_stop)
        self.assertEqual(self.player.current_action_index, 0)
    
    @patch('src.player.pyautogui.click')
    def test_execute_action_left_click(self, mock_click):
        """Test executing left click action"""
        action = {'x': 100, 'y': 200, 'button': 'left'}
        self.player._execute_action(action)
        mock_click.assert_called_once_with(100, 200, button='left')
    
    @patch('src.player.pyautogui.click')
    def test_execute_action_right_click(self, mock_click):
        """Test executing right click action"""
        action = {'x': 150, 'y': 250, 'button': 'right'}
        self.player._execute_action(action)
        mock_click.assert_called_once_with(150, 250, button='right')
    
    @patch('src.player.pyautogui.click')
    def test_execute_action_middle_click(self, mock_click):
        """Test executing middle click action"""
        action = {'x': 200, 'y': 300, 'button': 'middle'}
        self.player._execute_action(action)
        mock_click.assert_called_once_with(200, 300, button='middle')
    
    @patch('src.player.pyautogui.click')
    def test_execute_action_unknown_button(self, mock_click):
        """Test executing action with unknown button (defaults to left)"""
        action = {'x': 250, 'y': 350, 'button': 'unknown'}
        self.player._execute_action(action)
        mock_click.assert_called_once_with(250, 350, button='left')
    
    @patch('src.player.pyautogui.click')
    def test_execute_action_safe_mode_protection(self, mock_click):
        """Test safe mode protection against out-of-bounds clicks"""
        self.player.set_safe_mode(True)
        self.player.set_screen_bounds(800, 600)
        
        # Out of bounds action
        action = {'x': 1000, 'y': 700, 'button': 'left'}
        self.player._execute_action(action)
        
        # Should not have called click
        mock_click.assert_not_called()
    
    @patch('src.player.pyautogui.click')
    def test_execute_action_safe_mode_disabled(self, mock_click):
        """Test that safe mode can be disabled"""
        self.player.set_safe_mode(False)
        self.player.set_screen_bounds(800, 600)
        
        # Out of bounds action
        action = {'x': 1000, 'y': 700, 'button': 'left'}
        self.player._execute_action(action)
        
        # Should have called click even though out of bounds
        mock_click.assert_called_once_with(1000, 700, button='left')
    
    def test_get_playback_status_initial(self):
        """Test getting initial playback status"""
        self.player.load_actions(self.sample_actions)
        
        status = self.player.get_playback_status()
        
        expected = {
            'is_playing': False,
            'is_paused': False,
            'current_action': 0,
            'total_actions': 3,
            'progress': 0.0,
            'speed_multiplier': 1.0,
            'loop_mode': False,
            'safe_mode': True
        }
        
        self.assertEqual(status, expected)
    
    def test_get_playback_status_during_playback(self):
        """Test getting playback status during playback"""
        self.player.load_actions(self.sample_actions)
        self.player.is_playing = True
        self.player.is_paused = True
        self.player.current_action_index = 1
        self.player.set_speed(2.0)
        self.player.set_loop_mode(True)
        
        status = self.player.get_playback_status()
        
        self.assertTrue(status['is_playing'])
        self.assertTrue(status['is_paused'])
        self.assertEqual(status['current_action'], 1)
        self.assertEqual(status['total_actions'], 3)
        self.assertAlmostEqual(status['progress'], 1/3, places=6)
        self.assertEqual(status['speed_multiplier'], 2.0)
        self.assertTrue(status['loop_mode'])
    
    def test_get_time_remaining_not_playing(self):
        """Test getting time remaining when not playing"""
        remaining = self.player.get_time_remaining()
        self.assertEqual(remaining, 0.0)
    
    def test_get_time_remaining_during_playback(self):
        """Test getting time remaining during playback"""
        self.player.load_actions(self.sample_actions)
        self.player.is_playing = True
        self.player.current_action_index = 1
        self.player.set_speed(2.0)
        
        remaining = self.player.get_time_remaining()
        
        # Should calculate based on remaining timestamps and speed
        # Last action at 2.5s, current at 1.0s = 1.5s remaining
        # At 2x speed = 0.75s remaining
        self.assertAlmostEqual(remaining, 0.75, places=2)
    
    def test_skip_to_action_valid(self):
        """Test skipping to valid action index"""
        self.player.load_actions(self.sample_actions)
        
        result = self.player.skip_to_action(2)
        self.assertTrue(result)
        self.assertEqual(self.player.current_action_index, 2)
    
    def test_skip_to_action_invalid(self):
        """Test skipping to invalid action indices"""
        self.player.load_actions(self.sample_actions)
        
        # Negative index
        result = self.player.skip_to_action(-1)
        self.assertFalse(result)
        
        # Index too large
        result = self.player.skip_to_action(10)
        self.assertFalse(result)
        
        # Current index should be unchanged
        self.assertEqual(self.player.current_action_index, 0)
    
    def test_preview_action_valid(self):
        """Test previewing valid action"""
        self.player.load_actions(self.sample_actions)
        self.player.set_speed(2.0)
        
        preview = self.player.preview_action(1)
        
        self.assertIsNotNone(preview)
        self.assertEqual(preview['index'], 1)
        self.assertEqual(preview['type'], 'click')
        self.assertEqual(preview['x'], 200)
        self.assertEqual(preview['y'], 150)
        self.assertEqual(preview['button'], 'right')
        self.assertEqual(preview['timestamp'], 1.0)
        self.assertEqual(preview['estimated_time'], 0.5)  # 1.0 / 2.0 speed
    
    def test_preview_action_invalid(self):
        """Test previewing invalid action index"""
        self.player.load_actions(self.sample_actions)
        
        preview = self.player.preview_action(-1)
        self.assertIsNone(preview)
        
        preview = self.player.preview_action(10)
        self.assertIsNone(preview)
    
    def test_interruptible_sleep(self):
        """Test interruptible sleep functionality"""
        start_time = time.time()
        
        # Sleep for a short time without interruption
        self.player._interruptible_sleep(0.1)
        elapsed = time.time() - start_time
        self.assertGreaterEqual(elapsed, 0.1)
        self.assertLess(elapsed, 0.2)  # Should not take much longer
        
        # Test interruption
        self.player.should_stop = True
        start_time = time.time()
        self.player._interruptible_sleep(1.0)  # Try to sleep 1 second
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 0.5)  # Should be interrupted quickly


class TestActionPlayerValidation(unittest.TestCase):
    """Test validation functionality of ActionPlayer"""
    
    def setUp(self):
        """Set up test fixtures"""
        if ActionPlayer is None:
            self.skipTest("ActionPlayer not available")
        
        self.player = ActionPlayer()
    
    def test_validate_actions_empty(self):
        """Test validation with empty actions"""
        validation = self.player.validate_actions()
        
        self.assertFalse(validation['valid'])
        self.assertIn('No actions loaded', validation['issues'])
        self.assertEqual(validation['total_actions'], 0)
    
    def test_validate_actions_normal(self):
        """Test validation with normal actions"""
        normal_actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 200, 'y': 200, 'button': 'right', 'timestamp': 1.0},
        ]
        
        self.player.load_actions(normal_actions)
        self.player.set_screen_bounds(1920, 1080)
        
        validation = self.player.validate_actions()
        
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['issues']), 0)
        self.assertEqual(validation['total_actions'], 2)
        self.assertEqual(validation['duration'], 1.0)
    
    def test_validate_actions_out_of_bounds(self):
        """Test validation with out-of-bounds actions"""
        oob_actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 2000, 'y': 1200, 'button': 'left', 'timestamp': 1.0},  # Out of bounds
            {'type': 'click', 'x': -50, 'y': 50, 'button': 'left', 'timestamp': 2.0},    # Out of bounds
        ]
        
        self.player.load_actions(oob_actions)
        self.player.set_safe_mode(True)
        self.player.set_screen_bounds(1920, 1080)
        
        validation = self.player.validate_actions()
        
        self.assertTrue(validation['valid'])  # Still valid, just has warnings
        self.assertIn('actions are outside screen bounds', validation['warnings'][0])
    
    def test_validate_actions_rapid_clicks(self):
        """Test validation with rapid clicks"""
        rapid_actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 101, 'y': 101, 'button': 'left', 'timestamp': 0.01},   # Very fast
            {'type': 'click', 'x': 102, 'y': 102, 'button': 'left', 'timestamp': 0.02},   # Very fast
        ]
        
        self.player.load_actions(rapid_actions)
        validation = self.player.validate_actions()
        
        self.assertTrue(validation['valid'])
        self.assertIn('actions have very short intervals', validation['warnings'][0])
    
    def test_validate_actions_long_duration(self):
        """Test validation with very long duration"""
        long_actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 200, 'y': 200, 'button': 'left', 'timestamp': 400.0},  # > 5 minutes
        ]
        
        self.player.load_actions(long_actions)
        validation = self.player.validate_actions()
        
        self.assertTrue(validation['valid'])
        self.assertIn('Long playback duration', validation['warnings'][0])


class TestActionPlayerIntegration(unittest.TestCase):
    """Integration tests for ActionPlayer"""
    
    def setUp(self):
        """Set up test fixtures"""
        if ActionPlayer is None:
            self.skipTest("ActionPlayer not available")
        
        self.player = ActionPlayer()
    
    @patch('src.player.pyautogui.click')
    def test_callback_integration(self, mock_click):
        """Test that callbacks are properly called during playback simulation"""
        actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0},
            {'type': 'click', 'x': 200, 'y': 200, 'button': 'left', 'timestamp': 0.1},
        ]
        
        progress_calls = []
        complete_calls = []
        
        def progress_callback(progress, current, total):
            progress_calls.append((progress, current, total))
        
        def complete_callback(loops):
            complete_calls.append(loops)
        
        self.player.set_progress_callback(progress_callback)
        self.player.set_complete_callback(complete_callback)
        self.player.load_actions(actions)
        self.player.set_speed(10.0)  # Very fast for testing
        
        # Simulate playback by calling the internal method directly
        self.player.is_playing = True
        self.player._play_actions()
        
        # Check that callbacks were called
        self.assertGreater(len(progress_calls), 0)
        self.assertEqual(len(complete_calls), 1)
        self.assertEqual(complete_calls[0], 1)  # One loop completed
    
    def test_thread_safety(self):
        """Test thread safety of player operations"""
        actions = [
            {'type': 'click', 'x': 100, 'y': 100, 'button': 'left', 'timestamp': 0.0}
        ]
        
        self.player.load_actions(actions)
        
        # Function to get status in thread
        def get_status():
            for _ in range(10):
                status = self.player.get_playback_status()
                self.assertIsInstance(status, dict)
                time.sleep(0.001)
        
        # Function to modify state in thread
        def modify_state():
            for i in range(10):
                self.player.set_speed(1.0 + i * 0.1)
                self.player.set_loop_mode(i % 2 == 0)
                time.sleep(0.001)
        
        # Start threads
        thread1 = threading.Thread(target=get_status)
        thread2 = threading.Thread(target=modify_state)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Should complete without errors
        final_status = self.player.get_playback_status()
        self.assertIsInstance(final_status, dict)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestActionPlayer))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestActionPlayerValidation))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestActionPlayerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)