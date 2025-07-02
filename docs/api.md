# API Documentation

This document provides complete API reference for the Mouse Automation Toolkit.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Data Structures](#data-structures)
3. [Recording Module](#recording-module)
4. [Transformation Module](#transformation-module)
5. [Playback Module](#playback-module)
6. [GUI Module](#gui-module)
7. [Error Handling](#error-handling)
8. [Configuration](#configuration)

## Core Classes

### MouseAction

**Description**: Represents a single mouse action with timing and coordinate information.

```python
@dataclass
class MouseAction:
    timestamp: float
    action_type: str  # 'click', 'move', 'scroll'
    x: int
    y: int
    button: Optional[str] = None  # 'left', 'right', 'middle'
    pressed: Optional[bool] = None  # True for press, False for release
    scroll_direction: Optional[str] = None  # 'up', 'down'
    scroll_amount: Optional[int] = None
```

**Fields**:
- `timestamp`: Time offset from recording start (seconds)
- `action_type`: Type of mouse action performed
- `x`, `y`: Screen coordinates
- `button`: Mouse button for click actions
- `pressed`: Whether button was pressed (True) or released (False)
- `scroll_direction`: Direction of scroll action
- `scroll_amount`: Amount of scroll (wheel clicks)

## Recording Module

### MouseRecorder

**Description**: Records mouse actions with hotkey support and timing information.

#### Constructor

```python
def __init__(self, 
             start_hotkey: str = '<f9>',
             stop_hotkey: str = '<f10>',
             remove_duplicates: bool = True)
```

**Parameters**:
- `start_hotkey`: Hotkey to start recording (default: F9)
- `stop_hotkey`: Hotkey to stop recording (default: F10)
- `remove_duplicates`: Remove consecutive duplicate actions

#### Methods

##### start_recording()

```python
def start_recording(self) -> None
```

Start recording mouse actions immediately.

##### stop_recording()

```python
def stop_recording(self) -> List[MouseAction]
```

Stop recording and return all recorded actions.

**Returns**: List of MouseAction objects

##### record()

```python
def record(self, duration: Optional[float] = None) -> List[MouseAction]
```

Record for a specified duration or until manually stopped.

**Parameters**:
- `duration`: Recording duration in seconds (None = manual stop)

**Returns**: List of recorded actions

##### save_to_file()

```python
def save_to_file(self, filename: str, actions: Optional[List[MouseAction]] = None) -> None
```

Save actions to JSON file.

**Parameters**:
- `filename`: Output filename
- `actions`: Actions to save (uses current if None)

##### load_from_file()

```python
def load_from_file(self, filename: str) -> List[MouseAction]
```

Load actions from JSON file.

**Parameters**:
- `filename`: Input filename

**Returns**: List of loaded actions

##### start_hotkey_listener() / stop_hotkey_listener()

```python
def start_hotkey_listener(self) -> None
def stop_hotkey_listener(self) -> None
```

Start/stop listening for hotkeys to control recording.

##### get_recording_stats()

```python
def get_recording_stats(self) -> Dict[str, Any]
```

Get statistics about current recording.

**Returns**: Dictionary with action counts and duration

#### Properties

- `is_recording`: Boolean indicating if recording is active
- `actions`: List of currently recorded actions
- `on_recording_start`: Callback function for recording start
- `on_recording_stop`: Callback function for recording stop

#### Example Usage

```python
from src.recorder import MouseRecorder

recorder = MouseRecorder()

# Method 1: Timed recording
actions = recorder.record(duration=10.0)

# Method 2: Hotkey controlled
recorder.start_hotkey_listener()
# User presses F9 to start, F10 to stop

# Method 3: Manual control
recorder.start_recording()
# ... perform actions ...
actions = recorder.stop_recording()

# Save to file
recorder.save_to_file("my_actions.json", actions)

# Clean up
recorder.cleanup()
```

## Transformation Module

### CoordinateTransformer

**Description**: Transforms mouse action coordinates using various mathematical operations.

#### Constructor

```python
def __init__(self)
```

#### Basic Transformations

##### translate()

```python
def translate(self, actions: List[MouseAction], offset_x: float, offset_y: float) -> List[MouseAction]
```

Move all coordinates by fixed offset.

**Parameters**:
- `actions`: Actions to transform
- `offset_x`: X-axis offset
- `offset_y`: Y-axis offset

##### scale()

```python
def scale(self, actions: List[MouseAction], scale_x: float, scale_y: float, 
          center_x: Optional[float] = None, center_y: Optional[float] = None) -> List[MouseAction]
```

Scale coordinates around center point.

**Parameters**:
- `actions`: Actions to transform
- `scale_x`, `scale_y`: Scale factors
- `center_x`, `center_y`: Center point (auto-calculated if None)

##### rotate()

```python
def rotate(self, actions: List[MouseAction], angle_degrees: float,
           center_x: Optional[float] = None, center_y: Optional[float] = None) -> List[MouseAction]
```

Rotate coordinates around center point.

**Parameters**:
- `actions`: Actions to transform
- `angle_degrees`: Rotation angle in degrees (positive = clockwise)
- `center_x`, `center_y`: Rotation center (auto-calculated if None)

##### mirror_horizontal() / mirror_vertical()

```python
def mirror_horizontal(self, actions: List[MouseAction], axis_x: Optional[float] = None) -> List[MouseAction]
def mirror_vertical(self, actions: List[MouseAction], axis_y: Optional[float] = None) -> List[MouseAction]
```

Mirror coordinates around horizontal or vertical axis.

#### Advanced Transformations

##### apply_matrix_transform()

```python
def apply_matrix_transform(self, actions: List[MouseAction], 
                          transformation_matrix: np.ndarray) -> List[MouseAction]
```

Apply custom 2D transformation matrix.

**Parameters**:
- `actions`: Actions to transform
- `transformation_matrix`: 3x3 transformation matrix for homogeneous coordinates

##### chain_transforms()

```python
def chain_transforms(self, actions: List[MouseAction], 
                    transforms: List[Dict[str, Any]]) -> List[MouseAction]
```

Apply multiple transformations in sequence.

**Parameters**:
- `actions`: Actions to transform
- `transforms`: List of transformation dictionaries

**Transform Dictionary Format**:
```python
[
    {'type': 'translate', 'offset_x': 100, 'offset_y': 50},
    {'type': 'scale', 'scale_x': 1.5, 'scale_y': 1.5},
    {'type': 'rotate', 'angle_degrees': 45},
    {'type': 'mirror_horizontal'},
    {'type': 'mirror_vertical'}
]
```

##### fit_to_screen()

```python
def fit_to_screen(self, actions: List[MouseAction], screen_width: int, screen_height: int,
                  maintain_aspect_ratio: bool = True, margin: int = 10) -> List[MouseAction]
```

Scale and translate actions to fit screen bounds.

**Parameters**:
- `actions`: Actions to transform
- `screen_width`, `screen_height`: Target screen dimensions
- `maintain_aspect_ratio`: Preserve aspect ratio during scaling
- `margin`: Margin from screen edges

##### normalize_timing()

```python
def normalize_timing(self, actions: List[MouseAction], total_duration: float) -> List[MouseAction]
```

Adjust action timing to fit specific duration.

**Parameters**:
- `actions`: Actions to transform
- `total_duration`: Target total duration in seconds

#### Utility Methods

##### get_transformation_info()

```python
def get_transformation_info(self, original_actions: List[MouseAction], 
                           transformed_actions: List[MouseAction]) -> Dict[str, Any]
```

Get statistics about applied transformation.

**Returns**: Dictionary with bounds, center shift, scale factors, and area ratio

#### Example Usage

```python
from src.transformer import CoordinateTransformer

transformer = CoordinateTransformer()

# Basic transformations
translated = transformer.translate(actions, 100, 50)
scaled = transformer.scale(actions, 1.5, 1.5)
rotated = transformer.rotate(actions, 45)

# Chained transformations
transforms = [
    {'type': 'translate', 'offset_x': 50, 'offset_y': 25},
    {'type': 'scale', 'scale_x': 1.2, 'scale_y': 1.2},
    {'type': 'rotate', 'angle_degrees': 30}
]
result = transformer.chain_transforms(actions, transforms)

# Fit to screen
fitted = transformer.fit_to_screen(actions, 1920, 1080, maintain_aspect_ratio=True)
```

## Playback Module

### ActionPlayer

**Description**: Replays mouse actions with safety features and customizable timing.

#### Constructor

```python
def __init__(self, emergency_stop_key: str = 'esc', failsafe_enabled: bool = True, 
             default_pause: float = 0.1)
```

**Parameters**:
- `emergency_stop_key`: Key to stop playback immediately
- `failsafe_enabled`: Enable PyAutoGUI failsafe
- `default_pause`: Default pause between actions

#### Playback Methods

##### replay()

```python
def replay(self, actions: List[MouseAction], delay: float = 0.0, 
           speed_multiplier: float = 1.0, loop_count: int = 1, 
           start_delay: float = 3.0) -> bool
```

Replay mouse actions with specified settings.

**Parameters**:
- `actions`: Actions to replay
- `delay`: Additional delay between actions
- `speed_multiplier`: Speed multiplier (1.0 = normal, 2.0 = double speed)
- `loop_count`: Number of repetitions (0 = infinite)
- `start_delay`: Countdown before starting

**Returns**: True if completed successfully, False if stopped

##### replay_async()

```python
def replay_async(self, actions: List[MouseAction], delay: float = 0.0,
                speed_multiplier: float = 1.0, loop_count: int = 1,
                start_delay: float = 3.0) -> threading.Thread
```

Start playback in separate thread.

**Returns**: Thread object for the playback

##### stop_playback()

```python
def stop_playback(self) -> None
```

Stop current playback immediately.

#### Validation Methods

##### validate_actions()

```python
def validate_actions(self, actions: List[MouseAction]) -> Dict[str, Any]
```

Validate actions before playback.

**Returns**: Dictionary with validation results:
```python
{
    'valid': bool,
    'errors': List[str],
    'warnings': List[str],
    'action_count': int,
    'estimated_duration': float
}
```

#### Progress Tracking

##### get_playback_progress()

```python
def get_playback_progress(self) -> Dict[str, Any]
```

Get current playback progress.

**Returns**: Progress information:
```python
{
    'is_playing': bool,
    'progress_percent': float,
    'current_action': int,
    'total_actions': int
}
```

#### Action Creation

##### create_click_action()

```python
def create_click_action(self, x: int, y: int, button: str = 'left') -> List[MouseAction]
```

Create click action (press + release).

##### create_drag_action()

```python
def create_drag_action(self, start_x: int, start_y: int, end_x: int, end_y: int,
                      duration: float = 1.0, button: str = 'left') -> List[MouseAction]
```

Create drag action sequence.

#### Properties

- `is_playing`: Boolean indicating if playback is active
- `should_stop`: Boolean flag to stop playback
- `on_playback_start`: Callback for playback start
- `on_playback_stop`: Callback for playback stop
- `on_action_executed`: Callback for each action executed
- `on_progress_update`: Callback for progress updates

#### Example Usage

```python
from src.player import ActionPlayer

player = ActionPlayer()

# Validate before playback
validation = player.validate_actions(actions)
if not validation['valid']:
    print("Validation errors:", validation['errors'])

# Basic playback
success = player.replay(actions)

# Advanced playback
success = player.replay(
    actions,
    delay=0.5,           # Extra 0.5s between actions
    speed_multiplier=2.0, # Double speed
    loop_count=3,        # Repeat 3 times
    start_delay=5.0      # 5 second countdown
)

# Asynchronous playback
thread = player.replay_async(actions)
# Do other work...
thread.join()  # Wait for completion

# Clean up
player.cleanup()
```

## GUI Module

### MouseAutomationGUI

**Description**: Tkinter-based graphical interface for the toolkit.

#### Constructor

```python
def __init__(self, root)
```

**Parameters**:
- `root`: Tkinter root window

#### Key Features

- **Recording Tab**: Start/stop recording with hotkeys
- **Transformation Tab**: Apply coordinate transformations
- **Playback Tab**: Control action replay with progress tracking
- **Actions Tab**: File management and action editing
- **Settings Tab**: Configure hotkeys and safety settings

#### Example Usage

```python
import tkinter as tk
from src.gui import MouseAutomationGUI

root = tk.Tk()
app = MouseAutomationGUI(root)
root.mainloop()
```

## Error Handling

### Common Exceptions

#### ImportError
Raised when required dependencies are missing:
- `pynput is required. Install with: pip install pynput`
- `pyautogui is required. Install with: pip install pyautogui`
- `numpy is required. Install with: pip install numpy`

#### FileNotFoundError
Raised when trying to load non-existent action files.

#### ValueError
Raised for invalid parameters in transformations or playback settings.

#### pyautogui.FailSafeException
Raised when PyAutoGUI failsafe is triggered (mouse moved to corner).

### Error Handling Best Practices

```python
try:
    # Record actions
    recorder = MouseRecorder()
    actions = recorder.record(duration=10)
    
    # Transform actions
    transformer = CoordinateTransformer()
    transformed = transformer.scale(actions, 2.0, 2.0)
    
    # Validate before playback
    player = ActionPlayer()
    validation = player.validate_actions(transformed)
    
    if not validation['valid']:
        print("Validation failed:", validation['errors'])
        return
    
    # Safe playback
    success = player.replay(transformed)
    
except ImportError as e:
    print(f"Missing dependency: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    
finally:
    # Always clean up
    recorder.cleanup()
    player.cleanup()
```

## Configuration

### Environment Variables

The toolkit respects these environment variables:

- `MOUSE_AUTOMATION_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `MOUSE_AUTOMATION_FAILSAFE`: Enable/disable PyAutoGUI failsafe (true/false)

### Configuration Files

Settings can be stored in JSON format:

```python
{
    "hotkeys": {
        "start_recording": "<f9>",
        "stop_recording": "<f10>",
        "emergency_stop": "esc"
    },
    "safety": {
        "failsafe_enabled": true,
        "default_pause": 0.1,
        "validation_enabled": true
    },
    "recording": {
        "remove_duplicates": true,
        "min_movement_threshold": 5
    },
    "playback": {
        "default_speed": 1.0,
        "default_loops": 1,
        "start_delay": 3.0
    }
}
```

### PyAutoGUI Settings

The toolkit configures PyAutoGUI with safe defaults:

```python
import pyautogui

# Safety settings
pyautogui.FAILSAFE = True      # Move mouse to corner to stop
pyautogui.PAUSE = 0.1          # Pause between actions

# Get screen size
width, height = pyautogui.size()

# Safe coordinate checking
def safe_click(x, y):
    if 0 <= x <= width and 0 <= y <= height:
        pyautogui.click(x, y)
    else:
        raise ValueError(f"Coordinates out of bounds: ({x}, {y})")
```

## Type Hints

The toolkit uses comprehensive type hints for better development experience:

```python
from typing import List, Optional, Dict, Any, Callable, Union
import numpy as np

# Common type aliases
ActionList = List[MouseAction]
TransformDict = Dict[str, Any]
ValidationResult = Dict[str, Any]
ProgressCallback = Callable[[float], None]
ActionCallback = Callable[[int, MouseAction], None]
```

## Thread Safety

### Thread-Safe Operations

- Recording can be controlled from different threads
- Playback supports asynchronous execution
- GUI operations use proper thread synchronization

### Non-Thread-Safe Operations

- Modifying action lists during playback
- Concurrent transformations on same data
- File I/O operations should be serialized

### Best Practices

```python
import threading

# Use locks for shared data
action_lock = threading.Lock()

def safe_modify_actions(actions, modifier_func):
    with action_lock:
        return modifier_func(actions)

# Use queues for inter-thread communication
import queue
progress_queue = queue.Queue()

def progress_callback(progress):
    progress_queue.put(progress)
```

---

This API documentation provides complete reference for all modules and classes in the Mouse Automation Toolkit. For usage examples and tutorials, see the [Usage Guide](usage.md).