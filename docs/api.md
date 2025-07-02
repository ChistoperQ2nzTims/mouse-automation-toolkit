# API Documentation - Mouse Automation Toolkit

## Overview

The Mouse Automation Toolkit provides a comprehensive API for programmatic mouse action recording, transformation, and playback. This document covers all public classes, methods, and their usage.

## Module Structure

```
src/
├── __init__.py          # Package initialization and exports
├── recorder.py          # MouseRecorder class
├── transformer.py       # CoordinateTransformer class
├── player.py           # ActionPlayer class
└── gui.py              # MainGUI class
```

## Core Classes

### MouseRecorder

The `MouseRecorder` class provides functionality to record mouse actions with precise timing and coordinates.

#### Class Definition

```python
class MouseRecorder:
    def __init__(self)
```

#### Properties

- `actions: List[Dict[str, Any]]` - List of recorded actions
- `is_recording: bool` - Current recording state
- `debounce_threshold: float` - Minimum time between clicks (default: 0.1s)
- `start_time: Optional[float]` - Recording start timestamp
- `last_click_time: float` - Last click timestamp for debouncing

#### Methods

##### Recording Control

```python
def start_recording(self) -> bool
```
Start recording mouse actions.

**Returns:**
- `bool`: True if recording started successfully, False otherwise

**Example:**
```python
recorder = MouseRecorder()
if recorder.start_recording():
    print("Recording started")
```

```python
def stop_recording(self) -> bool
```
Stop recording mouse actions.

**Returns:**
- `bool`: True if recording stopped successfully, False otherwise

##### Action Management

```python
def get_actions(self) -> List[Dict[str, Any]]
```
Get all recorded actions.

**Returns:**
- `List[Dict]`: List of recorded actions

**Action Format:**
```python
{
    'type': 'click',
    'x': 100,                                    # Screen X coordinate
    'y': 200,                                    # Screen Y coordinate  
    'button': 'left',                            # 'left', 'right', or 'middle'
    'timestamp': 1.5,                           # Time since recording start
    'absolute_time': '2024-01-01T12:00:01'      # ISO format timestamp
}
```

```python
def clear_actions(self) -> None
```
Clear all recorded actions.

```python
def filter_duplicate_clicks(self, threshold: float = 1.0) -> int
```
Filter out clicks that are too close in time and space.

**Parameters:**
- `threshold`: Time threshold in seconds

**Returns:**
- `int`: Number of actions removed

##### File Operations

```python
def save_to_file(self, filename: str) -> bool
```
Save recorded actions to a JSON file.

**Parameters:**
- `filename`: Path to the output file

**Returns:**
- `bool`: True if saved successfully, False otherwise

```python
def load_from_file(self, filename: str) -> bool
```
Load actions from a JSON file.

**Parameters:**
- `filename`: Path to the input file

**Returns:**
- `bool`: True if loaded successfully, False otherwise

##### Callback Management

```python
def set_action_callback(self, callback: Callable) -> None
```
Set callback function to be called when an action is recorded.

**Parameters:**
- `callback`: Function that takes an action dict as parameter

**Example:**
```python
def on_action(action):
    print(f"Recorded click at ({action['x']}, {action['y']})")

recorder.set_action_callback(on_action)
```

##### Statistics

```python
def get_recording_stats(self) -> Dict[str, Any]
```
Get statistics about the current recording.

**Returns:**
```python
{
    'total_actions': 10,
    'duration': 5.5,
    'clicks_per_second': 1.82,
    'button_distribution': {'left': 8, 'right': 2}
}
```

### CoordinateTransformer

The `CoordinateTransformer` class provides coordinate transformation capabilities.

#### Class Definition

```python
class CoordinateTransformer:
    def __init__(self)
```

#### Properties

- `transformation_history: List[Dict[str, Any]]` - History of applied transformations

#### Core Transformation Methods

```python
def translate(self, x: float, y: float, offset_x: float, offset_y: float) -> Tuple[float, float]
```
Translate coordinates by given offset.

