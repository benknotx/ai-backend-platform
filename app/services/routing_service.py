import httpx
from app.core.config import OLLAMA_URL
from pydantic import BaseModel
from typing import Literal
from fastapi import HTTPException
import app.models as DBmodels
import app.services as helper
from app.core.config import MODEL_MAP
from app.integrations.ollama_client import get_installed_models

class ClassificationOptions(BaseModel): 
    category: Literal["CODER","GENERAL" ,"CHAT","SUMMARY"] 



async def classify_prompt(prompt:str):
    system_prompt="""
        You are a routing classifier.

        Classify the user request into exactly one category.
          The categories are:

        CODER
        - Write a Python function
        - Create a FastAPI endpoint
        - Implement a linked list
        - Optimize this SQL query
        - Write a SQL join
        - Fixing errors
        - Analyzing stack traces
        - Reviewing code
        - Finding bugs
        - Fix this SQL error
        - Why is this query failing
        - anything related to code

        CHAT
        - Casual conversation
        - Advice
        - Brainstorming
        - General discussion
        - Personal questions
        - Entertainment
        - Hobbies

        GENERAL
        - Explanations
        - Teaching concepts
        - Research questions
        - Technical knowledge
        - Science questions
        - History questions
        - Math problems

        SUMMARY
        - Summarizing text
        - Condensing information
        - Extracting key points
        - breif explanations of complex topics


        Return valid JSON only:
        {
        "category": "...",
        }        
        """
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload ={
            "model": "smollm2:1.7b",
            "messages": [
                {"role": "system",
                  "content": system_prompt},
                {"role":"user",
                 "content": prompt}
                ],
                 "format": ClassificationOptions.model_json_schema(),
                 "options": {"temperature": 0.0},
                 "stream": False
                }
        response = await client.post(OLLAMA_URL, json=payload)
        response_data = response.json()
        content_string = response_data["message"]["content"]
        validated_data = ClassificationOptions.model_validate_json(content_string)
        return validated_data


def set_mode(chat_id, mode, user_id, db):
    helper.get_user_chat_or_404(chat_id, user_id, db)
    mode=mode.upper()
    if mode not in ["AUTO", "MANUAL"]:
        raise HTTPException(status_code=422, detail= "Enrty must be AUTO or MANUAL")
    chat = db.query(DBmodels.Chat).filter(DBmodels.Chat.id==chat_id, DBmodels.Chat.user_id==user_id).first()
    chat.routing_mode = mode
    db.commit()
    db.refresh(chat)
    return {"chat_id": chat_id, "mode": mode}

def set_model(chat_id, model, user_id, db):
    chat = helper.get_user_chat_or_404(chat_id, user_id, db)
    installed_models = get_installed_models()
    installed_models = [m["name"] for m in installed_models]
    if model not in installed_models:
        raise HTTPException(status_code=422, detail= "Entry must be Valid Model")
    chat.routing_mode= "MANUAL"
    chat.model = model
    db.commit()
    db.refresh(chat)
    return {"chat_id": chat_id, "model": model}


async def get_model_for_chat(chat):
    return chat.model


async def get_model_for_new_chat(prompt):
    classification = await classify_prompt(prompt)
    model= MODEL_MAP[classification.category]
    return model