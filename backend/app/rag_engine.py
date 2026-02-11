import os
import re
from typing import List, Dict
import PyPDF2
import docx
from sentence_transformers import SentenceTransformer
import numpy as np

class RAGEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize RAG Engine with embedding model"""
        self.embedding_model = SentenceTransformer(model_name)
        self.chunk_size = 500
        self.chunk_overlap = 50
        
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from different file formats"""
        text = ""
        
        if file_type == "pdf":
            text = self._extract_from_pdf(file_path)
        elif file_type == "txt":
            text = self._extract_from_txt(file_path)
        elif file_type == "docx":
            text = self._extract_from_docx(file_path)
        elif file_type == "md":
            text = self._extract_from_txt(file_path)  # Markdown as text
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return text
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return text
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT/MD file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading text file: {e}")
            return ""
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ""
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) == 0:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                chunk = text[start:end]
                last_period = max(
                    chunk.rfind('. '),
                    chunk.rfind('! '),
                    chunk.rfind('? ')
                )
                
                if last_period > self.chunk_size * 0.5:
                    end = start + last_period + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts"""
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings
    
    def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generate response using retrieved context"""
        # Combine context
        context = "\n\n".join([
            f"[Source: {chunk['metadata']['document_name']}]\n{chunk['text']}"
            for chunk in context_chunks
        ])
        
        # Simple template-based response (replace with LLM call in production)
        response = self._template_response(query, context)
        
        return response
    
    def _template_response(self, query: str, context: str) -> str:
        """Generate a template-based response"""
        # This is a simple template. In production, use an LLM API
        response = f"Based on the provided documents:\n\n"
        
        if context:
            # Extract key information
            sentences = context.split('\n')
            relevant_sentences = [s for s in sentences if s.strip() and len(s) > 20][:3]
            
            response += "\n".join(relevant_sentences[:3])
            response += f"\n\nThis information is relevant to your query: '{query}'"
        else:
            response += "I couldn't find relevant information in the documents to answer your query."
        
        return response
    
    def calculate_similarity(self, query_embedding: np.ndarray, chunk_embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and chunks"""
        # Normalize vectors
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        chunks_norm = chunk_embeddings / np.linalg.norm(chunk_embeddings, axis=1, keepdims=True)
        
        # Calculate cosine similarity
        similarities = np.dot(chunks_norm, query_norm)
        
        return similarities
