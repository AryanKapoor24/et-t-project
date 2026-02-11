import numpy as np
import faiss
from typing import List, Dict, Optional
import pickle
import os

class VectorStore:
    def __init__(self, dimension: int = 384, index_path: str = "vector_index"):
        """Initialize vector store with FAISS"""
        self.dimension = dimension
        self.index_path = index_path
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(dimension)
        
        # Metadata storage
        self.chunks_metadata = []
        self.chunk_texts = []
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing index from disk"""
        if os.path.exists(f"{self.index_path}.faiss"):
            try:
                self.index = faiss.read_index(f"{self.index_path}.faiss")
                with open(f"{self.index_path}.pkl", 'rb') as f:
                    data = pickle.load(f)
                    self.chunks_metadata = data['metadata']
                    self.chunk_texts = data['texts']
                print(f"Loaded index with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"Error loading index: {e}")
    
    def _save_index(self):
        """Save index to disk"""
        try:
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            with open(f"{self.index_path}.pkl", 'wb') as f:
                pickle.dump({
                    'metadata': self.chunks_metadata,
                    'texts': self.chunk_texts
                }, f)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def add_chunks(self, chunks: List[str], metadata: List[Dict], embeddings: Optional[np.ndarray] = None) -> List[int]:
        """Add chunks to vector store"""
        from app.rag_engine import RAGEngine
        
        if embeddings is None:
            # Generate embeddings
            rag = RAGEngine()
            embeddings = rag.generate_embeddings(chunks)
        
        # Convert to float32 for FAISS
        embeddings = embeddings.astype('float32')
        
        # Add to index
        start_id = len(self.chunk_texts)
        self.index.add(embeddings)
        
        # Store metadata and texts
        self.chunk_texts.extend(chunks)
        self.chunks_metadata.extend(metadata)
        
        # Save index
        self._save_index()
        
        return list(range(start_id, start_id + len(chunks)))
    
    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar chunks"""
        from app.rag_engine import RAGEngine
        
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        rag = RAGEngine()
        query_embedding = rag.generate_embeddings([query])[0].astype('float32')
        
        # Search
        query_embedding = np.expand_dims(query_embedding, axis=0)
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunk_texts):
                # Convert L2 distance to similarity score (0-1)
                score = 1 / (1 + distance)
                
                results.append({
                    'text': self.chunk_texts[idx],
                    'metadata': self.chunks_metadata[idx],
                    'score': float(score),
                    'rank': i + 1
                })
        
        return results
    
    def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        # Find indices to keep
        indices_to_keep = [
            i for i, meta in enumerate(self.chunks_metadata)
            if meta.get('document_id') != document_id
        ]
        
        if len(indices_to_keep) == len(self.chunks_metadata):
            return  # Document not found
        
        # Rebuild index with remaining chunks
        from app.rag_engine import RAGEngine
        
        remaining_texts = [self.chunk_texts[i] for i in indices_to_keep]
        remaining_metadata = [self.chunks_metadata[i] for i in indices_to_keep]
        
        # Generate embeddings for remaining chunks
        if remaining_texts:
            rag = RAGEngine()
            embeddings = rag.generate_embeddings(remaining_texts).astype('float32')
            
            # Reset index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings)
        else:
            # Empty index
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.chunk_texts = remaining_texts
        self.chunks_metadata = remaining_metadata
        
        # Save updated index
        self._save_index()
    
    def get_size(self) -> int:
        """Get number of vectors in index"""
        return self.index.ntotal
    
    def clear(self):
        """Clear all data"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks_metadata = []
        self.chunk_texts = []
        self._save_index()
