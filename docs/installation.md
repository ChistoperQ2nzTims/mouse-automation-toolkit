# Installation Guide

## System Requirements

- **Python 3.8 or higher**
- **Operating System**: Windows, macOS, or Linux
- **Display**: GUI access required for recording and playback
- **Memory**: Minimum 100MB free RAM

## Installation Methods

### Method 1: Direct Installation (Recommended)

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

### Method 2: Development Installation

1. **Clone and install in development mode:**
   ```bash
   git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
   cd mouse-automation-toolkit
   pip install -e .
   ```

2. **Run the application:**
   ```bash
   mouse-automation
   ```

## Dependencies

The toolkit requires the following Python packages:

- **PyAutoGUI** (≥0.9.54): For GUI automation and mouse control
- **pynput** (≥1.7.6): For capturing mouse input events
- **tkinter**: For the graphical user interface (usually included with Python)

## Platform-Specific Notes

### Windows
- No additional setup required
- Windows Defender may flag the application - add exception if needed
- UAC (User Account Control) may require administrator privileges for some actions

### macOS
- **Accessibility permissions required:**
  1. Go to System Preferences → Security & Privacy → Privacy
  2. Click on "Accessibility" in the left sidebar
  3. Add Terminal or your Python interpreter to the list
  4. Enable the checkbox for the application

- **Screen recording permissions may be required:**
  1. Go to System Preferences → Security & Privacy → Privacy
  2. Click on "Screen Recording" in the left sidebar
  3. Add Terminal or your Python interpreter to the list

### Linux
- **X11 dependencies:**
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-tk python3-dev
  
  # CentOS/RHEL
  sudo yum install tkinter python3-devel
  
  # Arch Linux
  sudo pacman -S tk python
  ```

- **Additional dependencies for some distributions:**
  ```bash
  # For pyautogui on some systems
  sudo apt-get install scrot
  
  # For pynput on some systems
  sudo apt-get install python3-xlib
  ```

## Verification

To verify the installation is working correctly:

1. **Run the test suite:**
   ```bash
   python -m unittest discover tests/
   ```

2. **Run a basic example:**
   ```bash
   python examples/basic_usage.py
   ```

3. **Launch the GUI:**
   ```bash
   python main.py
   ```

## Troubleshooting

### Common Issues

**Import Error: No module named 'pyautogui'**
```bash
pip install pyautogui
```

**Import Error: No module named 'pynput'**
```bash
pip install pynput
```

**Permission denied on macOS**
- Follow the macOS-specific setup instructions above
- Grant accessibility and screen recording permissions

**Application crashes on Linux**
- Install X11 dependencies as shown above
- Ensure you're running in a graphical environment

**Mouse actions not working**
- Check that PyAutoGUI failsafe is not triggered (mouse in corner)
- Verify screen coordinates are within display bounds
- On Linux, ensure X11 forwarding is enabled if using SSH

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit/issues)
2. Review the [Usage Guide](usage.md)
3. Check the [API Documentation](api.md)
4. Create a new issue with your system details and error message

### System Information

To help with troubleshooting, gather this information:

```bash
python --version
pip list | grep -E "(pyautogui|pynput)"
python -c "import tkinter; print('tkinter available')"
```

**Display information:**
```bash
# Linux
echo $DISPLAY
xrandr

# macOS
system_profiler SPDisplaysDataType

# Windows
wmic desktopmonitor get screenheight,screenwidth
```