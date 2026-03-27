import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the healthcare intake agent"""
    
    # Groq Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")
    
    # Available Groq Models
    GROQ_MODELS = {
        "mixtral": "mixtral-8x7b-32768",
        "llama2": "llama2-70b-4096",
        "gemma": "gemma-7b-it"
    }
    
    # Vector DB Configuration
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
    CHROMA_COLLECTION_NAME = "medical_guidelines"
    
    # Model Parameters
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Safety Settings
    SAFETY_GUARDRAILS_ENABLED = True
    MAX_CONVERSATION_TURNS = 20
    
    # Medical Guidelines Paths
    MEDICAL_GUIDELINES_PATH = "./data/medical_guidelines"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required. Get it from https://console.groq.com")
        return True