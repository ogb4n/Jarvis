#!/usr/bin/env python3
"""
Test script for Jarvis voice assistant - Text mode for testing without audio hardware.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockJarvis:
    """Mock version of Jarvis for testing without audio hardware."""
    
    def __init__(self):
        """Initialize mock Jarvis."""
        self.is_listening = False
        print("Mock Jarvis initialized - Text mode for testing")
    
    def speak(self, text):
        """Mock speech output - just prints the text."""
        print(f"Jarvis: {text}")
    
    def listen(self):
        """Mock listen - gets input from keyboard."""
        try:
            text = input("You: ").strip()
            return text.lower() if text else None
        except (EOFError, KeyboardInterrupt):
            return "quit"
    
    def process_command(self, command):
        """Process voice commands and generate appropriate responses."""
        if not command:
            return True
        
        import datetime
        
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
        """Start the main interaction loop."""
        self.is_listening = True
        self.speak("Hello! I'm Jarvis in test mode. Type your commands (or 'quit' to exit):")
        
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
    """Main function to run mock Jarvis."""
    print("Running Jarvis in test mode (no audio required)")
    print("=" * 50)
    
    try:
        mock_jarvis = MockJarvis()
        mock_jarvis.start_listening()
    except Exception as e:
        print(f"Failed to initialize mock Jarvis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()