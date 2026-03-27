#!/usr/bin/env python
"""
Test script for healthcare intake agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health Check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_conversation():
    """Test full conversation flow"""
    
    # Test messages covering different scenarios
    test_scenarios = [
        {
            "name": "Basic Symptom",
            "messages": [
                "I've been having a headache for the past 3 days",
                "It's a throbbing pain on the left side, and it's pretty severe, about 7 out of 10",
                "I also feel a bit nauseous when it gets bad, and light bothers me"
            ]
        },
        {
            "name": "Medical History",
            "messages": [
                "I have high blood pressure that I take medication for",
                "I take lisinopril 10mg once daily",
                "I'm also allergic to penicillin"
            ]
        },
        {
            "name": "Emergency Detection",
            "messages": [
                "I'm having chest pain and difficulty breathing"
            ]
        }
    ]
    
    print("\n" + "="*60)
    print("HEALTHCARE INTAKE AGENT TEST")
    print("="*60)
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing Scenario: {scenario['name']}")
        print("-"*40)
        
        for message in scenario['messages']:
            print(f"\n👤 Patient: {message}")
            
            # Send message
            try:
                response = requests.post(
                    f"{BASE_URL}/message",
                    json={"message": message},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"🤖 Agent: {result['response'][:200]}...")
                    
                    if result.get('emergency'):
                        print("⚠️  EMERGENCY DETECTED - Escalation triggered")
                        break
                else:
                    print(f"❌ Error: {response.status_code} - {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
                break
            
            time.sleep(1)  # Small delay between messages
        
        print("-"*40)
    
    # Get summary
    print("\n" + "="*60)
    print("PATIENT SUMMARY")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/summary")
        if response.status_code == 200:
            summary = response.json()
            print(json.dumps(summary, indent=2, default=str))
        else:
            print(f"❌ Failed to get summary: {response.status_code}")
    except Exception as e:
        print(f"❌ Summary request failed: {e}")
    
    # Get status
    print("\n" + "="*60)
    print("AGENT STATUS")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print(json.dumps(status, indent=2))
    except Exception as e:
        print(f"❌ Status request failed: {e}")

def test_reset():
    """Test conversation reset"""
    print("\n" + "="*60)
    print("TESTING RESET FUNCTIONALITY")
    print("="*60)
    
    try:
        response = requests.post(f"{BASE_URL}/reset")
        if response.status_code == 200:
            print(f"✅ Reset successful: {response.json()}")
        else:
            print(f"❌ Reset failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Reset request failed: {e}")

if __name__ == "__main__":
    print("Starting Healthcare Intake Agent Tests...")
    print("Make sure the application is running (docker-compose up)")
    
    # Wait for service to be ready
    print("Waiting for service to be ready...")
    time.sleep(3)
    
    # Run tests
    if test_health():
        test_conversation()
        test_reset()
    else:
        print("\n❌ Cannot proceed with tests. Make sure the application is running.")
        print("Run: docker-compose up --build")