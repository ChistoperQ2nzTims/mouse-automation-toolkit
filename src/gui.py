"""
GUI Module for Mouse Automation Toolkit

This module provides a comprehensive Tkinter-based graphical user interface
for recording, transforming, and replaying mouse actions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import threading
import time
import os
from typing import Optional, Dict, Any, List

from .recorder import MouseRecorder
from .transformer import CoordinateTransformer
from .player import ActionPlayer


class MainGUI:
    """Main GUI application for Mouse Automation Toolkit"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mouse Automation Toolkit v1.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize core components
        self.recorder = MouseRecorder()
        self.transformer = CoordinateTransformer()
        self.player = ActionPlayer()
        
        # GUI state variables
        self.is_recording = tk.BooleanVar()
        self.is_playing = tk.BooleanVar()
        self.is_paused = tk.BooleanVar()
        self.loop_mode = tk.BooleanVar()
        self.safe_mode = tk.BooleanVar(value=True)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.action_count = tk.IntVar()
        self.progress_var = tk.DoubleVar()
        
        # File management
        self.current_file = None
        self.actions_list = []
        
        # Set up callbacks
        self.recorder.set_action_callback(self._on_action_recorded)
        self.player.set_progress_callback(self._on_playback_progress)
        self.player.set_complete_callback(self._on_playback_complete)
        
        # Create GUI
        self._setup_gui()
        self._update_status()
        
        # Start status update loop
        self._start_status_loop()
    
    def _setup_gui(self):
        """Set up the main GUI layout"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_record_tab()
        self._create_transform_tab()
        self._create_playback_tab()
        self._create_preview_tab()
        self._create_settings_tab()
        
        # Create status bar
        self._create_status_bar()
        
        # Create menu
        self._create_menu()
    
    def _create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Actions", command=self._clear_actions)
        edit_menu.add_command(label="Filter Duplicates", command=self._filter_duplicates)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self._new_file())
        self.root.bind('<Control-o>', lambda e: self._open_file())
        self.root.bind('<Control-s>', lambda e: self._save_file())
        self.root.bind('<Control-S>', lambda e: self._save_as_file())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
    
    def _create_record_tab(self):
        """Create the recording tab"""
        record_frame = ttk.Frame(self.notebook)
        self.notebook.add(record_frame, text="🔴 Record")
        
        # Main recording controls
        control_frame = ttk.LabelFrame(record_frame, text="Recording Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Record button
        self.record_btn = ttk.Button(control_frame, text="Start Recording", 
                                   command=self._toggle_recording, width=15)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        # Action counter
        counter_frame = ttk.Frame(control_frame)
        counter_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(counter_frame, text="Actions:").pack(side=tk.LEFT)
        ttk.Label(counter_frame, textvariable=self.action_count, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Recording status
        self.record_status = ttk.Label(control_frame, text="Ready to record", foreground="green")
        self.record_status.pack(side=tk.RIGHT, padx=5)
        
        # Recording options
        options_frame = ttk.LabelFrame(record_frame, text="Recording Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Debounce threshold
        debounce_frame = ttk.Frame(options_frame)
        debounce_frame.pack(anchor=tk.W, pady=2)
        ttk.Label(debounce_frame, text="Debounce (ms):").pack(side=tk.LEFT)
        self.debounce_var = tk.DoubleVar(value=100)
        debounce_spin = ttk.Spinbox(debounce_frame, from_=0, to=1000, increment=10, 
                                   textvariable=self.debounce_var, width=10)
        debounce_spin.pack(side=tk.LEFT, padx=5)
        
        # Live actions display
        actions_frame = ttk.LabelFrame(record_frame, text="Live Actions", padding=5)
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Actions tree
        columns = ("Time", "X", "Y", "Button")
        self.actions_tree = ttk.Treeview(actions_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.actions_tree.heading(col, text=col)
            self.actions_tree.column(col, width=100)
        
        # Scrollbars for actions tree
        v_scrollbar = ttk.Scrollbar(actions_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        h_scrollbar = ttk.Scrollbar(actions_frame, orient=tk.HORIZONTAL, command=self.actions_tree.xview)
        self.actions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.actions_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        actions_frame.grid_rowconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(0, weight=1)
    
    def _create_transform_tab(self):
        """Create the transformation tab"""
        transform_frame = ttk.Frame(self.notebook)
        self.notebook.add(transform_frame, text="🔄 Transform")
        
        # Left panel for transformations
        left_panel = ttk.Frame(transform_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Translation
        trans_frame = ttk.LabelFrame(left_panel, text="Translation", padding=10)
        trans_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(trans_frame, text="Offset X:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.trans_x_var = tk.DoubleVar()
        ttk.Entry(trans_frame, textvariable=self.trans_x_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(trans_frame, text="Offset Y:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.trans_y_var = tk.DoubleVar()
        ttk.Entry(trans_frame, textvariable=self.trans_y_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(trans_frame, text="Apply Translation", 
                  command=self._apply_translation).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Scaling
        scale_frame = ttk.LabelFrame(left_panel, text="Scaling", padding=10)
        scale_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(scale_frame, text="Scale X:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.scale_x_var = tk.DoubleVar(value=1.0)
        ttk.Entry(scale_frame, textvariable=self.scale_x_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(scale_frame, text="Scale Y:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.scale_y_var = tk.DoubleVar(value=1.0)
        ttk.Entry(scale_frame, textvariable=self.scale_y_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(scale_frame, text="Apply Scaling", 
                  command=self._apply_scaling).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Rotation
        rotate_frame = ttk.LabelFrame(left_panel, text="Rotation", padding=10)
        rotate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rotate_frame, text="Angle (°):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.rotate_var = tk.DoubleVar()
        ttk.Entry(rotate_frame, textvariable=self.rotate_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(rotate_frame, text="Apply Rotation", 
                  command=self._apply_rotation).grid(row=1, column=0, columnspan=2, pady=5)
        
        # Mirroring
        mirror_frame = ttk.LabelFrame(left_panel, text="Mirroring", padding=10)
        mirror_frame.pack(fill=tk.X, pady=5)
        
        self.mirror_var = tk.StringVar(value="horizontal")
        ttk.Radiobutton(mirror_frame, text="Horizontal", variable=self.mirror_var, 
                       value="horizontal").pack(anchor=tk.W)
        ttk.Radiobutton(mirror_frame, text="Vertical", variable=self.mirror_var, 
                       value="vertical").pack(anchor=tk.W)
        ttk.Radiobutton(mirror_frame, text="Both", variable=self.mirror_var, 
                       value="both").pack(anchor=tk.W)
        
        ttk.Button(mirror_frame, text="Apply Mirror", 
                  command=self._apply_mirror).pack(pady=5)
        
        # Right panel for preview and batch operations
        right_panel = ttk.Frame(transform_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Batch transformations
        batch_frame = ttk.LabelFrame(right_panel, text="Batch Operations", padding=10)
        batch_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(batch_frame, text="Fit to Screen", 
                  command=self._fit_to_screen).pack(side=tk.LEFT, padx=5)
        ttk.Button(batch_frame, text="Reset All", 
                  command=self._reset_transformations).pack(side=tk.LEFT, padx=5)
        
        # Transformation preview
        preview_frame = ttk.LabelFrame(right_panel, text="Transformation Preview", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.transform_preview = scrolledtext.ScrolledText(preview_frame, height=20, state=tk.DISABLED)
        self.transform_preview.pack(fill=tk.BOTH, expand=True)
    
    def _create_playback_tab(self):
        """Create the playback tab"""
        playback_frame = ttk.Frame(self.notebook)
        self.notebook.add(playback_frame, text="▶️ Playback")
        
        # Playback controls
        control_frame = ttk.LabelFrame(playback_frame, text="Playback Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Main control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT)
        
        self.play_btn = ttk.Button(btn_frame, text="▶ Play", command=self._toggle_playback, width=8)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = ttk.Button(btn_frame, text="⏸ Pause", command=self._pause_playback, width=8)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop", command=self._stop_playback, width=8)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Progress and status
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=20)
        
        self.play_status = ttk.Label(status_frame, text="Ready to play")
        self.play_status.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        # Playback options
        options_frame = ttk.LabelFrame(playback_frame, text="Playback Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Speed control
        speed_frame = ttk.Frame(options_frame)
        speed_frame.pack(anchor=tk.W, pady=2)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        speed_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=200)
        speed_scale.pack(side=tk.LEFT, padx=5)
        self.speed_label = ttk.Label(speed_frame, text="1.0x")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        speed_scale.configure(command=self._on_speed_change)
        
        # Options checkboxes
        options_checks = ttk.Frame(options_frame)
        options_checks.pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(options_checks, text="Loop mode", variable=self.loop_mode).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_checks, text="Safe mode", variable=self.safe_mode).pack(side=tk.LEFT, padx=10)
        
        # Validation and info
        info_frame = ttk.LabelFrame(playback_frame, text="Action Information", padding=5)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=15, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_preview_tab(self):
        """Create the preview tab"""
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="👁 Preview")
        
        # Preview controls
        control_frame = ttk.LabelFrame(preview_frame, text="Preview Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Refresh Preview", command=self._refresh_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Preview", command=self._export_preview).pack(side=tk.LEFT, padx=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(preview_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=4, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X)
        
        # Actions list
        list_frame = ttk.LabelFrame(preview_frame, text="Actions List", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create detailed actions tree
        columns = ("Index", "Time", "X", "Y", "Button", "Relative Time")
        self.preview_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=80)
        
        preview_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # General settings
        general_frame = ttk.LabelFrame(settings_frame, text="General Settings", padding=10)
        general_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Auto-save settings
        ttk.Checkbutton(general_frame, text="Auto-save recordings").pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(general_frame, text="Show notifications").pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(general_frame, text="Minimize to system tray").pack(anchor=tk.W, pady=2)
        
        # Hotkeys
        hotkeys_frame = ttk.LabelFrame(settings_frame, text="Hotkeys", padding=10)
        hotkeys_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(hotkeys_frame, text="Emergency Stop:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(hotkeys_frame, text="ESC", font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(hotkeys_frame, text="Quick Record:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(hotkeys_frame, text="F9", font=("Arial", 9, "bold")).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(hotkeys_frame, text="Quick Play:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(hotkeys_frame, text="F10", font=("Arial", 9, "bold")).grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Safety settings
        safety_frame = ttk.LabelFrame(settings_frame, text="Safety Settings", padding=10)
        safety_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(safety_frame, text="Screen boundary protection", variable=self.safe_mode).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(safety_frame, text="Confirm destructive operations").pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(safety_frame, text="Show click preview").pack(anchor=tk.W, pady=2)
        
        # Theme settings
        theme_frame = ttk.LabelFrame(settings_frame, text="Appearance", padding=10)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        theme_combo = ttk.Combobox(theme_frame, values=["Light", "Dark"], state="readonly", width=10)
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.set("Light")
        
        # Log area
        log_frame = ttk.LabelFrame(settings_frame, text="Application Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(self.status_bar, text="00:00:00")
        self.time_label.pack(side=tk.RIGHT, padx=5)
    
    # Recording methods
    def _toggle_recording(self):
        """Toggle recording on/off"""
        if self.is_recording.get():
            self._stop_recording()
        else:
            self._start_recording()
    
    def _start_recording(self):
        """Start recording"""
        self.recorder.debounce_threshold = self.debounce_var.get() / 1000.0
        
        if self.recorder.start_recording():
            self.is_recording.set(True)
            self.record_btn.config(text="Stop Recording")
            self.record_status.config(text="Recording...", foreground="red")
            self._clear_actions_tree()
            self._log("Recording started")
        else:
            messagebox.showerror("Error", "Failed to start recording")
    
    def _stop_recording(self):
        """Stop recording"""
        if self.recorder.stop_recording():
            self.is_recording.set(False)
            self.record_btn.config(text="Start Recording")
            self.record_status.config(text="Recording stopped", foreground="green")
            self.actions_list = self.recorder.get_actions()
            self._log(f"Recording stopped. {len(self.actions_list)} actions recorded")
            self._refresh_preview()
        else:
            messagebox.showerror("Error", "Failed to stop recording")
    
    def _on_action_recorded(self, action):
        """Called when an action is recorded"""
        self.action_count.set(len(self.recorder.get_actions()))
        
        # Add to actions tree
        time_str = f"{action['timestamp']:.2f}s"
        self.actions_tree.insert("", tk.END, values=(
            time_str, action['x'], action['y'], action['button']
        ))
        
        # Auto-scroll to bottom
        self.actions_tree.see(self.actions_tree.get_children()[-1])
    
    def _clear_actions_tree(self):
        """Clear the actions tree"""
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
        self.action_count.set(0)
    
    # Transformation methods
    def _apply_translation(self):
        """Apply translation transformation"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to transform")
            return
        
        offset_x = self.trans_x_var.get()
        offset_y = self.trans_y_var.get()
        
        transformation = self.transformer.create_translation_transform(offset_x, offset_y)
        self.actions_list = self.transformer.transform_actions(self.actions_list, [transformation])
        
        self._log(f"Applied translation: ({offset_x}, {offset_y})")
        self._refresh_preview()
    
    def _apply_scaling(self):
        """Apply scaling transformation"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to transform")
            return
        
        scale_x = self.scale_x_var.get()
        scale_y = self.scale_y_var.get()
        
        # Use center of actions as origin
        bbox = self.transformer.get_bounding_box(self.actions_list)
        origin = (bbox['center_x'], bbox['center_y'])
        
        transformation = self.transformer.create_scale_transform(scale_x, scale_y, origin)
        self.actions_list = self.transformer.transform_actions(self.actions_list, [transformation])
        
        self._log(f"Applied scaling: ({scale_x}, {scale_y})")
        self._refresh_preview()
    
    def _apply_rotation(self):
        """Apply rotation transformation"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to transform")
            return
        
        angle = self.rotate_var.get()
        
        # Use center of actions as pivot
        bbox = self.transformer.get_bounding_box(self.actions_list)
        pivot = (bbox['center_x'], bbox['center_y'])
        
        transformation = self.transformer.create_rotation_transform(angle, pivot)
        self.actions_list = self.transformer.transform_actions(self.actions_list, [transformation])
        
        self._log(f"Applied rotation: {angle}°")
        self._refresh_preview()
    
    def _apply_mirror(self):
        """Apply mirror transformation"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to transform")
            return
        
        axis = self.mirror_var.get()
        
        # Use center of actions as mirror center
        bbox = self.transformer.get_bounding_box(self.actions_list)
        center = (bbox['center_x'], bbox['center_y'])
        
        transformation = self.transformer.create_mirror_transform(axis, center)
        self.actions_list = self.transformer.transform_actions(self.actions_list, [transformation])
        
        self._log(f"Applied mirror: {axis}")
        self._refresh_preview()
    
    def _fit_to_screen(self):
        """Fit actions to screen size"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to transform")
            return
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.actions_list = self.transformer.fit_to_screen(self.actions_list, screen_width, screen_height)
        
        self._log(f"Fitted to screen: {screen_width}x{screen_height}")
        self._refresh_preview()
    
    def _reset_transformations(self):
        """Reset all transformations"""
        if messagebox.askyesno("Confirm", "Reset all transformations? This cannot be undone."):
            self.transformer.clear_transformation_history()
            self._log("Transformations reset")
    
    # Playback methods
    def _toggle_playback(self):
        """Toggle playback on/off"""
        if self.is_playing.get():
            self._stop_playback()
        else:
            self._start_playback()
    
    def _start_playback(self):
        """Start playback"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to play")
            return
        
        # Load actions and configure player
        self.player.load_actions(self.actions_list)
        self.player.set_speed(self.speed_var.get())
        self.player.set_loop_mode(self.loop_mode.get())
        self.player.set_safe_mode(self.safe_mode.get())
        
        if self.safe_mode.get():
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.player.set_screen_bounds(screen_width, screen_height)
        
        if self.player.play():
            self.is_playing.set(True)
            self.play_btn.config(text="⏸ Playing")
            self.play_status.config(text="Playing...")
            self._log("Playback started")
        else:
            messagebox.showerror("Error", "Failed to start playback")
    
    def _pause_playback(self):
        """Pause/unpause playback"""
        if self.player.pause():
            paused = self.player.is_paused
            self.is_paused.set(paused)
            self.pause_btn.config(text="▶ Resume" if paused else "⏸ Pause")
            self.play_status.config(text="Paused" if paused else "Playing...")
    
    def _stop_playback(self):
        """Stop playback"""
        if self.player.stop():
            self.is_playing.set(False)
            self.is_paused.set(False)
            self.play_btn.config(text="▶ Play")
            self.pause_btn.config(text="⏸ Pause")
            self.play_status.config(text="Stopped")
            self.progress_var.set(0)
            self._log("Playback stopped")
    
    def _on_playback_progress(self, progress, current, total):
        """Called during playback progress"""
        self.progress_var.set(progress * 100)
        self.play_status.config(text=f"Playing... ({current}/{total})")
    
    def _on_playback_complete(self, loops):
        """Called when playback completes"""
        self.is_playing.set(False)
        self.play_btn.config(text="▶ Play")
        self.play_status.config(text=f"Completed ({loops} loops)")
        self.progress_var.set(100)
        self._log(f"Playback completed. Loops: {loops}")
    
    def _on_speed_change(self, value):
        """Called when speed slider changes"""
        speed = float(value)
        self.speed_label.config(text=f"{speed:.1f}x")
        if hasattr(self, 'player'):
            self.player.set_speed(speed)
    
    # Preview methods
    def _refresh_preview(self):
        """Refresh the preview tab"""
        # Update statistics
        if self.actions_list:
            stats = self._get_action_statistics()
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats)
            self.stats_text.config(state=tk.DISABLED)
        
        # Update preview tree
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        for i, action in enumerate(self.actions_list):
            if action['type'] == 'click':
                rel_time = f"{action['timestamp']:.2f}s"
                self.preview_tree.insert("", tk.END, values=(
                    i, action.get('absolute_time', ''), action['x'], action['y'], 
                    action['button'], rel_time
                ))
        
        # Update playback info
        if self.actions_list:
            validation = self.player.validate_actions() if hasattr(self.player, 'validate_actions') else {}
            info_text = self._format_validation_info(validation)
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            self.info_text.config(state=tk.DISABLED)
    
    def _get_action_statistics(self) -> str:
        """Get formatted action statistics"""
        if not self.actions_list:
            return "No actions loaded"
        
        click_actions = [a for a in self.actions_list if a['type'] == 'click']
        total = len(click_actions)
        
        if total == 0:
            return "No click actions found"
        
        duration = click_actions[-1]['timestamp'] if click_actions else 0
        cps = total / duration if duration > 0 else 0
        
        # Button distribution
        buttons = {}
        for action in click_actions:
            button = action.get('button', 'unknown')
            buttons[button] = buttons.get(button, 0) + 1
        
        # Bounding box
        bbox = self.transformer.get_bounding_box(self.actions_list)
        
        stats = f"""Total Actions: {total}
