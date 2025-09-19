#!/usr/bin/env python3
"""
Demonstration script for Jarvis voice assistant.
Shows all available commands and capabilities.
"""

import time
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_jarvis import MockJarvis


def demo_conversation():
    """Run a demonstration conversation with Jarvis."""
    print("🎬 Jarvis Demonstration")
    print("=" * 50)
    print("This demo shows all the capabilities of Jarvis.")
    print("In real usage, you would speak these commands.\n")
    
    # Create mock Jarvis instance
    jarvis = MockJarvis()
    jarvis.speak("Hello! Let me demonstrate my capabilities.")
    
    # List of commands to demonstrate
    demo_commands = [
        ("Greeting", "hello jarvis"),
        ("Time Query", "what time is it"),
        ("Date Query", "what's the date today"),
        ("Weather (placeholder)", "what's the weather"),
        ("Help", "help"),
        ("Unknown Command", "play music"),
        ("Goodbye", "goodbye")
    ]
    
    print("\n🎤 Starting demonstration...\n")
    
    for i, (description, command) in enumerate(demo_commands, 1):
        print(f"Demo {i}: {description}")
        print(f"Command: \"{command}\"")
        
        # Process the command
        result = jarvis.process_command(command)
        
        print("-" * 30)
        
        # Small pause between commands
        time.sleep(1)
        
        # Break if goodbye was processed
        if not result:
            break
    
    print("\n✨ Demonstration complete!")
    print("\nTo try Jarvis yourself:")
    print("  • Text mode: python launch.py --test")
    print("  • Voice mode: python launch.py (requires microphone)")


def main():
    """Main demonstration function."""
    try:
        demo_conversation()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()