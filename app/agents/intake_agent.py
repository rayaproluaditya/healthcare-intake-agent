"""
Healthcare Intake Agent - Complete Working Version
Handles patient intake, symptom analysis, and data extraction
"""

from typing import List, Dict, Optional
import requests
from app.agents.safety_guardrails import SafetyGuardrails
from app.vector_db.faiss_client import FAISSVectorDB
from app.models.patient_data import PatientIntake, Symptom, Severity
import json
import logging
import os
import re
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthcareIntakeAgent:
    """Healthcare intake agent using Groq API"""
    
    def __init__(self, vector_db: FAISSVectorDB, model_name: str = None):
        self.vector_db = vector_db
        
        # Load environment variables
        load_dotenv(override=True)
        
        # Get API key and clean it
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.api_key = self.api_key.strip().replace('\n', '').replace('\r', '')
        
        # Get model name - use the working model
        if model_name is None:
            self.model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
        else:
            self.model_name = model_name
        
        self.safety_guardrails = SafetyGuardrails()
        
        # Initialize patient data
        self.patient_data = PatientIntake()
        
        # Conversation history
        self.conversation_history = []
        
        logger.info(f"Agent initialized with model: {self.model_name}")
        logger.info(f"API Key present: {bool(self.api_key)}")
        
        # OPTIMIZED CLINICAL SYSTEM PROMPT
        self.system_prompt = """You are a professional healthcare intake agent. Your role is to collect structured medical information for healthcare providers.

CRITICAL SAFETY RULES:
1. NEVER diagnose conditions (don't say "you have", "you are suffering from", etc.)
2. NEVER recommend specific treatments or medications
3. ALWAYS flag potential emergencies and advise seeking immediate care
4. ALWAYS maintain professional, empathetic boundaries

EMERGENCY FLAGGING - IMMEDIATELY ADVISE EMERGENCY CARE FOR:
- Chest pain with shortness of breath, sweating, or arm/jaw pain → "⚠️ URGENT: Please seek immediate medical attention"
- Severe difficulty breathing → "⚠️ URGENT: Call emergency services immediately"
- Sudden severe headache (worst of life) → "⚠️ URGENT: This could be serious, seek immediate care"
- Loss of consciousness → "⚠️ URGENT: Seek emergency care now"
- Severe bleeding → "⚠️ URGENT: Apply pressure and seek emergency care"

QUESTION STRUCTURE - ALWAYS ASK SYSTEMATICALLY:
When a patient describes a symptom, ALWAYS ask these structured questions:

1. Onset: "When did this start?"
2. Location: "Where exactly do you feel it?"
3. Duration: "How long does it last?"
4. Character: "What does it feel like? (throbbing, sharp, pressure, burning)"
5. Severity: "On a scale of 1-10, how severe is it?"
6. Associated: "Any other symptoms like nausea, fever, dizziness?"

MEDICAL HISTORY COLLECTION:
- Ask: "Do you have any medical conditions?"
- Ask: "What medications do you take?"
- Ask: "Do you have any allergies?"

TONE GUIDELINES - ALWAYS BE:
- Empathetic: "Thank you for sharing", "I understand", "I appreciate you telling me"
- Professional: Use clinical terms, maintain composure
- Thorough: Gather complete information

RESPONSE STRUCTURE - ALWAYS FOLLOW:
1. Acknowledge: "Thank you for sharing that information."
2. Show empathy: "I understand this must be concerning."
3. Ask structured questions: "To better understand, could you tell me: 1. When did it start? 2. Where exactly? 3. How severe?"
4. Collect history: "Do you have any medical conditions or take medications?"
5. Stay safe: Never diagnose, always advise consulting healthcare providers.

EXAMPLE RESPONSES - LEARN FROM THESE:

Example 1 - Headache:
Patient: "I have a headache"
Agent: "Thank you for sharing that. I understand headaches can be uncomfortable. To better understand, could you tell me:
1. When did it start?
2. Where exactly do you feel the pain?
3. On a scale of 1-10, how severe is it?
4. Is it throbbing, sharp, or pressure-like?"

Example 2 - Chest Pain:
Patient: "I have chest pain"
Agent: "Thank you for telling me about your chest pain. For safety, I need to ask:
1. Is the pain accompanied by shortness of breath?
2. Are you sweating?
3. Does the pain spread to your arm, jaw, or back?
⚠️ If you're experiencing any of these, please seek immediate medical attention."

Example 3 - Medical History:
Patient: "I have diabetes"
Agent: "Thank you for sharing your medical history. To help your healthcare provider, could you tell me:
1. What medications do you take for diabetes?
2. How well controlled is your blood sugar?
3. Do you have any other medical conditions?"

Example 4 - Allergy:
Patient: "I'm allergic to penicillin"
Agent: "Thank you for mentioning your penicillin allergy. This is important for your medical record. Have you experienced any other medication allergies? Also, are you currently taking any medications?"

Now, continue the conversation. ALWAYS use structured questions (1, 2, 3) and ALWAYS be empathetic. NEVER give a generic "Can you tell me more about your symptoms?" response."""
        
    def process_message(self, message: str) -> Dict:
        """Process user message and generate response"""
        try:
            logger.info(f"Processing: {message[:100]}...")
            
            # Check for emergencies first
            is_emergency, emergencies = self.safety_guardrails.check_emergency(message)
            if is_emergency:
                logger.warning(f"Emergency detected: {emergencies}")
                return {
                    "response": self.safety_guardrails.get_emergency_response(emergencies),
                    "emergency": True,
                    "patient_data": self.patient_data.dict(),
                    "emergencies": emergencies
                }
            
            # Check for sensitive topics
            is_sensitive, topics = self.safety_guardrails.check_sensitive_topics(message)
            
            # Retrieve relevant medical guidelines from vector DB
            context = self.retrieve_relevant_context(message)
            
            # Generate response using Groq
            response = self.generate_response(message, context)
            
            # Check response safety
            is_safe, violations = self.safety_guardrails.check_safety(response)
            if not is_safe:
                response = self.safety_guardrails.get_safety_response(violations)
            
            # Add sensitive topic handling if needed
            if is_sensitive:
                response = f"{response}\n\n{self.safety_guardrails.get_sensitive_response(topics)}"
            
            # Extract structured data from conversation
            self.extract_patient_data(message, response)
            
            # Store in conversation history
            self.conversation_history.append({"role": "patient", "content": message})
            self.conversation_history.append({"role": "agent", "content": response})
            
            # Debug output
            print(f"\n📊 Current patient data:")
            print(f"  Chief complaint: {self.patient_data.chief_complaint}")
            print(f"  Symptoms: {[s.name for s in self.patient_data.symptoms]}")
            
            return {
                "response": response,
                "emergency": False,
                "sensitive": is_sensitive,
                "patient_data": self.patient_data.dict(),
                "context_used": context[:2] if context else []
            }
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties.",
                "error": str(e),
                "patient_data": self.patient_data.dict()
            }
    
    def retrieve_relevant_context(self, message: str) -> List[str]:
        """Retrieve relevant medical guidelines from vector DB"""
        try:
            results = self.vector_db.similarity_search(message, k=3)
            logger.info(f"Retrieved {len(results)} relevant documents")
            return results
        except Exception as e:
            logger.error(f"Vector DB error: {e}")
            return []
    
    def generate_response(self, message: str, context: List[str]) -> str:
        """Generate response using Groq API"""
        try:
            if not self.api_key:
                logger.error("No API key found")
                return "I'm having trouble connecting. Please check the API configuration."
            
            # Build conversation history
            history_text = ""
            if len(self.conversation_history) > 0:
                recent_history = self.conversation_history[-4:]
                history_lines = []
                for h in recent_history:
                    history_lines.append(f"{h['role'].upper()}: {h['content']}")
                history_text = "\n".join(history_lines) + "\n\n"
            
            # Build user message with specific instructions to avoid generic responses
            user_message = f"""{history_text}Patient: {message}

IMPORTANT: As a healthcare intake agent, provide a STRUCTURED, EMPATHETIC response.
NEVER just say "Can you tell me more about your symptoms?"
ALWAYS ask specific numbered questions (1., 2., 3.) about:
- Onset (when it started)
- Location (where exactly)
- Severity (1-10 scale)
- Character (throbbing, sharp, etc.)
- Associated symptoms

Follow this format:
"Thank you for sharing. I understand. To better understand, could you tell me:
1. [specific question]
2. [specific question]
3. [specific question]"

Respond now with a professional, structured follow-up:"""
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "model": self.model_name,
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            logger.info(f"Sending to Groq with model: {self.model_name}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content']
                logger.info("Successfully received response")
                return response_text
            else:
                logger.error(f"Groq error: {response.status_code}")
                # Fallback to structured response
                return "Thank you for sharing. To better understand, could you tell me:\n1. When did this start?\n2. Where exactly do you feel it?\n3. On a scale of 1-10, how severe is it?"
            
        except Exception as e:
            logger.error(f"Exception: {e}")
            return "Thank you for sharing. To better understand, could you tell me:\n1. When did this start?\n2. Where exactly do you feel it?\n3. On a scale of 1-10, how severe is it?"
    
    def extract_patient_data(self, message: str, response: str):
        """Extract structured patient data from conversation"""
        try:
            message_lower = message.lower()
            print(f"\n🔍 Extracting data from: {message}")
            
            # Extract chief complaint
            if not self.patient_data.chief_complaint:
                complaint_keywords = {
                    "headache": "Headache",
                    "nausea": "Nausea",
                    "pain": "Pain",
                    "cough": "Cough",
                    "fever": "Fever",
                    "fatigue": "Fatigue",
                    "dizziness": "Dizziness",
                    "chest pain": "Chest Pain"
                }
                for keyword, complaint in complaint_keywords.items():
                    if keyword in message_lower:
                        self.patient_data.chief_complaint = complaint
                        print(f"✅ Chief complaint: {complaint}")
                        break
            
            # Extract symptoms
            symptom_keywords = {
                "headache": "Headache",
                "nausea": "Nausea",
                "vomiting": "Vomiting",
                "pain": "Pain",
                "fever": "Fever",
                "cough": "Cough"
            }
            
            for keyword, symptom_name in symptom_keywords.items():
                if keyword in message_lower:
                    existing_names = [s.name.lower() for s in self.patient_data.symptoms]
                    if keyword not in existing_names:
                        symptom = Symptom(name=symptom_name)
                        self.patient_data.symptoms.append(symptom)
                        print(f"✅ Added symptom: {symptom_name}")
            
            # Update symptom details
            if self.patient_data.symptoms:
                current_symptom = self.patient_data.symptoms[-1]
                
                # Extract duration
                duration_match = re.search(r'(\d+)\s*days?', message_lower)
                if duration_match and not current_symptom.duration:
                    current_symptom.duration = f"{duration_match.group(1)} days"
                    print(f"✅ Added duration: {current_symptom.duration}")
                
                # Extract severity
                severity_match = re.search(r'(\d+)\s*out of 10', message_lower)
                if severity_match and not current_symptom.severity:
                    severity_score = int(severity_match.group(1))
                    if severity_score <= 3:
                        current_symptom.severity = "mild"
                    elif severity_score <= 7:
                        current_symptom.severity = "moderate"
                    else:
                        current_symptom.severity = "severe"
                    print(f"✅ Added severity: {current_symptom.severity}")
                
                # Extract location
                if "left" in message_lower and not current_symptom.location:
                    current_symptom.location = "left side"
                    print(f"✅ Added location: left side")
                elif "right" in message_lower and not current_symptom.location:
                    current_symptom.location = "right side"
                    print(f"✅ Added location: right side")
            
            # Extract medical conditions
            if "diabetes" in message_lower and "Diabetes" not in self.patient_data.preexisting_conditions:
                self.patient_data.preexisting_conditions.append("Diabetes")
                print(f"✅ Added condition: Diabetes")
            if "high blood pressure" in message_lower and "Hypertension" not in self.patient_data.preexisting_conditions:
                self.patient_data.preexisting_conditions.append("Hypertension")
                print(f"✅ Added condition: Hypertension")
            
            # Extract allergies
            if "allergic" in message_lower or "allergy" in message_lower:
                if "penicillin" in message_lower and "Penicillin" not in self.patient_data.allergies:
                    self.patient_data.allergies.append("Penicillin")
                    print(f"✅ Added allergy: Penicillin")
            
            # Extract medications
            if "metformin" in message_lower and "Metformin" not in self.patient_data.medications:
                self.patient_data.medications.append("Metformin")
                print(f"✅ Added medication: Metformin")
            if "lisinopril" in message_lower and "Lisinopril" not in self.patient_data.medications:
                self.patient_data.medications.append("Lisinopril")
                print(f"✅ Added medication: Lisinopril")
            
        except Exception as e:
            print(f"❌ Extraction error: {e}")
            logger.error(f"Data extraction error: {e}")
    
    def get_summary(self) -> Dict:
        """Get structured summary for medical professional"""
        try:
            # Calculate completion percentage
            total_fields = 6
            completed_fields = 0
            
            if self.patient_data.chief_complaint:
                completed_fields += 1
            if self.patient_data.symptoms:
                completed_fields += 1
            if self.patient_data.preexisting_conditions:
                completed_fields += 1
            if self.patient_data.allergies:
                completed_fields += 1
            if self.patient_data.medications:
                completed_fields += 1
            if self.patient_data.age or self.patient_data.gender:
                completed_fields += 1
            
            completion_percentage = (completed_fields / total_fields) * 100 if total_fields > 0 else 0
            
            return {
                "patient_data": self.patient_data.dict(),
                "conversation_history": self.conversation_history,
                "completion_percentage": completion_percentage,
                "recommendation": "Ready for provider review" if completion_percentage > 50 else "Additional information needed",
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in get_summary: {e}")
            return {
                "patient_data": self.patient_data.dict(),
                "conversation_history": self.conversation_history,
                "error": str(e)
            }
    
    def reset_conversation(self):
        """Reset the conversation and patient data"""
        self.patient_data = PatientIntake()
        self.conversation_history = []
        logger.info("Conversation reset")