Duration: {duration:.2f} seconds
Clicks/Second: {cps:.2f}
Bounding Box: {bbox['width']:.0f} x {bbox['height']:.0f}
Center: ({bbox['center_x']:.0f}, {bbox['center_y']:.0f})

Button Distribution:
"""
        for button, count in buttons.items():
            percentage = (count / total) * 100
            stats += f"  {button}: {count} ({percentage:.1f}%)\n"
        
        return stats
    
    def _format_validation_info(self, validation: Dict[str, Any]) -> str:
        """Format validation information"""
        if not validation:
            return "Validation not available"
        
        info = f"Validation Status: {'✓ Valid' if validation.get('valid', False) else '✗ Invalid'}\n\n"
        
        if validation.get('issues'):
            info += "Issues:\n"
            for issue in validation['issues']:
                info += f"  • {issue}\n"
            info += "\n"
        
        if validation.get('warnings'):
            info += "Warnings:\n"
            for warning in validation['warnings']:
                info += f"  ⚠ {warning}\n"
            info += "\n"
        
        info += f"Total Actions: {validation.get('total_actions', 0)}\n"
        info += f"Duration: {validation.get('duration', 0):.2f} seconds\n"
        
        return info
    
    def _export_preview(self):
        """Export preview information"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Preview",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Mouse Automation Toolkit - Actions Preview\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self._get_action_statistics())
                    f.write("\n\nDetailed Actions:\n")
                    for i, action in enumerate(self.actions_list):
                        if action['type'] == 'click':
                            f.write(f"{i}: {action['timestamp']:.2f}s - "
                                  f"{action['button']} click at ({action['x']}, {action['y']})\n")
                
                self._log(f"Preview exported to: {filename}")
                messagebox.showinfo("Success", f"Preview exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export preview:\n{e}")
    
    # File operations
    def _new_file(self):
        """Create new file"""
        if self.actions_list and messagebox.askyesno("Confirm", "Clear current actions?"):
            self._clear_actions()
    
    def _open_file(self):
        """Open actions file"""
        filename = filedialog.askopenfilename(
            title="Open Actions File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    
                if isinstance(data, dict) and 'actions' in data:
                    self.actions_list = data['actions']
                else:
                    self.actions_list = data
                
                self.current_file = filename
                self._log(f"Loaded {len(self.actions_list)} actions from: {filename}")
                self._refresh_preview()
                messagebox.showinfo("Success", f"Loaded {len(self.actions_list)} actions")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")
    
    def _save_file(self):
        """Save actions to current file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self._save_as_file()
    
    def _save_as_file(self):
        """Save actions to new file"""
        filename = filedialog.asksaveasfilename(
            title="Save Actions File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            self._save_to_file(filename)
    
    def _save_to_file(self, filename: str):
        """Save actions to specified file"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to save")
            return
        
        try:
            data = {
                'metadata': {
                    'version': '1.0',
                    'created': self.actions_list[0].get('absolute_time', '') if self.actions_list else '',
                    'total_actions': len(self.actions_list),
                    'duration': self.actions_list[-1]['timestamp'] if self.actions_list else 0
                },
                'actions': self.actions_list
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.current_file = filename
            self._log(f"Saved {len(self.actions_list)} actions to: {filename}")
            messagebox.showinfo("Success", f"Actions saved to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")
    
    def _clear_actions(self):
        """Clear all actions"""
        self.actions_list = []
        self.current_file = None
        self._clear_actions_tree()
        self._refresh_preview()
        self._log("Actions cleared")
    
    def _filter_duplicates(self):
        """Filter duplicate actions"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to filter")
            return
        
        # This would need to be implemented properly
        # For now, just show a message
        messagebox.showinfo("Info", "Duplicate filtering not yet implemented")
    
    # Utility methods
    def _log(self, message: str):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_status(self):
        """Update status bar"""
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        
        # Update status based on current state
        if self.is_recording.get():
            status = f"Recording... ({self.action_count.get()} actions)"
        elif self.is_playing.get():
            status = f"Playing... ({len(self.actions_list)} actions)"
        else:
            status = f"Ready ({len(self.actions_list)} actions loaded)"
        
        self.status_label.config(text=status)
    
    def _start_status_loop(self):
        """Start the status update loop"""
        self._update_status()
        self.root.after(1000, self._start_status_loop)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """Mouse Automation Toolkit v1.0

A comprehensive tool for recording, transforming, and replaying mouse actions.

Features:
• Record mouse clicks with precise timing
• Transform coordinates (translate, scale, rotate, mirror)
• Replay actions with speed control and safety features
• Comprehensive GUI with preview and validation
• Export/import action profiles

© 2024 Christopher Q2nz Tims"""
        
        messagebox.showinfo("About", about_text)
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_text = """Keyboard Shortcuts:

File Operations:
  Ctrl+N    New file
  Ctrl+O    Open file
  Ctrl+S    Save file
  Ctrl+Shift+S    Save as
  Ctrl+Q    Quit

Emergency:
  ESC       Emergency stop (during playback)
  
Function Keys:
  F9        Quick record toggle
  F10       Quick play toggle"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)