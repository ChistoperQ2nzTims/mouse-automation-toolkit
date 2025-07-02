# Usage Guide

## Overview

The Mouse Automation Toolkit provides two ways to interact with the system:

1. **GUI Application** - User-friendly graphical interface
2. **Command Line Interface** - For scripting and automation

## GUI Application

### Starting the GUI

Launch the graphical interface:

```bash
python main.py
```

### Main Interface

The GUI consists of several sections:

#### Toolbar
- **Record** (🔴) - Start/stop recording mouse actions
- **Clear** (🗑️) - Clear all recorded actions
- **Transform** (🔄) - Apply coordinate transformations
- **Play** (▶️) - Start/stop playback
- **Pause** (⏸️) - Pause/resume playback
- **Stop** (⏹️) - Stop current playback

#### Tabs

**Actions Tab:**
- View recorded actions in a table
- See action details (type, position, button, delay)
- Select actions for detailed information

**Settings Tab:**
- Configure recording options (smart recording, minimum delay)
- Set playback options (delay multiplier, random delays, loop count)
- Adjust screen dimensions for transformations

**Log Tab:**
- Monitor application activity
- Debug issues
- Save logs to file

### Basic Workflow

#### 1. Recording Actions

1. Click **Record** button or press **F9**
2. Perform mouse actions you want to record
3. Click **Stop Recording** or press **F9** again
4. Review recorded actions in the Actions tab

**Recording Tips:**
- Enable "Smart Recording" to filter duplicate actions
- Adjust "Min Delay" to control sensitivity
- Use clear, deliberate movements for better results

#### 2. Transforming Coordinates

1. Select recorded actions
2. Click **Transform** button
3. Choose transformation type:
   - **Translate:** Move actions by X,Y offset
   - **Scale:** Resize pattern by scale factors
   - **Rotate:** Rotate around center point
   - **Mirror:** Flip horizontally or vertically
4. Apply transformation

**Transform Examples:**
- Move pattern 100 pixels right: Translate(100, 0)
- Double pattern size: Scale(2.0, 2.0)
- Rotate 45 degrees: Rotate(45)
- Mirror left-to-right: Mirror Horizontal

#### 3. Playing Back Actions

1. Ensure actions are loaded/recorded
2. Configure playback settings:
   - **Delay Multiplier:** Speed up (< 1.0) or slow down (> 1.0)
   - **Random Delay:** Add variation to timing
   - **Loop Count:** Repeat sequence multiple times
