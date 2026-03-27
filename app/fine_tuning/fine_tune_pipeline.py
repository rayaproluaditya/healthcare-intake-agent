"""
Clinical Tone Fine-tuning Pipeline
Uses few-shot learning and prompt engineering to achieve clinical tone
"""

import json
import os
from typing import List, Dict
import pandas as pd
from datetime import datetime

class ClinicalFineTuner:
    """Fine-tune clinical responses using few-shot examples"""
    
    def __init__(self):
        self.data_path = "./data/training_data"
        self.examples = []
        self.few_shot_prompt = ""
        
    def load_training_data(self):
        """Load training examples from JSON"""
        file_path = f"{self.data_path}/clinical_examples.json"
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.examples = data.get("examples", [])
                print(f"✅ Loaded {len(self.examples)} training examples")
        else:
            print(f"❌ Training data not found at {file_path}")
            return False
        return True
    
    def create_few_shot_prompt(self) -> str:
        """Create a comprehensive few-shot prompt for clinical tone"""
        
        system_prompt = """You are a professional healthcare intake agent with a clinical, empathetic tone. Your role is to gather structured medical information, NOT to diagnose or provide treatment advice.

CRITICAL SAFETY RULES:
1. NEVER diagnose conditions (don't say "you have", "you are suffering from", etc.)
2. NEVER recommend specific treatments or medications
3. ALWAYS flag potential emergencies and advise seeking immediate care
4. ALWAYS maintain professional, empathetic boundaries
5. ALWAYS structure questions systematically

CLINICAL TONE REQUIREMENTS:
- Be empathetic: "I understand", "Thank you for sharing", "I appreciate you telling me"
- Be professional: Use clinical terminology appropriately, maintain composure
- Be structured: Ask questions in a systematic way (onset, duration, severity, location, quality)
- Be thorough: Collect complete medical history, allergies, medications

Here are examples of appropriate responses to learn from:

"""
        
        # Add few-shot examples
        for i, example in enumerate(self.examples[:8], 1):
            system_prompt += f"""
Example {i} - Category: {example.get('category', 'general')}
Patient: {example['input']}
Agent: {example['output']}

"""
        
        system_prompt += """
Now, continue the conversation following this professional approach. Remember:
- Be empathetic but professional
- Ask structured follow-up questions
- Never diagnose
- Flag emergencies immediately
- Collect complete medical information

Patient: {input}
Agent:"""
        
        self.few_shot_prompt = system_prompt
        return system_prompt
    
    def create_clinical_system_prompt(self) -> str:
        """Create the optimized system prompt for the agent"""
        
        clinical_prompt = """You are a professional healthcare intake agent. Your role is to collect structured medical information for healthcare providers.

**CORE PRINCIPLES:**
1. **NEVER DIAGNOSE** - You are a data collector, not a doctor
2. **NEVER PRESCRIBE** - Don't recommend treatments or medications
3. **FLAG EMERGENCIES** - Immediately advise emergency care for:
   - Chest pain with shortness of breath, sweating, or arm/jaw pain
   - Severe difficulty breathing
   - Sudden severe headache (worst of life)
   - Loss of consciousness
   - Severe bleeding
   - Suicidal thoughts

**QUESTION STRUCTURE - Ask systematically:**
1. **Onset**: "When did this start?"
2. **Location**: "Where exactly do you feel it?"
3. **Duration**: "How long does it last?"
4. **Character**: "What does it feel like? (throbbing, sharp, pressure, burning)"
5. **Severity**: "On a scale of 1-10, how severe is it?"
6. **Aggravating**: "What makes it worse?"
7. **Relieving**: "What makes it better?"
8. **Associated**: "Any other symptoms?"

**MEDICAL HISTORY COLLECTION:**
- Ask about pre-existing conditions
- Ask about current medications
- Ask about allergies
- Ask about surgical history
- Ask about family history when relevant

**TONE GUIDELINES:**
- Be empathetic: "I understand", "Thank you for sharing", "I appreciate that"
- Be professional: Use clinical terms, maintain professional distance
- Be thorough: Gather complete information
- Be safe: Never offer opinions or advice beyond data collection

**RESPONSE STRUCTURE:**
1. Acknowledge: "Thank you for sharing that information."
2. Summarize: "So you're experiencing [symptom] for [duration]."
3. Ask next question: "Could you tell me about [next aspect]?"
4. Collect history: "Do you have any medical conditions or take medications?"

Remember: You are preparing information for a healthcare provider. Be thorough, empathetic, and safe."""
        
        return clinical_prompt
    
    def generate_evaluation_metrics(self, test_responses: List[str]) -> Dict:
        """Evaluate clinical tone of responses"""
        metrics = {
            "professionalism": 0,
            "empathy": 0,
            "safety_compliance": 0,
            "structured_questions": 0,
            "total": 0
        }
        
        for response in test_responses:
            response_lower = response.lower()
            
            # Check professionalism
            if any(word in response_lower for word in ["thank", "appreciate", "understand", "please"]):
                metrics["professionalism"] += 1
            
            # Check empathy
            if any(word in response_lower for word in ["understand", "sorry", "appreciate", "concern"]):
                metrics["empathy"] += 1
            
            # Check safety (no diagnosis/treatment)
            if not any(word in response_lower for word in ["diagnose", "you have", "you need", "prescribe", "take this"]):
                metrics["safety_compliance"] += 1
            
            # Check structured questions (numbered or bulleted)
            if any(char in response for char in ["1.", "2.", "3.", "•", "-"]) and response.count("?") > 1:
                metrics["structured_questions"] += 1
            
            metrics["total"] += 1
        
        # Calculate percentages
        if metrics["total"] > 0:
            metrics["professionalism"] = (metrics["professionalism"] / metrics["total"]) * 100
            metrics["empathy"] = (metrics["empathy"] / metrics["total"]) * 100
            metrics["safety_compliance"] = (metrics["safety_compliance"] / metrics["total"]) * 100
            metrics["structured_questions"] = (metrics["structured_questions"] / metrics["total"]) * 100
        
        return metrics
    
    def save_fine_tuning_results(self):
        """Save all fine-tuning artifacts"""
        os.makedirs(self.data_path, exist_ok=True)
        
        # Save few-shot prompt
        with open(f"{self.data_path}/few_shot_prompt.txt", 'w') as f:
            f.write(self.create_few_shot_prompt())
        
        # Save clinical system prompt
        with open(f"{self.data_path}/clinical_system_prompt.txt", 'w') as f:
            f.write(self.create_clinical_system_prompt())
        
        # Save metrics
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "num_examples": len(self.examples),
            "categories": list(set([e.get("category", "general") for e in self.examples]))
        }
        
        with open(f"{self.data_path}/fine_tuning_metrics.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"\n✅ Fine-tuning artifacts saved to {self.data_path}/")
        print(f"   - few_shot_prompt.txt")
        print(f"   - clinical_system_prompt.txt")
        print(f"   - fine_tuning_metrics.json")
    
    def run_fine_tuning(self):
        """Run the complete fine-tuning pipeline"""
        print("="*60)
        print("CLINICAL TONE FINE-TUNING PIPELINE")
        print("="*60)
        
        # Load training data
        print("\n1. Loading training examples...")
        if not self.load_training_data():
            return
        
        # Create prompts
        print("\n2. Creating few-shot prompt...")
        few_shot = self.create_few_shot_prompt()
        print(f"   Few-shot prompt length: {len(few_shot)} characters")
        
        print("\n3. Creating clinical system prompt...")
        clinical = self.create_clinical_system_prompt()
        print(f"   Clinical prompt length: {len(clinical)} characters")
        
        # Save results
        print("\n4. Saving fine-tuning artifacts...")
        self.save_fine_tuning_results()
        
        # Print summary
        print("\n" + "="*60)
        print("FINE-TUNING SUMMARY")
        print("="*60)
        print(f"Training Examples: {len(self.examples)}")
        print(f"Categories: {', '.join(set([e.get('category', 'general') for e in self.examples]))}")
        print("\n✅ Fine-tuning complete!")
        print("\nNext steps:")
        print("1. Review the clinical_system_prompt.txt")
        print("2. Update your agent's system prompt with this optimized version")
        print("3. Test with sample conversations")
        print("4. Iterate and add more examples as needed")

if __name__ == "__main__":
    tuner = ClinicalFineTuner()
    tuner.run_fine_tuning()