**Parameters:**
- `x, y`: Original coordinates
- `offset_x, offset_y`: Translation offsets

**Returns:**
- `Tuple[float, float]`: New coordinates

```python
def scale(self, x: float, y: float, scale_x: float, scale_y: float, 
          origin: Optional[Tuple[float, float]] = None) -> Tuple[float, float]
```
Scale coordinates by given factors around an origin point.

**Parameters:**
- `x, y`: Original coordinates
- `scale_x, scale_y`: Scaling factors
- `origin`: Origin point for scaling (default: (0, 0))

**Returns:**
- `Tuple[float, float]`: New coordinates

```python
def rotate(self, x: float, y: float, angle: float, 
           pivot: Optional[Tuple[float, float]] = None) -> Tuple[float, float]
```
Rotate coordinates by given angle around a pivot point.

**Parameters:**
- `x, y`: Original coordinates
- `angle`: Rotation angle in degrees (positive = clockwise)
- `pivot`: Pivot point for rotation (default: (0, 0))

**Returns:**
- `Tuple[float, float]`: New coordinates

```python
def mirror(self, x: float, y: float, axis: str, 
           center: Optional[Tuple[float, float]] = None) -> Tuple[float, float]
```
Mirror coordinates across a specified axis.

**Parameters:**
- `x, y`: Original coordinates
- `axis`: Mirror axis ('horizontal', 'vertical', or 'both')
- `center`: Center point for mirroring (default: (0, 0))

**Returns:**
- `Tuple[float, float]`: New coordinates

#### Batch Transformation Methods

```python
def transform_actions(self, actions: List[Dict[str, Any]], 
                     transformations: List[Dict[str, Any]]) -> List[Dict[str, Any]]
```
Apply multiple transformations to a list of actions.

**Parameters:**
- `actions`: List of mouse actions
- `transformations`: List of transformation configurations

**Returns:**
- `List[Dict]`: Transformed actions

##### Configuration Helpers

```python
def create_translation_transform(self, offset_x: float, offset_y: float) -> Dict[str, Any]
def create_scale_transform(self, scale_x: float, scale_y: float, 
                          origin: Optional[Tuple[float, float]] = None) -> Dict[str, Any]
def create_rotation_transform(self, angle: float, 
                             pivot: Optional[Tuple[float, float]] = None) -> Dict[str, Any]
def create_mirror_transform(self, axis: str, 
                           center: Optional[Tuple[float, float]] = None) -> Dict[str, Any]
```

Create transformation configuration dictionaries.

**Example:**
```python
transformer = CoordinateTransformer()

# Create transformations
transformations = [
    transformer.create_translation_transform(100, 50),
    transformer.create_scale_transform(1.5, 1.5, (200, 200)),
    transformer.create_rotation_transform(45, (200, 200))
]

# Apply to actions
result = transformer.transform_actions(actions, transformations)
```

#### Utility Methods

```python
def get_bounding_box(self, actions: List[Dict[str, Any]]) -> Dict[str, float]
```
Get bounding box of all click actions.

**Returns:**
```python
{
    'min_x': 100, 'min_y': 100, 'max_x': 300, 'max_y': 250,
    'width': 200, 'height': 150, 'center_x': 200, 'center_y': 175
}
```

```python
def fit_to_screen(self, actions: List[Dict[str, Any]], 
                  screen_width: int, screen_height: int, margin: int = 50) -> List[Dict[str, Any]]
```
Scale and translate actions to fit within screen bounds.

```python
def preview_transformation(self, actions: List[Dict[str, Any]], 
                          transformations: List[Dict[str, Any]]) -> Dict[str, Any]
```
Preview the result of transformations without applying them.

### ActionPlayer

The `ActionPlayer` class provides functionality to replay recorded mouse actions.

#### Class Definition

```python
class ActionPlayer:
    def __init__(self)
```

#### Properties

