# Mouse Automation Toolkit 🐭🤖

A comprehensive toolkit for recording, transforming, and replaying mouse actions automatically.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cross-platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit)

## ✨ Features

### 🎬 **Mouse Action Recording**
- Record mouse clicks, movements, and button presses
- Capture precise timing between actions
- Smart recording to filter duplicate actions
- Support for all mouse buttons (left, right, middle)
- Save recordings to JSON files with timestamps

### 🔄 **Coordinate Transformations**
- **Translation**: Move actions by X,Y offset
- **Scaling**: Resize patterns with custom scale factors
- **Rotation**: Rotate actions around any center point
- **Mirroring**: Flip actions horizontally or vertically
- **Chaining**: Combine multiple transformations
- **Normalization**: Fit actions to target dimensions
- **Custom matrices**: Apply advanced transformations

### ▶️ **Intelligent Playback**
- Replay actions with customizable timing
- Variable speed control (slow motion or fast forward)
- Loop playback with custom repeat counts
- Random delay variation for natural behavior
- Real-time progress monitoring
- Emergency stop functionality (ESC key)

### 🖥️ **User-Friendly Interface**
- Clean GUI built with tkinter
- Intuitive controls: Record, Transform, Replay
- Live action preview before playback
- Comprehensive logging and monitoring
- Profile management (save/load configurations)
- Keyboard shortcuts for efficient workflow

### 🔧 **Advanced Capabilities**
- Action validation and error checking
- Batch processing support
- Cross-platform compatibility
- Command-line interface for automation
- Comprehensive API for custom integrations
- Smart recording with duplicate filtering

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
   cd mouse-automation-toolkit
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Basic Usage

#### GUI Application
```bash
# Launch the graphical interface
python main.py
```

#### Command Line
```bash
# Record mouse actions
python main.py --record my_actions.json

# Play back actions
python main.py --play my_actions.json

# Apply transformations during playback
python main.py --play my_actions.json --translate 100,50 --scale 1.5,1.5
```

#### Python API
```python
from src.recorder import MouseRecorder
from src.player import MousePlayer
from src.transformer import CoordinateTransformer

# Record actions
recorder = MouseRecorder()
recorder.start_recording()
# ... perform mouse actions ...
recorder.stop_recording()

# Transform coordinates
transformer = CoordinateTransformer()
actions = recorder.get_actions()
transformed = transformer.translate(actions, 100, 50)

# Playback
player = MousePlayer()
player.play_actions(transformed, delay_multiplier=0.5)
```

## 📋 Requirements

- **Python 3.8+**
- **Operating System**: Windows, macOS, or Linux
- **Dependencies**:
  - PyAutoGUI (GUI automation)
  - pynput (input monitoring)
  - tkinter (GUI framework)
  - numpy (transformations)
  - Pillow (image processing)

## 🎯 Use Cases

- **UI Testing**: Automate repetitive interface testing
- **Data Entry**: Replay form filling sequences
- **Demonstrations**: Create consistent software demos
- **Gaming**: Automate repetitive in-game actions
- **Accessibility**: Assist users with motor difficulties
- **Workflow Automation**: Streamline repetitive tasks

## 📖 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Usage Guide](docs/usage.md)** - Complete user manual
- **[API Reference](docs/api.md)** - Programming interface documentation

## 🎮 Examples

### Recording and Playback
```bash
# Record a drawing sequence
python main.py --record drawing.json

# Replay at half speed
python main.py --play drawing.json --delay 2.0

# Replay with transformations
python main.py --play drawing.json --scale 2.0,2.0 --translate 100,0
```

### Coordinate Transformations
```python
# Load actions and apply transformations
transformer = CoordinateTransformer()

# Create a mirrored version
mirrored = transformer.mirror_horizontal(actions)

# Chain multiple transformations
transforms = [
    ('translate', {'offset_x': 50, 'offset_y': 50}),
    ('scale', {'scale_x': 1.5, 'scale_y': 1.5}),
    ('rotate', {'angle_degrees': 45})
]
result = transformer.chain_transforms(actions, transforms)
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **F9** | Toggle recording |
| **F5** | Start/stop playback |
| **Esc** | Emergency stop |
| **Ctrl+N** | New profile |
| **Ctrl+O** | Open profile |
| **Ctrl+S** | Save profile |

## 🛡️ Safety Features

- **Failsafe Mode**: Move mouse to screen corner to stop
- **Action Validation**: Check coordinates before playback
- **Emergency Stop**: ESC key immediately halts playback
- **Bounds Checking**: Prevent out-of-screen actions
- **Smart Recording**: Filter excessive mouse movements

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific tests:
```bash
python -m pytest tests/test_recorder.py
python -m pytest tests/test_transformer.py
python -m pytest tests/test_player.py
```

## 📁 Project Structure

```
mouse-automation-toolkit/
├── README.md                 # Project overview
├── requirements.txt          # Dependencies
├── setup.py                 # Package setup
├── main.py                  # Main entry point
├── src/                     # Source code
│   ├── __init__.py
│   ├── recorder.py          # Mouse recording functionality
│   ├── transformer.py       # Coordinate transformations
│   ├── player.py           # Action playback
│   └── gui.py              # GUI interface
├── examples/                # Usage examples
│   ├── basic_usage.py
│   ├── advanced_transform.py
│   └── sample_actions.json
├── tests/                   # Unit tests
│   ├── test_recorder.py
│   ├── test_transformer.py
│   └── test_player.py
└── docs/                    # Documentation
    ├── installation.md
    ├── usage.md
    └── api.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyAutoGUI](https://pyautogui.readthedocs.io/) for GUI automation
- Powered by [pynput](https://pynput.readthedocs.io/) for input monitoring
- UI created with [tkinter](https://docs.python.org/3/library/tkinter.html)
- Transformations using [NumPy](https://numpy.org/)

## 🐛 Issues and Support

- **Bug Reports**: [GitHub Issues](https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit/discussions)
- **Documentation**: Check the [docs](docs/) directory

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
  - Mouse recording and playback
  - Coordinate transformations
  - GUI and CLI interfaces
  - Comprehensive test suite
  - Complete documentation

---

Made with ❤️ using Python. **Happy Automating!** 🎉