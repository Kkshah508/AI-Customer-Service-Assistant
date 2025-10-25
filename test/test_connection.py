import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Backend Integration...")
print("=" * 60)

try:
    print("\n1. Testing imports...")
    from src.main_assistant import HealthcareAssistant
    from src.utils import validate_user_input
    print("   ✓ Imports successful")
    
    print("\n2. Initializing Healthcare Assistant...")
    assistant = HealthcareAssistant()
    print("   ✓ Assistant initialized")
    
    print("\n3. Testing message processing...")
    test_message = "Hello, I need help with my order"
    response = assistant.process_message(
        user_id="test_user",
        message=test_message
    )
    print(f"   ✓ Response received: {response.get('message', '')[:50]}...")
    
    print("\n4. Testing validation...")
    validation = validate_user_input(test_message)
    print(f"   ✓ Validation result: {validation.get('is_valid')}")
    
    print("\n5. Testing system stats...")
    stats = assistant.get_system_stats()
    print(f"   ✓ Stats retrieved: {stats.get('system_health')}")
    
    print("\n" + "=" * 60)
    print("✓ All backend components are working correctly!")
    print("=" * 60)
    print("\nYou can now start the Flask API server:")
    print("  python start_backend.py")
    print("\nOr start everything at once:")
    print("  START_APP.bat")
    
except Exception as e:
    print(f"\n✗ Error during testing: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
