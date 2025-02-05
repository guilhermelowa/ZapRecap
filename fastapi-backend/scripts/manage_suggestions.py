import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Suggestion, SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def print_menu():
    print("\n=== Suggestions Management ===")
    print("1. List all suggestions")
    print("2. List pending suggestions")
    print("3. Update suggestion status")
    print("4. Delete suggestion")
    print("5. Exit")
    return input("Choose an option: ")

def list_suggestions(status=None):
    query = session.query(Suggestion)
    if status:
        query = query.filter(Suggestion.status == status)
    
    suggestions = query.all()
    for s in suggestions:
        print(f"\nID: {s.id}")
        print(f"Suggestion: {s.suggestion}")
        print(f"Status: {s.status}")
        print(f"Timestamp: {s.timestamp}")
        print("-" * 50)

def update_status():
    suggestion_id = input("Enter suggestion ID: ")
    new_status = input("Enter new status (pending/approved/rejected): ")
    
    suggestion = session.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if suggestion:
        suggestion.status = new_status
        session.commit()
        print("Status updated successfully!")
    else:
        print("Suggestion not found!")

def delete_suggestion():
    suggestion_id = input("Enter suggestion ID to delete: ")
    suggestion = session.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if suggestion:
        session.delete(suggestion)
        session.commit()
        print("Suggestion deleted successfully!")
    else:
        print("Suggestion not found!")

if __name__ == "__main__":
    while True:
        choice = print_menu()
        if choice == "1":
            list_suggestions()
        elif choice == "2":
            list_suggestions("pending")
        elif choice == "3":
            update_status()
        elif choice == "4":
            delete_suggestion()
        elif choice == "5":
            sys.exit(0)
        else:
            print("Invalid option!") 