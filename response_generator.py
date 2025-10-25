"""
Response Generation Module

Generates appropriate responses based on intent, sentiment, context,
and healthcare triage results.
"""

import json
import os
import random
from typing import Dict, List, Optional, Any
import logging
import requests

logger = logging.getLogger(__name__)


class ResponseGenerator:
    def __init__(self, knowledge_base=None):
        self.responses = {}
        self.load_response_templates()
        self.use_llm = bool(os.getenv("OPENAI_API_KEY"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.knowledge_base = knowledge_base
        
        # Response tone modifiers
        self.tone_modifiers = {
            "empathetic": {
                "prefixes": ["I understand this must be concerning.", "I can see you're worried.", 
                           "This sounds distressing."],
                "connectors": ["Let me help you with this.", "I want to make sure you get the right care."],
                "tone": "caring and understanding"
            },
            "reassuring": {
                "prefixes": ["Let me help you understand this.", "I'm here to assist you.",
                           "Don't worry, we'll figure this out together."],
                "connectors": ["Here's what I recommend:", "Let's look at your options:"],
                "tone": "calm and supportive"
            },
            "professional": {
                "prefixes": ["Based on the information provided:", "According to medical guidelines:",
                           "Here's what I can tell you:"],
                "connectors": ["The recommended course of action is:", "I suggest the following:"],
                "tone": "professional and informative"
            },
            "urgent": {
                "prefixes": ["Important:", "Immediate attention may be required:",
                           "Please review this:"],
                "connectors": ["You need to:", "Please take the following action immediately:"],
                "tone": "clear and direct"
            }
        }
    
    def load_response_templates(self):
        """Load response templates from data file."""
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'responses.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.responses = json.load(f)
                logger.info("Loaded response templates successfully")
            else:
                logger.warning("Response templates file not found")
                self._create_fallback_responses()
        except Exception as e:
            logger.error(f"Error loading response templates: {e}")
            self._create_fallback_responses()
    
    def _create_fallback_responses(self):
        """Create basic fallback responses if templates can't be loaded."""
        self.responses = {
            "greeting": {
                "initial": "Hello! I'm your AI healthcare assistant. How can I help you today?"
            },
            "emergency": {
                "immediate": "This sounds like an emergency. Please call 911 or go to the nearest emergency room immediately."
            },
            "general": "I'd be happy to help you with your healthcare question."
        }
    
    def generate_response(self, intent: str, sentiment: Dict[str, Any], 
                         context: Dict[str, Any], entities: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate appropriate response based on all factors.
        
        Args:
            intent: Detected user intent
            sentiment: Sentiment analysis results
            context: Conversation context
            entities: Extracted entities (optional)
            
        Returns:
            Dictionary with response and metadata
        """
        if entities is None:
            entities = {}
        
        tone = self._determine_tone(sentiment, context)
        final_response = None
        if self.use_llm and intent in ["general_inquiry", "appointment_booking", "insurance_question", "medication_info"]:
            llm_text = self._generate_llm_response(intent, sentiment, context, entities)
            if llm_text:
                final_response = llm_text
        if not final_response:
            base_response = self._generate_base_response(intent, context, entities)
            final_response = self.adjust_tone_for_sentiment(base_response, sentiment, tone)
        
        # Add follow-up if needed
        if context.get("need_follow_up"):
            final_response += "\n\n" + self._generate_follow_up_prompt(intent, context)
        
        # Add medical disclaimer for medical content
        if intent in ["symptom_triage", "medication_info", "emergency"]:
            final_response += "\n\n" + self.responses.get("disclaimer", "")
        
        response_data = {
            "message": final_response,
            "tone": tone,
            "intent": intent,
            "urgency": sentiment.get("urgency_level", "low"),
            "requires_escalation": context.get("escalate", False),
            "metadata": {
                "response_type": context.get("response_type", "general"),
                "care_level": context.get("care_level"),
                "confidence": sentiment.get("confidence", 0.5)
            }
        }
        
        logger.info(f"Generated response for intent={intent}, tone={tone}, "
                   f"urgency={sentiment.get('urgency_level', 'low')}")
        
        return response_data

    def _generate_llm_response(self, intent: str, sentiment: Dict[str, Any], context: Dict[str, Any], entities: Dict[str, Any]) -> Optional[str]:
        try:
            if not self.openai_api_key:
                return None
            user_text = context.get("user_message") or ""
            if not user_text:
                return None
            
            kb_context = ""
            if self.knowledge_base:
                try:
                    retrieved_docs = self.knowledge_base.query(user_text, n_results=3)
                    if retrieved_docs:
                        kb_context = "\n\nRelevant information from knowledge base:\n"
                        for i, doc in enumerate(retrieved_docs, 1):
                            kb_context += f"\n[{i}] {doc['text']}\n"
                except Exception as e:
                    logger.warning(f"Knowledge base query failed: {e}")
            
            system_prompt = "You are a helpful customer service AI assistant. Provide concise, actionable answers and ask at most one clarifying question if needed."
            if kb_context:
                system_prompt += " Use the provided knowledge base information to answer accurately."
            
            user_content = user_text
            if kb_context:
                user_content = f"{user_text}{kb_context}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            payload = {"model": self.openai_model, "messages": messages, "temperature": 0.5, "max_tokens": 300}
            headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
            if r.status_code == 200:
                data = r.json()
                choice = (data.get("choices") or [{}])[0]
                content = (choice.get("message") or {}).get("content")
                return content
            return None
        except Exception:
            return None
    
    def _determine_tone(self, sentiment: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Determine appropriate response tone."""
        urgency = sentiment.get("urgency_level", "low")
        emotional_state = sentiment.get("emotional_state", "neutral")
        escalation_needed = context.get("escalate", False)
        
        if urgency == "critical" or escalation_needed:
            return "urgent"
        elif emotional_state in ["fear", "sadness", "anger"] or urgency == "high":
            return "empathetic"
        elif sentiment.get("sentiment") == "positive":
            return "professional"
        else:
            return "reassuring"
    
    def _generate_base_response(self, intent: str, context: Dict[str, Any], 
                              entities: Dict[str, Any]) -> str:
        """Generate base response based on intent and context."""
        response_type = context.get("response_type", "general")
        
        # Emergency responses - highest priority
        if intent == "emergency" or context.get("priority") == "critical":
            return self._get_emergency_response(context)
        
        # Symptom triage responses
        elif intent == "symptom_triage":
            return self._get_triage_response(context, entities)
        
        # Appointment booking responses
        elif intent == "appointment_booking":
            return self._get_appointment_response(context, entities)
        
        # Medication information responses
        elif intent == "medication_info":
            return self._get_medication_response(context, entities)
        
        # General inquiry responses
        elif intent == "general_inquiry":
            return self._get_general_response(context, entities)
        
        # Insurance question responses
        elif intent == "insurance_question":
            return self._get_insurance_response(context, entities)
        
        # Fallback response
        else:
            return self.responses.get("general", {}).get("fallback", 
                "I'd be happy to help you. Could you please provide more details about your question?")
    
    def _get_emergency_response(self, context: Dict[str, Any]) -> str:
        """Generate emergency response."""
        emergency_responses = self.responses.get("emergency", {})
        
        base_response = emergency_responses.get("immediate", 
            "🚨 This sounds like a medical emergency. Please call 911 immediately or go to the nearest emergency room.")
        
        # Add urgency indicators
        base_response += "\n\n⚠️ **Do not delay seeking care. Time is critical in emergency situations.**"
        
        return base_response
    
    def _get_triage_response(self, context: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Generate symptom triage response."""
        care_level = context.get("care_level", "self_care")
        triage_responses = self.responses.get("symptom_triage", {})
        
        if care_level == "emergency":
            response = triage_responses.get("critical", 
                "⚠️ **EMERGENCY**: These symptoms require immediate medical attention. Please call 911 or go to the nearest emergency room.")
        elif care_level == "urgent_care":
            response = triage_responses.get("urgent",
                "🏥 **URGENT**: These symptoms require prompt medical attention within the next 2-4 hours.")
        elif care_level == "clinic":
            response = triage_responses.get("moderate",
                "🩺 **MODERATE**: These symptoms should be evaluated by a healthcare provider within 24-48 hours.")
        else:
            response = triage_responses.get("mild",
                "💡 These symptoms can often be managed with self-care, but consult a healthcare provider if they worsen.")
        
        # Add specific care recommendations if available
        if context.get("care_recommendations"):
            response += f"\n\n**Recommendation:** {context['care_recommendations']}"
        
        return response
    
    def _get_appointment_response(self, context: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Generate appointment booking response."""
        appointment_responses = self.responses.get("appointment_booking", {})
        
        # Check for specific appointment types
        if "specialist" in str(entities).lower():
            return appointment_responses.get("specialist",
                "I can help you with specialist appointments. What type of specialist do you need to see?")
        elif "reschedule" in str(context).lower():
            return appointment_responses.get("reschedule",
                "I can help you reschedule your appointment. Please provide your current appointment details.")
        else:
            return appointment_responses.get("general",
                "I'd be happy to help you schedule an appointment. Let me connect you with our booking system.")
    
    def _get_medication_response(self, context: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Generate medication information response."""
        med_responses = self.responses.get("medication_info", {})
        
        base_response = med_responses.get("general",
            "I can provide general medication information. For personalized advice, please consult your pharmacist or healthcare provider.")
        
        # Add safety warning for medication questions
        base_response += "\n\n⚠️ **Important:** Never stop or change medications without consulting your healthcare provider."
        
        return base_response
    
    def _get_general_response(self, context: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Generate general inquiry response."""
        general_responses = self.responses.get("general_inquiry", {})
        
        # Try to match specific inquiries
        if "hours" in str(context).lower():
            return general_responses.get("hours", "Our clinic hours are Monday-Friday 8:00 AM - 6:00 PM.")
        elif "insurance" in str(context).lower():
            return general_responses.get("insurance", "We accept most major insurance plans. Please call our billing department for specific coverage information.")
        elif "parking" in str(context).lower():
            return general_responses.get("parking", "Free parking is available in our main lot with handicap accessible spaces near the entrance.")
        else:
            return "I'd be happy to help with your question. Could you please provide more specific details?"
    
    def _get_insurance_response(self, context: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Generate insurance question response."""
        return ("For insurance-related questions, I recommend speaking with our billing department. "
                "They can provide specific information about coverage, copays, and claims processing.")
    
    def adjust_tone_for_sentiment(self, response: str, sentiment: Dict[str, Any], tone: str) -> str:
        """
        Adjust response tone based on user emotional state.
        
        Args:
            response: Base response text
            sentiment: Sentiment analysis results
            tone: Desired tone
            
        Returns:
            Tone-adjusted response
        """
        if tone not in self.tone_modifiers:
            return response
        
        modifier = self.tone_modifiers[tone]
        
        # Add empathetic prefix for emotional situations
        if sentiment.get("urgency_level") in ["high", "critical"] or \
           sentiment.get("emotional_state") in ["fear", "sadness", "anger"]:
            
            prefix = random.choice(modifier["prefixes"])
            connector = random.choice(modifier["connectors"])
            
            return f"{prefix} {connector}\n\n{response}"
        
        return response
    
    def format_medical_response(self, care_level: str, recommendations: Dict[str, Any]) -> str:
        """
        Format medical advice appropriately with proper disclaimers.
        
        Args:
            care_level: Determined care level
            recommendations: Care recommendations
            
        Returns:
            Formatted medical response
        """
        care_icons = {
            "emergency": "🚨",
            "urgent_care": "🏥", 
            "clinic": "🩺",
            "telehealth": "💻",
            "self_care": "💡"
        }
        
        icon = care_icons.get(care_level, "ℹ️")
        description = recommendations.get("description", "Please consult with a healthcare provider.")
        timeframe = recommendations.get("timeframe", "")
        
        formatted_response = f"{icon} **{care_level.replace('_', ' ').title()}**\n\n{description}"
        
        if timeframe:
            formatted_response += f"\n\n⏰ **Timeframe:** {timeframe}"
        
        if "options" in recommendations:
            options = recommendations["options"]
            formatted_response += f"\n\n**Options:**\n" + "\n".join([f"• {opt}" for opt in options])
        
        return formatted_response
    
    def _generate_follow_up_prompt(self, intent: str, context: Dict[str, Any]) -> str:
        """Generate appropriate follow-up prompts."""
        follow_up_prompts = {
            "symptom_triage": [
                "To better assess your situation, could you tell me:",
                "I'd like to ask a few more questions to help determine the best care for you:",
                "To provide the most appropriate guidance, please let me know:"
            ],
            "medication_info": [
                "Do you have any other questions about this medication?",
                "Is there anything specific about the medication you'd like to know more about?"
            ],
            "appointment_booking": [
                "What type of appointment would you like to schedule?",
                "Do you have a preferred date and time?"
            ]
        }
        
        prompts = follow_up_prompts.get(intent, ["Is there anything else I can help you with?"])
        return random.choice(prompts)
    
    def generate_follow_up(self, conversation_state: Dict[str, Any]) -> str:
        """
        Generate relevant follow-up messages based on conversation state.
        
        Args:
            conversation_state: Current conversation state
            
        Returns:
            Follow-up message
        """
        intent = conversation_state.get("current_intent")
        urgency = conversation_state.get("urgency_level", "low")
        
        if urgency == "critical":
            return "Is there anything else urgent I can help you with while you seek emergency care?"
        elif intent == "symptom_triage":
            return "How are you feeling now? Do you have any other symptoms to report?"
        elif intent == "appointment_booking":
            return "Was I able to help you with your appointment needs? Do you need assistance with anything else?"
        else:
            return "Is there anything else I can help you with today?"
