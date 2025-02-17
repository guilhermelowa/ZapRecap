import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from app.database import SQLALCHEMY_DATABASE_URL, get_database_url  # noqa: E402
from app.models.database_models import ParsedConversation  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
import logging  # noqa: E402
import argparse  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def cleanup_conversations(days: int = 2, dry_run: bool = False, delete_all: bool = False):
    """
    Remove parsed conversations

    :param days: Number of days to keep conversations
    :param dry_run: If True, only show what would be deleted without actually deleting
    :param delete_all: If True, delete ALL conversations regardless of age
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        if delete_all:
            # Query ALL conversations
            old_conversations = db.query(ParsedConversation).all()
            logger.info("Preparing to delete ALL conversations")
        else:
            # Query conversations older than specified days
            cutoff_date = datetime.now() - timedelta(days=days)
            old_conversations = (
                db.query(ParsedConversation)
                .filter(ParsedConversation.timestamp < cutoff_date)
                .all()
            )
            logger.info(
                f"Found {len(old_conversations)} conversations \
                older than {days} days (before {cutoff_date})"
            )

        count = len(old_conversations)

        if dry_run:
            logger.info("Dry run mode: No conversations will be deleted")
            for conv in old_conversations[:10]:  # Show first 10 as example
                logger.info(f"Would delete: ID {conv.id}, Timestamp {conv.timestamp}")
            if count > 10:
                logger.info(f"... and {count - 10} more conversations")
        else:
            for conv in old_conversations:
                db.delete(conv)

            db.commit()
            logger.info(f"Removed {count} conversations")

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        if not dry_run:
            db.rollback()
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Clean up parsed conversations from the database")
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        default=2,
        help="Number of days to keep conversations (default: 2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument("--all", action="store_true", help="Delete ALL conversations, ignoring age")

    args = parser.parse_args()

    # Log database connection details (without sensitive info)
    db_url = get_database_url()
    logger.info(f"Connecting to database: {db_url}")

    # If --all is used, override days parameter
    cleanup_conversations(days=args.days, dry_run=args.dry_run, delete_all=args.all)


if __name__ == "__main__":
    main()
