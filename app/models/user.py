from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime, timezone



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String) 
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default =False)
    created_at = Column(DateTime, default= datetime.now(timezone.utc))

    chats = relationship("Chat", back_populates="user")
    documents = relationship("Document", back_populates="user")