"""
AI-Powered Healthcare Customer Service Assistant

A comprehensive healthcare triage and customer service system using 
machine learning for intent classification, sentiment analysis, and 
dialogue management.
"""

__version__ = "1.0.0"
__author__ = "Healthcare AI Assistant Team"

from .intent_classifier import IntentClassifier
from .sentiment_analyzer import SentimentAnalyzer
from .healthcare_logic import HealthcareTriageSystem
from .dialogue_manager import DialogueManager
from .response_generator import ResponseGenerator
from .main_assistant import HealthcareAssistant

__all__ = [
    'IntentClassifier',
    'SentimentAnalyzer', 
    'HealthcareTriageSystem',
    'DialogueManager',
    'ResponseGenerator',
    'HealthcareAssistant'
]
