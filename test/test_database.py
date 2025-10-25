import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import Database

print("Testing Database Integration...")
print("=" * 60)

db = Database("test_database.db")

print("\n1. Testing user creation...")
db.create_user("test_user_123", {"name": "Test User"})
print("   [OK] User created")

print("\n2. Testing conversation creation...")
db.create_conversation("session_test_123", "test_user_123")
print("   [OK] Conversation created")

print("\n3. Testing message storage...")
db.add_message("session_test_123", "user", "Hello, I need help")
db.add_message("session_test_123", "assistant", "I'm here to help!")
print("   [OK] Messages added")

print("\n4. Testing conversation update...")
db.update_conversation("session_test_123", 
                      current_intent="general_inquiry",
                      urgency_level="low")
print("   [OK] Conversation updated")

print("\n5. Testing context storage...")
db.update_context("session_test_123",
                 symptoms_mentioned=["headache"],
                 user_profile={"age": 25})
print("   [OK] Context updated")

print("\n6. Retrieving conversation...")
conv = db.get_conversation("session_test_123")
print(f"   [OK] Retrieved conversation: {conv['session_id']}")
print(f"      User: {conv['user_id']}")
print(f"      Intent: {conv['current_intent']}")

print("\n7. Retrieving messages...")
messages = db.get_messages("session_test_123")
print(f"   [OK] Retrieved {len(messages)} messages")
for msg in messages:
    print(f"      [{msg['sender']}]: {msg['message']}")

print("\n8. Retrieving context...")
context = db.get_context("session_test_123")
print(f"   [OK] Context retrieved")
print(f"      Symptoms: {context['symptoms_mentioned']}")
print(f"      Profile: {context['user_profile']}")

print("\n9. Getting statistics...")
stats = db.get_stats()
print(f"   [OK] Statistics retrieved")
print(f"      Total Users: {stats['total_users']}")
print(f"      Total Conversations: {stats['total_conversations']}")
print(f"      Total Messages: {stats['total_messages']}")

print("\n" + "=" * 60)
print("[SUCCESS] All database tests passed successfully!")
print("=" * 60)

db.close()

if os.path.exists("test_database.db"):
    os.remove("test_database.db")
    print("\nCleaned up test database file")
