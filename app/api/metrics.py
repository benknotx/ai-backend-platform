import app.models as DBmodels
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.services import routing_service
import app.integrations.chroma_client

def get_health(db):
    db_status=ollama_status="not connected"
    health_status = "down" 
    sync_status = "desynced"
    model_count = 0
    models = routing_service.get_installed_models()
    if db.query(DBmodels.User).first():
        db_status = "connected"
    if models:
        ollama_status = "connected"
        model_count = len(models)
    if db_status == "connected" and ollama_status =="connected":
        health_status = "healthy"
    if db.query(DBmodels.DocumentChunk).count() == app.integrations.chroma_client.count():
        sync_status = "synced"

    return {
        "status": health_status,
        "database": db_status,
        "ollama": ollama_status,
        "installed_models": model_count,
        "sync_status": sync_status
    }
    

def stats(db:Session):
    total_chats = db.query(DBmodels.Chat).count()
    users = db.query(DBmodels.User).count()
    total_messages = db.query(DBmodels.Message).count()
    model_usage_query = db.query(DBmodels.Message.model, func.count(DBmodels.Message.id)).filter(DBmodels.Message.model != "user").group_by(DBmodels.Message.model).all()
    model_usage = {model:count for model, count in model_usage_query}
    response_times_query = db.query(DBmodels.Message.response_time, DBmodels.Message.model).filter(DBmodels.Message.model !="user", DBmodels.Message.response_time != None).all()
    model_times_map = {model:[] for model in model_usage.keys()}
    doc_count= db.query(DBmodels.Document).count()
    chunk_count = db.query(DBmodels.DocumentChunk).count()
    vectors = app.integrations.chroma_client.count()
    documents_embedded_count= db.query(DBmodels.Document).filter(DBmodels.Document.embedded_bool == True ).count()
    for rt, model in response_times_query:
        if model in model_times_map:
            model_times_map[model].append(rt)
    time_data= {
        "average_response_time_seconds": round(sum([rt for rt, m in response_times_query])/len(response_times_query) if response_times_query else 0, 3),
        "fastest_response_seconds": round(min(rt for rt, model in response_times_query) if response_times_query else 0, 3),
        "slowest_response_seconds": round(max(rt for rt, model in response_times_query) if response_times_query else 0, 3),
        "model_response_times_seconds": {model:(round(sum(times)/len(times),3) if times else 0) for model, times in model_times_map.items()}
    }
    embedding_data={
        "documents": doc_count,
        "chunks": chunk_count,
        "vectors" : vectors,
        "embedded_documents": documents_embedded_count,
    }
    results = {
        "total_chats": total_chats,
        "total_users": users,
        "total_messages": total_messages,
        "most_model_used": max(model_usage, key=model_usage.get) if model_usage else None,
        "model_usage": model_usage,
        "time_data": time_data,
        "embedding_data" :  embedding_data
    }
    return results