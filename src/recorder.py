"""
Mouse Action Recorder
Records mouse clicks with coordinates, timing, and button types.
"""

import json
import time
from datetime import datetime
from threading import Thread, Event
try:
    from pynput import mouse
except ImportError:
    mouse = None
from typing import List, Dict, Any, Optional


class MouseAction:
    """Represents a single mouse action."""
    
    def __init__(self, x: int, y: int, button: str, timestamp: float, action_type: str = "click"):
        self.x = x
        self.y = y
        self.button = button
        self.timestamp = timestamp
        self.action_type = action_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "button": self.button,
            "timestamp": self.timestamp,
            "action_type": self.action_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MouseAction":
        """Create MouseAction from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            button=data["button"],
            timestamp=data["timestamp"],
            action_type=data.get("action_type", "click")
        )


class MouseRecorder:
    """Records mouse actions and saves them to JSON files."""
    
    def __init__(self):
        self.actions: List[MouseAction] = []
        self.is_recording = False
        self.recording_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.start_time: Optional[float] = None
        self.listener: Optional[mouse.Listener] = None
    
    def start_recording(self) -> None:
        """Start recording mouse actions."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.actions.clear()
        self.stop_event.clear()
        self.start_time = time.time()
        
        # Start mouse listener
        if mouse:
            self.listener = mouse.Listener(on_click=self._on_click)
            self.listener.start()
        else:
            print("Warning: pynput not available, using mock recording")
        
        print("Recording started. Click anywhere to record actions.")
    
    def stop_recording(self) -> None:
        """Stop recording mouse actions."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.stop_event.set()
        
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        print(f"Recording stopped. Recorded {len(self.actions)} actions.")
    
    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:
        """Handle mouse click events."""
        if not self.is_recording or not pressed:
            return
        
        # Convert button to string
        button_str = self._button_to_string(button)
        
        # Calculate relative timestamp
        current_time = time.time()
        relative_time = current_time - self.start_time if self.start_time else 0
        
        # Create and store action
        action = MouseAction(x, y, button_str, relative_time)
        self.actions.append(action)
        
        print(f"Recorded: {button_str} click at ({x}, {y}) at {relative_time:.2f}s")
    
    def _button_to_string(self, button) -> str:
        """Convert pynput button to string."""
        if not mouse:
            return "left"  # Default for mock mode
            
        if button == mouse.Button.left:
            return "left"
        elif button == mouse.Button.right:
            return "right"
        elif button == mouse.Button.middle:
            return "middle"
        else:
            return "unknown"
    
    def save_to_file(self, filename: str, include_metadata: bool = True) -> None:
        """Save recorded actions to JSON file."""
        data = {
            "actions": [action.to_dict() for action in self.actions],
        }
        
        if include_metadata:
            data["metadata"] = {
                "created_at": datetime.now().isoformat(),
                "total_actions": len(self.actions),
                "total_duration": self.actions[-1].timestamp if self.actions else 0,
                "version": "1.0.0"
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Actions saved to {filename}")
    
    def load_from_file(self, filename: str) -> None:
        """Load actions from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.actions = [MouseAction.from_dict(action_data) 
                          for action_data in data["actions"]]
            
            print(f"Loaded {len(self.actions)} actions from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found.")
        except json.JSONDecodeError:
            print(f"Invalid JSON in file {filename}")
        except KeyError:
            print(f"Invalid file format in {filename}")
    
    def get_actions(self) -> List[MouseAction]:
        """Get the list of recorded actions."""
        return self.actions.copy()
    
    def clear_actions(self) -> None:
        """Clear all recorded actions."""
        self.actions.clear()
        print("All actions cleared.")
    
    def remove_duplicate_actions(self, tolerance: float = 0.1) -> int:
        """Remove duplicate actions that occur within tolerance seconds."""
        if len(self.actions) <= 1:
            return 0
        
        filtered_actions = [self.actions[0]]
        removed_count = 0
        
        for i in range(1, len(self.actions)):
            current = self.actions[i]
            previous = filtered_actions[-1]
            
            # Check if actions are too close in time and position
            time_diff = abs(current.timestamp - previous.timestamp)
            pos_diff = abs(current.x - previous.x) + abs(current.y - previous.y)
            
            if time_diff > tolerance or pos_diff > 5 or current.button != previous.button:
                filtered_actions.append(current)
            else:
                removed_count += 1
        
        self.actions = filtered_actions
        print(f"Removed {removed_count} duplicate actions.")
        return removed_count