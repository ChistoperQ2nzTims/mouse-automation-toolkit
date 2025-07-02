# Installation Guide

This guide will help you install and set up the Mouse Automation Toolkit on your system.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 100MB of free RAM
- **Storage**: At least 50MB of free disk space

## Installation Methods

### Method 1: Installing from Source (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
   cd mouse-automation-toolkit
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package** (optional):
   ```bash
   pip install -e .
   ```

### Method 2: Direct Installation

If the package is available on PyPI:
```bash
pip install mouse-automation-toolkit
```

## Dependencies

The toolkit requires the following Python packages:

- `pyautogui>=0.9.54` - For mouse control and automation
- `pynput>=1.7.6` - For input monitoring and hotkey detection
- `numpy>=1.21.0` - For coordinate transformations
- `tkinter` - For GUI interface (usually included with Python)

## Platform-Specific Setup

### Windows

1. **Install Python** from [python.org](https://www.python.org/downloads/)
2. **Install dependencies**:
   ```cmd
   pip install pyautogui pynput numpy
   ```
3. **Security considerations**: Windows Defender may flag automation tools. Add an exception if needed.

### macOS

1. **Install Python** (if not already installed):
   ```bash
   brew install python
   ```
2. **Install dependencies**:
   ```bash
   pip3 install pyautogui pynput numpy
   ```
3. **Accessibility permissions**: 
   - Go to System Preferences → Security & Privacy → Privacy → Accessibility
   - Add Terminal (or your IDE) to the list of allowed applications

### Linux

1. **Install Python and pip**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-tk
   ```

2. **Install dependencies**:
   ```bash
   pip3 install pyautogui pynput numpy
   ```

3. **Install additional system packages** (may be required):
   ```bash
   sudo apt-get install scrot python3-tk python3-dev
   ```

## Verification

To verify your installation:

1. **Run the basic test**:
   ```bash
   python -c "import pyautogui, pynput, numpy; print('All dependencies installed successfully!')"
   ```

2. **Test the toolkit**:
   ```bash
   python main.py --help
   ```

3. **Run the GUI** (if tkinter is available):
   ```bash
   python main.py --gui
   ```

## Common Installation Issues

### Issue: "ModuleNotFoundError: No module named 'tkinter'"

**Solution for Ubuntu/Debian**:
```bash
sudo apt-get install python3-tk
```

**Solution for CentOS/RHEL**:
```bash
sudo yum install tkinter
# or
sudo dnf install python3-tkinter
```

### Issue: "Permission denied" on macOS

**Solution**: Grant accessibility permissions to your terminal or IDE:
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Click the lock to make changes
3. Add your terminal/IDE application
4. Restart the application

### Issue: PyAutoGUI failsafe triggering

**Solution**: This is a safety feature. To disable temporarily:
```python
import pyautogui
pyautogui.FAILSAFE = False  # Use with caution
```

### Issue: "Could not find a version that satisfies the requirement"

**Solution**: Update pip and try again:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Virtual Environment Setup (Recommended)

Using a virtual environment helps avoid conflicts:

1. **Create virtual environment**:
   ```bash
   python -m venv mouse_automation_env
   ```

2. **Activate virtual environment**:
   
   **Windows**:
   ```cmd
   mouse_automation_env\Scripts\activate
   ```
   
   **macOS/Linux**:
   ```bash
   source mouse_automation_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Deactivate when done**:
   ```bash
   deactivate
   ```

## Development Installation

For developers who want to contribute:

1. **Clone with development tools**:
   ```bash
   git clone https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit.git
   cd mouse-automation-toolkit
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .[dev]
   ```

3. **Install testing dependencies**:
   ```bash
   pip install pytest pytest-cov
   ```

4. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

## Security Considerations

⚠️ **Important Security Notes**:

1. **Antivirus software** may flag automation tools as potentially harmful
2. **Screen recording** permissions may be required on some systems
3. **Accessibility permissions** are needed for input monitoring
4. **Firewall exceptions** may be required for network features

## Troubleshooting

If you encounter issues:

1. **Check Python version**:
   ```bash
   python --version
   ```

2. **Verify package installation**:
   ```bash
   pip list | grep -E "(pyautogui|pynput|numpy)"
   ```

3. **Test basic functionality**:
   ```bash
   python examples/basic_usage.py
   ```

4. **Check system logs** for permission or security issues

5. **Consult the FAQ** in the documentation

## Next Steps

After successful installation:

1. Read the [Usage Guide](usage.md)
2. Try the [Examples](../examples/)
3. Explore the [API Documentation](api.md)
4. Join the community for support

## Support

If you need help:

- 📖 Check the [documentation](../docs/)
- 🐛 Report issues on [GitHub](https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit/issues)
- 💬 Join the community discussions
- 📧 Contact support (if available)

---

**Ready to get started?** Head over to the [Usage Guide](usage.md) to learn how to use the toolkit!