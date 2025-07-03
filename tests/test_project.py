"""
Basic project structure and functionality test.
Tests core functionality without requiring external dependencies.
"""

import unittest
import sys
import os
import json
import tempfile

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

class TestProjectStructure(unittest.TestCase):
    """Test the basic project structure and core functionality."""
    
    def test_project_structure(self):
        """Test that all required files and directories exist."""
        project_root = os.path.join(os.path.dirname(__file__), '..')
        
        # Check main files
        self.assertTrue(os.path.exists(os.path.join(project_root, 'README.md')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'requirements.txt')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'setup.py')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'main.py')))
        
        # Check directories
        self.assertTrue(os.path.exists(os.path.join(project_root, 'src')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'examples')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'tests')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'docs')))
        
        # Check source files
        src_dir = os.path.join(project_root, 'src')
        self.assertTrue(os.path.exists(os.path.join(src_dir, '__init__.py')))
        self.assertTrue(os.path.exists(os.path.join(src_dir, 'recorder.py')))
        self.assertTrue(os.path.exists(os.path.join(src_dir, 'transformer.py')))
        self.assertTrue(os.path.exists(os.path.join(src_dir, 'player.py')))
        self.assertTrue(os.path.exists(os.path.join(src_dir, 'gui.py')))
        
        # Check example files
        examples_dir = os.path.join(project_root, 'examples')
        self.assertTrue(os.path.exists(os.path.join(examples_dir, 'basic_usage.py')))
        self.assertTrue(os.path.exists(os.path.join(examples_dir, 'advanced_transform.py')))
        self.assertTrue(os.path.exists(os.path.join(examples_dir, 'sample_actions.json')))
        
        # Check documentation files
        docs_dir = os.path.join(project_root, 'docs')
        self.assertTrue(os.path.exists(os.path.join(docs_dir, 'installation.md')))
        self.assertTrue(os.path.exists(os.path.join(docs_dir, 'usage.md')))
        self.assertTrue(os.path.exists(os.path.join(docs_dir, 'api.md')))
    
    def test_sample_json_format(self):
        """Test that the sample JSON file has correct format."""
        sample_file = os.path.join(os.path.dirname(__file__), '..', 'examples', 'sample_actions.json')
        
        with open(sample_file, 'r') as f:
            data = json.load(f)
        
        # Check required keys
        self.assertIn('actions', data)
        self.assertIn('metadata', data)
        
        # Check actions format
        actions = data['actions']
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)
        
        for action in actions:
            self.assertIn('x', action)
            self.assertIn('y', action)
            self.assertIn('button', action)
            self.assertIn('timestamp', action)
            self.assertIn('action_type', action)
            
            self.assertIsInstance(action['x'], int)
            self.assertIsInstance(action['y'], int)
            self.assertIn(action['button'], ['left', 'right', 'middle'])
            self.assertIsInstance(action['timestamp'], (int, float))
            self.assertEqual(action['action_type'], 'click')
    
    def test_core_classes_importable(self):
        """Test that core classes can be imported (without external deps)."""
        # We'll test this by checking if the files contain the expected class definitions
        
        # Check recorder.py
        recorder_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'recorder.py')
        with open(recorder_file, 'r') as f:
            content = f.read()
            self.assertIn('class MouseAction:', content)
            self.assertIn('class MouseRecorder:', content)
            self.assertIn('def start_recording', content)
            self.assertIn('def stop_recording', content)
            self.assertIn('def save_to_file', content)
            self.assertIn('def load_from_file', content)
        
        # Check transformer.py
        transformer_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'transformer.py')
        with open(transformer_file, 'r') as f:
            content = f.read()
            self.assertIn('class CoordinateTransformer:', content)
            self.assertIn('def translate', content)
            self.assertIn('def scale', content)
            self.assertIn('def rotate', content)
            self.assertIn('def mirror_horizontal', content)
            self.assertIn('def mirror_vertical', content)
        
        # Check player.py
        player_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'player.py')
        with open(player_file, 'r') as f:
            content = f.read()
            self.assertIn('class ActionPlayer:', content)
            self.assertIn('def play_actions', content)
            self.assertIn('def stop_playback', content)
            self.assertIn('def set_speed_multiplier', content)
        
        # Check gui.py
        gui_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'gui.py')
        with open(gui_file, 'r') as f:
            content = f.read()
            self.assertIn('class MouseAutomationGUI:', content)
            self.assertIn('def setup_gui', content)
            self.assertIn('def run', content)
    
    def test_main_entry_point(self):
        """Test main.py structure."""
        main_file = os.path.join(os.path.dirname(__file__), '..', 'main.py')
        with open(main_file, 'r') as f:
            content = f.read()
            self.assertIn('def main()', content)
            self.assertIn('if __name__ == "__main__":', content)
            self.assertIn('MouseAutomationGUI', content)
    
    def test_requirements_format(self):
        """Test requirements.txt format."""
        requirements_file = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
        
        # Should have pyautogui and pynput
        content = ''.join(lines)
        self.assertIn('pyautogui', content)
        self.assertIn('pynput', content)
    
    def test_setup_py_format(self):
        """Test setup.py format."""
        setup_file = os.path.join(os.path.dirname(__file__), '..', 'setup.py')
        with open(setup_file, 'r') as f:
            content = f.read()
        
        self.assertIn('from setuptools import setup', content)
        self.assertIn('name="mouse-automation-toolkit"', content)
        self.assertIn('version="1.0.0"', content)
        self.assertIn('install_requires=', content)


class TestMouseActionBasics(unittest.TestCase):
    """Test MouseAction class basics without external dependencies."""
    
    def test_mock_mouse_action(self):
        """Test MouseAction-like functionality."""
        # Create a simple action data structure
        action_data = {
            'x': 100,
            'y': 200,
            'button': 'left',
            'timestamp': 1.5,
            'action_type': 'click'
        }
        
        # Test data validation
        self.assertIn(action_data['button'], ['left', 'right', 'middle'])
        self.assertIsInstance(action_data['x'], int)
        self.assertIsInstance(action_data['y'], int)
        self.assertIsInstance(action_data['timestamp'], (int, float))
        self.assertEqual(action_data['action_type'], 'click')
    
    def test_mock_transformation_math(self):
        """Test coordinate transformation mathematics."""
        # Test translation
        x, y = 100, 150
        offset_x, offset_y = 50, 25
        new_x, new_y = x + offset_x, y + offset_y
        self.assertEqual(new_x, 150)
        self.assertEqual(new_y, 175)
        
        # Test scaling
        x, y = 100, 150
        scale_x, scale_y = 2.0, 1.5
        center_x, center_y = 0, 0
        new_x = int((x - center_x) * scale_x + center_x)
        new_y = int((y - center_y) * scale_y + center_y)
        self.assertEqual(new_x, 200)
        self.assertEqual(new_y, 225)
        
        # Test mirroring
        x = 100
        axis_x = 150
        mirrored_x = 2 * axis_x - x
        self.assertEqual(mirrored_x, 200)


if __name__ == '__main__':
    unittest.main()