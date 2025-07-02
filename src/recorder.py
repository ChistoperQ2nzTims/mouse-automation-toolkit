"""
Mouse Action Recorder Module

This module provides functionality to record mouse actions including clicks, coordinates,
and timing information using the pynput library.
"""

import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pynput import mouse
from pynput.mouse import Button


class MouseRecorder:
    """
    Records mouse actions with precise timing and coordinates
    """
    
    def __init__(self):
        self.actions: List[Dict[str, Any]] = []
        self.is_recording = False
        self.listener: Optional[mouse.Listener] = None
        self.start_time: Optional[float] = None
        self.last_click_time = 0
        self.debounce_threshold = 0.1  # 100ms debounce
        self.on_action_callback: Optional[Callable] = None
        self.lock = threading.Lock()
    
    def set_action_callback(self, callback: Callable):
        """Set callback function to be called when an action is recorded"""
        self.on_action_callback = callback
    
    def start_recording(self) -> bool:
        """
        Start recording mouse actions
        
        Returns:
            bool: True if recording started successfully, False otherwise
        """
        if self.is_recording:
            return False
            
        try:
            self.actions.clear()
            self.is_recording = True
            self.start_time = time.time()
            self.last_click_time = 0
            
            # Start mouse listener
            self.listener = mouse.Listener(
                on_click=self._on_click,
                on_move=self._on_move
            )
            self.listener.start()
            
            return True
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
            return False
    
    def stop_recording(self) -> bool:
        """
        Stop recording mouse actions
        
        Returns:
            bool: True if recording stopped successfully, False otherwise
        """
        if not self.is_recording:
            return False
            
        try:
            self.is_recording = False
            if self.listener:
                self.listener.stop()
                self.listener = None
            return True
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False
    
    def _on_click(self, x: int, y: int, button: Button, pressed: bool):
        """Handle mouse click events"""
        if not self.is_recording or not pressed:
            return
            
        current_time = time.time()
        
        # Debounce rapid clicks
        if current_time - self.last_click_time < self.debounce_threshold:
            return
        
        self.last_click_time = current_time
        
        # Record the action
        action = {
            'type': 'click',
            'x': x,
            'y': y,
            'button': button.name,
            'timestamp': current_time - self.start_time,
            'absolute_time': datetime.now().isoformat()
        }
        
        with self.lock:
            self.actions.append(action)
        
        # Call callback if set
        if self.on_action_callback:
            try:
                self.on_action_callback(action)
            except Exception as e:
                print(f"Error in action callback: {e}")
    
    def _on_move(self, x: int, y: int):
        """Handle mouse move events (currently not recorded to avoid spam)"""
        pass
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """
        Get all recorded actions
        
        Returns:
            List[Dict]: List of recorded actions
        """
        with self.lock:
            return self.actions.copy()
    
    def clear_actions(self):
        """Clear all recorded actions"""
        with self.lock:
            self.actions.clear()
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save recorded actions to a JSON file
        
        Args:
            filename (str): Path to the output file
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            data = {
                'metadata': {
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'total_actions': len(self.actions),
                    'duration': self.actions[-1]['timestamp'] if self.actions else 0
                },
                'actions': self.actions
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
    
    def load_from_file(self, filename: str) -> bool:
        """
        Load actions from a JSON file
        
        Args:
            filename (str): Path to the input file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'actions' in data:
                with self.lock:
                    self.actions = data['actions']
            else:
                # Legacy format - assume the file is just an array of actions
                with self.lock:
                    self.actions = data
            
            return True
        except Exception as e:
            print(f"Error loading from file: {e}")
            return False
    
    def filter_duplicate_clicks(self, threshold: float = 1.0) -> int:
        """
        Filter out clicks that are too close in time and space
        
        Args:
            threshold (float): Time threshold in seconds
            
        Returns:
            int: Number of actions removed
        """
        if len(self.actions) <= 1:
            return 0
        
        filtered_actions = []
        removed_count = 0
        
        with self.lock:
            for i, action in enumerate(self.actions):
                if i == 0:
                    filtered_actions.append(action)
                    continue
                
                prev_action = filtered_actions[-1]
                time_diff = action['timestamp'] - prev_action['timestamp']
                
                if (action['type'] == 'click' and prev_action['type'] == 'click' and
                    time_diff < threshold and
                    action['x'] == prev_action['x'] and
                    action['y'] == prev_action['y'] and
                    action['button'] == prev_action['button']):
                    removed_count += 1
                else:
                    filtered_actions.append(action)
            
            self.actions = filtered_actions
        
        return removed_count
    
    def get_recording_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current recording
        
        Returns:
            Dict: Recording statistics
        """
        with self.lock:
            if not self.actions:
                return {
                    'total_actions': 0,
                    'duration': 0,
                    'clicks_per_second': 0,
                    'button_distribution': {}
                }
            
            total_actions = len(self.actions)
            duration = self.actions[-1]['timestamp'] if self.actions else 0
            clicks_per_second = total_actions / duration if duration > 0 else 0
            
            button_dist = {}
            for action in self.actions:
                button = action.get('button', 'unknown')
                button_dist[button] = button_dist.get(button, 0) + 1
            
            return {
                'total_actions': total_actions,
                'duration': duration,
                'clicks_per_second': clicks_per_second,
                'button_distribution': button_dist
            }