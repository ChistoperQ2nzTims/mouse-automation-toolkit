#!/usr/bin/env python3
"""
Advanced Transformation Example

This example demonstrates advanced coordinate transformation capabilities
including matrix transformations, fitting to screen, and complex chaining.
"""

import sys
import math
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import numpy as np
except ImportError:
    print("Error: numpy is required for advanced transformations")
    print("Install with: pip install numpy")
    sys.exit(1)

from src.recorder import MouseRecorder, MouseAction
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer


def create_complex_pattern():
    """Create a complex pattern of mouse actions for transformation."""
    actions = []
    
    # Create a spiral pattern
    center_x, center_y = 300, 300
    num_points = 20
    
    for i in range(num_points):
        angle = i * (2 * math.pi / num_points) * 3  # 3 full rotations
        radius = 10 + i * 5  # Expanding radius
        
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        timestamp = i * 0.1
        
        actions.append(MouseAction(timestamp, 'move', int(x), int(y)))
        
        # Add clicks at certain points
        if i % 5 == 0:
            actions.append(MouseAction(timestamp + 0.05, 'click', int(x), int(y), 'left', True))
            actions.append(MouseAction(timestamp + 0.1, 'click', int(x), int(y), 'left', False))
    
    return actions


def demonstrate_matrix_transformation(transformer, actions):
    """Demonstrate custom matrix transformations."""
    print("\n--- Matrix Transformations ---")
    
    # Example 1: Shear transformation
    print("1. Shear transformation")
    shear_matrix = np.array([
        [1, 0.5, 0],  # Shear in X direction
        [0, 1, 0],
        [0, 0, 1]
    ])
    
    sheared = transformer.apply_matrix_transform(actions, shear_matrix)
    print(f"Applied shear transformation to {len(actions)} actions")
    
    # Example 2: Custom scaling with translation
    print("2. Combined scale and translate matrix")
    scale_translate_matrix = np.array([
        [1.5, 0, 100],  # Scale by 1.5 and translate by 100
        [0, 1.5, 50],   # Scale by 1.5 and translate by 50
        [0, 0, 1]
    ])
    
    scaled_translated = transformer.apply_matrix_transform(actions, scale_translate_matrix)
    print(f"Applied combined scale/translate transformation")
    
    # Example 3: Perspective-like transformation
    print("3. Perspective-like transformation")
    perspective_matrix = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0.001, 0.001, 1]  # Small perspective effect
    ])
    
    perspective = transformer.apply_matrix_transform(actions, perspective_matrix)
    print(f"Applied perspective transformation")
    
    return sheared, scaled_translated, perspective


def demonstrate_advanced_scaling(transformer, actions):
    """Demonstrate advanced scaling operations."""
    print("\n--- Advanced Scaling ---")
    
    # Get original bounds
    bounds = transformer._get_action_bounds(actions)
    print(f"Original bounds: {bounds}")
    
    # Example 1: Non-uniform scaling
    print("1. Non-uniform scaling (stretch)")
    stretched = transformer.scale(actions, 2.0, 0.5)  # Wide and short
    stretched_bounds = transformer._get_action_bounds(stretched)
    print(f"Stretched bounds: {stretched_bounds}")
    
    # Example 2: Scaling around different center points
    print("2. Scaling around top-left corner")
    corner_scaled = transformer.scale(actions, 1.5, 1.5, bounds['min_x'], bounds['min_y'])
    corner_bounds = transformer._get_action_bounds(corner_scaled)
    print(f"Corner-scaled bounds: {corner_bounds}")
    
    # Example 3: Scaling to fit specific dimensions
    print("3. Scaling to fit 800x600 area")
    target_width, target_height = 800, 600
    
    current_width = bounds['max_x'] - bounds['min_x']
    current_height = bounds['max_y'] - bounds['min_y']
    
    if current_width > 0 and current_height > 0:
        scale_x = target_width / current_width
        scale_y = target_height / current_height
        
        fitted = transformer.scale(actions, scale_x, scale_y)
        fitted_bounds = transformer._get_action_bounds(fitted)
        print(f"Fitted bounds: {fitted_bounds}")
    
    return stretched, corner_scaled, fitted


