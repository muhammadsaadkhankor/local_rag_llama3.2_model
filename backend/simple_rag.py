import os
import requests
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import pickle

class SimpleRAG:
    def __init__(self):
        self.embeddings_model = None
        self.documents = []
        self.embeddings = []
        self.cache_file = "embeddings_cache.pkl"
        
    def _load_model(self):
        if self.embeddings_model is None:
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def load_pdfs(self, pdf_folder="pdfs", force_reload=False):
        # Make pdf_folder absolute if it's relative
        if not os.path.isabs(pdf_folder):
            pdf_folder = os.path.join(os.path.dirname(__file__), pdf_folder)
        
        print(f"Looking for PDFs in: {pdf_folder}")
        print(f"Directory exists: {os.path.exists(pdf_folder)}")
        
        # Check if cache exists
        cache_path = os.path.join(os.path.dirname(__file__), self.cache_file)
        if os.path.exists(cache_path) and not force_reload:
            print("Loading from cache...")
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
                self.documents = cached_data['documents']
                self.embeddings = cached_data['embeddings']
                return len(self.documents)
        
        # Process PDFs if no cache
        self._load_model()
        texts = []
        if not os.path.exists(pdf_folder):
            print(f"PDF folder does not exist: {pdf_folder}")
            return 0
        
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        print(f"Found {len(pdf_files)} PDF files")
            
        for filename in os.listdir(pdf_folder):
            if filename.endswith('.pdf'):
                print(f"Processing: {filename}")
                try:
                    with open(os.path.join(pdf_folder, filename), 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                        
                        # Split into chunks
                        chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
                        texts.extend(chunks)
                        print(f"Added {len(chunks)} chunks from {filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        self.documents = texts
        if texts:
            self.embeddings = self.embeddings_model.encode(texts)
            # Cache the results
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'embeddings': self.embeddings
                }, f)
        
        return len(texts)
    
    def query_ollama(self, prompt):
        try:
            # Use environment variable for Ollama URL (Docker compatibility)
            ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            response = requests.post(f'{ollama_url}/api/generate',
                json={
                    'model': 'llama3.2:3b',
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'top_k': 40
                    }
                })
            return response.json()['response']
        except Exception as e:
            return f"Error: Could not connect to Ollama at {ollama_url}. {str(e)}"
    
    def query(self, question):
        if not self.documents:
            return "No PDFs loaded. Add PDFs to the 'pdfs' folder."
        
        self._load_model()
        # Find relevant documents
        question_embedding = self.embeddings_model.encode([question])
        similarities = cosine_similarity(question_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-3:][::-1]
        
        context = "\n\n".join([self.documents[i] for i in top_indices])
        
        prompt = f"""You are a helpful AI assistant. Answer the question based on the provided context. Give a clear, direct answer without mentioning the context or saying "based on the context".

Context: {context}

Question: {question}

Answer the question naturally and comprehensively:"""
        
        return self.query_ollama(prompt)

if __name__ == "__main__":
    rag = SimpleRAG()
    
    os.makedirs("pdfs", exist_ok=True)
    print("Loading PDFs...")
    count = rag.load_pdfs()
    print(f"Loaded {count} text chunks from PDFs")
    
    while True:
        question = input("\nAsk a question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        
        answer = rag.query(question)
        print(f"\nAnswer: {answer}")