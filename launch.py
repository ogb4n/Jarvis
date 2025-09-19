#!/usr/bin/env python3
"""
Launcher script for Jarvis voice assistant.
Provides different modes and handles common issues.
"""

import sys
import subprocess
import argparse


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import speech_recognition
        import pyttsx3
        import pyaudio
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n🔧 To install dependencies, run:")
        print("   python setup.py")
        print("   or")
        print("   pip install -r requirements.txt")
        return False


def run_setup():
    """Run the setup script."""
    try:
        subprocess.run([sys.executable, "setup.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Setup failed. Please check the error messages above.")
        sys.exit(1)


def run_jarvis():
    """Run Jarvis in full voice mode."""
    if not check_dependencies():
        response = input("\nWould you like to run setup now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            run_setup()
        else:
            sys.exit(1)
    
    try:
        subprocess.run([sys.executable, "jarvis.py"], check=True)
    except subprocess.CalledProcessError:
        print("\n❌ Jarvis encountered an error.")
        print("💡 Try running in test mode: python launch.py --test")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


def run_test_mode():
    """Run Jarvis in test mode (no audio required)."""
    try:
        subprocess.run([sys.executable, "test_jarvis.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Test mode failed.")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Jarvis Voice Assistant Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py              # Run Jarvis in voice mode
  python launch.py --test       # Run in test mode (no audio)
  python launch.py --setup      # Run setup to install dependencies
        """
    )
    
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run in test mode (text input/output, no audio required)"
    )
    
    parser.add_argument(
        "--setup", 
        action="store_true", 
        help="Run setup to check and install dependencies"
    )
    
    args = parser.parse_args()
    
    print("🤖 Jarvis Voice Assistant Launcher")
    print("=" * 40)
    
    if args.setup:
        run_setup()
    elif args.test:
        print("🔧 Starting Jarvis in test mode...")
        run_test_mode()
    else:
        print("🎤 Starting Jarvis in voice mode...")
        run_jarvis()


if __name__ == "__main__":
    main()