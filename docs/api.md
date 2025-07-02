# API Documentation

## Overview

The Mouse Automation Toolkit provides a comprehensive Python API for programmatic control of mouse recording, transformation, and playback functionality.

## Core Modules

### src.recorder

#### MouseAction Class

Represents a single mouse action with coordinates, timing, and button information.

```python
class MouseAction:
    def __init__(self, action_type: str, x: int, y: int, button: str = None, 
                 timestamp: float = None, delay: float = 0)
```

**Parameters:**
- `action_type` (str): Type of action ('click', 'press', 'release', 'move')
- `x` (int): X coordinate
- `y` (int): Y coordinate  
- `button` (str, optional): Button name ('left', 'right', 'middle')
- `timestamp` (float, optional): Unix timestamp
- `delay` (float): Delay before this action in seconds

**Methods:**

##### to_dict()
```python
def to_dict(self) -> Dict[str, Any]
```
Convert action to dictionary for JSON serialization.

**Returns:** Dictionary representation of the action

##### from_dict()
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'MouseAction'
```
Create action from dictionary.

**Parameters:**
- `data` (dict): Dictionary containing action data

**Returns:** MouseAction instance

#### MouseRecorder Class

Records mouse actions with timing and smart filtering capabilities.

```python
class MouseRecorder:
    def __init__(self, smart_recording: bool = True, min_delay: float = 0.1)
```

**Parameters:**
- `smart_recording` (bool): Enable smart filtering of duplicate actions
- `min_delay` (float): Minimum delay between recorded actions

**Properties:**
- `actions` (List[MouseAction]): List of recorded actions
- `is_recording` (bool): Current recording status
- `smart_recording` (bool): Smart recording setting
- `min_delay` (float): Minimum delay setting

**Methods:**

##### start_recording()
```python
def start_recording(self, callback: Optional[Callable] = None)
```
Start recording mouse actions.

**Parameters:**
- `callback` (callable, optional): Function called for each recorded action

##### stop_recording()
```python
def stop_recording()
```
Stop recording mouse actions.

##### clear_actions()
```python
def clear_actions()
```
Clear all recorded actions.

##### get_actions()
```python
def get_actions(self) -> List[MouseAction]
```
Get copy of recorded actions.

**Returns:** List of MouseAction instances

##### save_to_file()
```python
def save_to_file(self, filename: str)
```
Save recorded actions to JSON file.

**Parameters:**
- `filename` (str): Path to output file

##### load_from_file()
```python
def load_from_file(self, filename: str)
```
Load actions from JSON file.

**Parameters:**
- `filename` (str): Path to input file

### src.transformer

#### CoordinateTransformer Class

Handles coordinate transformations including translation, scaling, rotation, and mirroring.

```python
class CoordinateTransformer:
    def __init__(self)
```

**Properties:**
- `screen_width` (int): Screen width for transformations
- `screen_height` (int): Screen height for transformations

**Methods:**

##### set_screen_dimensions()
```python
def set_screen_dimensions(self, width: int, height: int)
```
Set screen dimensions for transformations.

**Parameters:**
- `width` (int): Screen width in pixels
- `height` (int): Screen height in pixels

##### translate()
```python
def translate(self, actions: List[MouseAction], offset_x: int, offset_y: int) -> List[MouseAction]
```
Translate coordinates by offset values.

**Parameters:**
- `actions` (List[MouseAction]): Actions to transform
- `offset_x` (int): X offset to apply
- `offset_y` (int): Y offset to apply

**Returns:** List of transformed actions

##### scale()
```python
def scale(self, actions: List[MouseAction], scale_x: float, scale_y: float, 
          center_x: Optional[int] = None, center_y: Optional[int] = None) -> List[MouseAction]
```
Scale coordinates around a center point.

**Parameters:**
- `actions` (List[MouseAction]): Actions to transform
- `scale_x` (float): X scaling factor
- `scale_y` (float): Y scaling factor
- `center_x` (int, optional): X center point (default: screen center)
- `center_y` (int, optional): Y center point (default: screen center)

**Returns:** List of transformed actions

##### rotate()
```python
def rotate(self, actions: List[MouseAction], angle_degrees: float, 
           center_x: Optional[int] = None, center_y: Optional[int] = None) -> List[MouseAction]
```
Rotate coordinates around a center point.

**Parameters:**
- `actions` (List[MouseAction]): Actions to transform
- `angle_degrees` (float): Rotation angle in degrees
- `center_x` (int, optional): X center point (default: screen center)
- `center_y` (int, optional): Y center point (default: screen center)

**Returns:** List of transformed actions

##### mirror_horizontal()
```python
def mirror_horizontal(self, actions: List[MouseAction]) -> List[MouseAction]
```
Mirror coordinates horizontally (flip left-right).

**Parameters:**
- `actions` (List[MouseAction]): Actions to transform

**Returns:** List of transformed actions

##### mirror_vertical()
```python
def mirror_vertical(self, actions: List[MouseAction]) -> List[MouseAction]
```
Mirror coordinates vertically (flip up-down).

**Parameters:**
- `actions` (List[MouseAction]): Actions to transform

**Returns:** List of transformed actions

##### chain_transforms()
```python
def chain_transforms(self, actions: List[MouseAction], 
                    transforms: List[Tuple[str, dict]]) -> List[MouseAction]
