# Mouse Automation Toolkit 🐭🤖

A complete, production-ready mouse automation toolkit with recording, transformation, and replay capabilities. Perfect for automating repetitive tasks, testing applications, and creating interactive demonstrations.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit)

## ✨ Features

### 🎥 **Smart Recording**
- Record mouse clicks, movements, and scrolling with precise timing
- Hotkey support (F9 to start, F10 to stop)
- Automatic duplicate action removal
- Support for all mouse buttons (left, right, middle)
- Cross-platform input monitoring

### 🔄 **Advanced Transformations**
- **Translate**: Move actions to different screen positions
- **Scale**: Resize action patterns for different screen resolutions
- **Rotate**: Rotate action sequences around any point
- **Mirror**: Flip actions horizontally or vertically
- **Matrix Transformations**: Apply custom mathematical transformations
- **Screen Fitting**: Automatically adapt actions to different screen sizes
- **Chain Transformations**: Combine multiple transformations seamlessly

### ▶️ **Safe Playback**
- Configurable playback speed and timing
- Loop support with custom repetition counts
- Emergency stop functionality (ESC key)
- PyAutoGUI failsafe integration (move mouse to corner to stop)
- Action validation before playback
- Progress tracking and callbacks

### 🖥️ **GUI Interface**
- User-friendly Tkinter-based interface
- Real-time recording statistics
- Visual transformation preview
- Action management and editing
- Profile system for saving/loading configurations
- Comprehensive settings panel

### 🛡️ **Safety First**
- Built-in failsafe mechanisms
- Coordinate boundary checking
- Action validation and warnings
- Configurable safety timeouts
- Error handling and recovery

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
cd mouse-automation-toolkit

# Install dependencies
pip install -r requirements.txt

# Optional: Install as package
pip install -e .
```

### GUI Interface (Recommended)

```bash
python main.py
```

![GUI Screenshot](docs/screenshots/gui-interface.png)

### Command Line Usage

```bash
# Record mouse actions
python main.py --record my_actions.json --duration 10

# Play back actions
python main.py --play my_actions.json

# Transform actions
python main.py --transform input.json output.json --scale 1.5 1.5

# Advanced playback
python main.py --play actions.json --speed 2.0 --loops 3 --delay 0.5
```

### Python API

```python
from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer

# Record actions
recorder = MouseRecorder()
actions = recorder.record(duration=10.0)

# Transform coordinates
transformer = CoordinateTransformer()
scaled = transformer.scale(actions, 1.5, 1.5)
translated = transformer.translate(scaled, 100, 50)

# Play back with custom settings
player = ActionPlayer()
player.replay(translated, delay=0.5, speed_multiplier=2.0)

# Clean up
recorder.cleanup()
player.cleanup()
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Dependencies**:
  - `pyautogui>=0.9.54` - Mouse control and automation
  - `pynput>=1.7.6` - Input monitoring and hotkeys
  - `numpy>=1.21.0` - Coordinate transformations
  - `tkinter` - GUI interface (usually included with Python)

## 📖 Documentation

- 📘 [Installation Guide](docs/installation.md) - Detailed setup instructions
- 📗 [Usage Guide](docs/usage.md) - Comprehensive feature documentation
- 📙 [API Documentation](docs/api.md) - Complete API reference
- 🎯 [Examples](examples/) - Practical usage examples

## 🎬 Examples

### Basic Recording and Playback

```python
# Record user actions
recorder = MouseRecorder()
print("Recording for 5 seconds...")
actions = recorder.record(duration=5.0)
print(f"Recorded {len(actions)} actions")

# Save to file
recorder.save_to_file("demo.json", actions)

# Play back actions
player = ActionPlayer()
player.replay(actions, start_delay=3.0)
```

### Advanced Transformations

```python
# Chain multiple transformations
transforms = [
    {'type': 'translate', 'offset_x': 100, 'offset_y': 50},
    {'type': 'scale', 'scale_x': 1.2, 'scale_y': 1.2},
    {'type': 'rotate', 'angle_degrees': 45},
    {'type': 'mirror_horizontal'}
]

transformer = CoordinateTransformer()
result = transformer.chain_transforms(actions, transforms)
```

