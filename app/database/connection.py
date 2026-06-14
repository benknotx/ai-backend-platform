from sqlalchemy import create_engine
from app.core.config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)