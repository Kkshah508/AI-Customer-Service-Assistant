"""
Utility functions for the Healthcare Assistant system.

Common utilities for logging, data processing, validation, and helper functions.
"""

import re
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import hashlib


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for the healthcare assistant.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def validate_user_input(text: str) -> Dict[str, Any]:
    """
    Validate and sanitize user input.
    
    Args:
        text: User input text
        
    Returns:
        Validation result with cleaned text and flags
    """
    if not text or not isinstance(text, str):
        return {
            "is_valid": False,
            "cleaned_text": "",
            "issues": ["Empty or invalid input"],
            "severity": "error"
        }
    
    issues = []
    severity = "none"
    
    # Basic sanitization
    cleaned_text = text.strip()
    
    # Length validation
    if len(cleaned_text) > 1000:
        issues.append("Input too long (max 1000 characters)")
        cleaned_text = cleaned_text[:1000]
        severity = "warning"
    
    if len(cleaned_text) < 3:
        issues.append("Input too short (min 3 characters)")
        severity = "warning"
    
    # Check for potentially harmful content
    suspicious_patterns = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript URLs
        r'data:.*base64',           # Base64 data URLs
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, cleaned_text, re.IGNORECASE):
            issues.append("Potentially harmful content detected")
            severity = "error"
            break
    
    return {
        "is_valid": severity != "error",
        "cleaned_text": cleaned_text,
        "issues": issues,
        "severity": severity,
        "original_length": len(text),
        "cleaned_length": len(cleaned_text)
    }