### Screen Resolution Adaptation

```python
# Fit actions to different screen sizes
fitted_1080p = transformer.fit_to_screen(actions, 1920, 1080)
fitted_4k = transformer.fit_to_screen(actions, 3840, 2160)
```

## 🏗️ Project Structure

```
mouse-automation-toolkit/
├── 📄 main.py                 # Entry point and CLI
├── 📄 requirements.txt        # Python dependencies
├── 📄 setup.py               # Package configuration
├── 📁 src/                   # Core modules
│   ├── 📄 __init__.py
│   ├── 📄 recorder.py        # Mouse action recording
│   ├── 📄 transformer.py     # Coordinate transformations
│   ├── 📄 player.py          # Action replay
│   └── 📄 gui.py             # GUI interface
├── 📁 examples/              # Usage examples
│   ├── 📄 basic_usage.py
│   ├── 📄 advanced_transform.py
│   └── 📄 sample_actions.json
├── 📁 tests/                 # Unit tests
│   ├── 📄 test_recorder.py
│   ├── 📄 test_transformer.py
│   └── 📄 test_player.py
└── 📁 docs/                  # Documentation
    ├── 📄 installation.md
    ├── 📄 usage.md
    └── 📄 api.md
```

## 🧪 Testing

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test module
python -m unittest tests.test_recorder -v

# Run core functionality test (with mocked dependencies)
python test_core.py
```

## 🔧 Configuration

### Hotkeys
- **F9**: Start recording
- **F10**: Stop recording  
- **ESC**: Emergency stop during playback

### Safety Settings
- **Failsafe**: Move mouse to screen corner to stop
- **Validation**: Check actions before playback
- **Boundary Checking**: Verify coordinates are within screen

### Performance Options
- **Duplicate Removal**: Filter redundant mouse movements
- **Speed Control**: Adjust playback timing
- **Batch Processing**: Handle multiple action files

## 🎯 Use Cases

### 🖥️ **Application Testing**
- Automate repetitive UI interactions
- Create reproducible test scenarios
- Validate application responsiveness

### 📊 **Demonstration Creation**
- Record interactive software demos
- Create tutorial sequences
- Generate consistent presentations

### ⚡ **Task Automation**
- Automate data entry workflows
- Streamline repetitive operations
- Create custom macros

### 🎮 **Game Automation**
- Record and replay game actions
- Create training sequences
- Automate repetitive game tasks

### 🔄 **Cross-Platform Migration**
- Adapt workflows to different screen resolutions
- Transform actions between operating systems
- Scale interactions for different devices

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone for development
git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
cd mouse-automation-toolkit

# Install in development mode
pip install -e .[dev]

# Install testing dependencies
pip install pytest pytest-cov

# Run tests
python -m pytest tests/ -v
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyAutoGUI** - Cross-platform mouse and keyboard automation
- **pynput** - Input monitoring and control
- **NumPy** - Mathematical transformations
- **Tkinter** - GUI framework

## 📞 Support

- 📖 Check the [Documentation](docs/)
- 🐛 Report issues on [GitHub Issues](https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit/issues)
- 💬 Join discussions in [GitHub Discussions](https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit/discussions)
- ⭐ Star the project if you find it helpful!

## 🚨 Important Notes

### Security Considerations
- This toolkit can control your mouse and keyboard
- Use responsibly and ensure you understand what recorded actions do
- Keep emergency stops enabled for safety
- Be cautious when running actions from unknown sources

### Platform-Specific Notes

#### Windows
- May require running as administrator for some applications
- Windows Defender might flag automation tools

#### macOS  
- Requires accessibility permissions for input monitoring
- System Preferences → Security & Privacy → Accessibility

#### Linux
- May need additional packages: `python3-tk`, `scrot`
- X11 environment required for GUI functionality

---

**Ready to automate?** 🚀 [Get started with the installation guide](docs/installation.md) or try the [basic examples](examples/basic_usage.py)!