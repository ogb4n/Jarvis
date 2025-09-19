# Jarvis - Voice Recognition Service
Ever seen IronMan? This is your personal voice assistant inspired by Tony Stark's AI companion.

Jarvis is a voice recognition service that listens to your commands and responds with voice output, just like the AI assistant from the Iron Man movies.

## Features

- **Voice Recognition**: Listens to your voice commands using your microphone
- **Voice Response**: Responds back with synthesized speech
- **Basic Commands**: Supports greetings, time/date queries, and help
- **Extensible**: Easy to add new commands and features

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ogb4n/Jarvis.git
cd Jarvis
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

**Note**: You may need to install additional system dependencies for audio support:
- On Ubuntu/Debian: `sudo apt-get install portaudio19-dev python3-pyaudio`
- On macOS: `brew install portaudio`
- On Windows: PyAudio should install automatically

## Usage

### Quick Start

The easiest way to run Jarvis is using the launcher script:

```bash
# Run setup first (checks dependencies)
python launch.py --setup

# See a demonstration of all features
python demo.py

# Run Jarvis in voice mode
python launch.py

# Run Jarvis in test mode (no audio required)
python launch.py --test
```

### Manual Usage

You can also run Jarvis directly:

```bash
# Full voice mode
python jarvis.py

# Test mode (text input/output)
python test_jarvis.py

# Setup and dependency check
python setup.py
```

### Supported Commands

- **Greetings**: "Hello", "Hi", "Hey Jarvis"
- **Time**: "What time is it?", "Tell me the time"
- **Date**: "What's the date?", "What day is today?"
- **Help**: "Help me", "What can you do?"
- **Exit**: "Goodbye", "Exit", "Stop", "Quit"
- **Weather**: "What's the weather?" (placeholder for future implementation)

## How It Works

1. **Speech Recognition**: Uses Google's speech recognition service to convert your voice to text
2. **Command Processing**: Analyzes the recognized text to understand your intent
3. **Text-to-Speech**: Converts the response to speech using the system's TTS engine
4. **Continuous Loop**: Keeps listening for new commands until you say goodbye

## Requirements

- Python 3.6+
- Working microphone
- Internet connection (for speech recognition)
- Speakers or headphones for voice output

## Future Enhancements

- Weather integration with real weather APIs
- Smart home device control
- Calendar and reminder features
- Custom wake word detection
- Offline speech recognition options
