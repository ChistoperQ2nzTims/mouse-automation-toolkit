# Mouse Automation Toolkit

A comprehensive, production-ready tool for recording, transforming, and replaying mouse actions with advanced features and cross-platform support.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## ✨ Features

### 🔴 **Recording System**
- High-precision mouse click recording with microsecond timestamps
- Real-time action display and monitoring
- Intelligent debounce filtering to prevent accidental duplicate clicks
- Support for all mouse buttons (left, right, middle)
- JSON-based action storage with metadata

### 🔄 **Transformation Engine**
- **Translation**: Move patterns to any screen position
- **Scaling**: Resize patterns with custom aspect ratios
- **Rotation**: Rotate patterns around any pivot point
- **Mirroring**: Flip patterns horizontally, vertically, or both
- **Batch Operations**: Apply multiple transformations in sequence
- **Fit-to-Screen**: Automatically adapt patterns for different screen sizes

### ▶️ **Playback System**
- Precise timing reproduction with configurable speed control (0.1x to 5.0x)
- Loop mode for continuous repetition
- Emergency stop functionality (ESC key)
- Safe mode with screen boundary protection
- Progress monitoring and time estimation

### 🖥️ **Dual Interface**
- **GUI Mode**: Intuitive 5-tab interface with real-time previews
- **CLI Mode**: Full command-line automation support for scripting
- Cross-platform compatibility (Windows, macOS, Linux)

### 🛡️ **Safety Features**
- Screen boundary validation
- Accessibility permission handling
- Safe mode operation
- Action validation and warnings

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install PyAutoGUI>=0.9.54 pynput>=1.7.6

# Clone and install
git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
cd mouse-automation-toolkit
pip install -e .
```

### GUI Mode (Recommended)

```bash
python main.py
```

### CLI Mode

```bash
# Record mouse actions
python main.py --cli --record my_actions.json

# Play back actions
python main.py --cli --play my_actions.json --speed 2.0

# Transform actions
python main.py --cli --transform input.json output.json --translate 100 50 --rotate 45
```

## 📋 Requirements

- **Python**: 3.7 or higher
- **OS**: Windows 10+, macOS 10.12+, Linux (Ubuntu 18.04+)
- **Dependencies**: PyAutoGUI, pynput, tkinter (included with Python)
- **Permissions**: Accessibility permissions may be required on macOS/Linux

## 🎯 Use Cases

- **UI Testing**: Automate repetitive click sequences for testing applications
- **Data Entry**: Record and replay complex data entry patterns
- **Gaming**: Create macros for legitimate gaming automation
- **Presentation**: Automate demonstration click sequences
- **Training**: Create interactive tutorials with recorded mouse patterns
- **Accessibility**: Assist users with repetitive mouse tasks

## 📖 Documentation

- **[Installation Guide](docs/installation.md)**: Detailed setup instructions for all platforms
- **[Usage Guide](docs/usage.md)**: Comprehensive feature walkthrough and workflows
- **[API Documentation](docs/api.md)**: Complete programming interface reference

## 🏗️ Architecture

```
mouse-automation-toolkit/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
├── src/                   # Core modules
│   ├── __init__.py        # Package initialization
│   ├── recorder.py        # Mouse action recording
│   ├── transformer.py     # Coordinate transformations
│   ├── player.py         # Action playback
│   └── gui.py            # Tkinter GUI interface
├── examples/              # Usage examples
│   ├── basic_usage.py     # Simple recording/playback
│   ├── advanced_transform.py  # Complex transformations
│   └── sample_actions.json    # Sample data file
├── tests/                 # Unit tests
│   ├── test_recorder.py   # Recording functionality tests
│   ├── test_transformer.py    # Transformation tests
│   └── test_player.py     # Playback tests
└── docs/                  # Documentation
    ├── installation.md    # Setup guide
    ├── usage.md          # User manual
    └── api.md            # API reference
```

## 🔧 Core Classes

### MouseRecorder
Records mouse actions with precise timing and coordinates.

```python
from src.recorder import MouseRecorder

recorder = MouseRecorder()
recorder.start_recording()
# ... perform mouse actions ...
recorder.stop_recording()
actions = recorder.get_actions()
recorder.save_to_file('recording.json')
```

### CoordinateTransformer
Applies geometric transformations to recorded actions.

```python
from src.transformer import CoordinateTransformer

transformer = CoordinateTransformer()
transformations = [
    transformer.create_translation_transform(100, 50),
    transformer.create_scale_transform(1.5, 1.5),
    transformer.create_rotation_transform(45)
]
result = transformer.transform_actions(actions, transformations)
```

### ActionPlayer
Replays recorded actions with timing and safety controls.

```python
from src.player import ActionPlayer

player = ActionPlayer()
player.load_actions(actions)
player.set_speed(2.0)  # 2x speed
player.set_safe_mode(True)
player.play()
```

## 🎮 GUI Interface

The toolkit features a comprehensive 5-tab GUI interface:

1. **🔴 Record**: Start/stop recording with real-time action display
2. **🔄 Transform**: Apply translations, scaling, rotation, and mirroring
3. **▶️ Playback**: Control action replay with speed and safety options
4. **👁 Preview**: View statistics and validate actions before playback
5. **⚙️ Settings**: Configure preferences, hotkeys, and safety features

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python tests/test_recorder.py
python tests/test_transformer.py
python tests/test_player.py

# Test with coverage
pip install coverage
coverage run -m pytest tests/
coverage report
```

## 📊 Examples

### Basic Workflow

```python
from src import MouseRecorder, CoordinateTransformer, ActionPlayer

# 1. Record actions
recorder = MouseRecorder()
recorder.start_recording()
# ... user clicks ...
recorder.stop_recording()

# 2. Transform actions
transformer = CoordinateTransformer()
scaled_actions = transformer.transform_actions(
    recorder.get_actions(),
    [transformer.create_scale_transform(1.5, 1.5)]
)

# 3. Play back transformed actions
player = ActionPlayer()
player.load_actions(scaled_actions)
player.play()
```

### Advanced Transformation

```python
# Create a complex transformation chain
transformations = [
    transformer.create_translation_transform(-center_x, -center_y),  # Center
    transformer.create_scale_transform(2.0, 1.5),                   # Scale
    transformer.create_rotation_transform(45),                      # Rotate
    transformer.create_mirror_transform('horizontal'),              # Mirror
    transformer.create_translation_transform(400, 300)             # Position
]

result = transformer.transform_actions(original_actions, transformations)
```

## 🔒 Security and Safety

- **Safe Mode**: Prevents clicks outside screen boundaries
- **Emergency Stop**: ESC key immediately stops all playback
- **Permission Handling**: Proper accessibility permission requests
- **Validation**: Pre-playback action validation with warnings
- **Screen Protection**: Configurable screen bounds checking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone for development
git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
cd mouse-automation-toolkit

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest coverage

# Run tests
pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyAutoGUI**: Cross-platform GUI automation
- **pynput**: Input monitoring and control
- **tkinter**: GUI framework
- The Python community for excellent libraries and documentation

## 📞 Support

- **Documentation**: Check the `docs/` directory for comprehensive guides
- **Issues**: Report bugs and request features on GitHub
- **Examples**: See `examples/` for usage patterns
- **Tests**: Review `tests/` for implementation examples

---

**Mouse Automation Toolkit** - Making mouse automation simple, powerful, and safe. 🖱️✨