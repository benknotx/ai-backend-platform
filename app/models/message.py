from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime, timezone


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default= datetime.now(timezone.utc))
    model = Column(String, nullable= True)
    response_time = Column(Float, nullable= True)




    chat = relationship("Chat", back_populates="messages")
