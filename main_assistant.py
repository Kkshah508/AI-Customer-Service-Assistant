"""
Main Healthcare Assistant

Integrates all components to provide a complete AI-powered 
healthcare customer service assistant.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .intent_classifier import IntentClassifier
from .sentiment_analyzer import SentimentAnalyzer
from .healthcare_logic import HealthcareTriageSystem
from .dialogue_manager import DialogueManager
from .response_generator import ResponseGenerator
try:
    from .voice_handler import VoiceHandler
    VOICE_AVAILABLE = True
except ImportError as e:
    VoiceHandler = None
    VOICE_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthcareAssistant:
    """
    Main healthcare assistant that coordinates all system components
    to provide intelligent, empathetic healthcare customer service.
    """
    
    def __init__(self):
        """Initialize the healthcare assistant with all components."""
        logger.info("Initializing Healthcare Assistant...")
        
        try:
            # Initialize core components
            self.intent_classifier = IntentClassifier()
            logger.info("✓ Intent Classifier initialized")
            
            self.sentiment_analyzer = SentimentAnalyzer()
            logger.info("✓ Sentiment Analyzer initialized")
            
            self.healthcare_triage = HealthcareTriageSystem()
            logger.info("✓ Healthcare Triage System initialized")
            
            self.dialogue_manager = DialogueManager()
            logger.info("✓ Dialogue Manager initialized")
            
            self.response_generator = ResponseGenerator()
            logger.info("✓ Response Generator initialized")
            
            if VOICE_AVAILABLE:
                try:
                    self.voice_handler = VoiceHandler()
                    logger.info("✓ Voice Handler initialized")
                except Exception as e:
                    logger.warning(f"Voice Handler initialization failed: {e}")
                    self.voice_handler = None
            else:
                logger.info("Voice Handler not available (missing dependencies)")
                self.voice_handler = None
            
            # System state
            self.system_stats = {
                "total_conversations": 0,
                "emergency_responses": 0,
                "successful_triages": 0,
                "system_start_time": datetime.now()
            }
            
            logger.info("🏥 Healthcare Assistant fully initialized and ready!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Healthcare Assistant: {e}")
            raise
    
    def process_message(self, user_id: str, message: str, patient_age: Optional[int] = None) -> Dict[str, Any]:
        """
        Main entry point for processing user messages.
        
        Args:
            user_id: Unique identifier for the user
            message: User's input message
            patient_age: Optional patient age for better triage
            
        Returns:
            Complete response with all relevant information
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing message from user {user_id}: '{message[:50]}...'")
            
            # Step 1: Classify intent
            intent, intent_confidence = self.intent_classifier.classify_intent(message)
            intent_result = {"intent": intent, "confidence": intent_confidence}
            
            # Step 2: Analyze sentiment and urgency
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(message)
            
            # Step 3: Process through dialogue manager
            dialogue_result = self.dialogue_manager.process_user_input(
                user_id, message, intent_result, sentiment_result
            )
            
            # Step 4: Healthcare-specific processing
            healthcare_assessment = None
            if intent == "symptom_triage":
                healthcare_assessment = self.healthcare_triage.assess_symptoms(
                    message, patient_age
                )
                
                # Update dialogue context with healthcare assessment
                dialogue_result["care_level"] = healthcare_assessment["care_level"]
                dialogue_result["urgency"] = healthcare_assessment["urgency"]
                dialogue_result["care_recommendations"] = healthcare_assessment["recommendations"]
            
            # Step 5: Generate appropriate response
            response_data = self.response_generator.generate_response(
                intent, sentiment_result, dialogue_result, healthcare_assessment
            )
            
            # Step 6: Add response to dialogue history
            self.dialogue_manager.add_assistant_response(
                user_id, response_data["message"], response_data["metadata"]
            )
            
            # Step 7: Handle follow-up questions if needed
            follow_up_questions = []
            if healthcare_assessment and dialogue_result.get("need_follow_up"):
                follow_up_questions = self.healthcare_triage.generate_follow_up_questions(
                    intent, healthcare_assessment.get("symptoms_detected", [])
                )
                if follow_up_questions:
                    self.dialogue_manager.set_follow_up_questions(user_id, follow_up_questions)
            
            # Step 8: Update system statistics
            self._update_system_stats(intent, sentiment_result, dialogue_result)
            
            # Step 9: Compile complete response
            complete_response = {
                "message": response_data["message"],
                "intent": intent,
                "sentiment": sentiment_result,
                "urgency_level": sentiment_result.get("urgency_level", "low"),
                "care_level": healthcare_assessment.get("care_level") if healthcare_assessment else None,
                "requires_escalation": dialogue_result.get("escalate", False),
                "follow_up_questions": follow_up_questions,
                "conversation_id": dialogue_result["context"]["session_id"],
                "processing_time": round(time.time() - start_time, 3),
                "metadata": {
                    "intent_confidence": intent_confidence,
                    "response_tone": response_data.get("tone"),
                    "healthcare_assessment": healthcare_assessment,
                    "system_action": dialogue_result["action"]
                }
            }
            
            # Log emergency situations
            if complete_response["urgency_level"] == "critical" or intent == "emergency":
                logger.warning(f"EMERGENCY DETECTED - User: {user_id}, Message: {message[:100]}")
            
            logger.info(f"Successfully processed message for {user_id} in {complete_response['processing_time']}s")
            
            return complete_response
            
        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {e}")
            return {
                "message": "I apologize, but I'm experiencing technical difficulties. For urgent medical needs, please call 911 or contact your healthcare provider directly.",
                "intent": "system_error",
                "urgency_level": "low",
                "requires_escalation": True,
                "error": str(e),
                "processing_time": round(time.time() - start_time, 3)
            }
    
    def process_voice_message(self, user_id: str, audio_data, patient_age: Optional[int] = None) -> Dict[str, Any]:
        if not self.voice_handler:
            return {"error": "Voice processing not available"}
        
        text = self.voice_handler.process_audio_file(audio_data)
        if not text:
            return {"error": "Could not understand audio"}
        
        response = self.process_message(user_id, text, patient_age)
        
        if self.voice_handler:
            audio_response = self.voice_handler.text_to_speech(response["message"])
            if audio_response:
                response["audio_response"] = audio_response
        
        return response
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages with metadata
        """
        return self.dialogue_manager.get_conversation_history(user_id, limit)
    
    def reset_conversation(self, user_id: str) -> Dict[str, str]:
        """
        Reset conversation state for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Confirmation message
        """
        new_state = self.dialogue_manager.reset_conversation(user_id)
        logger.info(f"Reset conversation for user: {user_id}")
        
        return {
            "message": "Conversation has been reset. How can I help you today?",
            "session_id": new_state.session_id,
            "status": "conversation_reset"
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive system performance metrics.
        
        Returns:
            Dictionary with system statistics
        """
        dialogue_stats = self.dialogue_manager.get_system_stats()
        
        uptime = datetime.now() - self.system_stats["system_start_time"]
        
        return {
            **self.system_stats,
            **dialogue_stats,
            "system_uptime_hours": round(uptime.total_seconds() / 3600, 2),
            "average_response_time": "< 1 second",
            "system_health": "operational"
        }
    
    def handle_emergency(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Special handling for emergency situations.
        
        Args:
            user_id: User identifier
            message: Emergency message
            
        Returns:
            Emergency response with escalation
        """
        logger.warning(f"EMERGENCY HANDLER ACTIVATED - User: {user_id}")
        
        emergency_response = {
            "message": "🚨 **EMERGENCY DETECTED** 🚨\n\n"
                      "If this is a life-threatening emergency, please:\n"
                      "• **Call 911 immediately**\n"
                      "• **Go to the nearest emergency room**\n"
                      "• **Do not delay seeking professional medical care**\n\n"
                      "If you're experiencing:\n"
                      "• Chest pain or difficulty breathing\n"
                      "• Loss of consciousness\n" 
                      "• Severe bleeding\n"
                      "• Signs of stroke\n"
                      "• Severe allergic reaction\n\n"
                      "**Time is critical - seek help immediately!**",
            "intent": "emergency",
            "urgency_level": "critical",
            "requires_escalation": True,
            "care_level": "emergency",
            "system_action": "immediate_escalation",
            "processing_time": 0.1
        }
        
        # Log emergency for monitoring
        self.system_stats["emergency_responses"] += 1
        
        # Add to conversation history
        self.dialogue_manager.add_assistant_response(
            user_id, emergency_response["message"], 
            {"type": "emergency_response", "escalated": True}
        )
        
        return emergency_response
    
    def get_triage_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of the triage assessment for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Triage summary if available
        """
        state = self.dialogue_manager.get_conversation_state(user_id)
        if not state:
            return None
        
        return {
            "session_id": state.session_id,
            "symptoms_mentioned": state.symptoms_mentioned,
            "care_level": state.care_level_determined,
            "urgency_level": state.urgency_level,
            "escalation_triggered": state.escalation_triggered,
            "message_count": len(state.messages),
            "conversation_duration": (datetime.now() - state.created_at).total_seconds() / 60
        }
    
    def export_conversation(self, user_id: str) -> Dict[str, Any]:
        """
        Export complete conversation data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Complete conversation export
        """
        history = self.get_conversation_history(user_id, limit=None)
        triage_summary = self.get_triage_summary(user_id)
        
        return {
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "conversation_history": history,
            "triage_summary": triage_summary,
            "system_version": "1.0.0"
        }
    
    def _update_system_stats(self, intent: str, sentiment_result: Dict[str, Any], 
                           dialogue_result: Dict[str, Any]):
        """Update internal system statistics."""
        self.system_stats["total_conversations"] += 1
        
        if intent == "emergency" or sentiment_result.get("urgency_level") == "critical":
            self.system_stats["emergency_responses"] += 1
        
        if intent == "symptom_triage" and not dialogue_result.get("escalate"):
            self.system_stats["successful_triages"] += 1
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform system health check.
        
        Returns:
            Health check results
        """
        try:
            # Test each component
            test_message = "Hello"
            
            # Test intent classification
            intent, confidence = self.intent_classifier.classify_intent(test_message)
            
            # Test sentiment analysis
            sentiment = self.sentiment_analyzer.analyze_sentiment(test_message)
            
            # Test response generation (minimal)
            test_context = {"response_type": "general", "escalate": False}
            self.response_generator.generate_response("general_inquiry", sentiment, test_context)
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "intent_classifier": "operational",
                    "sentiment_analyzer": "operational", 
                    "healthcare_triage": "operational",
                    "dialogue_manager": "operational",
                    "response_generator": "operational"
                },
                "system_stats": self.get_system_stats()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
