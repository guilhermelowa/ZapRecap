from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Tuple, List, Any

SQLALCHEMY_DATABASE_URL = "sqlite:///./suggestions.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True)
    suggestion = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")

class ParsedConversation(Base):
    __tablename__ = "parsed_conversations"

    id = Column(Integer, primary_key=True, index=True)
    content_hash = Column(String, unique=True, index=True)  # To identify unique conversations
    dates = Column(JSON)
    author_and_messages = Column(JSON)
    conversation = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    @property
    def parsed_data(self) -> Tuple[List[datetime], dict, List[Any]]:
        return (self.dates, self.author_and_messages, self.conversation)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 