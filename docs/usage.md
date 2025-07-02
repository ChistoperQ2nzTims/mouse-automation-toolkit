# Usage Guide

This comprehensive guide covers all features and capabilities of the Mouse Automation Toolkit.

## Table of Contents

1. [Quick Start](#quick-start)
2. [GUI Interface](#gui-interface)
3. [Command Line Interface](#command-line-interface)
4. [Programming Interface](#programming-interface)
5. [Recording Mouse Actions](#recording-mouse-actions)
6. [Transforming Coordinates](#transforming-coordinates)
7. [Playing Back Actions](#playing-back-actions)
8. [Safety Features](#safety-features)
9. [Advanced Features](#advanced-features)
10. [Best Practices](#best-practices)

## Quick Start

### 1. Launch the GUI (Easiest)

```bash
python main.py
```

This opens the graphical interface where you can:
- Record mouse actions with hotkeys (F9/F10)
- Transform recorded actions
- Play back actions with safety features
- Manage action profiles

### 2. Record Actions via Command Line

```bash
# Record for 10 seconds
python main.py --record my_actions.json --duration 10

# Record manually (stop with F10)
python main.py --record my_actions.json
```

### 3. Play Back Actions

```bash
# Basic playback
python main.py --play my_actions.json

# Playback with custom settings
python main.py --play my_actions.json --speed 2.0 --loops 3 --delay 0.5
```

## GUI Interface

### Main Window

The GUI is organized into tabs:

1. **Recording Tab**: Control mouse action recording
2. **Transformation Tab**: Apply coordinate transformations
3. **Playback Tab**: Control action replay
4. **Actions Tab**: Manage action files and view recorded data
5. **Settings Tab**: Configure hotkeys and safety settings

### Recording Tab

**Controls:**
- **Start Recording (F9)**: Begin recording mouse actions
- **Stop Recording (F10)**: End recording session

**Settings:**
- **Duration**: Set automatic recording duration (empty = manual stop)
- **Remove Duplicates**: Filter out redundant mouse movements

**Statistics Display:** Shows real-time recording stats including:
- Number of actions recorded
- Recording duration
- Breakdown by action type (clicks, moves, scrolls)

### Transformation Tab

Apply coordinate transformations to recorded actions:

**Basic Transformations:**
- **Translate**: Move all actions by X, Y offset
- **Scale**: Resize action pattern by scale factors
- **Rotate**: Rotate actions around center point
- **Mirror**: Flip horizontally or vertically

**Advanced Transformations:**
- **Fit to Screen**: Automatically scale and position for current screen
- **Maintain Aspect Ratio**: Preserve original proportions

### Playback Tab

**Controls:**
- **Start Playback**: Begin replaying actions
- **Stop Playback (ESC)**: Emergency stop during playback
- **Validate Actions**: Check for potential issues

**Settings:**
- **Speed**: Playback speed multiplier (1.0 = normal, 2.0 = double speed)
- **Extra Delay**: Additional pause between actions
- **Loop Count**: Number of repetitions (0 = infinite)
- **Start Delay**: Countdown before playback begins

**Progress Tracking:** Real-time progress bar and status

### Actions Tab

**File Operations:**
- **Load Actions**: Import action files
- **Save Actions**: Export current actions
- **Clear Actions**: Remove all current actions

**Action List:** Detailed view of all recorded actions with:
- Timestamp
- Action type (move, click, scroll)
- Coordinates
- Button information
- Additional details

### Settings Tab

**Hotkey Configuration:**
- **Start Recording**: F9 (default)
- **Stop Recording**: F10 (default)
- **Emergency Stop**: ESC (default)

**Safety Settings:**
- **PyAutoGUI Failsafe**: Mouse-to-corner emergency stop
- **Default Pause**: Minimum delay between actions

**Application Log:** Real-time logging of toolkit operations

## Command Line Interface

### Recording Commands

```bash
# Basic recording
python main.py --record filename.json

# Timed recording
python main.py --record filename.json --duration 30

# With custom settings (programmatically)
python -c "
from src.recorder import MouseRecorder
recorder = MouseRecorder(remove_duplicates=True)
actions = recorder.record(duration=10)
recorder.save_to_file('recorded.json', actions)
"
```

### Playback Commands

```bash
# Basic playback
python main.py --play filename.json

# Custom speed and timing
python main.py --play filename.json --speed 1.5 --delay 0.2

# Multiple loops
python main.py --play filename.json --loops 5

# Infinite loop (stop with ESC)
python main.py --play filename.json --loops 0
```

### Transformation Commands

```bash
# Translate coordinates
python main.py --transform input.json output.json --translate 100 50

# Scale coordinates
python main.py --transform input.json output.json --scale 1.5 1.5

# Rotate coordinates
python main.py --transform input.json output.json --rotate 45

# Mirror horizontally
python main.py --transform input.json output.json --mirror-h

# Mirror vertically
python main.py --transform input.json output.json --mirror-v
```

### Combined Operations

```bash
# Record, transform, and play back
python main.py --record temp.json --duration 10
python main.py --transform temp.json scaled.json --scale 2.0 2.0
python main.py --play scaled.json --speed 0.5
```

## Programming Interface

### Basic Usage

```python
from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer

# Initialize components
recorder = MouseRecorder()
transformer = CoordinateTransformer()
player = ActionPlayer()

# Record actions
print("Recording for 5 seconds...")
actions = recorder.record(duration=5.0)

# Transform actions
translated = transformer.translate(actions, offset_x=100, offset_y=50)
scaled = transformer.scale(translated, scale_x=1.5, scale_y=1.5)

# Play back actions
print("Playing back transformed actions...")
player.replay(scaled, delay=0.5, speed_multiplier=1.0)

# Clean up
recorder.cleanup()
player.cleanup()
```

### Advanced Programming

```python
# Custom transformation chain
transforms = [
    {'type': 'translate', 'offset_x': 50, 'offset_y': 25},
    {'type': 'scale', 'scale_x': 1.2, 'scale_y': 1.2},
    {'type': 'rotate', 'angle_degrees': 30}
]

chained_result = transformer.chain_transforms(actions, transforms)

# Matrix transformation
import numpy as np
custom_matrix = np.array([
    [1.5, 0, 100],  # Scale X by 1.5, translate by 100
    [0, 1.5, 50],   # Scale Y by 1.5, translate by 50
    [0, 0, 1]
])

matrix_result = transformer.apply_matrix_transform(actions, custom_matrix)

# Fit to specific screen size
fitted = transformer.fit_to_screen(actions, 1920, 1080, maintain_aspect_ratio=True)

# Callback functions
def on_recording_start():
    print("Recording started!")

def on_playback_progress(progress):
    print(f"Playback progress: {progress * 100:.1f}%")

recorder.on_recording_start = on_recording_start
player.on_progress_update = on_playback_progress
```

## Recording Mouse Actions

### Manual Recording

1. **Start recording**: Press F9 or use GUI/command
2. **Perform actions**: Move mouse, click, scroll as needed
3. **Stop recording**: Press F10 or use GUI/command

### Automatic Recording

```python
# Record for specific duration
actions = recorder.record(duration=30.0)  # 30 seconds

# Record with custom settings
recorder.remove_duplicates = True
recorder.start_hotkey = '<f9>'
recorder.stop_hotkey = '<f10>'
```

### Recording Tips

- **Smooth movements**: Avoid jerky mouse movements for better playback
- **Timing awareness**: Consider delays between actions
- **Screen resolution**: Record on same resolution as playback when possible
- **Application state**: Ensure target applications are in same state

### Recorded Data Format

Actions are saved in JSON format:
```json
{
  "metadata": {
    "recorded_at": "2024-01-01T12:00:00.000000",
    "action_count": 5,
    "duration": 3.0
  },
  "actions": [
    {
      "timestamp": 0.0,
      "action_type": "move",
      "x": 100,
      "y": 100,
      "button": null,
      "pressed": null
    },
    {
      "timestamp": 0.5,
      "action_type": "click",
      "x": 100,
      "y": 100,
      "button": "left",
      "pressed": true
    }
  ]
}
```

## Transforming Coordinates

### Basic Transformations

**Translation** - Move all coordinates:
```python
translated = transformer.translate(actions, offset_x=100, offset_y=50)
```

**Scaling** - Resize the pattern:
```python
scaled = transformer.scale(actions, scale_x=1.5, scale_y=1.5)
```

**Rotation** - Rotate around center:
```python
rotated = transformer.rotate(actions, angle_degrees=45)
```

**Mirroring** - Flip horizontally or vertically:
```python
h_mirrored = transformer.mirror_horizontal(actions)
v_mirrored = transformer.mirror_vertical(actions)
```

### Advanced Transformations

**Screen Fitting**:
```python
# Fit to full HD screen
fitted = transformer.fit_to_screen(actions, 1920, 1080, maintain_aspect_ratio=True)

# Fit with custom margin
fitted = transformer.fit_to_screen(actions, 800, 600, margin=20)
```

**Custom Matrix Transformations**:
```python
import numpy as np

# Shear transformation
shear_matrix = np.array([
    [1, 0.5, 0],  # Shear in X
    [0, 1, 0],
    [0, 0, 1]
])

sheared = transformer.apply_matrix_transform(actions, shear_matrix)
```

**Chained Transformations**:
```python
# Apply multiple transformations in sequence
transforms = [
    {'type': 'translate', 'offset_x': 100, 'offset_y': 50},
    {'type': 'scale', 'scale_x': 1.2, 'scale_y': 1.2},
    {'type': 'rotate', 'angle_degrees': 30},
    {'type': 'mirror_horizontal'}
]

result = transformer.chain_transforms(actions, transforms)
```

### Timing Transformations

**Normalize Duration**:
```python
# Make all actions fit in 10 seconds
normalized = transformer.normalize_timing(actions, total_duration=10.0)
```

## Playing Back Actions

### Basic Playback

```python
# Simple playback
success = player.replay(actions)

# Custom settings
success = player.replay(
    actions,
    delay=0.5,           # Extra delay between actions
    speed_multiplier=1.5, # 1.5x speed
    loop_count=3,        # Repeat 3 times
    start_delay=3.0      # 3 second countdown
)
```

### Validation Before Playback

```python
validation = player.validate_actions(actions)

if validation['valid']:
    print("Actions are valid")
    player.replay(actions)
else:
    print("Validation errors:")
    for error in validation['errors']:
        print(f"  - {error}")

if validation['warnings']:
    print("Warnings:")
    for warning in validation['warnings']:
        print(f"  - {warning}")
```

### Asynchronous Playback

```python
import threading

# Start playback in background
thread = player.replay_async(actions, delay=0.1, speed_multiplier=2.0)

# Do other work...
print("Playback running in background")

# Wait for completion
thread.join()
print("Playback completed")
```

### Creating Custom Actions

```python
# Create a simple click
click_actions = player.create_click_action(x=200, y=300, button='left')

# Create a drag operation
drag_actions = player.create_drag_action(
    start_x=100, start_y=100,
    end_x=300, end_y=200,
    duration=2.0,
    button='left'
)

# Combine with other actions
all_actions = click_actions + drag_actions
player.replay(all_actions)
```

## Safety Features

### Built-in Safety Mechanisms

1. **PyAutoGUI Failsafe**: Move mouse to top-left corner to stop
2. **Emergency Stop Key**: Press ESC to stop playback immediately
3. **Action Validation**: Check coordinates and timing before playback
4. **Boundary Checking**: Warn about actions outside screen bounds

### Configuring Safety Settings

```python
# Disable failsafe (use with caution)
import pyautogui
pyautogui.FAILSAFE = False

# Custom emergency stop key
player = ActionPlayer(emergency_stop_key='space')

# Adjust default pause between actions
player.default_pause = 0.2  # 200ms between actions
```

### Validation Warnings

The toolkit warns about:
- Coordinates outside screen boundaries
- Actions near screen corners (failsafe trigger zones)
- Extremely rapid action sequences
- Long playback durations

## Advanced Features

### Hotkey Management

```python
# Custom hotkeys
recorder = MouseRecorder(
    start_hotkey='<f1>',
    stop_hotkey='<f2>'
)

# Start hotkey listener
recorder.start_hotkey_listener()

# Stop listener when done
recorder.stop_hotkey_listener()
```

### Callback Functions

```python
def on_recording_start():
    print("Recording started!")

def on_recording_stop():
    print("Recording stopped!")

def on_action_executed(index, action):
    print(f"Executed action {index}: {action.action_type}")

def on_progress_update(progress):
    print(f"Progress: {progress * 100:.1f}%")

# Set callbacks
recorder.on_recording_start = on_recording_start
recorder.on_recording_stop = on_recording_stop
player.on_action_executed = on_action_executed
player.on_progress_update = on_progress_update
```

### Batch Processing

```python
import os

# Process multiple files
input_dir = "recordings"
output_dir = "transformed"

for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        # Load actions
        actions = recorder.load_from_file(os.path.join(input_dir, filename))
        
        # Transform
        transformed = transformer.scale(actions, 1.5, 1.5)
        
        # Save
        output_path = os.path.join(output_dir, f"scaled_{filename}")
        recorder.save_to_file(output_path, transformed)
        
        print(f"Processed {filename}")
```

### Performance Optimization

```python
# Reduce recording frequency for better performance
recorder.remove_duplicates = True

# Optimize playback speed
player.default_pause = 0.01  # Minimum pause

# Use speed multiplier for faster execution
player.replay(actions, speed_multiplier=5.0)
```

## Best Practices

### Recording Best Practices

1. **Plan your actions**: Think through the sequence before recording
2. **Use consistent timing**: Maintain steady pace for better playback
3. **Minimize movements**: Record only necessary mouse actions
4. **Test on same setup**: Record and playback on similar screen configurations
5. **Use descriptive filenames**: Name files based on their purpose

### Transformation Best Practices

1. **Validate before applying**: Check bounds and coordinates
2. **Chain efficiently**: Combine related transformations
3. **Preserve aspect ratios**: Use screen fitting when changing resolutions
4. **Test incrementally**: Apply and test transformations step by step
5. **Backup originals**: Keep copies of original recordings

### Playback Best Practices

1. **Always validate**: Check actions before playback
2. **Use start delays**: Give yourself time to position applications
3. **Enable safety features**: Keep failsafe and emergency stops enabled
4. **Test in safe environments**: Avoid critical applications during testing
5. **Monitor progress**: Use callbacks for long sequences

### Error Handling

```python
try:
    # Record actions
    actions = recorder.record(duration=10)
    
    # Validate
    validation = player.validate_actions(actions)
    if not validation['valid']:
        print("Invalid actions:", validation['errors'])
        return
    
    # Transform
    transformed = transformer.scale(actions, 2.0, 2.0)
    
    # Play back
    success = player.replay(transformed)
    if not success:
        print("Playback was interrupted")

except Exception as e:
    print(f"Error: {e}")
    
finally:
    # Always clean up
    recorder.cleanup()
    player.cleanup()
```

## Troubleshooting

### Common Issues

**Recording not working:**
- Check accessibility permissions (macOS)
- Verify hotkey conflicts
- Ensure pynput is properly installed

**Playback not accurate:**
- Check screen resolution differences
- Validate action coordinates
- Adjust timing and speed settings

**GUI not loading:**
- Verify tkinter installation
- Check display environment variables (Linux)
- Try command-line interface instead

**Performance issues:**
- Reduce recording frequency
- Enable duplicate removal
- Use faster playback speeds

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed information about operations
recorder = MouseRecorder()
# ... operations will now show debug output
```

---

**Next Steps:**
- Explore the [API Documentation](api.md) for detailed technical information
- Check out [Examples](../examples/) for more usage patterns
- Read [Installation Guide](installation.md) for setup issues