"""
Healthcare Intake Agent - Working Streamlit Frontend with Auto-refresh
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Healthcare Intake Agent",
    page_icon="🏥",
    layout="wide"
)

# Backend URL
BACKEND_URL = "http://localhost:8000"
API_URL = f"{BACKEND_URL}/api/v1"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "patient_data" not in st.session_state:
    st.session_state.patient_data = None
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# Helper functions
def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(message):
    try:
        response = requests.post(
            f"{API_URL}/message",
            json={"message": message},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_summary():
    """Get patient summary from backend"""
    try:
        response = requests.get(f"{API_URL}/summary", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Summary error: {e}")
        return None

def reset_conversation():
    try:
        response = requests.post(f"{API_URL}/reset")
        if response.status_code == 200:
            st.session_state.messages = []
            st.session_state.patient_data = None
            st.session_state.last_update = time.time()
            return True
        return False
    except:
        return False

# Main UI
st.title("🏥 Healthcare Intake Agent")
st.markdown("Your AI-powered medical intake assistant")

# Check backend connection
if not check_backend():
    st.error("❌ Cannot connect to backend. Make sure it's running: python -m uvicorn app.main:app --reload")
    st.stop()

st.success("✅ Connected to backend")

# Create two columns
col1, col2 = st.columns([2, 1])

# Main chat column
with col1:
    st.markdown("### 💬 Conversation")
    
    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Describe your symptoms..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                result = send_message(prompt)
                
                if "error" in result:
                    response_text = f"❌ {result['error']}"
                    st.error(response_text)
                else:
                    response_text = result.get("response", "I couldn't process that.")
                    st.markdown(response_text)
                    
                    # Check for emergency
                    if result.get("emergency"):
                        st.error("⚠️ **URGENT: Please seek immediate medical attention!**")
                
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                # Update timestamp to trigger sidebar refresh
                st.session_state.last_update = time.time()
        
        st.rerun()

# Sidebar column with auto-refresh
with col2:
    st.markdown("### 📋 Patient Summary")
    
    # Reset button
    if st.button("🔄 Reset Conversation", use_container_width=True):
        if reset_conversation():
            st.success("Conversation reset!")
            st.rerun()
        else:
            st.error("Failed to reset")
    
    st.markdown("---")
    
    # Auto-refresh placeholder for summary
    summary_placeholder = st.empty()
    
    # Refresh button
    if st.button("🔄 Refresh Summary", use_container_width=True):
        st.session_state.last_update = time.time()
        st.rerun()
    
    st.markdown("---")
    
    # Display patient summary with auto-refresh
    with summary_placeholder.container():
        # Get latest summary
        summary = get_summary()
        
        if summary and summary.get("patient_data"):
            data = summary["patient_data"]
            
            # Chief complaint
            if data.get("chief_complaint"):
                st.info(f"**Chief Complaint:** {data['chief_complaint']}")
            else:
                st.info("No chief complaint recorded yet")
            
            # Symptoms
            if data.get("symptoms"):
                st.markdown("**📝 Symptoms:**")
                for symptom in data["symptoms"]:
                    st.write(f"• **{symptom.get('name', 'Unknown')}**")
                    if symptom.get("duration"):
                        st.caption(f"  Duration: {symptom['duration']}")
                    if symptom.get("severity"):
                        severity_value = symptom.get('severity')
                        if hasattr(severity_value, 'value'):
                            severity_value = severity_value.value
                        st.caption(f"  Severity: {severity_value}")
                    if symptom.get("location"):
                        st.caption(f"  Location: {symptom['location']}")
                    st.markdown("---")
            else:
                st.write("No symptoms recorded yet")
            
            # Medical history
            if data.get("preexisting_conditions"):
                st.markdown("**🏥 Medical History:**")
                for condition in data["preexisting_conditions"]:
                    st.write(f"• {condition}")
            else:
                st.write("No medical history recorded yet")
            
            # Allergies
            if data.get("allergies"):
                st.markdown("**⚠️ Allergies:**")
                for allergy in data["allergies"]:
                    st.warning(f"• {allergy}")
            else:
                st.write("No allergies recorded")
            
            # Medications
            if data.get("medications"):
                st.markdown("**💊 Medications:**")
                for med in data["medications"]:
                    st.write(f"• {med}")
            else:
                st.write("No medications recorded")
            
            # Demographics
            if data.get("age") or data.get("gender"):
                st.markdown("**👤 Demographics:**")
                if data.get("age"):
                    st.write(f"Age: {data['age']}")
                if data.get("gender"):
                    st.write(f"Gender: {data['gender']}")
            
            # Completion percentage
            if summary.get("completion_percentage"):
                st.markdown("---")
                st.markdown("**Data Collection Progress**")
                st.progress(summary["completion_percentage"] / 100)
                st.caption(f"{summary['completion_percentage']:.0f}% Complete")
            
            # Last updated
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        else:
            st.info("💡 Start a conversation to see patient data here")
            st.write("Try: 'I have a headache'")

# Footer
st.markdown("---")
st.caption("⚠️ This is an AI assistant for medical intake. Not a substitute for professional medical advice.")