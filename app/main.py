from fastapi import FastAPI, Depends, Request, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import ollama
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.database.base import Base
from app.database.connection import engine
from app.database.session import get_db
import app.models as DBmodels
import app.services as helper
from app.integrations import ollama_client as ollama
import app.schemas as schemas
import app.core.security as auth
from fastapi.security import OAuth2PasswordRequestForm
import app.api.metrics as metrics
from slowapi.errors import RateLimitExceeded as RLE
from slowapi import _rate_limit_exceeded_handler as RLH
from app.core.rate_limit import limiter




Base.metadata.create_all(bind=engine)
app = FastAPI(title= "Private AI Platform")
app.state.limiter = limiter
app.add_exception_handler(RLE,RLH)



@app.get("/")
def read_root():
    return {"message": "Welcome to the Private AI Platform!"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return metrics.get_health(db)

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return metrics.stats(db)

@app.post("/auth/register", response_model=schemas.RegisterResponse)
@limiter.limit("2/minute")
def register(request: Request, login_request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    return auth.create_user(login_request.username, login_request.password, db)

@app.post("/auth/login", response_model=schemas.TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth.login_auth(form_data.username, form_data.password, db)

@app.get("/me", response_model=schemas.UserResponse)
def read_user(current_user: DBmodels.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/chat", response_model=schemas.ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: schemas.ChatRequest, current_user = Depends(auth.get_current_user), db : Session = Depends(get_db)):
    return await helper.process_chat(user_id = current_user.id,
                                                prompt=chat_request.prompt,
                                               chat_id=chat_request.chat_id,
                                                db=db)

@app.get("/chat/history/{chat_id}", response_model=schemas.EntireHistoryResponse)
@limiter.limit("10/minute")
def get_chat_history(request: Request, chat_id:int, current_user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return {"history": helper.get_chat_history_return_all(chat_id, current_user.id, db)}

@app.patch("/chat/{chat_id}/title", response_model= schemas.PatchTitleResponse)
def update_chat_title(chat_requests: schemas.PatchTitleRequest, current_user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    chat = helper.get_user_chat_or_404(chat_requests.chat_id, current_user.id, db)
    chat.title = chat_requests.title
    db.commit()
    db.refresh(chat)
    return {"chat_id": chat.id, "title": chat.title, "model": chat.model}

@app.get("/chat/list")
@limiter.limit("2/minute")
def get_chats(request: Request, db: Session= Depends(get_db), current_user = Depends(auth.get_current_user)):
    return helper.get_chat_list(current_user.id, db)

@app.post("/chat/stream")
@limiter.limit("10/minute")
async def stream_chat(request: Request, chat_request: schemas.ChatRequest, current_user = Depends(auth.get_current_user), db : Session = Depends(get_db)):
    if not chat_request.chat_id:
        chat_request.chat_id = helper.create_chat(current_user.id, db)
    helper.get_user_chat_or_404(chat_request.chat_id, current_user.id, db)
    async def event_generator():
        async for chunk in helper.process_stream_chat(user_id = current_user.id,
                                                prompt=chat_request.prompt,
                                               db=db, 
                                               chat_id=chat_request.chat_id):
            yield chunk
    return StreamingResponse(event_generator(), media_type="text/plain")

@app.get("/models")
def display_models():
    return {"models": ollama.get_installed_models()}

@app.patch("/model/update/routing_mode",response_model = schemas.RoutingMode)
def set_routing_mode(route_request: schemas.RoutingMode, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return helper.set_mode(route_request.chat_id, route_request.mode, current_user.id, db)
 

@app.patch("/model/update/model", response_model = schemas.UpdateModel)
def update_model(model_request: schemas.UpdateModel, current_user=Depends(auth.get_current_user),db: Session = Depends(get_db)):
    return helper.set_model(model_request.chat_id, model_request.model, current_user.id, db)

@app.delete("/chat/{chat_id}")
def delete_chat(chat_id: int, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return helper.del_chat(chat_id, current_user.id, db)


@app.get("/documents/list", response_model= schemas.DocumentList)
def retrieve_a_list_of_all__available_documents(request: Request, current_user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return {"documents": helper.get_all_available_documents(current_user.id, db)}


@app.get("/documents/{doc_id}", response_model = schemas.DocumentResponse)
def retrieve_document(request: Request, doc_id,current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return helper.get_accessible_document(doc_id, current_user.id, db)

@app.post("/documents/upload", response_model=schemas.DocumentResponse) 
async def upload_document(file: UploadFile, visibility: schemas.VisibilityEnum = schemas.VisibilityEnum.private, current_user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return await helper.upload_document_pipeline(file, current_user.id, visibility=visibility, db=db)

@app.delete("/documents/{id}")
def delete_document(doc_id: int, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return helper.document_delete_pipeline(doc_id, current_user.id, db)

@app.patch("/document/visibility", response_model=schemas.DocumentResponse)
def set_routing_mode(visibility_request: schemas.VisibilityChange, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return helper.visibility_update_pipeline(visibility_request.doc_id, visibility_request.visibility, current_user.id, db)
    
