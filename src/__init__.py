"""
Mouse Automation Toolkit

A comprehensive toolkit for recording, transforming, and replaying mouse actions.
"""

__version__ = "1.0.0"
__author__ = "ChistoperQ2nzTims"

from .recorder import MouseRecorder
from .transformer import CoordinateTransformer
from .player import MousePlayer

__all__ = ['MouseRecorder', 'CoordinateTransformer', 'MousePlayer']