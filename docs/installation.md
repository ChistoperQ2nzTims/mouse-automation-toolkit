# Installation Guide

## System Requirements

- Python 3.8 or higher
- Operating System: Windows, macOS, or Linux
- Display server with GUI support
- Mouse/pointing device

## Dependencies

The toolkit requires the following Python packages:

- `pyautogui>=0.9.54` - GUI automation
- `pynput>=1.7.6` - Input monitoring and control
- `numpy>=1.21.0` - Numerical operations for transformations
- `Pillow>=8.3.0` - Image processing (PyAutoGUI dependency)
- `tkinter` - GUI framework (usually included with Python)

## Installation Methods

### Method 1: Install from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
   cd mouse-automation-toolkit
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the package:**
   ```bash
   pip install -e .
   ```

### Method 2: Direct Installation

If the package is available on PyPI:

```bash
pip install mouse-automation-toolkit
```

## Platform-Specific Setup

### Windows

1. **Install Python** from [python.org](https://python.org) or Microsoft Store
2. **No additional setup required** - all dependencies should install automatically
3. **Optional:** For better performance, ensure Windows is updated

### macOS

1. **Install Python** using Homebrew or from [python.org](https://python.org):
   ```bash
   brew install python
   ```

2. **Grant accessibility permissions:**
   - System Preferences → Security & Privacy → Privacy → Accessibility
   - Add Python or Terminal to the list of allowed applications
   - This is required for mouse control functionality

3. **Install Xcode Command Line Tools** (if not already installed):
   ```bash
   xcode-select --install
   ```

### Linux

1. **Install Python and dependencies:**
   ```bash
   # Ubuntu/Debian:
   sudo apt update
   sudo apt install python3 python3-pip python3-venv python3-tk
   sudo apt install python3-dev libxkbcommon-x11-0
   
   # Fedora:
   sudo dnf install python3 python3-pip python3-tkinter
   sudo dnf install python3-devel
   
   # Arch Linux:
   sudo pacman -S python python-pip tk
   ```

2. **Install X11 development packages** (if not already installed):
   ```bash
   # Ubuntu/Debian:
   sudo apt install libx11-dev libxtst6
   
   # Fedora:
   sudo dnf install libX11-devel libXtst
   ```

## Verification

After installation, verify everything works correctly:

1. **Test basic import:**
   ```python
   python -c "import src.recorder, src.player, src.transformer; print('✅ All modules imported successfully')"
   ```

2. **Test GUI dependencies:**
   ```python
   python -c "import tkinter; print('✅ Tkinter available')"
   ```

3. **Test automation dependencies:**
   ```python
   python -c "import pyautogui, pynput; print('✅ Automation libraries available')"
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Troubleshooting

### Common Issues

#### "Permission denied" errors on macOS
- **Solution:** Grant accessibility permissions as described in the macOS setup section
- **Alternative:** Run with sudo (not recommended for regular use)

#### "No module named 'tkinter'" error
- **Windows/macOS:** Reinstall Python with tkinter support
- **Linux:** Install python3-tk package as shown above

#### "Failed to connect to display" on Linux
- **Solution:** Ensure X11 is running and DISPLAY variable is set
- **For headless systems:** Install and configure Xvfb

#### PyAutoGUI failsafe triggers unexpectedly
- **Solution:** Move mouse away from screen corners, or disable failsafe:
  ```python
  import pyautogui
  pyautogui.FAILSAFE = False
  ```

#### High CPU usage during recording
- **Solution:** Increase minimum delay in recording settings
- **Alternative:** Enable smart recording to filter duplicate actions

### Performance Tips

1. **Reduce recording sensitivity** by increasing minimum delay
2. **Enable smart recording** to filter out unnecessary actions
3. **Use lower delay multipliers** for faster playback
4. **Close unnecessary applications** while recording/playing

### Getting Help

If you encounter issues not covered here:

1. **Check the logs** in the application's log tab
2. **Run with verbose logging:**
   ```bash
   python main.py --log-level DEBUG
   ```
3. **Check system requirements** and dependencies
4. **Search existing issues** on the project repository
5. **Create a new issue** with:
   - Your operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

## Development Setup

For developers who want to contribute:

1. **Clone and install in development mode:**
   ```bash
   git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
   cd mouse-automation-toolkit
   pip install -e ".[dev]"
   ```

2. **Install development dependencies:**
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

3. **Run tests:**
   ```bash
   pytest tests/
   ```

4. **Check code style:**
   ```bash
   black src/ tests/
   flake8 src/ tests/
   ```

## Next Steps

Once installation is complete:

1. **Read the [Usage Guide](usage.md)** to learn how to use the toolkit
2. **Check out the [API Documentation](api.md)** for programmatic usage
3. **Try the examples** in the `examples/` directory
4. **Explore the GUI application** by running `python main.py`