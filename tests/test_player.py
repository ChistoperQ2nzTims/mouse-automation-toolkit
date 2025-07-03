"""
Test for ActionPlayer functionality.
"""

import unittest
import time
import sys
import os
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from recorder import MouseAction
from player import ActionPlayer


class TestActionPlayer(unittest.TestCase):
    """Test cases for ActionPlayer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player = ActionPlayer()
        
        # Create test actions
        self.test_actions = [
            MouseAction(100, 100, "left", 0.0),
            MouseAction(200, 200, "right", 1.0),
            MouseAction(300, 300, "middle", 2.0),
        ]
    
    def test_player_initialization(self):
        """Test player initial state."""
        self.assertFalse(self.player.is_playing)
        self.assertFalse(self.player.is_paused)
        self.assertFalse(self.player.stop_requested)
        self.assertEqual(self.player.speed_multiplier, 1.0)
        self.assertEqual(self.player.random_delay_range, (0.0, 0.0))
        self.assertEqual(self.player.loop_count, 1)
        self.assertTrue(self.player.safe_mode)
    
    def test_set_speed_multiplier(self):
        """Test setting speed multiplier."""
        self.player.set_speed_multiplier(2.0)
        self.assertEqual(self.player.speed_multiplier, 2.0)
        
        # Test minimum value
        self.player.set_speed_multiplier(0.05)
        self.assertEqual(self.player.speed_multiplier, 0.1)  # Should be clamped to minimum
    
    def test_set_random_delay(self):
        """Test setting random delay range."""
        self.player.set_random_delay(0.1, 0.5)
        self.assertEqual(self.player.random_delay_range, (0.1, 0.5))
        
        # Test with negative values
        self.player.set_random_delay(-0.1, 0.3)
        self.assertEqual(self.player.random_delay_range, (0.0, 0.3))  # Min should be clamped to 0
        
        # Test with reversed values
        self.player.set_random_delay(0.5, 0.1)
        self.assertEqual(self.player.random_delay_range, (0.5, 0.5))  # Max should be at least min
    
    def test_set_loop_count(self):
        """Test setting loop count."""
        self.player.set_loop_count(5)
        self.assertEqual(self.player.loop_count, 5)
        
        # Test infinite loops
        self.player.set_loop_count(-1)
        self.assertEqual(self.player.loop_count, -1)
        
        # Test invalid values
        self.player.set_loop_count(-5)
        self.assertEqual(self.player.loop_count, -1)  # Should be clamped to -1
    
    def test_set_safe_mode(self):
        """Test setting safe mode."""
        self.player.set_safe_mode(False)
        self.assertFalse(self.player.safe_mode)
        
        self.player.set_safe_mode(True)
        self.assertTrue(self.player.safe_mode)
    
    def test_progress_callback(self):
        """Test setting progress callback."""
        callback = Mock()
        self.player.set_progress_callback(callback)
        self.assertEqual(self.player.progress_callback, callback)
    
    def test_get_estimated_duration(self):
        """Test estimated duration calculation."""
        # Test with normal speed
        duration = self.player.get_estimated_duration(self.test_actions)
        self.assertEqual(duration, 2.0)  # Last timestamp is 2.0
        
        # Test with speed multiplier
        self.player.set_speed_multiplier(2.0)
        duration = self.player.get_estimated_duration(self.test_actions)
        self.assertEqual(duration, 1.0)  # Should be half the time
        
        # Test with loop count
        self.player.set_loop_count(3)
        duration = self.player.get_estimated_duration(self.test_actions)
        self.assertEqual(duration, 3.0)  # Should be 3 times the base duration
        
        # Test with random delay
        self.player.set_loop_count(1)
        self.player.set_speed_multiplier(1.0)
        self.player.set_random_delay(0.1, 0.3)
        duration = self.player.get_estimated_duration(self.test_actions)
        # Should be 2.0 + (3 actions * 0.2 average delay) = 2.6
        self.assertEqual(duration, 2.6)
    
    def test_get_estimated_duration_empty_actions(self):
        """Test estimated duration with empty actions."""
        duration = self.player.get_estimated_duration([])
        self.assertEqual(duration, 0.0)
    
    @patch('pyautogui.size')
    @patch('pyautogui.click')
    def test_perform_action(self, mock_click, mock_size):
        """Test performing a single action."""
        mock_size.return_value = (1920, 1080)
        
        action = MouseAction(100, 200, "left", 1.0)
        self.player._perform_action(action)
        
        mock_click.assert_called_once_with(100, 200, button='left')
    
    @patch('pyautogui.size')
    @patch('pyautogui.click')
    def test_perform_action_different_buttons(self, mock_click, mock_size):
        """Test performing actions with different button types."""
        mock_size.return_value = (1920, 1080)
        
        # Test right click
        action_right = MouseAction(150, 250, "right", 1.0)
        self.player._perform_action(action_right)
        mock_click.assert_called_with(150, 250, button='right')
        
        # Test middle click
        action_middle = MouseAction(200, 300, "middle", 2.0)
        self.player._perform_action(action_middle)
        mock_click.assert_called_with(200, 300, button='middle')
    
    @patch('pyautogui.size')
    def test_perform_action_out_of_bounds(self, mock_size):
        """Test performing action with coordinates out of screen bounds."""
        mock_size.return_value = (1920, 1080)
        
        # Action outside screen bounds
        action = MouseAction(2000, 1500, "left", 1.0)
        
        # Should not raise exception, just print warning
        self.player._perform_action(action)
    
    def test_is_busy(self):
        """Test is_busy method."""
        self.assertFalse(self.player.is_busy())
        
        self.player.is_playing = True
        self.assertTrue(self.player.is_busy())
    
    def test_stop_playback(self):
        """Test stopping playback."""
        self.player.is_playing = True
        self.player.stop_playback()
        
        self.assertFalse(self.player.is_playing)
        self.assertTrue(self.player.stop_requested)
    
    def test_pause_resume_playback(self):
        """Test pausing and resuming playback."""
        self.player.is_playing = True
        
        # Test pause
        self.player.pause_playback()
        self.assertTrue(self.player.is_paused)
        
        # Test resume
        self.player.resume_playback()
        self.assertFalse(self.player.is_paused)
    
    @patch('tkinter.messagebox.showinfo')
    def test_preview_actions(self, mock_showinfo):
        """Test previewing actions."""
        self.player.preview_actions(self.test_actions)
        
        # Should call messagebox.showinfo
        mock_showinfo.assert_called_once()
        
        # Check that the preview includes action information
        call_args = mock_showinfo.call_args[1]
        self.assertIn("Actions to be performed", call_args['message'])
    
    def test_preview_actions_empty(self):
        """Test previewing empty actions list."""
        # Should not raise exception
        self.player.preview_actions([])
    
    @patch('pyautogui.size')
    @patch('pyautogui.click')
    @patch('time.sleep')
    def test_play_actions_basic(self, mock_sleep, mock_click, mock_size):
        """Test basic action playback."""
        mock_size.return_value = (1920, 1080)
        
        # Create simple actions
        actions = [
            MouseAction(100, 100, "left", 0.0),
            MouseAction(200, 200, "left", 0.5),
        ]
        
        # Mock the threading to avoid actual delays
        with patch('threading.Thread') as mock_thread:
            self.player.play_actions(actions)
            
            # Should create a playback thread
            mock_thread.assert_called_once()
            
            # Simulate thread execution
            thread_target = mock_thread.call_args[1]['target']
            thread_args = mock_thread.call_args[1]['args']
            
            # Execute the thread function
            thread_target(*thread_args)
        
        # Should have called click for each action
        self.assertEqual(mock_click.call_count, 2)
    
    def test_play_actions_empty(self):
        """Test playing empty actions list."""
        # Should not start playback
        self.player.play_actions([])
        self.assertFalse(self.player.is_playing)
    
    def test_play_actions_already_playing(self):
        """Test starting playback when already playing."""
        self.player.is_playing = True
        
        # Should not start new playback
        self.player.play_actions(self.test_actions)
        # State should remain unchanged
        self.assertTrue(self.player.is_playing)


if __name__ == '__main__':
    unittest.main()