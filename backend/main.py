from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime
import json

from app.rag_engine import RAGEngine
from app.vector_store import VectorStore
from app.knowledge_graph import KnowledgeGraphBuilder

app = FastAPI(title="NeuralRAG API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rag_engine = RAGEngine()
vector_store = VectorStore()
kg_builder = KnowledgeGraphBuilder()

# Data models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    response: str
    sources: List[dict]
    confidence: float

class Document(BaseModel):
    id: str
    name: str
    type: str
    size: int
    chunks: int
    uploaded_at: str

# In-memory storage (replace with database in production)
documents_db = []
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "NeuralRAG API",
        "version": "1.0.0",
        "status": "active"
    }

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    uploaded_docs = []
    
    for file in files:
        try:
            # Save file
            file_id = str(uuid.uuid4())
            file_extension = file.filename.split('.')[-1].lower()
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_extension}")
            
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Process document
            text = rag_engine.extract_text(file_path, file_extension)
            chunks = rag_engine.chunk_text(text)
            
            # Store in vector database
            chunk_ids = vector_store.add_chunks(
                chunks=chunks,
                metadata=[{
                    "document_id": file_id,
                    "document_name": file.filename,
                    "chunk_index": i
                } for i in range(len(chunks))]
            )
            
            # Create document record
            doc_record = {
                "id": file_id,
                "name": file.filename,
                "type": file_extension,
                "size": len(content),
                "chunks": len(chunks),
                "uploaded_at": datetime.now().isoformat()
            }
            
            documents_db.append(doc_record)
            uploaded_docs.append(doc_record)
            
            # Update knowledge graph
            kg_builder.add_document(file_id, text, chunks)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {str(e)}")
    
    return {
        "success": True,
        "documents": uploaded_docs,
        "message": f"Successfully uploaded {len(uploaded_docs)} document(s)"
    }

@app.get("/documents")
async def get_documents():
    """Get all uploaded documents"""
    return {
        "documents": documents_db,
        "total": len(documents_db)
    }

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    global documents_db
    
    # Find and remove document
    doc = next((d for d in documents_db if d["id"] == document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    documents_db = [d for d in documents_db if d["id"] != document_id]
    
    # Remove from vector store
    vector_store.delete_document(document_id)
    
    # Remove file
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}.{doc['type']}")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return {"success": True, "message": "Document deleted"}

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system"""
    try:
        if not documents_db:
            raise HTTPException(status_code=400, detail="No documents uploaded yet")
        
        # Retrieve relevant chunks
        results = vector_store.similarity_search(
            query=request.query,
            top_k=request.top_k
        )
        
        # Generate response using RAG
        response = rag_engine.generate_response(
            query=request.query,
            context_chunks=results
        )
        
        # Format sources
        sources = [
            {
                "document": r["metadata"]["document_name"],
                "score": r["score"],
                "chunk_index": r["metadata"]["chunk_index"]
            }
            for r in results
        ]
        
        return QueryResponse(
            response=response,
            sources=sources,
            confidence=sum(r["score"] for r in results) / len(results) if results else 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge-graph")
async def get_knowledge_graph():
    """Get the knowledge graph visualization data"""
    try:
        graph_data = kg_builder.build_graph()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    total_chunks = sum(doc["chunks"] for doc in documents_db)
    total_size = sum(doc["size"] for doc in documents_db)
    
    return {
        "total_documents": len(documents_db),
        "total_chunks": total_chunks,
        "total_size": total_size,
        "vector_store_size": vector_store.get_size(),
        "knowledge_graph_nodes": kg_builder.get_node_count()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
