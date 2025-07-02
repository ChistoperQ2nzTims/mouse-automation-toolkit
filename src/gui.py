#!/usr/bin/env python3
"""
GUI Module

Provides a Tkinter-based graphical interface for the mouse automation toolkit.
Includes recording, transformation, and playback controls with real-time feedback.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
import time
import os
from typing import List, Optional, Dict, Any
import logging

from .recorder import MouseRecorder, MouseAction
from .transformer import CoordinateTransformer
from .player import ActionPlayer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogHandler(logging.Handler):
    """Custom log handler to display logs in the GUI."""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self._append_log, msg)
    
    def _append_log(self, msg):
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)


class MouseAutomationGUI:
    """
    Main GUI application for the Mouse Automation Toolkit.
    
    Features:
    - Recording controls with hotkey support
    - Transformation tools with real-time preview
    - Playback controls with safety features
    - Action list with editing capabilities
    - Profile management for saving/loading
    - Real-time log display
    - Settings panel
    """
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Mouse Automation Toolkit 🐭🤖")
        self.root.geometry("1000x700")
        
        # Initialize core components
        self.recorder = MouseRecorder()
        self.transformer = CoordinateTransformer()
        self.player = ActionPlayer()
        
        # Current actions and state
        self.current_actions: List[MouseAction] = []
        self.is_recording = False
        self.is_playing = False
        self.current_profile_file = None
        
        # Setup callbacks
        self.recorder.on_recording_start = self._on_recording_start
        self.recorder.on_recording_stop = self._on_recording_stop
        self.player.on_playback_start = self._on_playback_start
        self.player.on_playback_stop = self._on_playback_stop
        self.player.on_progress_update = self._on_progress_update
        
        # Create GUI
        self._create_widgets()
        self._setup_logging()
        
        # Start hotkey listener
        self.recorder.start_hotkey_listener()
        
        logger.info("Mouse Automation Toolkit GUI started")
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_recording_tab()
        self._create_transformation_tab()
        self._create_playback_tab()
        self._create_actions_tab()
        self._create_settings_tab()
        
        # Status bar
        self._create_status_bar()
    
    def _create_recording_tab(self):
        """Create the recording control tab."""
        recording_frame = ttk.Frame(self.notebook)
        self.notebook.add(recording_frame, text="Recording")
        
        # Recording controls
        controls_frame = ttk.LabelFrame(recording_frame, text="Recording Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.record_btn = ttk.Button(buttons_frame, text="Start Recording (F9)", 
                                   command=self._start_recording, state=tk.NORMAL)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_record_btn = ttk.Button(buttons_frame, text="Stop Recording (F10)", 
                                        command=self._stop_recording, state=tk.DISABLED)
        self.stop_record_btn.pack(side=tk.LEFT, padx=5)
        
        # Recording settings
        settings_frame = ttk.LabelFrame(recording_frame, text="Recording Settings")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Duration setting
        duration_frame = ttk.Frame(settings_frame)
        duration_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(duration_frame, text="Duration (seconds):").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="")
        duration_entry = ttk.Entry(duration_frame, textvariable=self.duration_var, width=10)
        duration_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(duration_frame, text="(empty = manual stop)").pack(side=tk.LEFT)
        
        # Remove duplicates setting
        self.remove_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Remove duplicate actions", 
                       variable=self.remove_duplicates_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Recording stats
        stats_frame = ttk.LabelFrame(recording_frame, text="Recording Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=10, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_transformation_tab(self):
        """Create the transformation control tab."""
        transform_frame = ttk.Frame(self.notebook)
        self.notebook.add(transform_frame, text="Transformation")
        
        # Basic transformations
        basic_frame = ttk.LabelFrame(transform_frame, text="Basic Transformations")
        basic_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Translation
        translate_frame = ttk.Frame(basic_frame)
        translate_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(translate_frame, text="Translate:").pack(side=tk.LEFT)
        ttk.Label(translate_frame, text="X:").pack(side=tk.LEFT, padx=(10, 0))
        self.translate_x_var = tk.StringVar(value="0")
        ttk.Entry(translate_frame, textvariable=self.translate_x_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(translate_frame, text="Y:").pack(side=tk.LEFT, padx=(5, 0))
        self.translate_y_var = tk.StringVar(value="0")
        ttk.Entry(translate_frame, textvariable=self.translate_y_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(translate_frame, text="Apply", command=self._apply_translation).pack(side=tk.LEFT, padx=5)
        
        # Scaling
        scale_frame = ttk.Frame(basic_frame)
        scale_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(scale_frame, text="Scale:").pack(side=tk.LEFT)
        ttk.Label(scale_frame, text="X:").pack(side=tk.LEFT, padx=(10, 0))
        self.scale_x_var = tk.StringVar(value="1.0")
        ttk.Entry(scale_frame, textvariable=self.scale_x_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(scale_frame, text="Y:").pack(side=tk.LEFT, padx=(5, 0))
        self.scale_y_var = tk.StringVar(value="1.0")
        ttk.Entry(scale_frame, textvariable=self.scale_y_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(scale_frame, text="Apply", command=self._apply_scaling).pack(side=tk.LEFT, padx=5)
        
        # Rotation
        rotate_frame = ttk.Frame(basic_frame)
        rotate_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(rotate_frame, text="Rotate:").pack(side=tk.LEFT)
        self.rotate_angle_var = tk.StringVar(value="0")
        ttk.Entry(rotate_frame, textvariable=self.rotate_angle_var, width=8).pack(side=tk.LEFT, padx=(10, 2))
        ttk.Label(rotate_frame, text="degrees").pack(side=tk.LEFT)
        ttk.Button(rotate_frame, text="Apply", command=self._apply_rotation).pack(side=tk.LEFT, padx=5)
        
        # Mirror operations
        mirror_frame = ttk.Frame(basic_frame)
        mirror_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(mirror_frame, text="Mirror:").pack(side=tk.LEFT)
        ttk.Button(mirror_frame, text="Horizontal", command=self._apply_mirror_horizontal).pack(side=tk.LEFT, padx=(10, 2))
        ttk.Button(mirror_frame, text="Vertical", command=self._apply_mirror_vertical).pack(side=tk.LEFT, padx=2)
        
        # Advanced transformations
        advanced_frame = ttk.LabelFrame(transform_frame, text="Advanced Transformations")
        advanced_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Fit to screen
        fit_frame = ttk.Frame(advanced_frame)
        fit_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(fit_frame, text="Fit to Screen", command=self._fit_to_screen).pack(side=tk.LEFT)
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(fit_frame, text="Maintain aspect ratio", 
                       variable=self.maintain_aspect_var).pack(side=tk.LEFT, padx=10)
        
        # Transformation preview
        preview_frame = ttk.LabelFrame(transform_frame, text="Transformation Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.transform_preview_text = scrolledtext.ScrolledText(preview_frame, height=8, state=tk.DISABLED)
        self.transform_preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_playback_tab(self):
        """Create the playback control tab."""
        playback_frame = ttk.Frame(self.notebook)
        self.notebook.add(playback_frame, text="Playback")
        
        # Playback controls
        controls_frame = ttk.LabelFrame(playback_frame, text="Playback Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.play_btn = ttk.Button(buttons_frame, text="Start Playback", 
                                 command=self._start_playback, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_play_btn = ttk.Button(buttons_frame, text="Stop Playback (ESC)", 
                                      command=self._stop_playback, state=tk.DISABLED)
        self.stop_play_btn.pack(side=tk.LEFT, padx=5)
        
        self.validate_btn = ttk.Button(buttons_frame, text="Validate Actions", 
                                     command=self._validate_actions)
        self.validate_btn.pack(side=tk.LEFT, padx=5)
        
        # Playback settings
        settings_frame = ttk.LabelFrame(playback_frame, text="Playback Settings")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Speed and delay
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="1.0")
        ttk.Entry(speed_frame, textvariable=self.speed_var, width=8).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(speed_frame, text="x").pack(side=tk.LEFT)
        
        ttk.Label(speed_frame, text="Extra delay:").pack(side=tk.LEFT, padx=(20, 0))
        self.delay_var = tk.StringVar(value="0.0")
        ttk.Entry(speed_frame, textvariable=self.delay_var, width=8).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(speed_frame, text="sec").pack(side=tk.LEFT)
        
        # Loop settings
        loop_frame = ttk.Frame(settings_frame)
        loop_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(loop_frame, text="Loop count:").pack(side=tk.LEFT)
        self.loop_var = tk.StringVar(value="1")
        ttk.Entry(loop_frame, textvariable=self.loop_var, width=8).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(loop_frame, text="(0 = infinite)").pack(side=tk.LEFT)
        
        # Start delay
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(delay_frame, text="Start delay:").pack(side=tk.LEFT)
        self.start_delay_var = tk.StringVar(value="3.0")
        ttk.Entry(delay_frame, textvariable=self.start_delay_var, width=8).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(delay_frame, text="sec").pack(side=tk.LEFT)
        
        # Progress bar
        progress_frame = ttk.LabelFrame(playback_frame, text="Playback Progress")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(padx=5, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.pack(pady=2)
        
        # Validation results
        validation_frame = ttk.LabelFrame(playback_frame, text="Validation Results")
        validation_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.validation_text = scrolledtext.ScrolledText(validation_frame, height=8, state=tk.DISABLED)
        self.validation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_actions_tab(self):
        """Create the actions management tab."""
        actions_frame = ttk.Frame(self.notebook)
        self.notebook.add(actions_frame, text="Actions")
        
        # File operations
        file_frame = ttk.LabelFrame(actions_frame, text="File Operations")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        file_buttons_frame = ttk.Frame(file_frame)
        file_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_buttons_frame, text="Load Actions", command=self._load_actions).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_buttons_frame, text="Save Actions", command=self._save_actions).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_buttons_frame, text="Clear Actions", command=self._clear_actions).pack(side=tk.LEFT, padx=2)
        
        # Current file label
        self.current_file_label = ttk.Label(file_frame, text="No file loaded")
        self.current_file_label.pack(pady=2)
        
        # Actions list
        list_frame = ttk.LabelFrame(actions_frame, text="Current Actions")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for actions
        columns = ('Index', 'Time', 'Type', 'X', 'Y', 'Button', 'Details')
        self.actions_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.actions_tree.heading(col, text=col)
            self.actions_tree.column(col, width=80 if col != 'Details' else 150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        self.actions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.actions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _create_settings_tab(self):
        """Create the settings and configuration tab."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Hotkey settings
        hotkey_frame = ttk.LabelFrame(settings_frame, text="Hotkey Settings")
        hotkey_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start recording hotkey
        start_frame = ttk.Frame(hotkey_frame)
        start_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(start_frame, text="Start Recording:").pack(side=tk.LEFT)
        self.start_hotkey_var = tk.StringVar(value="<f9>")
        ttk.Entry(start_frame, textvariable=self.start_hotkey_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Stop recording hotkey
        stop_frame = ttk.Frame(hotkey_frame)
        stop_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(stop_frame, text="Stop Recording:").pack(side=tk.LEFT)
        self.stop_hotkey_var = tk.StringVar(value="<f10>")
        ttk.Entry(stop_frame, textvariable=self.stop_hotkey_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Emergency stop hotkey
        emergency_frame = ttk.Frame(hotkey_frame)
        emergency_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(emergency_frame, text="Emergency Stop:").pack(side=tk.LEFT)
        self.emergency_hotkey_var = tk.StringVar(value="esc")
        ttk.Entry(emergency_frame, textvariable=self.emergency_hotkey_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Safety settings
        safety_frame = ttk.LabelFrame(settings_frame, text="Safety Settings")
        safety_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.failsafe_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, text="Enable PyAutoGUI failsafe (mouse to corner stops)", 
                       variable=self.failsafe_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Default pause
        pause_frame = ttk.Frame(safety_frame)
        pause_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(pause_frame, text="Default pause between actions:").pack(side=tk.LEFT)
        self.default_pause_var = tk.StringVar(value="0.1")
        ttk.Entry(pause_frame, textvariable=self.default_pause_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(pause_frame, text="seconds").pack(side=tk.LEFT)
        
        # Apply settings button
        ttk.Button(safety_frame, text="Apply Settings", command=self._apply_settings).pack(pady=10)
        
        # Log display
        log_frame = ttk.LabelFrame(settings_frame, text="Application Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Action count label
        self.action_count_label = ttk.Label(self.status_frame, text="Actions: 0")
        self.action_count_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def _setup_logging(self):
        """Setup logging to display in the GUI."""
        log_handler = LogHandler(self.log_text)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(log_handler)
    
    # Recording methods
    def _start_recording(self):
        """Start recording mouse actions."""
        try:
            duration_str = self.duration_var.get().strip()
            duration = float(duration_str) if duration_str else None
            
            self.recorder.remove_duplicates = self.remove_duplicates_var.get()
            
            if duration:
                # Timed recording
                threading.Thread(target=self._timed_recording, args=(duration,), daemon=True).start()
            else:
                # Manual recording
                self.recorder.start_recording()
                
        except ValueError:
            messagebox.showerror("Error", "Invalid duration value")
    
    def _timed_recording(self, duration):
        """Perform timed recording in a separate thread."""
        actions = self.recorder.record(duration)
        self.current_actions = actions
        self._update_actions_display()
    
    def _stop_recording(self):
        """Stop recording mouse actions."""
        actions = self.recorder.stop_recording()
        self.current_actions = actions
        self._update_actions_display()
    
    def _on_recording_start(self):
        """Callback when recording starts."""
        self.is_recording = True
        self.record_btn.config(state=tk.DISABLED)
        self.stop_record_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Recording...")
        self._update_recording_stats()
    
    def _on_recording_stop(self):
        """Callback when recording stops."""
        self.is_recording = False
        self.record_btn.config(state=tk.NORMAL)
        self.stop_record_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Recording completed")
        self._update_recording_stats()
        self.play_btn.config(state=tk.NORMAL if self.current_actions else tk.DISABLED)
    
    def _update_recording_stats(self):
        """Update recording statistics display."""
        if self.is_recording:
            # Update stats during recording
            stats = self.recorder.get_recording_stats()
            stats_text = f"Recording in progress...\n"
            stats_text += f"Actions recorded: {stats.get('action_count', 0)}\n"
            stats_text += f"Duration: {stats.get('duration', 0):.1f} seconds\n"
            stats_text += f"Clicks: {stats.get('click_count', 0)}\n"
            stats_text += f"Moves: {stats.get('move_count', 0)}\n"
            stats_text += f"Scrolls: {stats.get('scroll_count', 0)}\n"
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            self.stats_text.config(state=tk.DISABLED)
            
            # Schedule next update
            self.root.after(500, self._update_recording_stats)
    
    # Transformation methods
    def _apply_translation(self):
        """Apply translation transformation."""
        try:
            offset_x = float(self.translate_x_var.get())
            offset_y = float(self.translate_y_var.get())
            
            if self.current_actions:
                self.current_actions = self.transformer.translate(self.current_actions, offset_x, offset_y)
                self._update_actions_display()
                self._update_transform_preview()
        except ValueError:
            messagebox.showerror("Error", "Invalid translation values")
    
    def _apply_scaling(self):
        """Apply scaling transformation."""
        try:
            scale_x = float(self.scale_x_var.get())
            scale_y = float(self.scale_y_var.get())
            
            if self.current_actions:
                self.current_actions = self.transformer.scale(self.current_actions, scale_x, scale_y)
                self._update_actions_display()
                self._update_transform_preview()
        except ValueError:
            messagebox.showerror("Error", "Invalid scaling values")
    
    def _apply_rotation(self):
        """Apply rotation transformation."""
        try:
            angle = float(self.rotate_angle_var.get())
            
            if self.current_actions:
                self.current_actions = self.transformer.rotate(self.current_actions, angle)
                self._update_actions_display()
                self._update_transform_preview()
        except ValueError:
            messagebox.showerror("Error", "Invalid rotation angle")
    
    def _apply_mirror_horizontal(self):
        """Apply horizontal mirror transformation."""
        if self.current_actions:
            self.current_actions = self.transformer.mirror_horizontal(self.current_actions)
            self._update_actions_display()
            self._update_transform_preview()
    
    def _apply_mirror_vertical(self):
        """Apply vertical mirror transformation."""
        if self.current_actions:
            self.current_actions = self.transformer.mirror_vertical(self.current_actions)
            self._update_actions_display()
            self._update_transform_preview()
    
    def _fit_to_screen(self):
        """Fit actions to current screen size."""
        if self.current_actions:
            try:
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                maintain_aspect = self.maintain_aspect_var.get()
                
                self.current_actions = self.transformer.fit_to_screen(
                    self.current_actions, screen_width, screen_height, maintain_aspect
                )
                self._update_actions_display()
                self._update_transform_preview()
                
                messagebox.showinfo("Success", f"Actions fitted to screen {screen_width}x{screen_height}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fit to screen: {e}")
    
    def _update_transform_preview(self):
        """Update transformation preview."""
        if not self.current_actions:
            return
        
        bounds = self.transformer._get_action_bounds(self.current_actions)
        
        preview_text = f"Action Bounds:\n"
        preview_text += f"X range: {bounds['min_x']:.0f} to {bounds['max_x']:.0f}\n"
        preview_text += f"Y range: {bounds['min_y']:.0f} to {bounds['max_y']:.0f}\n"
        preview_text += f"Width: {bounds['max_x'] - bounds['min_x']:.0f}\n"
        preview_text += f"Height: {bounds['max_y'] - bounds['min_y']:.0f}\n"
        
        if len(self.current_actions) > 1:
            duration = self.current_actions[-1].timestamp - self.current_actions[0].timestamp
            preview_text += f"Duration: {duration:.2f} seconds\n"
        
        self.transform_preview_text.config(state=tk.NORMAL)
        self.transform_preview_text.delete(1.0, tk.END)
        self.transform_preview_text.insert(1.0, preview_text)
        self.transform_preview_text.config(state=tk.DISABLED)
    
    # Playback methods
    def _start_playback(self):
        """Start playing back actions."""
        if not self.current_actions:
            messagebox.showwarning("Warning", "No actions to play")
            return
        
        try:
            speed = float(self.speed_var.get())
            delay = float(self.delay_var.get())
            loop_count = int(self.loop_var.get())
            start_delay = float(self.start_delay_var.get())
            
            # Start playback in separate thread
            threading.Thread(
                target=self._playback_worker,
                args=(speed, delay, loop_count, start_delay),
                daemon=True
            ).start()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid playback settings")
    
    def _playback_worker(self, speed, delay, loop_count, start_delay):
        """Worker method for playback in separate thread."""
        success = self.player.replay(
            self.current_actions,
            delay=delay,
            speed_multiplier=speed,
            loop_count=loop_count,
            start_delay=start_delay
        )
        
        # Update UI in main thread
        self.root.after(0, self._on_playback_complete, success)
    
    def _stop_playback(self):
        """Stop current playback."""
        self.player.stop_playback()
    
    def _validate_actions(self):
        """Validate current actions and display results."""
        if not self.current_actions:
            messagebox.showwarning("Warning", "No actions to validate")
            return
        
        validation = self.player.validate_actions(self.current_actions)
        
        validation_text = f"Validation Results:\n\n"
        validation_text += f"Valid: {'Yes' if validation['valid'] else 'No'}\n"
        validation_text += f"Action count: {validation.get('action_count', 0)}\n"
        validation_text += f"Estimated duration: {validation.get('estimated_duration', 0):.2f} seconds\n\n"
        
        if validation.get('errors'):
            validation_text += "ERRORS:\n"
            for error in validation['errors']:
                validation_text += f"- {error}\n"
            validation_text += "\n"
        
        if validation.get('warnings'):
            validation_text += "WARNINGS:\n"
            for warning in validation['warnings']:
                validation_text += f"- {warning}\n"
        
        self.validation_text.config(state=tk.NORMAL)
        self.validation_text.delete(1.0, tk.END)
        self.validation_text.insert(1.0, validation_text)
        self.validation_text.config(state=tk.DISABLED)
    
    def _on_playback_start(self):
        """Callback when playback starts."""
        self.is_playing = True
        self.play_btn.config(state=tk.DISABLED)
        self.stop_play_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Playing back actions...")
        self.progress_var.set(0)
        self.progress_label.config(text="Starting playback...")
    
    def _on_playback_stop(self):
        """Callback when playback stops."""
        self.is_playing = False
        self.play_btn.config(state=tk.NORMAL)
        self.stop_play_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Playback stopped")
        self.progress_label.config(text="Playback stopped")
    
    def _on_playback_complete(self, success):
        """Callback when playback completes."""
        self.is_playing = False
        self.play_btn.config(state=tk.NORMAL)
        self.stop_play_btn.config(state=tk.DISABLED)
        self.progress_var.set(100 if success else 0)
        
        if success:
            self.status_label.config(text="Playback completed successfully")
            self.progress_label.config(text="Completed")
        else:
            self.status_label.config(text="Playback was stopped")
            self.progress_label.config(text="Stopped")
    
    def _on_progress_update(self, progress):
        """Callback for playback progress updates."""
        self.progress_var.set(progress * 100)
        self.progress_label.config(text=f"Progress: {progress * 100:.1f}%")
    
    # File operations
    def _load_actions(self):
        """Load actions from a file."""
        filename = filedialog.askopenfilename(
            title="Load Actions",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.current_actions = self.recorder.load_from_file(filename)
                self.current_profile_file = filename
                self.current_file_label.config(text=f"File: {os.path.basename(filename)}")
                self._update_actions_display()
                messagebox.showinfo("Success", f"Loaded {len(self.current_actions)} actions")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def _save_actions(self):
        """Save current actions to a file."""
        if not self.current_actions:
            messagebox.showwarning("Warning", "No actions to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Actions",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.recorder.save_to_file(filename, self.current_actions)
                self.current_profile_file = filename
                self.current_file_label.config(text=f"File: {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Saved {len(self.current_actions)} actions")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def _clear_actions(self):
        """Clear all current actions."""
        if self.current_actions:
            result = messagebox.askyesno("Confirm", "Clear all actions?")
            if result:
                self.current_actions.clear()
                self.current_profile_file = None
                self.current_file_label.config(text="No file loaded")
                self._update_actions_display()
    
    def _update_actions_display(self):
        """Update the actions display in the treeview."""
        # Clear existing items
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
        
        # Add current actions
        for i, action in enumerate(self.current_actions):
            details = ""
            if action.action_type == 'click':
                details = f"{'Press' if action.pressed else 'Release'}"
            elif action.action_type == 'scroll':
                details = f"{action.scroll_direction} ({action.scroll_amount})"
            
            self.actions_tree.insert('', 'end', values=(
                i,
                f"{action.timestamp:.2f}",
                action.action_type,
                action.x,
                action.y,
                action.button or "",
                details
            ))
        
        # Update action count
        self.action_count_label.config(text=f"Actions: {len(self.current_actions)}")
        
        # Update button states
        has_actions = len(self.current_actions) > 0
        self.play_btn.config(state=tk.NORMAL if has_actions and not self.is_playing else tk.DISABLED)
        self.validate_btn.config(state=tk.NORMAL if has_actions else tk.DISABLED)
        
        # Update transformation preview
        self._update_transform_preview()
    
    # Settings methods
    def _apply_settings(self):
        """Apply current settings."""
        try:
            # Update recorder settings
            self.recorder.stop_hotkey_listener()
            self.recorder.start_hotkey = self.start_hotkey_var.get()
            self.recorder.stop_hotkey = self.stop_hotkey_var.get()
            self.recorder.start_hotkey_listener()
            
            # Update player settings
            self.player.emergency_stop_key = self.emergency_hotkey_var.get().replace('<', '').replace('>', '')
            self.player.failsafe_enabled = self.failsafe_var.get()
            self.player.default_pause = float(self.default_pause_var.get())
            
            # Update PyAutoGUI settings
            import pyautogui
            pyautogui.FAILSAFE = self.failsafe_var.get()
            pyautogui.PAUSE = float(self.default_pause_var.get())
            
            messagebox.showinfo("Success", "Settings applied successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
    
    def cleanup(self):
        """Clean up resources when closing."""
        logger.info("Cleaning up GUI resources...")
        
        if self.is_recording:
            self.recorder.stop_recording()
        
        if self.is_playing:
            self.player.stop_playback()
        
        self.recorder.cleanup()
        self.player.cleanup()


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = MouseAutomationGUI(root)
    
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()


if __name__ == "__main__":
    main()