```
Apply multiple transformations in sequence.

**Parameters:**
- `actions` (List[MouseAction]): Actions to transform
- `transforms` (List[Tuple[str, dict]]): List of (transform_name, parameters)

**Returns:** List of transformed actions

**Transform Names:**
- `'translate'`: Parameters: `{'offset_x': int, 'offset_y': int}`
- `'scale'`: Parameters: `{'scale_x': float, 'scale_y': float, 'center_x': int, 'center_y': int}`
- `'rotate'`: Parameters: `{'angle_degrees': float, 'center_x': int, 'center_y': int}`
- `'mirror_horizontal'`: No parameters
- `'mirror_vertical'`: No parameters

##### get_bounds()
```python
def get_bounds(self, actions: List[MouseAction]) -> Tuple[int, int, int, int]
```
Get bounding box of all actions.

**Parameters:**
- `actions` (List[MouseAction]): Actions to analyze

**Returns:** Tuple of (min_x, min_y, max_x, max_y)

##### normalize_to_bounds()
```python
def normalize_to_bounds(self, actions: List[MouseAction], 
                       target_width: int, target_height: int) -> List[MouseAction]
```
Normalize actions to fit within target bounds.

**Parameters:**
- `actions` (List[MouseAction]): Actions to normalize
- `target_width` (int): Target width
- `target_height` (int): Target height

**Returns:** List of normalized actions

##### apply_matrix_transform()
```python
def apply_matrix_transform(self, actions: List[MouseAction], 
                          transform_matrix: np.ndarray) -> List[MouseAction]
```
Apply custom transformation matrix.

**Parameters:**
- `actions` (List[MouseAction]): Actions to transform
- `transform_matrix` (np.ndarray): 3x3 transformation matrix

**Returns:** List of transformed actions

### src.player

#### MousePlayer Class

Handles playback of recorded mouse actions with various options.

```python
class MousePlayer:
    def __init__(self)
```

**Properties:**
- `is_playing` (bool): Current playback status
- `is_paused` (bool): Current pause status
- `current_action_index` (int): Index of current action
- `total_actions` (int): Total number of actions in sequence

**Methods:**

##### play_actions()
```python
def play_actions(self, actions: List[MouseAction], 
                delay_multiplier: float = 1.0,
                random_delay: bool = False,
                loop_count: int = 1,
                progress_callback: Optional[Callable] = None,
                completion_callback: Optional[Callable] = None)
```
Play back mouse actions.

**Parameters:**
- `actions` (List[MouseAction]): Actions to play
- `delay_multiplier` (float): Multiplier for delays between actions
- `random_delay` (bool): Add random variation to delays
- `loop_count` (int): Number of times to repeat (0 for infinite)
- `progress_callback` (callable, optional): Called with (current, total) progress
- `completion_callback` (callable, optional): Called when playback completes

##### pause_playback()
```python
def pause_playback()
```
Pause the current playback.

##### resume_playback()
```python
def resume_playback()
```
Resume paused playback.

##### stop_playback()
```python
def stop_playback()
```
Stop the current playback.

##### get_playback_status()
```python
def get_playback_status(self) -> dict
```
Get current playback status.

**Returns:** Dictionary with keys:
- `is_playing` (bool): Whether playback is active
- `is_paused` (bool): Whether playback is paused
- `current_action` (int): Current action number (1-based)
- `total_actions` (int): Total number of actions
- `progress_percentage` (float): Progress as percentage

##### preview_actions()
```python
def preview_actions(self, actions: List[MouseAction]) -> List[dict]
```
Preview actions without executing them.

**Parameters:**
- `actions` (List[MouseAction]): Actions to preview

**Returns:** List of dictionaries with action summaries

##### validate_actions()
```python
def validate_actions(self, actions: List[MouseAction]) -> List[str]
```
Validate actions and return warnings.

**Parameters:**
- `actions` (List[MouseAction]): Actions to validate

**Returns:** List of warning messages

##### get_estimated_duration()
```python
def get_estimated_duration(self, actions: List[MouseAction], 
                          delay_multiplier: float = 1.0) -> float
```
Estimate total playback duration.

**Parameters:**
- `actions` (List[MouseAction]): Actions to analyze
- `delay_multiplier` (float): Delay multiplier to apply

**Returns:** Estimated duration in seconds

##### set_failsafe()
```python
def set_failsafe(self, enabled: bool)
```
Enable or disable PyAutoGUI failsafe.

**Parameters:**
- `enabled` (bool): Whether to enable failsafe

##### set_pause_duration()
```python
def set_pause_duration(self, pause: float)
```
Set default pause between PyAutoGUI actions.

**Parameters:**
- `pause` (float): Pause duration in seconds

### src.gui

#### MouseAutomationGUI Class

Main GUI application class.

```python
class MouseAutomationGUI:
    def __init__(self)
