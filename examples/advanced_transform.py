"""
Advanced Transformation Example
Demonstrates coordinate transformation capabilities.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from recorder import MouseRecorder, MouseAction
from transformer import CoordinateTransformer
from player import ActionPlayer


def create_sample_actions():
    """Create sample actions for demonstration."""
    actions = [
        MouseAction(100, 100, "left", 0.0),
        MouseAction(200, 100, "left", 1.0),
        MouseAction(200, 200, "left", 2.0),
        MouseAction(100, 200, "left", 3.0),
        MouseAction(150, 150, "right", 4.0),
    ]
    return actions


def print_actions(actions, title):
    """Print actions with a title."""
    print(f"\n{title}:")
    for i, action in enumerate(actions):
        print(f"  {i+1}: ({action.x:3d}, {action.y:3d}) {action.button} at {action.timestamp:.1f}s")


def main():
    """Advanced transformation example."""
    print("Mouse Automation Toolkit - Advanced Transformation Example")
    print("=" * 60)
    
    # Create sample actions (a square with center click)
    original_actions = create_sample_actions()
    print_actions(original_actions, "Original Actions (Square Pattern)")
    
    # Create transformer
    transformer = CoordinateTransformer()
    
    # Show bounding box
    min_x, min_y, max_x, max_y = transformer.get_bounding_box(original_actions)
    center_x, center_y = transformer.get_center_point(original_actions)
    print(f"\nBounding Box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
    print(f"Center Point: ({center_x}, {center_y})")
    
    # 1. Translation
    print("\n" + "="*40)
    print("1. TRANSLATION")
    translated = transformer.translate(original_actions, 300, 300)
    print_actions(translated, "Translated by (300, 300)")
    
    # 2. Scaling
    print("\n" + "="*40)
    print("2. SCALING")
    scaled = transformer.scale(original_actions, 2.0, 1.5, center_x, center_y)
    print_actions(scaled, "Scaled 2x horizontally, 1.5x vertically")
    
    # 3. Rotation
    print("\n" + "="*40)
    print("3. ROTATION")
    rotated = transformer.rotate(original_actions, 45, center_x, center_y)
    print_actions(rotated, "Rotated 45 degrees around center")
    
    # 4. Mirroring
    print("\n" + "="*40)
    print("4. MIRRORING")
    mirrored_h = transformer.mirror_horizontal(original_actions, center_x)
    print_actions(mirrored_h, "Mirrored horizontally")
    
    mirrored_v = transformer.mirror_vertical(original_actions, center_y)
    print_actions(mirrored_v, "Mirrored vertically")
    
    # 5. Complex transformation chain
    print("\n" + "="*40)
    print("5. TRANSFORMATION CHAIN")
    
    transformations = [
        {"type": "translate", "params": {"offset_x": 100, "offset_y": 50}},
        {"type": "scale", "params": {"scale_x": 1.5, "scale_y": 1.5, "center_x": 150, "center_y": 150}},
        {"type": "rotate", "params": {"angle": 30, "center_x": 225, "center_y": 225}},
    ]
    
    chained = transformer.apply_transformation_chain(original_actions, transformations)
    print_actions(chained, "Chain: Translate(100,50) → Scale(1.5x) → Rotate(30°)")
    
    # 6. Fit to screen
    print("\n" + "="*40)
    print("6. FIT TO SCREEN")
    fitted = transformer.fit_to_screen(original_actions, 800, 600, margin=50)
    print_actions(fitted, "Fitted to 800x600 screen with 50px margin")
    
    # 7. Save and demonstrate playback
    print("\n" + "="*40)
    print("7. SAVE AND PLAYBACK DEMO")
    
    # Create recorder and save different transformations
    recorder = MouseRecorder()
    
    # Save original
    recorder.actions = original_actions
    recorder.save_to_file("sample_original.json")
    print("Saved original actions to sample_original.json")
    
    # Save transformed
    recorder.actions = chained
    recorder.save_to_file("sample_transformed.json")
    print("Saved transformed actions to sample_transformed.json")
    
    # Demonstrate loading and preview
    player = ActionPlayer()
    
    print("\nPreviewing original actions:")
    player.preview_actions(original_actions)
    
    print("\nPreviewing transformed actions:")
    player.preview_actions(chained)
    
    print("\n" + "="*60)
    print("Transformation example completed!")
    print("\nFiles created:")
    print("  - sample_original.json")
    print("  - sample_transformed.json")
    print("\nYou can load these files in the GUI to see the transformations.")


if __name__ == "__main__":
    main()