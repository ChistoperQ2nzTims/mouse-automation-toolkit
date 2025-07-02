#!/usr/bin/env python3
"""
Advanced Transform Example for Mouse Automation Toolkit

This example demonstrates coordinate transformation capabilities.
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.recorder import MouseRecorder, MouseAction
from src.transformer import CoordinateTransformer
from src.player import MousePlayer


def create_sample_actions():
    """Create sample actions for demonstration."""
    actions = [
        MouseAction('move', 100, 100, timestamp=0.0, delay=0.0),
        MouseAction('press', 100, 100, 'left', timestamp=0.1, delay=0.1),
        MouseAction('release', 100, 100, 'left', timestamp=0.2, delay=0.1),
        MouseAction('move', 200, 100, timestamp=0.5, delay=0.3),
        MouseAction('press', 200, 100, 'left', timestamp=0.6, delay=0.1),
        MouseAction('release', 200, 100, 'left', timestamp=0.7, delay=0.1),
        MouseAction('move', 200, 200, timestamp=1.0, delay=0.3),
        MouseAction('press', 200, 200, 'left', timestamp=1.1, delay=0.1),
        MouseAction('release', 200, 200, 'left', timestamp=1.2, delay=0.1),
        MouseAction('move', 100, 200, timestamp=1.5, delay=0.3),
        MouseAction('press', 100, 200, 'left', timestamp=1.6, delay=0.1),
        MouseAction('release', 100, 200, 'left', timestamp=1.7, delay=0.1),
    ]
    return actions


def print_action_coordinates(actions, title):
    """Print coordinates of actions for comparison."""
    print(f"\n{title}:")
    print("   Index | Action | Coordinates")
    print("   ------|--------|------------")
    for i, action in enumerate(actions):
        print(f"   {i+1:5} | {action.action_type:6} | ({action.x:4}, {action.y:4})")


def main():
    """Demonstrate advanced transformation capabilities."""
    print("🔄 Mouse Automation Toolkit - Advanced Transform Example")
    print("=" * 60)
    
    # Create transformer and sample data
    transformer = CoordinateTransformer()
    transformer.set_screen_dimensions(1920, 1080)
    
    # Create sample actions (a square pattern)
    original_actions = create_sample_actions()
    print(f"📝 Created {len(original_actions)} sample actions (square pattern)")
    
    print_action_coordinates(original_actions, "Original coordinates")
    
    # Get bounds of original actions
    min_x, min_y, max_x, max_y = transformer.get_bounds(original_actions)
    print(f"\n📏 Original bounds: ({min_x}, {min_y}) to ({max_x}, {max_y})")
    print(f"   Size: {max_x - min_x} x {max_y - min_y}")
    
    print(f"\n🔄 Applying various transformations...")
    
    # 1. Translation
    print(f"\n1. Translation (+50, +30)")
    translated = transformer.translate(original_actions, 50, 30)
    print_action_coordinates(translated, "After translation")
    
    # 2. Scaling
    print(f"\n2. Scaling (2x, 1.5x)")
    scaled = transformer.scale(original_actions, 2.0, 1.5)
    print_action_coordinates(scaled, "After scaling")
    
    # 3. Rotation
    print(f"\n3. Rotation (45 degrees)")
    rotated = transformer.rotate(original_actions, 45)
    print_action_coordinates(rotated, "After rotation")
    
    # 4. Horizontal mirror
    print(f"\n4. Horizontal mirror")
    h_mirrored = transformer.mirror_horizontal(original_actions)
    print_action_coordinates(h_mirrored, "After horizontal mirror")
    
    # 5. Vertical mirror
    print(f"\n5. Vertical mirror")
    v_mirrored = transformer.mirror_vertical(original_actions)
    print_action_coordinates(v_mirrored, "After vertical mirror")
    
    # 6. Chained transformations
    print(f"\n6. Chained transformations (translate + scale + rotate)")
    chain_transforms = [
        ('translate', {'offset_x': 100, 'offset_y': 100}),
        ('scale', {'scale_x': 1.5, 'scale_y': 1.5}),
        ('rotate', {'angle_degrees': 30})
    ]
    
    chained = transformer.chain_transforms(original_actions, chain_transforms)
    print_action_coordinates(chained, "After chained transformations")
    
    # 7. Normalization
    print(f"\n7. Normalization to 300x300 bounds")
    normalized = transformer.normalize_to_bounds(original_actions, 300, 300)
    print_action_coordinates(normalized, "After normalization")
    
    norm_min_x, norm_min_y, norm_max_x, norm_max_y = transformer.get_bounds(normalized)
    print(f"   Normalized bounds: ({norm_min_x}, {norm_min_y}) to ({norm_max_x}, {norm_max_y})")
    print(f"   Normalized size: {norm_max_x - norm_min_x} x {norm_max_y - norm_min_y}")
    
    # Save examples to files
    print(f"\n💾 Saving transformation examples...")
    
    examples = {
        'original': original_actions,
        'translated': translated,
        'scaled': scaled,
        'rotated': rotated,
        'h_mirrored': h_mirrored,
        'v_mirrored': v_mirrored,
        'chained': chained,
        'normalized': normalized
    }
    
    recorder = MouseRecorder()
    for name, actions in examples.items():
        filename = f"transform_example_{name}.json"
        recorder.actions = actions
        recorder.save_to_file(filename)
        print(f"   📁 {filename}")
    
    # Validation of all transformations
    print(f"\n✅ Validating all transformations...")
    player = MousePlayer()
    
    for name, actions in examples.items():
        warnings = player.validate_actions(actions)
        if warnings:
            print(f"   ⚠️ {name}: {len(warnings)} warnings")
        else:
            print(f"   ✅ {name}: Valid")
    
    # Interactive demonstration
    print(f"\n🎮 Interactive demonstration:")
    print("   Choose a transformation to preview:")
    print("   1. Original")
    print("   2. Translated (+50, +30)")
    print("   3. Scaled (2x, 1.5x)")
    print("   4. Rotated (45°)")
    print("   5. Horizontally mirrored")
    print("   6. Vertically mirrored")
    print("   7. Chained (translate + scale + rotate)")
    print("   8. Normalized (300x300)")
    print("   0. Skip preview")
    
    try:
        choice = input("\n   Enter choice (0-8): ")
        choice_map = {
            '1': ('Original', original_actions),
            '2': ('Translated', translated),
            '3': ('Scaled', scaled),
            '4': ('Rotated', rotated),
            '5': ('Horizontally mirrored', h_mirrored),
            '6': ('Vertically mirrored', v_mirrored),
            '7': ('Chained', chained),
            '8': ('Normalized', normalized)
        }
        
        if choice in choice_map:
            name, actions = choice_map[choice]
            print(f"\n📋 Preview of {name} transformation:")
            preview = player.preview_actions(actions)
            
            print("   Index | Type    | Position     | Button | Delay")
            print("   ------|---------|--------------|--------|-------")
            for item in preview:
                print(f"   {item['index']:5} | {item['action_type']:7} | {item['position']:12} | {item['button']:6} | {item['delay']}")
            
            response = input(f"\n   Replay {name} actions? (y/N): ")
            if response.lower() == 'y':
                print(f"   ▶️ Playing {name} actions...")
                
                player.play_actions(actions, delay_multiplier=0.3)
                
                while player.is_playing:
                    import time
                    time.sleep(0.1)
                
                print("   ✅ Playback completed!")
        
    except KeyboardInterrupt:
        print("\n   Preview cancelled.")
    
    print(f"\n🎉 Advanced transform example completed!")
    print("📁 All transformation examples saved as JSON files.")
    print("💡 Try loading these files in the GUI to see the visual differences!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Example interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()