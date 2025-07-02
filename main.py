#!/usr/bin/env python3
"""
Mouse Automation Toolkit - Main Entry Point

A complete mouse automation toolkit with recording, transformation, and replay capabilities.

Usage:
    python main.py [options]
    
Options:
    --gui           Launch the GUI interface (default)
    --record FILE   Record mouse actions to file
    --play FILE     Play back actions from file
    --help          Show this help message
"""

import sys
import argparse
import logging
import time
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.recorder import MouseRecorder
from src.transformer import CoordinateTransformer
from src.player import ActionPlayer
from src.gui import main as gui_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def record_actions(output_file: str, duration: float = None) -> None:
    """
    Record mouse actions to a file.
    
    Args:
        output_file: Output filename for recorded actions
        duration: Recording duration in seconds (None for manual stop)
    """
    recorder = MouseRecorder()
    
    print(f"Starting mouse recording to '{output_file}'")
    if duration:
        print(f"Recording for {duration} seconds...")
        actions = recorder.record(duration)
    else:
        print("Press F9 to start recording, F10 to stop")
        print("Press Ctrl+C to exit")
        
        recorder.start_hotkey_listener()
        
        try:
            while True:
                time.sleep(0.1)
                if not recorder.is_recording and recorder.actions:
                    # Recording was stopped
                    actions = recorder.actions
                    break
        except KeyboardInterrupt:
            print("\nExiting...")
            actions = recorder.stop_recording() if recorder.is_recording else []
        finally:
            recorder.cleanup()
    
    if actions:
        recorder.save_to_file(output_file, actions)
        print(f"Saved {len(actions)} actions to '{output_file}'")
    else:
        print("No actions recorded")


def play_actions(input_file: str, 
                delay: float = 0.0, 
                speed: float = 1.0, 
                loops: int = 1) -> None:
    """
    Play back mouse actions from a file.
    
    Args:
        input_file: Input filename with recorded actions
        delay: Additional delay between actions
        speed: Speed multiplier
        loops: Number of times to repeat
    """
    recorder = MouseRecorder()
    player = ActionPlayer()
    
    try:
        # Load actions
        print(f"Loading actions from '{input_file}'...")
        actions = recorder.load_from_file(input_file)
        print(f"Loaded {len(actions)} actions")
        
        # Validate actions
        validation = player.validate_actions(actions)
        if not validation['valid']:
            print("WARNING: Actions failed validation:")
            for error in validation.get('errors', []):
                print(f"  ERROR: {error}")
        
        if validation.get('warnings'):
            print("WARNINGS:")
            for warning in validation['warnings']:
                print(f"  WARNING: {warning}")
        
        # Start playback
        print(f"Starting playback in 3 seconds...")
        print("Press ESC to stop playback")
        
        success = player.replay(
            actions,
            delay=delay,
            speed_multiplier=speed,
            loop_count=loops,
            start_delay=3.0
        )
        
        if success:
            print("Playback completed successfully")
        else:
            print("Playback was stopped")
            
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        player.cleanup()


def transform_actions(input_file: str, 
                     output_file: str,
                     transform_type: str,
                     **kwargs) -> None:
    """
    Transform actions and save to a new file.
    
    Args:
        input_file: Input filename
        output_file: Output filename
        transform_type: Type of transformation
        **kwargs: Transformation parameters
    """
    recorder = MouseRecorder()
    transformer = CoordinateTransformer()
    
    try:
        # Load actions
        print(f"Loading actions from '{input_file}'...")
        actions = recorder.load_from_file(input_file)
        print(f"Loaded {len(actions)} actions")
        
        # Apply transformation
        print(f"Applying {transform_type} transformation...")
        
        if transform_type == 'translate':
            transformed = transformer.translate(
                actions, 
                kwargs.get('offset_x', 0), 
                kwargs.get('offset_y', 0)
            )
        elif transform_type == 'scale':
            transformed = transformer.scale(
                actions,
                kwargs.get('scale_x', 1.0),
                kwargs.get('scale_y', 1.0)
            )
        elif transform_type == 'rotate':
            transformed = transformer.rotate(
                actions,
                kwargs.get('angle', 0)
            )
        elif transform_type == 'mirror_h':
            transformed = transformer.mirror_horizontal(actions)
        elif transform_type == 'mirror_v':
            transformed = transformer.mirror_vertical(actions)
        else:
            print(f"Unknown transformation type: {transform_type}")
            return
        
        # Save transformed actions
        recorder.save_to_file(output_file, transformed)
        print(f"Saved {len(transformed)} transformed actions to '{output_file}'")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except Exception as e:
        print(f"Error: {e}")


