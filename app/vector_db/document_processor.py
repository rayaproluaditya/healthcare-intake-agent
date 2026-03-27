import os
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process medical documents for vector database"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        os.makedirs(data_path, exist_ok=True)
    
    def process_medical_guidelines(self) -> List[str]:
        """Process medical guidelines files"""
        documents = []
        
        # Process text files
        if os.path.exists(self.data_path):
            for filename in os.listdir(self.data_path):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.data_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Chunk the content
                            chunks = self._chunk_text(content)
                            documents.extend(chunks)
                            logger.info(f"Processed {filename}: {len(chunks)} chunks")
                    except Exception as e:
                        logger.error(f"Error processing {filename}: {e}")
        
        return documents
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks"""
        # Split by paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            if not para.strip():
                continue
                
            if current_length + len(para) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [para]
                current_length = len(para)
            else:
                current_chunk.append(para)
                current_length += len(para)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def create_medical_dataset(self) -> List[str]:
        """Create comprehensive medical guidelines dataset"""
        
        guidelines = [
            """
            CDC Guidelines for Symptom Assessment:
            
            Fever Assessment:
            - Temperature > 100.4°F (38°C) is considered a fever
            - Acute fever: < 7 days duration
            - Subacute fever: 7-14 days duration
            - Chronic fever: > 14 days duration
            - Associated symptoms: chills, sweating, dehydration, headache
            - Red flags: fever in infants < 3 months, fever > 104°F, fever with stiff neck, confusion, or difficulty breathing
            - When to seek emergency care: fever with seizure, severe headache, difficulty breathing, or altered mental status
            
            Respiratory Symptom Assessment:
            - Cough duration: acute (< 3 weeks), subacute (3-8 weeks), chronic (> 8 weeks)
            - Cough characteristics: dry, productive, barking, whooping
            - Sputum assessment: color (clear, yellow, green, bloody), consistency, amount
            - Shortness of breath: assess onset (sudden vs gradual), triggers, severity (mild, moderate, severe)
            - Associated symptoms: fever, chest pain, wheezing, fatigue
            - Emergency warning signs: difficulty breathing, chest pain, blue lips/fingers, confusion
            
            Headache Assessment Protocol:
            - Tension-type: bilateral location, pressing/tightening quality, mild-moderate severity
            - Migraine: unilateral location, throbbing quality, moderate-severe severity, with nausea/photophobia
            - Cluster: severe, unilateral, orbital/supraorbital location, with autonomic symptoms
            - Red flags (SNOOP): Sudden onset, Neurological symptoms, Onset after age 50, Pattern change, Precipitated by Valsalva
            - Emergency: "thunderclap" headache, headache with fever, headache after head injury
            
            Gastrointestinal Symptom Assessment:
            - Abdominal pain: location (quadrants), quality (cramping, sharp, dull), severity, timing
            - Nausea/vomiting: duration, frequency, associated symptoms, blood content
            - Diarrhea: duration, frequency, consistency, bloody or not, associated symptoms
            - Constipation: frequency, consistency, straining, duration
            - Red flags: severe pain, persistent vomiting, bloody stools, dehydration, weight loss
            
            Cardiovascular Symptom Assessment:
            - Chest pain: location, radiation, quality (pressure, burning, stabbing), duration, triggers
            - Palpitations: onset, duration, frequency, associated symptoms
            - Shortness of breath: exertion vs rest, orthopnea, paroxysmal nocturnal dyspnea
            - Edema: location, timing, pitting vs non-pitting
            - Emergency: chest pain with sweating, nausea, shortness of breath, pain radiating to arm/jaw
            
            Neurological Symptom Assessment:
            - Dizziness/vertigo: onset, duration, triggers, associated symptoms
            - Numbness/weakness: location, onset, progression, associated symptoms
            - Seizures: description, duration, post-ictal state, frequency
            - Vision changes: onset, duration, unilateral/bilateral, associated symptoms
            - Emergency: sudden weakness, facial droop, speech difficulty, sudden severe headache
            
            Mental Health Assessment:
            - Mood: changes in mood, duration, impact on daily activities
            - Anxiety: triggers, physical symptoms, coping mechanisms
            - Depression: sleep changes, appetite changes, anhedonia, suicidal thoughts
            - Sleep patterns: difficulty falling asleep, staying asleep, early waking
            - Emergency: suicidal ideation with plan, homicidal ideation, psychosis
            
            Medication History:
            - Current medications: name, dose, frequency, reason, duration
            - Over-the-counter medications: regular use, reason
            - Supplements: vitamins, herbal supplements, reason
            - Medication allergies: specific reaction, severity
            - Medication adherence: compliance, missed doses, reasons
            
            Past Medical History:
            - Chronic conditions: diabetes, hypertension, heart disease, lung disease, kidney disease
            - Surgical history: procedures, dates, complications
            - Hospitalizations: reasons, dates, outcomes
            - Trauma: injuries, dates, sequelae
            - Vaccination status: COVID-19, influenza, pneumonia, others
            
            Social History:
            - Tobacco use: status (never, former, current), duration, quantity
            - Alcohol use: frequency, quantity, pattern
            - Substance use: recreational drugs, frequency, route
            - Occupation: type, exposures, physical demands
            - Living situation: housing, support system, activities of daily living
            - Exercise: frequency, type, duration
            - Diet: typical intake, restrictions, preferences
            
            Review of Systems:
            - Constitutional: fever, chills, fatigue, weight changes, night sweats
            - HEENT: headaches, vision changes, hearing loss, sore throat, nasal congestion
            - Cardiovascular: chest pain, palpitations, edema, claudication
            - Respiratory: cough, sputum, shortness of breath, wheezing
            - Gastrointestinal: nausea, vomiting, diarrhea, constipation, abdominal pain
            - Genitourinary: dysuria, frequency, hematuria, sexual function
            - Musculoskeletal: joint pain, swelling, stiffness, weakness
            - Neurological: numbness, weakness, seizures, coordination
            - Psychiatric: depression, anxiety, mood changes, sleep
            - Endocrine: temperature intolerance, weight changes, thirst, fatigue
            - Hematologic: bleeding, bruising, lymphadenopathy
            - Allergic/Immunologic: allergies, autoimmune conditions
            """
        ]
        
        # Save to file
        output_path = os.path.join(self.data_path, "comprehensive_guidelines.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(guidelines))
        
        logger.info(f"Created medical dataset at {output_path}")
        return guidelines