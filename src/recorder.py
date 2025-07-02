"""
Mouse Recorder Module

Records mouse actions including clicks, positions, timing, and button types.
"""

import time
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pynput import mouse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MouseAction:
    """Represents a single mouse action."""
    
    def __init__(self, action_type: str, x: int, y: int, button: str = None, 
                 timestamp: float = None, delay: float = 0):
        self.action_type = action_type  # 'click', 'press', 'release', 'move'
        self.x = x
        self.y = y
        self.button = button  # 'left', 'right', 'middle'
        self.timestamp = timestamp or time.time()
        self.delay = delay
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary for JSON serialization."""
        return {
            'action_type': self.action_type,
            'x': self.x,
            'y': self.y,
            'button': self.button,
            'timestamp': self.timestamp,
            'delay': self.delay
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MouseAction':
        """Create action from dictionary."""
        return cls(
            action_type=data['action_type'],
            x=data['x'],
            y=data['y'],
            button=data.get('button'),
            timestamp=data.get('timestamp'),
            delay=data.get('delay', 0)
        )


class MouseRecorder:
    """Records mouse actions with timing and smart filtering."""
    
    def __init__(self, smart_recording: bool = True, min_delay: float = 0.1):
        self.actions: List[MouseAction] = []
        self.is_recording = False
        self.smart_recording = smart_recording
        self.min_delay = min_delay
        self.last_action_time = 0
        self.listener = None
        self.callback: Optional[Callable] = None
        self._lock = threading.Lock()
        
    def start_recording(self, callback: Optional[Callable] = None):
        """Start recording mouse actions."""
        if self.is_recording:
            logger.warning("Recording is already active")
            return
            
        self.callback = callback
        self.actions.clear()
        self.is_recording = True
        self.last_action_time = time.time()
        
        # Start mouse listener
        self.listener = mouse.Listener(
            on_click=self._on_click,
            on_move=self._on_move
        )
        self.listener.start()
        logger.info("Mouse recording started")
        
    def stop_recording(self):
        """Stop recording mouse actions."""
        if not self.is_recording:
            logger.warning("Recording is not active")
            return
            
        self.is_recording = False
        if self.listener:
            self.listener.stop()
            self.listener = None
            
        self._calculate_delays()
        logger.info(f"Mouse recording stopped. Recorded {len(self.actions)} actions")
        
    def _on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not self.is_recording:
            return
            
        current_time = time.time()
        action_type = 'press' if pressed else 'release'
        button_name = button.name if hasattr(button, 'name') else str(button)
        
        # Smart recording: filter out duplicate actions
        if self.smart_recording and self._is_duplicate_action(x, y, action_type, button_name):
            return
            
        with self._lock:
            action = MouseAction(
                action_type=action_type,
                x=x,
                y=y,
                button=button_name,
                timestamp=current_time
            )
            self.actions.append(action)
            self.last_action_time = current_time
            
        if self.callback:
            self.callback(action)
            
    def _on_move(self, x, y):
        """Handle mouse move events."""
        if not self.is_recording:
            return
            
        current_time = time.time()
        
        # Only record significant moves to avoid spam
        if current_time - self.last_action_time < self.min_delay:
            return
            
        # Smart recording: only record moves that are significant
        if self.smart_recording:
            if self.actions and abs(x - self.actions[-1].x) < 5 and abs(y - self.actions[-1].y) < 5:
                return
                
        with self._lock:
            action = MouseAction(
                action_type='move',
                x=x,
                y=y,
                timestamp=current_time
            )
            self.actions.append(action)
            self.last_action_time = current_time
            
        if self.callback:
            self.callback(action)
            
    def _is_duplicate_action(self, x, y, action_type, button) -> bool:
        """Check if this action is a duplicate of the last action."""
        if not self.actions:
            return False
            
        last_action = self.actions[-1]
        return (last_action.x == x and 
                last_action.y == y and 
                last_action.action_type == action_type and 
                last_action.button == button)
                
    def _calculate_delays(self):
        """Calculate delays between actions."""
        for i in range(1, len(self.actions)):
            delay = self.actions[i].timestamp - self.actions[i-1].timestamp
            self.actions[i].delay = delay
            
    def save_to_file(self, filename: str):
        """Save recorded actions to JSON file."""
        try:
            data = {
                'metadata': {
                    'recorded_at': datetime.now().isoformat(),
                    'total_actions': len(self.actions),
                    'duration': self.actions[-1].timestamp - self.actions[0].timestamp if self.actions else 0
                },
                'actions': [action.to_dict() for action in self.actions]
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Actions saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to file: {e}")
            raise
            
    def load_from_file(self, filename: str):
        """Load actions from JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            self.actions = [MouseAction.from_dict(action_data) 
                          for action_data in data['actions']]
            
            logger.info(f"Loaded {len(self.actions)} actions from {filename}")
            
        except Exception as e:
            logger.error(f"Error loading from file: {e}")
            raise
            
    def get_actions(self) -> List[MouseAction]:
        """Get the recorded actions."""
        return self.actions.copy()
        
    def clear_actions(self):
        """Clear all recorded actions."""
        with self._lock:
            self.actions.clear()
        logger.info("Actions cleared")