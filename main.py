#!/usr/bin/env python3
"""
Mouse Automation Toolkit - Main Entry Point

Launch the GUI application or run command-line interface.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gui import MouseAutomationGUI
from src.recorder import MouseRecorder
from src.player import MousePlayer
from src.transformer import CoordinateTransformer


def setup_logging(log_level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_gui():
    """Run the GUI application."""
    print("🐭🤖 Mouse Automation Toolkit - Starting GUI...")
    app = MouseAutomationGUI()
    app.run()


def run_cli(args):
    """Run command-line interface."""
    recorder = MouseRecorder()
    player = MousePlayer()
    transformer = CoordinateTransformer()
    
    if args.record:
        print(f"Recording to {args.record}...")
        print("Press Ctrl+C to stop recording")
        
        try:
            recorder.start_recording()
            input("Press Enter to stop recording...")
        except KeyboardInterrupt:
            pass
        finally:
            recorder.stop_recording()
            recorder.save_to_file(args.record)
            print(f"Saved {len(recorder.get_actions())} actions to {args.record}")
            
    elif args.play:
        print(f"Playing actions from {args.play}...")
        
        try:
            recorder.load_from_file(args.play)
            actions = recorder.get_actions()
            
            # Apply transformations if specified
            if args.translate:
                x_offset, y_offset = map(int, args.translate.split(','))
                actions = transformer.translate(actions, x_offset, y_offset)
                print(f"Applied translation: ({x_offset}, {y_offset})")
                
            if args.scale:
                scale_x, scale_y = map(float, args.scale.split(','))
                actions = transformer.scale(actions, scale_x, scale_y)
                print(f"Applied scaling: ({scale_x}, {scale_y})")
                
            if args.rotate:
                actions = transformer.rotate(actions, float(args.rotate))
                print(f"Applied rotation: {args.rotate}°")
                
            # Validate actions
            warnings = player.validate_actions(actions)
            if warnings:
                print(f"⚠️  {len(warnings)} validation warnings:")
                for warning in warnings[:5]:
                    print(f"   {warning}")
                if len(warnings) > 5:
                    print(f"   ... and {len(warnings) - 5} more")
                    
                if input("Continue? (y/N): ").lower() != 'y':
                    return
                    
            # Playback
            delay_multiplier = args.delay if args.delay else 1.0
            loop_count = args.loop if args.loop else 1
            
            print(f"Playing {len(actions)} actions...")
            print("Press Ctrl+C to stop playback")
            
            player.play_actions(
                actions,
                delay_multiplier=delay_multiplier,
                loop_count=loop_count
            )
            
            # Wait for completion
            while player.is_playing:
                try:
                    import time
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    player.stop_playback()
                    break
                    
            print("Playback completed")
            
        except FileNotFoundError:
            print(f"❌ File not found: {args.play}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    elif args.validate:
        print(f"Validating actions from {args.validate}...")
        
        try:
            recorder.load_from_file(args.validate)
            actions = recorder.get_actions()
            warnings = player.validate_actions(actions)
            
            if warnings:
                print(f"❌ Found {len(warnings)} issues:")
                for warning in warnings:
                    print(f"   {warning}")
            else:
                print("✅ All actions are valid!")
                
        except FileNotFoundError:
            print(f"❌ File not found: {args.validate}")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Mouse Automation Toolkit 🐭🤖",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Launch GUI
  %(prog)s --record actions.json    # Record actions to file
  %(prog)s --play actions.json      # Play actions from file
  %(prog)s --play actions.json --delay 0.5 --loop 3  # Play with custom settings
  %(prog)s --validate actions.json  # Validate actions file
  
Keyboard shortcuts (GUI):
  F9      Toggle recording
  F5      Start/stop playback
  Esc     Emergency stop
  Ctrl+N  New profile
  Ctrl+O  Open profile
  Ctrl+S  Save profile
        """
    )
    
    # Main action arguments
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--record", "-r",
        metavar="FILE",
        help="Record mouse actions to JSON file"
    )
    action_group.add_argument(
        "--play", "-p",
        metavar="FILE", 
        help="Play mouse actions from JSON file"
    )
    action_group.add_argument(
        "--validate", "-v",
        metavar="FILE",
        help="Validate actions in JSON file"
    )
    
    # Playback options
    parser.add_argument(
        "--delay", "-d",
        type=float,
        metavar="MULTIPLIER",
        help="Delay multiplier for playback (default: 1.0)"
    )
    parser.add_argument(
        "--loop", "-l", 
        type=int,
        metavar="COUNT",
        help="Number of times to loop playback (default: 1)"
    )
    
    # Transform options
    parser.add_argument(
        "--translate",
        metavar="X,Y",
        help="Translate coordinates by X,Y offset"
    )
    parser.add_argument(
        "--scale",
        metavar="X,Y", 
        help="Scale coordinates by X,Y factors"
    )
    parser.add_argument(
        "--rotate",
        metavar="DEGREES",
        help="Rotate coordinates by degrees"
    )
    
    # Other options
    parser.add_argument(
        "--log-level",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Set logging level"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Mouse Automation Toolkit 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = getattr(logging, args.log_level.upper())
    setup_logging(log_level)
    
    # Run appropriate mode
    if args.record or args.play or args.validate:
        run_cli(args)
    else:
        run_gui()


if __name__ == "__main__":
    main()