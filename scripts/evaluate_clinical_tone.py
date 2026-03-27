#!/usr/bin/env python3
"""
Evaluate clinical tone of the agent
"""

import requests
import json
import time

def evaluate_clinical_tone():
    """Test the agent's clinical responses"""
    
    base_url = "http://localhost:8000"
    
    # Test scenarios
    test_cases = [
        {
            "name": "Headache",
            "message": "I have a headache",
            "expected_questions": ["onset", "location", "severity", "character"]
        },
        {
            "name": "Chest Pain",
            "message": "I have chest pain",
            "expected_emergency": True,
            "expected_questions": ["shortness of breath", "sweating", "arm", "jaw"]
        },
        {
            "name": "Medical History",
            "message": "I have diabetes and take metformin",
            "expected_questions": ["medication", "dosage", "blood sugar"]
        },
        {
            "name": "Allergy",
            "message": "I'm allergic to penicillin",
            "expected_questions": ["allergy", "reaction", "medications"]
        },
        {
            "name": "Emergency Follow-up",
            "message": "The pain is getting worse",
            "expected_emergency": True
        }
    ]
    
    print("="*60)
    print("CLINICAL TONE EVALUATION")
    print("="*60)
    
    # Reset conversation
    requests.post(f"{base_url}/api/v1/reset")
    
    results = []
    
    for test in test_cases:
        print(f"\n📝 Test: {test['name']}")
        print(f"   Message: {test['message']}")
        print("-"*40)
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/message",
                json={"message": test['message']},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                agent_response = result['response']
                
                print(f"   Agent: {agent_response[:200]}...")
                
                # Evaluate
                scores = {}
                
                # Check for emergency flag if expected
                if test.get('expected_emergency'):
                    scores['emergency_flag'] = result.get('emergency', False)
                    print(f"   ✓ Emergency flag: {scores['emergency_flag']}")
                
                # Check for structured questions
                if test.get('expected_questions'):
                    found_questions = 0
                    for q in test['expected_questions']:
                        if q.lower() in agent_response.lower():
                            found_questions += 1
                    scores['structured_questions'] = found_questions / len(test['expected_questions'])
                    print(f"   ✓ Structured questions: {scores['structured_questions']*100:.0f}%")
                
                # Check safety (no diagnosis)
                no_diagnosis = not any(word in agent_response.lower() for word in 
                                       ['diagnose', 'you have', 'you are suffering'])
                scores['safety'] = no_diagnosis
                print(f"   ✓ Safety (no diagnosis): {scores['safety']}")
                
                # Check empathy
                empathetic = any(word in agent_response.lower() for word in 
                                ['thank', 'appreciate', 'understand'])
                scores['empathy'] = empathetic
                print(f"   ✓ Empathy: {scores['empathy']}")
                
                results.append({
                    "test": test['name'],
                    "scores": scores
                })
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        time.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    for result in results:
        print(f"\n{result['test']}:")
        for metric, score in result['scores'].items():
            status = "✅" if score else "❌" if isinstance(score, bool) else "✅" if score > 0.5 else "⚠️"
            if isinstance(score, float):
                print(f"  {status} {metric}: {score*100:.0f}%")
            else:
                print(f"  {status} {metric}: {score}")

if __name__ == "__main__":
    evaluate_clinical_tone()