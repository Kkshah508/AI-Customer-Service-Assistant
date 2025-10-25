"""
Intent Classification Module for Healthcare Assistant

Uses Hugging Face transformers for zero-shot classification of user intents
in healthcare conversations.
"""

import json
import os
from typing import Dict, List, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Intent classifier using keyword-based classification.
    Identifies user intents in healthcare conversations.
    """
    
    def __init__(self):
        """
        Initialize the intent classifier with keyword-based classification.
        """
        logger.info("Initializing keyword-based intent classifier")
        self.classifier = None      
        # Define healthcare-specific intents
        self.intents = [
            "symptom_triage",
            "emergency", 
            "appointment_booking",
            "general_inquiry",
            "insurance_question"
        ]
        
        # Intent descriptions for better classification
        self.intent_descriptions = {
            "symptom_triage": "reporting medical symptoms or health concerns that need assessment",
            "emergency": "urgent medical emergency requiring immediate attention",
            "appointment_booking": "scheduling, rescheduling, or canceling medical appointments",
            "medication_info": "questions about medications, side effects, or drug interactions", 
            "general_inquiry": "general questions about hospital services, hours, or policies",
            "insurance_question": "questions about insurance coverage, billing, or claims"
        }
        
        # Load training data if available
        self._load_training_data()
    
    def _load_training_data(self):
        """Load training examples for intent classification."""
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'intents.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.training_data = json.load(f)
                logger.info("Loaded training data for intent classification")
            else:
                logger.warning("Training data file not found")
                self.training_data = {}
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            self.training_data = {}
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Classify the intent of user input using keyword matching.
        
        Args:
            text: User input text to classify
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        if not text or not text.strip():
            return "general_inquiry", 0.5
        
        text_lower = text.lower()
        
        emergency_keywords = ['emergency', 'urgent', 'critical', 'severe', 'chest pain', 'can\'t breathe', 'unconscious', 'bleeding', 'overdose', '911']
        symptom_keywords = ['pain', 'fever', 'headache', 'nausea', 'dizzy', 'symptoms', 'sick', 'hurt', 'ache', 'rash']
        appointment_keywords = ['appointment', 'schedule', 'booking', 'reschedule', 'cancel', 'visit']
        medication_keywords = ['medication', 'prescription', 'medicine', 'drug', 'pill', 'dose']
        insurance_keywords = ['insurance', 'coverage', 'billing', 'claim', 'copay', 'deductible']
        
        if any(keyword in text_lower for keyword in emergency_keywords):
            return "emergency", 0.9
        elif any(keyword in text_lower for keyword in symptom_keywords):
            return "symptom_triage", 0.8
        elif any(keyword in text_lower for keyword in appointment_keywords):
            return "appointment_booking", 0.8
        elif any(keyword in text_lower for keyword in medication_keywords):
            return "medication_info", 0.8
        elif any(keyword in text_lower for keyword in insurance_keywords):
            return "insurance_question", 0.8
        else:
            return "general_inquiry", 0.6
    
    def _is_emergency(self, text: str) -> bool:
        """
        Detect emergency situations using keyword matching.
        
        Args:
            text: User input text
            
        Returns:
            True if emergency detected
        """
        emergency_keywords = [
            "emergency", "911", "can't breathe", "heart attack", "stroke",
            "choking", "severe pain", "unconscious", "bleeding heavily",
            "allergic reaction", "chest pain", "difficulty breathing",
            "severe allergic", "call ambulance", "losing consciousness"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)
    
    def get_intent_confidence(self, text: str, specific_intent: str) -> float:
        """
        Get confidence score for a specific intent.
        
        Args:
            text: User input text
            specific_intent: Intent to check confidence for
            
        Returns:
            Confidence score for the specific intent
        """
        if specific_intent not in self.intents:
            return 0.0
        
        try:
            candidate_labels = [self.intent_descriptions[specific_intent]]
            result = self.classifier(text, candidate_labels)
            return result['scores'][0]
        except Exception as e:
            logger.error(f"Error getting intent confidence: {e}")
            return 0.0
    
    def batch_classify(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Classify multiple texts at once.
        
        Args:
            texts: List of texts to classify
            
        Returns:
            List of (intent, confidence) tuples
        """
        results = []
        for text in texts:
            intent, confidence = self.classify_intent(text)
            results.append((intent, confidence))
        return results
    
    def get_intent_examples(self, intent: str) -> List[str]:
        """
        Get training examples for a specific intent.
        
        Args:
            intent: Intent name
            
        Returns:
            List of example texts for the intent
        """
        return self.training_data.get(intent, [])
    
    def update_training_data(self, intent: str, examples: List[str]):
        """
        Update training data with new examples.
        
        Args:
            intent: Intent name
            examples: New example texts
        """
        if intent not in self.training_data:
            self.training_data[intent] = []
        self.training_data[intent].extend(examples)
        logger.info(f"Added {len(examples)} examples for intent: {intent}")
