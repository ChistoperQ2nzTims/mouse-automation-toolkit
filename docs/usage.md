# Usage Guide - Mouse Automation Toolkit

## Overview

The Mouse Automation Toolkit provides both graphical (GUI) and command-line (CLI) interfaces for recording, transforming, and replaying mouse actions. This guide covers all major features and workflows.

## Quick Start

### GUI Mode (Recommended for beginners)

```bash
# Launch the GUI application
python3 main.py
```

### CLI Mode (For automation and scripting)

```bash
# Record mouse actions
python3 main.py --cli --record my_actions.json

# Play back recorded actions
python3 main.py --cli --play my_actions.json

# Transform actions
python3 main.py --cli --transform input.json output.json --translate 100 50
```

## GUI Interface Guide

### Main Interface Layout

The GUI consists of 5 main tabs:
1. **🔴 Record** - Recording mouse actions
2. **🔄 Transform** - Coordinate transformations
3. **▶️ Playback** - Action replay
4. **👁 Preview** - Action visualization and statistics
5. **⚙️ Settings** - Configuration and preferences

### Recording Tab

#### Basic Recording
1. Click **"Start Recording"** button
2. Perform mouse clicks on your screen
3. Watch actions appear in real-time
4. Click **"Stop Recording"** when finished

#### Recording Options
- **Debounce (ms)**: Minimum time between clicks (prevents accidental duplicates)
- **Action Counter**: Shows total number of recorded actions
- **Live Actions Display**: Real-time list of recorded actions

#### Tips for Better Recording
- Use consistent timing between clicks
- Avoid rapid-fire clicking unless intentional
- Record in a clutter-free environment
- Test your pattern before final recording

### Transform Tab

#### Translation (Movement)
- **Offset X/Y**: Move all actions by specified pixels
- Use positive values to move right/down
- Use negative values to move left/up

#### Scaling (Resize)
- **Scale X/Y**: Multiply coordinates by scale factors
- Values > 1.0 make pattern larger
- Values < 1.0 make pattern smaller
- Different X/Y values create aspect ratio changes

#### Rotation
- **Angle**: Rotate pattern around its center
- Positive angles = clockwise rotation
- Negative angles = counterclockwise rotation
- Common values: 90°, 180°, 270°

#### Mirroring
- **Horizontal**: Flip pattern left-to-right
- **Vertical**: Flip pattern top-to-bottom
- **Both**: Flip both directions (180° rotation equivalent)

#### Batch Operations
- **Fit to Screen**: Automatically scale and position to fit screen
- **Reset All**: Clear transformation history

### Playback Tab

#### Playback Controls
- **▶ Play**: Start action replay
- **⏸ Pause**: Pause/resume playback
- **⏹ Stop**: Stop playback and reset

#### Playback Options
- **Speed**: Control playback speed (0.1x to 5.0x)
- **Loop Mode**: Repeat actions continuously
- **Safe Mode**: Prevent clicks outside screen bounds

#### Progress Monitoring
- Real-time progress bar
- Current action indicator
- Time remaining estimate

### Preview Tab

#### Statistics Display
- Total number of actions
- Recording duration
- Clicks per second
- Button distribution (left/right/middle)
- Bounding box dimensions

#### Action List
- Detailed view of all recorded actions
- Timestamps and coordinates
- Action indices for reference

#### Export Features
- Export action data to text files
- Generate reports and summaries

### Settings Tab

#### General Settings
- Auto-save preferences
- Notification settings
- System tray options

#### Hotkeys
- **ESC**: Emergency stop during playback
- **F9**: Quick record toggle
- **F10**: Quick play toggle

#### Safety Settings
- Screen boundary protection
- Confirmation for destructive operations
- Click preview options

## CLI Interface Guide

### Recording Actions

```bash
# Basic recording
python3 main.py --cli --record output.json

# Recording with options
python3 main.py --cli --record output.json --verbose
```

**During recording:**
- Perform your mouse clicks
- Press `Ctrl+C` to stop recording
- Actions are automatically saved to the specified file

### Playing Actions

```bash
# Basic playback
python3 main.py --cli --play actions.json

# Playback with options
python3 main.py --cli --play actions.json --speed 2.0 --loop --verbose

# Disable safety features
python3 main.py --cli --play actions.json --no-safe-mode
```

**Playback options:**
- `--speed MULTIPLIER`: Playback speed (0.1 to 5.0)
- `--loop`: Repeat continuously until interrupted
- `--no-safe-mode`: Disable screen boundary protection
- `--verbose`: Show detailed progress information

### Transforming Actions

```bash
# Translation
python3 main.py --cli --transform input.json output.json --translate 100 50

# Scaling
python3 main.py --cli --transform input.json output.json --scale 1.5 1.2

# Rotation
python3 main.py --cli --transform input.json output.json --rotate 45

# Mirroring
python3 main.py --cli --transform input.json output.json --mirror horizontal

# Multiple transformations
python3 main.py --cli --transform input.json output.json \
    --translate 100 50 --scale 1.5 1.5 --rotate 30
```

## File Format

### Action File Structure

```json
{
  "metadata": {
    "version": "1.0",
    "created": "2024-01-01T12:00:00",
    "total_actions": 5,
    "duration": 10.5
  },
  "actions": [
    {
      "type": "click",
      "x": 100,
      "y": 200,
      "button": "left",
      "timestamp": 0.0,
      "absolute_time": "2024-01-01T12:00:00"
    }
  ]
}
```

### Action Properties
- **type**: Always "click" for mouse actions
- **x, y**: Screen coordinates
- **button**: "left", "right", or "middle"
- **timestamp**: Relative time from recording start (seconds)
- **absolute_time**: ISO format timestamp

