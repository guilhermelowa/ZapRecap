from bisect import bisect_left
from datetime import datetime, timedelta
from app.models.data_formats import Message
import re
import json
from hashlib import sha256
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.database_models import ParsedConversation
import logging

logger = logging.getLogger(__name__)


def is_new_message(line):
    # Check if line starts with date pattern DD/MM/YYYY HH:MM
    date_pattern = r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}"
    return bool(re.match(date_pattern, line))


def parse_line(line):
    # Split line into date and message
    date, message = line.split(" - ", 1)
    date = datetime.strptime(date, "%d/%m/%Y %H:%M")
    return date, message


def parse_message(message):
    # Split message into author and content
    try:
        author, content = message.split(": ", 1)
        return author, content
    except ValueError:
        return "None", "None"


def store_message(messages, msg):
    # Store message in messages dictionary
    try:
        messages[msg.author].append(msg)
    except KeyError:
        messages[msg.author] = [msg]
    except TypeError:
        pass


def get_last_years_dates(dates, days=365):
    today = datetime.now()
    cutoff = today - timedelta(days=days)
    result = bisect_left(dates, cutoff)
    return dates[result:]


def parse_whatsapp_chat(chat_text):
    dates = []
    author_and_messages = {}
    conversation = []
    current_author = None
    current_message = None

    now = datetime.now()
    OLDEST_DATE = now - timedelta(days=365)
    date = now - timedelta(days=365 * 2)

    lines = chat_text.split("\n")
    lines = [line.strip().lower() for line in lines if line.strip()]

    if len(lines) < 2:  # Check if there are at least 2 lines
        return [], {}, []

    while date < OLDEST_DATE:
        lines = lines[1:]  # skip line. always skip first line (default WhatsApp msg)
        date, message = parse_line(lines[1])

    dates.append(date)
    current_author, current_message = parse_message(message)

    # Skip if author is None
    if current_author != "None":
        msg = Message(date=date, author=current_author, content=current_message)
        conversation.append(msg)
        author_and_messages[current_author] = [msg]

    for line in lines[2:]:  # Process remaining lines
        if is_new_message(line):
            if current_author != "None":  # Only process if author is not None
                msg = Message(date=date, author=current_author, content=current_message)
                store_message(author_and_messages, msg)
                conversation.append(msg)
            date, message = parse_line(line)
            dates.append(date)
            current_author, current_message = parse_message(message)
        else:
            current_message += " " + line

    # Handle last message
    if current_author != "None":  # Only process if author is not None
        msg = Message(date=date, author=current_author, content=current_message)
        store_message(author_and_messages, msg)
        conversation.append(msg)

    return dates, author_and_messages, conversation


def get_or_create_parsed_conversation(content: str, db: Session) -> tuple[list, dict, list, str]:
    """
    Retrieves parsed conversation from DB or creates new one if not exists.
    Returns (dates, author_and_messages, conversation, content_hash)
    """
    content_hash = sha256(content.encode()).hexdigest()

    parsed_conv = (
        db.query(ParsedConversation).filter(ParsedConversation.content_hash == content_hash).first()
    )

    if parsed_conv:
        logger.info("Found existing conversation in database")
        dates = [datetime.fromisoformat(d) for d in json.loads(parsed_conv.dates)]
        author_and_messages = {
            author: [Message.model_validate(msg) for msg in messages]
            for author, messages in json.loads(parsed_conv.author_and_messages).items()
        }
        conversation = [Message.model_validate(msg) for msg in json.loads(parsed_conv.conversation)]
        return dates, author_and_messages, conversation, content_hash

    logger.info("Parsing new conversation")
    dates, author_and_messages, conversation = parse_whatsapp_chat(content)

    # Convert Message objects to dictionaries before JSON serialization
    parsed_conv = ParsedConversation(
        content_hash=content_hash,
        dates=json.dumps([d.isoformat() for d in dates]),
        author_and_messages=json.dumps(
            {
                author: [message_to_dict(msg) for msg in messages]
                for author, messages in author_and_messages.items()
            }
        ),
        conversation=json.dumps([message_to_dict(msg) for msg in conversation]),
    )

    try:
        db.add(parsed_conv)
        db.commit()
        db.refresh(parsed_conv)
    except IntegrityError:
        logger.warning("Race condition occurred, rolling back and fetching existing record")
        db.rollback()
        parsed_conv = (
            db.query(ParsedConversation)
            .filter(ParsedConversation.content_hash == content_hash)
            .first()
        )
        dates = [datetime.fromisoformat(d) for d in json.loads(parsed_conv.dates)]
        author_and_messages = {
            author: [Message.model_validate(msg) for msg in messages]
            for author, messages in json.loads(parsed_conv.author_and_messages).items()
        }
        conversation = [Message.model_validate(msg) for msg in json.loads(parsed_conv.conversation)]

    return dates, author_and_messages, conversation, content_hash


def message_to_dict(msg: Message) -> dict:
    return {"date": msg.date.isoformat(), "author": msg.author, "content": msg.content}