def show_examples():
    """Show usage examples."""
    examples = """
Mouse Automation Toolkit - Usage Examples:

1. Launch GUI (default):
   python main.py
   python main.py --gui

2. Record mouse actions:
   python main.py --record actions.json
   python main.py --record actions.json --duration 10

3. Play back recorded actions:
   python main.py --play actions.json
   python main.py --play actions.json --delay 0.5 --speed 2.0 --loops 3

4. Transform actions:
   python main.py --transform actions.json output.json --translate 100 50
   python main.py --transform actions.json output.json --scale 1.5 1.5
   python main.py --transform actions.json output.json --rotate 45

5. Command combinations:
   # Record for 30 seconds, then play back twice at half speed
   python main.py --record temp.json --duration 30
   python main.py --play temp.json --speed 0.5 --loops 2

Features:
- Cross-platform support (Windows, macOS, Linux)
- Safety features with emergency stops
- Coordinate transformations
- GUI interface for easy use
- Hotkey support (F9 to start recording, F10 to stop, ESC to stop playback)
- Batch processing capabilities

For more information, visit: https://github.com/ChistoperQ2nzTims/mouse-automation-toolkit
"""
    print(examples)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Mouse Automation Toolkit - Record, transform, and replay mouse actions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Use --examples for usage examples"
    )
    
    # Main action arguments
    parser.add_argument('--gui', action='store_true', default=False,
                       help='Launch the GUI interface')
    parser.add_argument('--record', metavar='FILE',
                       help='Record mouse actions to file')
    parser.add_argument('--play', metavar='FILE',
                       help='Play back actions from file')
    parser.add_argument('--transform', nargs=2, metavar=('INPUT', 'OUTPUT'),
                       help='Transform actions from INPUT file to OUTPUT file')
    parser.add_argument('--examples', action='store_true',
                       help='Show usage examples')
    
    # Recording options
    parser.add_argument('--duration', type=float, metavar='SECONDS',
                       help='Recording duration in seconds')
    
    # Playback options
    parser.add_argument('--delay', type=float, default=0.0, metavar='SECONDS',
                       help='Additional delay between actions (default: 0.0)')
    parser.add_argument('--speed', type=float, default=1.0, metavar='MULTIPLIER',
                       help='Speed multiplier for playback (default: 1.0)')
    parser.add_argument('--loops', type=int, default=1, metavar='COUNT',
                       help='Number of times to repeat playback (default: 1)')
    
    # Transformation options
    parser.add_argument('--translate', nargs=2, type=float, metavar=('X', 'Y'),
                       help='Translate coordinates by X, Y offset')
    parser.add_argument('--scale', nargs=2, type=float, metavar=('X', 'Y'),
                       help='Scale coordinates by X, Y factors')
    parser.add_argument('--rotate', type=float, metavar='DEGREES',
                       help='Rotate coordinates by degrees')
    parser.add_argument('--mirror-h', action='store_true',
                       help='Mirror coordinates horizontally')
    parser.add_argument('--mirror-v', action='store_true',
                       help='Mirror coordinates vertically')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show examples if requested
    if args.examples:
        show_examples()
        return
    
    # Determine action based on arguments
    if args.record:
        record_actions(args.record, args.duration)
    elif args.play:
        play_actions(args.play, args.delay, args.speed, args.loops)
    elif args.transform:
        input_file, output_file = args.transform
        
        # Determine transformation type and parameters
        if args.translate:
            transform_actions(input_file, output_file, 'translate',
                            offset_x=args.translate[0], offset_y=args.translate[1])
        elif args.scale:
            transform_actions(input_file, output_file, 'scale',
                            scale_x=args.scale[0], scale_y=args.scale[1])
        elif args.rotate:
            transform_actions(input_file, output_file, 'rotate',
                            angle=args.rotate)
        elif args.mirror_h:
            transform_actions(input_file, output_file, 'mirror_h')
        elif args.mirror_v:
            transform_actions(input_file, output_file, 'mirror_v')
        else:
            print("Error: No transformation specified. Use --translate, --scale, --rotate, --mirror-h, or --mirror-v")
    else:
        # Default action: launch GUI
        print("Mouse Automation Toolkit 🐭🤖")
        print("Launching GUI interface...")
        print("Use --help for command-line options")
        
        try:
            gui_main()
        except ImportError as e:
            print(f"Error: Failed to import GUI dependencies: {e}")
            print("Make sure tkinter is installed")
        except Exception as e:
            print(f"Error launching GUI: {e}")


if __name__ == "__main__":
    main()