3. Click **Play** or press **F5**
4. Use **Pause**/**Stop** as needed

**Playback Tips:**
- Validate actions before playback
- Use preview to verify coordinates
- Start with slower speeds for testing
- Keep mouse away from screen corners (failsafe)

### File Management

#### Saving Profiles
- **File → Save Profile** (Ctrl+S) - Save to current file
- **File → Save Profile As** - Save with new name
- Profiles are saved as JSON files

#### Loading Profiles
- **File → Open Profile** (Ctrl+O) - Load existing profile
- Supports JSON files created by the toolkit

#### Profile Format
Profiles contain:
- Action sequences with timing
- Metadata (recording date, duration)
- Action details (coordinates, buttons, delays)

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| F9 | Toggle recording |
| F5 | Start/stop playback |
| Esc | Emergency stop |
| Ctrl+N | New profile |
| Ctrl+O | Open profile |
| Ctrl+S | Save profile |

### Advanced Features

#### Action Validation
- **Tools → Validate Actions** - Check for issues
- Detects out-of-bounds coordinates
- Warns about long delays
- Identifies unknown button types

#### Action Preview
- **Tools → Preview Actions** - See action summary
- Review coordinates before playback
- Estimate playback duration

## Command Line Interface

### Basic Commands

#### Recording Actions
```bash
python main.py --record actions.json
```
- Records mouse actions to JSON file
- Press Enter to stop recording
- Use Ctrl+C for emergency stop

#### Playing Actions
```bash
python main.py --play actions.json
```
- Plays actions from JSON file
- Validates actions before playback
- Shows progress during playback

#### Validating Actions
```bash
python main.py --validate actions.json
```
- Checks actions for issues
- Reports warnings and errors
- Returns exit code 0 for valid actions

### Playback Options

#### Delay Multiplier
```bash
python main.py --play actions.json --delay 0.5
```
- Multiplies all delays by 0.5 (2x speed)
- Use > 1.0 to slow down, < 1.0 to speed up

#### Loop Playback
```bash
python main.py --play actions.json --loop 3
```
- Repeats the sequence 3 times
- Use 0 for infinite loop (Ctrl+C to stop)

### Transformations

Apply transformations during playback:

#### Translation
```bash
python main.py --play actions.json --translate 100,50
```
- Moves all actions 100 pixels right, 50 pixels down

#### Scaling
```bash
python main.py --play actions.json --scale 1.5,1.2
```
- Scales X coordinates by 1.5, Y coordinates by 1.2

#### Rotation
```bash
python main.py --play actions.json --rotate 45
```
- Rotates all coordinates 45 degrees around screen center

#### Combined Transformations
```bash
python main.py --play actions.json --translate 50,50 --scale 2.0,2.0 --rotate 30
```
- Applies multiple transformations in sequence

### Advanced CLI Usage

#### Verbose Logging
```bash
python main.py --play actions.json --log-level DEBUG
```
- Shows detailed operation information
- Useful for troubleshooting

#### Batch Processing
```bash
# Record multiple sequences
python main.py --record seq1.json
python main.py --record seq2.json

# Transform and play
python main.py --play seq1.json --scale 0.5,0.5 --delay 2.0
python main.py --play seq2.json --translate 200,0 --loop 2
```

## Programmatic Usage

### Python API

Import modules for custom scripts:

```python
from src.recorder import MouseRecorder
from src.player import MousePlayer
from src.transformer import CoordinateTransformer

# Create components
recorder = MouseRecorder()
player = MousePlayer()
transformer = CoordinateTransformer()

# Record actions
recorder.start_recording()
# ... wait for user input ...
recorder.stop_recording()
actions = recorder.get_actions()

# Transform actions
transformed = transformer.translate(actions, 100, 50)

# Play actions
player.play_actions(transformed, delay_multiplier=0.5)
```

See [API Documentation](api.md) for complete reference.

## Best Practices

### Recording

1. **Plan your sequence** before recording
2. **Use consistent timing** for better results
3. **Enable smart recording** to reduce noise
4. **Record at normal speed** - adjust playback speed later
5. **Test in safe areas** first

### Transformations

1. **Start with small changes** to verify behavior
2. **Use preview** to check results before applying
3. **Chain transformations** for complex modifications
4. **Keep backups** of original recordings

### Playback

1. **Validate before playing** to catch issues
2. **Start with slow speeds** for testing
3. **Use appropriate loop counts** to avoid infinite runs
4. **Monitor system resources** during long sequences
5. **Keep emergency stop accessible** (Esc key)

### Troubleshooting

#### Recording Issues
- **No actions recorded:** Check permissions and mouse movement
- **Too many actions:** Increase minimum delay or enable smart recording
- **Inaccurate timing:** Ensure stable system performance

#### Playback Issues
- **Actions out of bounds:** Check screen resolution and scaling
- **Wrong timing:** Adjust delay multiplier
- **Unexpected behavior:** Validate actions and check for warnings

#### Performance Issues
- **High CPU usage:** Reduce recording sensitivity
- **Slow playback:** Check delay settings and system load
- **Memory usage:** Clear actions when not needed

## Examples

### Example 1: Simple Automation
```bash
# Record a sequence
python main.py --record drawing.json

# Play it back slower
python main.py --play drawing.json --delay 2.0

# Scale it up and repeat
python main.py --play drawing.json --scale 1.5,1.5 --loop 3
```

### Example 2: Position Adjustment
```bash
# Record actions in one area
python main.py --record actions.json

# Play in different area (translated)
python main.py --play actions.json --translate 200,100
```

### Example 3: Pattern Manipulation
```bash
# Record a pattern
python main.py --record pattern.json

# Create variations
python main.py --play pattern.json --scale 0.5,0.5          # Smaller
python main.py --play pattern.json --rotate 90              # Rotated
python main.py --play pattern.json --translate 100,0 --scale 2.0,1.0  # Stretched
```

## Tips and Tricks

1. **Use the preview feature** extensively to avoid mistakes
2. **Save profiles frequently** to preserve work
3. **Test transformations** on copies of important recordings
4. **Use keyboard shortcuts** for efficient workflow
5. **Monitor the log tab** for troubleshooting information
6. **Adjust screen dimensions** in settings for accurate transformations
7. **Use validation** to catch potential issues early
8. **Keep recording sessions short** for easier management