def demonstrate_screen_fitting(transformer, actions):
    """Demonstrate screen fitting capabilities."""
    print("\n--- Screen Fitting ---")
    
    # Simulate different screen sizes
    screen_sizes = [
        (1920, 1080, "Full HD"),
        (1366, 768, "HD"),
        (800, 600, "SVGA"),
        (1280, 720, "HD 720p")
    ]
    
    fitted_actions = {}
    
    for width, height, name in screen_sizes:
        print(f"Fitting to {name} ({width}x{height})")
        
        # Fit with aspect ratio maintained
        fitted_maintain = transformer.fit_to_screen(actions, width, height, maintain_aspect_ratio=True)
        bounds_maintain = transformer._get_action_bounds(fitted_maintain)
        
        # Fit without maintaining aspect ratio
        fitted_stretch = transformer.fit_to_screen(actions, width, height, maintain_aspect_ratio=False)
        bounds_stretch = transformer._get_action_bounds(fitted_stretch)
        
        fitted_actions[name] = {
            'maintain_aspect': fitted_maintain,
            'stretch': fitted_stretch
        }
        
        print(f"  Maintain aspect: {bounds_maintain}")
        print(f"  Stretch: {bounds_stretch}")
    
    return fitted_actions


def demonstrate_complex_chaining(transformer, actions):
    """Demonstrate complex transformation chaining."""
    print("\n--- Complex Transformation Chaining ---")
    
    # Example 1: Animation-like sequence
    print("1. Animation sequence")
    animation_transforms = [
        {'type': 'scale', 'scale_x': 0.5, 'scale_y': 0.5},  # Shrink
        {'type': 'rotate', 'angle_degrees': 90},             # Rotate
        {'type': 'translate', 'offset_x': 200, 'offset_y': 100},  # Move
        {'type': 'scale', 'scale_x': 2.0, 'scale_y': 2.0},  # Grow
        {'type': 'mirror_horizontal'}                         # Mirror
    ]
    
    animated = transformer.chain_transforms(actions, animation_transforms)
    print(f"Applied {len(animation_transforms)} animation transforms")
    
    # Example 2: Correction sequence
    print("2. Correction sequence")
    correction_transforms = [
        {'type': 'translate', 'offset_x': -50, 'offset_y': -30},  # Offset correction
        {'type': 'rotate', 'angle_degrees': -5},                   # Slight rotation correction
        {'type': 'scale', 'scale_x': 1.02, 'scale_y': 0.98},     # Slight aspect correction
    ]
    
    corrected = transformer.chain_transforms(actions, correction_transforms)
    print(f"Applied {len(correction_transforms)} correction transforms")
    
    # Example 3: Kaleidoscope effect
    print("3. Kaleidoscope effect")
    kaleidoscope_results = []
    
    for i in range(6):  # 6 copies
        angle = i * 60  # 60 degrees apart
        transforms = [
            {'type': 'rotate', 'angle_degrees': angle},
            {'type': 'scale', 'scale_x': 0.3, 'scale_y': 0.3},
            {'type': 'translate', 'offset_x': 100 * math.cos(math.radians(angle)), 
                                  'offset_y': 100 * math.sin(math.radians(angle))}
        ]
        
        kaleidoscope_copy = transformer.chain_transforms(actions, transforms)
        kaleidoscope_results.append(kaleidoscope_copy)
    
    print(f"Created {len(kaleidoscope_results)} kaleidoscope copies")
    
    return animated, corrected, kaleidoscope_results


def demonstrate_timing_transformations(transformer, actions):
    """Demonstrate timing-based transformations."""
    print("\n--- Timing Transformations ---")
    
    if len(actions) < 2:
        print("Need at least 2 actions for timing transformations")
        return
    
    original_duration = actions[-1].timestamp - actions[0].timestamp
    print(f"Original duration: {original_duration:.2f} seconds")
    
    # Example 1: Speed up
    print("1. Speed up (half duration)")
    sped_up = transformer.normalize_timing(actions, original_duration / 2)
    new_duration = sped_up[-1].timestamp - sped_up[0].timestamp
    print(f"New duration: {new_duration:.2f} seconds")
    
    # Example 2: Slow down
    print("2. Slow down (double duration)")
    slowed_down = transformer.normalize_timing(actions, original_duration * 2)
    new_duration2 = slowed_down[-1].timestamp - slowed_down[0].timestamp
    print(f"New duration: {new_duration2:.2f} seconds")
    
    # Example 3: Fixed duration
    print("3. Fixed 10-second duration")
    fixed_duration = transformer.normalize_timing(actions, 10.0)
    new_duration3 = fixed_duration[-1].timestamp - fixed_duration[0].timestamp
    print(f"New duration: {new_duration3:.2f} seconds")
    
    return sped_up, slowed_down, fixed_duration


