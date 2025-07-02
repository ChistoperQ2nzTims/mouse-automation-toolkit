#!/usr/bin/env python3
"""
Basic Usage Example - Mouse Automation Toolkit

This example demonstrates the basic functionality of the Mouse Automation Toolkit
including recording, transforming, and playing back mouse actions.
"""

import sys
import os
import time
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.recorder import MouseRecorder
    from src.transformer import CoordinateTransformer
    from src.player import ActionPlayer
except ImportError:
    print("Error: Could not import required modules. Please ensure pynput and PyAutoGUI are installed.")
    print("Run: pip install pynput PyAutoGUI")
    sys.exit(1)


def basic_recording_example():
    """Demonstrate basic recording functionality"""
    print("=== Basic Recording Example ===")
    
    recorder = MouseRecorder()
    
    # Set up callback to show recorded actions
    def on_action(action):
        print(f"Recorded: {action['button']} click at ({action['x']}, {action['y']}) at {action['timestamp']:.2f}s")
    
    recorder.set_action_callback(on_action)
    
    print("Starting recording for 10 seconds...")
    print("Click anywhere on the screen!")
    
    # Start recording
    if recorder.start_recording():
        time.sleep(10)  # Record for 10 seconds
        recorder.stop_recording()
        
        actions = recorder.get_actions()
        print(f"\nRecorded {len(actions)} actions")
        
        # Save to file
        if recorder.save_to_file("example_recording.json"):
            print("Recording saved to: example_recording.json")
        
        return actions
    else:
        print("Failed to start recording")
        return []


def basic_transformation_example(actions):
    """Demonstrate basic transformation functionality"""
    print("\n=== Basic Transformation Example ===")
    
    if not actions:
        print("No actions to transform")
        return actions
    
    transformer = CoordinateTransformer()
    
    # Show original bounding box
    bbox = transformer.get_bounding_box(actions)
    print(f"Original bounding box: {bbox['width']:.0f}x{bbox['height']:.0f} at ({bbox['min_x']:.0f}, {bbox['min_y']:.0f})")
    
    # Apply a translation
    print("Applying translation (+100, +50)...")
    transformations = [transformer.create_translation_transform(100, 50)]
    transformed_actions = transformer.transform_actions(actions, transformations)
    
    # Show new bounding box
    new_bbox = transformer.get_bounding_box(transformed_actions)
    print(f"New bounding box: {new_bbox['width']:.0f}x{new_bbox['height']:.0f} at ({new_bbox['min_x']:.0f}, {new_bbox['min_y']:.0f})")
    
    # Apply scaling
    print("Applying scaling (0.5x, 0.5x)...")
    transformations = [transformer.create_scale_transform(0.5, 0.5, (new_bbox['center_x'], new_bbox['center_y']))]
    transformed_actions = transformer.transform_actions(transformed_actions, transformations)
    
    # Show final bounding box
    final_bbox = transformer.get_bounding_box(transformed_actions)
    print(f"Final bounding box: {final_bbox['width']:.0f}x{final_bbox['height']:.0f} at ({final_bbox['min_x']:.0f}, {final_bbox['min_y']:.0f})")
    
    return transformed_actions


def basic_playback_example(actions):
    """Demonstrate basic playback functionality"""
    print("\n=== Basic Playback Example ===")
    
    if not actions:
        print("No actions to play back")
        return
    
    player = ActionPlayer()
    
    # Set up callbacks
    def on_progress(progress, current, total):
        print(f"\rProgress: {progress*100:.1f}% ({current}/{total})", end='', flush=True)
    
    def on_complete(loops):
        print(f"\nPlayback completed. Loops: {loops}")
    
    player.set_progress_callback(on_progress)
    player.set_complete_callback(on_complete)
    
    # Load actions
    if not player.load_actions(actions):
        print("Failed to load actions")
        return
    
    # Configure playback
    player.set_speed(2.0)  # 2x speed
    player.set_safe_mode(True)  # Enable safety checks
    
    print(f"Playing back {len(actions)} actions at 2x speed...")
    print("Press ESC to stop playback early")
    
    if player.play():
        # Wait for playback to complete
        while player.is_playing:
            time.sleep(0.1)
    else:
        print("Failed to start playback")


