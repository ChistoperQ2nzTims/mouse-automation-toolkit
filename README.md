# Mouse Automation Toolkit 🐭🤖

A complete toolkit for recording, transforming, and replaying mouse actions with precision and flexibility.

## ✨ Features

### 📹 **Mouse Action Recording**
- Record mouse clicks with exact coordinates, timing, and button types
- Smart duplicate removal for cleaner recordings
- Support for left, right, and middle mouse buttons
- Precise timestamp tracking for natural replay timing
- Save recordings to JSON format with metadata

### 🔄 **Coordinate Transformations**
- **Translation**: Move coordinates by X/Y offset
- **Scaling**: Resize coordinate space with custom factors
- **Rotation**: Rotate around any center point
- **Mirroring**: Flip horizontally or vertically
- **Fit-to-Screen**: Automatically adapt to different screen sizes
- **Transformation Chains**: Apply multiple transformations in sequence

### ▶️ **Intelligent Playback**
- Customizable playback speed (0.1x to 5.0x)
- Loop support (single, multiple, or infinite)
- Random delay injection for natural timing
- Real-time progress monitoring
- Pause/resume functionality during playback

### 🛡️ **Safety Features**
- **ESC Key Emergency Stop**: Instantly halt playback
- **PyAutoGUI Failsafe**: Move mouse to corner to trigger stop
- **Safe Mode**: Configurable safety mechanisms
- **Bounds Checking**: Validate coordinates against screen limits
- **Cross-platform Compatibility**: Windows, macOS, Linux

### 🖥️ **User-Friendly GUI**
- Intuitive tabbed interface
- Real-time action preview
- Visual coordinate transformation feedback
- Comprehensive playback controls
- Detailed logging and progress tracking

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

3. **Launch the application:**
   ```bash
   python main.py
   ```

### Basic Usage

1. **Record Actions:**
   - Click "Start Recording" in the Record tab
   - Perform mouse clicks on your screen
   - Click "Stop Recording" when finished

2. **Transform Coordinates (Optional):**
   - Switch to the Transform tab
   - Apply translations, scaling, rotation, or mirroring
   - Preview changes before applying

3. **Replay Actions:**
   - Go to the Play tab
   - Adjust speed, loops, and delay settings
   - Click "Play" to start playback
   - Press ESC to stop anytime

## 📁 Project Structure

```
mouse-automation-toolkit/
├── README.md                 # Project overview and quick start
├── requirements.txt          # Python dependencies
├── setup.py                 # Package installation configuration
├── main.py                  # Application entry point
├── src/                     # Core source code
│   ├── __init__.py         # Package initialization
│   ├── recorder.py         # Mouse action recording
│   ├── transformer.py      # Coordinate transformations
│   ├── player.py           # Action playback engine
│   └── gui.py              # Graphical user interface
├── examples/               # Usage examples and demos
│   ├── basic_usage.py      # Simple recording/playback example
│   ├── advanced_transform.py # Transformation demonstrations
│   └── sample_actions.json # Sample action file
├── tests/                  # Comprehensive test suite
│   ├── test_recorder.py    # Recording functionality tests
│   ├── test_transformer.py # Transformation tests
│   └── test_player.py      # Playback tests
└── docs/                   # Complete documentation
    ├── installation.md     # Detailed installation guide
    ├── usage.md           # Comprehensive usage guide
    └── api.md             # Full API documentation
```

## 🛠️ Technologies

- **Python 3.8+**: Core programming language
- **PyAutoGUI**: GUI automation and mouse control
- **pynput**: Real-time input event capture
- **tkinter**: Cross-platform GUI framework
- **JSON**: Lightweight data serialization
- **Threading**: Non-blocking operation support

## 💡 Use Cases

### **Automation & Testing**
- Automate repetitive GUI tasks
- Create UI test scripts
- Generate user interaction recordings
- Stress test applications with repeated actions

### **Accessibility & Training**
- Create step-by-step interaction guides
- Demonstrate software usage
- Assist users with motor difficulties
- Generate training materials

### **Content Creation**
- Record click sequences for tutorials
- Create interactive demonstrations
- Generate precise UI interaction data
- Develop user experience studies

### **Cross-Platform Development**
- Adapt interactions for different screen sizes
- Test responsive interfaces
- Validate UI consistency across platforms
- Create device-specific interaction patterns

## 🎯 Advanced Features

### **Smart Recording**
- Automatic duplicate detection and removal
- Configurable tolerance for similar actions
- Intelligent timing calculation
- Metadata preservation

### **Flexible Transformations**
- Mathematical precision in coordinate operations
- Preservation of timing and button information
- Batch transformation support
- Undo/redo capability through file operations

### **Robust Playback**
- Thread-safe operation
- Real-time monitoring and control
- Adaptive timing based on system performance
- Comprehensive error handling

## 📚 Documentation

- **[Installation Guide](docs/installation.md)**: Platform-specific setup instructions
- **[Usage Guide](docs/usage.md)**: Comprehensive feature walkthrough
- **[API Documentation](docs/api.md)**: Complete programming interface reference

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test files
python -m unittest tests.test_recorder
python -m unittest tests.test_transformer
python -m unittest tests.test_player

# Run with verbose output
python -m unittest discover tests/ -v
```

## 🔧 Development

### **Setup Development Environment**
```bash
git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
cd mouse-automation-toolkit
pip install -e .
```

### **Run Examples**
```bash
# Basic usage demonstration
python examples/basic_usage.py

# Advanced transformation showcase
python examples/advanced_transform.py
```

## 🔒 Security & Privacy

- **Local Operation**: All processing happens on your machine
- **No Network Communication**: No data transmitted to external servers
- **File-Based Storage**: Actions saved as human-readable JSON
- **Configurable Safety**: Multiple layers of user protection
- **Open Source**: Full code transparency and auditability

## 🤝 Contributing

We welcome contributions! Areas for enhancement:

- Additional transformation algorithms
- New input device support
- Enhanced GUI features
- Performance optimizations
- Documentation improvements
- Platform-specific enhancements

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is designed for legitimate automation, testing, and accessibility purposes. Users are responsible for:

- Complying with applicable laws and regulations
- Respecting software terms of service
- Using the tool ethically and responsibly
- Ensuring actions don't harm systems or data

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: Comprehensive guides in the `docs/` directory
- **Examples**: Working code samples in the `examples/` directory
- **Community**: Join discussions in GitHub Discussions

---

**Mouse Automation Toolkit** - Empowering precise, flexible, and safe mouse automation for everyone. 🚀