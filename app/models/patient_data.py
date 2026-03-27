from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class Severity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"

class Symptom(BaseModel):
    """Individual symptom details"""
    name: str = Field(..., description="Symptom name")
    duration: Optional[str] = Field(None, description="How long the symptom has been present")
    severity: Optional[Severity] = Field(None, description="Symptom severity")
    description: Optional[str] = Field(None, description="Detailed description")
    location: Optional[str] = Field(None, description="Location on/in body")
    triggers: Optional[List[str]] = Field(default_factory=list, description="What triggers the symptom")
    relieving_factors: Optional[List[str]] = Field(default_factory=list, description="What relieves the symptom")

class PatientIntake(BaseModel):
    """Structured patient intake data for medical professionals"""
    
    # Demographics
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[Gender] = None
    
    # Medical Information
    chief_complaint: str = Field(default="", description="Main reason for consultation")
    symptoms: List[Symptom] = Field(default_factory=list)
    
    # Medical History
    preexisting_conditions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    surgical_history: List[str] = Field(default_factory=list)
    
    # Lifestyle
    smoking_status: Optional[str] = Field(None, description="Never, former, current")
    alcohol_consumption: Optional[str] = Field(None, description="Frequency and quantity")
    exercise_frequency: Optional[str] = Field(None, description="How often they exercise")
    
    # Vital Signs (if available)
    temperature: Optional[float] = Field(None, ge=95, le=108)
    blood_pressure: Optional[str] = None
    heart_rate: Optional[int] = Field(None, ge=40, le=200)
    
    # Additional Information
    additional_notes: Optional[str] = None
    consultation_date: datetime = Field(default_factory=datetime.now)
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError('Age must be between 0 and 120')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and (v < 95 or v > 108):
            raise ValueError('Temperature must be between 95°F and 108°F')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "age": 35,
                "gender": "male",
                "chief_complaint": "Persistent headache for 3 days",
                "symptoms": [
                    {
                        "name": "headache",
                        "duration": "3 days",
                        "severity": "moderate",
                        "location": "frontal region",
                        "description": "Throbbing pain"
                    }
                ]
            }
        }