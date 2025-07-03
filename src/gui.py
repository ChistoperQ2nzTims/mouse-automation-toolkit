"""
GUI Interface
Provides a user-friendly interface for the mouse automation toolkit.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
import os
from typing import Optional
from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer


class MouseAutomationGUI:
    """Main GUI application for mouse automation toolkit."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mouse Automation Toolkit 🐭🤖")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Core components
        self.recorder = MouseRecorder()
        self.transformer = CoordinateTransformer()
        self.player = ActionPlayer()
        
        # GUI state
        self.current_filename = ""
        self.is_recording = False
        self.is_playing = False
        
        # Setup progress callback
        self.player.set_progress_callback(self.update_progress)
        
        self.setup_gui()
        self.update_status()
    
    def setup_gui(self):
        """Setup the GUI layout and components."""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_record_tab()
        self.create_transform_tab()
        self.create_play_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, 
                                          maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_record_tab(self):
        """Create the recording tab."""
        self.record_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.record_frame, text="📹 Record")
        
        # Recording controls
        controls_frame = ttk.LabelFrame(self.record_frame, text="Recording Controls")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(pady=10)
        
        self.record_button = ttk.Button(button_frame, text="Start Recording", 
                                       command=self.toggle_recording, width=15)
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Actions", 
                                      command=self.clear_actions, width=15)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_dupes_button = ttk.Button(button_frame, text="Remove Duplicates", 
                                             command=self.remove_duplicates, width=15)
        self.remove_dupes_button.pack(side=tk.LEFT, padx=5)
        
        # File operations
        file_frame = ttk.LabelFrame(self.record_frame, text="File Operations")
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        file_button_frame = ttk.Frame(file_frame)
        file_button_frame.pack(pady=10)
        
        ttk.Button(file_button_frame, text="Save", command=self.save_actions, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_button_frame, text="Load", command=self.load_actions, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_button_frame, text="Save As", command=self.save_as_actions, 
                  width=10).pack(side=tk.LEFT, padx=5)
        
        # Current file label
        self.file_label = ttk.Label(file_frame, text="No file loaded")
        self.file_label.pack(pady=5)
        
        # Actions display
        actions_frame = ttk.LabelFrame(self.record_frame, text="Recorded Actions")
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for actions
        columns = ("Index", "X", "Y", "Button", "Time")
        self.actions_tree = ttk.Treeview(actions_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.actions_tree.heading(col, text=col)
            self.actions_tree.column(col, width=100)
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(actions_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        h_scrollbar = ttk.Scrollbar(actions_frame, orient=tk.HORIZONTAL, command=self.actions_tree.xview)
        self.actions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.actions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_transform_tab(self):
        """Create the transformation tab."""
        self.transform_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transform_frame, text="🔄 Transform")
        
        # Transformation controls
        transform_controls = ttk.LabelFrame(self.transform_frame, text="Transformations")
        transform_controls.pack(fill=tk.X, padx=10, pady=5)
        
        # Translation
        translate_frame = ttk.Frame(transform_controls)
        translate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(translate_frame, text="Translate:").pack(side=tk.LEFT)
        ttk.Label(translate_frame, text="X:").pack(side=tk.LEFT, padx=(10, 0))
        self.translate_x = tk.IntVar(value=0)
        ttk.Entry(translate_frame, textvariable=self.translate_x, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(translate_frame, text="Y:").pack(side=tk.LEFT)
        self.translate_y = tk.IntVar(value=0)
        ttk.Entry(translate_frame, textvariable=self.translate_y, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(translate_frame, text="Apply", 
                  command=self.apply_translation).pack(side=tk.LEFT, padx=(10, 0))
        
        # Scaling
        scale_frame = ttk.Frame(transform_controls)
        scale_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(scale_frame, text="Scale:").pack(side=tk.LEFT)
        ttk.Label(scale_frame, text="X:").pack(side=tk.LEFT, padx=(10, 0))
        self.scale_x = tk.DoubleVar(value=1.0)
        ttk.Entry(scale_frame, textvariable=self.scale_x, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(scale_frame, text="Y:").pack(side=tk.LEFT)
        self.scale_y = tk.DoubleVar(value=1.0)
        ttk.Entry(scale_frame, textvariable=self.scale_y, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(scale_frame, text="Apply", 
                  command=self.apply_scaling).pack(side=tk.LEFT, padx=(10, 0))
        
        # Rotation
        rotate_frame = ttk.Frame(transform_controls)
        rotate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rotate_frame, text="Rotate:").pack(side=tk.LEFT)
        ttk.Label(rotate_frame, text="Angle:").pack(side=tk.LEFT, padx=(10, 0))
        self.rotate_angle = tk.DoubleVar(value=0.0)
        ttk.Entry(rotate_frame, textvariable=self.rotate_angle, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(rotate_frame, text="°").pack(side=tk.LEFT)
        
        ttk.Button(rotate_frame, text="Apply", 
                  command=self.apply_rotation).pack(side=tk.LEFT, padx=(10, 0))
        
        # Mirror
        mirror_frame = ttk.Frame(transform_controls)
        mirror_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mirror_frame, text="Mirror:").pack(side=tk.LEFT)
        ttk.Button(mirror_frame, text="Horizontal", 
                  command=self.apply_mirror_horizontal).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(mirror_frame, text="Vertical", 
                  command=self.apply_mirror_vertical).pack(side=tk.LEFT, padx=5)
        
        # Fit to screen
        fit_frame = ttk.Frame(transform_controls)
        fit_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(fit_frame, text="Fit to Screen", 
                  command=self.apply_fit_to_screen).pack(side=tk.LEFT)
        
        # Preview
        preview_frame = ttk.LabelFrame(self.transform_frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=15, width=60)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_play_tab(self):
        """Create the playback tab."""
        self.play_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.play_frame, text="▶️ Play")
        
        # Playback controls
        play_controls = ttk.LabelFrame(self.play_frame, text="Playback Controls")
        play_controls.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = ttk.Frame(play_controls)
        button_frame.pack(pady=10)
        
        self.play_button = ttk.Button(button_frame, text="Play", 
                                     command=self.start_playback, width=10)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", 
                                      command=self.pause_playback, width=10)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_playback, width=10)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.preview_button = ttk.Button(button_frame, text="Preview", 
                                        command=self.preview_actions, width=10)
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        # Playback settings
        settings_frame = ttk.LabelFrame(self.play_frame, text="Playback Settings")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Speed
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=200)
        speed_scale.pack(side=tk.LEFT, padx=10)
        self.speed_label = ttk.Label(speed_frame, text="1.0x")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        speed_scale.configure(command=self.update_speed_label)
        
        # Loop count
        loop_frame = ttk.Frame(settings_frame)
        loop_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(loop_frame, text="Loop count:").pack(side=tk.LEFT)
        self.loop_var = tk.IntVar(value=1)
        ttk.Entry(loop_frame, textvariable=self.loop_var, width=8).pack(side=tk.LEFT, padx=10)
        ttk.Label(loop_frame, text="(-1 for infinite)").pack(side=tk.LEFT)
        
        # Random delay
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(delay_frame, text="Random delay:").pack(side=tk.LEFT)
        ttk.Label(delay_frame, text="Min:").pack(side=tk.LEFT, padx=(10, 0))
        self.delay_min = tk.DoubleVar(value=0.0)
        ttk.Entry(delay_frame, textvariable=self.delay_min, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(delay_frame, text="Max:").pack(side=tk.LEFT)
        self.delay_max = tk.DoubleVar(value=0.0)
        ttk.Entry(delay_frame, textvariable=self.delay_max, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(delay_frame, text="seconds").pack(side=tk.LEFT)
        
        # Log
        log_frame = ttk.LabelFrame(self.play_frame, text="Playback Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=60)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_settings_tab(self):
        """Create the settings tab."""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        
        # General settings
        general_frame = ttk.LabelFrame(self.settings_frame, text="General Settings")
        general_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.safe_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(general_frame, text="Safe Mode (ESC to stop)", 
                       variable=self.safe_mode_var).pack(anchor=tk.W, padx=10, pady=5)
        
        # About
        about_frame = ttk.LabelFrame(self.settings_frame, text="About")
        about_frame.pack(fill=tk.X, padx=10, pady=5)
        
        about_text = ("Mouse Automation Toolkit v1.0.0\n\n"
                     "A complete toolkit for recording, transforming, and replaying mouse actions.\n\n"
                     "Features:\n"
                     "• Record mouse clicks with timing\n"
                     "• Transform coordinates (translate, scale, rotate, mirror)\n"
                     "• Replay with customizable settings\n"
                     "• Safe mode with ESC key to stop\n\n"
                     "Press ESC during playback to stop\n"
                     "Press SPACE during playback to pause/resume")
        
        ttk.Label(about_frame, text=about_text, justify=tk.LEFT).pack(padx=10, pady=10)
    
    def toggle_recording(self):
        """Toggle recording state."""
        if not self.is_recording:
            self.recorder.start_recording()
            self.is_recording = True
            self.record_button.config(text="Stop Recording")
            self.log_message("Recording started...")
        else:
            self.recorder.stop_recording()
            self.is_recording = False
            self.record_button.config(text="Start Recording")
            self.log_message("Recording stopped.")
            self.update_actions_display()
    
    def clear_actions(self):
        """Clear all recorded actions."""
        if messagebox.askyesno("Clear Actions", "Are you sure you want to clear all actions?"):
            self.recorder.clear_actions()
            self.update_actions_display()
            self.log_message("Actions cleared.")
    
    def remove_duplicates(self):
        """Remove duplicate actions."""
        removed = self.recorder.remove_duplicate_actions()
        self.update_actions_display()
        self.log_message(f"Removed {removed} duplicate actions.")
    
    def save_actions(self):
        """Save actions to current file."""
        if not self.current_filename:
            self.save_as_actions()
        else:
            self.recorder.save_to_file(self.current_filename)
            self.log_message(f"Actions saved to {self.current_filename}")
    
    def save_as_actions(self):
        """Save actions to a new file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.recorder.save_to_file(filename)
            self.current_filename = filename
            self.file_label.config(text=f"File: {os.path.basename(filename)}")
            self.log_message(f"Actions saved to {filename}")
    
    def load_actions(self):
        """Load actions from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.recorder.load_from_file(filename)
            self.current_filename = filename
            self.file_label.config(text=f"File: {os.path.basename(filename)}")
            self.update_actions_display()
            self.log_message(f"Actions loaded from {filename}")
    
    def update_actions_display(self):
        """Update the actions treeview."""
        # Clear existing items
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
        
        # Add current actions
        actions = self.recorder.get_actions()
        for i, action in enumerate(actions):
            self.actions_tree.insert("", tk.END, values=(
                i + 1,
                action.x,
                action.y,
                action.button,
                f"{action.timestamp:.2f}s"
            ))
        
        # Update preview
        self.update_preview()
    
    def update_preview(self):
        """Update the transformation preview."""
        actions = self.recorder.get_actions()
        if not actions:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "No actions to preview.")
            return
        
        # Get bounding box info
        min_x, min_y, max_x, max_y = self.transformer.get_bounding_box(actions)
        center_x, center_y = self.transformer.get_center_point(actions)
        
        preview_text = f"Current Actions Summary:\n"
        preview_text += f"Total actions: {len(actions)}\n"
        preview_text += f"Bounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})\n"
        preview_text += f"Center point: ({center_x}, {center_y})\n"
        preview_text += f"Duration: {actions[-1].timestamp:.2f} seconds\n\n"
        
        preview_text += "Actions:\n"
        for i, action in enumerate(actions[:20]):  # Show first 20 actions
            preview_text += f"{i+1:3d}: ({action.x:4d}, {action.y:4d}) {action.button:6s} at {action.timestamp:6.2f}s\n"
        
        if len(actions) > 20:
            preview_text += f"... and {len(actions) - 20} more actions\n"
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, preview_text)
    
    def apply_translation(self):
        """Apply translation transformation."""
        actions = self.recorder.get_actions()
        if not actions:
            messagebox.showwarning("No Actions", "No actions to transform.")
            return
        
        offset_x = self.translate_x.get()
        offset_y = self.translate_y.get()
        
        transformed = self.transformer.translate(actions, offset_x, offset_y)
        self.recorder.actions = transformed
        self.update_actions_display()
        self.log_message(f"Applied translation: ({offset_x}, {offset_y})")
    
    def apply_scaling(self):
        """Apply scaling transformation."""
        actions = self.recorder.get_actions()
        if not actions:
            messagebox.showwarning("No Actions", "No actions to transform.")
            return
        
        scale_x = self.scale_x.get()
        scale_y = self.scale_y.get()
        center_x, center_y = self.transformer.get_center_point(actions)
        
        transformed = self.transformer.scale(actions, scale_x, scale_y, center_x, center_y)
        self.recorder.actions = transformed
        self.update_actions_display()
        self.log_message(f"Applied scaling: ({scale_x}, {scale_y}) around center ({center_x}, {center_y})")
    
    def apply_rotation(self):
        """Apply rotation transformation."""
        actions = self.recorder.get_actions()
        if not actions:
            messagebox.showwarning("No Actions", "No actions to transform.")
            return
        
        angle = self.rotate_angle.get()
        center_x, center_y = self.transformer.get_center_point(actions)
        
        transformed = self.transformer.rotate(actions, angle, center_x, center_y)
        self.recorder.actions = transformed
        self.update_actions_display()
        self.log_message(f"Applied rotation: {angle}° around center ({center_x}, {center_y})")
    
    def apply_mirror_horizontal(self):
        """Apply horizontal mirroring."""
        actions = self.recorder.get_actions()
        if not actions:
            messagebox.showwarning("No Actions", "No actions to transform.")
            return
        
        center_x, _ = self.transformer.get_center_point(actions)
        transformed = self.transformer.mirror_horizontal(actions, center_x)
        self.recorder.actions = transformed
        self.update_actions_display()
        self.log_message(f"Applied horizontal mirror around x={center_x}")
    
    def apply_mirror_vertical(self):
        """Apply vertical mirroring."""
        actions = self.recorder.get_actions()
        if not actions:
            messagebox.showwarning("No Actions", "No actions to transform.")
            return
        
        _, center_y = self.transformer.get_center_point(actions)
        transformed = self.transformer.mirror_vertical(actions, center_y)
        self.recorder.actions = transformed
        self.update_actions_display()
        self.log_message(f"Applied vertical mirror around y={center_y}")
    
    def apply_fit_to_screen(self):
        """Apply fit to screen transformation."""
        actions = self.recorder.get_actions()
        if not actions:
            messagebox.showwarning("No Actions", "No actions to transform.")
            return
        
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        
        transformed = self.transformer.fit_to_screen(actions, screen_width, screen_height)
        self.recorder.actions = transformed
        self.update_actions_display()
        self.log_message(f"Fitted actions to screen ({screen_width}x{screen_height})")
    
    def start_playback(self):
        """Start action playback."""
        actions = self.recorder.get_actions()
        if not actions:
            messagebox.showwarning("No Actions", "No actions to play.")
            return
        
        if self.is_playing:
            messagebox.showwarning("Already Playing", "Playback is already in progress.")
            return
        
        # Apply settings
        self.player.set_speed_multiplier(self.speed_var.get())
        self.player.set_loop_count(self.loop_var.get())
        self.player.set_random_delay(self.delay_min.get(), self.delay_max.get())
        self.player.set_safe_mode(self.safe_mode_var.get())
        
        # Start playback
        self.is_playing = True
        self.player.play_actions(actions)
        self.log_message("Playback started. Press ESC to stop.")
        
        # Update UI
        self.play_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start monitoring thread
        threading.Thread(target=self.monitor_playback, daemon=True).start()
    
    def pause_playback(self):
        """Pause/resume playback."""
        if self.player.is_paused:
            self.player.resume_playback()
            self.pause_button.config(text="Pause")
            self.log_message("Playback resumed.")
        else:
            self.player.pause_playback()
            self.pause_button.config(text="Resume")
            self.log_message("Playback paused.")
    
    def stop_playback(self):
        """Stop playback."""
        self.player.stop_playback()
        self.is_playing = False
        self.play_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(text="Pause")
        self.progress_var.set(0)
        self.log_message("Playback stopped.")
    
    def preview_actions(self):
        """Preview actions without playing."""
        actions = self.recorder.get_actions()
        if not actions:
            messagebox.showwarning("No Actions", "No actions to preview.")
            return
        
        self.player.preview_actions(actions)
    
    def monitor_playback(self):
        """Monitor playback status in separate thread."""
        while self.is_playing and self.player.is_busy():
            time.sleep(0.1)
        
        if self.is_playing:  # Playback finished naturally
            self.root.after(0, self.stop_playback)
    
    def update_progress(self, current: int, total: int):
        """Update progress bar."""
        if total > 0:
            progress = (current / total) * 100
            self.root.after(0, lambda: self.progress_var.set(progress))
    
    def update_speed_label(self, value):
        """Update speed label."""
        speed = float(value)
        self.speed_label.config(text=f"{speed:.1f}x")
    
    def log_message(self, message: str):
        """Add message to log."""
        import time
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def update_status(self):
        """Update status bar."""
        actions_count = len(self.recorder.get_actions())
        status = f"Actions: {actions_count}"
        
        if self.is_recording:
            status += " | Recording..."
        elif self.is_playing:
            status += " | Playing..."
        else:
            status += " | Ready"
        
        self.status_label.config(text=status)
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def run(self):
        """Start the GUI application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_playback()
            if self.is_recording:
                self.recorder.stop_recording()


def main():
    """Main entry point for GUI application."""
    app = MouseAutomationGUI()
    app.run()


if __name__ == "__main__":
    main()