"""
Coordinate Transformer
Transforms mouse action coordinates with various operations.
"""

import math
from typing import List, Tuple, Dict, Any
from src.recorder import MouseAction


class CoordinateTransformer:
    """Transforms coordinates using various mathematical operations."""
    
    def __init__(self):
        pass
    
    def translate(self, actions: List[MouseAction], offset_x: int, offset_y: int) -> List[MouseAction]:
        """Translate coordinates by offset values."""
        transformed_actions = []
        
        for action in actions:
            new_action = MouseAction(
                x=action.x + offset_x,
                y=action.y + offset_y,
                button=action.button,
                timestamp=action.timestamp,
                action_type=action.action_type
            )
            transformed_actions.append(new_action)
        
        return transformed_actions
    
    def scale(self, actions: List[MouseAction], scale_x: float, scale_y: float, 
              center_x: int = 0, center_y: int = 0) -> List[MouseAction]:
        """Scale coordinates around a center point."""
        transformed_actions = []
        
        for action in actions:
            # Translate to origin
            temp_x = action.x - center_x
            temp_y = action.y - center_y
            
            # Scale
            scaled_x = temp_x * scale_x
            scaled_y = temp_y * scale_y
            
            # Translate back
            new_x = int(scaled_x + center_x)
            new_y = int(scaled_y + center_y)
            
            new_action = MouseAction(
                x=new_x,
                y=new_y,
                button=action.button,
                timestamp=action.timestamp,
                action_type=action.action_type
            )
            transformed_actions.append(new_action)
        
        return transformed_actions
    
    def rotate(self, actions: List[MouseAction], angle_degrees: float, 
               center_x: int = 0, center_y: int = 0) -> List[MouseAction]:
        """Rotate coordinates around a center point."""
        transformed_actions = []
        angle_radians = math.radians(angle_degrees)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        for action in actions:
            # Translate to origin
            temp_x = action.x - center_x
            temp_y = action.y - center_y
            
            # Rotate
            rotated_x = temp_x * cos_angle - temp_y * sin_angle
            rotated_y = temp_x * sin_angle + temp_y * cos_angle
            
            # Translate back
            new_x = int(rotated_x + center_x)
            new_y = int(rotated_y + center_y)
            
            new_action = MouseAction(
                x=new_x,
                y=new_y,
                button=action.button,
                timestamp=action.timestamp,
                action_type=action.action_type
            )
            transformed_actions.append(new_action)
        
        return transformed_actions
    
    def mirror_horizontal(self, actions: List[MouseAction], axis_x: int = 0) -> List[MouseAction]:
        """Mirror coordinates horizontally around a vertical axis."""
        transformed_actions = []
        
        for action in actions:
            new_x = 2 * axis_x - action.x
            
            new_action = MouseAction(
                x=new_x,
                y=action.y,
                button=action.button,
                timestamp=action.timestamp,
                action_type=action.action_type
            )
            transformed_actions.append(new_action)
        
        return transformed_actions
    
    def mirror_vertical(self, actions: List[MouseAction], axis_y: int = 0) -> List[MouseAction]:
        """Mirror coordinates vertically around a horizontal axis."""
        transformed_actions = []
        
        for action in actions:
            new_y = 2 * axis_y - action.y
            
            new_action = MouseAction(
                x=action.x,
                y=new_y,
                button=action.button,
                timestamp=action.timestamp,
                action_type=action.action_type
            )
            transformed_actions.append(new_action)
        
        return transformed_actions
    
    def get_bounding_box(self, actions: List[MouseAction]) -> Tuple[int, int, int, int]:
        """Get bounding box of all actions (min_x, min_y, max_x, max_y)."""
        if not actions:
            return (0, 0, 0, 0)
        
        min_x = min(action.x for action in actions)
        max_x = max(action.x for action in actions)
        min_y = min(action.y for action in actions)
        max_y = max(action.y for action in actions)
        
        return (min_x, min_y, max_x, max_y)
    
    def get_center_point(self, actions: List[MouseAction]) -> Tuple[int, int]:
        """Get center point of all actions."""
        if not actions:
            return (0, 0)
        
        min_x, min_y, max_x, max_y = self.get_bounding_box(actions)
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        return (center_x, center_y)
    
    def fit_to_screen(self, actions: List[MouseAction], screen_width: int, 
                      screen_height: int, margin: int = 10) -> List[MouseAction]:
        """Scale and translate actions to fit within screen bounds with margin."""
        if not actions:
            return actions
        
        min_x, min_y, max_x, max_y = self.get_bounding_box(actions)
        
        # Calculate current dimensions
        current_width = max_x - min_x
        current_height = max_y - min_y
        
        if current_width == 0 or current_height == 0:
            return actions
        
        # Calculate scale factors
        target_width = screen_width - 2 * margin
        target_height = screen_height - 2 * margin
        
        scale_x = target_width / current_width
        scale_y = target_height / current_height
        
        # Use uniform scaling (smaller scale factor)
        scale = min(scale_x, scale_y)
        
        # First, translate to origin
        translated = self.translate(actions, -min_x, -min_y)
        
        # Then scale
        scaled = self.scale(translated, scale, scale)
        
        # Finally, translate to margin position
        final = self.translate(scaled, margin, margin)
        
        return final
    
    def apply_transformation_chain(self, actions: List[MouseAction], 
                                   transformations: List[Dict[str, Any]]) -> List[MouseAction]:
        """Apply a chain of transformations."""
        result = actions.copy()
        
        for transform in transformations:
            transform_type = transform.get("type")
            params = transform.get("params", {})
            
            if transform_type == "translate":
                result = self.translate(result, params.get("offset_x", 0), params.get("offset_y", 0))
            elif transform_type == "scale":
                result = self.scale(result, params.get("scale_x", 1.0), params.get("scale_y", 1.0),
                                  params.get("center_x", 0), params.get("center_y", 0))
            elif transform_type == "rotate":
                result = self.rotate(result, params.get("angle", 0),
                                   params.get("center_x", 0), params.get("center_y", 0))
            elif transform_type == "mirror_horizontal":
                result = self.mirror_horizontal(result, params.get("axis_x", 0))
            elif transform_type == "mirror_vertical":
                result = self.mirror_vertical(result, params.get("axis_y", 0))
            elif transform_type == "fit_to_screen":
                result = self.fit_to_screen(result, params.get("screen_width", 1920),
                                          params.get("screen_height", 1080), params.get("margin", 10))
        
        return result