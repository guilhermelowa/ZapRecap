from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import SQLALCHEMY_DATABASE_URL, ParsedConversation
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_old_conversations(days: int = 2):
    """Remove parsed conversations older than specified days"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_conversations = (
            db.query(ParsedConversation).filter(ParsedConversation.timestamp < cutoff_date).all()
        )

        count = len(old_conversations)
        for conv in old_conversations:
            db.delete(conv)

        db.commit()
        logger.info(f"Removed {count} old conversations")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_old_conversations()
