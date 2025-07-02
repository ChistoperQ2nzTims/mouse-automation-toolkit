"""
Coordinate Transformer Module

Handles coordinate transformations including translation, scaling, rotation, and mirroring.
"""

import math
from typing import List, Tuple, Optional
import numpy as np
import logging

from .recorder import MouseAction

logger = logging.getLogger(__name__)


class CoordinateTransformer:
    """Handles various coordinate transformations for mouse actions."""
    
    def __init__(self):
        self.screen_width = 1920  # Default screen width
        self.screen_height = 1080  # Default screen height
        
    def set_screen_dimensions(self, width: int, height: int):
        """Set screen dimensions for transformations."""
        self.screen_width = width
        self.screen_height = height
        logger.info(f"Screen dimensions set to {width}x{height}")
        
    def translate(self, actions: List[MouseAction], offset_x: int, offset_y: int) -> List[MouseAction]:
        """
        Translate coordinates by offset values.
        
        Args:
            actions: List of mouse actions to transform
            offset_x: X offset to apply
            offset_y: Y offset to apply
            
        Returns:
            List of transformed actions
        """
        transformed_actions = []
        
        for action in actions:
            new_action = MouseAction(
                action_type=action.action_type,
                x=action.x + offset_x,
                y=action.y + offset_y,
                button=action.button,
                timestamp=action.timestamp,
                delay=action.delay
            )
            transformed_actions.append(new_action)
            
        logger.info(f"Applied translation: offset_x={offset_x}, offset_y={offset_y}")
        return transformed_actions
        
    def scale(self, actions: List[MouseAction], scale_x: float, scale_y: float, 
              center_x: Optional[int] = None, center_y: Optional[int] = None) -> List[MouseAction]:
        """
        Scale coordinates around a center point.
        
        Args:
            actions: List of mouse actions to transform
            scale_x: X scaling factor
            scale_y: Y scaling factor
            center_x: X center point for scaling (default: screen center)
            center_y: Y center point for scaling (default: screen center)
            
        Returns:
            List of transformed actions
        """
        if center_x is None:
            center_x = self.screen_width // 2
        if center_y is None:
            center_y = self.screen_height // 2
            
        transformed_actions = []
        
        for action in actions:
            # Translate to origin
            x_origin = action.x - center_x
            y_origin = action.y - center_y
            
            # Scale
            x_scaled = x_origin * scale_x
            y_scaled = y_origin * scale_y
            
            # Translate back
            new_x = int(x_scaled + center_x)
            new_y = int(y_scaled + center_y)
            
            new_action = MouseAction(
                action_type=action.action_type,
                x=new_x,
                y=new_y,
                button=action.button,
                timestamp=action.timestamp,
                delay=action.delay
            )
            transformed_actions.append(new_action)
            
        logger.info(f"Applied scaling: scale_x={scale_x}, scale_y={scale_y}, center=({center_x}, {center_y})")
        return transformed_actions
        
    def rotate(self, actions: List[MouseAction], angle_degrees: float, 
               center_x: Optional[int] = None, center_y: Optional[int] = None) -> List[MouseAction]:
        """
        Rotate coordinates around a center point.
        
        Args:
            actions: List of mouse actions to transform
            angle_degrees: Rotation angle in degrees
            center_x: X center point for rotation (default: screen center)
            center_y: Y center point for rotation (default: screen center)
            
        Returns:
            List of transformed actions
        """
        if center_x is None:
            center_x = self.screen_width // 2
        if center_y is None:
            center_y = self.screen_height // 2
            
        angle_radians = math.radians(angle_degrees)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        transformed_actions = []
        
        for action in actions:
            # Translate to origin
            x_origin = action.x - center_x
            y_origin = action.y - center_y
            
            # Rotate
            x_rotated = x_origin * cos_angle - y_origin * sin_angle
            y_rotated = x_origin * sin_angle + y_origin * cos_angle
            
            # Translate back
            new_x = int(x_rotated + center_x)
            new_y = int(y_rotated + center_y)
            
            new_action = MouseAction(
                action_type=action.action_type,
                x=new_x,
                y=new_y,
                button=action.button,
                timestamp=action.timestamp,
                delay=action.delay
            )
            transformed_actions.append(new_action)
            
        logger.info(f"Applied rotation: angle={angle_degrees}°, center=({center_x}, {center_y})")
        return transformed_actions
        
    def mirror_horizontal(self, actions: List[MouseAction]) -> List[MouseAction]:
        """
        Mirror coordinates horizontally (flip left-right).
        
        Args:
            actions: List of mouse actions to transform
            
        Returns:
            List of transformed actions
        """
        transformed_actions = []
        
        for action in actions:
            new_x = self.screen_width - action.x
            
            new_action = MouseAction(
                action_type=action.action_type,
                x=new_x,
                y=action.y,
                button=action.button,
                timestamp=action.timestamp,
                delay=action.delay
            )
            transformed_actions.append(new_action)
            
        logger.info("Applied horizontal mirroring")
        return transformed_actions
        
    def mirror_vertical(self, actions: List[MouseAction]) -> List[MouseAction]:
        """
        Mirror coordinates vertically (flip up-down).
        
        Args:
            actions: List of mouse actions to transform
            
        Returns:
            List of transformed actions
        """
        transformed_actions = []
        
        for action in actions:
            new_y = self.screen_height - action.y
            
            new_action = MouseAction(
                action_type=action.action_type,
                x=action.x,
                y=new_y,
                button=action.button,
                timestamp=action.timestamp,
                delay=action.delay
            )
            transformed_actions.append(new_action)
            
        logger.info("Applied vertical mirroring")
        return transformed_actions
        
    def apply_matrix_transform(self, actions: List[MouseAction], 
                              transform_matrix: np.ndarray) -> List[MouseAction]:
        """
        Apply a custom transformation matrix to coordinates.
        
        Args:
            actions: List of mouse actions to transform
            transform_matrix: 3x3 transformation matrix
            
        Returns:
            List of transformed actions
        """
        if transform_matrix.shape != (3, 3):
            raise ValueError("Transform matrix must be 3x3")
            
        transformed_actions = []
        
        for action in actions:
            # Create homogeneous coordinates
            point = np.array([action.x, action.y, 1])
            
            # Apply transformation
            transformed_point = transform_matrix @ point
            
            # Convert back to cartesian coordinates
            new_x = int(transformed_point[0] / transformed_point[2])
            new_y = int(transformed_point[1] / transformed_point[2])
            
            new_action = MouseAction(
                action_type=action.action_type,
                x=new_x,
                y=new_y,
                button=action.button,
                timestamp=action.timestamp,
                delay=action.delay
            )
            transformed_actions.append(new_action)
            
        logger.info("Applied custom matrix transformation")
        return transformed_actions
        
    def chain_transforms(self, actions: List[MouseAction], 
                        transforms: List[Tuple[str, dict]]) -> List[MouseAction]:
        """
        Apply multiple transformations in sequence.
        
        Args:
            actions: List of mouse actions to transform
            transforms: List of (transform_name, parameters) tuples
            
        Returns:
            List of transformed actions
        """
        result = actions
        
        for transform_name, params in transforms:
            if transform_name == 'translate':
                result = self.translate(result, params['offset_x'], params['offset_y'])
            elif transform_name == 'scale':
                result = self.scale(result, params['scale_x'], params['scale_y'],
                                   params.get('center_x'), params.get('center_y'))
            elif transform_name == 'rotate':
                result = self.rotate(result, params['angle_degrees'],
                                   params.get('center_x'), params.get('center_y'))
            elif transform_name == 'mirror_horizontal':
                result = self.mirror_horizontal(result)
            elif transform_name == 'mirror_vertical':
                result = self.mirror_vertical(result)
            else:
                logger.warning(f"Unknown transform: {transform_name}")
                
        logger.info(f"Applied {len(transforms)} chained transformations")
        return result
        
    def get_bounds(self, actions: List[MouseAction]) -> Tuple[int, int, int, int]:
        """
        Get the bounding box of all actions.
        
        Args:
            actions: List of mouse actions
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        if not actions:
            return (0, 0, 0, 0)
            
        x_coords = [action.x for action in actions]
        y_coords = [action.y for action in actions]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
        
    def normalize_to_bounds(self, actions: List[MouseAction], 
                           target_width: int, target_height: int) -> List[MouseAction]:
        """
        Normalize actions to fit within target bounds.
        
        Args:
            actions: List of mouse actions to normalize
            target_width: Target width
            target_height: Target height
            
        Returns:
            List of normalized actions
        """
        if not actions:
            return actions
            
        min_x, min_y, max_x, max_y = self.get_bounds(actions)
        
        # Calculate scaling factors
        current_width = max_x - min_x
        current_height = max_y - min_y
        
        if current_width == 0 or current_height == 0:
            return actions
            
        scale_x = target_width / current_width
        scale_y = target_height / current_height
        
        # Use uniform scaling to maintain aspect ratio
        scale = min(scale_x, scale_y)
        
        # First translate to origin, then scale, then translate to center of target
        result = self.translate(actions, -min_x, -min_y)
        result = self.scale(result, scale, scale, 0, 0)
        result = self.translate(result, target_width // 2, target_height // 2)
        
        logger.info(f"Normalized actions to {target_width}x{target_height}")
        return result