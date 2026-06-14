from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime, timezone

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    model = Column(String)
    routing_mode = Column(String, default="AUTO")
    created_at = Column(DateTime, default= datetime.now(timezone.utc))
    summary = Column(Text, nullable= True)
    summary_message_count = Column(Integer, default=0)
    
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")