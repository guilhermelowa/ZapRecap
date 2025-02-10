from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.database import Suggestion, SQLALCHEMY_DATABASE_URL
import pandas as pd
import os
from datetime import datetime

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def print_all_suggestions():
    suggestions = session.query(Suggestion).all()
    print("\n=== All Suggestions ===")
    for s in suggestions:
        print(f"\nID: {s.id}")
        print(f"Suggestion: {s.suggestion}")
        print(f"Conversation ID: {s.conversation_id}")
        print(f"Timestamp: {s.timestamp}")
        print(f"Status: {s.status}")
        print("-" * 50)


def get_suggestions_stats():
    total = session.query(func.count(Suggestion.id)).scalar()
    pending = (
        session.query(func.count(Suggestion.id)).filter(Suggestion.status == "pending").scalar()
    )
    by_date = (
        session.query(func.date(Suggestion.timestamp), func.count(Suggestion.id))
        .group_by(func.date(Suggestion.timestamp))
        .all()
    )

    print("\n=== Suggestions Statistics ===")
    print(f"Total suggestions: {total}")
    print(f"Pending suggestions: {pending}")
    print("\nSuggestions by date:")
    for date, count in by_date:
        print(f"{date}: {count} suggestions")


def export_to_csv():
    suggestions = session.query(Suggestion).all()

    # Convert to DataFrame
    data = [
        {
            "id": s.id,
            "suggestion": s.suggestion,
            "conversation_id": s.conversation_id,
            "timestamp": s.timestamp,
            "status": s.status,
        }
        for s in suggestions
    ]

    df = pd.DataFrame(data)

    # Create backups directory if it doesn't exist
    backup_dir = "backups/suggestions"
    os.makedirs(backup_dir, exist_ok=True)

    # Save with timestamp
    filename = f"{backup_dir}/suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Backup saved to {filename}")


if __name__ == "__main__":
    print_all_suggestions()
    print("\n")
    get_suggestions_stats()
    export_to_csv()
