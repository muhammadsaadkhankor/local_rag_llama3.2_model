# PDF RAG Chat Application

A modern React + FastAPI application for chatting with your PDFs using Llama 3.2.

## 🏗️ Project Structure

```
custom_model/
├── backend/           # FastAPI server
│   ├── main.py       # API endpoints
│   ├── simple_rag.py # RAG logic
│   └── pdfs/         # Your PDF files
├── frontend/         # React TypeScript app
│   └── src/
│       ├── App.tsx   # Main chat component
│       └── App.css   # Styles
└── start.sh          # Start both servers
```

## 🚀 Quick Start

1. **Install backend dependencies:**
```bash
cd backend
pip install -r api_requirements.txt
```

2. **Install frontend dependencies:**
```bash
cd frontend
npm install
```

3. **Add your PDFs:**
```bash
# Copy your PDF files to backend/pdfs/
cp /path/to/your/file.pdf backend/pdfs/
```

4. **Start the application:**
```bash
./start.sh
```

5. **Open your browser:**
   - Frontend: http://localhost:3000
   - API docs: http://localhost:8000/docs

## ✨ Features

- 🎨 **Modern React UI** - Clean, responsive chat interface
- ⚡ **Fast API** - Cached embeddings, no PDF reloading
- 🧠 **Smart RAG** - Uses Llama 3.2 with context retrieval
- 📱 **Mobile Friendly** - Works on all devices
- 🔄 **Real-time Status** - Shows PDF count and readiness

## 🛠️ Manual Start

**Backend only:**
```bash
cd backend
python main.py
```

**Frontend only:**
```bash
cd frontend
npm start
```

## 📝 API Endpoints

- `GET /status` - Check system status
- `POST /query` - Send questions to RAG system

The backend loads PDFs once and keeps them in memory for fast responses!# local_llama_rag_model
# local_rag_llama3.2_model
