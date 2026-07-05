import app.models
from app.services import chunking_service
from app.services import document_service
from app.services import rag_service
from fastapi import HTTPException
import app.models as DBmodels
from loguru import logger



async def upload_document_pipeline(file, user_id, visibility, db):
    doc = await document_service.create_document(file, user_id, visibility, db)
    doc_id = doc.id
    logger.info(f"New document uploaded {doc_id}")
    chunks = chunking_service.generate_chunks(doc.clean_text)
    chunking_service.store_chunks(doc_id, chunks, db)
    stored = db.query(DBmodels.DocumentChunk).filter(DBmodels.DocumentChunk.document_id == doc.id).count()
    chunks = chunking_service.get_chunks_or_404(doc.id, db)
    logger.info(f"{len(chunks)} New Chunks from document {doc_id}")
    records = await rag_service.generate_embedding_records(doc_id, db)
    rag_service.store_embeddings(records)
    rag_service.mark_document_embedded(doc_id, db)
    chunk_amount = db.query(DBmodels.DocumentChunk).count()
    logger.info(f"total chunks in Database is now {chunk_amount}")
    return document_service.get_owned_document(doc_id, user_id, db)

def document_delete_pipeline(doc_id, user_id, db):
    logger.info(f"Document {doc_id} is being deleted by user {user_id}")
    rag_service.delete_embeddings(doc_id, db)
    chunking_service.delete_chunks(doc_id, db)
    document_service.delete_doc(doc_id, user_id, db)
    return{'details': "deletion complete"}

def visibility_update_pipeline(doc_id, visibility, user_id, db):
    document_service.set_visibility(doc_id, visibility, user_id, db)
    rag_service.update_embedding_visibility(doc_id, user_id, visibility, db)
    logger.info(f"Document {doc_id}'s visibility has been changed to {visibility} by {user_id}")
    return document_service.get_owned_document(doc_id, user_id, db)


async def regenerate_document_pipeline(doc_id, user_id, db):
    rag_service.delete_embeddings(doc_id, db)
    chunking_service.delete_chunks(doc_id, db)
    doc = document_service.get_owned_document(doc_id, user_id, db)
    chunks = chunking_service.generate_chunks(doc.clean_text)
    chunking_service.store_chunks(doc_id, chunks, db)
    records = await rag_service.generate_embedding_records(doc_id, db)
    rag_service.store_embeddings(records)
    rag_service.mark_document_embedded(doc_id, db)
    return document_service.get_owned_document(doc_id, user_id, db)

async def replace_document_pipeline(file, visibility, doc_id, user_id, db):
    document_delete_pipeline(doc_id, user_id, db)
    upload_document_pipeline(file, user_id, visibility, db)




