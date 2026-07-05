# AI Backend Platform
### Self-Hosted RAG & Multi-Model AI Service

A self-hosted AI backend platform built with FastAPI, Ollama, and ChromaDB that combines secure multi-user chat with Retrieval-Augmented Generation (RAG).

- JWT-secured multi-user chat
- Automatic model routing
- Streaming responses
- Persistent conversation history
- Context-window management through conversation summarization
- Dynamic model discovery
- Rate limiting and operational metrics

Rather than acting as a thin wrapper around a language model, the platform manages authentication, conversation persistence, document ingestion, semantic retrieval, prompt construction, and AI orchestration entirely on the backend. 

## Project Goals

This project was built to demonstrate backend engineering skills beyond simple CRUD APIs. The focus areas include:

- Authentication and authorization
- Service-oriented architecture
- AI model integration
- Context management
- API design
- Performance monitoring
- Production-minded error handling

The goal was to create a platform that resembles a real AI service rather than a simple chatbot wrapper.

## Key Capabilities

- Secure multi-user AI chat
- Retrieval-Augmented Generation (RAG)
- Local LLM inference with Ollama
- Semantic document search
- PDF knowledge base ingestion
- Multi-model orchestration

## Design Philosophy

- Local-first AI platform
- Self-hosted models
- Modular service architecture
- Separation of concerns
- Production-inspired backend design

## Features

### AI Chat

- JWT-secured multi-user authentication
- Persistent conversation history
- Streaming responses
- Automatic conversation summarization
- Automatic model routing
- Manual model selection

### Document Processing

- PDF upload
- Plain text upload
- Automatic text cleaning
- Configurable chunk generation
- Chunk overlap

### RAG

- Local embeddings with nomic-embed-text
- ChromaDB vector storage
- Permission-aware semantic retrieval
- Public/private document visibility
- Automatic prompt context construction

### Platform

- Rate limiting
- Operational metrics
- Health monitoring
- Dynamic model discovery

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- Pydantic

### AI & Retrieval
- Ollama
- ChromaDB
- nomic-embed-text
- HTTPX

### Logging
- Loguru 

### Document Processing
- PyPDF

### Security
- JWT (python-jose)
- pwdlib

### Infrastructure
- SlowAPI
- SQLite

## Project Structure

```
app/
├── api/             # API endpoints
├── core/            # Configuration, security, rate limiting
├── integrations/    # Ollama and ChromaDB clients
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response models
├── services/        # Business logic (chat, routing, documents, RAG)
└── main.py          # FastAPI application
```


## Prerequisites

- Python 3.11+
- A working Ollama installation and running server
- A local database (the project currently defaults to SQLite via DATABASE_URL)

## Environment Variables

Create an environment file in the app directory named .env and set values such as:

```env
SECRET_KEY=replace-with-a-secure-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./ai_platform.db
OLLAMA_URL=http://localhost:11434/api/chat
BASE_OLLAMA_URL=http://localhost:11434
DEFAULT_MODEL=qwen:latest
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_URL = "http://localhost:11434/api/embeddings"
CHROMA_PATH = "./chroma_db"
CHROMA_COLLECTION = name-of-database

```

## Installation

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

From the app directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Main Endpoints
```text 
Authentication

- POST     /auth/register
- POST     /auth/login
- GET      /me

Chat

- POST     /chat
- POST     /chat/stream
- GET      /chat/history/{chat_id}
- PATCH    /chat/{chat_id}/title
- GET      /chat/list
- DELETE   /chat/{chat_id}

Models and Routing

- GET /models
- PATCH    /model/update/routing_mode
- PATCH    /model/update/model

Monitoring

- GET      /health
- GET      /stats

Documents

- POST     /documents/upload
- GET      /documents/list
- GET      /documents/{doc_id}
- DELETE   /documents/{doc_id}
- PATCH    /document/visibility
```

## Architecture

```text
                    Document Upload
                           │
                           ▼
                  PDF / TXT Extraction
                           │
                           ▼
                    Text Cleaning
                           │
                           ▼
                  Chunk Generation
                           │
                           ▼
                 Ollama Embeddings
                           │
                           ▼
                     ChromaDB

────────────────────────────────────────────

User Prompt
      │
      ▼
Authentication
      │
      ▼
Generate Query Embedding
      │
      ▼
Semantic Search
      │
      ▼
Retrieve Context
      │
      ▼
Build Prompt
      │
      ▼
Conversation History
      │
      ▼
System Prompt
      │
      ▼
Payload Builder
      │
      ▼
    Ollama
      │
      ▼
Persist Response
```

## Technical Highlights

### Automatic Model Routing

New conversations are automatically routed to the most appropriate local model based on the user's request. Model selection is persisted and periodically re-evaluated during conversation summarization to reduce routing overhead.

### Context Window Management

Long conversations are automatically summarized after a configurable number of messages.
The generated summary is stored with the chat and injected into future requests, allowing the platform to retain conversational context while reducing prompt size and inference cost.

### Multi-User Security

All chat operations enforce user ownership validation, preventing unauthorized access, modification, or deletion of another user's conversations.

### Streaming Responses

Supports token streaming from Ollama for improved user responsiveness while persisting the complete assistant response to the database for future retrieval and context management.

### Retrieval-Augmented Generation

Uploaded documents are parsed, cleaned, chunked, embedded with Ollama's nomic-embed-text model, and stored in ChromaDB. User prompts are embedded at query time and matched against permission-filtered document vectors before being injected into the LLM prompt.

### Operational Metrics

Tracks:
- Total users
- Total chats
- Total messages
- Most used model
- Model usage distribution
- Average response times
- Per-model latency metrics
- Documents
- Embedded documents
- Chunks
- Stored vectors
- Synchronization status

## Current Status

Version 2.0

The platform now supports authenticated multi-user chat, Retrieval-Augmented Generation (RAG), semantic document search, and local LLM orchestration using Ollama and ChromaDB.

## Future Improvements (V3)

- Repository ingestion
- Code-aware chunking
- Hybrid search
- Workspace support
- Redis caching
- Docker deployment