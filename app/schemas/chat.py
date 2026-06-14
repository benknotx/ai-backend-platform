from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    chat_id: Optional[int] = None
    prompt: str

class ChatResponse(BaseModel):
    chat_id: int
    response: str

class MessageResponse(BaseModel):
    role: str
    content: str
    model: Optional[str]= None

class EntireHistoryResponse(BaseModel):
    history: list[MessageResponse]


class PatchTitleRequest(BaseModel):
    chat_id: int
    title: str

class PatchTitleResponse(BaseModel):
    chat_id: int
    title: str
    model: str

class ChatListResponse(BaseModel):
    chats: list[PatchTitleResponse]