```

**Properties:**
- `recorder` (MouseRecorder): Recorder instance
- `transformer` (CoordinateTransformer): Transformer instance
- `player` (MousePlayer): Player instance
- `current_actions` (List[MouseAction]): Currently loaded actions

**Methods:**

##### run()
```python
def run()
```
Start the GUI application.

##### log_message()
```python
def log_message(self, message: str)
```
Add message to GUI log.

**Parameters:**
- `message` (str): Message to log

## Usage Examples

### Basic Recording and Playback

```python
from src.recorder import MouseRecorder
from src.player import MousePlayer

# Create recorder and player
recorder = MouseRecorder(smart_recording=True)
player = MousePlayer()

# Record actions
print("Recording... move mouse and click")
recorder.start_recording()

# Wait for user actions (in real app, you'd have a proper wait mechanism)
import time
time.sleep(10)

recorder.stop_recording()
actions = recorder.get_actions()
print(f"Recorded {len(actions)} actions")

# Save actions
recorder.save_to_file("my_actions.json")

# Play back actions
player.play_actions(actions, delay_multiplier=0.5)
```

### Coordinate Transformations

```python
from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer

# Load actions
recorder = MouseRecorder()
recorder.load_from_file("my_actions.json")
actions = recorder.get_actions()

# Create transformer
transformer = CoordinateTransformer()
transformer.set_screen_dimensions(1920, 1080)

# Apply transformations
translated = transformer.translate(actions, 100, 50)
scaled = transformer.scale(translated, 1.5, 1.5)
rotated = transformer.rotate(scaled, 45)

# Chain transformations
transforms = [
    ('translate', {'offset_x': 100, 'offset_y': 50}),
    ('scale', {'scale_x': 1.5, 'scale_y': 1.5}),
    ('rotate', {'angle_degrees': 45})
]
chained = transformer.chain_transforms(actions, transforms)
```

### Advanced Playback with Callbacks

```python
from src.player import MousePlayer

player = MousePlayer()

def progress_callback(current, total):
    percent = (current / total) * 100
    print(f"Progress: {percent:.1f}% ({current}/{total})")

def completion_callback():
    print("Playback completed!")

# Play with callbacks
player.play_actions(
    actions,
    delay_multiplier=1.0,
    random_delay=True,
    loop_count=3,
    progress_callback=progress_callback,
    completion_callback=completion_callback
)

# Monitor playback
while player.is_playing:
    status = player.get_playback_status()
    print(f"Status: {status}")
    time.sleep(0.5)
```

### Custom Matrix Transformation

```python
import numpy as np
from src.transformer import CoordinateTransformer

transformer = CoordinateTransformer()

# Create custom transformation matrix (45-degree rotation + translation)
angle = np.radians(45)
cos_a, sin_a = np.cos(angle), np.sin(angle)

transform_matrix = np.array([
    [cos_a, -sin_a, 100],  # Rotate and translate X
    [sin_a,  cos_a, 50 ],  # Rotate and translate Y
    [0,      0,     1  ]   # Homogeneous coordinate
])

# Apply transformation
transformed = transformer.apply_matrix_transform(actions, transform_matrix)
```

### Action Validation and Preview

```python
from src.player import MousePlayer

player = MousePlayer()

# Validate actions
warnings = player.validate_actions(actions)
if warnings:
    print("Warnings found:")
    for warning in warnings:
        print(f"  - {warning}")
else:
    print("All actions are valid!")

# Preview actions
preview = player.preview_actions(actions)
for item in preview:
    print(f"Action {item['index']}: {item['action_type']} at {item['position']}")

# Estimate duration
duration = player.get_estimated_duration(actions, delay_multiplier=1.0)
print(f"Estimated playback duration: {duration:.1f} seconds")
```

## Error Handling

### Common Exceptions

- `FileNotFoundError`: When loading non-existent files
- `json.JSONDecodeError`: When loading invalid JSON files
- `ValueError`: When invalid parameters are provided
- `PermissionError`: When file access is denied
- `Exception`: General PyAutoGUI or pynput errors

### Best Practices

1. **Always validate actions** before playback
2. **Handle file operations** with try-catch blocks
3. **Check playback status** before controlling playback
4. **Use callbacks** for long-running operations
5. **Enable failsafe** for safety during development

## Thread Safety

- **MouseRecorder**: Thread-safe for recording operations
- **MousePlayer**: Thread-safe for playback control
- **CoordinateTransformer**: Stateless, inherently thread-safe
- **GUI components**: Must be accessed from main thread only

## Performance Considerations

- **Smart recording** reduces action count and memory usage
- **Delay multipliers** affect playback speed and CPU usage
- **Large action lists** may consume significant memory
- **Frequent transformations** can be CPU-intensive for large datasets