"""
GUI Module

Tkinter-based graphical user interface for the Mouse Automation Toolkit.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import os
from typing import List, Optional
import json
import logging

from .recorder import MouseRecorder, MouseAction
from .transformer import CoordinateTransformer
from .player import MousePlayer

logger = logging.getLogger(__name__)


class MouseAutomationGUI:
    """Main GUI application for Mouse Automation Toolkit."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mouse Automation Toolkit 🐭🤖")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Core components
        self.recorder = MouseRecorder()
        self.transformer = CoordinateTransformer()
        self.player = MousePlayer()
        
        # State variables
        self.current_actions: List[MouseAction] = []
        self.current_profile_path = None
        
        # GUI variables
        self.recording_var = tk.BooleanVar()
        self.playing_var = tk.BooleanVar()
        self.progress_var = tk.StringVar(value="Ready")
        
        self._setup_gui()
        self._setup_hotkeys()
        
    def _setup_gui(self):
        """Set up the GUI layout."""
        # Create main frames
        self._create_menu()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()
        
    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Profile", command=self.new_profile)
        file_menu.add_command(label="Open Profile...", command=self.open_profile)
        file_menu.add_command(label="Save Profile", command=self.save_profile)
        file_menu.add_command(label="Save Profile As...", command=self.save_profile_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate Actions", command=self.validate_actions)
        tools_menu.add_command(label="Preview Actions", command=self.preview_actions)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def _create_toolbar(self):
        """Create the toolbar with main action buttons."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Recording controls
        record_frame = ttk.LabelFrame(toolbar, text="Recording")
        record_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        self.record_btn = ttk.Button(record_frame, text="🔴 Record", 
                                   command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = ttk.Button(record_frame, text="🗑️ Clear", 
                                  command=self.clear_actions)
        self.clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Transform controls
        transform_frame = ttk.LabelFrame(toolbar, text="Transform")
        transform_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        self.transform_btn = ttk.Button(transform_frame, text="🔄 Transform", 
                                      command=self.show_transform_dialog)
        self.transform_btn.pack(side=tk.LEFT, padx=2)
        
        # Playback controls
        playback_frame = ttk.LabelFrame(toolbar, text="Playback")
        playback_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        self.play_btn = ttk.Button(playback_frame, text="▶️ Play", 
                                 command=self.toggle_playback)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = ttk.Button(playback_frame, text="⏸️ Pause", 
                                  command=self.pause_playback, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(playback_frame, text="⏹️ Stop", 
                                 command=self.stop_playback, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
    def _create_main_content(self):
        """Create the main content area."""
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Actions tab
        actions_frame = ttk.Frame(self.notebook)
        self.notebook.add(actions_frame, text="Actions")
        self._create_actions_tab(actions_frame)
        
        # Settings tab
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        self._create_settings_tab(settings_frame)
        
        # Log tab
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Log")
        self._create_log_tab(log_frame)
        
    def _create_actions_tab(self, parent):
        """Create the actions tab content."""
        # Actions list
        list_frame = ttk.LabelFrame(parent, text="Recorded Actions")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for actions
        columns = ("Index", "Type", "Position", "Button", "Delay")
        self.actions_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.actions_tree.heading(col, text=col)
            self.actions_tree.column(col, width=100)
            
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.actions_tree.xview)
        
        self.actions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.actions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Action details
        details_frame = ttk.LabelFrame(parent, text="Action Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.action_details = tk.Text(details_frame, height=4, state=tk.DISABLED)
        self.action_details.pack(fill=tk.X, padx=5, pady=5)
        
    def _create_settings_tab(self, parent):
        """Create the settings tab content."""
        # Recording settings
        record_settings = ttk.LabelFrame(parent, text="Recording Settings")
        record_settings.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(record_settings, text="Smart Recording:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.smart_recording_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(record_settings, variable=self.smart_recording_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(record_settings, text="Min Delay (s):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.min_delay_var = tk.DoubleVar(value=0.1)
        ttk.Entry(record_settings, textvariable=self.min_delay_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Playback settings
        playback_settings = ttk.LabelFrame(parent, text="Playback Settings")
        playback_settings.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(playback_settings, text="Delay Multiplier:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.delay_multiplier_var = tk.DoubleVar(value=1.0)
        ttk.Entry(playback_settings, textvariable=self.delay_multiplier_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(playback_settings, text="Random Delay:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.random_delay_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(playback_settings, variable=self.random_delay_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(playback_settings, text="Loop Count:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.loop_count_var = tk.IntVar(value=1)
        ttk.Entry(playback_settings, textvariable=self.loop_count_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Screen settings
        screen_settings = ttk.LabelFrame(parent, text="Screen Settings")
        screen_settings.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(screen_settings, text="Screen Width:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.screen_width_var = tk.IntVar(value=1920)
        ttk.Entry(screen_settings, textvariable=self.screen_width_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(screen_settings, text="Screen Height:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.screen_height_var = tk.IntVar(value=1080)
        ttk.Entry(screen_settings, textvariable=self.screen_height_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Apply settings button
        ttk.Button(parent, text="Apply Settings", command=self.apply_settings).pack(pady=10)
        
    def _create_log_tab(self, parent):
        """Create the log tab content."""
        self.log_text = scrolledtext.ScrolledText(parent, state=tk.DISABLED, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log controls
        log_controls = ttk.Frame(parent)
        log_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_controls, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT)
        ttk.Button(log_controls, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)
        
    def _create_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(status_frame, textvariable=self.progress_var).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(status_frame, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
    def _setup_hotkeys(self):
        """Set up keyboard shortcuts."""
        self.root.bind('<Control-n>', lambda e: self.new_profile())
        self.root.bind('<Control-o>', lambda e: self.open_profile())
        self.root.bind('<Control-s>', lambda e: self.save_profile())
        self.root.bind('<F9>', lambda e: self.toggle_recording())
        self.root.bind('<F5>', lambda e: self.toggle_playback())
        self.root.bind('<Escape>', lambda e: self.stop_playback())
        
    def toggle_recording(self):
        """Toggle recording on/off."""
        if not self.recording_var.get():
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start recording mouse actions."""
        self.recorder.smart_recording = self.smart_recording_var.get()
        self.recorder.min_delay = self.min_delay_var.get()
        
        self.recorder.start_recording(callback=self.on_action_recorded)
        self.recording_var.set(True)
        self.record_btn.config(text="⏹️ Stop Recording")
        self.progress_var.set("Recording... Press F9 or click button to stop")
        self.log_message("Recording started")
        
    def stop_recording(self):
        """Stop recording mouse actions."""
        self.recorder.stop_recording()
        self.recording_var.set(False)
        self.record_btn.config(text="🔴 Record")
        self.current_actions = self.recorder.get_actions()
        self.update_actions_display()
        self.progress_var.set(f"Recording stopped. {len(self.current_actions)} actions recorded")
        self.log_message(f"Recording stopped. {len(self.current_actions)} actions recorded")
        
    def on_action_recorded(self, action: MouseAction):
        """Called when a new action is recorded."""
        # Update UI in main thread
        self.root.after(0, self._update_recording_status)
        
    def _update_recording_status(self):
        """Update recording status in UI."""
        if self.recording_var.get():
            action_count = len(self.recorder.actions)
            self.progress_var.set(f"Recording... {action_count} actions")
            
    def clear_actions(self):
        """Clear all recorded actions."""
        if messagebox.askyesno("Clear Actions", "Are you sure you want to clear all recorded actions?"):
            self.recorder.clear_actions()
            self.current_actions.clear()
            self.update_actions_display()
            self.progress_var.set("Actions cleared")
            self.log_message("Actions cleared")
            
    def update_actions_display(self):
        """Update the actions display in the treeview."""
        # Clear existing items
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
            
        # Add current actions
        for i, action in enumerate(self.current_actions):
            self.actions_tree.insert("", "end", values=(
                i + 1,
                action.action_type,
                f"({action.x}, {action.y})",
                action.button or "N/A",
                f"{action.delay:.3f}s" if action.delay > 0 else "N/A"
            ))
            
    def toggle_playback(self):
        """Toggle playback on/off."""
        if not self.playing_var.get():
            self.start_playback()
        else:
            self.stop_playback()
            
    def start_playback(self):
        """Start playing back actions."""
        if not self.current_actions:
            messagebox.showwarning("No Actions", "No actions to play. Please record some actions first.")
            return
            
        # Validate actions first
        warnings = self.player.validate_actions(self.current_actions)
        if warnings:
            if not messagebox.askyesno("Validation Warnings", 
                                     f"Found {len(warnings)} warnings:\n" + 
                                     "\n".join(warnings[:5]) + 
                                     ("\n..." if len(warnings) > 5 else "") +
                                     "\n\nContinue anyway?"):
                return
                
        self.playing_var.set(True)
        self.play_btn.config(text="⏹️ Stop", state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        delay_multiplier = self.delay_multiplier_var.get()
        random_delay = self.random_delay_var.get()
        loop_count = self.loop_count_var.get()
        
        self.player.play_actions(
            self.current_actions,
            delay_multiplier=delay_multiplier,
            random_delay=random_delay,
            loop_count=loop_count,
            progress_callback=self.on_playback_progress,
            completion_callback=self.on_playback_complete
        )
        
        estimated_duration = self.player.get_estimated_duration(self.current_actions, delay_multiplier)
        self.progress_var.set(f"Playing... Estimated duration: {estimated_duration:.1f}s")
        self.log_message("Playback started")
        
    def pause_playback(self):
        """Pause/resume playback."""
        if self.player.is_paused:
            self.player.resume_playback()
            self.pause_btn.config(text="⏸️ Pause")
            self.log_message("Playback resumed")
        else:
            self.player.pause_playback()
            self.pause_btn.config(text="▶️ Resume")
            self.log_message("Playback paused")
            
    def stop_playback(self):
        """Stop playback."""
        self.player.stop_playback()
        self._reset_playback_ui()
        
    def on_playback_progress(self, current: int, total: int):
        """Called during playback to update progress."""
        self.root.after(0, self._update_playback_progress, current, total)
        
    def _update_playback_progress(self, current: int, total: int):
        """Update playback progress in UI."""
        progress = (current / total) * 100 if total > 0 else 0
        self.progress_bar['value'] = progress
        self.progress_var.set(f"Playing... {current}/{total} ({progress:.1f}%)")
        
    def on_playback_complete(self):
        """Called when playback completes."""
        self.root.after(0, self._on_playback_complete)
        
    def _on_playback_complete(self):
        """Handle playback completion in UI thread."""
        self._reset_playback_ui()
        self.progress_var.set("Playback completed")
        self.log_message("Playback completed")
        
    def _reset_playback_ui(self):
        """Reset playback UI controls."""
        self.playing_var.set(False)
        self.play_btn.config(text="▶️ Play", state=tk.NORMAL)
        self.pause_btn.config(text="⏸️ Pause", state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        
    def show_transform_dialog(self):
        """Show transformation dialog."""
        if not self.current_actions:
            messagebox.showwarning("No Actions", "No actions to transform. Please record some actions first.")
            return
            
        TransformDialog(self, self.current_actions, self.transformer)
        
    def apply_settings(self):
        """Apply current settings."""
        self.transformer.set_screen_dimensions(
            self.screen_width_var.get(),
            self.screen_height_var.get()
        )
        self.log_message("Settings applied")
        
    def validate_actions(self):
        """Validate current actions."""
        if not self.current_actions:
            messagebox.showinfo("No Actions", "No actions to validate.")
            return
            
        warnings = self.player.validate_actions(self.current_actions)
        if warnings:
            messagebox.showwarning("Validation Results", 
                                 f"Found {len(warnings)} issues:\n" + "\n".join(warnings))
        else:
            messagebox.showinfo("Validation Results", "All actions are valid!")
            
    def preview_actions(self):
        """Show action preview."""
        if not self.current_actions:
            messagebox.showinfo("No Actions", "No actions to preview.")
            return
            
        preview = self.player.preview_actions(self.current_actions)
        PreviewDialog(self, preview)
        
    def new_profile(self):
        """Create a new profile."""
        if self.current_actions and messagebox.askyesno("New Profile", 
                                                       "Current actions will be lost. Continue?"):
            self.current_actions.clear()
            self.update_actions_display()
            self.current_profile_path = None
            self.progress_var.set("New profile created")
            
    def open_profile(self):
        """Open a profile from file."""
        filename = filedialog.askopenfilename(
            title="Open Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.recorder.load_from_file(filename)
                self.current_actions = self.recorder.get_actions()
                self.update_actions_display()
                self.current_profile_path = filename
                self.progress_var.set(f"Loaded profile: {os.path.basename(filename)}")
                self.log_message(f"Loaded profile: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load profile: {e}")
                
    def save_profile(self):
        """Save current profile."""
        if self.current_profile_path:
            self._save_to_file(self.current_profile_path)
        else:
            self.save_profile_as()
            
    def save_profile_as(self):
        """Save profile with new filename."""
        filename = filedialog.asksaveasfilename(
            title="Save Profile As",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        
        if filename:
            self._save_to_file(filename)
            self.current_profile_path = filename
            
    def _save_to_file(self, filename: str):
        """Save actions to file."""
        try:
            # Set actions in recorder for saving
            self.recorder.actions = self.current_actions
            self.recorder.save_to_file(filename)
            self.progress_var.set(f"Saved profile: {os.path.basename(filename)}")
            self.log_message(f"Saved profile: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {e}")
            
    def show_settings(self):
        """Show settings dialog."""
        # Switch to settings tab
        self.notebook.select(1)
        
    def show_about(self):
        """Show about dialog."""
        about_text = """Mouse Automation Toolkit 🐭🤖

Version 1.0.0

A comprehensive toolkit for recording, transforming, and replaying mouse actions.

Features:
• Mouse action recording with smart filtering
• Coordinate transformations (translate, scale, rotate, mirror)
• Playback with customizable delays and looping
• User-friendly GUI interface
• Profile management
• Action validation and preview

Keyboard shortcuts:
• F9: Toggle recording
• F5: Start/stop playback  
• Esc: Emergency stop
• Ctrl+N: New profile
• Ctrl+O: Open profile
• Ctrl+S: Save profile

Made with ❤️ using Python, PyAutoGUI, pynput, and tkinter."""

        messagebox.showinfo("About", about_text)
        
    def log_message(self, message: str):
        """Add message to log."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def clear_log(self):
        """Clear the log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def save_log(self):
        """Save log to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Log",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            defaultextension=".txt"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
                
    def run(self):
        """Start the GUI application."""
        self.apply_settings()  # Apply default settings
        self.log_message("Mouse Automation Toolkit started")
        self.root.mainloop()


class TransformDialog:
    """Dialog for coordinate transformations."""
    
    def __init__(self, parent, actions: List[MouseAction], transformer: CoordinateTransformer):
        self.parent = parent
        self.actions = actions
        self.transformer = transformer
        
        self.dialog = tk.Toplevel(parent.root)
        self.dialog.title("Transform Coordinates")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent.root)
        self.dialog.grab_set()
        
        self._setup_dialog()
        
    def _setup_dialog(self):
        """Set up the dialog interface."""
        # Transform options
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Translate tab
        translate_frame = ttk.Frame(notebook)
        notebook.add(translate_frame, text="Translate")
        self._create_translate_tab(translate_frame)
        
        # Scale tab
        scale_frame = ttk.Frame(notebook)
        notebook.add(scale_frame, text="Scale")
        self._create_scale_tab(scale_frame)
        
        # Rotate tab
        rotate_frame = ttk.Frame(notebook)
        notebook.add(rotate_frame, text="Rotate")
        self._create_rotate_tab(rotate_frame)
        
        # Mirror tab
        mirror_frame = ttk.Frame(notebook)
        notebook.add(mirror_frame, text="Mirror")
        self._create_mirror_tab(mirror_frame)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=self.apply_transform).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
    def _create_translate_tab(self, parent):
        """Create translate tab."""
        ttk.Label(parent, text="X Offset:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.translate_x = tk.IntVar(value=0)
        ttk.Entry(parent, textvariable=self.translate_x, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(parent, text="Y Offset:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.translate_y = tk.IntVar(value=0)
        ttk.Entry(parent, textvariable=self.translate_y, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(parent, text="Apply Translation", 
                  command=lambda: self._apply_single_transform('translate')).grid(row=2, column=0, columnspan=2, pady=10)
        
    def _create_scale_tab(self, parent):
        """Create scale tab."""
        ttk.Label(parent, text="X Scale:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.scale_x = tk.DoubleVar(value=1.0)
        ttk.Entry(parent, textvariable=self.scale_x, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(parent, text="Y Scale:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.scale_y = tk.DoubleVar(value=1.0)
        ttk.Entry(parent, textvariable=self.scale_y, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(parent, text="Apply Scaling", 
                  command=lambda: self._apply_single_transform('scale')).grid(row=2, column=0, columnspan=2, pady=10)
        
    def _create_rotate_tab(self, parent):
        """Create rotate tab."""
        ttk.Label(parent, text="Angle (degrees):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.rotate_angle = tk.DoubleVar(value=0.0)
        ttk.Entry(parent, textvariable=self.rotate_angle, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(parent, text="Apply Rotation", 
                  command=lambda: self._apply_single_transform('rotate')).grid(row=1, column=0, columnspan=2, pady=10)
        
    def _create_mirror_tab(self, parent):
        """Create mirror tab."""
        ttk.Button(parent, text="Mirror Horizontal", 
                  command=lambda: self._apply_single_transform('mirror_horizontal')).pack(pady=10)
        ttk.Button(parent, text="Mirror Vertical", 
                  command=lambda: self._apply_single_transform('mirror_vertical')).pack(pady=10)
        
    def _apply_single_transform(self, transform_type: str):
        """Apply a single transformation."""
        try:
            if transform_type == 'translate':
                transformed = self.transformer.translate(self.actions, 
                                                       self.translate_x.get(), 
                                                       self.translate_y.get())
            elif transform_type == 'scale':
                transformed = self.transformer.scale(self.actions, 
                                                   self.scale_x.get(), 
                                                   self.scale_y.get())
            elif transform_type == 'rotate':
                transformed = self.transformer.rotate(self.actions, 
                                                    self.rotate_angle.get())
            elif transform_type == 'mirror_horizontal':
                transformed = self.transformer.mirror_horizontal(self.actions)
            elif transform_type == 'mirror_vertical':
                transformed = self.transformer.mirror_vertical(self.actions)
            else:
                return
                
            self.parent.current_actions = transformed
            self.parent.update_actions_display()
            self.parent.log_message(f"Applied {transform_type} transformation")
            messagebox.showinfo("Success", f"{transform_type.title()} transformation applied!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply transformation: {e}")
            
    def apply_transform(self):
        """Apply the selected transformation and close dialog."""
        self.dialog.destroy()


class PreviewDialog:
    """Dialog for previewing actions."""
    
    def __init__(self, parent, preview_data: List[dict]):
        self.dialog = tk.Toplevel(parent.root)
        self.dialog.title("Action Preview")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent.root)
        self.dialog.grab_set()
        
        # Create treeview
        columns = ("Index", "Type", "Position", "Button", "Delay")
        tree = ttk.Treeview(self.dialog, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=90)
            
        # Add data
        for item in preview_data:
            tree.insert("", "end", values=(
                item['index'],
                item['action_type'],
                item['position'],
                item['button'],
                item['delay']
            ))
            
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Pack
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Close button
        ttk.Button(self.dialog, text="Close", 
                  command=self.dialog.destroy).pack(side=tk.BOTTOM, pady=10)


def main():
    """Main entry point for the GUI application."""
    app = MouseAutomationGUI()
    app.run()


if __name__ == "__main__":
    main()