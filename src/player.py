"""
Action Player
Replays recorded mouse actions with customizable settings.
"""

import time
import random
import threading
from typing import List, Optional, Callable
try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from pynput import keyboard
except ImportError:
    keyboard = None

from src.recorder import MouseAction


class ActionPlayer:
    """Plays back recorded mouse actions."""
    
    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        self.stop_requested = False
        self.play_thread: Optional[threading.Thread] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.progress_callback: Optional[Callable[[int, int], None]] = None
        
        # Playback settings
        self.speed_multiplier = 1.0
        self.random_delay_range = (0.0, 0.0)  # (min, max) in seconds
        self.loop_count = 1
        self.safe_mode = True
        
        # Configure PyAutoGUI if available
        if pyautogui:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.01
    
    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """Set callback function for progress updates."""
        self.progress_callback = callback
    
    def set_speed_multiplier(self, multiplier: float) -> None:
        """Set speed multiplier for playback (1.0 = normal speed)."""
        self.speed_multiplier = max(0.1, multiplier)
    
    def set_random_delay(self, min_delay: float, max_delay: float) -> None:
        """Set random delay range between actions."""
        self.random_delay_range = (max(0.0, min_delay), max(min_delay, max_delay))
    
    def set_loop_count(self, count: int) -> None:
        """Set number of times to loop the actions (-1 for infinite)."""
        self.loop_count = max(-1, count)
    
    def set_safe_mode(self, enabled: bool) -> None:
        """Enable/disable safe mode (ESC key to stop)."""
        self.safe_mode = enabled
    
    def play_actions(self, actions: List[MouseAction]) -> None:
        """Start playing back actions."""
        if self.is_playing:
            print("Already playing actions.")
            return
        
        if not actions:
            print("No actions to play.")
            return
        
        self.is_playing = True
        self.is_paused = False
        self.stop_requested = False
        
        # Start keyboard listener for safe mode
        if self.safe_mode and keyboard:
            self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
            self.keyboard_listener.start()
        
        # Start playback thread
        self.play_thread = threading.Thread(target=self._play_actions_thread, args=(actions,))
        self.play_thread.start()
        
        print(f"Started playing {len(actions)} actions. Press ESC to stop.")
    
    def stop_playback(self) -> None:
        """Stop the current playback."""
        if not self.is_playing:
            return
        
        self.stop_requested = True
        self.is_playing = False
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        print("Playback stopped.")
    
    def pause_playback(self) -> None:
        """Pause the current playback."""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            print("Playback paused.")
    
    def resume_playback(self) -> None:
        """Resume the paused playback."""
        if self.is_playing and self.is_paused:
            self.is_paused = False
            print("Playback resumed.")
    
    def _on_key_press(self, key) -> None:
        """Handle keyboard events for safe mode."""
        if not keyboard:
            return
            
        try:
            if key == keyboard.Key.esc:
                self.stop_playback()
            elif key == keyboard.Key.space:
                if self.is_paused:
                    self.resume_playback()
                else:
                    self.pause_playback()
        except AttributeError:
            pass
    
    def _play_actions_thread(self, actions: List[MouseAction]) -> None:
        """Thread function for playing back actions."""
        try:
            loop_counter = 0
            total_actions = len(actions)
            
            while (self.loop_count == -1 or loop_counter < self.loop_count) and not self.stop_requested:
                loop_counter += 1
                print(f"Starting loop {loop_counter}")
                
                for i, action in enumerate(actions):
                    if self.stop_requested:
                        break
                    
                    # Handle pause
                    while self.is_paused and not self.stop_requested:
                        time.sleep(0.1)
                    
                    if self.stop_requested:
                        break
                    
                    # Calculate delay
                    delay = 0
                    if i > 0:
                        time_diff = action.timestamp - actions[i-1].timestamp
                        delay = time_diff / self.speed_multiplier
                        
                        # Add random delay if configured
                        if self.random_delay_range[1] > 0:
                            random_delay = random.uniform(self.random_delay_range[0], 
                                                        self.random_delay_range[1])
                            delay += random_delay
                    
                    # Wait for the calculated delay
                    if delay > 0:
                        time.sleep(delay)
                    
                    # Perform the action
                    self._perform_action(action)
                    
                    # Update progress
                    if self.progress_callback:
                        current_total = (loop_counter - 1) * total_actions + i + 1
                        max_total = total_actions * (self.loop_count if self.loop_count > 0 else 1)
                        self.progress_callback(current_total, max_total)
                
                if self.stop_requested:
                    break
            
            print("Playback completed.")
            
        except Exception as e:
            print(f"Error during playback: {e}")
        finally:
            self.is_playing = False
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
    
    def _perform_action(self, action: MouseAction) -> None:
        """Perform a single mouse action."""
        if not pyautogui:
            print(f"Mock: {action.button} click at ({action.x}, {action.y})")
            return
            
        try:
            # Check screen bounds for safety
            screen_width, screen_height = pyautogui.size()
            if action.x < 0 or action.x >= screen_width or action.y < 0 or action.y >= screen_height:
                print(f"Warning: Action at ({action.x}, {action.y}) is outside screen bounds")
                return
            
            # Perform the click
            if action.button == "left":
                pyautogui.click(action.x, action.y, button='left')
            elif action.button == "right":
                pyautogui.click(action.x, action.y, button='right')
            elif action.button == "middle":
                pyautogui.click(action.x, action.y, button='middle')
            else:
                print(f"Unknown button type: {action.button}")
                return
            
            print(f"Performed {action.button} click at ({action.x}, {action.y})")
            
        except Exception as e:
            if "FailSafeException" in str(e):
                print("PyAutoGUI FailSafe triggered - mouse moved to corner")
                self.stop_playback()
            else:
                print(f"Error performing action: {e}")
    
    def get_estimated_duration(self, actions: List[MouseAction]) -> float:
        """Get estimated duration for playing back actions."""
        if not actions:
            return 0.0
        
        total_time = actions[-1].timestamp / self.speed_multiplier
        
        # Add random delay estimates
        if self.random_delay_range[1] > 0:
            avg_random_delay = (self.random_delay_range[0] + self.random_delay_range[1]) / 2
            total_time += avg_random_delay * len(actions)
        
        return total_time * (self.loop_count if self.loop_count > 0 else 1)
    
    def preview_actions(self, actions: List[MouseAction], duration: float = 2.0) -> None:
        """Preview actions by highlighting positions without clicking."""
        if not actions:
            print("No actions to preview.")
            return
        
        print(f"Previewing {len(actions)} actions for {duration} seconds...")
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            # Create preview window
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            # Show preview coordinates
            coords_text = "\n".join([f"{i+1}: ({action.x}, {action.y}) - {action.button}" 
                                   for i, action in enumerate(actions[:10])])
            if len(actions) > 10:
                coords_text += f"\n... and {len(actions) - 10} more actions"
            
            messagebox.showinfo("Action Preview", 
                              f"Actions to be performed:\n\n{coords_text}\n\n"
                              f"Total actions: {len(actions)}\n"
                              f"Estimated duration: {self.get_estimated_duration(actions):.1f}s")
            
            root.destroy()
            
        except ImportError:
            # Fallback to console output
            print("Action preview:")
            for i, action in enumerate(actions[:10]):
                print(f"  {i+1}: ({action.x}, {action.y}) - {action.button}")
            if len(actions) > 10:
                print(f"  ... and {len(actions) - 10} more actions")
            print(f"Total actions: {len(actions)}")
            print(f"Estimated duration: {self.get_estimated_duration(actions):.1f}s")
    
    def is_busy(self) -> bool:
        """Check if player is currently playing actions."""
        return self.is_playing