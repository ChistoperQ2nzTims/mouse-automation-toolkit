#!/usr/bin/env python3
"""
Action Player Module

Replays recorded mouse actions with safety features and customizable settings.
Supports loop playback, emergency stops, and progress tracking.
"""

import time
import threading
from typing import List, Optional, Callable, Dict, Any
import logging

try:
    import pyautogui
    # Configure PyAutoGUI safety features
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    raise ImportError("pyautogui is required. Install with: pip install pyautogui")

try:
    from pynput import keyboard
except ImportError:
    raise ImportError("pynput is required. Install with: pip install pynput")

from .recorder import MouseAction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionPlayer:
    """
    Replays recorded mouse actions with safety features.
    
    Features:
    - Replay recorded actions with custom delays
    - Loop playback support
    - ESC hotkey emergency stop
    - Progress tracking and callbacks
    - Safe mode with fail-safes
    - Speed control and timing adjustment
    """
    
    def __init__(self, 
                 emergency_stop_key: str = 'esc',
                 failsafe_enabled: bool = True,
                 default_pause: float = 0.1):
        """
        Initialize the action player.
        
        Args:
            emergency_stop_key: Key to stop playback immediately (default: ESC)
            failsafe_enabled: Enable PyAutoGUI failsafe (mouse to corner stops)
            default_pause: Default pause between PyAutoGUI actions
        """
        self.emergency_stop_key = emergency_stop_key
        self.failsafe_enabled = failsafe_enabled
        self.default_pause = default_pause
        
        self.is_playing = False
        self.should_stop = False
        self.current_action_index = 0
        self.total_actions = 0
        
        self.keyboard_listener: Optional[keyboard.Listener] = None
        
        # Callbacks
        self.on_playback_start: Optional[Callable] = None
        self.on_playback_stop: Optional[Callable] = None
        self.on_action_executed: Optional[Callable[[int, MouseAction], None]] = None
        self.on_progress_update: Optional[Callable[[float], None]] = None
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = failsafe_enabled
        pyautogui.PAUSE = default_pause
        
        logger.info(f"ActionPlayer initialized with emergency stop: {emergency_stop_key}")
    
    def replay(self, 
               actions: List[MouseAction], 
               delay: float = 0.0,
               speed_multiplier: float = 1.0,
               loop_count: int = 1,
               start_delay: float = 3.0) -> bool:
        """
        Replay a list of mouse actions.
        
        Args:
            actions: List of mouse actions to replay
            delay: Additional delay between actions (seconds)
            speed_multiplier: Speed multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)
            loop_count: Number of times to repeat the sequence (0 = infinite)
            start_delay: Delay before starting playback (seconds)
            
        Returns:
            True if playback completed successfully, False if stopped
        """
        if not actions:
            logger.warning("No actions to replay")
            return False
        
        if self.is_playing:
            logger.warning("Playback already in progress")
            return False
        
        self.is_playing = True
        self.should_stop = False
        self.total_actions = len(actions)
        
        logger.info(f"Starting playback of {len(actions)} actions with {start_delay}s delay")
        
        # Start emergency stop listener
        self._start_emergency_listener()
        
        if self.on_playback_start:
            self.on_playback_start()
        
        try:
            # Initial delay
            if start_delay > 0:
                logger.info(f"Waiting {start_delay}s before starting playback...")
                if self._wait_interruptible(start_delay):
                    return False
            
            loops_completed = 0
            while loop_count == 0 or loops_completed < loop_count:
                if self.should_stop:
                    break
                
                success = self._replay_sequence(actions, delay, speed_multiplier)
                if not success:
                    break
                
                loops_completed += 1
                
                if loop_count > 1 or loop_count == 0:
                    logger.info(f"Completed loop {loops_completed}")
            
            logger.info(f"Playback completed successfully. Loops: {loops_completed}")
            return True
            
        except Exception as e:
            logger.error(f"Error during playback: {e}")
            return False
        
        finally:
            self.is_playing = False
            self._stop_emergency_listener()
            
            if self.on_playback_stop:
                self.on_playback_stop()
    
    def stop_playback(self) -> None:
        """Stop the current playback."""
        if self.is_playing:
            self.should_stop = True
            logger.info("Playback stop requested")
    
    def pause_playback(self, duration: float) -> None:
        """
        Pause playback for a specified duration.
        
        Args:
            duration: Pause duration in seconds
        """
        if self.is_playing:
            logger.info(f"Pausing playback for {duration}s")
            self._wait_interruptible(duration)
    
    def get_playback_progress(self) -> Dict[str, Any]:
        """
        Get current playback progress information.
        
        Returns:
            Dictionary with progress information
        """
        if not self.is_playing:
            return {
                'is_playing': False,
                'progress_percent': 0,
                'current_action': 0,
                'total_actions': 0
            }
        
        progress_percent = (self.current_action_index / self.total_actions * 100) if self.total_actions > 0 else 0
        
        return {
            'is_playing': self.is_playing,
            'progress_percent': progress_percent,
            'current_action': self.current_action_index,
            'total_actions': self.total_actions
        }
    
    def replay_async(self, 
                    actions: List[MouseAction], 
                    delay: float = 0.0,
                    speed_multiplier: float = 1.0,
                    loop_count: int = 1,
                    start_delay: float = 3.0) -> threading.Thread:
        """
        Start playback in a separate thread.
        
        Args:
            actions: List of mouse actions to replay
            delay: Additional delay between actions (seconds)
            speed_multiplier: Speed multiplier
            loop_count: Number of loops
            start_delay: Delay before starting
            
        Returns:
            Thread object for the playback
        """
        def replay_worker():
            self.replay(actions, delay, speed_multiplier, loop_count, start_delay)
        
        thread = threading.Thread(target=replay_worker, daemon=True)
        thread.start()
        return thread
    
    def validate_actions(self, actions: List[MouseAction]) -> Dict[str, Any]:
        """
        Validate actions before playback and provide safety warnings.
        
        Args:
            actions: List of actions to validate
            
        Returns:
            Dictionary with validation results and warnings
        """
        if not actions:
            return {'valid': False, 'error': 'No actions provided'}
        
        warnings = []
        errors = []
        
        # Get screen size for boundary checking
        try:
            screen_width, screen_height = pyautogui.size()
        except Exception as e:
            warnings.append(f"Could not get screen size: {e}")
            screen_width = screen_height = float('inf')
        
        # Check each action
        for i, action in enumerate(actions):
            # Check coordinates are within screen bounds
            if action.x < 0 or action.x > screen_width:
                warnings.append(f"Action {i}: X coordinate {action.x} outside screen bounds (0-{screen_width})")
            
            if action.y < 0 or action.y > screen_height:
                warnings.append(f"Action {i}: Y coordinate {action.y} outside screen bounds (0-{screen_height})")
            
            # Check for actions at screen corners (failsafe triggers)
            if self.failsafe_enabled:
                corner_threshold = 10
                if ((action.x < corner_threshold or action.x > screen_width - corner_threshold) and
                    (action.y < corner_threshold or action.y > screen_height - corner_threshold)):
                    warnings.append(f"Action {i}: Near screen corner - may trigger failsafe")
            
            # Check for extremely rapid actions
            if i > 0:
                time_diff = action.timestamp - actions[i-1].timestamp
                if time_diff < 0.01:  # Less than 10ms
                    warnings.append(f"Action {i}: Very rapid execution (< 10ms from previous)")
        
        # Check total duration
        if len(actions) > 1:
            total_duration = actions[-1].timestamp - actions[0].timestamp
            if total_duration > 300:  # More than 5 minutes
                warnings.append(f"Long playback duration: {total_duration:.1f} seconds")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'action_count': len(actions),
            'estimated_duration': actions[-1].timestamp - actions[0].timestamp if len(actions) > 1 else 0
        }
    
    def _replay_sequence(self, 
                        actions: List[MouseAction], 
                        delay: float, 
                        speed_multiplier: float) -> bool:
        """Replay a single sequence of actions."""
        self.current_action_index = 0
        start_time = time.time()
        
        for i, action in enumerate(actions):
            if self.should_stop:
                logger.info("Playback stopped by user")
                return False
            
            self.current_action_index = i
            
            # Calculate timing
            if i == 0:
                # First action - no wait
                pass
            else:
                # Wait for the appropriate time based on original timing
                original_delay = action.timestamp - actions[i-1].timestamp
                adjusted_delay = original_delay / speed_multiplier + delay
                
                if adjusted_delay > 0:
                    if self._wait_interruptible(adjusted_delay):
                        return False
            
            # Execute the action
            try:
                self._execute_action(action)
                
                if self.on_action_executed:
                    self.on_action_executed(i, action)
                
                # Update progress
                if self.on_progress_update:
                    progress = (i + 1) / len(actions)
                    self.on_progress_update(progress)
                
            except Exception as e:
                logger.error(f"Error executing action {i}: {e}")
                # Continue with next action rather than stopping completely
        
        self.current_action_index = len(actions)
        return True
    
    def _execute_action(self, action: MouseAction) -> None:
        """Execute a single mouse action."""
        try:
            if action.action_type == 'click':
                if action.pressed:
                    # Mouse press
                    button_map = {'left': 'left', 'right': 'right', 'middle': 'middle'}
                    button = button_map.get(action.button, 'left')
                    pyautogui.mouseDown(action.x, action.y, button=button)
                    logger.debug(f"Mouse press: {action.button} at ({action.x}, {action.y})")
                else:
                    # Mouse release
                    button_map = {'left': 'left', 'right': 'right', 'middle': 'middle'}
                    button = button_map.get(action.button, 'left')
                    pyautogui.mouseUp(action.x, action.y, button=button)
                    logger.debug(f"Mouse release: {action.button} at ({action.x}, {action.y})")
            
            elif action.action_type == 'move':
                pyautogui.moveTo(action.x, action.y)
                logger.debug(f"Mouse move to ({action.x}, {action.y})")
            
            elif action.action_type == 'scroll':
                # Move to position first
                pyautogui.moveTo(action.x, action.y)
                
                # Determine scroll direction and amount
                scroll_amount = action.scroll_amount or 1
                if action.scroll_direction == 'up':
                    pyautogui.scroll(scroll_amount, x=action.x, y=action.y)
                else:
                    pyautogui.scroll(-scroll_amount, x=action.x, y=action.y)
                
                logger.debug(f"Mouse scroll {action.scroll_direction} at ({action.x}, {action.y})")
            
        except pyautogui.FailSafeException:
            logger.warning("PyAutoGUI failsafe triggered - stopping playback")
            self.should_stop = True
            raise
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            raise
    
    def _wait_interruptible(self, duration: float) -> bool:
        """
        Wait for a duration while checking for stop signals.
        
        Args:
            duration: Time to wait in seconds
            
        Returns:
            True if interrupted, False if completed normally
        """
        end_time = time.time() + duration
        
        while time.time() < end_time:
            if self.should_stop:
                return True
            time.sleep(0.01)  # Check every 10ms
        
        return False
    
    def _start_emergency_listener(self) -> None:
        """Start listening for emergency stop key."""
        def on_key_press(key):
            try:
                if hasattr(key, 'name') and key.name == self.emergency_stop_key:
                    logger.info(f"Emergency stop triggered ({self.emergency_stop_key})")
                    self.stop_playback()
            except AttributeError:
                # Handle special keys
                if str(key) == f"Key.{self.emergency_stop_key}":
                    logger.info(f"Emergency stop triggered ({self.emergency_stop_key})")
                    self.stop_playback()
        
        self.keyboard_listener = keyboard.Listener(on_press=on_key_press)
        self.keyboard_listener.start()
        logger.debug("Emergency stop listener started")
    
    def _stop_emergency_listener(self) -> None:
        """Stop the emergency stop listener."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            logger.debug("Emergency stop listener stopped")
    
    def create_click_action(self, x: int, y: int, button: str = 'left') -> List[MouseAction]:
        """
        Create a simple click action (press + release).
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            
        Returns:
            List containing press and release actions
        """
        return [
            MouseAction(0.0, 'click', x, y, button, True),
            MouseAction(0.1, 'click', x, y, button, False)
        ]
    
    def create_drag_action(self, 
                          start_x: int, start_y: int, 
                          end_x: int, end_y: int, 
                          duration: float = 1.0,
                          button: str = 'left') -> List[MouseAction]:
        """
        Create a drag action sequence.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of the drag in seconds
            button: Mouse button to use
            
        Returns:
            List of actions for the drag sequence
        """
        actions = []
        
        # Mouse press at start
        actions.append(MouseAction(0.0, 'click', start_x, start_y, button, True))
        
        # Intermediate move actions
        steps = max(abs(end_x - start_x), abs(end_y - start_y)) // 10  # One action per 10 pixels
        steps = max(steps, 2)  # At least 2 intermediate steps
        
        for i in range(1, steps):
            progress = i / steps
            x = int(start_x + (end_x - start_x) * progress)
            y = int(start_y + (end_y - start_y) * progress)
            timestamp = duration * progress
            actions.append(MouseAction(timestamp, 'move', x, y))
        
        # Final move to end position
        actions.append(MouseAction(duration * 0.9, 'move', end_x, end_y))
        
        # Mouse release at end
        actions.append(MouseAction(duration, 'click', end_x, end_y, button, False))
        
        return actions
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.is_playing:
            self.stop_playback()
        
        self._stop_emergency_listener()
        logger.info("ActionPlayer cleanup completed")


if __name__ == "__main__":
    # Example usage
    from .recorder import MouseAction
    
    # Create sample actions
    actions = [
        MouseAction(0.0, 'move', 100, 100),
        MouseAction(0.5, 'click', 100, 100, 'left', True),
        MouseAction(0.6, 'click', 100, 100, 'left', False),
        MouseAction(1.0, 'move', 200, 200),
        MouseAction(1.5, 'click', 200, 200, 'left', True),
        MouseAction(1.6, 'click', 200, 200, 'left', False),
    ]
    
    player = ActionPlayer()
    
    print("Validating actions...")
    validation = player.validate_actions(actions)
    print(f"Valid: {validation['valid']}")
    if validation['warnings']:
        print("Warnings:", validation['warnings'])
    
    print("Starting playback in 3 seconds...")
    print("Press ESC to stop")
    
    try:
        success = player.replay(actions, delay=0.5, start_delay=3.0)
        print(f"Playback {'completed' if success else 'stopped'}")
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        player.cleanup()