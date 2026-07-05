from sqlalchemy.orm import Session
from sqlalchemy import insert, delete
import app.models
from fastapi import HTTPException
from app.core.config import CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL

def generate_chunks(clean_text):
    lines = clean_text.split('\n')
    chunks = []
    current_chunk = []
    current_length = 0 
    for line in lines:
        line_length = len(line) + 1
        if current_length + line_length > CHUNK_SIZE and current_chunk:
            combined_chunk = "\n".join(current_chunk)
            chunks.append(combined_chunk)
            overlap_chunk = []
            overlap_length = 0
            for prev_line in reversed(current_chunk):
                if overlap_length + len(prev_line) + 1 <= CHUNK_OVERLAP:
                    overlap_chunk.insert(0, prev_line)
                    overlap_length += len(prev_line) + 1
                else:
                    break
            current_chunk = overlap_chunk
            current_length = overlap_length
        current_chunk.append(line)
        current_length += line_length
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks

def get_chunks_or_404(doc_id, db:Session):
    chunks = db.query(app.models.DocumentChunk).filter(app.models.DocumentChunk.document_id == doc_id).all()
    if not chunks:
        raise HTTPException(status_code=404, detail= "Chunks not found")
    return chunks


def store_chunks(doc_id, chunks, db:Session):
    chunk_data =[
                    {"document_id": doc_id, "chunk_index": i, "content": chunk}
                    for i, chunk in enumerate(chunks)
                ]
    if chunk_data:
        db.execute(insert(app.models.DocumentChunk), chunk_data)
        db.commit()
    

def delete_chunks(doc_id, db:Session):
    stmt = delete(app.models.DocumentChunk).where(app.models.DocumentChunk.document_id == doc_id)
    db.execute(stmt)
    db.commit()

def regenerate_chunks(doc_id, clean_text,db:Session):
    get_chunks_or_404(doc_id, db)
    delete_chunks(doc_id, db)
    new_chunks = generate_chunks(clean_text)
    store_chunks(doc_id,new_chunks, db)