## Advanced Workflows

### Workflow 1: Pattern Creation and Replication

1. **Record a basic pattern**:
   ```bash
   python3 main.py --cli --record pattern.json
   ```

2. **Create variations using transformations**:
   ```bash
   # Create larger version
   python3 main.py --cli --transform pattern.json pattern_large.json --scale 2.0 2.0
   
   # Create rotated version
   python3 main.py --cli --transform pattern.json pattern_rotated.json --rotate 90
   
   # Create mirrored version
   python3 main.py --cli --transform pattern.json pattern_mirrored.json --mirror vertical
   ```

3. **Play back all variations**:
   ```bash
   python3 main.py --cli --play pattern_large.json --speed 0.5
   python3 main.py --cli --play pattern_rotated.json
   python3 main.py --cli --play pattern_mirrored.json
   ```

### Workflow 2: Multi-Screen Setup

1. **Record on primary screen**:
   ```bash
   python3 main.py --cli --record primary_screen.json
   ```

2. **Adapt for secondary screen**:
   ```bash
   # Translate to secondary screen (assuming 1920px offset)
   python3 main.py --cli --transform primary_screen.json secondary_screen.json \
       --translate 1920 0
   ```

3. **Play on appropriate screen**:
   ```bash
   python3 main.py --cli --play secondary_screen.json --no-safe-mode
   ```

### Workflow 3: Automated Testing Integration

```bash
#!/bin/bash
# test_sequence.sh

# Record test sequence
echo "Recording test sequence..."
python3 main.py --cli --record test_sequence.json

# Create scaled version for different resolutions
python3 main.py --cli --transform test_sequence.json test_1080p.json \
    --scale 1.0 1.0

python3 main.py --cli --transform test_sequence.json test_720p.json \
    --scale 0.67 0.67

# Run tests at different speeds
echo "Running fast test..."
python3 main.py --cli --play test_1080p.json --speed 3.0

echo "Running slow test..."
python3 main.py --cli --play test_1080p.json --speed 0.5
```

## Best Practices

### Recording Best Practices

1. **Plan your actions**: Think through the sequence before recording
2. **Use consistent timing**: Maintain steady rhythm for natural playback
3. **Minimize movements**: Record only necessary clicks
4. **Test in safe environment**: Use a test application or safe area
5. **Save frequently**: Use descriptive filenames and save important recordings

### Transformation Best Practices

1. **Preview before applying**: Use GUI preview to check transformations
2. **Apply incrementally**: Make small changes and test between
3. **Keep originals**: Always work from copies of your original recordings
4. **Document changes**: Use descriptive output filenames
5. **Test on target environment**: Verify transformations work where needed

### Playback Best Practices

1. **Enable safe mode**: Protect against accidental clicks outside screen
2. **Start with slow speed**: Test at 0.5x speed before full speed
3. **Use emergency stop**: Know that ESC key stops playback immediately
4. **Clear workspace**: Ensure target applications are ready
5. **Monitor progress**: Watch for unexpected behavior during playback

## Safety Considerations

### Screen Protection
- Always enable safe mode when testing
- Verify screen bounds match your actual resolution
- Test in isolated environments before production use

### Application Safety
- Close important applications before playback
- Save work before running automated sequences
- Use test applications when possible

### Timing Considerations
- Account for application response times
- Add delays between critical actions
- Test on target hardware/software configuration

## Troubleshooting Common Issues

### Recording Issues

**Problem**: No actions recorded
- **Solution**: Check if Python has accessibility permissions
- **macOS**: System Preferences → Security & Privacy → Privacy → Accessibility
- **Linux**: Verify X11 permissions and desktop environment compatibility

**Problem**: Duplicate actions recorded
- **Solution**: Increase debounce threshold in recording options

### Transformation Issues

**Problem**: Actions move outside screen
- **Solution**: Use "Fit to Screen" or adjust transformation parameters

**Problem**: Pattern doesn't look right after transformation
- **Solution**: Check transformation order - apply translate last for positioning

### Playback Issues

**Problem**: Clicks not registering
- **Solution**: Disable fast user switching, check application focus

**Problem**: Wrong click locations
- **Solution**: Verify screen resolution, check display scaling settings

**Problem**: Playback too fast/slow
- **Solution**: Adjust speed multiplier, account for system performance

## Integration Examples

### Python Script Integration

```python
#!/usr/bin/env python3
from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer

# Record actions programmatically
recorder = MouseRecorder()
recorder.start_recording()
# ... user performs actions ...
recorder.stop_recording()
actions = recorder.get_actions()

# Transform actions
transformer = CoordinateTransformer()
transformations = [
    transformer.create_translation_transform(100, 50),
    transformer.create_scale_transform(1.5, 1.5)
]
transformed = transformer.transform_actions(actions, transformations)

# Play back actions
player = ActionPlayer()
player.load_actions(transformed)
player.set_speed(2.0)
player.play()
```

### Batch Processing

```bash
#!/bin/bash
# Process multiple action files

for file in recordings/*.json; do
    base=$(basename "$file" .json)
    
    # Create transformed versions
    python3 main.py --cli --transform "$file" "processed/${base}_large.json" \
        --scale 1.5 1.5
    
    python3 main.py --cli --transform "$file" "processed/${base}_rotated.json" \
        --rotate 90
    
    echo "Processed $file"
done
```

This comprehensive usage guide should help you get the most out of the Mouse Automation Toolkit. Start with simple recording and playback, then gradually explore the transformation and automation features as you become more comfortable with the interface.