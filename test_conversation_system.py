#!/usr/bin/env python3
"""
Script de test pour le système de wake word de Jarvis
Usage: python test_jarvis_conversation.py
"""

import time
import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_separator(title: str):
    """Print a nice separator with title"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_api_endpoint(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test an API endpoint and return the response"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"Testing {method} {endpoint}")
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if data:
                response = requests.post(url, data=data)
            else:
                response = requests.post(url)
        else:
            print(f"Unsupported method: {method}")
            return {"error": f"Unsupported method: {method}"}
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("Make sure Jarvis server is running on port 8000")
        return {"error": "Connection failed"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

def main():
    """Main test sequence"""
    print("🤖 Testing Jarvis Conversation System")
    print(f"Server URL: {BASE_URL}")
    
    # Test 1: Health check
    print_separator("1. Health Check")
    health = test_api_endpoint("/health")
    if "error" in health:
        print("❌ Server not available - stopping tests")
        sys.exit(1)
    
    # Test 2: Audio system test
    print_separator("2. Audio System Test")
    audio_test = test_api_endpoint("/api/audio/test")
    
    # Test 3: Get conversation status (before starting)
    print_separator("3. Initial Conversation Status")
    status = test_api_endpoint("/api/conversation/status")
    
    # Test 4: Test built-in responses
    print_separator("4. Built-in Responses Test")
    responses = test_api_endpoint("/api/conversation/test-responses")
    
    # Test 5: Start conversation mode
    print_separator("5. Starting Conversation Mode")
    start_result = test_api_endpoint("/api/conversation/start", "POST")
    
    if start_result.get("success"):
        print("✅ Conversation mode started successfully!")
        
        # Wait a moment
        print("\nWaiting 2 seconds...")
        time.sleep(2)
        
        # Test 6: Get status after starting
        print_separator("6. Conversation Status After Start")
        status_after = test_api_endpoint("/api/conversation/status")
        
        # Test 7: Simulate wake word
        print_separator("7. Simulating Wake Word")
        wake_sim = test_api_endpoint("/api/conversation/simulate-wake", "POST")
        
        # Test 8: Send text command
        print_separator("8. Sending Text Command")
        command_data = {"command": "bonjour jarvis"}
        command_result = test_api_endpoint("/api/conversation/send-command", "POST", command_data)
        
        # Test 9: Get conversation history
        print_separator("9. Conversation History")
        history = test_api_endpoint("/api/conversation/history")
        
        # Test 10: Update wake words
        print_separator("10. Updating Wake Words")
        wake_words_data = {
            "wake_phrases": ["hey jarvis", "salut jarvis", "écoute jarvis", "jarvis"]
        }
        update_result = test_api_endpoint("/api/conversation/config/wake-words", "POST", wake_words_data)
        
        # Test 11: Update sensitivity
        print_separator("11. Updating Sensitivity")
        sensitivity_data = {
            "sensitivity": "0.8",
            "min_confidence": "0.7",
            "timeout_seconds": "6.0"
        }
        sensitivity_result = test_api_endpoint("/api/conversation/config/sensitivity", "POST", sensitivity_data)
        
        # Wait a bit before stopping
        print("\nLetting the system run for 3 seconds...")
        time.sleep(3)
        
        # Test 12: Stop conversation mode
        print_separator("12. Stopping Conversation Mode")
        stop_result = test_api_endpoint("/api/conversation/stop", "POST")
        
        if stop_result.get("success"):
            print("✅ Conversation mode stopped successfully!")
        
    else:
        print("❌ Failed to start conversation mode")
    
    # Final status
    print_separator("13. Final Status Check")
    final_status = test_api_endpoint("/api/conversation/status")
    
    print_separator("Test Summary")
    print("🎉 All tests completed!")
    print("📝 Check the outputs above for any errors")
    print("🔊 If you want to test voice recognition:")
    print("   1. Start conversation mode: POST /api/conversation/start")
    print("   2. Say 'Hey Jarvis' near your microphone")
    print("   3. Give a voice command")
    print("   4. Check history: GET /api/conversation/history")

if __name__ == "__main__":
    main()