# Installation Guide - Mouse Automation Toolkit

## System Requirements

### Operating System Support
- **Windows**: Windows 10/11 (recommended), Windows 7+ (basic support)
- **macOS**: macOS 10.12+ (Sierra and later)
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+, or equivalent

### Python Requirements
- **Python Version**: 3.7 or higher (3.9+ recommended)
- **Architecture**: 64-bit preferred, 32-bit supported

### Hardware Requirements
- **RAM**: Minimum 512MB, 2GB+ recommended
- **Storage**: 50MB for installation, additional space for recorded actions
- **Display**: Any resolution supported, 1920x1080+ recommended for GUI

## Installation Methods

### Method 1: Using pip (Recommended)

```bash
# Install from source (if published to PyPI)
pip install mouse-automation-toolkit

# Or install from local directory
pip install .
```

### Method 2: Manual Installation

1. **Clone or download the repository**:
   ```bash
   git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
   cd mouse-automation-toolkit
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package**:
   ```bash
   python setup.py install
   ```

### Method 3: Development Installation

For developers who want to modify the code:

```bash
# Clone the repository
git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
cd mouse-automation-toolkit

# Install in development mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

## Dependencies

### Core Dependencies
- **PyAutoGUI** (≥0.9.54): GUI automation and mouse control
- **pynput** (≥1.7.6): Mouse and keyboard event monitoring

### Built-in Dependencies (included with Python)
- **tkinter**: GUI framework
- **json**: Data serialization
- **threading**: Multi-threading support
- **time**: Timing functions
- **math**: Mathematical operations

### Optional Dependencies
- **pytest** (for running tests): `pip install pytest`
- **coverage** (for test coverage): `pip install coverage`

## Platform-Specific Instructions

### Windows Installation

1. **Install Python** (if not already installed):
   - Download from [python.org](https://python.org)
   - During installation, check "Add Python to PATH"

2. **Install the toolkit**:
   ```cmd
   pip install PyAutoGUI>=0.9.54 pynput>=1.7.6
   python -m pip install mouse-automation-toolkit
   ```

3. **Security considerations**:
   - Windows Defender may flag PyAutoGUI - add exception if needed
   - Run as Administrator if permission issues occur

### macOS Installation

1. **Install Python** (if not using system Python):
   ```bash
   # Using Homebrew (recommended)
   brew install python

   # Or download from python.org
   ```

2. **Install dependencies**:
   ```bash
   pip3 install PyAutoGUI>=0.9.54 pynput>=1.7.6
   ```

3. **Grant accessibility permissions**:
   - System Preferences → Security & Privacy → Privacy
   - Check "Accessibility" and add Terminal/Python to allowed apps

### Linux Installation

1. **Install Python and dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-tk python3-dev

   # CentOS/RHEL
   sudo yum install python3 python3-pip tkinter python3-devel

   # Arch Linux
   sudo pacman -S python python-pip tk
   ```

2. **Install X11 dependencies** (for PyAutoGUI):
   ```bash
   # Ubuntu/Debian
   sudo apt install scrot python3-xlib

   # CentOS/RHEL
   sudo yum install scrot python3-xlib

   # Or use alternative screenshot tools
   sudo apt install gnome-screenshot  # GNOME
   sudo apt install imagemagick       # ImageMagick
   ```

3. **Install the toolkit**:
   ```bash
   pip3 install PyAutoGUI>=0.9.54 pynput>=1.7.6
   ```

## Verification

### Test Installation

1. **Test core imports**:
   ```python
   python3 -c "from src import MouseRecorder, CoordinateTransformer, ActionPlayer; print('Installation successful!')"
   ```

2. **Test GUI (optional)**:
   ```python
   python3 -c "import tkinter; tkinter.Tk().quit(); print('GUI support available')"
   ```

3. **Run example**:
   ```bash
   python3 examples/basic_usage.py
   ```

### Run Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test file
python3 tests/test_recorder.py

# Run with coverage
coverage run -m pytest tests/
coverage report
```

## Configuration

### GUI Configuration
The toolkit will use your system's default GUI settings. For best experience:
- Use a desktop environment with proper window manager
- Ensure adequate screen resolution (1024x768 minimum)
- Configure accessibility permissions as needed

### Command Line Usage
```bash
# Launch GUI
python3 main.py

# CLI recording
python3 main.py --cli --record actions.json

# CLI playback
python3 main.py --cli --play actions.json

# Get help
python3 main.py --help
```

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'pynput'"**
   ```bash
   pip install pynput>=1.7.6
   ```

2. **"ModuleNotFoundError: No module named 'PyAutoGUI'"**
   ```bash
   pip install PyAutoGUI>=0.9.54
   ```

3. **GUI not working on Linux**
   ```bash
   sudo apt install python3-tk
   ```

4. **Permission denied errors**
   - Run with appropriate permissions
   - On macOS: Grant accessibility permissions
   - On Linux: Check X11 forwarding if using SSH

5. **PyAutoGUI fails on macOS**
   - Grant accessibility permissions to Python/Terminal
   - System Preferences → Security & Privacy → Privacy → Accessibility

6. **Clicks not working properly**
   - Check screen resolution and scaling
   - Verify PyAutoGUI compatibility with your desktop environment
   - Try running with `--no-safe-mode` for testing

### Performance Issues

1. **Slow GUI response**
   - Close other applications to free memory
   - Use lower recording frequency
   - Reduce the number of transformation previews

2. **High CPU usage during recording**
   - Increase debounce threshold
   - Record shorter sessions
   - Close unnecessary background applications

### Platform-Specific Issues

**Windows:**
- Antivirus software may interfere - add exceptions
- Windows scaling may affect coordinates
- UAC prompts may block automation

**macOS:**
- Accessibility permissions required for automation
- SIP (System Integrity Protection) may block some operations
- Mission Control/Spaces may interfere with coordinates

**Linux:**
- X11 vs Wayland compatibility varies
- Desktop environment differences
- Permission issues with /dev/input devices

## Uninstallation

```bash
# If installed via pip
pip uninstall mouse-automation-toolkit

# Remove dependencies (optional)
pip uninstall PyAutoGUI pynput

# Remove downloaded files
rm -rf mouse-automation-toolkit/
```

## Getting Help

- **Documentation**: Check `docs/usage.md` and `docs/api.md`
- **Examples**: Review files in `examples/` directory
- **Issues**: Report bugs on GitHub repository
- **Community**: Join discussions in the project forum

For additional support, please check the project's GitHub repository for the latest documentation and community discussions.