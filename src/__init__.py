"""
Mouse Automation Toolkit - A complete toolkit for recording, transforming, and replaying mouse actions.

This package provides tools for:
- Recording mouse clicks and movements
- Transforming coordinates (translate, scale, rotate, mirror)
- Replaying mouse actions with safety features
- GUI interface for easy interaction
"""

__version__ = "1.0.0"
__author__ = "Mouse Automation Toolkit Team"
__email__ = "info@mouseautomation.com"

from .recorder import MouseRecorder
from .transformer import CoordinateTransformer
from .player import ActionPlayer

__all__ = ['MouseRecorder', 'CoordinateTransformer', 'ActionPlayer']