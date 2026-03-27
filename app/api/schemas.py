from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MessageRequest(BaseModel):
    """Request schema for message endpoint"""
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "message": "I've had a headache for the past 3 days"
            }
        }

class MessageResponse(BaseModel):
    """Response schema for message endpoint"""
    response: str
    emergency: bool = False
    sensitive: bool = False
    patient_data: Optional[Dict[str, Any]] = None
    context_used: Optional[List[str]] = None

class SummaryResponse(BaseModel):
    """Response schema for summary endpoint"""
    patient_data: Dict[str, Any]
    conversation_complete: bool
    recommendation: str
    clinical_summary: Optional[str] = None
    completeness: Optional[Dict[str, Any]] = None