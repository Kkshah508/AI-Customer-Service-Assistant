import requests
import time
import json

API_BASE = "http://localhost:5000"

def test_health():
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"  Response: {response.json()}")
            return True
        else:
            print("✗ Health check failed")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_initialize():
    print("\nTesting initialization...")
    try:
        response = requests.get(f"{API_BASE}/api/initialize")
        if response.status_code == 200:
            data = response.json()
            print("✓ Initialization successful")
            print(f"  Status: {data.get('status')}")
            print(f"  Capabilities: {data.get('capabilities')}")
            return True
        else:
            print("✗ Initialization failed")
            return False
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False

def test_message_processing():
    print("\nTesting message processing...")
    test_messages = [
        "I need help with my account",
        "Where is my order?",
        "I want to return an item",
        "The app is not working"
    ]
    
    for msg in test_messages:
        try:
            response = requests.post(
                f"{API_BASE}/api/process",
                json={
                    "user_id": "test_user",
                    "message": msg
                }
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Message: '{msg}'")
                print(f"  Response: {data.get('message')[:80]}...")
                if 'metadata' in data:
                    print(f"  Intent: {data['metadata'].get('intent')}")
            else:
                print(f"✗ Failed for: '{msg}'")
        except Exception as e:
            print(f"✗ Error processing '{msg}': {e}")
        time.sleep(0.5)
    
    return True

def test_capabilities():
    print("\nTesting capabilities endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/capabilities")
        if response.status_code == 200:
            data = response.json()
            print("✓ Capabilities retrieved")
            for key, value in data.get('capabilities', {}).items():
                status = "✓" if value else "✗"
                print(f"  {status} {key}: {value}")
            return True
        else:
            print("✗ Capabilities check failed")
            return False
    except Exception as e:
        print(f"✗ Capabilities error: {e}")
        return False

def test_intents():
    print("\nTesting intents endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/intents")
        if response.status_code == 200:
            data = response.json()
            intents = data.get('intents', [])
            print(f"✓ Found {len(intents)} intents")
            for intent in intents:
                print(f"  - {intent}")
            return True
        else:
            print("✗ Intents check failed")
            return False
    except Exception as e:
        print(f"✗ Intents error: {e}")
        return False

def test_conversation_reset():
    print("\nTesting conversation reset...")
    try:
        response = requests.post(
            f"{API_BASE}/api/reset",
            json={"user_id": "test_user"}
        )
        if response.status_code == 200:
            print("✓ Conversation reset successful")
            return True
        else:
            print("✗ Conversation reset failed")
            return False
    except Exception as e:
        print(f"✗ Reset error: {e}")
        return False

def main():
    print("="*60)
    print("AI Customer Service Assistant - Full System Test")
    print("="*60)
    print("\nMake sure the backend is running on http://localhost:5000")
    print("Start it with: python start_backend.py")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)
    
    tests = [
        test_health,
        test_initialize,
        test_capabilities,
        test_intents,
        test_message_processing,
        test_conversation_reset
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Tests Complete: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n✓ All systems operational!")
        print("\nNext steps:")
        print("1. Start the React frontend: cd frontend/react-app && npm start")
        print("2. Open browser to http://localhost:3000")
        print("3. Test the full UI with voice and text chat")
    else:
        print("\n✗ Some tests failed. Check the backend logs.")

if __name__ == "__main__":
    main()
