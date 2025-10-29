from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from simple_rag import SimpleRAG
import os

app = FastAPI(title="PDF RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag = SimpleRAG()
rag.load_pdfs()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    status: str

@app.get("/")
def root():
    return {"message": "PDF RAG API is running"}

@app.get("/status")
def status():
    pdf_count = len([f for f in os.listdir("pdfs") if f.endswith('.pdf')]) if os.path.exists("pdfs") else 0
    chunk_count = len(rag.documents)
    return {
        "pdf_files": pdf_count,
        "text_chunks": chunk_count,
        "ready": chunk_count > 0
    }

@app.post("/query", response_model=QueryResponse)
def query_pdf(request: QueryRequest):
    try:
        answer = rag.query(request.question)
        return QueryResponse(answer=answer, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)