import sqlite3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    
    def __init__(self, db_path: str = "customer_service.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def initialize_database(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        logger.info(f"Database initialized at {self.db_path}")
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profile_data TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_intent TEXT,
                urgency_level TEXT DEFAULT 'low',
                escalation_triggered INTEGER DEFAULT 0,
                conversation_complete INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES conversations(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_context (
                session_id TEXT PRIMARY KEY,
                symptoms_mentioned TEXT,
                care_level_determined TEXT,
                follow_up_questions TEXT,
                user_profile TEXT,
                FOREIGN KEY (session_id) REFERENCES conversations(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_user 
            ON conversations(user_id)
        """)
        
        self.conn.commit()
    
    def create_user(self, user_id: str, profile_data: Dict = None):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, profile_data)
                VALUES (?, ?)
            """, (user_id, json.dumps(profile_data or {})))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating user: {e}")
    
    def update_user_activity(self, user_id: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET last_active = CURRENT_TIMESTAMP 
            WHERE user_id = ?
        """, (user_id,))
        self.conn.commit()
    
    def create_conversation(self, session_id: str, user_id: str, metadata: Dict = None):
        cursor = self.conn.cursor()
        self.create_user(user_id)
        
        try:
            cursor.execute("""
                INSERT INTO conversations 
                (session_id, user_id, metadata)
                VALUES (?, ?, ?)
            """, (session_id, user_id, json.dumps(metadata or {})))
            
            cursor.execute("""
                INSERT INTO conversation_context 
                (session_id, symptoms_mentioned, follow_up_questions, user_profile)
                VALUES (?, ?, ?, ?)
            """, (session_id, json.dumps([]), json.dumps([]), json.dumps({})))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
    
    def update_conversation(self, session_id: str, **kwargs):
        cursor = self.conn.cursor()
        
        valid_fields = ['current_intent', 'urgency_level', 'escalation_triggered', 
                       'conversation_complete', 'metadata']
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in valid_fields:
                if key == 'metadata':
                    value = json.dumps(value)
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            updates.append("last_updated = CURRENT_TIMESTAMP")
            values.append(session_id)
            
            query = f"UPDATE conversations SET {', '.join(updates)} WHERE session_id = ?"
            cursor.execute(query, values)
            self.conn.commit()
    
    def add_message(self, session_id: str, sender: str, message: str, metadata: Dict = None):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO messages (session_id, sender, message, metadata)
                VALUES (?, ?, ?, ?)
            """, (session_id, sender, message, json.dumps(metadata or {})))
            
            cursor.execute("""
                UPDATE conversations 
                SET last_updated = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            """, (session_id,))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error adding message: {e}")
    
    def get_messages(self, session_id: str, limit: int = None) -> List[Dict]:
        cursor = self.conn.cursor()
        
        query = """
            SELECT timestamp, sender, message, metadata 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'timestamp': row['timestamp'],
                'sender': row['sender'],
                'message': row['message'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {}
            })
        
        return messages
    
    def get_conversation(self, session_id: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversations WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'session_id': row['session_id'],
            'user_id': row['user_id'],
            'created_at': row['created_at'],
            'last_updated': row['last_updated'],
            'current_intent': row['current_intent'],
            'urgency_level': row['urgency_level'],
            'escalation_triggered': bool(row['escalation_triggered']),
            'conversation_complete': bool(row['conversation_complete']),
            'metadata': json.loads(row['metadata']) if row['metadata'] else {}
        }
    
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE user_id = ? 
            ORDER BY last_updated DESC 
            LIMIT ?
        """, (user_id, limit))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'session_id': row['session_id'],
                'created_at': row['created_at'],
                'last_updated': row['last_updated'],
                'current_intent': row['current_intent'],
                'urgency_level': row['urgency_level'],
                'conversation_complete': bool(row['conversation_complete'])
            })
        
        return conversations
    
    def update_context(self, session_id: str, **kwargs):
        cursor = self.conn.cursor()
        
        valid_fields = ['symptoms_mentioned', 'care_level_determined', 
                       'follow_up_questions', 'user_profile']
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in valid_fields:
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            values.append(session_id)
            query = f"UPDATE conversation_context SET {', '.join(updates)} WHERE session_id = ?"
            cursor.execute(query, values)
            self.conn.commit()
    
    def get_context(self, session_id: str) -> Dict:
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversation_context WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if not row:
            return {
                'symptoms_mentioned': [],
                'care_level_determined': None,
                'follow_up_questions': [],
                'user_profile': {}
            }
        
        return {
            'symptoms_mentioned': json.loads(row['symptoms_mentioned']) if row['symptoms_mentioned'] else [],
            'care_level_determined': row['care_level_determined'],
            'follow_up_questions': json.loads(row['follow_up_questions']) if row['follow_up_questions'] else [],
            'user_profile': json.loads(row['user_profile']) if row['user_profile'] else {}
        }
    
    def get_active_sessions(self) -> List[str]:
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT session_id FROM conversations 
            WHERE conversation_complete = 0 
            AND datetime(last_updated) > datetime('now', '-2 hours')
        """)
        
        return [row['session_id'] for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM conversations")
        total_conversations = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM messages")
        total_messages = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM conversations 
            WHERE conversation_complete = 0 
            AND datetime(last_updated) > datetime('now', '-2 hours')
        """)
        active_sessions = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM conversations 
            WHERE escalation_triggered = 1
        """)
        total_escalations = cursor.fetchone()['count']
        
        return {
            'total_users': total_users,
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'active_sessions': active_sessions,
            'total_escalations': total_escalations
        }
    
    def close(self):
        if self.conn:
            self.conn.close()
