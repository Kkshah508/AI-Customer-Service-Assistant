"""
Sentiment Analysis Module for Healthcare Assistant

Analyzes user emotional state and urgency level to provide appropriate
responses and escalation when needed.
"""

import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes sentiment and emotional state of user messages
    to provide appropriate responses and detect urgency.
    """
    
    def __init__(self):
        """
        Initialize the sentiment analyzer with keyword-based analysis.
        """
        logger.info("Initializing keyword-based sentiment analyzer")
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        
        # Define emotional markers
        self.urgency_markers = {
            "high": [
                "emergency", "urgent", "immediately", "right away", "asap",
                "can't wait", "severe", "intense", "unbearable", "excruciating",
                "help me", "please help", "desperate", "terrible", "awful"
            ],
            "anxiety": [
                "worried", "scared", "anxious", "nervous", "concerned", 
                "frightened", "panicking", "terrified", "afraid"
            ],
            "pain": [
                "pain", "hurt", "ache", "agony", "burning", "stabbing",
                "throbbing", "sharp", "dull", "cramping"
            ],
            "distress": [
                "can't", "unable", "difficulty", "trouble", "struggling",
                "won't stop", "getting worse", "not getting better"
            ]
        }
        
        self.positive_markers = [
            "thank you", "thanks", "grateful", "appreciate", "helpful",
            "better", "improving", "good", "great", "excellent"
        ]
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment and emotional state of text.
        
        Args:
            text: User input text
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text or not text.strip():
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotional_state": "neutral",
                "urgency_level": "low"
            }
        
        result = {
            "sentiment": "neutral",
            "confidence": 0.5,
            "emotional_state": "neutral", 
            "urgency_level": "low",
            "emotion_markers": []
        }
        
        try:
            # Primary sentiment analysis
            if self.sentiment_pipeline:
                sentiment_result = self.sentiment_pipeline(text)[0]
                result["sentiment"] = sentiment_result["label"].lower()
                result["confidence"] = sentiment_result["score"]
            else:
                # Fallback keyword-based sentiment
                result.update(self._keyword_sentiment(text))
            
            # Emotion detection
            if self.emotion_pipeline:
                emotion_result = self.emotion_pipeline(text)[0]
                result["emotional_state"] = emotion_result["label"].lower()
            else:
                result["emotional_state"] = self._detect_emotion_keywords(text)
            
            # Urgency assessment
            result["urgency_level"] = self.assess_urgency_level(text, result["sentiment"])
            
            # Extract emotion markers
            result["emotion_markers"] = self.get_emotion_markers(text)
            
            logger.info(f"Sentiment analysis: {result['sentiment']} ({result['confidence']:.2f}), "
                       f"emotion: {result['emotional_state']}, urgency: {result['urgency_level']}")
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
        
        return result
    
    def _keyword_sentiment(self, text: str) -> Dict[str, any]:
        """Fallback keyword-based sentiment analysis."""
        text_lower = text.lower()
        
        negative_words = [
            "pain", "hurt", "terrible", "awful", "bad", "worse", "emergency",
            "help", "scared", "worried", "can't", "unable", "severe"
        ]
        
        positive_words = [
            "good", "better", "thanks", "thank you", "great", "excellent", 
            "helpful", "appreciate", "improving"
        ]
        
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if negative_count > positive_count:
            return {"sentiment": "negative", "confidence": 0.7}
        elif positive_count > negative_count:
            return {"sentiment": "positive", "confidence": 0.7}
        else:
            return {"sentiment": "neutral", "confidence": 0.6}
    
    def _detect_emotion_keywords(self, text: str) -> str:
        """Detect emotions using keyword matching."""
        text_lower = text.lower()
        
        if any(marker in text_lower for marker in self.urgency_markers["anxiety"]):
            return "fear"
        elif any(marker in text_lower for marker in self.urgency_markers["pain"]):
            return "sadness"
        elif any(marker in text_lower for marker in self.urgency_markers["distress"]):
            return "anger"
        elif any(marker in text_lower for marker in self.positive_markers):
            return "joy"
        else:
            return "neutral"
    
    def get_emotion_markers(self, text: str) -> List[str]:
        """
        Extract emotional indicators from text.
        
        Args:
            text: User input text
            
        Returns:
            List of detected emotion markers
        """
        markers = []
        text_lower = text.lower()
        
        for category, keywords in self.urgency_markers.items():
            found_keywords = [word for word in keywords if word in text_lower]
            if found_keywords:
                markers.extend([f"{category}:{word}" for word in found_keywords])
        
        # Check for positive markers
        found_positive = [word for word in self.positive_markers if word in text_lower]
        markers.extend([f"positive:{word}" for word in found_positive])
        
        return markers
    
    def assess_urgency_level(self, text: str, sentiment: str) -> str:
        """
        Determine urgency level based on text content and sentiment.
        
        Args:
            text: User input text
            sentiment: Detected sentiment
            
        Returns:
            Urgency level: critical, high, medium, low
        """
        text_lower = text.lower()
        
        # Critical urgency indicators
        critical_indicators = [
            "emergency", "911", "can't breathe", "chest pain", "heart attack",
            "stroke", "unconscious", "severe bleeding", "choking", "overdose"
        ]
        
        if any(indicator in text_lower for indicator in critical_indicators):
            return "critical"
        
        # High urgency indicators
        high_urgency = self.urgency_markers["high"] + self.urgency_markers["distress"]
        high_count = sum(1 for marker in high_urgency if marker in text_lower)
        
        if high_count >= 2 or sentiment == "negative":
            return "high"
        elif high_count == 1:
            return "medium"
        else:
            return "low"
    
    def is_escalation_needed(self, sentiment_result: Dict[str, any]) -> bool:
        """
        Determine if human escalation is needed based on sentiment analysis.
        
        Args:
            sentiment_result: Result from analyze_sentiment()
            
        Returns:
            True if escalation is recommended
        """
        return (
            sentiment_result["urgency_level"] in ["critical", "high"] or
            sentiment_result["emotional_state"] in ["fear", "anger"] or
            (sentiment_result["sentiment"] == "negative" and 
             sentiment_result["confidence"] > 0.8)
        )
    
    def get_response_tone(self, sentiment_result: Dict[str, any]) -> str:
        """
        Determine appropriate response tone based on sentiment.
        
        Args:
            sentiment_result: Result from analyze_sentiment()
            
        Returns:
            Response tone: empathetic, reassuring, professional, urgent
        """
        urgency = sentiment_result["urgency_level"]
        emotion = sentiment_result["emotional_state"]
        
        if urgency == "critical":
            return "urgent"
        elif emotion in ["fear", "sadness"] or urgency == "high":
            return "empathetic"
        elif sentiment_result["sentiment"] == "positive":
            return "professional"
        else:
            return "reassuring"
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        return [self.analyze_sentiment(text) for text in texts]
