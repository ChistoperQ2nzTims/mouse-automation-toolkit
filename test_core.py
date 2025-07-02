#!/usr/bin/env python3
"""
Test script to validate core functionality without external dependencies.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Mock external dependencies
class MockPyAutoGUI:
    FAILSAFE = True
    PAUSE = 0.1
    
    @staticmethod
    def size():
        return (1920, 1080)
    
    @staticmethod
    def moveTo(x, y):
        print(f"MOCK: moveTo({x}, {y})")
    
    @staticmethod
    def mouseDown(x, y, button='left'):
        print(f"MOCK: mouseDown({x}, {y}, {button})")
    
    @staticmethod
    def mouseUp(x, y, button='left'):
        print(f"MOCK: mouseUp({x}, {y}, {button})")
    
    @staticmethod
    def scroll(amount, x=None, y=None):
        print(f"MOCK: scroll({amount}, x={x}, y={y})")
    
    class FailSafeException(Exception):
        pass

class MockPynput:
    class mouse:
        class Button:
            left = 'left'
            right = 'right'
            middle = 'middle'
            
            def __init__(self, name):
                self.name = name
        
        class Listener:
            def __init__(self, on_click=None, on_move=None, on_scroll=None):
                self.on_click = on_click
                self.on_move = on_move
                self.on_scroll = on_scroll
            
            def start(self):
                print("MOCK: Mouse listener started")
            
            def stop(self):
                print("MOCK: Mouse listener stopped")
    
    class keyboard:
        class Listener:
            def __init__(self, on_press=None):
                self.on_press = on_press
            
            def start(self):
                print("MOCK: Keyboard listener started")
            
            def stop(self):
                print("MOCK: Keyboard listener stopped")

class MockNumpy:
    ndarray = object  # Mock type hint
    
    @staticmethod
    def array(data):
        return MockArray(data)

class MockArray:
    def __init__(self, data):
        self.data = data
        self.shape = (len(data), len(data[0]) if data else 0)
    
    def __matmul__(self, other):
        # Simple mock matrix multiplication
        if hasattr(other, '__iter__') and len(other) == 3:
            return [100, 200, 1]  # Mock result
        return self

# Install mocks
sys.modules['pyautogui'] = MockPyAutoGUI()
sys.modules['pynput'] = MockPynput()
sys.modules['numpy'] = MockNumpy()

# Now test the core modules
def test_recorder():
    """Test the recorder module."""
    print("\n=== Testing Recorder Module ===")
    try:
        from recorder import MouseRecorder, MouseAction
        
        # Test MouseAction creation
        action = MouseAction(0.0, 'click', 100, 200, 'left', True)
        print(f"✓ MouseAction created: {action.action_type} at ({action.x}, {action.y})")
        
        # Test recorder initialization
        recorder = MouseRecorder()
        print("✓ MouseRecorder initialized")
        
        # Test stats with sample data
        recorder.actions = [
            MouseAction(0.0, 'click', 100, 100, 'left', True),
            MouseAction(0.1, 'click', 100, 100, 'left', False),
            MouseAction(0.5, 'move', 200, 200),
        ]
        
        stats = recorder.get_recording_stats()
        print(f"✓ Recording stats: {stats}")
        
        # Test save/load
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        recorder.save_to_file(temp_file, recorder.actions)
        loaded = recorder.load_from_file(temp_file)
        print(f"✓ Save/Load test: saved {len(recorder.actions)}, loaded {len(loaded)}")
        
        os.unlink(temp_file)
        recorder.cleanup()
        
        return True
        
    except Exception as e:
        print(f"✗ Recorder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_transformer():
    """Test the transformer module."""
    print("\n=== Testing Transformer Module ===")
    try:
        from transformer import CoordinateTransformer
        from recorder import MouseAction
        
        transformer = CoordinateTransformer()
        print("✓ CoordinateTransformer initialized")
        
        # Create test actions
        actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.5, 'click', 200, 200, 'left', True),
            MouseAction(0.6, 'click', 200, 200, 'left', False)
        ]
        
        # Test translation
        translated = transformer.translate(actions, 50, 25)
        print(f"✓ Translation: ({actions[0].x}, {actions[0].y}) -> ({translated[0].x}, {translated[0].y})")
        
        # Test scaling
        scaled = transformer.scale(actions, 1.5, 1.5)
        print(f"✓ Scaling: ({actions[0].x}, {actions[0].y}) -> ({scaled[0].x}, {scaled[0].y})")
        
        # Test rotation
        rotated = transformer.rotate(actions, 45)
        print(f"✓ Rotation: ({actions[0].x}, {actions[0].y}) -> ({rotated[0].x}, {rotated[0].y})")
        
        # Test mirroring
        mirrored = transformer.mirror_horizontal(actions)
        print(f"✓ Mirroring: ({actions[0].x}, {actions[0].y}) -> ({mirrored[0].x}, {mirrored[0].y})")
        
        # Test bounds calculation
        bounds = transformer._get_action_bounds(actions)
        print(f"✓ Bounds calculation: {bounds}")
        
        # Test chained transformations
        transforms = [
            {'type': 'translate', 'offset_x': 10, 'offset_y': 20},
            {'type': 'scale', 'scale_x': 1.2, 'scale_y': 1.2}
        ]
        chained = transformer.chain_transforms(actions, transforms)
        print(f"✓ Chained transformations: {len(chained)} actions processed")
        
        return True
        
    except Exception as e:
        print(f"✗ Transformer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_player():
    """Test the player module."""
    print("\n=== Testing Player Module ===")
    try:
        from player import ActionPlayer
        from recorder import MouseAction
        
        player = ActionPlayer()
        print("✓ ActionPlayer initialized")
        
        # Create test actions
        actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.5, 'click', 100, 100, 'left', True),
            MouseAction(0.6, 'click', 100, 100, 'left', False)
        ]
        
        # Test validation
        validation = player.validate_actions(actions)
        print(f"✓ Action validation: valid={validation['valid']}, warnings={len(validation.get('warnings', []))}")
        
        # Test progress tracking
        player.total_actions = 10
        player.current_action_index = 3
        progress = player.get_playback_progress()
        print(f"✓ Progress tracking: {progress['progress_percent']}%")
        
        # Test create click action
        click_actions = player.create_click_action(150, 250, 'right')
        print(f"✓ Create click action: {len(click_actions)} actions created")
        
        # Test create drag action
        drag_actions = player.create_drag_action(100, 100, 300, 200, 2.0)
        print(f"✓ Create drag action: {len(drag_actions)} actions created")
        
        player.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ Player test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between modules."""
    print("\n=== Testing Integration ===")
    try:
        from recorder import MouseRecorder, MouseAction
        from transformer import CoordinateTransformer
        from player import ActionPlayer
        
        # Create sample workflow
        recorder = MouseRecorder()
        transformer = CoordinateTransformer()
        player = ActionPlayer()
        
        # Create actions
        actions = [
            MouseAction(0.0, 'move', 100, 100),
            MouseAction(0.5, 'click', 100, 100, 'left', True),
            MouseAction(0.6, 'click', 100, 100, 'left', False),
            MouseAction(1.0, 'move', 200, 200),
            MouseAction(1.5, 'click', 200, 200, 'right', True),
            MouseAction(1.6, 'click', 200, 200, 'right', False)
        ]
        
        # Save to file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        recorder.save_to_file(temp_file, actions)
        
        # Load and transform
        loaded = recorder.load_from_file(temp_file)
        transformed = transformer.translate(loaded, 50, 25)
        scaled = transformer.scale(transformed, 1.5, 1.5)
        
        # Validate for playback
        validation = player.validate_actions(scaled)
        
        print(f"✓ Full workflow: {len(actions)} -> {len(loaded)} -> {len(transformed)} -> {len(scaled)}")
        print(f"✓ Final validation: {validation['valid']}")
        
        # Clean up
        os.unlink(temp_file)
        recorder.cleanup()
        player.cleanup()
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_examples():
    """Test that examples can be imported."""
    print("\n=== Testing Examples ===")
    try:
        # Test basic example structure
        example_file = Path(__file__).parent / 'examples' / 'sample_actions.json'
        if example_file.exists():
            with open(example_file, 'r') as f:
                data = json.load(f)
                print(f"✓ Sample actions file: {data['metadata']['action_count']} actions")
        
        return True
        
    except Exception as e:
        print(f"✗ Examples test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Mouse Automation Toolkit - Core Functionality Test")
    print("=" * 50)
    
    tests = [
        test_recorder,
        test_transformer,
        test_player,
        test_integration,
        test_examples
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "PASS" if result else "FAIL"
        print(f"  {test.__name__}: {status}")
    
    passed = sum(results)
    total = len(results)
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core functionality tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed - see details above")
        return 1

if __name__ == "__main__":
    exit(main())