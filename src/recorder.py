#!/usr/bin/env python3
"""
Mouse Recorder Module

Records mouse clicks and movements with timestamps and coordinates.
Supports hotkey control for starting/stopping recording.
"""

import json
import time
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

try:
    import pynput
    from pynput import mouse, keyboard
except ImportError:
    raise ImportError("pynput is required. Install with: pip install pynput")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MouseAction:
    """Represents a recorded mouse action."""
    timestamp: float
    action_type: str  # 'click', 'move', 'scroll'
    x: int
    y: int
    button: Optional[str] = None  # 'left', 'right', 'middle'
    pressed: Optional[bool] = None  # True for press, False for release
    scroll_direction: Optional[str] = None  # 'up', 'down'
    scroll_amount: Optional[int] = None


class MouseRecorder:
    """
    Records mouse actions with hotkey support.
    
    Features:
    - Record mouse clicks (left, right, middle)
    - Track timing between actions
    - Hotkey support for start/stop recording
    - Save to JSON format
    - Remove duplicate actions
    """
    
    def __init__(self, 
                 start_hotkey: str = '<f9>',
                 stop_hotkey: str = '<f10>',
                 remove_duplicates: bool = True):
        """
        Initialize the mouse recorder.
        
        Args:
            start_hotkey: Hotkey to start recording (default: F9)
            stop_hotkey: Hotkey to stop recording (default: F10)
            remove_duplicates: Whether to remove duplicate consecutive actions
        """
        self.start_hotkey = start_hotkey
        self.stop_hotkey = stop_hotkey
        self.remove_duplicates = remove_duplicates
        
        self.is_recording = False
        self.actions: List[MouseAction] = []
        self.start_time: Optional[float] = None
        
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        
        self.on_recording_start: Optional[Callable] = None
        self.on_recording_stop: Optional[Callable] = None
        
        logger.info(f"MouseRecorder initialized with hotkeys: Start={start_hotkey}, Stop={stop_hotkey}")
    
    def start_recording(self) -> None:
        """Start recording mouse actions."""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return
        
        self.is_recording = True
        self.actions.clear()
        self.start_time = time.time()
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_move=self._on_move,
            on_scroll=self._on_scroll
        )
        self.mouse_listener.start()
        
        logger.info("Mouse recording started")
        if self.on_recording_start:
            self.on_recording_start()
    
    def stop_recording(self) -> List[MouseAction]:
        """
        Stop recording and return recorded actions.
        
        Returns:
            List of recorded mouse actions
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return []
        
        self.is_recording = False
        
        # Stop mouse listener
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        # Process actions if duplicate removal is enabled
        if self.remove_duplicates:
            self.actions = self._remove_duplicate_actions(self.actions)
        
        logger.info(f"Mouse recording stopped. Recorded {len(self.actions)} actions")
        if self.on_recording_stop:
            self.on_recording_stop()
        
        return self.actions.copy()
    
    def start_hotkey_listener(self) -> None:
        """Start listening for hotkeys to control recording."""
        def on_hotkey_press(key):
            try:
                if hasattr(key, 'name'):
                    key_name = f'<{key.name}>'
                else:
                    key_name = str(key)
                
                if key_name == self.start_hotkey:
                    if not self.is_recording:
                        self.start_recording()
                elif key_name == self.stop_hotkey:
                    if self.is_recording:
                        self.stop_recording()
            except Exception as e:
                logger.error(f"Error processing hotkey: {e}")
        
        self.keyboard_listener = keyboard.Listener(on_press=on_hotkey_press)
        self.keyboard_listener.start()
        logger.info(f"Hotkey listener started. Press {self.start_hotkey} to start, {self.stop_hotkey} to stop")
    
    def stop_hotkey_listener(self) -> None:
        """Stop the hotkey listener."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            logger.info("Hotkey listener stopped")
    
    def record(self, duration: Optional[float] = None) -> List[MouseAction]:
        """
        Record mouse actions for a specified duration.
        
        Args:
            duration: Recording duration in seconds. If None, records until stop_recording() is called
            
        Returns:
            List of recorded mouse actions
        """
        self.start_recording()
        
        if duration:
            # Record for specified duration
            time.sleep(duration)
            return self.stop_recording()
        else:
            # Recording continues until manually stopped
            return []
    
    def save_to_file(self, filename: str, actions: Optional[List[MouseAction]] = None) -> None:
        """
        Save recorded actions to a JSON file.
        
        Args:
            filename: Output filename
            actions: Actions to save (uses last recorded if None)
        """
        if actions is None:
            actions = self.actions
        
        if not actions:
            logger.warning("No actions to save")
            return
        
        data = {
            'metadata': {
                'recorded_at': datetime.now().isoformat(),
                'action_count': len(actions),
                'duration': actions[-1].timestamp - actions[0].timestamp if len(actions) > 1 else 0
            },
            'actions': [asdict(action) for action in actions]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Actions saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to file: {e}")
            raise
    
    def load_from_file(self, filename: str) -> List[MouseAction]:
        """
        Load actions from a JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            List of loaded mouse actions
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            actions = []
            for action_data in data['actions']:
                action = MouseAction(**action_data)
                actions.append(action)
            
            logger.info(f"Loaded {len(actions)} actions from {filename}")
            return actions
        except Exception as e:
            logger.error(f"Error loading from file: {e}")
            raise
    
    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """Handle mouse click events."""
        if not self.is_recording:
            return
        
        button_name = button.name if hasattr(button, 'name') else str(button)
        timestamp = time.time() - self.start_time
        
        action = MouseAction(
            timestamp=timestamp,
            action_type='click',
            x=x,
            y=y,
            button=button_name,
            pressed=pressed
        )
        
        self.actions.append(action)
        logger.debug(f"Recorded click: {button_name} {'pressed' if pressed else 'released'} at ({x}, {y})")
    
    def _on_move(self, x: int, y: int) -> None:
        """Handle mouse move events."""
        if not self.is_recording:
            return
        
        # Only record significant movements to avoid too many actions
        if len(self.actions) > 0:
            last_action = self.actions[-1]
            if (last_action.action_type == 'move' and 
                abs(last_action.x - x) < 5 and 
                abs(last_action.y - y) < 5):
                return  # Skip small movements
        
        timestamp = time.time() - self.start_time
        
        action = MouseAction(
            timestamp=timestamp,
            action_type='move',
            x=x,
            y=y
        )
        
        self.actions.append(action)
        logger.debug(f"Recorded move to ({x}, {y})")
    
    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Handle mouse scroll events."""
        if not self.is_recording:
            return
        
        timestamp = time.time() - self.start_time
        
        action = MouseAction(
            timestamp=timestamp,
            action_type='scroll',
            x=x,
            y=y,
            scroll_direction='up' if dy > 0 else 'down',
            scroll_amount=abs(dy)
        )
        
        self.actions.append(action)
        logger.debug(f"Recorded scroll {action.scroll_direction} at ({x}, {y})")
    
    def _remove_duplicate_actions(self, actions: List[MouseAction]) -> List[MouseAction]:
        """Remove duplicate consecutive actions."""
        if len(actions) <= 1:
            return actions
        
        filtered_actions = [actions[0]]
        
        for action in actions[1:]:
            last_action = filtered_actions[-1]
            
            # Skip duplicate moves to same position
            if (action.action_type == 'move' and 
                last_action.action_type == 'move' and
                action.x == last_action.x and 
                action.y == last_action.y):
                continue
            
            filtered_actions.append(action)
        
        removed_count = len(actions) - len(filtered_actions)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate actions")
        
        return filtered_actions
    
    def get_recording_stats(self) -> Dict[str, Any]:
        """Get statistics about the current recording."""
        if not self.actions:
            return {'action_count': 0}
        
        stats = {
            'action_count': len(self.actions),
            'duration': self.actions[-1].timestamp - self.actions[0].timestamp if len(self.actions) > 1 else 0,
            'click_count': len([a for a in self.actions if a.action_type == 'click']),
            'move_count': len([a for a in self.actions if a.action_type == 'move']),
            'scroll_count': len([a for a in self.actions if a.action_type == 'scroll']),
        }
        
        return stats
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.is_recording:
            self.stop_recording()
        
        self.stop_hotkey_listener()
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        logger.info("MouseRecorder cleanup completed")


if __name__ == "__main__":
    # Example usage
    recorder = MouseRecorder()
    
    print("Starting hotkey listener...")
    print("Press F9 to start recording, F10 to stop")
    print("Press Ctrl+C to exit")
    
    recorder.start_hotkey_listener()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        recorder.cleanup()