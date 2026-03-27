#!/usr/bin/env python
"""
Initialize vector database with medical guidelines
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.vector_db.chroma_client import ChromaVectorDB
from app.vector_db.document_processor import DocumentProcessor
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_vector_db():
    """Initialize and populate vector database"""
    
    try:
        # Create medical guidelines directory if needed
        os.makedirs(Config.MEDICAL_GUIDELINES_PATH, exist_ok=True)
        
        # Initialize document processor
        processor = DocumentProcessor(Config.MEDICAL_GUIDELINES_PATH)
        
        # Create medical dataset
        logger.info("Creating medical guidelines dataset...")
        guidelines = processor.create_medical_dataset()
        
        # Initialize ChromaDB
        logger.info("Initializing ChromaDB...")
        chroma_db = ChromaVectorDB(
            persist_dir=Config.CHROMA_PERSIST_DIR,
            collection_name=Config.CHROMA_COLLECTION_NAME
        )
        
        # Process documents
        logger.info("Processing documents...")
        documents = processor.process_medical_guidelines()
        
        if documents:
            # Add to vector DB
            logger.info(f"Adding {len(documents)} documents to vector database...")
            chroma_db.add_documents(documents)
            
            logger.info("Vector database initialization complete!")
            stats = chroma_db.get_collection_stats()
            logger.info(f"Collection stats: {stats}")
        else:
            logger.warning("No documents found to add to vector database")
        
        # Test search
        test_query = "chest pain and difficulty breathing"
        results = chroma_db.similarity_search(test_query, k=2)
        logger.info(f"\nTest search for '{test_query}':")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: {result[:150]}...")
            
    except Exception as e:
        logger.error(f"Error initializing vector DB: {e}")
        raise

if __name__ == "__main__":
    init_vector_db()