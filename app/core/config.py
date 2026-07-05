from dotenv import load_dotenv
import os 
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
DATABASE_URL = os.getenv("DATABASE_URL")
OLLAMA_URL = os.getenv("OLLAMA_URL")
BASE_OLLAMA_URL = os.getenv("BASE_OLLAMA_URL")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")

MAX_CONTEXT_MESSAGES = 20
MODEL_MAP = {
    "CODER": "qwen3-coder:latest",
    "GENERAL": "qwen:latest",
    "CHAT": "gemma4:e4b",
    "SUMMARY": "gemma3:1b"
}

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
EMBEDDING_URL = os.getenv("EMBEDDING_URL")

CHROMA_PATH = os.getenv("CHROMA_PATH")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION")

