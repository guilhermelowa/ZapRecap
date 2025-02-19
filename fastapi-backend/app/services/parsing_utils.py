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
import zipfile
import io
from fastapi import UploadFile, HTTPException

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

    Raises:
    - ValueError: If the chat text is invalid or no valid messages are found
    """
    try:
        # Split raw text into lines without preprocessing
        lines = chat_text.split("\n")

        # Find the index of the first valid message
        try:
            first_valid_index = _find_first_valid_message_index(lines)
        except ValueError as e:
            raise ValueError(f"Invalid WhatsApp chat format: {str(e)}")

        return _process_chat_lines_from_index(lines[first_valid_index:])
    except (IndexError, AttributeError) as e:
        raise ValueError(f"Invalid WhatsApp chat format: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in parse_whatsapp_chat: {e}")
        raise ValueError(f"Error parsing WhatsApp chat: {str(e)}")


def _find_first_valid_message_index(lines):
    """
    Find the index of the first valid message line.

    Args:
        lines (list): Raw chat lines

    Returns:
        int: Index of first valid line, or -1 if no valid line found
    """
    if not lines:
        raise ValueError("No valid messages found in chat text")

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

    raise ValueError("No valid WhatsApp chat messages found in the content")


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


def _handle_new_message_line(
    line, current_date, current_author, current_message, dates, author_and_messages, conversation
):
    """
    Handle processing of a new message line.

    Args:
        line (str): Current line being processed
        current_date (datetime): Current message date
        current_author (str): Current message author
        current_message (str): Current message content
        dates (list): List of dates
        author_and_messages (dict): Messages by author
        conversation (list): Overall conversation list

    Returns:
        tuple: Updated (current_date, current_author, current_message)
    """
    # Store previous message if exists
    if current_author and current_author != "None" and current_message:
        msg = _create_message(current_date, current_author, current_message)
        _update_conversation_data(conversation, author_and_messages, msg)

    # Parse new message
    current_date, message = parse_line(line)
    dates.append(current_date)
    current_author, current_message = parse_message(message)

    return current_date, current_author, current_message


def _process_chat_lines_from_index(lines):
    """
    Process chat lines starting from a valid message.

    Args:
        lines (list): Chat lines starting from first valid message

    Returns:
        tuple: (dates, author_and_messages, conversation)

    Raises:
        ValueError: If the chat format is invalid or no valid messages are found
    """
    if not lines:
        raise ValueError("No valid WhatsApp chat messages found")

    dates = []
    author_and_messages = {}
    conversation = []

    current_date = None
    current_author = None
    current_message = None

    try:
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # If it's a new message line
            if is_new_message(line):
                current_date, current_author, current_message = _handle_new_message_line(
                    line,
                    current_date,
                    current_author,
                    current_message,
                    dates,
                    author_and_messages,
                    conversation,
                )
            else:
                # Accumulate multi-line messages
                if current_message is None:
                    raise ValueError("Invalid chat format: message content without header")
                current_message += " " + line

        # Handle last message
        if current_author and current_author != "None" and current_message:
            final_msg = _create_message(current_date, current_author, current_message)
            _update_conversation_data(conversation, author_and_messages, final_msg)

        if not dates:
            raise ValueError("No valid WhatsApp chat messages found")

        return dates, author_and_messages, conversation

    except (IndexError, AttributeError) as e:
        raise ValueError(f"Invalid WhatsApp chat format: {str(e)}")


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


def extract_txt_from_zip(zip_content: bytes) -> str:
    """
    Extract the first .txt file from a zip file.

    Args:
        zip_content (bytes): Zip file content

    Returns:
        str: Content of the first .txt file found
    """
    with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zip_ref:
        # Find the first .txt file
        txt_files = [f for f in zip_ref.namelist() if f.lower().endswith(".txt")]

        if not txt_files:
            raise ValueError("No .txt file found in the zip archive")

        # Read the first .txt file
        with zip_ref.open(txt_files[0]) as txt_file:
            return txt_file.read().decode("utf-8", errors="replace")


async def extract_file_content(file: UploadFile) -> str:
    """
    Extract and validate content from an uploaded file.

    Args:
        file (UploadFile): The uploaded file

    Returns:
        str: The extracted content

    Raises:
        HTTPException: If file type is unsupported or content is empty
    """
    # Reset file pointer to beginning
    await file.seek(0)

    # Read file content
    content = await file.read()

    # Determine file type and extract content
    try:
        if file.filename.lower().endswith(".txt"):
            file_content = content.decode("utf-8", errors="replace")
        elif file.filename.lower().endswith(".zip"):
            file_content = extract_txt_from_zip(content)
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported file type. Please upload a .txt or .zip file."
            )

        if not file_content.strip():
            raise HTTPException(status_code=422, detail="File content cannot be empty")

        return file_content

    except HTTPException:
        raise
    except ValueError as ve:
        # Specific error for no .txt file in zip
        if "No .txt file found in the zip archive" in str(ve):
            raise HTTPException(status_code=422, detail="No .txt file found in the zip archive")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(ve)}")
    except Exception as e:
        logger.error(f"Error extracting file content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
