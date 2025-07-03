"""
Basic Usage Example
Demonstrates basic recording and playback functionality.
"""

import time
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from recorder import MouseRecorder
from player import ActionPlayer


def main():
    """Basic usage example."""
    print("Mouse Automation Toolkit - Basic Usage Example")
    print("=" * 50)
    
    # Create recorder and player
    recorder = MouseRecorder()
    player = ActionPlayer()
    
    # Record some actions
    print("\n1. Recording mouse actions...")
    print("   Click anywhere on the screen. Recording will start in 3 seconds.")
    
    for i in range(3, 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1)
    
    print("   Recording started! Click 3-5 times, then wait 5 seconds.")
    recorder.start_recording()
    
    # Record for 10 seconds
    time.sleep(10)
    
    recorder.stop_recording()
    actions = recorder.get_actions()
    
    if not actions:
        print("   No actions recorded. Please run again and click some areas.")
        return
    
    print(f"   Recorded {len(actions)} actions.")
    
    # Save actions
    filename = "example_actions.json"
    recorder.save_to_file(filename)
    print(f"   Actions saved to {filename}")
    
    # Show recorded actions
    print("\n2. Recorded actions:")
    for i, action in enumerate(actions):
        print(f"   {i+1}: {action.button} click at ({action.x}, {action.y}) at {action.timestamp:.2f}s")
    
    # Preview before playing
    print("\n3. Previewing actions...")
    player.preview_actions(actions)
    
    # Play back actions
    print("\n4. Playing back actions in 3 seconds...")
    print("   Move your mouse to a corner to trigger failsafe if needed.")
    
    for i in range(3, 0, -1):
        print(f"   Playing in {i}...")
        time.sleep(1)
    
    print("   Playing actions... (Press ESC to stop)")
    player.set_speed_multiplier(0.5)  # Play at half speed
    player.play_actions(actions)
    
    # Wait for playback to finish
    while player.is_busy():
        time.sleep(0.1)
    
    print("\n5. Playback completed!")
    print("\nExample finished. You can now:")
    print("   - Load the saved actions in the GUI")
    print("   - Try different transformations")
    print("   - Experiment with different playback settings")


if __name__ == "__main__":
    main()