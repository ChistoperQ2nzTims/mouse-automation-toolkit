#!/usr/bin/env python3
"""
Coordinate Transformer Module

Provides various coordinate transformation capabilities for mouse actions.
Supports translation, scaling, rotation, and mirroring operations.
"""

import math
import copy
from typing import List, Dict, Any, Tuple, Optional
import logging

try:
    import numpy as np
except ImportError:
    raise ImportError("numpy is required. Install with: pip install numpy")

try:
    from .recorder import MouseAction
except ImportError:
    from recorder import MouseAction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoordinateTransformer:
    """
    Transform mouse action coordinates using various mathematical operations.
    
    Features:
    - Translate coordinates (offset X, Y)
    - Scale coordinates (zoom in/out)
    - Rotate coordinates around point
    - Mirror coordinates (horizontal/vertical)
    - Batch transform multiple actions
    - Preserve action timing and properties
    """
    
    def __init__(self):
        """Initialize the coordinate transformer."""
        logger.info("CoordinateTransformer initialized")
    
    def translate(self, 
                  actions: List[MouseAction], 
                  offset_x: float, 
                  offset_y: float) -> List[MouseAction]:
        """
        Translate all coordinates by a fixed offset.
        
        Args:
            actions: List of mouse actions to transform
            offset_x: X-axis offset
            offset_y: Y-axis offset
            
        Returns:
            List of transformed mouse actions
        """
        transformed_actions = []
        
        for action in actions:
            new_action = copy.deepcopy(action)
            new_action.x = int(action.x + offset_x)
            new_action.y = int(action.y + offset_y)
            transformed_actions.append(new_action)
        
        logger.info(f"Translated {len(actions)} actions by offset ({offset_x}, {offset_y})")
        return transformed_actions
    
    def scale(self, 
              actions: List[MouseAction], 
              scale_x: float, 
              scale_y: float, 
              center_x: Optional[float] = None, 
              center_y: Optional[float] = None) -> List[MouseAction]:
        """
        Scale coordinates around a center point.
        
        Args:
            actions: List of mouse actions to transform
            scale_x: X-axis scale factor
            scale_y: Y-axis scale factor
            center_x: X coordinate of scaling center (default: center of bounding box)
            center_y: Y coordinate of scaling center (default: center of bounding box)
            
        Returns:
            List of transformed mouse actions
        """
        if not actions:
            return []
        
        # Calculate center point if not provided
        if center_x is None or center_y is None:
            bounds = self._get_action_bounds(actions)
            if center_x is None:
                center_x = (bounds['min_x'] + bounds['max_x']) / 2
            if center_y is None:
                center_y = (bounds['min_y'] + bounds['max_y']) / 2
        
        transformed_actions = []
        
        for action in actions:
            new_action = copy.deepcopy(action)
            
            # Translate to origin
            rel_x = action.x - center_x
            rel_y = action.y - center_y
            
            # Scale
            scaled_x = rel_x * scale_x
            scaled_y = rel_y * scale_y
            
            # Translate back
            new_action.x = int(scaled_x + center_x)
            new_action.y = int(scaled_y + center_y)
            
            transformed_actions.append(new_action)
        
        logger.info(f"Scaled {len(actions)} actions by factors ({scale_x}, {scale_y}) around center ({center_x}, {center_y})")
        return transformed_actions
    
    def rotate(self, 
               actions: List[MouseAction], 
               angle_degrees: float, 
               center_x: Optional[float] = None, 
               center_y: Optional[float] = None) -> List[MouseAction]:
        """
        Rotate coordinates around a center point.
        
        Args:
            actions: List of mouse actions to transform
            angle_degrees: Rotation angle in degrees (positive = clockwise)
            center_x: X coordinate of rotation center (default: center of bounding box)
            center_y: Y coordinate of rotation center (default: center of bounding box)
            
        Returns:
            List of transformed mouse actions
        """
        if not actions:
            return []
        
        # Calculate center point if not provided
        if center_x is None or center_y is None:
            bounds = self._get_action_bounds(actions)
            if center_x is None:
                center_x = (bounds['min_x'] + bounds['max_x']) / 2
            if center_y is None:
                center_y = (bounds['min_y'] + bounds['max_y']) / 2
        
        # Convert angle to radians
        angle_radians = math.radians(angle_degrees)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        transformed_actions = []
        
        for action in actions:
            new_action = copy.deepcopy(action)
            
            # Translate to origin
            rel_x = action.x - center_x
            rel_y = action.y - center_y
            
            # Rotate
            rotated_x = rel_x * cos_angle - rel_y * sin_angle
            rotated_y = rel_x * sin_angle + rel_y * cos_angle
            
            # Translate back
            new_action.x = int(rotated_x + center_x)
            new_action.y = int(rotated_y + center_y)
            
            transformed_actions.append(new_action)
        
        logger.info(f"Rotated {len(actions)} actions by {angle_degrees}° around center ({center_x}, {center_y})")
        return transformed_actions
    
    def mirror_horizontal(self, 
                         actions: List[MouseAction], 
                         axis_x: Optional[float] = None) -> List[MouseAction]:
        """
        Mirror coordinates horizontally around a vertical axis.
        
        Args:
            actions: List of mouse actions to transform
            axis_x: X coordinate of mirror axis (default: center of bounding box)
            
        Returns:
            List of transformed mouse actions
        """
        if not actions:
            return []
        
        # Calculate axis if not provided
        if axis_x is None:
            bounds = self._get_action_bounds(actions)
            axis_x = (bounds['min_x'] + bounds['max_x']) / 2
        
        transformed_actions = []
        
        for action in actions:
            new_action = copy.deepcopy(action)
            new_action.x = int(2 * axis_x - action.x)
            transformed_actions.append(new_action)
        
        logger.info(f"Mirrored {len(actions)} actions horizontally around x={axis_x}")
        return transformed_actions
    
    def mirror_vertical(self, 
                       actions: List[MouseAction], 
                       axis_y: Optional[float] = None) -> List[MouseAction]:
        """
        Mirror coordinates vertically around a horizontal axis.
        
        Args:
            actions: List of mouse actions to transform
            axis_y: Y coordinate of mirror axis (default: center of bounding box)
            
        Returns:
            List of transformed mouse actions
        """
        if not actions:
            return []
        
        # Calculate axis if not provided
        if axis_y is None:
            bounds = self._get_action_bounds(actions)
            axis_y = (bounds['min_y'] + bounds['max_y']) / 2
        
        transformed_actions = []
        
        for action in actions:
            new_action = copy.deepcopy(action)
            new_action.y = int(2 * axis_y - action.y)
            transformed_actions.append(new_action)
        
        logger.info(f"Mirrored {len(actions)} actions vertically around y={axis_y}")
        return transformed_actions
    
    def apply_matrix_transform(self, 
                              actions: List[MouseAction], 
                              transformation_matrix: np.ndarray) -> List[MouseAction]:
        """
        Apply a custom 2D transformation matrix to coordinates.
        
        Args:
            actions: List of mouse actions to transform
            transformation_matrix: 3x3 transformation matrix for homogeneous coordinates
            
        Returns:
            List of transformed mouse actions
        """
        if transformation_matrix.shape != (3, 3):
            raise ValueError("Transformation matrix must be 3x3")
        
        transformed_actions = []
        
        for action in actions:
            new_action = copy.deepcopy(action)
            
            # Convert to homogeneous coordinates
            point = np.array([action.x, action.y, 1])
            
            # Apply transformation
            transformed_point = transformation_matrix @ point
            
            # Convert back to Cartesian coordinates
            new_action.x = int(transformed_point[0] / transformed_point[2])
            new_action.y = int(transformed_point[1] / transformed_point[2])
            
            transformed_actions.append(new_action)
        
        logger.info(f"Applied matrix transformation to {len(actions)} actions")
        return transformed_actions
    
    def chain_transforms(self, 
                        actions: List[MouseAction], 
                        transforms: List[Dict[str, Any]]) -> List[MouseAction]:
        """
        Apply multiple transformations in sequence.
        
        Args:
            actions: List of mouse actions to transform
            transforms: List of transformation dictionaries with 'type' and parameters
            
        Example:
            transforms = [
                {'type': 'translate', 'offset_x': 100, 'offset_y': 50},
                {'type': 'scale', 'scale_x': 1.5, 'scale_y': 1.5},
                {'type': 'rotate', 'angle_degrees': 45}
            ]
            
        Returns:
            List of transformed mouse actions
        """
        result_actions = actions
        
        for transform in transforms:
            transform_type = transform.get('type')
            
            if transform_type == 'translate':
                result_actions = self.translate(
                    result_actions, 
                    transform.get('offset_x', 0), 
                    transform.get('offset_y', 0)
                )
            elif transform_type == 'scale':
                result_actions = self.scale(
                    result_actions,
                    transform.get('scale_x', 1.0),
                    transform.get('scale_y', 1.0),
                    transform.get('center_x'),
                    transform.get('center_y')
                )
            elif transform_type == 'rotate':
                result_actions = self.rotate(
                    result_actions,
                    transform.get('angle_degrees', 0),
                    transform.get('center_x'),
                    transform.get('center_y')
                )
            elif transform_type == 'mirror_horizontal':
                result_actions = self.mirror_horizontal(
                    result_actions,
                    transform.get('axis_x')
                )
            elif transform_type == 'mirror_vertical':
                result_actions = self.mirror_vertical(
                    result_actions,
                    transform.get('axis_y')
                )
            else:
                logger.warning(f"Unknown transformation type: {transform_type}")
        
        logger.info(f"Applied {len(transforms)} chained transformations")
        return result_actions
    
    def fit_to_screen(self, 
                      actions: List[MouseAction], 
                      screen_width: int, 
                      screen_height: int, 
                      maintain_aspect_ratio: bool = True,
                      margin: int = 10) -> List[MouseAction]:
        """
        Scale and translate actions to fit within screen bounds.
        
        Args:
            actions: List of mouse actions to transform
            screen_width: Target screen width
            screen_height: Target screen height
            maintain_aspect_ratio: Whether to maintain aspect ratio during scaling
            margin: Margin from screen edges
            
        Returns:
            List of transformed mouse actions
        """
        if not actions:
            return []
        
        bounds = self._get_action_bounds(actions)
        
        # Calculate current dimensions
        current_width = bounds['max_x'] - bounds['min_x']
        current_height = bounds['max_y'] - bounds['min_y']
        
        if current_width == 0 or current_height == 0:
            return actions
        
        # Calculate target dimensions (with margin)
        target_width = screen_width - 2 * margin
        target_height = screen_height - 2 * margin
        
        # Calculate scale factors
        scale_x = target_width / current_width
        scale_y = target_height / current_height
        
        if maintain_aspect_ratio:
            scale = min(scale_x, scale_y)
            scale_x = scale_y = scale
        
        # First scale around current center
        center_x = (bounds['min_x'] + bounds['max_x']) / 2
        center_y = (bounds['min_y'] + bounds['max_y']) / 2
        
        scaled_actions = self.scale(actions, scale_x, scale_y, center_x, center_y)
        
        # Calculate new bounds after scaling
        new_bounds = self._get_action_bounds(scaled_actions)
        
        # Calculate translation to center on screen
        new_center_x = (new_bounds['min_x'] + new_bounds['max_x']) / 2
        new_center_y = (new_bounds['min_y'] + new_bounds['max_y']) / 2
        
        target_center_x = screen_width / 2
        target_center_y = screen_height / 2
        
        offset_x = target_center_x - new_center_x
        offset_y = target_center_y - new_center_y
        
        # Apply translation
        result_actions = self.translate(scaled_actions, offset_x, offset_y)
        
        logger.info(f"Fitted {len(actions)} actions to screen {screen_width}x{screen_height}")
        return result_actions
    
    def normalize_timing(self, 
                        actions: List[MouseAction], 
                        total_duration: float) -> List[MouseAction]:
        """
        Normalize action timing to fit within a specified duration.
        
        Args:
            actions: List of mouse actions to transform
            total_duration: Target total duration in seconds
            
        Returns:
            List of actions with normalized timing
        """
        if not actions or len(actions) < 2:
            return actions
        
        # Get current duration
        current_duration = actions[-1].timestamp - actions[0].timestamp
        
        if current_duration == 0:
            return actions
        
        # Calculate time scale factor
        time_scale = total_duration / current_duration
        
        normalized_actions = []
        base_time = actions[0].timestamp
        
        for action in actions:
            new_action = copy.deepcopy(action)
            relative_time = action.timestamp - base_time
            new_action.timestamp = relative_time * time_scale
            normalized_actions.append(new_action)
        
        logger.info(f"Normalized timing for {len(actions)} actions to {total_duration}s duration")
        return normalized_actions
    
    def _get_action_bounds(self, actions: List[MouseAction]) -> Dict[str, float]:
        """Get bounding box of all action coordinates."""
        if not actions:
            return {'min_x': 0, 'max_x': 0, 'min_y': 0, 'max_y': 0}
        
        x_coords = [action.x for action in actions]
        y_coords = [action.y for action in actions]
        
        return {
            'min_x': min(x_coords),
            'max_x': max(x_coords),
            'min_y': min(y_coords),
            'max_y': max(y_coords)
        }
    
    def get_transformation_info(self, 
                               original_actions: List[MouseAction], 
                               transformed_actions: List[MouseAction]) -> Dict[str, Any]:
        """
        Get information about the transformation applied.
        
        Args:
            original_actions: Original actions before transformation
            transformed_actions: Actions after transformation
            
        Returns:
            Dictionary with transformation statistics
        """
        if not original_actions or not transformed_actions:
            return {}
        
        orig_bounds = self._get_action_bounds(original_actions)
        trans_bounds = self._get_action_bounds(transformed_actions)
        
        # Calculate center shift
        orig_center_x = (orig_bounds['min_x'] + orig_bounds['max_x']) / 2
        orig_center_y = (orig_bounds['min_y'] + orig_bounds['max_y']) / 2
        trans_center_x = (trans_bounds['min_x'] + trans_bounds['max_x']) / 2
        trans_center_y = (trans_bounds['min_y'] + trans_bounds['max_y']) / 2
        
        center_shift_x = trans_center_x - orig_center_x
        center_shift_y = trans_center_y - orig_center_y
        
        # Calculate scale factors
        orig_width = orig_bounds['max_x'] - orig_bounds['min_x']
        orig_height = orig_bounds['max_y'] - orig_bounds['min_y']
        trans_width = trans_bounds['max_x'] - trans_bounds['min_x']
        trans_height = trans_bounds['max_y'] - trans_bounds['min_y']
        
        scale_x = trans_width / orig_width if orig_width > 0 else 1.0
        scale_y = trans_height / orig_height if orig_height > 0 else 1.0
        
        return {
            'original_bounds': orig_bounds,
            'transformed_bounds': trans_bounds,
            'center_shift': {'x': center_shift_x, 'y': center_shift_y},
            'scale_factors': {'x': scale_x, 'y': scale_y},
            'area_ratio': (trans_width * trans_height) / (orig_width * orig_height) if orig_width > 0 and orig_height > 0 else 1.0
        }


if __name__ == "__main__":
    # Example usage
    from .recorder import MouseAction
    
    # Create sample actions
    actions = [
        MouseAction(0.0, 'click', 100, 100, 'left', True),
        MouseAction(0.5, 'move', 200, 150),
        MouseAction(1.0, 'click', 200, 150, 'left', False),
    ]
    
    transformer = CoordinateTransformer()
    
    # Test transformations
    translated = transformer.translate(actions, 50, 25)
    scaled = transformer.scale(actions, 1.5, 1.5)
    rotated = transformer.rotate(actions, 45)
    
    print(f"Original: {[(a.x, a.y) for a in actions]}")
    print(f"Translated: {[(a.x, a.y) for a in translated]}")
    print(f"Scaled: {[(a.x, a.y) for a in scaled]}")
    print(f"Rotated: {[(a.x, a.y) for a in rotated]}")