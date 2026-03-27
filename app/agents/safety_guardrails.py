import re
from typing import List, Tuple

class SafetyGuardrails:
    """Safety guardrails for medical intake agent"""
    
    # Forbidden patterns that should trigger warnings
    FORBIDDEN_PATTERNS = [
        (r"(you have|certainly|definitely|diagnosed with|it sounds like you have) (cancer|tumor|malignant|diabetes|hypertension|infection)", "Avoid definitive diagnosis"),
        (r"you (will|must|need to) take (medication|drug|pill|antibiotic|aspirin|ibuprofen)", "Avoid prescribing medication"),
        (r"I (diagnose|confirm|determine|prescribe|recommend treatment)", "Avoid diagnostic language"),
        (r"take (aspirin|ibuprofen|paracetamol|tylenol) for", "Avoid medication recommendations"),
        (r"you should (take|use|apply) (.*?) for your (symptom|pain|condition)", "Avoid treatment recommendations"),
    ]
    
    # Emergency keywords that require immediate escalation
    EMERGENCY_KEYWORDS = [
        "chest pain", "difficulty breathing", "unconscious", "unresponsive",
        "severe bleeding", "stroke", "heart attack", "suicide", "seizure",
        "can't breathe", "choking", "overdose", "head injury", "loss of consciousness",
        "cardiac arrest", "massive bleeding", "gushing blood", "not breathing"
    ]
    
    # Sensitive topics that need extra care
    SENSITIVE_TOPICS = [
        "mental health", "suicide", "self-harm", "abuse", "domestic violence",
        "sexual assault", "eating disorder", "substance abuse", "depression"
    ]
    
    @classmethod
    def check_safety(cls, text: str) -> Tuple[bool, List[str]]:
        """
        Check if text violates safety guidelines
        Returns: (is_safe, violations)
        """
        violations = []
        text_lower = text.lower()
        
        # Check forbidden patterns
        for pattern, message in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, text_lower):
                violations.append(message)
        
        return len(violations) == 0, violations
    
    @classmethod
    def check_emergency(cls, text: str) -> Tuple[bool, List[str]]:
        """
        Check for emergency keywords
        Returns: (is_emergency, detected_emergencies)
        """
        detected = []
        text_lower = text.lower()
        
        for keyword in cls.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                detected.append(keyword)
        
        return len(detected) > 0, detected
    
    @classmethod
    def check_sensitive_topics(cls, text: str) -> Tuple[bool, List[str]]:
        """Check for sensitive topics requiring special handling"""
        detected = []
        text_lower = text.lower()
        
        for topic in cls.SENSITIVE_TOPICS:
            if topic in text_lower:
                detected.append(topic)
        
        return len(detected) > 0, detected
    
    @classmethod
    def get_safety_response(cls, violations: List[str]) -> str:
        """Generate appropriate safety response for violations"""
        return "I want to remind you that I'm not a medical professional. " \
               "My role is to collect information for your healthcare provider. " \
               "Please consult with a qualified medical professional for any diagnosis or treatment decisions."
    
    @classmethod
    def get_emergency_response(cls, emergencies: List[str]) -> str:
        """Generate emergency escalation response"""
        return "⚠️ **URGENT MEDICAL ATTENTION NEEDED** ⚠️\n\n" \
               "Based on your description, this may be a medical emergency. " \
               "Please seek immediate medical attention:\n" \
               "• Call emergency services (911 in US, 112 in EU) immediately\n" \
               "• Go to the nearest emergency room\n" \
               "• Do not wait for further responses\n\n" \
               f"Detected concerns: {', '.join(emergencies)}\n\n" \
               "**This is not a substitute for emergency medical care.**"
    
    @classmethod
    def get_sensitive_response(cls, topics: List[str]) -> str:
        """Generate response for sensitive topics"""
        return "\n\n💙 **Support Resources** 💙\n\n" \
               "I understand this is a sensitive topic. I want to ensure you get appropriate support. " \
               "Please know that:\n" \
               "• I'm here to help collect information for your healthcare provider\n" \
               "• You can speak with a mental health professional for specialized support\n" \
               "• Crisis helplines are available 24/7 if you need immediate assistance\n\n" \
               "Would you like to continue, or would you prefer to speak with a healthcare professional directly?"