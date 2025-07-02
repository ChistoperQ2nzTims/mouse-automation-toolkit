#!/usr/bin/env python3
"""
Unit tests for the ActionPlayer module.
"""

import unittest
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recorder import MouseAction
from src.player import ActionPlayer


class TestActionPlayer(unittest.TestCase):
    """Test the ActionPlayer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player = ActionPlayer()
        
        # Create sample actions for testing
        self.sample_actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.5, 'click', 100, 100, 'left', True),
            MouseAction(0.6, 'click', 100, 100, 'left', False),
            MouseAction(1.0, 'move', 200, 200),
            MouseAction(1.5, 'click', 200, 200, 'right', True),
            MouseAction(1.6, 'click', 200, 200, 'right', False)
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        self.player.cleanup()
    
    def test_player_initialization(self):
        """Test player initialization."""
        self.assertFalse(self.player.is_playing)
        self.assertFalse(self.player.should_stop)
        self.assertEqual(self.player.current_action_index, 0)
        self.assertEqual(self.player.total_actions, 0)
    
    def test_create_click_action(self):
        """Test creating click actions."""
        click_actions = self.player.create_click_action(150, 250, 'right')
        
        self.assertEqual(len(click_actions), 2)
        
        # Check press action
        press_action = click_actions[0]
        self.assertEqual(press_action.action_type, 'click')
        self.assertEqual(press_action.x, 150)
        self.assertEqual(press_action.y, 250)
        self.assertEqual(press_action.button, 'right')
        self.assertTrue(press_action.pressed)
        
        # Check release action
        release_action = click_actions[1]
        self.assertEqual(release_action.action_type, 'click')
        self.assertEqual(release_action.x, 150)
        self.assertEqual(release_action.y, 250)
        self.assertEqual(release_action.button, 'right')
        self.assertFalse(release_action.pressed)
    
    def test_create_drag_action(self):
        """Test creating drag actions."""
        drag_actions = self.player.create_drag_action(100, 100, 300, 200, 2.0, 'left')
        
        self.assertGreater(len(drag_actions), 3)  # At least press, some moves, release
        
        # First action should be press
        first_action = drag_actions[0]
        self.assertEqual(first_action.action_type, 'click')
        self.assertEqual(first_action.x, 100)
        self.assertEqual(first_action.y, 100)
        self.assertTrue(first_action.pressed)
        
        # Last action should be release
        last_action = drag_actions[-1]
        self.assertEqual(last_action.action_type, 'click')
        self.assertEqual(last_action.x, 300)
        self.assertEqual(last_action.y, 200)
        self.assertFalse(last_action.pressed)
        
        # Duration should match
        self.assertAlmostEqual(last_action.timestamp, 2.0, places=1)
    
    def test_validate_actions(self):
        """Test action validation."""
        validation = self.player.validate_actions(self.sample_actions)
        
        self.assertTrue(validation['valid'])
        self.assertEqual(validation['action_count'], len(self.sample_actions))
        self.assertGreater(validation['estimated_duration'], 0)
    
    def test_validate_empty_actions(self):
        """Test validation of empty action list."""
        validation = self.player.validate_actions([])
        
        self.assertFalse(validation['valid'])
        self.assertIn('No actions provided', validation['error'])
    
    @patch('pyautogui.size')
    def test_validate_out_of_bounds_actions(self, mock_size):
        """Test validation of actions outside screen bounds."""
        mock_size.return_value = (1000, 800)  # Mock screen size
        
        out_of_bounds_actions = [
            MouseAction(0.0, 'move', -10, 100),      # X out of bounds
            MouseAction(0.5, 'move', 100, -10),      # Y out of bounds
            MouseAction(1.0, 'move', 1500, 100),     # X too large
            MouseAction(1.5, 'move', 100, 1000),     # Y too large
        ]
        
        validation = self.player.validate_actions(out_of_bounds_actions)
        
        self.assertTrue(validation['valid'])  # Still valid, just warnings
        self.assertGreater(len(validation['warnings']), 0)
        
        # Check that warnings mention out-of-bounds coordinates
        warning_text = ' '.join(validation['warnings'])
        self.assertIn('outside screen bounds', warning_text)
    
    def test_playback_progress(self):
        """Test playback progress tracking."""
        # Initially no progress
        progress = self.player.get_playback_progress()
        self.assertFalse(progress['is_playing'])
        self.assertEqual(progress['progress_percent'], 0)
        
        # Mock playing state
        self.player.is_playing = True
        self.player.total_actions = 10
        self.player.current_action_index = 3
        
        progress = self.player.get_playback_progress()
        self.assertTrue(progress['is_playing'])
        self.assertEqual(progress['current_action'], 3)
        self.assertEqual(progress['total_actions'], 10)
        self.assertEqual(progress['progress_percent'], 30.0)
    
    def test_stop_playback(self):
        """Test stopping playback."""
        self.player.is_playing = True
        self.assertFalse(self.player.should_stop)
        
        self.player.stop_playback()
        self.assertTrue(self.player.should_stop)
    
    @patch('time.sleep')
    def test_wait_interruptible(self, mock_sleep):
        """Test interruptible wait functionality."""
        # Test normal completion
        self.player.should_stop = False
        result = self.player._wait_interruptible(0.001)  # Very short duration
        self.assertFalse(result)  # Should complete normally
        
        # Test interruption
        self.player.should_stop = True
        result = self.player._wait_interruptible(1.0)
        self.assertTrue(result)  # Should be interrupted
    
    @patch('pyautogui.moveTo')
    @patch('pyautogui.mouseDown')
    @patch('pyautogui.mouseUp')
    def test_execute_click_actions(self, mock_mouse_up, mock_mouse_down, mock_move_to):
        """Test execution of click actions."""
        # Test mouse press
        press_action = MouseAction(0.0, 'click', 100, 200, 'left', True)
        self.player._execute_action(press_action)
        mock_mouse_down.assert_called_once_with(100, 200, button='left')
        
        # Test mouse release
        mock_mouse_down.reset_mock()
        release_action = MouseAction(0.1, 'click', 100, 200, 'left', False)
        self.player._execute_action(release_action)
        mock_mouse_up.assert_called_once_with(100, 200, button='left')
    
    @patch('pyautogui.moveTo')
    def test_execute_move_action(self, mock_move_to):
        """Test execution of move actions."""
        move_action = MouseAction(0.0, 'move', 300, 400)
        self.player._execute_action(move_action)
        mock_move_to.assert_called_once_with(300, 400)
    
    @patch('pyautogui.moveTo')
    @patch('pyautogui.scroll')
    def test_execute_scroll_action(self, mock_scroll, mock_move_to):
        """Test execution of scroll actions."""
        # Test scroll up
        scroll_up_action = MouseAction(0.0, 'scroll', 150, 250, 
                                     scroll_direction='up', scroll_amount=3)
        self.player._execute_action(scroll_up_action)
        mock_move_to.assert_called_with(150, 250)
        mock_scroll.assert_called_with(3, x=150, y=250)
        
        # Test scroll down
        mock_scroll.reset_mock()
        scroll_down_action = MouseAction(0.5, 'scroll', 150, 250,
                                       scroll_direction='down', scroll_amount=2)
        self.player._execute_action(scroll_down_action)
        mock_scroll.assert_called_with(-2, x=150, y=250)
    
    @patch('pyautogui.moveTo')
    def test_execute_action_with_pyautogui_failsafe(self, mock_move_to):
        """Test handling of PyAutoGUI failsafe exception."""
        # Mock PyAutoGUI failsafe exception
        from pyautogui import FailSafeException
        mock_move_to.side_effect = FailSafeException("Failsafe triggered")
        
        move_action = MouseAction(0.0, 'move', 0, 0)  # Corner position
        
        with self.assertRaises(FailSafeException):
            self.player._execute_action(move_action)
        
        # should_stop should be set
        self.assertTrue(self.player.should_stop)
    
    @patch('time.time')
    def test_timing_during_replay(self, mock_time):
        """Test timing calculations during replay."""
        # Mock time progression
        mock_time.side_effect = [1000.0, 1000.5, 1001.0, 1001.5]
        
        # Create actions with specific timing
        timed_actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.5, 'move', 200, 200),
            MouseAction(1.0, 'move', 300, 300)
        ]
        
        # Test speed multiplier effect
        # At 2x speed, 0.5s delay should become 0.25s
        # At 0.5x speed, 0.5s delay should become 1.0s
        
        # This test verifies the timing calculation logic exists
        # Full replay testing would require more complex mocking
        self.assertTrue(hasattr(self.player, '_replay_sequence'))


class TestPlayerIntegration(unittest.TestCase):
    """Integration tests for the player."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player = ActionPlayer()
    
    def tearDown(self):
        """Clean up after tests."""
        self.player.cleanup()
    
    @patch('pyautogui.moveTo')
    @patch('pyautogui.mouseDown')
    @patch('pyautogui.mouseUp')
    @patch('time.sleep')
    def test_replay_with_mocked_pyautogui(self, mock_sleep, mock_mouse_up, 
                                         mock_mouse_down, mock_move_to):
        """Test replay with mocked PyAutoGUI calls."""
        # Simple actions for testing
        simple_actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.1, 'click', 100, 100, 'left', True),
            MouseAction(0.2, 'click', 100, 100, 'left', False)
        ]
        
        # Mock successful replay
        result = self.player.replay(simple_actions, delay=0.0, speed_multiplier=10.0, start_delay=0.0)
        
        # Should succeed
        self.assertTrue(result)
        
        # Verify PyAutoGUI calls were made
        mock_move_to.assert_called()
        mock_mouse_down.assert_called()
        mock_mouse_up.assert_called()
    
    def test_callback_functionality(self):
        """Test callback functionality."""
        start_called = False
        stop_called = False
        progress_values = []
        
        def on_start():
            nonlocal start_called
            start_called = True
        
        def on_stop():
            nonlocal stop_called
            stop_called = True
        
        def on_progress(progress):
            progress_values.append(progress)
        
        # Set callbacks
        self.player.on_playback_start = on_start
        self.player.on_playback_stop = on_stop
        self.player.on_progress_update = on_progress
        
        # Test callback invocation
        self.player.on_playback_start()
        self.player.on_progress_update(0.5)
        self.player.on_playback_stop()
        
        self.assertTrue(start_called)
        self.assertTrue(stop_called)
        self.assertIn(0.5, progress_values)


class TestPlayerErrorHandling(unittest.TestCase):
    """Test error handling in the player."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player = ActionPlayer()
    
    def tearDown(self):
        """Clean up after tests."""
        self.player.cleanup()
    
    def test_replay_empty_actions(self):
        """Test replaying empty action list."""
        result = self.player.replay([])
        self.assertFalse(result)
    
    def test_replay_while_already_playing(self):
        """Test starting replay while already playing."""
        self.player.is_playing = True
        
        result = self.player.replay([MouseAction(0.0, 'move', 100, 100)])
        self.assertFalse(result)
    
    @patch('pyautogui.moveTo')
    def test_action_execution_error_handling(self, mock_move_to):
        """Test handling of errors during action execution."""
        # Mock an exception during execution
        mock_move_to.side_effect = Exception("Test error")
        
        move_action = MouseAction(0.0, 'move', 100, 100)
        
        # Should raise the exception
        with self.assertRaises(Exception):
            self.player._execute_action(move_action)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)