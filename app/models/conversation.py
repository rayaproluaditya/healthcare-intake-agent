from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum
import uuid

class MessageRole(str, Enum):
    PATIENT = "patient"
    AGENT = "agent"
    SYSTEM = "system"

class Message(BaseModel):
    """Individual message in conversation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = Field(default_factory=dict)
    
class Conversation(BaseModel):
    """Full conversation history"""
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    metadata: dict = Field(default_factory=dict)
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[dict] = None):
        """Add message to conversation"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.last_updated = datetime.now()
    
    def get_last_message(self) -> Optional[Message]:
        """Get the last message in conversation"""
        return self.messages[-1] if self.messages else None
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)
    
    def get_patient_messages(self) -> List[Message]:
        """Get all patient messages"""
        return [msg for msg in self.messages if msg.role == MessageRole.PATIENT]
    
    def get_agent_messages(self) -> List[Message]:
        """Get all agent messages"""
        return [msg for msg in self.messages if msg.role == MessageRole.AGENT]