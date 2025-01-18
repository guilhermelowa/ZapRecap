from collections import Counter, defaultdict
from typing import List
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np
import re
import os
import openai
from langdetect import detect
from app.models.data_formats import AnalysisResponse, ConversationStats, WordMetrics, HeatmapData, PeriodStats, Message
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

def create_messages_heatmap(dates) -> HeatmapData:
    # Initialize 7x53 matrix
    matrix = [[0] * 53 for _ in range(7)]
    dates_matrix = [[''] * 53 for _ in range(7)]

    # Count messages
    for date in dates:
        weekday = date.weekday()
        week = date.isocalendar()[1] - 1  # 0-52
        matrix[weekday][week] += 1
        dates_matrix[weekday][week] = date.strftime('%d/%m/%Y')
    
    # Initialize vmin and vmax
    vmin = 0
    vmax = 0
    
    # Normalize values
    all_values = [v for row in matrix for v in row if v > 0]
    vmin = float(np.percentile(all_values, 5))
    vmax = float(np.percentile(all_values, 95))
    
    return HeatmapData(
        z=matrix,
        x=[f'W{i+1}' for i in range(53)],
        y=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        dates=dates_matrix,
        zmin=vmin,
        zmax=vmax
    )

def calculate_conversation_stats(conversation, author_and_messages):
    # Calculate weekday, week, and month statistics
    weekday_counts, week_counts, month_counts, max_conversation, conversation_lenghts = calculate_conversation_parts(conversation)

    # Calculate average
    avg_length = sum(conversation_lenghts) / len(conversation_lenghts)

    # Find most/least active periods with counts
    weekday_most = max(weekday_counts.items(), key=lambda x: x[1])
    weekday_least = min(weekday_counts.items(), key=lambda x: x[1])
    
    week_most = max(week_counts.items(), key=lambda x: x[1])
    week_least = min(week_counts.items(), key=lambda x: x[1])
    
    month_most = max(month_counts.items(), key=lambda x: x[1])
    month_least = min(month_counts.items(), key=lambda x: x[1])

    # Create conversation samples
    themes = extract_themes(max_conversation)

    return ConversationStats(
        total_messages=len(conversation),
        participant_count=len(author_and_messages.keys()),
        average_length=round(avg_length, 2),
        longest_conversation_length=len(max_conversation),
        longest_conversation_start=max_conversation[0].date,
        longest_conversation_end=max_conversation[-1].date,
        most_active_weekday=PeriodStats(period=weekday_most[0], count=weekday_most[1]),
        least_active_weekday=PeriodStats(period=weekday_least[0], count=weekday_least[1]),
        most_active_week=PeriodStats(period=week_most[0], count=week_most[1]),
        least_active_week=PeriodStats(period=week_least[0], count=week_least[1]),
        most_active_month=PeriodStats(period=month_most[0], count=month_most[1]),
        least_active_month=PeriodStats(period=month_least[0], count=month_least[1]),
        themes=themes
    )

def calculate_conversation_parts(conversation: List[Message], time_threshold=30*60):
    # Initialize counters
    weekday_counts = {i: 0 for i in range(7)}  # 0-6: Mon-Sun
    week_counts = {i: 0 for i in range(53)}    # 0-52 weeks
    month_counts = {i: 0 for i in range(1, 13)} # 1-12 months

    current_conversation = []
    conversation_lenghts = []
    max_conversation = []

    for i, msg in enumerate(conversation[:-1]):
        current_conversation.append(msg)
        weekday_counts[msg.date.weekday()] += 1
        week_counts[msg.date.isocalendar()[1] - 1] += 1
        month_counts[msg.date.month] += 1

        # Calculate time difference with next message
        time_diff = (conversation[i+1].date - msg.date).total_seconds()
        if time_diff > time_threshold:
            if len(current_conversation) > len(max_conversation):
                max_conversation = current_conversation.copy()
            conversation_lenghts.append(len(current_conversation))
            current_conversation = []

    # Handle last message
    current_conversation.append(conversation[-1])
    conversation_lenghts.append(len(current_conversation))
    if len(current_conversation) > len(max_conversation):
        max_conversation = current_conversation.copy()

    return weekday_counts, week_counts, month_counts, max_conversation, conversation_lenghts

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
    return {word: count for word, count in most_common}

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
    message_lengths = dict(sorted(message_lengths.items(), key=lambda x: x[1], reverse=True))
    sorted_messages = dict(sorted(messages_per_author.items(), key=lambda x: x[1], reverse=True))
    sorted_curse_words = dict(sorted(curse_words_count.items(), key=lambda x: x[1], reverse=True))

    return WordMetrics(
        messages_per_author=sorted_messages,
        average_message_length=message_lengths,
        curse_words_per_author=sorted_curse_words,
        curse_words_by_author=dict(curse_words_by_author),
        curse_words_frequency=dict(curse_words_frequency.most_common())
    )

def detect_language(conversation: List[Message]) -> str:
    """
    Detect the language of the conversation. Returns 'en' for English or 'pt' for Portuguese.
    Falls back to 'en' if detection fails.
    """
    try:
        conversation_text = "\n".join([msg.content for msg in conversation])
        lang = detect(conversation_text)
        return 'pt' if lang == 'pt' else 'en'
    except:
        return 'en'

def create_prompt(conversation: List[Message], language: str) -> str:
    """
    Create the prompt for ChatGPT based on the conversation and detected language.
    """
    prompts = {
        'pt': """Analise a seguinte conversa do WhatsApp e liste os principais temas discutidos.
        Forneça não apenas os temas, mas também exemplos da conversa que ilustram cada tema.
        
        Conversa:""",
        'en': """Analyze the following WhatsApp conversation and list the main themes discussed.
        Provide not only the themes but also examples from the conversation that illustrate each theme.
        
        Conversation:"""
    }
    conversation_text = "\n".join([f"{msg.author}: {msg.content}" for msg in conversation])
    return f"{prompts.get(language, prompts['en'])}\n{conversation_text}"

def extract_themes(conversation: List[Message]) -> str:
    """
    Extract main themes from a conversation using ChatGPT
    """
    
    # Initialize OpenAI client
    client = openai.OpenAI()
    
    # Detect language
    language = detect_language(conversation)
    
    # Create prompt for ChatGPT
    prompt = create_prompt(conversation, language)
    
    # Call ChatGPT
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        
        # Extract themes from response
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error extracting themes: {str(e)}")
        return []

def calculate_all_metrics(chat_content: str) -> AnalysisResponse:
    """
    Calculate all metrics for the chat content
    """
    dates, author_and_messages, conversation = parse_whatsapp_chat(chat_content)
    
    return AnalysisResponse(
        conversation_stats=calculate_conversation_stats(conversation, author_and_messages),
        word_metrics=get_word_metrics(author_and_messages),
        heatmap_data=create_messages_heatmap(dates),
        common_words=get_most_common_words(author_and_messages)
    )