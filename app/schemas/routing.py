from pydantic import BaseModel

class RoutingMode(BaseModel):
    chat_id: int
    mode: str

class UpdateModel(BaseModel):
    chat_id: int
    model: str