- `actions: List[Dict[str, Any]]` - Loaded actions for playback
- `is_playing: bool` - Current playback state
- `is_paused: bool` - Current pause state
- `speed_multiplier: float` - Playback speed (default: 1.0)
- `loop_mode: bool` - Loop playback mode (default: False)
- `safe_mode: bool` - Safe mode protection (default: True)
- `current_action_index: int` - Current action being played

#### Playback Control

```python
def load_actions(self, actions: List[Dict[str, Any]]) -> bool
```
Load actions to be played.

**Parameters:**
- `actions`: List of mouse actions

**Returns:**
- `bool`: True if loaded successfully

```python
def play(self) -> bool
```
Start playing actions.

**Returns:**
- `bool`: True if playback started successfully

```python
def pause(self) -> bool
```
Pause/unpause playback.

**Returns:**
- `bool`: True if pause state changed successfully

```python
def stop(self) -> bool
```
Stop playback.

**Returns:**
- `bool`: True if stopped successfully

#### Configuration Methods

```python
def set_speed(self, speed_multiplier: float) -> None
```
Set playback speed multiplier (0.1x to 5.0x).

```python
def set_loop_mode(self, loop: bool) -> None
```
Enable or disable loop mode.

```python
def set_safe_mode(self, safe: bool) -> None
```
Enable or disable safe mode (screen boundary checks).

```python
def set_screen_bounds(self, width: int, height: int) -> None
```
Set screen bounds for safety checks.

#### Callback Management

```python
def set_progress_callback(self, callback: Callable) -> None
```
Set callback function for playback progress updates.

**Callback signature:**
```python
def progress_callback(progress: float, current: int, total: int):
    # progress: 0.0 to 1.0
    # current: current action index
    # total: total number of actions
```

```python
def set_complete_callback(self, callback: Callable) -> None
```
Set callback function for playback completion.

**Callback signature:**
```python
def complete_callback(loops: int):
    # loops: number of loops completed
```

#### Status and Information

```python
def get_playback_status(self) -> Dict[str, Any]
```
Get current playback status.

**Returns:**
```python
{
    'is_playing': False,
    'is_paused': False,
    'current_action': 0,
    'total_actions': 10,
    'progress': 0.0,
    'speed_multiplier': 1.0,
    'loop_mode': False,
    'safe_mode': True
}
```

```python
def get_time_remaining(self) -> float
```
Get estimated time remaining for current playback.

**Returns:**
- `float`: Time remaining in seconds

```python
def validate_actions(self) -> Dict[str, Any]
```
Validate loaded actions for potential issues.

**Returns:**
```python
{
    'valid': True,
    'issues': [],
    'warnings': ['2 actions are outside screen bounds'],
    'total_actions': 10,
    'duration': 5.5
}
```

#### Navigation Methods

```python
def skip_to_action(self, action_index: int) -> bool
```
Skip to a specific action index.

```python
def preview_action(self, action_index: int) -> Optional[Dict[str, Any]]
```
Get preview information for a specific action.

### MainGUI

The `MainGUI` class provides the graphical user interface.

#### Class Definition

```python
class MainGUI:
    def __init__(self, root: tk.Tk)
```

**Parameters:**
- `root`: Tkinter root window

#### Example Usage

```python
import tkinter as tk
from src.gui import MainGUI

root = tk.Tk()
app = MainGUI(root)
root.mainloop()
```

## Usage Examples

### Basic Recording and Playback

```python
from src.recorder import MouseRecorder
from src.player import ActionPlayer
import time

# Record actions
recorder = MouseRecorder()
recorder.start_recording()

# Wait for user to perform actions
time.sleep(10)

recorder.stop_recording()
actions = recorder.get_actions()

# Save recording
recorder.save_to_file('my_recording.json')

# Play back actions
player = ActionPlayer()
player.load_actions(actions)
player.set_speed(2.0)  # 2x speed
player.play()

# Wait for playback to complete
while player.is_playing:
    time.sleep(0.1)
```

### Advanced Transformation

