import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os
import pickle
import logging

logger = logging.getLogger(__name__)

class FAISSVectorDB:
    """FAISS-based vector database - lightweight and no migration issues"""
    
    def __init__(self, persist_dir: str, collection_name: str = "medical_guidelines"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.index_path = os.path.join(persist_dir, f"{collection_name}.faiss")
        self.metadata_path = os.path.join(persist_dir, f"{collection_name}_metadata.pkl")
        
        # Ensure persist directory exists
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize embedding model
        logger.info("Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index
        self.index = None
        self.documents = []
        self.metadatas = []
        
        # Load existing index if available
        self._load_index()
        
        logger.info(f"FAISS vector DB initialized with collection: {collection_name}")
    
    def _load_index(self):
        """Load existing FAISS index if available"""
        try:
            import faiss
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadatas = data['metadatas']
                logger.info(f"Loaded existing index with {len(self.documents)} documents")
            else:
                self._create_new_index()
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        try:
            import faiss
            # Use L2 distance index
            dimension = 384  # all-MiniLM-L6-v2 embedding dimension
            self.index = faiss.IndexFlatL2(dimension)
            logger.info("Created new FAISS index")
        except ImportError:
            logger.error("FAISS not installed. Run: pip install faiss-cpu")
            raise
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Add documents to vector database"""
        try:
            import faiss
            
            if metadatas is None:
                metadatas = [{"source": f"doc_{i}"} for i in range(len(documents))]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} documents...")
            embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Store documents and metadata
            self.documents.extend(documents)
            self.metadatas.extend(metadatas)
            
            # Save index and metadata
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadatas': self.metadatas
                }, f)
            
            logger.info(f"Added {len(documents)} documents to collection")
            return [f"doc_{i}" for i in range(len(documents))]
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 3) -> List[str]:
        """Search for similar documents"""
        try:
            import faiss
            
            if self.index is None or self.index.ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search
            distances, indices = self.index.search(query_embedding.astype('float32'), min(k, self.index.ntotal))
            
            # Return documents
            results = []
            for idx in indices[0]:
                if idx >= 0 and idx < len(self.documents):
                    results.append(self.documents[idx])
            
            return results
            
        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            "collection_name": self.collection_name,
            "document_count": len(self.documents),
            "persist_dir": self.persist_dir
        }
    
    def delete_collection(self):
        """Delete the collection"""
        try:
            import faiss
            self.index = None
            self.documents = []
            self.metadatas = []
            
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            self._create_new_index()
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")