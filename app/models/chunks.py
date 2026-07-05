from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime, timezone


class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    id = Column(Integer, primary_key = True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index= Column(Integer)
    content = Column(Text)
    
    document = relationship("Document", back_populates="chunks")
