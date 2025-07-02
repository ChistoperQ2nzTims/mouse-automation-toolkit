#!/usr/bin/env python3
"""
Basic Usage Example for Mouse Automation Toolkit

This example demonstrates basic recording and playback functionality.
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.recorder import MouseRecorder
from src.player import MousePlayer


def main():
    """Demonstrate basic recording and playback."""
    print("🐭 Mouse Automation Toolkit - Basic Usage Example")
    print("=" * 50)
    
    # Create components
    recorder = MouseRecorder(smart_recording=True)
    player = MousePlayer()
    
    # Recording example
    print("\n1. Recording mouse actions...")
    print("   Move your mouse and click a few times.")
    print("   Recording will start in 3 seconds...")
    
    for i in range(3, 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1)
    
    print("   🔴 RECORDING STARTED! (Recording for 10 seconds)")
    recorder.start_recording()
    
    # Record for 10 seconds
    time.sleep(10)
    
    recorder.stop_recording()
    actions = recorder.get_actions()
    print(f"   ⏹️ Recording stopped. Captured {len(actions)} actions.")
    
    if not actions:
        print("   No actions recorded. Please run again and move the mouse.")
        return
    
    # Save actions
    filename = "basic_example_actions.json"
    recorder.save_to_file(filename)
    print(f"   💾 Actions saved to {filename}")
    
    # Display some action details
    print(f"\n2. Action details:")
    for i, action in enumerate(actions[:5]):  # Show first 5 actions
        print(f"   Action {i+1}: {action.action_type} at ({action.x}, {action.y})")
        if action.button:
            print(f"              Button: {action.button}")
        if action.delay > 0:
            print(f"              Delay: {action.delay:.3f}s")
    
    if len(actions) > 5:
        print(f"   ... and {len(actions) - 5} more actions")
    
    # Validation
    print(f"\n3. Validating actions...")
    warnings = player.validate_actions(actions)
    if warnings:
        print(f"   ⚠️ Found {len(warnings)} warnings:")
        for warning in warnings[:3]:
            print(f"      {warning}")
        if len(warnings) > 3:
            print(f"      ... and {len(warnings) - 3} more")
    else:
        print("   ✅ All actions are valid!")
    
    # Playback confirmation
    print(f"\n4. Playback demonstration...")
    estimated_duration = player.get_estimated_duration(actions)
    print(f"   Estimated playback duration: {estimated_duration:.1f} seconds")
    
    response = input("   Do you want to replay the actions? (y/N): ")
    if response.lower() == 'y':
        print("   Playback starting in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"   Starting in {i}...")
            time.sleep(1)
        
        print("   ▶️ PLAYBACK STARTED!")
        
        # Set up progress callback
        def progress_callback(current, total):
            progress = (current / total) * 100
            print(f"   Progress: {current}/{total} ({progress:.1f}%)")
        
        # Play actions
        player.play_actions(
            actions,
            delay_multiplier=0.5,  # Play at half speed for demo
            progress_callback=progress_callback
        )
        
        # Wait for completion
        while player.is_playing:
            time.sleep(0.1)
        
        print("   ✅ Playback completed!")
    else:
        print("   Playback skipped.")
    
    print(f"\n🎉 Basic example completed!")
    print(f"📁 Actions saved to: {filename}")
    print("💡 Try loading this file in the GUI application!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Example interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()