#!/usr/bin/env python3
"""
Jarvis - Voice Recognition Service
A voice assistant that listens to user commands and responds with voice.
"""

import speech_recognition as sr
import pyttsx3
import datetime
import threading
import sys


class Jarvis:
    def __init__(self):
        """Initialize Jarvis voice assistant."""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.tts_engine = pyttsx3.init()
            self.is_listening = False
            
            # Configure text-to-speech settings
            self.setup_voice()
            
            # Adjust for ambient noise
            print("Adjusting for ambient noise... Please wait.")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            print("Ready to listen!")
            
        except Exception as e:
            print(f"❌ Failed to initialize Jarvis: {e}")
            print("\n💡 Troubleshooting tips:")
            print("   • Make sure your microphone is connected")
            print("   • Check that no other applications are using the microphone")
            print("   • Try running: python launch.py --test (for text mode)")
            print("   • Run: python setup.py (to check dependencies)")
            raise
    
    def setup_voice(self):
        """Configure the text-to-speech voice settings."""
        voices = self.tts_engine.getProperty('voices')
        # Try to use a male voice if available
        for voice in voices:
            if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 180)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
    
    def speak(self, text):
        """Convert text to speech."""
        print(f"Jarvis: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """Listen for voice input and return recognized text."""
        try:
            with self.microphone as source:
                print("Listening...")
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Recognizing...")
            # Use Google's speech recognition service
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
    
    def process_command(self, command):
        """Process voice commands and generate appropriate responses."""
        if not command:
            return
        
        # Greeting commands
        if any(word in command for word in ['hello', 'hi', 'hey', 'jarvis']):
            responses = [
                "Hello! How can I assist you today?",
                "Good day! What can I do for you?",
                "Greetings! I'm here to help.",
                "Hello there! Ready to assist."
            ]
            import random
            self.speak(random.choice(responses))
        
        # Time command
        elif any(word in command for word in ['time', 'clock']):
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
        
        # Date command
        elif any(word in command for word in ['date', 'today']):
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
        
        # Exit commands
        elif any(word in command for word in ['exit', 'quit', 'goodbye', 'bye', 'stop']):
            self.speak("Goodbye! Have a great day!")
            self.is_listening = False
            return False
        
        # Weather placeholder (can be extended with actual weather API)
        elif 'weather' in command:
            self.speak("I would check the weather for you, but I need to be connected to a weather service first.")
        
        # Help command
        elif 'help' in command:
            help_text = (
                "I can help you with the following commands: "
                "Ask for the time, date, say hello, ask about weather, or say goodbye to exit."
            )
            self.speak(help_text)
        
        # Default response for unrecognized commands
        else:
            responses = [
                "I'm sorry, I didn't understand that command.",
                "Could you please repeat that?",
                "I'm not sure how to help with that.",
                "Can you try asking in a different way?"
            ]
            import random
            self.speak(random.choice(responses))
        
        return True
    
    def start_listening(self):
        """Start the main voice recognition loop."""
        self.is_listening = True
        self.speak("Hello! I'm Jarvis, your voice assistant. How can I help you today?")
        
        while self.is_listening:
            try:
                command = self.listen()
                if command:
                    continue_listening = self.process_command(command)
                    if not continue_listening:
                        break
                        
            except KeyboardInterrupt:
                print("\nShutting down...")
                self.speak("Shutting down. Goodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                self.speak("I encountered an error. Let me try again.")


def main():
    """Main function to run Jarvis."""
    try:
        jarvis = Jarvis()
        jarvis.start_listening()
    except Exception as e:
        print(f"Failed to initialize Jarvis: {e}")
        print("Make sure you have a microphone connected and the required dependencies installed.")
        sys.exit(1)


if __name__ == "__main__":
    main()