from sqlalchemy.orm import Session
from sqlalchemy import func
import app.integrations.ollama_client as ollama_client
import app.models
from fastapi import HTTPException
import app.services as services
from app.core.config import MAX_CONTEXT_MESSAGES, MODEL_MAP
import time 

def add_message_to_db(chat_id, message, db: Session, model=None, response_time = None):
    message_entry = app.models.Message(chat_id=chat_id, role=message["role"], content =message["content"], model=model, response_time = response_time)
    db.add(message_entry)
    db.commit()
    db.refresh(message_entry)



async def process_chat(user_id, prompt, db: Session, chat_id):
    start_time = time.perf_counter()
    if not chat_id:
        new_chat_model= await services.routing_service.get_model_for_new_chat(prompt)
        chat_id = create_chat(user_id, db, new_chat_model)
    chat= get_user_chat_or_404(chat_id, user_id, db)
    user_message = {"role": "user", "content": prompt}
    add_message_to_db(chat_id, user_message, db, model = "user")
    selected_model = await services.routing_service.get_model_for_chat(chat)
    response = await ollama_client.chat(get_chat_history_return_conversation(chat_id, user_id, db), selected_model)
    assistant_message = {"role": "assistant", "content": response}
    elapsed_time = time.perf_counter()-start_time
    add_message_to_db(chat_id, assistant_message, db, model = selected_model, response_time = elapsed_time)
    await check_and_call_summarizer(chat_id, user_id, db)
    return {"chat_id": chat_id, "response": response}

async def process_stream_chat(user_id, prompt, db:Session, chat_id):
    start_time = time.perf_counter()
    user_message = {"role": "user", "content": prompt}
    add_message_to_db(chat_id, user_message, db, model = "user")
    chunks =[]
    selected_model = await services.routing_service.get_model_for_chat(get_user_chat_or_404(chat_id, user_id, db))
    conversation = get_chat_history_return_conversation(chat_id, user_id, db)
    async for chunk in ollama_client.stream_chat(conversation, selected_model):
        chunks.append(chunk)
        yield chunk
    full_response = "".join(chunks)
    assistant_message = {"role": "assistant", "content": full_response}
    elapsed_time = time.perf_counter()-start_time
    add_message_to_db(chat_id, assistant_message, db, model = selected_model, response_time = elapsed_time)
    await check_and_call_summarizer(chat_id, user_id, db)

def create_chat(id, db:Session, model):
    new_chat = app.models.Chat(user_id = id,
                               title = "New Chat", 
                               model = model)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat.id

def get_user_chat_or_404(chat_id, user_id, db: Session):
    chat = db.query(app.models.Chat).filter(app.models.Chat.user_id == user_id, app.models.Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail= "Chat not found")
    return chat

def get_chat_history_return_conversation(chat_id, user_id, db: Session):
    history = db.query(app.models.Message).join(app.models.Chat).filter(app.models.Message.chat_id == chat_id, app.models.Chat.user_id== user_id).order_by(app.models.Message.timestamp).all()
    chat = get_user_chat_or_404(chat_id, user_id, db)
    if not history:
        raise HTTPException(status_code=404, detail="Chat History not found")
    history = history[-MAX_CONTEXT_MESSAGES:]
    conversation= []
    if chat.summary:
        conversation.append({"role": "system", "content": f"Previous conversation summary: {chat.summary} use this summary as context."})
    for message in history:
        conversation.append({"role": message.role, "content": message.content})
    return conversation

def get_chat_history_return_all(chat_id, user_id, db: Session):
    history = db.query(app.models.Message).join(app.models.Chat).filter(app.models.Message.chat_id == chat_id, app.models.Chat.user_id== user_id).order_by(app.models.Message.timestamp).all()
    if not history:
        raise HTTPException(status_code=404, detail="Chat History not found")
    return [{"role": msg.role, "content": msg.content, "model": msg.model} for msg in history]


async def check_and_call_summarizer(chat_id, user_id, db):
    chat = get_user_chat_or_404(chat_id, user_id, db)
    message_count = (db.query(app.models.Message).filter(app.models.Message.chat_id == chat_id).count())
    if message_count >= (chat.summary_message_count + MAX_CONTEXT_MESSAGES):
        summary_data = await ollama_client.generate_chat_summary(chat_id, user_id, db)
        if chat.routing_mode =="AUTO":
            category = await services.classify_prompt(summary_data)
            chat.model= MODEL_MAP[category]
        chat.summary = summary_data
        chat.summary_message_count = message_count
        db.commit()


def get_chat_list(user_id, db:Session): 
    chats = db.query(app.models.Chat).filter(app.models.Chat.user_id == user_id).all()
    if not chats:
        raise HTTPException(status_code= 404, detail="No chats found!")
    return {"chats": [{"id": chat.id, "title": chat.title, "model": chat.model, "routing_mode": chat.routing_mode} for chat in chats]}

def del_chat(chat_id, user_id, db):
    chat = get_user_chat_or_404(chat_id, user_id, db)
    db.delete(chat)
    db.commit()
    return {"detail": "Chat deleted successfully"}
