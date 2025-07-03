#!/usr/bin/env python3
"""
Standalone verification script for Mouse Automation Toolkit.
Tests core functionality without requiring GUI dependencies.
"""

import sys
import os
import json
import tempfile
import math

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock the external dependencies that might not be available
class MockMouse:
    class Button:
        left = "left"
        right = "right"
        middle = "middle"

class MockPyAutoGUI:
    @staticmethod
    def size():
        return (1920, 1080)
    
    @staticmethod
    def click(x, y, button='left'):
        print(f"Mock click: {button} at ({x}, {y})")

class MockListener:
    def __init__(self, on_click=None):
        self.on_click = on_click
    
    def start(self):
        print("Mock listener started")
    
    def stop(self):
        print("Mock listener stopped")

# Patch modules before importing our code
sys.modules['pynput'] = type('MockPynput', (), {'mouse': MockMouse})()
sys.modules['pynput.mouse'] = MockMouse
sys.modules['pyautogui'] = MockPyAutoGUI

# Now import our modules
try:
    from recorder import MouseAction, MouseRecorder
    from transformer import CoordinateTransformer
    
    # Mock the player without pyautogui
    from player import ActionPlayer
    
    print("✅ Successfully imported core modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_mouse_action():
    """Test MouseAction functionality."""
    print("\n🧪 Testing MouseAction...")
    
    # Create action
    action = MouseAction(100, 200, "left", 1.5)
    assert action.x == 100
    assert action.y == 200
    assert action.button == "left"
    assert action.timestamp == 1.5
    assert action.action_type == "click"
    
    # Test serialization
    data = action.to_dict()
    expected = {
        "x": 100,
        "y": 200,
        "button": "left",
        "timestamp": 1.5,
        "action_type": "click"
    }
    assert data == expected
    
    # Test deserialization
    action2 = MouseAction.from_dict(data)
    assert action2.x == action.x
    assert action2.y == action.y
    assert action2.button == action.button
    
    print("✅ MouseAction tests passed")

def test_recorder():
    """Test MouseRecorder functionality."""
    print("\n🧪 Testing MouseRecorder...")
    
    recorder = MouseRecorder()
    
    # Test initial state
    assert not recorder.is_recording
    assert len(recorder.actions) == 0
    
    # Test adding actions manually
    action1 = MouseAction(100, 100, "left", 0.0)
    action2 = MouseAction(200, 200, "right", 1.0)
    recorder.actions = [action1, action2]
    
    actions = recorder.get_actions()
    assert len(actions) == 2
    assert actions[0].x == 100
    assert actions[1].button == "right"
    
    # Test file operations
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_filename = f.name
    
    try:
        recorder.save_to_file(temp_filename)
        assert os.path.exists(temp_filename)
        
        # Test loading
        new_recorder = MouseRecorder()
        new_recorder.load_from_file(temp_filename)
        loaded_actions = new_recorder.get_actions()
        
        assert len(loaded_actions) == 2
        assert loaded_actions[0].x == 100
        assert loaded_actions[1].button == "right"
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
    
    print("✅ MouseRecorder tests passed")

def test_transformer():
    """Test CoordinateTransformer functionality."""
    print("\n🧪 Testing CoordinateTransformer...")
    
    transformer = CoordinateTransformer()
    
    # Create test actions
    actions = [
        MouseAction(100, 100, "left", 0.0),
        MouseAction(200, 100, "left", 1.0),
        MouseAction(200, 200, "left", 2.0),
        MouseAction(100, 200, "left", 3.0),
    ]
    
    # Test translation
    translated = transformer.translate(actions, 50, 75)
    assert translated[0].x == 150  # 100 + 50
    assert translated[0].y == 175  # 100 + 75
    
    # Test scaling
    scaled = transformer.scale(actions, 2.0, 1.5, 150, 150)
    # First point (100, 100) relative to center (150, 150) is (-50, -50)
    # Scaled: (-100, -75), back to absolute: (50, 75)
    assert scaled[0].x == 50
    assert scaled[0].y == 75
    
    # Test bounding box
    min_x, min_y, max_x, max_y = transformer.get_bounding_box(actions)
    assert min_x == 100
    assert min_y == 100
    assert max_x == 200
    assert max_y == 200
    
    # Test center point
    center_x, center_y = transformer.get_center_point(actions)
    assert center_x == 150
    assert center_y == 150
    
    # Test rotation (90 degrees)
    rotated = transformer.rotate(actions, 90, 150, 150)
    # Point (100, 100) relative to (150, 150) is (-50, -50)
    # After 90-degree rotation clockwise: (50, -50)
    # Back to absolute: (200, 100)
    assert abs(rotated[0].x - 200) <= 1
    assert abs(rotated[0].y - 100) <= 1
    
    # Test mirroring
    mirrored_h = transformer.mirror_horizontal(actions, 150)
    assert mirrored_h[0].x == 200  # 2*150 - 100 = 200
    assert mirrored_h[0].y == 100  # y unchanged
    
    mirrored_v = transformer.mirror_vertical(actions, 150)
    assert mirrored_v[0].x == 100  # x unchanged
    assert mirrored_v[0].y == 200  # 2*150 - 100 = 200
    
    print("✅ CoordinateTransformer tests passed")

def test_player():
    """Test ActionPlayer functionality."""
    print("\n🧪 Testing ActionPlayer...")
    
    player = ActionPlayer()
    
    # Test initial state
    assert not player.is_playing
    assert not player.is_paused
    assert player.speed_multiplier == 1.0
    assert player.loop_count == 1
    
    # Test settings
    player.set_speed_multiplier(2.0)
    assert player.speed_multiplier == 2.0
    
    player.set_loop_count(3)
    assert player.loop_count == 3
    
    player.set_random_delay(0.1, 0.5)
    assert player.random_delay_range == (0.1, 0.5)
    
    # Test estimated duration
    actions = [
        MouseAction(100, 100, "left", 0.0),
        MouseAction(200, 200, "left", 2.0),
    ]
    
    # Reset to defaults first
    player.set_speed_multiplier(1.0)
    player.set_loop_count(3)
    player.set_random_delay(0.0, 0.0)  # Reset random delay
    
    duration = player.get_estimated_duration(actions)
    assert duration == 6.0  # 2.0 seconds * 3 loops
    
    print("✅ ActionPlayer tests passed")

def test_examples():
    """Test example files format."""
    print("\n🧪 Testing example files...")
    
    # Test sample_actions.json
    sample_file = os.path.join('examples', 'sample_actions.json')
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    assert 'actions' in data
    assert 'metadata' in data
    assert len(data['actions']) > 0
    
    for action in data['actions']:
        assert all(key in action for key in ['x', 'y', 'button', 'timestamp', 'action_type'])
        assert action['button'] in ['left', 'right', 'middle']
        assert action['action_type'] == 'click'
    
    print("✅ Example files tests passed")

def main():
    """Run all verification tests."""
    print("🐭🤖 Mouse Automation Toolkit - Verification Script")
    print("=" * 60)
    
    try:
        test_mouse_action()
        test_recorder()
        test_transformer()
        test_player()
        test_examples()
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! Mouse Automation Toolkit is ready to use.")
        print("\n📋 Project Summary:")
        print("• Complete mouse action recording system")
        print("• Advanced coordinate transformation engine")
        print("• Flexible action replay with timing control")
        print("• Cross-platform GUI interface (requires tkinter)")
        print("• Comprehensive test suite and documentation")
        print("\n🚀 To get started:")
        print("1. Install dependencies: pip install pyautogui pynput")
        print("2. Launch GUI: python main.py")
        print("3. Or run examples: python examples/basic_usage.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)