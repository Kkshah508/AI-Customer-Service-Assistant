"""
Healthcare Triage System

Implements medical triage logic, symptom assessment, and care level 
determination based on healthcare guidelines.
"""

import json
import os
import re
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class HealthcareTriageSystem:
    """
    Healthcare triage system that assesses symptoms and determines
    appropriate care level based on medical guidelines.
    """
    
    def __init__(self):
        """Initialize the healthcare triage system."""
        self.guidelines = {}
        self.care_levels = {}
        self.follow_up_questions = {}
        
        # Load medical guidelines
        self._load_medical_guidelines()
        
        # Initialize symptom patterns
        self._init_symptom_patterns()
    
    def _load_medical_guidelines(self):
        """Load medical guidelines and triage rules."""
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'medical_guidelines.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.guidelines = data.get('triage_rules', {})
                    self.care_levels = data.get('care_level_definitions', {})
                    self.follow_up_questions = data.get('follow_up_questions', {})
                    self.emergency_symptoms = data.get('emergency_symptoms', [])
                    self.urgent_symptoms = data.get('urgent_symptoms', [])
                    self.pediatric_red_flags = data.get('pediatric_red_flags', [])
                logger.info("Loaded medical guidelines successfully")
            else:
                logger.warning("Medical guidelines file not found")
        except Exception as e:
            logger.error(f"Error loading medical guidelines: {e}")
    
    def _init_symptom_patterns(self):
        """Initialize regex patterns for symptom detection."""
        self.symptom_patterns = {
            'fever': re.compile(r'fever|temperature|hot|burning up|(\d+\.?\d*)\s*°?[fF]', re.IGNORECASE),
            'pain': re.compile(r'pain|hurt|ache|aching|sore|tender', re.IGNORECASE),
            'respiratory': re.compile(r'breath|breathing|cough|wheez|shortness|chest', re.IGNORECASE),
            'cardiac': re.compile(r'chest pain|heart|cardiac|palpitations', re.IGNORECASE),
            'neurological': re.compile(r'headache|dizz|confusion|seizure|stroke|numb', re.IGNORECASE),
            'gastrointestinal': re.compile(r'nausea|vomit|diarrhea|stomach|abdominal', re.IGNORECASE),
            'pediatric': re.compile(r'child|baby|infant|toddler|kid|son|daughter', re.IGNORECASE),
            'rash': re.compile(r'rash|skin|spots|bumps|hives', re.IGNORECASE),
            'bleeding': re.compile(r'bleed|blood|hemorrhag', re.IGNORECASE)
        }
    
    def assess_symptoms(self, symptoms_text: str, patient_age: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze symptoms and determine care level needed.
        
        Args:
            symptoms_text: Description of symptoms
            patient_age: Patient age in years (optional)
            
        Returns:
            Assessment results including care level and recommendations
        """
        if not symptoms_text or not symptoms_text.strip():
            return {
                "care_level": "self_care",
                "urgency": "low",
                "symptoms_detected": [],
                "red_flags": [],
                "recommendations": "Please describe your symptoms for proper assessment."
            }
        
        assessment = {
            "symptoms_detected": [],
            "red_flags": [],
            "care_level": "self_care",
            "urgency": "low",
            "recommendations": "",
            "follow_up_needed": False,
            "age_category": self._determine_age_category(patient_age)
        }
        
        # Detect symptoms
        assessment["symptoms_detected"] = self._detect_symptoms(symptoms_text)
        
        # Check for red flags
        assessment["red_flags"] = self.check_red_flags(symptoms_text)
        
        # Determine care level
        assessment["care_level"] = self.determine_care_level(
            symptoms_text, assessment["red_flags"], patient_age
        )
        
        # Set urgency based on care level
        assessment["urgency"] = self._map_care_level_to_urgency(assessment["care_level"])
        
        # Generate recommendations
        assessment["recommendations"] = self._generate_recommendations(assessment)
        
        # Determine if follow-up questions needed
        assessment["follow_up_needed"] = self._needs_follow_up(assessment)
        
        logger.info(f"Symptom assessment: care_level={assessment['care_level']}, "
                   f"urgency={assessment['urgency']}, symptoms={len(assessment['symptoms_detected'])}")
        
        return assessment
    
    def _detect_symptoms(self, text: str) -> List[str]:
        """Detect symptoms mentioned in the text."""
        detected = []
        for symptom_type, pattern in self.symptom_patterns.items():
            if pattern.search(text):
                detected.append(symptom_type)
        return detected
    
    def _determine_age_category(self, age: Optional[int]) -> str:
        """Determine age category for triage purposes."""
        if age is None:
            return "unknown"
        elif age < 0.25:  # 3 months
            return "infant_0_3_months"
        elif age < 3:
            return "child_3_months_3_years"
        elif age < 18:
            return "child"
        else:
            return "adult"
    
    def check_red_flags(self, symptoms_text: str) -> List[str]:
        """
        Identify emergency symptoms that require immediate attention.
        
        Args:
            symptoms_text: Description of symptoms
            
        Returns:
            List of red flag symptoms detected
        """
        red_flags = []
        text_lower = symptoms_text.lower()
        
        # Check emergency symptoms
        for symptom in self.emergency_symptoms:
            if symptom.lower() in text_lower:
                red_flags.append(symptom)
        
        # Additional pattern-based red flag detection
        emergency_patterns = [
            (r'can\'?t breathe|difficulty breathing|shortness of breath', 'respiratory_distress'),
            (r'chest pain|heart attack|cardiac', 'cardiac_emergency'),
            (r'unconscious|loss of consciousness|passed out', 'altered_consciousness'),
            (r'severe bleeding|hemorrhag|blood loss', 'severe_bleeding'),
            (r'allergic reaction|anaphylaxis|swelling', 'allergic_reaction'),
            (r'stroke|face drooping|arm weakness|speech', 'stroke_symptoms'),
            (r'choking|can\'?t swallow', 'airway_obstruction'),
            (r'poisoning|overdose|toxic', 'poisoning'),
            (r'severe burn|chemical burn', 'severe_burns'),
            (r'head injury|skull|brain', 'head_trauma')
        ]
        
        for pattern, flag in emergency_patterns:
            if re.search(pattern, text_lower):
                red_flags.append(flag)
        
        return red_flags
    
    def determine_care_level(self, symptoms: str, red_flags: List[str], age: Optional[int] = None) -> str:
        """
        Determine appropriate care level based on symptoms and patient factors.
        
        Args:
            symptoms: Symptom description
            red_flags: List of red flag symptoms
            age: Patient age
            
        Returns:
            Care level: emergency, urgent_care, clinic, telehealth, self_care
        """
        # Emergency level - any red flags
        if red_flags:
            return "emergency"
        
        # Check fever guidelines
        fever_temp = self._extract_temperature(symptoms)
        if fever_temp:
            age_category = self._determine_age_category(age)
            fever_assessment = self._assess_fever(fever_temp, age_category)
            if fever_assessment in ["emergency", "urgent_care"]:
                return fever_assessment
        
        # Check pain level
        pain_level = self._assess_pain_level(symptoms)
        if pain_level >= 7:
            return "urgent_care"
        elif pain_level >= 4:
            return "clinic"
        
        # Check symptom combinations
        symptoms_detected = self._detect_symptoms(symptoms)
        
        # Respiratory + fever = urgent
        if "respiratory" in symptoms_detected and "fever" in symptoms_detected:
            return "urgent_care"
        
        # Multiple concerning symptoms
        concerning_symptoms = ["fever", "pain", "respiratory", "gastrointestinal", "neurological"]
        concerning_count = len([s for s in symptoms_detected if s in concerning_symptoms])
        
        if concerning_count >= 3:
            return "urgent_care"
        elif concerning_count >= 2:
            return "clinic"
        elif concerning_count == 1:
            return "telehealth"
        
        return "self_care"
    
    def _extract_temperature(self, text: str) -> Optional[float]:
        """Extract temperature value from text."""
        # Look for temperature patterns
        temp_pattern = r'(\d+(?:\.\d+)?)\s*°?[fF]'
        match = re.search(temp_pattern, text)
        if match:
            return float(match.group(1))
        
        # Look for descriptive fever terms
        if re.search(r'high fever|very hot', text, re.IGNORECASE):
            return 103.0  # Assume high fever
        elif re.search(r'fever|hot|temperature', text, re.IGNORECASE):
            return 101.0  # Assume moderate fever
        
        return None
    
    def _assess_fever(self, temperature: float, age_category: str) -> str:
        """Assess fever severity based on age and temperature."""
        fever_guidelines = self.guidelines.get("fever_guidelines", {})
        
        if age_category in fever_guidelines:
            guideline = fever_guidelines[age_category]
            threshold = guideline.get("threshold", 101.0)
            
            if temperature >= threshold:
                return guideline.get("action", "clinic")
        
        # Default fever assessment
        if temperature >= 104:
            return "emergency"
        elif temperature >= 102:
            return "urgent_care"
        elif temperature >= 100.4:
            return "clinic"
        else:
            return "self_care"
    
    def _assess_pain_level(self, text: str) -> int:
        """Extract and assess pain level from text."""
        # Look for numeric pain scale
        pain_pattern = r'(\d+)\s*(?:out of|/)\s*10|pain.*?(\d+)'
        match = re.search(pain_pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1) or match.group(2))
        
        # Look for descriptive pain terms
        if re.search(r'excruciating|unbearable|severe|intense', text, re.IGNORECASE):
            return 9
        elif re.search(r'bad|terrible|awful|sharp', text, re.IGNORECASE):
            return 7
        elif re.search(r'moderate|noticeable', text, re.IGNORECASE):
            return 5
        elif re.search(r'mild|slight|little', text, re.IGNORECASE):
            return 3
        elif re.search(r'pain|hurt|ache', text, re.IGNORECASE):
            return 5  # Default moderate pain
        
        return 0
    
    def _map_care_level_to_urgency(self, care_level: str) -> str:
        """Map care level to urgency classification."""
        mapping = {
            "emergency": "critical",
            "urgent_care": "high", 
            "clinic": "medium",
            "telehealth": "low",
            "self_care": "low"
        }
        return mapping.get(care_level, "low")
    
    def generate_follow_up_questions(self, intent: str, symptoms: List[str]) -> List[str]:
        """
        Generate relevant follow-up questions based on intent and symptoms.
        
        Args:
            intent: Detected user intent
            symptoms: List of detected symptoms
            
        Returns:
            List of follow-up questions
        """
        questions = []
        
        # Get base questions for symptom types
        for symptom in symptoms:
            if symptom in self.follow_up_questions:
                questions.extend(self.follow_up_questions[symptom][:2])  # Limit to 2 per symptom
        
        # Add general triage questions if none found
        if not questions:
            questions = [
                "Can you describe your symptoms in more detail?",
                "When did these symptoms start?",
                "Are the symptoms getting better, worse, or staying the same?"
            ]
        
        # Limit total questions
        return questions[:3]
    
    def get_care_recommendations(self, care_level: str, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide specific care recommendations based on care level.
        
        Args:
            care_level: Determined care level
            location: User location (optional)
            
        Returns:
            Dictionary with care recommendations
        """
        if care_level not in self.care_levels:
            care_level = "self_care"
        
        care_info = self.care_levels[care_level].copy()
        
        # Add specific recommendations based on care level
        if care_level == "emergency":
            care_info["immediate_action"] = "Call 911 or go to nearest emergency room"
            care_info["warning"] = "Do not delay seeking care"
        elif care_level == "urgent_care":
            care_info["immediate_action"] = "Seek medical attention within 2-4 hours"
            care_info["options"] = ["Urgent care center", "Emergency room", "Call doctor"]
        elif care_level == "clinic":
            care_info["immediate_action"] = "Schedule appointment within 24-48 hours"
            care_info["options"] = ["Primary care doctor", "Clinic visit", "Telehealth"]
        
        return care_info
    
    def _generate_recommendations(self, assessment: Dict[str, Any]) -> str:
        """Generate care recommendations based on assessment."""
        care_level = assessment["care_level"]
        care_info = self.get_care_recommendations(care_level)
        
        return care_info.get("description", "Please consult with a healthcare provider.")
    
    def _needs_follow_up(self, assessment: Dict[str, Any]) -> bool:
        """Determine if follow-up questions are needed."""
        # Need follow-up if care level is uncertain or moderate symptoms
        return (
            assessment["care_level"] in ["clinic", "urgent_care"] and
            len(assessment["symptoms_detected"]) <= 2 and
            not assessment["red_flags"]
        )