def main():
    """Run the advanced transformation example."""
    print("Mouse Automation Toolkit - Advanced Transformation Example")
    print("=" * 60)
    
    # Initialize components
    recorder = MouseRecorder()
    transformer = CoordinateTransformer()
    player = ActionPlayer()
    
    try:
        # Create a complex pattern
        print("Creating complex pattern...")
        actions = create_complex_pattern()
        print(f"Created {len(actions)} actions in a spiral pattern")
        
        # Save original pattern
        recorder.save_to_file("complex_pattern.json", actions)
        
        # Show original bounds
        original_bounds = transformer._get_action_bounds(actions)
        print(f"Original pattern bounds: {original_bounds}")
        
        # Demonstrate various transformations
        matrix_results = demonstrate_matrix_transformation(transformer, actions)
        scaling_results = demonstrate_advanced_scaling(transformer, actions)
        screen_fitting_results = demonstrate_screen_fitting(transformer, actions)
        chaining_results = demonstrate_complex_chaining(transformer, actions)
        timing_results = demonstrate_timing_transformations(transformer, actions)
        
        # Save some interesting results
        print("\n--- Saving Results ---")
        
        # Save matrix transformations
        sheared, scaled_translated, perspective = matrix_results
        recorder.save_to_file("sheared_pattern.json", sheared)
        recorder.save_to_file("scaled_translated_pattern.json", scaled_translated)
        
        # Save screen fitting examples
        if 'Full HD' in screen_fitting_results:
            fullhd_maintain = screen_fitting_results['Full HD']['maintain_aspect']
            recorder.save_to_file("fullhd_pattern.json", fullhd_maintain)
        
        # Save animation sequence
        animated, corrected, kaleidoscope = chaining_results
        recorder.save_to_file("animated_pattern.json", animated)
        
        # Save kaleidoscope pieces
        for i, piece in enumerate(kaleidoscope):
            recorder.save_to_file(f"kaleidoscope_piece_{i}.json", piece)
        
        # Demonstrate transformation analysis
        print("\n--- Transformation Analysis ---")
        
        for name, result_actions in [
            ("Original", actions),
            ("Sheared", sheared),
            ("Animated", animated),
        ]:
            bounds = transformer._get_action_bounds(result_actions)
            info = transformer.get_transformation_info(actions, result_actions)
            
            print(f"\n{name}:")
            print(f"  Bounds: {bounds}")
            print(f"  Center shift: ({info['center_shift']['x']:.1f}, {info['center_shift']['y']:.1f})")
            print(f"  Scale factors: ({info['scale_factors']['x']:.2f}, {info['scale_factors']['y']:.2f})")
            print(f"  Area ratio: {info['area_ratio']:.2f}")
        
        # Interactive playback option
        response = input("\nWould you like to see a playback preview? (y/n): ")
        if response.lower() == 'y':
            print("Choose a pattern to preview:")
            print("1. Original spiral")
            print("2. Sheared pattern")
            print("3. Animated sequence")
            
            choice = input("Enter choice (1-3): ")
            
            preview_actions = actions
            if choice == '2':
                preview_actions = sheared
            elif choice == '3':
                preview_actions = animated
            
            print("Validating actions...")
            validation = player.validate_actions(preview_actions)
            
            if validation['valid']:
                print("Starting preview in 3 seconds...")
                print("Press ESC to stop")
                
                player.replay(preview_actions, delay=0.1, speed_multiplier=0.5, start_delay=3.0)
            else:
                print("Actions failed validation:")
                for error in validation.get('errors', []):
                    print(f"  - {error}")
        
        print("\n" + "=" * 60)
        print("Advanced transformation example completed!")
        print("\nFiles created:")
        print("- complex_pattern.json (original spiral)")
        print("- sheared_pattern.json (shear transformation)")
        print("- scaled_translated_pattern.json (matrix transformation)")
        print("- fullhd_pattern.json (fitted to Full HD)")
        print("- animated_pattern.json (animation sequence)")
        print("- kaleidoscope_piece_*.json (kaleidoscope effect)")
        
        print("\nYou can replay these with:")
        print("python main.py --play <filename>")
        
    except Exception as e:
        print(f"Error during advanced example: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        recorder.cleanup()
        player.cleanup()


if __name__ == "__main__":
    main()