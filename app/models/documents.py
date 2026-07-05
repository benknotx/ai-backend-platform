from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime, timezone



class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable = False)
    visibility = Column(String, default = "private")
    raw_text=  Column(Text)
    clean_text = Column(Text)
    created_at = Column(DateTime, default= datetime.now(timezone.utc))
    embedded_bool = Column(Boolean, default= False, nullable = False)
    embedding_model = Column(String, nullable=True)
    embedded_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")





