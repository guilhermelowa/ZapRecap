from bisect import bisect_left
from datetime import datetime, timedelta
from app.models.data_formats import Conversation, Message
import re

def is_new_message(line):
    # Check if line starts with date pattern DD/MM/YYYY HH:MM
    date_pattern = r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}'
    return bool(re.match(date_pattern, line))

def parse_line(line):
    # Split line into date and message
    date, message = line.split(' - ', 1)
    date = datetime.strptime(date, '%d/%m/%Y %H:%M')
    return date, message

def parse_message(message):
    # Split message into author and content
    try:
        author, content = message.split(': ', 1)
        return author, content
    except ValueError:
        return None, None

def store_message(messages, date, author, content):
    # Store message in messages dictionary
    try:
        messages[author].append((date, content))
    except KeyError:
        messages[author] = [(date, content)]
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
    oldest_date = now - timedelta(days=365).date()
    date = now - timedelta(days=365*2).date()

    lines = chat_text.split('\n')
    lines = [line.strip().lower() for line in lines if line.strip()]
    
    if len(lines) < 2:  # Check if there are at least 2 lines
        return [], {}
    
    while date < oldest_date:
        lines = lines[1:] # skip line. always skip first line (default WhatsApp msg)
        date, message = parse_line(lines[1])

    dates.append(date)
    current_author, current_message = parse_message(message)
    conversation.append(Message(date=date, author=current_author, content=current_message))

    for line in lines[2:]:  # Process remaining lines
        if is_new_message(line):
            store_message(author_and_messages, date, current_author, current_message)
            date, message = parse_line(line)
            dates.append(date)
            current_author, current_message = parse_message(message)
        else:
            current_message += ' ' + line
            
    dates = get_last_years_dates(dates)
    store_message(author_and_messages, date, current_author, current_message)
    
    return dates, author_and_messages, conversation