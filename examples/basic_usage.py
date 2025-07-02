#!/usr/bin/env python3
"""
Basic Usage Example

This example demonstrates the basic functionality of the Mouse Automation Toolkit.
Shows how to record, transform, and replay mouse actions programmatically.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recorder import MouseRecorder, MouseAction
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer


def main():
    """Demonstrate basic usage of the toolkit."""
    print("Mouse Automation Toolkit - Basic Usage Example")
    print("=" * 50)
    
    # Initialize components
    recorder = MouseRecorder()
    transformer = CoordinateTransformer()
    player = ActionPlayer()
    
    try:
        # Example 1: Create some sample actions manually
        print("\n1. Creating sample mouse actions...")
        
        sample_actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.5, 'click', 100, 100, 'left', True),
            MouseAction(0.6, 'click', 100, 100, 'left', False),
            MouseAction(1.0, 'move', 200, 200),
            MouseAction(1.5, 'click', 200, 200, 'left', True),
            MouseAction(1.6, 'click', 200, 200, 'left', False),
        ]
        
        print(f"Created {len(sample_actions)} sample actions")
        
        # Example 2: Save actions to file
        print("\n2. Saving actions to file...")
        filename = "sample_actions.json"
        recorder.save_to_file(filename, sample_actions)
        print(f"Saved actions to {filename}")
        
        # Example 3: Load actions from file
        print("\n3. Loading actions from file...")
        loaded_actions = recorder.load_from_file(filename)
        print(f"Loaded {len(loaded_actions)} actions from {filename}")
        
        # Example 4: Transform actions
        print("\n4. Transforming actions...")
        
        # Translate actions
        translated = transformer.translate(loaded_actions, 50, 25)
        print(f"Translated actions by (50, 25)")
        
        # Scale actions
        scaled = transformer.scale(loaded_actions, 1.5, 1.5)
        print(f"Scaled actions by factor 1.5")
        
        # Rotate actions
        rotated = transformer.rotate(loaded_actions, 45)
        print(f"Rotated actions by 45 degrees")
        
        # Example 5: Show transformation results
        print("\n5. Transformation results:")
        print("Original coordinates:")
        for i, action in enumerate(loaded_actions):
            print(f"  Action {i}: ({action.x}, {action.y})")
        
        print("Translated coordinates:")
        for i, action in enumerate(translated):
            print(f"  Action {i}: ({action.x}, {action.y})")
        
        print("Scaled coordinates:")
        for i, action in enumerate(scaled):
            print(f"  Action {i}: ({action.x}, {action.y})")
        
        print("Rotated coordinates:")
        for i, action in enumerate(rotated):
            print(f"  Action {i}: ({action.x}, {action.y})")
        
        # Example 6: Validate actions before playback
        print("\n6. Validating actions...")
        validation = player.validate_actions(loaded_actions)
        print(f"Actions valid: {validation['valid']}")
        
        if validation.get('warnings'):
            print("Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        # Example 7: Chain multiple transformations
        print("\n7. Chaining transformations...")
        chained_transforms = [
            {'type': 'translate', 'offset_x': 100, 'offset_y': 50},
            {'type': 'scale', 'scale_x': 1.2, 'scale_y': 1.2},
            {'type': 'rotate', 'angle_degrees': 30}
        ]
        
        chained_result = transformer.chain_transforms(loaded_actions, chained_transforms)
        print(f"Applied {len(chained_transforms)} chained transformations")
        
        print("Final coordinates:")
        for i, action in enumerate(chained_result):
            print(f"  Action {i}: ({action.x}, {action.y})")
        
        # Example 8: Get transformation information
        print("\n8. Transformation analysis...")
        transform_info = transformer.get_transformation_info(loaded_actions, chained_result)
        
        print(f"Original bounds: {transform_info['original_bounds']}")
        print(f"Transformed bounds: {transform_info['transformed_bounds']}")
        print(f"Center shift: {transform_info['center_shift']}")
        print(f"Scale factors: {transform_info['scale_factors']}")
        print(f"Area ratio: {transform_info['area_ratio']:.2f}")
        
        # Example 9: Interactive recording (optional)
        response = input("\n9. Would you like to try interactive recording? (y/n): ")
        if response.lower() == 'y':
            print("Starting interactive recording...")
            print("Move your mouse and click a few times")
            print("Recording will stop automatically after 5 seconds")
            
            recorded_actions = recorder.record(duration=5.0)
            
            if recorded_actions:
                print(f"Recorded {len(recorded_actions)} actions")
                
                # Show recording statistics
                stats = {
                    'click_count': len([a for a in recorded_actions if a.action_type == 'click']),
                    'move_count': len([a for a in recorded_actions if a.action_type == 'move']),
                    'scroll_count': len([a for a in recorded_actions if a.action_type == 'scroll']),
                }
                
                print(f"Statistics: {stats}")
                
                # Save recorded actions
                recorder.save_to_file("recorded_actions.json", recorded_actions)
                print("Saved recorded actions to 'recorded_actions.json'")
            else:
                print("No actions were recorded")
        
        print("\n" + "=" * 50)
        print("Basic usage example completed successfully!")
        print("\nNext steps:")
        print("- Try the GUI interface: python main.py --gui")
        print("- Record your own actions: python main.py --record my_actions.json")
        print("- Play back actions: python main.py --play my_actions.json")
        
    except Exception as e:
        print(f"Error during example execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        recorder.cleanup()
        player.cleanup()


if __name__ == "__main__":
    main()