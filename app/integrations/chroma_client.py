import chromadb
from app.core.config import CHROMA_COLLECTION, CHROMA_PATH

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=CHROMA_COLLECTION)

def store_records(records):
    if not records:
        return
    ids = [record["id"] for record in records]
    documents = [record["document"] for record in records]
    embeddings = [record["embedding"] for record in records]
    metadatas = [record["metadata"] for record in records]
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

def get_records_by_ids(ids):
    results = collection.get(ids=ids)
    if not results["ids"]:
        return None
    return results

def delete_records(ids):
    collection.delete(ids=ids)
    return len(ids)

def search_records(query_embedding, where_filter, nresults=5):
    results = collection.query(query_embeddings=[query_embedding], n_results=nresults,
                     where=where_filter)
    if not results["ids"][0]:
        return None
    return results
    
def update_visibility(chunk_ids, new_metadata):
    collection.update(
        ids = chunk_ids,
        metadatas = new_metadata
    )

def count():
    return collection.count()



