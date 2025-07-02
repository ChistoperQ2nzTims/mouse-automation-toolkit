"""
Action Player Module

This module provides functionality to replay recorded mouse actions with customizable
timing, speed control, and safety features using PyAutoGUI.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
import pyautogui
from pynput import keyboard


class ActionPlayer:
    """
    Replays recorded mouse actions with timing control and safety features
    """
    
    def __init__(self):
        self.actions: List[Dict[str, Any]] = []
        self.is_playing = False
        self.is_paused = False
        self.should_stop = False
        self.play_thread: Optional[threading.Thread] = None
        self.speed_multiplier = 1.0
        self.loop_mode = False
        self.current_action_index = 0
        self.on_progress_callback: Optional[Callable] = None
        self.on_complete_callback: Optional[Callable] = None
        self.emergency_stop_key = keyboard.Key.esc
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.safe_mode = True
        self.screen_bounds = None
        self.lock = threading.Lock()
        
        # Configure PyAutoGUI safety
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    def set_progress_callback(self, callback: Callable):
        """Set callback function to be called during playback progress"""
        self.on_progress_callback = callback
    
    def set_complete_callback(self, callback: Callable):
        """Set callback function to be called when playback completes"""
        self.on_complete_callback = callback
    
    def load_actions(self, actions: List[Dict[str, Any]]) -> bool:
        """
        Load actions to be played
        
        Args:
            actions (List[Dict]): List of mouse actions
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            self.actions = [action for action in actions if action['type'] == 'click']
            self.current_action_index = 0
            return True
        except Exception as e:
            print(f"Error loading actions: {e}")
            return False
    
    def set_speed(self, speed_multiplier: float):
        """
        Set playback speed multiplier
        
        Args:
            speed_multiplier (float): Speed multiplier (0.1x to 5.0x)
        """
        self.speed_multiplier = max(0.1, min(5.0, speed_multiplier))
    
    def set_loop_mode(self, loop: bool):
        """Enable or disable loop mode"""
        self.loop_mode = loop
    
    def set_safe_mode(self, safe: bool):
        """Enable or disable safe mode (screen boundary checks)"""
        self.safe_mode = safe
    
    def set_screen_bounds(self, width: int, height: int):
        """Set screen bounds for safety checks"""
        self.screen_bounds = (width, height)
    
    def play(self) -> bool:
        """
        Start playing actions
        
        Returns:
            bool: True if playback started successfully, False otherwise
        """
        if self.is_playing or not self.actions:
            return False
        
        try:
            self.is_playing = True
            self.is_paused = False
            self.should_stop = False
            
            # Start emergency stop listener
            self._start_emergency_stop_listener()
            
            # Start playback in separate thread
            self.play_thread = threading.Thread(target=self._play_actions, daemon=True)
            self.play_thread.start()
            
            return True
        except Exception as e:
            print(f"Error starting playback: {e}")
            self.is_playing = False
            return False
    
    def pause(self) -> bool:
        """
        Pause playback
        
        Returns:
            bool: True if paused successfully, False otherwise
        """
        if not self.is_playing:
            return False
        
        self.is_paused = not self.is_paused
        return True
    
    def stop(self) -> bool:
        """
        Stop playback
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if not self.is_playing:
            return False
        
        self.should_stop = True
        self.is_paused = False
        
        # Wait for playback thread to finish
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
        
        self._stop_emergency_stop_listener()
        
        self.is_playing = False
        self.current_action_index = 0
        
        return True
    
    def _start_emergency_stop_listener(self):
        """Start keyboard listener for emergency stop"""
        try:
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press
            )
            self.keyboard_listener.start()
        except Exception as e:
            print(f"Warning: Could not start emergency stop listener: {e}")
    
    def _stop_emergency_stop_listener(self):
        """Stop keyboard listener for emergency stop"""
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            except Exception as e:
                print(f"Warning: Error stopping emergency stop listener: {e}")
    
    def _on_key_press(self, key):
        """Handle emergency stop key press"""
        if key == self.emergency_stop_key:
            print("Emergency stop activated!")
            self.should_stop = True
    
    def _play_actions(self):
        """Main playback loop (runs in separate thread)"""
        try:
            loop_count = 0
            
            while True:
                # Reset action index for new loop
                self.current_action_index = 0
                
                for i, action in enumerate(self.actions):
                    # Check for stop signal
                    if self.should_stop:
                        return
                    
                    # Handle pause
                    while self.is_paused and not self.should_stop:
                        time.sleep(0.1)
                    
                    if self.should_stop:
                        return
                    
                    # Update current action index
                    with self.lock:
                        self.current_action_index = i
                    
                    # Execute action
                    self._execute_action(action)
                    
                    # Calculate delay until next action
                    if i < len(self.actions) - 1:
                        next_action = self.actions[i + 1]
                        delay = (next_action['timestamp'] - action['timestamp']) / self.speed_multiplier
                        
                        # Minimum delay for safety
                        delay = max(0.01, delay)
                        
                        # Sleep with interrupt checking
                        self._interruptible_sleep(delay)
                    
                    # Call progress callback
                    if self.on_progress_callback:
                        try:
                            progress = (i + 1) / len(self.actions)
                            self.on_progress_callback(progress, i + 1, len(self.actions))
                        except Exception as e:
                            print(f"Error in progress callback: {e}")
                
                loop_count += 1
                
                # Check if we should continue looping
                if not self.loop_mode or self.should_stop:
                    break
                
                # Small delay between loops
                self._interruptible_sleep(0.5)
            
            # Playback completed
            if self.on_complete_callback and not self.should_stop:
                try:
                    self.on_complete_callback(loop_count)
                except Exception as e:
                    print(f"Error in complete callback: {e}")
                    
        except Exception as e:
            print(f"Error during playback: {e}")
        finally:
            self.is_playing = False
            self._stop_emergency_stop_listener()
    
    def _execute_action(self, action: Dict[str, Any]):
        """Execute a single mouse action"""
        try:
            x, y = action['x'], action['y']
            button = action.get('button', 'left')
            
            # Safety checks
            if self.safe_mode and self.screen_bounds:
                width, height = self.screen_bounds
                if x < 0 or y < 0 or x >= width or y >= height:
                    print(f"Warning: Skipping action outside screen bounds: ({x}, {y})")
                    return
            
            # Convert button name to PyAutoGUI format
            if button == 'left':
                pyautogui.click(x, y, button='left')
            elif button == 'right':
                pyautogui.click(x, y, button='right')
            elif button == 'middle':
                pyautogui.click(x, y, button='middle')
            else:
                pyautogui.click(x, y, button='left')  # Default to left click
                
        except Exception as e:
            print(f"Error executing action: {e}")
    
    def _interruptible_sleep(self, duration: float):
        """Sleep that can be interrupted by stop signal"""
        end_time = time.time() + duration
        while time.time() < end_time and not self.should_stop:
            sleep_time = min(0.1, end_time - time.time())
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def get_playback_status(self) -> Dict[str, Any]:
        """
        Get current playback status
        
        Returns:
            Dict: Playback status information
        """
        with self.lock:
            total_actions = len(self.actions)
            progress = self.current_action_index / total_actions if total_actions > 0 else 0
            
            return {
                'is_playing': self.is_playing,
                'is_paused': self.is_paused,
                'current_action': self.current_action_index,
                'total_actions': total_actions,
                'progress': progress,
                'speed_multiplier': self.speed_multiplier,
                'loop_mode': self.loop_mode,
                'safe_mode': self.safe_mode
            }
    
    def get_time_remaining(self) -> float:
        """
        Get estimated time remaining for current playback
        
        Returns:
            float: Time remaining in seconds
        """
        if not self.is_playing or not self.actions:
            return 0.0
        
        with self.lock:
            if self.current_action_index >= len(self.actions):
                return 0.0
            
            # Calculate remaining time based on timestamps
            current_action = self.actions[self.current_action_index]
            last_action = self.actions[-1]
            
            remaining_time = (last_action['timestamp'] - current_action['timestamp']) / self.speed_multiplier
            return max(0.0, remaining_time)
    
    def skip_to_action(self, action_index: int) -> bool:
        """
        Skip to a specific action index
        
        Args:
            action_index (int): Index of action to skip to
            
        Returns:
            bool: True if skipped successfully, False otherwise
        """
        if action_index < 0 or action_index >= len(self.actions):
            return False
        
        with self.lock:
            self.current_action_index = action_index
        
        return True
    
    def preview_action(self, action_index: int) -> Optional[Dict[str, Any]]:
        """
        Get preview information for a specific action
        
        Args:
            action_index (int): Index of action to preview
            
        Returns:
            Dict: Action preview information, or None if invalid index
        """
        if action_index < 0 or action_index >= len(self.actions):
            return None
        
        action = self.actions[action_index]
        
        return {
            'index': action_index,
            'type': action['type'],
            'x': action['x'],
            'y': action['y'],
            'button': action.get('button', 'left'),
            'timestamp': action['timestamp'],
            'estimated_time': action['timestamp'] / self.speed_multiplier
        }
    
    def validate_actions(self) -> Dict[str, Any]:
        """
        Validate loaded actions for potential issues
        
        Returns:
            Dict: Validation results
        """
        issues = []
        warnings = []
        
        if not self.actions:
            issues.append("No actions loaded")
            return {'valid': False, 'issues': issues, 'warnings': warnings}
        
        # Check for screen bounds violations
        if self.safe_mode and self.screen_bounds:
            width, height = self.screen_bounds
            out_of_bounds = 0
            for action in self.actions:
                x, y = action['x'], action['y']
                if x < 0 or y < 0 or x >= width or y >= height:
                    out_of_bounds += 1
            
            if out_of_bounds > 0:
                warnings.append(f"{out_of_bounds} actions are outside screen bounds")
        
        # Check for rapid clicks that might cause issues
        rapid_clicks = 0
        for i in range(1, len(self.actions)):
            time_diff = self.actions[i]['timestamp'] - self.actions[i-1]['timestamp']
            if time_diff < 0.05:  # Less than 50ms
                rapid_clicks += 1
        
        if rapid_clicks > 0:
            warnings.append(f"{rapid_clicks} actions have very short intervals")
        
        # Check total duration
        total_duration = self.actions[-1]['timestamp'] if self.actions else 0
        if total_duration > 300:  # More than 5 minutes
            warnings.append(f"Long playback duration: {total_duration:.1f} seconds")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_actions': len(self.actions),
            'duration': total_duration
        }