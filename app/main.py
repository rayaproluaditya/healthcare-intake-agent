from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.config import Config
from app.vector_db.faiss_client import FAISSVectorDB
from app.vector_db.document_processor import DocumentProcessor
from app.agents.intake_agent import HealthcareIntakeAgent
import logging
import os

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Intake Agent",
    description="AI-powered healthcare intake system using Groq",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    try:
        # Validate config
        Config.validate()
        logger.info("Configuration validated")
        
        # Initialize vector database
        vector_db = FAISSVectorDB(
            persist_dir=Config.CHROMA_PERSIST_DIR,
            collection_name=Config.CHROMA_COLLECTION_NAME
        )
        
        # Check if vector DB is empty and populate if needed
        if vector_db.get_collection_stats()["document_count"] == 0:
            logger.info("Populating vector database with medical guidelines...")
            doc_processor = DocumentProcessor(Config.MEDICAL_GUIDELINES_PATH)
            
            # Create synthetic guidelines if files don't exist
            if not os.path.exists(Config.MEDICAL_GUIDELINES_PATH):
                os.makedirs(Config.MEDICAL_GUIDELINES_PATH, exist_ok=True)
                doc_processor.create_medical_dataset()
            
            # Process and add documents
            documents = doc_processor.process_medical_guidelines()
            if documents:
                vector_db.add_documents(documents)
                logger.info(f"Added {len(documents)} documents to vector DB")
        
        # Initialize healthcare agent
        routes.agent = HealthcareIntakeAgent(
            vector_db=vector_db,
            model_name=Config.GROQ_MODEL_NAME
        )
        logger.info("Healthcare intake agent initialized")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Healthcare Intake Agent",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "POST /api/v1/message": "Process patient message",
            "GET /api/v1/summary": "Get patient summary",
            "POST /api/v1/reset": "Reset conversation",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "healthcare-intake-agent",
        "groq_ready": routes.agent is not None
    }

# Include routers
app.include_router(routes.router, prefix="/api/v1", tags=["intake"])