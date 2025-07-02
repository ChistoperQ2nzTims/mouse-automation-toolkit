"""
Mouse Player Module

Handles playback of recorded mouse actions with various options.
"""

import time
import random
import threading
from typing import List, Optional, Callable
import pyautogui
import logging

from .recorder import MouseAction

logger = logging.getLogger(__name__)

# Configure PyAutoGUI
pyautogui.FAILSAFE = True  # Enable failsafe (move mouse to corner to stop)
pyautogui.PAUSE = 0.1  # Default pause between actions


class MousePlayer:
    """Plays back recorded mouse actions with various playback options."""
    
    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        self.stop_requested = False
        self.current_action_index = 0
        self.total_actions = 0
        self.playback_thread = None
        self.progress_callback: Optional[Callable] = None
        self.completion_callback: Optional[Callable] = None
        
    def play_actions(self, actions: List[MouseAction], 
                    delay_multiplier: float = 1.0,
                    random_delay: bool = False,
                    loop_count: int = 1,
                    progress_callback: Optional[Callable] = None,
                    completion_callback: Optional[Callable] = None):
        """
        Play back mouse actions.
        
        Args:
            actions: List of actions to play
            delay_multiplier: Multiplier for delays between actions
            random_delay: Whether to add random variation to delays
            loop_count: Number of times to repeat the sequence (0 for infinite)
            progress_callback: Called with progress info (current_action, total_actions)
            completion_callback: Called when playback completes
        """
        if self.is_playing:
            logger.warning("Playback is already active")
            return
            
        if not actions:
            logger.warning("No actions to play")
            return
            
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.stop_requested = False
        
        # Start playback in separate thread
        self.playback_thread = threading.Thread(
            target=self._playback_worker,
            args=(actions, delay_multiplier, random_delay, loop_count)
        )
        self.playback_thread.start()
        
    def _playback_worker(self, actions: List[MouseAction], 
                        delay_multiplier: float,
                        random_delay: bool,
                        loop_count: int):
        """Worker method for playback thread."""
        try:
            self.is_playing = True
            self.current_action_index = 0
            self.total_actions = len(actions) * (loop_count if loop_count > 0 else 1)
            
            loops_completed = 0
            
            while not self.stop_requested:
                # Play the sequence once
                for i, action in enumerate(actions):
                    if self.stop_requested:
                        break
                        
                    # Handle pause
                    while self.is_paused and not self.stop_requested:
                        time.sleep(0.1)
                        
                    if self.stop_requested:
                        break
                        
                    self.current_action_index = i + (loops_completed * len(actions))
                    
                    # Execute the action
                    self._execute_action(action)
                    
                    # Update progress
                    if self.progress_callback:
                        self.progress_callback(self.current_action_index + 1, self.total_actions)
                    
                    # Apply delay
                    if i < len(actions) - 1:  # Don't delay after last action
                        delay = action.delay * delay_multiplier
                        
                        if random_delay and delay > 0:
                            # Add random variation (±25%)
                            variation = delay * 0.25
                            delay += random.uniform(-variation, variation)
                            
                        if delay > 0:
                            time.sleep(max(0, delay))
                            
                loops_completed += 1
                
                # Check loop condition
                if loop_count > 0 and loops_completed >= loop_count:
                    break
                    
        except Exception as e:
            logger.error(f"Error during playback: {e}")
            
        finally:
            self.is_playing = False
            self.is_paused = False
            
            if self.completion_callback and not self.stop_requested:
                self.completion_callback()
                
            logger.info("Playback completed")
            
    def _execute_action(self, action: MouseAction):
        """Execute a single mouse action."""
        try:
            if action.action_type == 'move':
                pyautogui.moveTo(action.x, action.y)
                
            elif action.action_type == 'click':
                button_map = {
                    'left': 'left',
                    'right': 'right',
                    'middle': 'middle'
                }
                button = button_map.get(action.button, 'left')
                pyautogui.click(action.x, action.y, button=button)
                
            elif action.action_type == 'press':
                button_map = {
                    'left': 'left',
                    'right': 'right', 
                    'middle': 'middle'
                }
                button = button_map.get(action.button, 'left')
                pyautogui.mouseDown(action.x, action.y, button=button)
                
            elif action.action_type == 'release':
                button_map = {
                    'left': 'left',
                    'right': 'right',
                    'middle': 'middle'
                }
                button = button_map.get(action.button, 'left')
                pyautogui.mouseUp(action.x, action.y, button=button)
                
        except Exception as e:
            logger.error(f"Error executing action {action.action_type}: {e}")
            
    def pause_playback(self):
        """Pause the current playback."""
        if self.is_playing:
            self.is_paused = True
            logger.info("Playback paused")
            
    def resume_playback(self):
        """Resume paused playback."""
        if self.is_playing and self.is_paused:
            self.is_paused = False
            logger.info("Playback resumed")
            
    def stop_playback(self):
        """Stop the current playback."""
        if self.is_playing:
            self.stop_requested = True
            logger.info("Playback stop requested")
            
            # Wait for thread to finish
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=5.0)
                
    def get_playback_status(self) -> dict:
        """Get current playback status."""
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_action': self.current_action_index + 1,
            'total_actions': self.total_actions,
            'progress_percentage': (self.current_action_index + 1) / self.total_actions * 100 if self.total_actions > 0 else 0
        }
        
    def preview_actions(self, actions: List[MouseAction]) -> List[dict]:
        """
        Preview actions without executing them.
        
        Args:
            actions: List of actions to preview
            
        Returns:
            List of action summaries
        """
        preview = []
        
        for i, action in enumerate(actions):
            preview.append({
                'index': i + 1,
                'action_type': action.action_type,
                'position': f"({action.x}, {action.y})",
                'button': action.button or 'N/A',
                'delay': f"{action.delay:.3f}s" if action.delay > 0 else 'N/A'
            })
            
        return preview
        
    def validate_actions(self, actions: List[MouseAction]) -> List[str]:
        """
        Validate actions and return list of warnings/issues.
        
        Args:
            actions: List of actions to validate
            
        Returns:
            List of validation warnings
        """
        warnings = []
        screen_width, screen_height = pyautogui.size()
        
        for i, action in enumerate(actions):
            # Check coordinates are within screen bounds
            if action.x < 0 or action.x >= screen_width:
                warnings.append(f"Action {i+1}: X coordinate {action.x} is outside screen bounds (0-{screen_width-1})")
                
            if action.y < 0 or action.y >= screen_height:
                warnings.append(f"Action {i+1}: Y coordinate {action.y} is outside screen bounds (0-{screen_height-1})")
                
            # Check for very long delays
            if action.delay > 10:
                warnings.append(f"Action {i+1}: Very long delay ({action.delay:.1f}s)")
                
            # Check for unknown button types
            if action.button and action.button not in ['left', 'right', 'middle']:
                warnings.append(f"Action {i+1}: Unknown button type '{action.button}'")
                
        return warnings
        
    def get_estimated_duration(self, actions: List[MouseAction], 
                              delay_multiplier: float = 1.0) -> float:
        """
        Estimate total playback duration.
        
        Args:
            actions: List of actions
            delay_multiplier: Delay multiplier to apply
            
        Returns:
            Estimated duration in seconds
        """
        if not actions:
            return 0.0
            
        total_delay = sum(action.delay for action in actions)
        estimated_execution_time = len(actions) * 0.05  # Estimate 50ms per action
        
        return (total_delay * delay_multiplier) + estimated_execution_time
        
    def set_failsafe(self, enabled: bool):
        """Enable or disable PyAutoGUI failsafe."""
        pyautogui.FAILSAFE = enabled
        logger.info(f"Failsafe {'enabled' if enabled else 'disabled'}")
        
    def set_pause_duration(self, pause: float):
        """Set default pause between PyAutoGUI actions."""
        pyautogui.PAUSE = pause
        logger.info(f"Default pause set to {pause}s")