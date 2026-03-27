from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional
from app.agents.intake_agent import HealthcareIntakeAgent
from app.api.schemas import MessageRequest, MessageResponse, SummaryResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Global agent instance (will be injected)
agent = None

def get_agent():
    """Dependency to get agent instance"""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return agent

@router.post("/message", response_model=MessageResponse)
async def process_message(
    request: MessageRequest,
    agent: HealthcareIntakeAgent = Depends(get_agent)
):
    """Process a message from the patient"""
    try:
        result = agent.process_message(request.message)
        return MessageResponse(
            response=result["response"],
            emergency=result.get("emergency", False),
            sensitive=result.get("sensitive", False),
            patient_data=result.get("patient_data"),
            context_used=result.get("context_used", [])
        )
    except Exception as e:
        logger.error(f"Error in message endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    agent: HealthcareIntakeAgent = Depends(get_agent)
):
    """Get structured summary for medical professional"""
    try:
        summary = agent.get_summary()
        return SummaryResponse(
            patient_data=summary["patient_data"],
            conversation_complete=summary["completion_percentage"] > 50,
            recommendation=summary["recommendation"],
            clinical_summary=summary.get("clinical_summary"),
            completeness=summary.get("completeness", {})
        )
    except Exception as e:
        logger.error(f"Error in summary endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_conversation(
    agent: HealthcareIntakeAgent = Depends(get_agent)
):
    """Reset the conversation"""
    try:
        agent.reset_conversation()
        return {"status": "success", "message": "Conversation reset successfully"}
    except Exception as e:
        logger.error(f"Error in reset endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status(
    agent: HealthcareIntakeAgent = Depends(get_agent)
):
    """Get agent status and statistics"""
    try:
        return {
            "status": "active",
            "model": agent.model_name,
            "conversation_turns": len(agent.conversation_history) // 2,
            "data_collected": {
                "symptoms": len(agent.patient_data.symptoms),
                "conditions": len(agent.patient_data.preexisting_conditions),
                "allergies": len(agent.patient_data.allergies),
                "medications": len(agent.patient_data.medications)
            }
        }
    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))