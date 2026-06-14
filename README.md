# AI Backend Platform

A self-hosted AI platform built with FastAPI and Ollama that provides:

- JWT-secured multi-user chat
- Automatic model routing
- Streaming responses
- Persistent conversation history
- Context-window management through conversation summarization
- Dynamic model discovery
- Rate limiting and operational metrics

The project focuses on backend architecture, AI integrations, security, and system design rather than simply forwarding prompts to an LLM.

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

## Features

- JWT-secured multi-user authentication
- Persistent chat history stored in SQLAlchemy
- Automatic model routing for new conversations
- Manual model selection and routing controls
- Streaming responses from Ollama
- Conversation summarization for context-window management
- Dynamic model discovery from Ollama
- User ownership validation on all chat operations
- Rate limiting with SlowAPI
- Health checks and operational metrics

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- Pydantic

### AI Integration
- Ollama
- HTTPX

### Security
- JWT (python-jose)
- pwdlib

### Infrastructure
- SlowAPI
- SQLite


## Project Structure

- app/main.py - FastAPI application and route definitions
- app/core/ - configuration, security, rate limiting
- app/services/ - chat and routing logic
- app/integrations/ - Ollama client integration
- app/models/ - SQLAlchemy models
- app/schemas/ - request/response models
- app/api/ - metrics and health helpers


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

### Authentication
- POST /auth/register
- POST /auth/login
- GET /me

### Chat
- POST /chat
- POST /chat/stream
- GET /chat/history/{chat_id}
- PATCH /chat/{chat_id}/title
- GET /chat/list
- DELETE /chat/{chat_id}

### Models and Routing
- GET /models
- PATCH /model/update/routing_mode
- PATCH /model/update/model

### Monitoring
- GET /health
- GET /stats

## Architecture

```text
User Prompt
      │
      ▼
Authentication
      │
      ▼
Chat Service
      │
      ├── Context Management
      ├── Chat Persistence
      ├── Model Selection
      └── Streaming Support
      │
      ▼
    Ollama
      │
      ▼
Response Stored in Database
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

### Operational Metrics

Tracks:
- Total users
- Total chats
- Total messages
- Most used model
- Model usage distribution
- Average response times
- Per-model latency metrics

## Current Status

V1.1 Feature Complete

Implemented:
- Authentication and authorization
- Multi-user chat persistence
- Model routing
- Streaming responses
- Conversation summarization
- Dynamic model discovery
- Rate limiting
- Health monitoring
- Operational metrics

## Roadmap (V2)

- PDF and document upload
- Document parsing pipeline
- Embeddings generation
- Vector database integration
- Retrieval Augmented Generation (RAG)
- Knowledge-base search
- Multi-document analysis