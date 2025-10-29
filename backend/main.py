from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from simple_rag import SimpleRAG
import os
import secrets
import json
from datetime import datetime

app = FastAPI(title="MCR Multi RAG API", description="Multi-Course Retrieval Augmented Generation for CV, Multimedia, Haptics, Ethics & More")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:6006"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG instance - loads once and stays in memory
rag_instance = None

def get_rag():
    global rag_instance
    if rag_instance is None:
        print("Initializing RAG system...")
        rag_instance = SimpleRAG()
        count = rag_instance.load_pdfs(force_reload=False)
        print(f"✅ RAG system ready with {count} chunks")
    return rag_instance

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    status: str

class ApiKeyResponse(BaseModel):
    api_key: str
    created_at: str
    status: str

# Initialize RAG lazily instead of on startup
# This prevents blocking the server start

@app.get("/")
def root():
    return {"message": "MCR Multi RAG API is running - Multi-Course Knowledge Assistant"}

@app.get("/status")
def status():
    rag = get_rag()
    pdf_folder = os.path.join(os.path.dirname(__file__), "pdfs")
    pdf_count = len([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]) if os.path.exists(pdf_folder) else 0
    
    # Count API keys
    api_keys_count = 0
    if os.path.exists("api_keys.json"):
        with open("api_keys.json", 'r') as f:
            keys = json.load(f)
            api_keys_count = len([k for k in keys if k.get('active', True)])
    
    return {
        "pdf_files": pdf_count,
        "text_chunks": len(rag.documents),
        "ready": len(rag.documents) > 0,
        "api_keys_created": api_keys_count
    }

@app.post("/query", response_model=QueryResponse)
def query_pdf(request: QueryRequest):
    try:
        rag = get_rag()
        answer = rag.query(request.question)
        return QueryResponse(answer=answer, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-pdfs")
def process_pdfs():
    try:
        print("🔄 Manual PDF processing requested...")
        global rag_instance
        rag_instance = SimpleRAG()
        count = rag_instance.load_pdfs(force_reload=True)
        print(f"✅ Processed {count} text chunks from PDFs")
        return {"status": "success", "chunks_processed": count, "message": f"Successfully processed {count} text chunks from PDFs"}
    except Exception as e:
        print(f"❌ Error processing PDFs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-api-key", response_model=ApiKeyResponse)
def create_api_key():
    try:
        print("Creating API key...")
        # Generate a secure API key
        api_key = f"mcr_{secrets.token_urlsafe(32)}"
        created_at = datetime.now().isoformat()
        print(f"Generated key: {api_key[:20]}...")
        
        # Save to file (in production, use a proper database)
        api_keys_file = "api_keys.json"
        if os.path.exists(api_keys_file):
            with open(api_keys_file, 'r') as f:
                keys = json.load(f)
        else:
            keys = []
        
        keys.append({
            "api_key": api_key,
            "created_at": created_at,
            "active": True
        })
        
        
        with open(api_keys_file, 'w') as f:
            json.dump(keys, f, indent=2)
        
        print(f"✅ API key created successfully")
        return ApiKeyResponse(
            api_key=api_key,
            created_at=created_at,
            status="success"
        )
    except Exception as e:
        print(f"❌ Error creating API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7007)