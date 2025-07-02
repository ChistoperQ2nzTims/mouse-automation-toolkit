"""
Coordinate Transformation Module

This module provides comprehensive coordinate transformation capabilities including
translation, scaling, rotation, and mirroring operations.
"""

import math
from typing import Tuple, List, Dict, Any, Optional, Union


class CoordinateTransformer:
    """
    Provides coordinate transformation operations for mouse actions
    """
    
    def __init__(self):
        self.transformation_history: List[Dict[str, Any]] = []
    
    def translate(self, x: float, y: float, offset_x: float, offset_y: float) -> Tuple[float, float]:
        """
        Translate coordinates by given offset
        
        Args:
            x (float): Original x coordinate
            y (float): Original y coordinate
            offset_x (float): X offset to add
            offset_y (float): Y offset to add
            
        Returns:
            Tuple[float, float]: New (x, y) coordinates
        """
        return (x + offset_x, y + offset_y)
    
    def scale(self, x: float, y: float, scale_x: float, scale_y: float, 
              origin: Optional[Tuple[float, float]] = None) -> Tuple[float, float]:
        """
        Scale coordinates by given factors around an origin point
        
        Args:
            x (float): Original x coordinate
            y (float): Original y coordinate
            scale_x (float): X scaling factor
            scale_y (float): Y scaling factor
            origin (Tuple[float, float], optional): Origin point for scaling. Defaults to (0, 0)
            
        Returns:
            Tuple[float, float]: New (x, y) coordinates
        """
        if origin is None:
            origin = (0, 0)
        
        origin_x, origin_y = origin
        
        # Translate to origin
        translated_x = x - origin_x
        translated_y = y - origin_y
        
        # Apply scaling
        scaled_x = translated_x * scale_x
        scaled_y = translated_y * scale_y
        
        # Translate back
        final_x = scaled_x + origin_x
        final_y = scaled_y + origin_y
        
        return (final_x, final_y)
    
    def rotate(self, x: float, y: float, angle: float, 
               pivot: Optional[Tuple[float, float]] = None) -> Tuple[float, float]:
        """
        Rotate coordinates by given angle around a pivot point
        
        Args:
            x (float): Original x coordinate
            y (float): Original y coordinate
            angle (float): Rotation angle in degrees (positive = clockwise)
            pivot (Tuple[float, float], optional): Pivot point for rotation. Defaults to (0, 0)
            
        Returns:
            Tuple[float, float]: New (x, y) coordinates
        """
        if pivot is None:
            pivot = (0, 0)
        
        pivot_x, pivot_y = pivot
        
        # Convert angle to radians
        angle_rad = math.radians(angle)
        
        # Translate to pivot
        translated_x = x - pivot_x
        translated_y = y - pivot_y
        
        # Apply rotation
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        rotated_x = translated_x * cos_angle - translated_y * sin_angle
        rotated_y = translated_x * sin_angle + translated_y * cos_angle
        
        # Translate back
        final_x = rotated_x + pivot_x
        final_y = rotated_y + pivot_y
        
        return (final_x, final_y)
    
    def mirror(self, x: float, y: float, axis: str, 
               center: Optional[Tuple[float, float]] = None) -> Tuple[float, float]:
        """
        Mirror coordinates across a specified axis
        
        Args:
            x (float): Original x coordinate
            y (float): Original y coordinate
            axis (str): Mirror axis ('horizontal', 'vertical', or 'both')
            center (Tuple[float, float], optional): Center point for mirroring. Defaults to (0, 0)
            
        Returns:
            Tuple[float, float]: New (x, y) coordinates
        """
        if center is None:
            center = (0, 0)
        
        center_x, center_y = center
        
        if axis.lower() == 'horizontal':
            # Mirror across horizontal axis (flip vertically)
            return (x, 2 * center_y - y)
        elif axis.lower() == 'vertical':
            # Mirror across vertical axis (flip horizontally)
            return (2 * center_x - x, y)
        elif axis.lower() == 'both':
            # Mirror across both axes
            return (2 * center_x - x, 2 * center_y - y)
        else:
            raise ValueError(f"Invalid axis '{axis}'. Must be 'horizontal', 'vertical', or 'both'")
    
    def transform_actions(self, actions: List[Dict[str, Any]], 
                         transformations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply multiple transformations to a list of actions
        
        Args:
            actions (List[Dict]): List of mouse actions
            transformations (List[Dict]): List of transformation configurations
            
        Returns:
            List[Dict]: Transformed actions
        """
        transformed_actions = []
        
        for action in actions:
            if action['type'] != 'click':
                transformed_actions.append(action.copy())
                continue
            
            x, y = action['x'], action['y']
            
            # Apply each transformation in sequence
            for transform in transformations:
                transform_type = transform['type']
                
                if transform_type == 'translate':
                    x, y = self.translate(x, y, transform['offset_x'], transform['offset_y'])
                elif transform_type == 'scale':
                    origin = transform.get('origin', (0, 0))
                    x, y = self.scale(x, y, transform['scale_x'], transform['scale_y'], origin)
                elif transform_type == 'rotate':
                    pivot = transform.get('pivot', (0, 0))
                    x, y = self.rotate(x, y, transform['angle'], pivot)
                elif transform_type == 'mirror':
                    center = transform.get('center', (0, 0))
                    x, y = self.mirror(x, y, transform['axis'], center)
                else:
                    print(f"Unknown transformation type: {transform_type}")
            
            # Create new action with transformed coordinates
            new_action = action.copy()
            new_action['x'] = round(x)
            new_action['y'] = round(y)
            transformed_actions.append(new_action)
        
        # Store transformation history
        self.transformation_history.append({
            'transformations': transformations.copy(),
            'timestamp': len(self.transformation_history)
        })
        
        return transformed_actions
    
    def create_translation_transform(self, offset_x: float, offset_y: float) -> Dict[str, Any]:
        """Create a translation transformation configuration"""
        return {
            'type': 'translate',
            'offset_x': offset_x,
            'offset_y': offset_y
        }
    
    def create_scale_transform(self, scale_x: float, scale_y: float, 
                              origin: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """Create a scaling transformation configuration"""
        return {
            'type': 'scale',
            'scale_x': scale_x,
            'scale_y': scale_y,
            'origin': origin or (0, 0)
        }
    
    def create_rotation_transform(self, angle: float, 
                                 pivot: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """Create a rotation transformation configuration"""
        return {
            'type': 'rotate',
            'angle': angle,
            'pivot': pivot or (0, 0)
        }
    
    def create_mirror_transform(self, axis: str, 
                               center: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """Create a mirroring transformation configuration"""
        return {
            'type': 'mirror',
            'axis': axis,
            'center': center or (0, 0)
        }
    
    def get_bounding_box(self, actions: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Get bounding box of all click actions
        
        Args:
            actions (List[Dict]): List of mouse actions
            
        Returns:
            Dict: Bounding box with min_x, min_y, max_x, max_y, width, height
        """
        click_actions = [action for action in actions if action['type'] == 'click']
        
        if not click_actions:
            return {
                'min_x': 0, 'min_y': 0, 'max_x': 0, 'max_y': 0,
                'width': 0, 'height': 0, 'center_x': 0, 'center_y': 0
            }
        
        x_coords = [action['x'] for action in click_actions]
        y_coords = [action['y'] for action in click_actions]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        width = max_x - min_x
        height = max_y - min_y
        center_x = min_x + width / 2
        center_y = min_y + height / 2
        
        return {
            'min_x': min_x, 'min_y': min_y, 'max_x': max_x, 'max_y': max_y,
            'width': width, 'height': height, 'center_x': center_x, 'center_y': center_y
        }
    
    def fit_to_screen(self, actions: List[Dict[str, Any]], 
                      screen_width: int, screen_height: int,
                      margin: int = 50) -> List[Dict[str, Any]]:
        """
        Scale and translate actions to fit within screen bounds
        
        Args:
            actions (List[Dict]): List of mouse actions
            screen_width (int): Target screen width
            screen_height (int): Target screen height
            margin (int): Margin from screen edges
            
        Returns:
            List[Dict]: Transformed actions that fit the screen
        """
        bbox = self.get_bounding_box(actions)
        
        if bbox['width'] == 0 or bbox['height'] == 0:
            return actions
        
        # Calculate scale factors to fit within screen bounds
        available_width = screen_width - 2 * margin
        available_height = screen_height - 2 * margin
        
        scale_x = available_width / bbox['width'] if bbox['width'] > 0 else 1.0
        scale_y = available_height / bbox['height'] if bbox['height'] > 0 else 1.0
        
        # Use the smaller scale factor to maintain aspect ratio
        scale = min(scale_x, scale_y, 1.0)  # Don't scale up
        
        # Create transformations
        transformations = [
            # First, translate to origin
            self.create_translation_transform(-bbox['min_x'], -bbox['min_y']),
            # Then scale
            self.create_scale_transform(scale, scale),
            # Finally, translate to center with margin
            self.create_translation_transform(margin, margin)
        ]
        
        return self.transform_actions(actions, transformations)
    
    def get_transformation_history(self) -> List[Dict[str, Any]]:
        """Get the history of applied transformations"""
        return self.transformation_history.copy()
    
    def clear_transformation_history(self):
        """Clear the transformation history"""
        self.transformation_history.clear()
    
    def preview_transformation(self, actions: List[Dict[str, Any]], 
                              transformations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Preview the result of transformations without applying them
        
        Args:
            actions (List[Dict]): Original actions
            transformations (List[Dict]): Transformations to preview
            
        Returns:
            Dict: Preview information including bounding boxes and sample points
        """
        original_bbox = self.get_bounding_box(actions)
        transformed_actions = self.transform_actions(actions, transformations)
        transformed_bbox = self.get_bounding_box(transformed_actions)
        
        # Get sample points for visualization
        sample_points = []
        for i, action in enumerate(actions[:10]):  # Sample first 10 actions
            if action['type'] == 'click':
                original = (action['x'], action['y'])
                transformed = (transformed_actions[i]['x'], transformed_actions[i]['y'])
                sample_points.append({
                    'original': original,
                    'transformed': transformed
                })
        
        return {
            'original_bbox': original_bbox,
            'transformed_bbox': transformed_bbox,
            'sample_points': sample_points,
            'total_actions': len([a for a in actions if a['type'] == 'click'])
        }