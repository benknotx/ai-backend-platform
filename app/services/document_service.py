from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
import app.models
import app.services as helper
import io
from pypdf import PdfReader
import re


def get_accessible_document(doc_id, user_id, db: Session):
    doc = db.query(app.models.Document).filter(app.models.Document.id == doc_id,or_(app.models.Document.user_id == user_id, app.models.Document.visibility=="public")).first()
    if not doc:
        raise HTTPException(status_code=404, detail= "Document not found")
    return doc

def get_owned_document(doc_id, user_id, db:Session):
    doc = db.query(app.models.Document).filter(app.models.Document.id == doc_id,app.models.Document.user_id == user_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail= "Document not found")
    return doc

def get_all_available_documents(user_id, db: Session):
    document_list = db.query(app.models.Document).filter(or_(app.models.Document.user_id == user_id, app.models.Document.visibility=="public")).all()
    if not document_list:
        raise HTTPException(status_code=404, detail="No documents Avaialble")
    return [{"id": doc.id, "filename": doc.filename, "visibility": doc.visibility} for doc in document_list]

async def create_document(file, user_id,  visibility, db:Session):
    text_content = await extract_text(file)
    clean_content = await clean_text(text_content)
    new_doc = app.models.Document(user_id = user_id, filename = file.filename,
                                  visibility= visibility, raw_text = text_content, clean_text = clean_content)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

def delete_doc(doc_id, user_id, db:Session):
    doc = get_owned_document(doc_id, user_id, db)
    if doc:
        db.delete(doc)
        db.commit()
    else:
        raise HTTPException(status_code= 404, detail= "Document not found")
    
def set_visibility(doc_id, mode, user_id, db):
    document = get_owned_document(doc_id, user_id, db)
    if mode not in ["private", "public"]:
        raise HTTPException(status_code=422, detail= "Entry must be private or public")
    if document:
        document.visibility = mode
        db.commit()
        db.refresh(document)
        return document
    else:
        raise HTTPException(status_code=404, detail= "Document not found")
    
async def extract_text(file):
    file_bytes = await file.read()
    extracted_text = ""
    if file.content_type == "application/pdf" or file.filename.endswith(".pdf"):
        try:
            pdf_stream = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_stream)
            pages_text = []
            for page in reader.pages:
                text = page.extract_text() or ""
                pages_text.append(text)
            extracted_text = "\n".join(pages_text)
        except Exception:
            raise HTTPException(status_code=400, detail="Failed to parse PDF contents.") 
    elif file.content_type in ["text/plain", ""] or file.filename.endswith(".txt"):
        try:
            extracted_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Text file must be UTF-8 encoded.")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF and TXT allowed.")
    return extracted_text

async def clean_text(raw_text):
    lines = raw_text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        line = line.lstrip("▢•*- ")
        line = re.sub(r'[ \t]+', ' ', line)
        if not line:
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    return text.strip() 
