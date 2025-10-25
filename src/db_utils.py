import sys
import os
from database import Database
from datetime import datetime

def view_stats():
    db = Database()
    stats = db.get_stats()
    
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"Total Users:          {stats['total_users']}")
    print(f"Total Conversations:  {stats['total_conversations']}")
    print(f"Total Messages:       {stats['total_messages']}")
    print(f"Active Sessions:      {stats['active_sessions']}")
    print(f"Total Escalations:    {stats['total_escalations']}")
    print("="*60 + "\n")
    
    db.close()

def view_user_conversations(user_id):
    db = Database()
    conversations = db.get_user_conversations(user_id, 100)
    
    print(f"\n{'='*60}")
    print(f"CONVERSATIONS FOR USER: {user_id}")
    print(f"{'='*60}")
    
    for conv in conversations:
        print(f"\nSession: {conv['session_id']}")
        print(f"  Created:  {conv['created_at']}")
        print(f"  Updated:  {conv['last_updated']}")
        print(f"  Intent:   {conv.get('current_intent', 'N/A')}")
        print(f"  Urgency:  {conv['urgency_level']}")
        print(f"  Complete: {'Yes' if conv['conversation_complete'] else 'No'}")
        
        messages = db.get_messages(conv['session_id'])
        print(f"  Messages: {len(messages)}")
    
    print(f"{'='*60}\n")
    db.close()

def view_conversation(session_id):
    db = Database()
    
    conv = db.get_conversation(session_id)
    if not conv:
        print(f"No conversation found with session_id: {session_id}")
        db.close()
        return
    
    print(f"\n{'='*60}")
    print(f"CONVERSATION: {session_id}")
    print(f"{'='*60}")
    print(f"User ID:      {conv['user_id']}")
    print(f"Created:      {conv['created_at']}")
    print(f"Last Updated: {conv['last_updated']}")
    print(f"Intent:       {conv.get('current_intent', 'N/A')}")
    print(f"Urgency:      {conv['urgency_level']}")
    print(f"Escalation:   {'Yes' if conv['escalation_triggered'] else 'No'}")
    print(f"Complete:     {'Yes' if conv['conversation_complete'] else 'No'}")
    
    context = db.get_context(session_id)
    if context.get('symptoms_mentioned'):
        print(f"Symptoms:     {', '.join(context['symptoms_mentioned'])}")
    
    messages = db.get_messages(session_id)
    print(f"\nMessages ({len(messages)}):")
    print("-"*60)
    
    for msg in messages:
        timestamp = msg['timestamp'].split('T')[1][:8] if 'T' in msg['timestamp'] else msg['timestamp']
        sender_label = msg['sender'].upper().ljust(10)
        print(f"[{timestamp}] {sender_label}: {msg['message']}")
    
    print("="*60 + "\n")
    db.close()

def clear_old_conversations(days=30):
    db = Database()
    cursor = db.conn.cursor()
    
    cursor.execute(f"""
        SELECT COUNT(*) as count FROM conversations 
        WHERE datetime(last_updated) < datetime('now', '-{days} days')
    """)
    count = cursor.fetchone()['count']
    
    if count == 0:
        print(f"No conversations older than {days} days found.")
        db.close()
        return
    
    response = input(f"Delete {count} conversations older than {days} days? (yes/no): ")
    if response.lower() == 'yes':
        cursor.execute(f"""
            DELETE FROM messages WHERE session_id IN (
                SELECT session_id FROM conversations 
                WHERE datetime(last_updated) < datetime('now', '-{days} days')
            )
        """)
        
        cursor.execute(f"""
            DELETE FROM conversation_context WHERE session_id IN (
                SELECT session_id FROM conversations 
                WHERE datetime(last_updated) < datetime('now', '-{days} days')
            )
        """)
        
        cursor.execute(f"""
            DELETE FROM conversations 
            WHERE datetime(last_updated) < datetime('now', '-{days} days')
        """)
        
        db.conn.commit()
        print(f"Deleted {count} old conversations.")
    else:
        print("Cancelled.")
    
    db.close()

def export_conversation_csv(session_id, output_file):
    db = Database()
    messages = db.get_messages(session_id)
    
    if not messages:
        print(f"No messages found for session: {session_id}")
        db.close()
        return
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("timestamp,sender,message\n")
        for msg in messages:
            message_text = msg['message'].replace('"', '""')
            f.write(f'"{msg["timestamp"]}","{msg["sender"]}","{message_text}"\n')
    
    print(f"Exported {len(messages)} messages to {output_file}")
    db.close()

def main():
    if len(sys.argv) < 2:
        print("\nDatabase Utilities")
        print("\nUsage:")
        print("  python db_utils.py stats")
        print("  python db_utils.py user <user_id>")
        print("  python db_utils.py conversation <session_id>")
        print("  python db_utils.py clean <days>")
        print("  python db_utils.py export <session_id> <output_file>")
        return
    
    command = sys.argv[1]
    
    if command == "stats":
        view_stats()
    elif command == "user" and len(sys.argv) > 2:
        view_user_conversations(sys.argv[2])
    elif command == "conversation" and len(sys.argv) > 2:
        view_conversation(sys.argv[2])
    elif command == "clean" and len(sys.argv) > 2:
        clear_old_conversations(int(sys.argv[2]))
    elif command == "export" and len(sys.argv) > 3:
        export_conversation_csv(sys.argv[2], sys.argv[3])
    else:
        print("Invalid command or missing arguments")

if __name__ == "__main__":
    main()
