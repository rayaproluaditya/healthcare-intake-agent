import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_backend():
    print("="*60)
    print("TESTING BACKEND API")
    print("="*60)
    
    # 1. Check health
    print("\n1. Checking health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 2. Reset conversation
    print("\n2. Resetting conversation...")
    response = requests.post(f"{BASE_URL}/api/v1/reset")
    print(f"Response: {response.json()}")
    
    # 3. Send first message
    print("\n3. Sending: 'I have a headache'")
    response = requests.post(
        f"{BASE_URL}/api/v1/message",
        json={"message": "I have a headache"}
    )
    result = response.json()
    print(f"Agent: {result['response'][:150]}...")
    print(f"Patient data after message: {result.get('patient_data', {})}")
    
    # 4. Send second message
    print("\n4. Sending: 'It's throbbing on the left side'")
    response = requests.post(
        f"{BASE_URL}/api/v1/message",
        json={"message": "It's throbbing on the left side"}
    )
    result = response.json()
    print(f"Agent: {result['response'][:150]}...")
    print(f"Patient data after message: {result.get('patient_data', {})}")
    
    # 5. Get summary
    print("\n5. Getting patient summary...")
    response = requests.get(f"{BASE_URL}/api/v1/summary")
    summary = response.json()
    print(json.dumps(summary, indent=2, default=str))
    
    # 6. Check if data was extracted
    print("\n6. Checking extracted data...")
    patient_data = summary.get('patient_data', {})
    if patient_data.get('chief_complaint'):
        print(f"✅ Chief complaint: {patient_data['chief_complaint']}")
    else:
        print("❌ No chief complaint extracted")
    
    if patient_data.get('symptoms'):
        print(f"✅ Symptoms: {[s.get('name') for s in patient_data['symptoms']]}")
    else:
        print("❌ No symptoms extracted")

if __name__ == "__main__":
    test_backend()