def file_operations_example():
    """Demonstrate file loading and saving operations"""
    print("\n=== File Operations Example ===")
    
    # Try to load the example recording
    try:
        with open("example_recording.json", "r") as f:
            data = json.load(f)
            actions = data.get('actions', data) if isinstance(data, dict) else data
        
        print(f"Loaded {len(actions)} actions from file")
        
        # Show some statistics
        if actions:
            duration = actions[-1]['timestamp'] if actions else 0
            print(f"Recording duration: {duration:.2f} seconds")
            
            # Count button types
            button_counts = {}
            for action in actions:
                button = action.get('button', 'unknown')
                button_counts[button] = button_counts.get(button, 0) + 1
            
            print("Button distribution:")
            for button, count in button_counts.items():
                print(f"  {button}: {count}")
        
        return actions
    
    except FileNotFoundError:
        print("No example recording found. Run the recording example first.")
        return []
    except Exception as e:
        print(f"Error loading file: {e}")
        return []


def validation_example(actions):
    """Demonstrate action validation functionality"""
    print("\n=== Validation Example ===")
    
    if not actions:
        print("No actions to validate")
        return
    
    player = ActionPlayer()
    
    # Get screen dimensions (mock values for demo)
    screen_width = 1920
    screen_height = 1080
    player.set_screen_bounds(screen_width, screen_height)
    
    if hasattr(player, 'validate_actions'):
        player.load_actions(actions)
        validation = player.validate_actions()
        
        print(f"Validation result: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
        
        if validation.get('issues'):
            print("Issues:")
            for issue in validation['issues']:
                print(f"  • {issue}")
        
        if validation.get('warnings'):
            print("Warnings:")
            for warning in validation['warnings']:
                print(f"  ⚠ {warning}")
        
        print(f"Total actions: {validation.get('total_actions', 0)}")
        print(f"Duration: {validation.get('duration', 0):.2f} seconds")
    else:
        print("Validation not available in this version")


def main():
    """Main example function"""
    print("Mouse Automation Toolkit - Basic Usage Examples")
    print("=" * 50)
    
    # Example 1: Basic recording
    # Note: This will actually try to record mouse clicks
    # Uncomment the line below to enable recording
    # actions = basic_recording_example()
    
    # For demo purposes, use file operations instead
    actions = file_operations_example()
    
    if not actions:
        # Create some sample actions for demonstration
        print("Creating sample actions for demonstration...")
        actions = [
            {
                'type': 'click',
                'x': 100,
                'y': 100,
                'button': 'left',
                'timestamp': 0.0,
                'absolute_time': '2024-01-01T12:00:00'
            },
            {
                'type': 'click',
                'x': 200,
                'y': 150,
                'button': 'left',
                'timestamp': 1.5,
                'absolute_time': '2024-01-01T12:00:01'
            },
            {
                'type': 'click',
                'x': 150,
                'y': 200,
                'button': 'right',
                'timestamp': 3.0,
                'absolute_time': '2024-01-01T12:00:03'
            }
        ]
        print(f"Created {len(actions)} sample actions")
    
    # Example 2: Transform the actions
    transformed_actions = basic_transformation_example(actions)
    
    # Example 3: Validate actions
    validation_example(transformed_actions)
    
    # Example 4: Playback (commented out to avoid unwanted clicks)
    # Uncomment the line below to enable playback
    # basic_playback_example(transformed_actions)
    
    print("\n=== Examples completed ===")
    print("To enable recording and playback, uncomment the respective lines in this script.")
    print("Make sure you have a safe environment before enabling playback!")


if __name__ == "__main__":
    main()