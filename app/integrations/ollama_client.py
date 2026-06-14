import httpx
from app.core.config import BASE_OLLAMA_URL, OLLAMA_URL, DEFAULT_MODEL
import json
import app.services as services
from fastapi import HTTPException


async def chat(messages: list, model: str = DEFAULT_MODEL):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OLLAMA_URL, 
                                        json={"model": model,
                                            "messages": messages,
                                            "stream": False})
            response.raise_for_status()
            response_data = response.json()
            print(response_data)
            return  response_data["message"]["content"]
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="Model response timed out.")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama unavailable")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Model not found.")
        raise HTTPException(status_code=500, detail="Ollama request failed.")
        
        
async def stream_chat(messages: list, model: str = DEFAULT_MODEL):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", OLLAMA_URL, json={"model": model, "messages": messages, "stream": True}) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data["message"]["content"]
                        yield chunk
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="Model response timed out.")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama unavailable")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Model not found.")
        raise HTTPException(status_code=500, detail="Ollama request failed.")



async def generate_chat_summary(chat_id, user_id, db):
    history = services.chat_service.get_chat_history_return_conversation(chat_id, user_id, db)
    system_prompt ="""
                   You are a summarization assistant.
                    Generate a concise summary of the conversation between a user and an AI assistant.
                    Include:
                    - Important topics discussed
                    - Decisions made
                    - Relevant preferences or goals
                    - Action items
                    Limit the summary to 3 sentences maximum.
                    """
    conversation_text = "\n".join(f"{msg['role']}: {msg['content']}" for msg in history)
    payload={
        "model": "gemma4:e4b",
        "messages": [
            {"role": "system",
             "content": system_prompt},
            {"role": "user",
             "content": conversation_text}
                    ],
            "stream": False
                }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            return response_data["message"]["content"]
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="Model response timed out.")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama unavailable")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail="Ollama request failed.")

    


def get_installed_models():
    try:
        response = httpx.get(f"{BASE_OLLAMA_URL}/api/tags")
        response.raise_for_status()
        models = response.json()
        return models.get("models", [])
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama unavailable")