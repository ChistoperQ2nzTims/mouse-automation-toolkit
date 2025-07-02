"""
Tests for the MousePlayer module.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.recorder import MouseAction
from src.player import MousePlayer


class TestMousePlayer(unittest.TestCase):
    """Test MousePlayer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player = MousePlayer()
        
        # Create test actions
        self.test_actions = [
            MouseAction('move', 100, 100, delay=0.1),
            MouseAction('press', 100, 100, 'left', delay=0.1),
            MouseAction('release', 100, 100, 'left', delay=0.1),
            MouseAction('move', 200, 200, delay=0.2),
            MouseAction('press', 200, 200, 'right', delay=0.1),
            MouseAction('release', 200, 200, 'right', delay=0.1)
        ]
        
    def test_create_player(self):
        """Test creating a player."""
        self.assertFalse(self.player.is_playing)
        self.assertFalse(self.player.is_paused)
        self.assertFalse(self.player.stop_requested)
        self.assertEqual(self.player.current_action_index, 0)
        
    def test_get_playback_status(self):
        """Test getting playback status."""
        status = self.player.get_playback_status()
        
        expected_keys = ['is_playing', 'is_paused', 'current_action', 'total_actions', 'progress_percentage']
        for key in expected_keys:
            self.assertIn(key, status)
            
        self.assertFalse(status['is_playing'])
        self.assertFalse(status['is_paused'])
        self.assertEqual(status['current_action'], 1)
        self.assertEqual(status['total_actions'], 0)
        self.assertEqual(status['progress_percentage'], 0)
        
    def test_preview_actions(self):
        """Test previewing actions."""
        preview = self.player.preview_actions(self.test_actions)
        
        self.assertEqual(len(preview), len(self.test_actions))
        
        # Check first action preview
        first_preview = preview[0]
        self.assertEqual(first_preview['index'], 1)
        self.assertEqual(first_preview['action_type'], 'move')
        self.assertEqual(first_preview['position'], '(100, 100)')
        self.assertEqual(first_preview['button'], 'N/A')
        self.assertEqual(first_preview['delay'], '0.100s')
        
        # Check action with button
        second_preview = preview[1]
        self.assertEqual(second_preview['button'], 'left')
        
    def test_validate_actions_valid(self):
        """Test validating valid actions."""
        with patch('pyautogui.size', return_value=(1920, 1080)):
            warnings = self.player.validate_actions(self.test_actions)
            self.assertEqual(len(warnings), 0)
            
    def test_validate_actions_out_of_bounds(self):
        """Test validating actions with out-of-bounds coordinates."""
        invalid_actions = [
            MouseAction('click', -10, 50, 'left'),  # Negative X
            MouseAction('click', 50, -10, 'left'),  # Negative Y
            MouseAction('click', 2000, 50, 'left'), # X too large
            MouseAction('click', 50, 1100, 'left')  # Y too large
        ]
        
        with patch('pyautogui.size', return_value=(1920, 1080)):
            warnings = self.player.validate_actions(invalid_actions)
            self.assertEqual(len(warnings), 4)
            
            # Check warning messages contain coordinate information
            for warning in warnings:
                self.assertIn('coordinate', warning.lower())
                self.assertIn('outside screen bounds', warning.lower())
                
    def test_validate_actions_long_delays(self):
        """Test validating actions with very long delays."""
        long_delay_actions = [
            MouseAction('click', 100, 100, 'left', delay=15.0),
            MouseAction('move', 200, 200, delay=0.1)
        ]
        
        with patch('pyautogui.size', return_value=(1920, 1080)):
            warnings = self.player.validate_actions(long_delay_actions)
            self.assertEqual(len(warnings), 1)
            self.assertIn('Very long delay', warnings[0])
            
    def test_validate_actions_unknown_button(self):
        """Test validating actions with unknown button types."""
        unknown_button_actions = [
            MouseAction('click', 100, 100, 'unknown_button'),
            MouseAction('press', 200, 200, 'another_unknown')
        ]
        
        with patch('pyautogui.size', return_value=(1920, 1080)):
            warnings = self.player.validate_actions(unknown_button_actions)
            self.assertEqual(len(warnings), 2)
            
            for warning in warnings:
                self.assertIn('Unknown button type', warning)
                
    def test_get_estimated_duration(self):
        """Test estimating playback duration."""
        duration = self.player.get_estimated_duration(self.test_actions)
        
        # Total delay = 0.1 + 0.1 + 0.1 + 0.2 + 0.1 + 0.1 = 0.7
        # Estimated execution time = 6 actions * 0.05 = 0.3
        # Total = 0.7 + 0.3 = 1.0
        expected_duration = 0.7 + (6 * 0.05)
        self.assertEqual(duration, expected_duration)
        
    def test_get_estimated_duration_with_multiplier(self):
        """Test estimating duration with delay multiplier."""
        multiplier = 2.0
        duration = self.player.get_estimated_duration(self.test_actions, multiplier)
        
        # Total delay = 0.7 * 2.0 = 1.4
        # Estimated execution time = 6 actions * 0.05 = 0.3
        # Total = 1.4 + 0.3 = 1.7
        expected_duration = (0.7 * multiplier) + (6 * 0.05)
        self.assertEqual(duration, expected_duration)
        
    def test_get_estimated_duration_empty(self):
        """Test estimating duration for empty action list."""
        duration = self.player.get_estimated_duration([])
        self.assertEqual(duration, 0.0)
        
    @patch('pyautogui.moveTo')
    def test_execute_move_action(self, mock_move):
        """Test executing move action."""
        action = MouseAction('move', 150, 250)
        self.player._execute_action(action)
        
        mock_move.assert_called_once_with(150, 250)
        
    @patch('pyautogui.click')
    def test_execute_click_action(self, mock_click):
        """Test executing click action."""
        action = MouseAction('click', 300, 400, 'right')
        self.player._execute_action(action)
        
        mock_click.assert_called_once_with(300, 400, button='right')
        
    @patch('pyautogui.mouseDown')
    def test_execute_press_action(self, mock_press):
        """Test executing press action."""
        action = MouseAction('press', 500, 600, 'left')
        self.player._execute_action(action)
        
        mock_press.assert_called_once_with(500, 600, button='left')
        
    @patch('pyautogui.mouseUp')
    def test_execute_release_action(self, mock_release):
        """Test executing release action."""
        action = MouseAction('release', 700, 800, 'middle')
        self.player._execute_action(action)
        
        mock_release.assert_called_once_with(700, 800, button='middle')
        
    def test_execute_unknown_action(self):
        """Test executing unknown action type."""
        action = MouseAction('unknown', 100, 100)
        
        # Should not raise exception
        try:
            self.player._execute_action(action)
        except Exception as e:
            self.fail(f"Executing unknown action raised an exception: {e}")
            
    def test_button_mapping(self):
        """Test button name mapping."""
        # Test that None button defaults to 'left'
        with patch('pyautogui.click') as mock_click:
            action = MouseAction('click', 100, 100, None)
            self.player._execute_action(action)
            mock_click.assert_called_once_with(100, 100, button='left')
            
        # Test that unknown button defaults to 'left'
        with patch('pyautogui.click') as mock_click:
            action = MouseAction('click', 100, 100, 'unknown')
            self.player._execute_action(action)
            mock_click.assert_called_once_with(100, 100, button='left')
            
    def test_set_failsafe(self):
        """Test setting failsafe mode."""
        with patch('pyautogui.FAILSAFE', True) as mock_failsafe:
            self.player.set_failsafe(False)
            # Note: We can't directly test pyautogui.FAILSAFE assignment
            # but we can test that the method doesn't raise exceptions
            
    def test_set_pause_duration(self):
        """Test setting pause duration."""
        with patch('pyautogui.PAUSE', 0.1) as mock_pause:
            self.player.set_pause_duration(0.5)
            # Note: We can't directly test pyautogui.PAUSE assignment
            # but we can test that the method doesn't raise exceptions
            
    @patch('threading.Thread')
    def test_play_actions_empty_list(self, mock_thread):
        """Test playing empty action list."""
        self.player.play_actions([])
        
        # Should not start a thread for empty actions
        mock_thread.assert_not_called()
        
    @patch('threading.Thread')
    def test_play_actions_already_playing(self, mock_thread):
        """Test playing actions when already playing."""
        self.player.is_playing = True
        
        self.player.play_actions(self.test_actions)
        
        # Should not start a new thread
        mock_thread.assert_not_called()
        
    def test_stop_playback_not_playing(self):
        """Test stopping playback when not playing."""
        # Should not raise exception
        self.player.stop_playback()
        self.assertFalse(self.player.is_playing)
        
    def test_pause_resume_not_playing(self):
        """Test pause/resume when not playing."""
        # Should not raise exceptions
        self.player.pause_playback()
        self.player.resume_playback()
        
    @patch('time.sleep')
    @patch('pyautogui.moveTo')
    @patch('pyautogui.click')
    def test_playback_with_callbacks(self, mock_click, mock_move, mock_sleep):
        """Test playback with progress and completion callbacks."""
        progress_calls = []
        completion_called = []
        
        def progress_callback(current, total):
            progress_calls.append((current, total))
            
        def completion_callback():
            completion_called.append(True)
            
        # Use a simple action for testing
        simple_actions = [MouseAction('click', 100, 100, 'left', delay=0.01)]
        
        # Start playback
        self.player.play_actions(
            simple_actions,
            progress_callback=progress_callback,
            completion_callback=completion_callback
        )
        
        # Wait a moment for the thread to start and complete
        time.sleep(0.1)
        
        # Check that callbacks were set
        self.assertEqual(self.player.progress_callback, progress_callback)
        self.assertEqual(self.player.completion_callback, completion_callback)


class TestMousePlayerIntegration(unittest.TestCase):
    """Integration tests for MousePlayer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player = MousePlayer()
        
    def test_full_playback_cycle(self):
        """Test complete playback cycle with mocked PyAutoGUI."""
        actions = [
            MouseAction('move', 100, 100, delay=0.01),
            MouseAction('click', 100, 100, 'left', delay=0.01)
        ]
        
        with patch('pyautogui.moveTo') as mock_move, \
             patch('pyautogui.click') as mock_click, \
             patch('time.sleep') as mock_sleep:
            
            # Start playback
            progress_updates = []
            
            def track_progress(current, total):
                progress_updates.append((current, total))
                
            self.player.play_actions(
                actions,
                delay_multiplier=0.1,  # Speed up for testing
                progress_callback=track_progress
            )
            
            # Wait for playback to complete
            timeout = 2.0
            start_time = time.time()
            
            while self.player.is_playing and (time.time() - start_time) < timeout:
                time.sleep(0.01)
                
            # Verify playback completed
            self.assertFalse(self.player.is_playing)
            
            # Verify PyAutoGUI calls were made
            mock_move.assert_called()
            mock_click.assert_called()


if __name__ == '__main__':
    unittest.main()