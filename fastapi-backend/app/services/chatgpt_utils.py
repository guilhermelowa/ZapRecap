from collections import defaultdict
from typing import List, Dict, Tuple
from langdetect import detect
import openai
import tiktoken
import re
from app.models.data_formats import Message
import logging

logger = logging.getLogger(__name__)

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
    Ensures the total tokens stay under the model's limit of 16385 tokens.
    """
    prompts = {
        'pt': """Analise a seguinte conversa do WhatsApp e liste os principais temas discutidos.
        Forneça não apenas os temas, mas também exemplos da conversa que ilustram cada tema.
        
        Conversa:""",
        'en': """Analyze the following WhatsApp conversation and list the main themes discussed.
        Provide not only the themes but also examples from the conversation that illustrate each theme.
        
        Conversation:"""
    }
    
    base_prompt = prompts.get(language, prompts['en'])
    max_tokens = 16385  # GPT-3.5-turbo token limit
    base_tokens = count_tokens(base_prompt)
    max_conversation_tokens = max_tokens - base_tokens - 100  # Leave some buffer
    
    # Convert messages to text format
    messages_text = [f"{msg.author}: {msg.content}" for msg in conversation]
    
    # Start with all messages and remove from the end until we're under the token limit
    conversation_text = "\n".join(messages_text)
    while count_tokens(conversation_text) > max_conversation_tokens and messages_text:
        messages_text = messages_text[:-100]
        conversation_text = "\n".join(messages_text)
    
    return f"{base_prompt}\n{conversation_text}"

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text using GPT-3.5's tokenizer
    """
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

def extract_themes(conversation: List[Message]) -> Dict[str, str]:
    """
    Extract main themes from a conversation using ChatGPT
    """
    if not conversation:
        logger.warning("Empty conversation provided to extract_themes")
        return {}
        
    logger.info(f"Extracting themes from conversation with {len(conversation)} messages")
    themes_with_examples = defaultdict(str)
    
    try:
        client = openai.OpenAI()
        # Detect language
        language = detect_language(conversation)
        
        # Create prompt for ChatGPT
        prompt = create_prompt(conversation, language)
        
        # Call ChatGPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000  
        )
        
        # Extract themes from response
        response_text = response.choices[0].message.content.strip()
        
        # Split by numbered items (1., 2., etc) but keep the numbers
        themes = re.split(r'(?=\d+\.)', response_text)
        
        # Remove empty strings and process each theme
        themes = [t.strip() for t in themes if t.strip()]
        
        for theme_text in themes:
            # Extract theme and example
            theme, example = extract_examples_from_themes(theme_text, language)
            if theme and example:
                themes_with_examples[theme.strip()] = example.strip()

        return dict(themes_with_examples)
    except Exception as e:
        logger.error(f"Error in extract_themes: {str(e)}")
        return {}

def extract_examples_from_themes(theme: str, language: str) -> Tuple[str, str]:
    """
    Extract an example for a theme from a conversation
    """
    # Return empty strings if theme is empty
    if not theme.strip():
        return "", ""

    split_word = 'Exemplo:' if language == 'pt' else 'Example:'
    
    # Split by example marker, with fallback if no example is found
    parts = theme.split(split_word, 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    else:
        return parts[0].strip(), ""  # Return theme without example

def simulate_author_message(conversation: List[Message], author: str, prompt: str, language: str = 'pt') -> str:
    """
    Simulate a message from a specific author based on their writing style in the conversation.
    """
    # Get messages from the specific author to analyze their style
    author_messages = [msg for msg in conversation if msg.author == author]
    
    if not author_messages:
        return "Author not found in conversation"
    
    # Create a prompt that includes author's style examples and the user's prompt
    style_examples = "\n".join([f"{msg.content}" for msg in author_messages[:5]])
    
    system_prompts = {
        'pt': f"""Você é {author} em uma conversa de WhatsApp. Analise as seguintes mensagens reais de {author}:

        {style_examples}

        Baseado nessas mensagens, responda à próxima mensagem mantendo o mesmo estilo de escrita, incluindo:
        - Uso similar de emojis
        - Mesmo nível de formalidade
        - Mesmos padrões de pontuação
        - Gírias ou expressões características
        - Comprimento típico das mensagens

        Responda como {author} responderia à seguinte mensagem:""",
                'en': f"""You are {author} in a WhatsApp conversation. Analyze these real messages from {author}:

        {style_examples}

        Based on these messages, respond to the next message maintaining the same writing style, including:
        - Similar emoji usage
        - Same level of formality
        - Same punctuation patterns
        - Characteristic slang or expressions
        - Typical message length

        Respond as {author} would respond to the following message:"""
    }
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI()
        
        # Call ChatGPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompts.get(language, system_prompts['en'])},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error simulating message: {str(e)}")
        return "Error generating message"
