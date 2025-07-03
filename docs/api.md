# API Documentation

## Overview

The Mouse Automation Toolkit provides a modular API with four main components:

- **MouseRecorder**: Records mouse actions
- **CoordinateTransformer**: Transforms coordinate systems
- **ActionPlayer**: Replays mouse actions
- **MouseAutomationGUI**: Provides graphical interface

## MouseAction Class

Represents a single mouse action.

### Constructor
```python
MouseAction(x: int, y: int, button: str, timestamp: float, action_type: str = "click")
```

**Parameters:**
- `x`: X coordinate of the action
- `y`: Y coordinate of the action  
- `button`: Mouse button ("left", "right", "middle")
- `timestamp`: Time offset in seconds from recording start
- `action_type`: Type of action (default: "click")

### Methods

#### `to_dict() -> Dict[str, Any]`
Convert action to dictionary for JSON serialization.

#### `from_dict(data: Dict[str, Any]) -> MouseAction`
Create MouseAction from dictionary (class method).

---

## MouseRecorder Class

Records mouse clicks with coordinates, timing, and button information.

### Constructor
```python
MouseRecorder()
```

### Properties
- `is_recording: bool` - Current recording state
- `actions: List[MouseAction]` - List of recorded actions
- `start_time: Optional[float]` - Recording start timestamp

### Methods

#### `start_recording() -> None`
Start recording mouse actions.
- Clears existing actions
- Begins listening for mouse clicks
- Records relative timestamps

#### `stop_recording() -> None`
Stop recording mouse actions.
- Stops mouse listener
- Preserves recorded actions

#### `save_to_file(filename: str, include_metadata: bool = True) -> None`
Save recorded actions to JSON file.

**Parameters:**
- `filename`: Output file path
- `include_metadata`: Include creation time, duration, etc.

#### `load_from_file(filename: str) -> None`
Load actions from JSON file.

**Parameters:**
- `filename`: Input file path

**Exceptions:**
- Handles FileNotFoundError, JSONDecodeError gracefully

#### `get_actions() -> List[MouseAction]`
Get copy of recorded actions list.

#### `clear_actions() -> None`
Clear all recorded actions.

#### `remove_duplicate_actions(tolerance: float = 0.1) -> int`
Remove actions that occur within tolerance timeframe.

**Parameters:**
- `tolerance`: Time tolerance in seconds

**Returns:**
- Number of actions removed

---

## CoordinateTransformer Class

Transforms mouse action coordinates using mathematical operations.

### Constructor
```python
CoordinateTransformer()
```

### Methods

#### `translate(actions: List[MouseAction], offset_x: int, offset_y: int) -> List[MouseAction]`
Translate coordinates by offset values.

**Parameters:**
- `actions`: Input actions to transform
- `offset_x`: X offset in pixels
- `offset_y`: Y offset in pixels

**Returns:**
- New list of transformed actions

#### `scale(actions: List[MouseAction], scale_x: float, scale_y: float, center_x: int = 0, center_y: int = 0) -> List[MouseAction]`
Scale coordinates around center point.

**Parameters:**
- `actions`: Input actions to transform
- `scale_x`: X scale factor
- `scale_y`: Y scale factor
- `center_x`: Center point X coordinate
- `center_y`: Center point Y coordinate

#### `rotate(actions: List[MouseAction], angle_degrees: float, center_x: int = 0, center_y: int = 0) -> List[MouseAction]`
Rotate coordinates around center point.

**Parameters:**
- `actions`: Input actions to transform
- `angle_degrees`: Rotation angle in degrees (positive = clockwise)
- `center_x`: Center point X coordinate
- `center_y`: Center point Y coordinate

#### `mirror_horizontal(actions: List[MouseAction], axis_x: int = 0) -> List[MouseAction]`
Mirror coordinates horizontally around vertical axis.

**Parameters:**
- `actions`: Input actions to transform
- `axis_x`: X coordinate of mirror axis

#### `mirror_vertical(actions: List[MouseAction], axis_y: int = 0) -> List[MouseAction]`
Mirror coordinates vertically around horizontal axis.

**Parameters:**
- `actions`: Input actions to transform
- `axis_y`: Y coordinate of mirror axis

#### `get_bounding_box(actions: List[MouseAction]) -> Tuple[int, int, int, int]`
Get bounding box of all actions.

**Returns:**
- Tuple of (min_x, min_y, max_x, max_y)

#### `get_center_point(actions: List[MouseAction]) -> Tuple[int, int]`
Get center point of all actions.

**Returns:**
- Tuple of (center_x, center_y)

#### `fit_to_screen(actions: List[MouseAction], screen_width: int, screen_height: int, margin: int = 10) -> List[MouseAction]`
Scale and translate actions to fit within screen bounds.

**Parameters:**
- `actions`: Input actions to transform
- `screen_width`: Target screen width
- `screen_height`: Target screen height
- `margin`: Margin in pixels

#### `apply_transformation_chain(actions: List[MouseAction], transformations: List[Dict[str, Any]]) -> List[MouseAction]`
Apply sequence of transformations.

**Parameters:**
- `actions`: Input actions to transform
- `transformations`: List of transformation specifications

**Transformation Format:**
```python
{
  "type": "translate",  # translate, scale, rotate, mirror_horizontal, mirror_vertical, fit_to_screen
  "params": {
    "offset_x": 100,    # Parameters specific to transformation type
    "offset_y": 50
  }
}
```

---