def extract_medical_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract medical entities from text using pattern matching.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary of extracted medical entities
    """
    entities = {
        "symptoms": [],
        "body_parts": [],
        "medications": [],
        "time_expressions": [],
        "measurements": [],
        "age_mentions": []
    }
    
    text_lower = text.lower()
    
    # Symptom patterns
    symptom_patterns = [
        r'\b(pain|ache|hurt|burning|tingling|numbness)\b',
        r'\b(fever|temperature|hot|chills)\b',
        r'\b(cough|wheez|shortness of breath|difficulty breathing)\b',
        r'\b(nausea|vomit|diarrhea|constipation)\b',
        r'\b(headache|migraine|dizziness|lightheaded)\b',
        r'\b(rash|itching|swelling|bruising|bleeding)\b'
    ]
    
    for pattern in symptom_patterns:
        matches = re.findall(pattern, text_lower)
        entities["symptoms"].extend(matches)
    
    # Body part patterns
    body_parts = [
        'head', 'neck', 'chest', 'back', 'arm', 'leg', 'hand', 'foot',
        'stomach', 'abdomen', 'throat', 'eye', 'ear', 'nose', 'mouth',
        'heart', 'lung', 'liver', 'kidney', 'brain'
    ]
    
    for part in body_parts:
        if part in text_lower:
            entities["body_parts"].append(part)
    
    # Time expressions
    time_patterns = [
        r'\b(\d+)\s*(hour|day|week|month|year)s?\s*ago\b',
        r'\b(yesterday|today|last\s+night|this\s+morning)\b',
        r'\bfor\s+(\d+)\s*(hour|day|week|month)s?\b'
    ]
    
    for pattern in time_patterns:
        matches = re.findall(pattern, text_lower)
        entities["time_expressions"].extend([' '.join(match) if isinstance(match, tuple) else match for match in matches])
    
    # Measurements (temperature, weight, etc.)
    measurement_patterns = [
        r'\b(\d+\.?\d*)\s*°?[fF]\b',  # Temperature
        r'\b(\d+)\s*(mg|g|kg|lb|lbs)\b',  # Weight/dosage
        r'\b(\d+)/(\d+)\b'  # Blood pressure, fractions
    ]
    
    for pattern in measurement_patterns:
        matches = re.findall(pattern, text_lower)
        entities["measurements"].extend([' '.join(match) if isinstance(match, tuple) else match for match in matches])
    
    # Age mentions
    age_patterns = [
        r'\b(\d+)\s*years?\s*old\b',
        r'\baged?\s*(\d+)\b',
        r'\b(infant|baby|toddler|child|teenager|adult|elderly)\b'
    ]
    
    for pattern in age_patterns:
        matches = re.findall(pattern, text_lower)
        entities["age_mentions"].extend(matches)
    
    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    return entities


def calculate_urgency_score(symptoms: List[str], sentiment: Dict[str, Any], 
                          entities: Dict[str, List[str]]) -> float:
    """
    Calculate urgency score based on multiple factors.
    
    Args:
        symptoms: List of detected symptoms
        sentiment: Sentiment analysis results
        entities: Extracted medical entities
        
    Returns:
        Urgency score between 0 and 1
    """
    base_score = 0.0
    
    # Symptom-based scoring
    high_urgency_symptoms = ['chest pain', 'difficulty breathing', 'unconscious', 'bleeding']
    moderate_urgency_symptoms = ['fever', 'severe pain', 'vomiting']
    
    for symptom in symptoms:
        if any(urgent in symptom.lower() for urgent in high_urgency_symptoms):
            base_score += 0.3
        elif any(moderate in symptom.lower() for moderate in moderate_urgency_symptoms):
            base_score += 0.2
        else:
            base_score += 0.1
    
    # Sentiment-based adjustment
    sentiment_urgency = sentiment.get('urgency_level', 'low')
    sentiment_multiplier = {
        'critical': 1.0,
        'high': 0.8,
        'medium': 0.6,
        'low': 0.4
    }.get(sentiment_urgency, 0.4)
    
    base_score *= sentiment_multiplier
    
    # Entity-based adjustment
    if entities.get('measurements'):
        base_score += 0.1  # Specific measurements suggest more serious concern
    
    if entities.get('time_expressions'):
        # Recent onset or persistent symptoms
        base_score += 0.05
    
    return min(base_score, 1.0)  # Cap at 1.0


def format_conversation_export(conversation_data: Dict[str, Any]) -> str:
    """
    Format conversation data for export.
    
    Args:
        conversation_data: Conversation data to format
        
    Returns:
        Formatted string representation
    """
    output = []
    output.append("=" * 60)
    output.append("HEALTHCARE ASSISTANT CONVERSATION EXPORT")
    output.append("=" * 60)
    output.append(f"User ID: {conversation_data.get('user_id', 'Unknown')}")
    output.append(f"Export Time: {conversation_data.get('export_timestamp', 'Unknown')}")
    output.append("")
    
    # Triage Summary
    triage = conversation_data.get('triage_summary', {})
    if triage:
        output.append("TRIAGE SUMMARY:")
        output.append(f"  Care Level: {triage.get('care_level', 'N/A')}")
        output.append(f"  Urgency: {triage.get('urgency_level', 'N/A')}")
        output.append(f"  Symptoms: {', '.join(triage.get('symptoms_mentioned', []))}")
        output.append(f"  Duration: {triage.get('conversation_duration', 0):.1f} minutes")
        output.append("")
    
    # Conversation History
    history = conversation_data.get('conversation_history', [])
    if history:
        output.append("CONVERSATION HISTORY:")
        output.append("-" * 40)
        
        for i, msg in enumerate(history, 1):
            timestamp = msg.get('timestamp', 'Unknown')
            sender = msg.get('sender', 'Unknown').upper()
            message = msg.get('message', '')
            
            output.append(f"[{timestamp}] {sender}:")
            output.append(f"  {message}")
            output.append("")
    
    output.append("=" * 60)
    output.append("END OF CONVERSATION EXPORT")
    output.append("=" * 60)
    
    return "\n".join(output)


def generate_session_id(user_id: str) -> str:
    """
    Generate a unique session ID.
    
    Args:
        user_id: User identifier
        
    Returns:
        Unique session ID
    """
    timestamp = str(int(datetime.now().timestamp()))
    combined = f"{user_id}_{timestamp}"
    hash_object = hashlib.md5(combined.encode())
    return f"session_{hash_object.hexdigest()[:8]}"


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Safely load JSON file with error handling.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded JSON data or empty dict if error
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logging.warning(f"JSON file not found: {file_path}")
            return {}
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return {}


def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Safely save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")
        return False


def mask_sensitive_info(text: str) -> str:
    """
    Mask potentially sensitive information in text.
    
    Args:
        text: Input text
        
    Returns:
        Text with sensitive information masked
    """
    # Mask phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Mask email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Mask social security numbers
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Mask medical record numbers
    text = re.sub(r'\b(MRN|mrn)[:=]?\s*\d+\b', '[MRN]', text, flags=re.IGNORECASE)
    
    return text


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for diagnostics.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": sys.version,
        "timestamp": datetime.now().isoformat(),
        "working_directory": os.getcwd()
    }


def validate_age_input(age_input: Union[str, int, None]) -> Optional[int]:
    """
    Validate and convert age input.
    
    Args:
        age_input: Age input to validate
        
    Returns:
        Validated age as integer or None if invalid
    """
    if age_input is None:
        return None
    
    try:
        age = int(age_input)
        if 0 <= age <= 150:  # Reasonable age range
            return age
        else:
            return None
    except (ValueError, TypeError):
        return None


class HealthcareValidator:
    """Validator class for healthcare-specific data."""
    
    @staticmethod
    def validate_temperature(temp_str: str) -> Optional[float]:
        """Validate temperature input."""
        try:
            # Extract numeric value
            temp_match = re.search(r'(\d+\.?\d*)', temp_str)
            if temp_match:
                temp = float(temp_match.group(1))
                
                # Convert Celsius to Fahrenheit if needed
                if temp < 50:  # Assume Celsius if under 50
                    temp = (temp * 9/5) + 32
                
                # Validate range (95-110°F is reasonable for human body temperature)
                if 95 <= temp <= 110:
                    return temp
            
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_pain_scale(pain_str: str) -> Optional[int]:
        """Validate pain scale input (1-10)."""
        try:
            pain_match = re.search(r'(\d+)', pain_str)
            if pain_match:
                pain = int(pain_match.group(1))
                if 1 <= pain <= 10:
                    return pain
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def is_emergency_keyword(text: str) -> bool:
        """Check if text contains emergency keywords."""
        emergency_keywords = [
            'emergency', '911', 'ambulance', 'heart attack', 'stroke',
            'choking', 'unconscious', 'not breathing', 'severe bleeding',
            'poisoning', 'overdose', 'chest pain', 'anaphylaxis'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)