```python
from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer

# Load recorded actions
recorder = MouseRecorder()
recorder.load_from_file('original_actions.json')
actions = recorder.get_actions()

# Create complex transformation
transformer = CoordinateTransformer()

# Get pattern center for transformations
bbox = transformer.get_bounding_box(actions)
center = (bbox['center_x'], bbox['center_y'])

# Define transformation sequence
transformations = [
    # Move to origin
    transformer.create_translation_transform(-center[0], -center[1]),
    # Scale up 1.5x
    transformer.create_scale_transform(1.5, 1.5),
    # Rotate 45 degrees
    transformer.create_rotation_transform(45),
    # Move to new position
    transformer.create_translation_transform(400, 300)
]

# Apply transformations
transformed_actions = transformer.transform_actions(actions, transformations)

# Play transformed actions
player = ActionPlayer()
player.load_actions(transformed_actions)
player.set_safe_mode(True)
player.play()
```

### Custom Callbacks and Monitoring

```python
from src.recorder import MouseRecorder
from src.player import ActionPlayer

# Recording with callback
def on_action_recorded(action):
    print(f"Recorded: {action['button']} at ({action['x']}, {action['y']})")

recorder = MouseRecorder()
recorder.set_action_callback(on_action_recorded)
recorder.start_recording()

# Playback with progress monitoring
def on_progress(progress, current, total):
    print(f"Progress: {progress*100:.1f}% ({current}/{total})")

def on_complete(loops):
    print(f"Playback completed after {loops} loops")

player = ActionPlayer()
player.set_progress_callback(on_progress)
player.set_complete_callback(on_complete)
player.load_actions(recorder.get_actions())
player.set_loop_mode(True)
player.play()
```

### Validation and Safety

```python
from src.player import ActionPlayer

player = ActionPlayer()
player.load_actions(actions)

# Set up safety constraints
player.set_safe_mode(True)
player.set_screen_bounds(1920, 1080)

# Validate before playing
validation = player.validate_actions()
if validation['valid']:
    print("Actions are valid")
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # Play with monitoring
    player.play()
    while player.is_playing:
        status = player.get_playback_status()
        remaining = player.get_time_remaining()
        print(f"Progress: {status['progress']*100:.1f}%, Time remaining: {remaining:.1f}s")
        time.sleep(1)
else:
    print("Validation failed:")
    for issue in validation['issues']:
        print(f"  - {issue}")
```

## Error Handling

### Common Exceptions

Most methods return boolean values to indicate success/failure rather than raising exceptions. Check return values and use validation methods where available.

```python
# Safe recording
recorder = MouseRecorder()
if not recorder.start_recording():
    print("Failed to start recording - check permissions")
    return

# Safe file operations
if not recorder.save_to_file('actions.json'):
    print("Failed to save file - check disk space and permissions")

# Safe playback
player = ActionPlayer()
if not player.load_actions(actions):
    print("Failed to load actions - check action format")
    return

validation = player.validate_actions()
if not validation['valid']:
    print("Actions failed validation:")
    for issue in validation['issues']:
        print(f"  - {issue}")
    return

if not player.play():
    print("Failed to start playback - check system state")
```

### Permission Issues

On some systems, you may need to grant accessibility permissions:

```python
try:
    from src.recorder import MouseRecorder
    recorder = MouseRecorder()
    if not recorder.start_recording():
        print("Recording failed - may need accessibility permissions")
        print("Check system settings for permission grants")
except ImportError as e:
    print(f"Import failed: {e}")
    print("Install required dependencies: pip install pynput PyAutoGUI")
```

## Performance Considerations

### Memory Usage

- Large action sequences consume memory proportional to action count
- Clear actions when no longer needed: `recorder.clear_actions()`
- Use file-based storage for large recordings

### CPU Usage

- Recording uses minimal CPU for click monitoring
- Transformations are CPU-intensive for large action sets
- Playback CPU usage depends on action frequency and speed

### Timing Accuracy

- Recording timing is accurate to ~1ms
- Playback timing depends on system performance
- Use appropriate speed multipliers for your target system

This API documentation provides comprehensive coverage of all public interfaces in the Mouse Automation Toolkit. For implementation details and internal methods, refer to the source code in the `src/` directory.