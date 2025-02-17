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
    return bool(re.match(date_pattern, line.strip()))


def parse_line(line):
    """
    Parse a line from WhatsApp chat export.
    Returns (datetime, message) or raises ValueError if line is not parseable.
    """
    line = line.strip()

    # Check if line matches date pattern
    if not is_new_message(line):
        raise ValueError(f"Line does not start with a date: {line}")

    try:
        # Split into date and message
        date_str, message = line.split(" - ", 1)
        date = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        return date, message
    except ValueError as e:
        # More detailed error logging
        logger.error(f"Error parsing line: {line}")
        logger.error(f"Specific error: {str(e)}")
        raise


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
    """
    Parse WhatsApp chat text into structured data.

    Returns:
    - dates: List of datetime objects
    - author_and_messages: Dictionary of messages by author
    - conversation: List of all messages
    """
    # Split raw text into lines without preprocessing
    lines = chat_text.split("\n")

    # Find the index of the first valid message
    first_valid_index = _find_first_valid_message_index(lines)

    # If no valid message found
    if first_valid_index == -1:
        logger.warning("No valid messages found in chat text")
        return [], {}, []

    try:
        return _process_chat_lines_from_index(lines[first_valid_index:])
    except Exception as e:
        logger.error(f"Unexpected error in parse_whatsapp_chat: {e}")
        return [], {}, []


def _find_first_valid_message_index(lines):
    """
    Find the index of the first valid message line.

    Args:
        lines (list): Raw chat lines

    Returns:
        int: Index of first valid line, or -1 if no valid line found
    """
    now = datetime.now()
    OLDEST_DATE = now - timedelta(days=365)

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        try:
            date, _ = parse_line(line)
            # Check if date is within the last year
            if date >= OLDEST_DATE:
                return i
        except ValueError:
            # Skip lines that can't be parsed
            continue

    return -1  # No valid message found


def _create_message(date, author, content):
    """
    Create a Message object.

    Args:
        date (datetime): Message date
        author (str): Message author
        content (str): Message content

    Returns:
        Message: Constructed message object
    """
    return Message(date=date, author=author, content=content.strip())


def _update_conversation_data(conversation, author_and_messages, msg):
    """
    Update conversation and author message collections.

    Args:
        conversation (list): Overall conversation list
        author_and_messages (dict): Messages by author
        msg (Message): Message to add
    """
    conversation.append(msg)
    store_message(author_and_messages, msg)


def _process_chat_lines_from_index(lines):
    """
    Process chat lines starting from a valid message.

    Args:
        lines (list): Chat lines starting from first valid message

    Returns:
        tuple: (dates, author_and_messages, conversation)
    """
    dates = []
    author_and_messages = {}
    conversation = []

    current_date = None
    current_author = None
    current_message = None

    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        try:
            # If it's a new message line
            if is_new_message(line):
                # Store previous message if exists
                if current_author and current_author != "None" and current_message:
                    msg = _create_message(current_date, current_author, current_message)
                    _update_conversation_data(conversation, author_and_messages, msg)

                # Parse new message
                current_date, message = parse_line(line)
                dates.append(current_date)
                current_author, current_message = parse_message(message)
            else:
                # Accumulate multi-line messages
                current_message += " " + line

        except ValueError:
            # Log and skip unparseable lines
            logger.warning(f"Skipping unparseable line: {line}")
            continue

    # Handle last message
    if current_author and current_author != "None" and current_message:
        final_msg = _create_message(current_date, current_author, current_message)
        _update_conversation_data(conversation, author_and_messages, final_msg)

    return dates, author_and_messages, conversation


def get_or_create_parsed_conversation(content: str, db: Session) -> tuple[list, dict, list, str]:
    """
    Retrieves parsed conversation from DB or creates new one if not exists.
    Returns (dates, author_and_messages, conversation, content_hash)
    """
    content_hash = sha256(content.encode()).hexdigest()

    # First, try to retrieve existing conversation
    parsed_conv = _retrieve_existing_conversation(db, content_hash)
    if parsed_conv:
        return _deserialize_parsed_conversation(parsed_conv)

    # If not found, parse the conversation
    dates, author_and_messages, conversation = parse_whatsapp_chat(content)

    # Attempt to store the new conversation
    try:
        parsed_conv = _store_new_conversation(
            db, content_hash, dates, author_and_messages, conversation
        )
    except IntegrityError:
        # Handle potential race condition
        logger.warning("Race condition occurred, rolling back and fetching existing record")
        db.rollback()
        parsed_conv = _retrieve_existing_conversation(db, content_hash)
        return _deserialize_parsed_conversation(parsed_conv)

    return dates, author_and_messages, conversation, content_hash


def _retrieve_existing_conversation(db: Session, content_hash: str):
    """
    Retrieve an existing parsed conversation from the database.

    Args:
        db (Session): Database session
        content_hash (str): Hash of the conversation content

    Returns:
        ParsedConversation or None
    """
    logger.info("Checking for existing conversation in database")
    return (
        db.query(ParsedConversation).filter(ParsedConversation.content_hash == content_hash).first()
    )


def _store_new_conversation(
    db: Session, content_hash: str, dates: list, author_and_messages: dict, conversation: list
):
    """
    Store a new parsed conversation in the database.

    Args:
        db (Session): Database session
        content_hash (str): Hash of the conversation content
        dates (list): List of dates
        author_and_messages (dict): Messages by author
        conversation (list): Full conversation list

    Returns:
        ParsedConversation: Stored database record
    """
    logger.info("Parsing and storing new conversation")

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

    db.add(parsed_conv)
    db.commit()
    db.refresh(parsed_conv)

    return parsed_conv


def _deserialize_parsed_conversation(parsed_conv):
    """
    Deserialize a ParsedConversation database record.

    Args:
        parsed_conv (ParsedConversation): Database record

    Returns:
        tuple: (dates, author_and_messages, conversation, content_hash)
    """
    logger.info("Deserializing existing conversation from database")

    dates = [datetime.fromisoformat(d) for d in json.loads(parsed_conv.dates)]

    author_and_messages = {
        author: [Message.model_validate(msg) for msg in messages]
        for author, messages in json.loads(parsed_conv.author_and_messages).items()
    }

    conversation = [Message.model_validate(msg) for msg in json.loads(parsed_conv.conversation)]

    return dates, author_and_messages, conversation, parsed_conv.content_hash


def message_to_dict(msg: Message) -> dict:
    return {"date": msg.date.isoformat(), "author": msg.author, "content": msg.content}
