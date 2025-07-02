"""
Mouse Automation Toolkit - A comprehensive tool for recording, transforming, and replaying mouse actions

This package provides a complete solution for automating mouse interactions with features including:
- Recording mouse actions with precise timing
- Transforming coordinates (translate, scale, rotate, mirror)  
- Replaying actions with customizable speed and timing
- GUI interface for easy interaction
"""

__version__ = "1.0.0"
__author__ = "Christopher Q2nz Tims"

from .recorder import MouseRecorder
from .transformer import CoordinateTransformer
from .player import ActionPlayer
from .gui import MainGUI

__all__ = [
    "MouseRecorder",
    "CoordinateTransformer", 
    "ActionPlayer",
    "MainGUI"
]