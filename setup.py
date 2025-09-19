#!/usr/bin/env python3
"""
Setup script for Jarvis voice assistant.
Checks dependencies and provides installation guidance.
"""

import sys
import subprocess
import importlib
import platform


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True


def check_dependency(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is not installed")
        return False


def install_dependencies():
    """Install dependencies using pip."""
    print("\n🔧 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_audio_dependencies():
    """Check platform-specific audio dependencies."""
    system = platform.system().lower()
    
    print(f"\n🔊 Checking audio dependencies for {system}...")
    
    if system == "linux":
        print("ℹ️  On Linux, you may need to install:")
        print("   sudo apt-get install portaudio19-dev python3-pyaudio")
        print("   or")
        print("   sudo yum install portaudio-devel python3-pyaudio")
    elif system == "darwin":  # macOS
        print("ℹ️  On macOS, you may need to install:")
        print("   brew install portaudio")
    elif system == "windows":
        print("ℹ️  On Windows, PyAudio should install automatically")
    
    return True


def test_audio_availability():
    """Test if audio devices are available."""
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Check for input devices (microphones)
        input_devices = []
        output_devices = []
        
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info['name'])
            if device_info['maxOutputChannels'] > 0:
                output_devices.append(device_info['name'])
        
        p.terminate()
        
        if input_devices:
            print(f"✅ Found {len(input_devices)} input device(s)")
        else:
            print("⚠️  No input devices (microphones) found")
        
        if output_devices:
            print(f"✅ Found {len(output_devices)} output device(s)")
        else:
            print("⚠️  No output devices (speakers) found")
        
        return len(input_devices) > 0 and len(output_devices) > 0
        
    except Exception as e:
        print(f"⚠️  Could not test audio devices: {e}")
        return False


def main():
    """Main setup function."""
    print("🤖 Jarvis Voice Assistant Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    dependencies = [
        ("speechrecognition", "speech_recognition"),
        ("pyttsx3", "pyttsx3"),
        ("pyaudio", "pyaudio")
    ]
    
    missing_deps = []
    for package, import_name in dependencies:
        if not check_dependency(package, import_name):
            missing_deps.append(package)
    
    # Install missing dependencies
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        response = input("Would you like to install them now? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            if install_dependencies():
                print("\n✅ All dependencies installed!")
            else:
                print("\n❌ Failed to install some dependencies")
                sys.exit(1)
        else:
            print("\n⚠️  Please install dependencies manually before running Jarvis")
            sys.exit(1)
    else:
        print("\n✅ All required dependencies are installed!")
    
    # Check audio dependencies
    check_audio_dependencies()
    
    # Test audio devices
    print("\n🎤 Testing audio devices...")
    if test_audio_availability():
        print("✅ Audio system appears to be working!")
    else:
        print("⚠️  Audio system may not be properly configured")
        print("   You can still test Jarvis using: python test_jarvis.py")
    
    print("\n🚀 Setup complete! You can now run:")
    print("   python jarvis.py        # Full voice mode")
    print("   python test_jarvis.py   # Text mode for testing")


if __name__ == "__main__":
    main()