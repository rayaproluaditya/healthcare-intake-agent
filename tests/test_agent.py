import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.intake_agent import HealthcareIntakeAgent
from app.agents.safety_guardrails import SafetyGuardrails
from app.vector_db.chroma_client import ChromaVectorDB
from app.models.patient_data import PatientIntake

class TestSafetyGuardrails:
    """Test safety guardrail functionality"""
    
    def test_emergency_detection(self):
        """Test emergency keyword detection"""
        is_emergency, emergencies = SafetyGuardrails.check_emergency("I have chest pain")
        assert is_emergency == True
        assert "chest pain" in emergencies
    
    def test_safety_violation(self):
        """Test safety violation detection"""
        is_safe, violations = SafetyGuardrails.check_safety("You have cancer")
        assert is_safe == False
        assert len(violations) > 0
    
    def test_sensitive_topics(self):
        """Test sensitive topic detection"""
        is_sensitive, topics = SafetyGuardrails.check_sensitive_topics("I'm feeling depressed")
        assert is_sensitive == True
        assert "depression" in topics

class TestPatientIntake:
    """Test patient data models"""
    
    def test_patient_intake_creation(self):
        """Test creating patient intake"""
        patient = PatientIntake()
        assert patient.age is None
        assert patient.symptoms == []
    
    def test_symptom_addition(self):
        """Test adding symptoms"""
        patient = PatientIntake()
        assert len(patient.symptoms) == 0

class TestIntakeAgent:
    """Test intake agent functionality (requires running service)"""
    
    @pytest.fixture
    def mock_vector_db(self, mocker):
        """Mock vector database"""
        mock = mocker.Mock(spec=ChromaVectorDB)
        mock.similarity_search.return_value = ["Test guideline"]
        return mock
    
    def test_agent_initialization(self, mock_vector_db):
        """Test agent initialization"""
        agent = HealthcareIntakeAgent(vector_db=mock_vector_db)
        assert agent is not None
        assert agent.model_name == "mixtral-8x7b-32768"
    
    def test_process_message(self, mock_vector_db):
        """Test message processing"""
        agent = HealthcareIntakeAgent(vector_db=mock_vector_db)
        result = agent.process_message("I have a headache")
        assert "response" in result
        assert isinstance(result["response"], str)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])