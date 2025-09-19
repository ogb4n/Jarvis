#!/usr/bin/env python3
"""
Script simple pour contrôler le mode conversation de Jarvis
Usage: 
  python jarvis_control.py start    # Démarrer l'écoute
  python jarvis_control.py stop     # Arrêter l'écoute  
  python jarvis_control.py status   # Voir le statut
  python jarvis_control.py test     # Tester les commandes
"""

import sys
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """Call Jarvis API endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, data=data or {})
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Jarvis server at {BASE_URL}")
        print("Make sure the server is running with: python -m jarvis.core.app")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def start_conversation():
    """Start conversation mode"""
    print("🚀 Starting conversation mode...")
    result = call_api("/api/conversation/start", "POST")
    
    if result and result.get("success"):
        print("✅ Conversation mode started!")
        print(f"📢 Wake phrases: {', '.join(result.get('wake_phrases', []))}")
        print("🎤 Say 'Hey Jarvis' to activate voice commands")
        
        # Show status
        show_status()
        
        print("\n💡 Tips:")
        print("- Say 'Hey Jarvis' to wake up the assistant")
        print("- Try commands like: 'bonjour', 'quelle heure est-il', 'aide'")
        print("- Use Ctrl+C in the server terminal to stop")
        
    else:
        print("❌ Failed to start conversation mode")

def stop_conversation():
    """Stop conversation mode"""
    print("🛑 Stopping conversation mode...")
    result = call_api("/api/conversation/stop", "POST")
    
    if result and result.get("success"):
        print("✅ Conversation mode stopped")
    else:
        print("❌ Failed to stop conversation mode")

def show_status():
    """Show current status"""
    print("📊 Getting system status...")
    result = call_api("/api/conversation/status")
    
    if result:
        print("\n🤖 Jarvis Status:")
        print(f"  Conversation Manager: {result.get('conversation_manager', {}).get('active', 'Unknown')}")
        print(f"  Wake Word Detector: {result.get('wake_word_detector', {}).get('state', 'Unknown')}")
        
        # Show additional details
        wwd_status = result.get('wake_word_detector', {})
        if wwd_status.get('is_running'):
            print(f"  🎤 Listening: {wwd_status.get('is_running', False)}")
            print(f"  🔊 Current State: {wwd_status.get('state', 'Unknown')}")
        
    else:
        print("❌ Could not get status")

def test_commands():
    """Test built-in commands"""
    print("🧪 Testing built-in commands...")
    
    # Check if conversation mode is running
    status_result = call_api("/api/conversation/status")
    if not status_result or not status_result.get('wake_word_detector', {}).get('is_running'):
        print("⚠️  Conversation mode is not running")
        print("Starting conversation mode first...")
        start_conversation()
        time.sleep(1)
    
    # Test commands
    test_commands_list = [
        "bonjour",
        "comment vas-tu", 
        "quelle heure est-il",
        "aide"
    ]
    
    print("\n🎯 Testing commands:")
    for cmd in test_commands_list:
        print(f"\n📤 Sending: '{cmd}'")
        result = call_api("/api/conversation/send-command", "POST", {"command": cmd})
        
        if result and result.get("success"):
            print(f"✅ Command processed successfully")
        else:
            print(f"❌ Command failed")
        
        time.sleep(0.5)
    
    # Show history
    print("\n📜 Conversation history:")
    history_result = call_api("/api/conversation/history")
    if history_result and history_result.get("success"):
        history = history_result.get("history", [])
        if history:
            for i, msg in enumerate(history[-5:], 1):  # Show last 5 messages
                print(f"  {i}. {msg.get('role', '?')}: {msg.get('content', '')}")
        else:
            print("  No conversation history")

def main():
    if len(sys.argv) != 2:
        print("Usage: python jarvis_control.py {start|stop|status|test}")
        print()
        print("Commands:")
        print("  start  - Start conversation mode with wake word detection")
        print("  stop   - Stop conversation mode") 
        print("  status - Show current system status")
        print("  test   - Test built-in commands")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    print(f"🤖 Jarvis Control - {command.upper()}")
    print(f"Server: {BASE_URL}")
    print("-" * 40)
    
    if command == "start":
        start_conversation()
    elif command == "stop":
        stop_conversation()
    elif command == "status":
        show_status()
    elif command == "test":
        test_commands()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: start, stop, status, test")
        sys.exit(1)

if __name__ == "__main__":
    main()