## ActionPlayer Class

Replays recorded mouse actions with customizable settings.

### Constructor
```python
ActionPlayer()
```

### Properties
- `is_playing: bool` - Current playback state
- `is_paused: bool` - Current pause state
- `speed_multiplier: float` - Playback speed multiplier
- `loop_count: int` - Number of playback loops
- `safe_mode: bool` - ESC key stop functionality

### Methods

#### `set_progress_callback(callback: Callable[[int, int], None]) -> None`
Set callback for progress updates.

**Parameters:**
- `callback`: Function called with (current, total) progress

#### `set_speed_multiplier(multiplier: float) -> None`
Set playback speed multiplier.

**Parameters:**
- `multiplier`: Speed factor (0.1 to 5.0+, 1.0 = normal speed)

#### `set_random_delay(min_delay: float, max_delay: float) -> None`
Set random delay range between actions.

**Parameters:**
- `min_delay`: Minimum additional delay in seconds
- `max_delay`: Maximum additional delay in seconds

#### `set_loop_count(count: int) -> None`
Set number of playback loops.

**Parameters:**
- `count`: Number of loops (-1 = infinite, 0+ = specific count)

#### `set_safe_mode(enabled: bool) -> None`
Enable/disable safe mode ESC key stopping.

#### `play_actions(actions: List[MouseAction]) -> None`
Start playing back actions.

**Parameters:**
- `actions`: Actions to play back

**Behavior:**
- Runs in separate thread
- Respects timing, speed, and loop settings
- Can be stopped with ESC key (if safe mode enabled)

#### `stop_playback() -> None`
Stop current playback immediately.

#### `pause_playback() -> None`
Pause current playback.

#### `resume_playback() -> None`
Resume paused playback.

#### `get_estimated_duration(actions: List[MouseAction]) -> float`
Calculate estimated playback duration.

**Parameters:**
- `actions`: Actions to analyze

**Returns:**
- Estimated duration in seconds

#### `preview_actions(actions: List[MouseAction], duration: float = 2.0) -> None`
Preview actions without executing them.

**Parameters:**
- `actions`: Actions to preview
- `duration`: Preview display duration

#### `is_busy() -> bool`
Check if player is currently active.

**Returns:**
- True if playing, False otherwise

---

## MouseAutomationGUI Class

Provides graphical user interface for the toolkit.

### Constructor
```python
MouseAutomationGUI()
```

### Methods

#### `run() -> None`
Start the GUI application main loop.

#### `log_message(message: str) -> None`
Add message to the playback log.

---

## Usage Examples

### Basic Recording and Playback
```python
from src.recorder import MouseRecorder
from src.player import ActionPlayer

# Record actions
recorder = MouseRecorder()
recorder.start_recording()
# ... perform mouse clicks ...
recorder.stop_recording()

# Save actions
recorder.save_to_file("my_actions.json")

# Play back actions
player = ActionPlayer()
player.set_speed_multiplier(0.5)  # Half speed
player.play_actions(recorder.get_actions())
```

### Coordinate Transformation
```python
from src.transformer import CoordinateTransformer

transformer = CoordinateTransformer()

# Load actions
recorder.load_from_file("my_actions.json")
actions = recorder.get_actions()

# Transform coordinates
translated = transformer.translate(actions, 100, 50)
scaled = transformer.scale(translated, 1.5, 1.5, 400, 300)
rotated = transformer.rotate(scaled, 45, 400, 300)

# Save transformed actions
recorder.actions = rotated
recorder.save_to_file("transformed_actions.json")
```

### Advanced Playback
```python
player = ActionPlayer()

# Configure playback
player.set_speed_multiplier(2.0)        # Double speed
player.set_loop_count(3)                # Repeat 3 times
player.set_random_delay(0.1, 0.3)       # Random delay 0.1-0.3s
player.set_safe_mode(True)              # ESC key stops

# Progress monitoring
def progress_handler(current, total):
    print(f"Progress: {current}/{total}")

player.set_progress_callback(progress_handler)

# Start playback
player.play_actions(actions)
```

### Transformation Chain
```python
transformations = [
    {"type": "translate", "params": {"offset_x": 100, "offset_y": 50}},
    {"type": "scale", "params": {"scale_x": 1.2, "scale_y": 1.2, "center_x": 400, "center_y": 300}},
    {"type": "rotate", "params": {"angle": 30, "center_x": 400, "center_y": 300}},
    {"type": "fit_to_screen", "params": {"screen_width": 1920, "screen_height": 1080, "margin": 50}}
]

result = transformer.apply_transformation_chain(actions, transformations)
```

## Error Handling

### Common Exceptions
- **FileNotFoundError**: When loading non-existent files
- **JSONDecodeError**: When loading invalid JSON files
- **PyAutoGUI.FailSafeException**: When mouse moved to screen corner
- **ImportError**: When required dependencies are missing

### Best Practices
1. Always check `is_busy()` before starting new operations
2. Use `try/except` blocks for file operations
3. Validate coordinates before playback
4. Enable safe mode for interactive use
5. Monitor progress callbacks for long operations

## Thread Safety

### Thread-Safe Operations
- Starting/stopping recording
- Starting/stopping playback  
- Progress callbacks

### Non-Thread-Safe Operations
- Modifying action lists during playback
- Multiple simultaneous recordings
- GUI operations from background threads

### Recommendations
- Use the GUI for interactive operations
- Use separate instances for concurrent operations
- Coordinate access with proper synchronization