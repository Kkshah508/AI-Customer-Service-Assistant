"""
Dialogue Management System

Manages conversation state, context, and determines next actions
for the healthcare assistant.
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ConversationState:
    """Represents the state of a single conversation."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = f"session_{user_id}_{int(time.time())}"
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
        # Conversation context
        self.messages = []
        self.current_intent = None
        self.current_sentiment = {}
        self.user_profile = {}
        
        # Healthcare specific context
        self.symptoms_mentioned = []
        self.care_level_determined = None
        self.urgency_level = "low"
        self.follow_up_questions = []
        self.escalation_triggered = False
        
        # State flags
        self.awaiting_user_response = False
        self.conversation_complete = False
        self.human_handoff_requested = False
    
    def add_message(self, message: str, sender: str, metadata: Dict = None):
        """Add a message to the conversation history."""
        msg = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "message": message,
            "metadata": metadata or {}
        }
        self.messages.append(msg)
        self.last_updated = datetime.now()
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation context."""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "current_intent": self.current_intent,
            "symptoms": self.symptoms_mentioned,
            "care_level": self.care_level_determined,
            "urgency": self.urgency_level,
            "escalation_needed": self.escalation_triggered,
            "duration_minutes": (datetime.now() - self.created_at).total_seconds() / 60
        }


class DialogueManager:
    """
    Manages conversation flow, context, and determines next actions
    for the healthcare assistant.
    """
    
    def __init__(self):
        """Initialize the dialogue manager."""
        self.active_sessions: Dict[str, ConversationState] = {}
        self.session_timeout = timedelta(hours=2)  # Session expires after 2 hours
        
        # Conversation flow rules
        self.flow_rules = {
            "greeting": ["symptom_triage", "appointment_booking", "general_inquiry"],
            "symptom_triage": ["follow_up_questions", "care_recommendation", "escalation"],
            "emergency": ["immediate_escalation"],
            "follow_up_questions": ["symptom_assessment", "care_recommendation"],
            "care_recommendation": ["appointment_booking", "self_care_guidance", "escalation"]
        }
        
        # State transitions
        self.state_transitions = {
            "new_conversation": "greeting",
            "greeting": "intent_processing",
            "intent_processing": "response_generation",
            "follow_up_needed": "follow_up_questions",
            "escalation_needed": "human_handoff",
            "care_complete": "conversation_end"
        }
    
    def start_conversation(self, user_id: str) -> ConversationState:
        """
        Initialize a new conversation session.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            ConversationState object
        """
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        # Create new conversation state
        state = ConversationState(user_id)
        self.active_sessions[user_id] = state
        
        logger.info(f"Started new conversation for user: {user_id}")
        return state
    
    def process_user_input(self, user_id: str, message: str, 
                          intent_result: Dict, sentiment_result: Dict) -> Dict[str, Any]:
        """
        Process user input and determine next action.
        
        Args:
            user_id: User identifier
            message: User's message
            intent_result: Results from intent classification
            sentiment_result: Results from sentiment analysis
            
        Returns:
            Dictionary with next action and context
        """
        # Get or create conversation state
        if user_id not in self.active_sessions:
            state = self.start_conversation(user_id)
        else:
            state = self.active_sessions[user_id]
        
        # Add user message to history
        state.add_message(message, "user", {
            "intent": intent_result,
            "sentiment": sentiment_result
        })
        
        # Update conversation context
        self.maintain_context(user_id, intent_result, sentiment_result)
        
        # Determine next action
        next_action = self.determine_next_action(user_id, intent_result, sentiment_result)
        
        logger.info(f"Processed input for {user_id}: intent={intent_result.get('intent')}, "
                   f"next_action={next_action['action']}")
        
        return next_action
    
    def maintain_context(self, user_id: str, intent_result: Dict, sentiment_result: Dict):
        """
        Maintain and update conversation context.
        
        Args:
            user_id: User identifier
            intent_result: Intent classification results
            sentiment_result: Sentiment analysis results
        """
        state = self.active_sessions[user_id]
        
        # Update current intent and sentiment
        state.current_intent = intent_result.get("intent")
        state.current_sentiment = sentiment_result
        
        # Update urgency level
        if sentiment_result.get("urgency_level", "low") > state.urgency_level:
            state.urgency_level = sentiment_result["urgency_level"]
        
        # Check for escalation triggers
        if sentiment_result.get("urgency_level") == "critical" or \
           intent_result.get("intent") == "emergency":
            state.escalation_triggered = True
        
        # Update user profile with preferences/information
        self._update_user_profile(state, intent_result, sentiment_result)
    
    def determine_next_action(self, user_id: str, intent_result: Dict, 
                            sentiment_result: Dict) -> Dict[str, Any]:
        """
        Determine the next action based on conversation state and input.
        
        Args:
            user_id: User identifier
            intent_result: Intent classification results
            sentiment_result: Sentiment analysis results
            
        Returns:
            Dictionary describing the next action
        """
        state = self.active_sessions[user_id]
        intent = intent_result.get("intent", "general_inquiry")
        urgency = sentiment_result.get("urgency_level", "low")
        
        # Emergency handling - highest priority
        if intent == "emergency" or urgency == "critical":
            return {
                "action": "emergency_response",
                "priority": "critical",
                "escalate": True,
                "response_type": "emergency",
                "context": state.get_context_summary()
            }
        
        # High urgency - needs prompt handling
        if urgency == "high" or state.escalation_triggered:
            return {
                "action": "urgent_response", 
                "priority": "high",
                "escalate": True,
                "response_type": "urgent",
                "context": state.get_context_summary()
            }
        
        # Symptom triage workflow
        if intent == "symptom_triage":
            if len(state.messages) == 1:  # First symptom report
                return {
                    "action": "symptom_assessment",
                    "priority": "medium",
                    "escalate": False,
                    "response_type": "assessment",
                    "need_follow_up": True,
                    "context": state.get_context_summary()
                }
            else:  # Follow-up interaction
                return {
                    "action": "care_recommendation",
                    "priority": "medium", 
                    "escalate": False,
                    "response_type": "recommendation",
                    "context": state.get_context_summary()
                }
        
        # Appointment booking
        if intent == "appointment_booking":
            return {
                "action": "appointment_assistance",
                "priority": "low",
                "escalate": False,
                "response_type": "booking",
                "context": state.get_context_summary()
            }
        
        # Medication information
        if intent == "medication_info":
            return {
                "action": "medication_guidance",
                "priority": "medium",
                "escalate": False,
                "response_type": "information",
                "context": state.get_context_summary()
            }
        
        # General inquiry
        return {
            "action": "general_response",
            "priority": "low",
            "escalate": False,
            "response_type": "information",
            "context": state.get_context_summary()
        }
    
    def add_assistant_response(self, user_id: str, response: str, metadata: Dict = None):
        """
        Add assistant response to conversation history.
        
        Args:
            user_id: User identifier
            response: Assistant's response
            metadata: Additional response metadata
        """
        if user_id in self.active_sessions:
            state = self.active_sessions[user_id]
            state.add_message(response, "assistant", metadata)
    
    def set_follow_up_questions(self, user_id: str, questions: List[str]):
        """
        Set follow-up questions for the conversation.
        
        Args:
            user_id: User identifier
            questions: List of follow-up questions
        """
        if user_id in self.active_sessions:
            state = self.active_sessions[user_id]
            state.follow_up_questions = questions
            state.awaiting_user_response = True
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        if user_id not in self.active_sessions:
            return []
        
        state = self.active_sessions[user_id]
        return state.messages[-limit:] if limit else state.messages
    
    def get_conversation_state(self, user_id: str) -> Optional[ConversationState]:
        """Get the conversation state for a user."""
        return self.active_sessions.get(user_id)
    
    def end_conversation(self, user_id: str, reason: str = "completed"):
        """
        End a conversation session.
        
        Args:
            user_id: User identifier
            reason: Reason for ending conversation
        """
        if user_id in self.active_sessions:
            state = self.active_sessions[user_id]
            state.conversation_complete = True
            state.add_message(f"Conversation ended: {reason}", "system")
            
            # Optionally remove from active sessions or archive
            # For now, we'll keep it for potential follow-up
            logger.info(f"Ended conversation for {user_id}: {reason}")
    
    def reset_conversation(self, user_id: str) -> ConversationState:
        """
        Reset conversation state for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            New ConversationState object
        """
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
        
        return self.start_conversation(user_id)
    
    def _update_user_profile(self, state: ConversationState, 
                           intent_result: Dict, sentiment_result: Dict):
        """Update user profile with conversation insights."""
        # Track symptom mentions
        if intent_result.get("intent") == "symptom_triage":
            last_message = state.messages[-1]["message"]
            # Simple keyword extraction for symptoms
            symptom_keywords = ["fever", "pain", "cough", "headache", "nausea", "rash"]
            for symptom in symptom_keywords:
                if symptom in last_message.lower() and symptom not in state.symptoms_mentioned:
                    state.symptoms_mentioned.append(symptom)
        
        # Track emotional state patterns
        emotion = sentiment_result.get("emotional_state")
        if emotion and emotion not in state.user_profile.get("emotions_expressed", []):
            if "emotions_expressed" not in state.user_profile:
                state.user_profile["emotions_expressed"] = []
            state.user_profile["emotions_expressed"].append(emotion)
    
    def _cleanup_expired_sessions(self):
        """Remove expired conversation sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for user_id, state in self.active_sessions.items():
            if current_time - state.last_updated > self.session_timeout:
                expired_sessions.append(user_id)
        
        for user_id in expired_sessions:
            del self.active_sessions[user_id]
            logger.info(f"Cleaned up expired session for user: {user_id}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "active_sessions": len(self.active_sessions),
            "total_messages": sum(len(state.messages) for state in self.active_sessions.values()),
            "escalations_triggered": sum(1 for state in self.active_sessions.values() 
                                       if state.escalation_triggered),
            "emergency_conversations": sum(1 for state in self.active_sessions.values() 
                                         if state.urgency_level == "critical")
        }
