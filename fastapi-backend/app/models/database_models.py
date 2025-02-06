from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

Base = declarative_base()

class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True)
    suggestion = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now())
    status = Column(String, default="pending")

class ParsedConversation(Base):
    __tablename__ = "parsed_conversations"

    id = Column(Integer, primary_key=True, index=True)
    content_hash = Column(String, unique=True, index=True)
    dates = Column(String)  # JSON string of dates
    author_and_messages = Column(String)  # JSON string of messages by author
    conversation = Column(String)  # JSON string of all messages
    timestamp = Column(DateTime, default=datetime.utcnow) 