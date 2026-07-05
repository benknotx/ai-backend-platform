import app.integrations.ollama_client as Ollama
from sqlalchemy.orm import Session
import app.services as helper
import app.integrations.chroma_client as ChromaClient
import app.models as DBmodels
import chromadb
from app.core.config import EMBEDDING_MODEL
from fastapi import HTTPException
from datetime import datetime, timezone
from loguru import logger


async def generate_embedding_records(doc_id, db):
    chunks = helper.get_chunks_or_404(doc_id, db)
    doc = db.query(DBmodels.Document).filter(DBmodels.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code= 404, detail= "Document not found")
    records=[]
    for chunk in chunks:
        embedding= await Ollama.generate_embeddings(chunk.content)
        records.append({
            "id": str(chunk.id),
            "document": chunk.content,
            "embedding": embedding,
            "metadata":{
                "user_id": doc.user_id,
                "document_id": doc.id,
                "visibility": doc.visibility
            }})
    logger.info(f"Embeddings generated for {doc_id}")
    return records

def mark_document_embedded(doc_id, db:Session):
    doc = db.query(DBmodels.Document).filter(DBmodels.Document.id==doc_id).first()
    if doc is None:
        raise HTTPException(status_code =404, detail="Document not found")
    doc.embedded_bool = True
    doc.embedding_model = EMBEDDING_MODEL
    doc.embedded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(doc)
    logger.info(f"Document {doc_id} marked as embedded")

def store_embeddings(records):
    if not records:
        raise HTTPException(status_code=400, detail="No records to store")
    return ChromaClient.store_records(records)

def delete_embeddings(doc_id, db:Session):
    chunks = db.query(DBmodels.DocumentChunk).filter((DBmodels.DocumentChunk.document_id == doc_id)).all()
    if not chunks:
        raise HTTPException(status_code=404,detail="Embedding not found")
    ids = [str(chunk.id) for chunk in chunks]
    ChromaClient.delete_records(ids)

async def regenerate_embeddings(doc_id, db:Session):
    delete_embeddings(doc_id, db)
    records = await  generate_embedding_records(doc_id, db)
    store_embeddings(records)

async def search_embeddings(text, user_id):
    query_embedding = await Ollama.generate_embeddings(text)
    where_filter = {"$or": [ {"user_id":user_id}, {"visibility":"public"}]}
    results = ChromaClient.search_records(query_embedding, where_filter)
    if not results:
        return None
    return format_embeddings(results)

def format_embeddings(records):
    results=[]
    for id_, document, metadata, distance in zip(
        records['ids'][0],
        records['documents'][0],
        records['metadatas'][0],
        records['distances'][0]):
        results.append({ "id": id_, 
                         "content": document, 
                         "metadata": metadata,
                         "distance": distance})
    return results

def update_embedding_visibility(doc_id, user_id, visibility, db):
    chunks = db.query(DBmodels.DocumentChunk).filter((DBmodels.DocumentChunk.document_id == doc_id)).all()
    if not chunks:
        raise HTTPException(status_code=404,detail="Embedding not found59")
    chunk_ids = [str(chunk.id) for chunk in chunks]
    new_metadata=[{
                 "user_id": user_id,
                "document_id": doc_id,
                "visibility": visibility}
                for i in range(len(chunk_ids))]
    ChromaClient.update_visibility(chunk_ids, new_metadata)
    logger.info(f"Embedding metadata updated for Document {doc_id} by {user_id} to {visibility}")


def build_context(rag_context):
    if rag_context:
        content_list = [item["content"] for item in rag_context]
        breakline= "\n----------\n"
        return f"Relevent Context\n{breakline} Use the following information if it helps answer the user's question.\nIf the context is not relevant, answer normally.\n{breakline}\n" +breakline.join(content_list)
    
    else:
        return None


async def retrieve_context(text, user_id):
    return build_context(await search_embeddings(text, user_id))



