#!/usr/bin/env python3
"""
Mouse Automation Toolkit - Main Entry Point

A comprehensive tool for recording, transforming, and replaying mouse actions.
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui import MainGUI
from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description="Mouse Automation Toolkit - Record, transform, and replay mouse actions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Launch GUI interface
  %(prog)s --cli --record out.json  # Record actions to file (CLI mode)
  %(prog)s --cli --play in.json     # Play actions from file (CLI mode)
  %(prog)s --cli --transform in.json out.json --translate 100 50  # Transform and save
        """
    )
    
    # GUI or CLI mode
    parser.add_argument('--cli', action='store_true',
                       help='Run in command-line mode instead of GUI')
    
    # CLI mode operations
    parser.add_argument('--record', metavar='FILE',
                       help='Record mouse actions to file')
    parser.add_argument('--play', metavar='FILE',
                       help='Play mouse actions from file')
    parser.add_argument('--transform', nargs=2, metavar=('INPUT', 'OUTPUT'),
                       help='Transform actions from INPUT file and save to OUTPUT file')
    
    # Transformation options
    parser.add_argument('--translate', nargs=2, type=float, metavar=('X', 'Y'),
                       help='Translate coordinates by X,Y offset')
    parser.add_argument('--scale', nargs=2, type=float, metavar=('X', 'Y'),
                       help='Scale coordinates by X,Y factors')
    parser.add_argument('--rotate', type=float, metavar='ANGLE',
                       help='Rotate coordinates by ANGLE degrees')
    parser.add_argument('--mirror', choices=['horizontal', 'vertical', 'both'],
                       help='Mirror coordinates across axis')
    
    # Playback options
    parser.add_argument('--speed', type=float, default=1.0, metavar='MULTIPLIER',
                       help='Playback speed multiplier (0.1 to 5.0)')
    parser.add_argument('--loop', action='store_true',
                       help='Loop playback continuously')
    parser.add_argument('--no-safe-mode', action='store_true',
                       help='Disable safe mode (screen boundary checks)')
    
    # General options
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.cli:
        return run_cli_mode(args)
    else:
        return run_gui_mode(args)


def run_gui_mode(args):
    """Run the application in GUI mode"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        # Create and run the GUI
        root = tk.Tk()
        app = MainGUI(root)
        
        # Handle any command line arguments for GUI mode
        if args.verbose:
            print("Starting Mouse Automation Toolkit GUI...")
        
        root.mainloop()
        return 0
        
    except ImportError:
        print("Error: tkinter is not available. Please install tkinter or use --cli mode.")
        return 1
    except Exception as e:
        print(f"Error starting GUI: {e}")
        return 1


def run_cli_mode(args):
    """Run the application in CLI mode"""
    try:
        if args.record:
            return record_actions_cli(args)
        elif args.play:
            return play_actions_cli(args)
        elif args.transform:
            return transform_actions_cli(args)
        else:
            print("Error: CLI mode requires --record, --play, or --transform operation")
            return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def record_actions_cli(args):
    """Record mouse actions in CLI mode"""
    recorder = MouseRecorder()
    
    def on_action(action):
        if args.verbose:
            print(f"Recorded: {action['button']} click at ({action['x']}, {action['y']})")
    
    recorder.set_action_callback(on_action)
    
    print(f"Recording mouse actions to: {args.record}")
    print("Press Ctrl+C to stop recording...")
    
    if not recorder.start_recording():
        print("Error: Failed to start recording")
        return 1
    
    try:
        # Keep recording until interrupted
        import time
        while recorder.is_recording:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    
    recorder.stop_recording()
    
    actions = recorder.get_actions()
    print(f"\nRecorded {len(actions)} actions")
    
    if recorder.save_to_file(args.record):
        print(f"Actions saved to: {args.record}")
        return 0
    else:
        print("Error: Failed to save actions")
        return 1


def play_actions_cli(args):
    """Play mouse actions in CLI mode"""
    player = ActionPlayer()
    
    # Load actions from file
    if not os.path.exists(args.play):
        print(f"Error: File not found: {args.play}")
        return 1
    
    try:
        with open(args.play, 'r') as f:
            data = json.load(f)
            actions = data.get('actions', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error loading actions: {e}")
        return 1
    
    if not player.load_actions(actions):
        print("Error: Failed to load actions")
        return 1
    
    # Configure playback
    player.set_speed(args.speed)
    player.set_loop_mode(args.loop)
    player.set_safe_mode(not args.no_safe_mode)
    
    # Progress callback
    def on_progress(progress, current, total):
        if args.verbose:
            print(f"\rProgress: {progress*100:.1f}% ({current}/{total})", end='', flush=True)
    
    def on_complete(loops):
        if args.verbose:
            print(f"\nPlayback completed. Loops: {loops}")
    
    player.set_progress_callback(on_progress)
    player.set_complete_callback(on_complete)
    
    print(f"Playing {len(actions)} actions from: {args.play}")
    print(f"Speed: {args.speed}x, Loop: {args.loop}, Safe mode: {not args.no_safe_mode}")
    print("Press ESC to stop playback...")
    
    if not player.play():
        print("Error: Failed to start playback")
        return 1
    
    # Wait for playback to complete
    try:
        while player.is_playing:
            import time
            time.sleep(0.1)
    except KeyboardInterrupt:
        player.stop()
        print("\nPlayback stopped by user")
    
    return 0


def transform_actions_cli(args):
    """Transform mouse actions in CLI mode"""
    input_file, output_file = args.transform
    
    # Load actions
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return 1
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
            actions = data.get('actions', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error loading actions: {e}")
        return 1
    
    # Create transformer and build transformation list
    transformer = CoordinateTransformer()
    transformations = []
    
    if args.translate:
        transformations.append(transformer.create_translation_transform(args.translate[0], args.translate[1]))
        if args.verbose:
            print(f"Added translation: ({args.translate[0]}, {args.translate[1]})")
    
    if args.scale:
        transformations.append(transformer.create_scale_transform(args.scale[0], args.scale[1]))
        if args.verbose:
            print(f"Added scaling: ({args.scale[0]}, {args.scale[1]})")
    
    if args.rotate:
        transformations.append(transformer.create_rotation_transform(args.rotate))
        if args.verbose:
            print(f"Added rotation: {args.rotate} degrees")
    
    if args.mirror:
        transformations.append(transformer.create_mirror_transform(args.mirror))
        if args.verbose:
            print(f"Added mirroring: {args.mirror}")
    
    if not transformations:
        print("Error: No transformations specified")
        return 1
    
    # Apply transformations
    if args.verbose:
        print(f"Applying {len(transformations)} transformation(s)...")
    
    transformed_actions = transformer.transform_actions(actions, transformations)
    
    # Save transformed actions
    try:
        output_data = {
            'metadata': {
                'version': '1.0',
                'created': actions[0]['absolute_time'] if actions else '',
                'transformed': True,
                'original_file': input_file,
                'transformations': transformations,
                'total_actions': len(transformed_actions)
            },
            'actions': transformed_actions
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Transformed {len(actions)} actions and saved to: {output_file}")
        return 0
        
    except Exception as e:
        print(f"Error saving transformed actions: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())