#!/usr/bin/env python3
"""
Mouse Automation Toolkit - Main Entry Point
A complete toolkit for recording, transforming, and replaying mouse actions.
"""

import sys
import argparse
from src.gui import MouseAutomationGUI


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Mouse Automation Toolkit - Record, transform, and replay mouse actions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Launch GUI interface
  python main.py --gui         # Launch GUI interface (explicit)

Features:
  • Record mouse clicks with coordinates, timing, and button types
  • Transform coordinates (translate, scale, rotate, mirror)
  • Replay actions with customizable speed, loops, and delays
  • Safe mode with ESC key to stop playback
  • Smart recording with duplicate action removal
  • Cross-platform support (Windows, macOS, Linux)

Safety:
  - PyAutoGUI failsafe is enabled (move mouse to corner to stop)
  - ESC key stops playback immediately
  - All coordinates are validated against screen bounds
        """
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        default=True,
        help="Launch GUI interface (default)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Mouse Automation Toolkit v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    try:
        # Import and check dependencies
        import pyautogui
        import pynput
        import tkinter
        
        print("Mouse Automation Toolkit v1.0.0")
        print("Starting GUI interface...")
        print("Note: Move mouse to screen corner to trigger PyAutoGUI failsafe")
        print("Press ESC during playback to stop actions")
        print("-" * 50)
        
        # Launch GUI
        app = MouseAutomationGUI()
        app.run()
        
    except ImportError as e:
        print(f"Error: Missing required dependency: {e}")
        print("Please install required packages using: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()