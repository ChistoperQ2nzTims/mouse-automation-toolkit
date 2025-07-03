# Usage Guide

## Quick Start

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Record mouse actions:**
   - Click the "Start Recording" button
   - Perform mouse clicks on your screen
   - Click "Stop Recording" when done

3. **Transform coordinates (optional):**
   - Go to the "Transform" tab
   - Apply translations, scaling, rotation, or mirroring

4. **Replay actions:**
   - Go to the "Play" tab
   - Adjust playback settings as needed
   - Click "Play" to start replay

## Interface Overview

The application has four main tabs:

### 📹 Record Tab
- **Recording Controls**: Start/stop recording, clear actions, remove duplicates
- **File Operations**: Save, load, and save-as functionality
- **Actions Display**: View recorded mouse clicks in a table

### 🔄 Transform Tab
- **Translation**: Move all coordinates by X/Y offset
- **Scaling**: Scale coordinates with X/Y multipliers
- **Rotation**: Rotate coordinates around center point
- **Mirroring**: Flip coordinates horizontally or vertically
- **Fit to Screen**: Automatically scale to fit screen dimensions
- **Preview**: Shows current actions and transformations

### ▶️ Play Tab
- **Playback Controls**: Play, pause, stop, and preview actions
- **Speed Control**: Adjust playback speed (0.1x to 5.0x)
- **Loop Settings**: Set number of repetitions (-1 for infinite)
- **Random Delay**: Add random delays between actions
- **Playback Log**: Monitor playback progress and events

### ⚙️ Settings Tab
- **Safe Mode**: Enable/disable ESC key to stop playback
- **About Information**: Version and feature details

## Recording Mouse Actions

### Basic Recording
1. Click "Start Recording" in the Record tab
2. Perform your mouse clicks
3. Click "Stop Recording" when finished

### Recording Tips
- **Plan your actions**: Think through the sequence before recording
- **Use consistent timing**: Keep a steady pace between clicks
- **Avoid unnecessary clicks**: Only record actions you want to replay
- **Stay within screen bounds**: Ensure all clicks are on visible areas

### Smart Recording Features
- **Duplicate Removal**: Automatically removes clicks that are too close in time/position
- **Timestamp Tracking**: Records precise timing between actions
- **Button Detection**: Distinguishes between left, right, and middle mouse buttons

## File Operations

### Saving Actions
- **Save**: Quick save to current file
- **Save As**: Choose new filename and location
- **Format**: Actions are saved in JSON format with metadata

### Loading Actions
- **Load**: Open previously saved action files
- **Compatibility**: Supports files created by the toolkit
- **Validation**: Automatically validates file format and content

### File Format
```json
{
  "actions": [
    {
      "x": 100,
      "y": 200,
      "button": "left",
      "timestamp": 0.0,
      "action_type": "click"
    }
  ],
  "metadata": {
    "created_at": "2024-01-01T12:00:00",
    "total_actions": 1,
    "total_duration": 5.0,
    "version": "1.0.0"
  }
}
```

## Coordinate Transformations

### Translation
Move all coordinates by a fixed offset:
- **Use case**: Adapt recordings for different window positions
- **Parameters**: X offset, Y offset
- **Example**: Offset by (100, 50) to move actions right and down

### Scaling
Resize the coordinate space:
- **Use case**: Adapt recordings for different screen resolutions
- **Parameters**: X scale factor, Y scale factor
- **Example**: Scale by (2.0, 2.0) to double the size
- **Center point**: Scaling occurs around the calculated center

### Rotation
Rotate coordinates around a center point:
- **Use case**: Adapt recordings for rotated interfaces
- **Parameters**: Angle in degrees
- **Example**: Rotate by 90° for landscape/portrait adaptation
- **Direction**: Positive angles rotate clockwise

### Mirroring
Flip coordinates along an axis:
- **Horizontal**: Flip left-to-right around vertical axis
- **Vertical**: Flip top-to-bottom around horizontal axis
- **Use case**: Adapt recordings for mirrored layouts

### Fit to Screen
Automatically scale to fit screen dimensions:
- **Parameters**: Target screen width/height, margin
- **Behavior**: Maintains aspect ratio, adds margin
- **Use case**: Make recordings work on any screen size

## Playback Options

### Speed Control
- **Range**: 0.1x to 5.0x normal speed
- **Use case**: Slow down for precise actions, speed up for repetitive tasks
- **Note**: Affects delay between actions, not click duration

### Loop Settings
- **Single**: Play once (default)
- **Multiple**: Specify number of repetitions
- **Infinite**: Loop continuously until stopped (-1)

### Random Delay
Add randomness to timing:
- **Parameters**: Minimum and maximum delay in seconds
- **Use case**: Make playback appear more natural
- **Application**: Added to normal timing delays

### Safety Features
- **ESC Key**: Immediately stops playback when pressed
- **PyAutoGUI Failsafe**: Move mouse to screen corner to trigger emergency stop
- **Bounds Checking**: Validates coordinates are within screen limits
- **Pause/Resume**: Space key to pause/resume during playback

## Best Practices

### Recording
1. **Test your sequence** manually before recording
2. **Keep recordings short** and focused on specific tasks
3. **Use descriptive filenames** for saved actions
4. **Remove duplicates** after recording to clean up actions
5. **Check the preview** before saving

### Transformations
1. **Preview transformations** before applying
2. **Save original** before making major changes
3. **Use fit-to-screen** for cross-platform compatibility
4. **Test transformations** on target environment

### Playback
1. **Start with slow speed** to verify actions
2. **Use preview** to check coordinates before playing
3. **Keep ESC key accessible** for emergency stops
4. **Monitor playback log** for any issues
5. **Test in safe environment** before production use

## Keyboard Shortcuts

### During Playback
- **ESC**: Stop playback immediately
- **Space**: Pause/resume playback
- **Mouse to corner**: Trigger PyAutoGUI failsafe

### Interface
- **Ctrl+S**: Save actions (when focused on Record tab)
- **Ctrl+O**: Load actions (when focused on Record tab)

## Troubleshooting

### Recording Issues
- **No actions recorded**: Ensure you're clicking after recording starts
- **Inaccurate coordinates**: Check if screen scaling affects coordinates
- **Missing clicks**: Verify mouse buttons are working correctly

### Playback Issues
- **Actions in wrong location**: Use coordinate transformations
- **Too fast/slow**: Adjust speed multiplier
- **Stuck in loop**: Press ESC to stop infinite loops
- **Click not registered**: Check if target area is clickable

### Transformation Issues
- **Actions outside screen**: Use fit-to-screen transformation
- **Distorted patterns**: Check scale factors and center points
- **Unexpected results**: Preview transformations before applying

## Advanced Usage

### Command Line
```bash
# Launch with specific options
python main.py --gui

# Check version
python main.py --version
```

### Scripting
See the examples directory for programmatic usage:
- `examples/basic_usage.py`: Basic recording and playback
- `examples/advanced_transform.py`: Coordinate transformations
- `examples/sample_actions.json`: Sample action file format

### Integration
The toolkit components can be used independently:
```python
from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer

# Use components programmatically
recorder = MouseRecorder()
transformer = CoordinateTransformer()
player = ActionPlayer()
```