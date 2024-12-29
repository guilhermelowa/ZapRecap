import calendar
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd
import re
from app.services.parsing_utils import parse_whatsapp_chat

# Download required NLTK data
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')

# Get Portuguese stop words
stop_words = set(stopwords.words('portuguese'))

# Add custom stop words
custom_stop_words = {'pra', 'tá', 'q', 'tb', 'né', 'tô', 'ta', 'to', 'mídia', 'oculta'}
stop_words.update(custom_stop_words)
curse_words = {'porra', 'caralho', 'merda', 'foda', 'fodase', 'foda-se', 'puta', 'putas', 'putinha', 'putinhas', 'putao'}

def create_messages_heatmap(dates):
    # Create DataFrame from dates list
    df = pd.DataFrame({'datetime': dates})

    # Add necessary columns for heatmap
    df['weekday'] = df['datetime'].dt.dayofweek
    df['month_year'] = df['datetime'].dt.strftime('%m/%Y')
    df['week'] = df['datetime'].dt.isocalendar().week

    # Create pivot table for heatmap
    pivot = pd.pivot_table(
        df,
        values='datetime',
        index='weekday',
        columns=['month_year', 'week'],
        aggfunc='count',
        fill_value=0
    )

    # Flatten multi-index columns
    pivot.columns = [f"{m}_{w}" for m, w in pivot.columns]

    # Normalize data using percentile-based scaling
    vmax = np.percentile(pivot.values[pivot.values > 0], 95)  # 95th percentile
    vmin = np.percentile(pivot.values[pivot.values > 0], 5)   # 5th percentile

    # Create heatmap with green colormap
    plt.figure(figsize=(20, 5))
    ax = plt.gca()
    plt.imshow(pivot, cmap='Greens', aspect='auto', vmin=vmin, vmax=vmax)
    plt.colorbar(label='Message Count')

    # Add labels
    plt.yticks(range(7), calendar.day_name)

    # Create x-axis labels (show month only at transitions)
    month_labels = []
    prev_month = None
    for col in pivot.columns:
        month = col.split('_')[0]
        if month != prev_month:
            month_labels.append(month)
            prev_month = month
        else:
            month_labels.append('')

    plt.xticks(range(len(pivot.columns)), month_labels, rotation=45)
    plt.xlabel('Month/Year')
    plt.ylabel('Day of Week')

    # Remove grid and border
    ax.grid(False)
    ax.set_frame_on(False)

    plt.tight_layout()
    plt.show()

def calculate_conversation_length_stats(dates, time_threshold=30*60):
    # Initialize variables
    conversation_messages = []
    current_conversation = []
    max_conversation = []

    # Group messages into conversations
    for i in range(len(dates)-1):
        current_conversation.append(dates[i])
        
        # Calculate time difference with next message
        time_diff = (dates[i+1] - dates[i]).total_seconds()
        
        # If gap is more than 30 minutes, end current conversation
        if time_diff > time_threshold:
            if len(current_conversation) > len(max_conversation):
                max_conversation = current_conversation.copy()
            conversation_messages.append(len(current_conversation))
            current_conversation = []

    # Handle last message
    current_conversation.append(dates[-1])
    conversation_messages.append(len(current_conversation))
    if len(current_conversation) > len(max_conversation):
        max_conversation = current_conversation

    # Calculate average
    avg_length = sum(conversation_messages) / len(conversation_messages)

    return {
        'average_length': round(avg_length, 2),
        'longest_conversation_length': len(max_conversation),
        'longest_conversation_start': max_conversation[0],
        'longest_conversation_end': max_conversation[-1]
    }

# Function to clean and tokenize text
def process_text(text):
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^\w\s]', '', text)
    
    # Tokenize
    words = word_tokenize(text)
    
    # Remove stop words and short words
    words = [word for word in words if word not in stop_words]
    
    return words

def get_most_common_words(author_and_messages, top_n=20):
    # Process all messages
    all_words = []
    for author, messages in author_and_messages.items():
        if author is not None:  # Skip None author
            for _, content in messages:
                words = process_text(content)
                all_words.extend(words)

    # Count word frequencies
    word_counts = Counter(all_words)

    # Get the most common words
    most_common = word_counts.most_common(top_n)

    return most_common

def get_word_metrics(author_and_messages):
    """
    Analyze word metrics for each author in the chat
    We analyze word frequency and curse words usage
    """
    
    messages_per_author = {}
    message_lengths = {}
    curse_words_count = {}
    curse_words_by_author = defaultdict(Counter)
    curse_words_frequency = Counter()

    # Calculate all metrics in a single loop
    for author, messages in author_and_messages.items():
        if author is not None:
            # Message count and length calculations
            messages_per_author[author] = len(messages)
            total_length = sum(len(msg[1]) for msg in messages)
            message_lengths[author] = total_length / len(messages)
            
            # curse_words calculations
            curse_words_count[author] = 0
            for _, content in messages:
                for word in curse_words:
                    count = content.count(word)
                    if count > 0:
                        curse_words_count[author] += count
                        curse_words_by_author[author][word] += count
                        curse_words_frequency[word] += count

    # Sort results
    sorted_messages = dict(sorted(messages_per_author.items(), key=lambda x: x[1], reverse=True))
    sorted_curse_words = dict(sorted(curse_words_count.items(), key=lambda x: x[1], reverse=True))

    return {
        'messages_per_author': sorted_messages,
        'average_message_length': message_lengths,
        'curse_words_per_author': sorted_curse_words,
        'curse_words_by_author': dict(curse_words_by_author),
        'curse_words_frequency': dict(curse_words_frequency.most_common())
    }

def calculate_all_metrics(chat_content):
    # Parse the chat content
    dates, author_messages = parse_whatsapp_chat(chat_content)

    # Calculate all metrics
    heatmap_data = create_messages_heatmap(dates)
    conversation_stats = calculate_conversation_length_stats(dates)
    word_metrics = get_word_metrics(author_messages)
    common_words = get_most_common_words(author_messages)

    return {
        'conversation_stats': conversation_stats,
        'word_metrics': word_metrics,
        'common_words': [{'word': word, 'count': count} for word, count in common_words]
    }