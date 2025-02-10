from typing import List, Dict, Tuple
from langdetect import detect, LangDetectException
import openai
import tiktoken
from app.models.data_formats import Message
import logging
import random
import json

logger = logging.getLogger(__name__)


def detect_language(conversation: List[Message]) -> str:
    """
    Detect the language of the conversation. Returns 'en' for English or 'pt' for Portuguese.
    Falls back to 'en' if detection fails.
    """
    try:
        conversation_text = "\n".join([msg.content for msg in conversation])
        lang = detect(conversation_text)
        return "pt" if lang == "pt" else "en"
    except (LangDetectException, ValueError) as e:
        logger.warning(f"Language detection failed: {str(e)}")
        return "en"


def create_prompt(conversation: List[Message], language: str, max_output_tokens: int) -> dict:
    """
    Create the system and user messages for ChatGPT based on the conversation and detected language.
    Returns a dictionary with the structured format specification and conversation.
    """
    system_prompts = {
        "pt": (
            "Analise a seguinte conversa do WhatsApp e liste os 5 à 9 principais temas.\n"
            "Forneça não apenas os temas, mas também exemplos que ilustram cada tema.\n"
            "Retorne a resposta no formato JSON especificado."
        ),
        "en": (
            "Analyze the following WhatsApp conversation and list 5 to 9 main themes.\n"
            "Provide not only the themes but also examples that illustrate each theme.\n"
            "Return the response in the specified JSON format."
        ),
    }

    # Define the JSON structure we want
    json_structure = {
        "type": "object",
        "properties": {
            "themes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string"},
                        "example": {"type": "string"},
                    },
                    "required": ["theme", "example"],
                },
            }
        },
        "required": ["themes"],
    }

    # Convert messages to text format
    messages_text = [f"{msg.author}: {msg.content}" for msg in conversation]
    conversation_text = format_conversation_within_token_limit(
        messages_text,
        system_prompts.get(language, system_prompts["en"]),
        max_output_tokens,
    )

    return {
        "system_message": system_prompts.get(language, system_prompts["en"]),
        "user_message": conversation_text,
        "json_structure": json_structure,
    }


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text using GPT-3.5's tokenizer
    """
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))


def format_conversation_within_token_limit(
    messages: List[str], system_prompt: str, max_output_tokens: int
) -> str:
    """Helper function to format conversation text within token limits"""
    max_tokens = 16385  # GPT-3.5-turbo token limit
    base_tokens = count_tokens(system_prompt)
    max_conversation_tokens = (
        max_tokens - base_tokens - max_output_tokens - 100
    )  # Leave some buffer

    conversation_text = "\n".join(messages)
    while (
        count_tokens(conversation_text) > (max_conversation_tokens - max_output_tokens) and messages
    ):
        messages = messages[:-100]
        conversation_text = "\n".join(messages)

    return conversation_text


def parse_themes_response(response_json: dict) -> Dict[str, str]:
    """
    Parse the structured JSON response from OpenAI into a dictionary of themes and examples.

    Args:
        response_json: JSON response from OpenAI containing themes and examples

    Returns:
        Dictionary mapping themes to their examples
    """
    themes_with_examples = {}
    try:
        # Check for both 'themes' and 'temas' keys
        themes_array = response_json.get("themes", response_json.get("temas", []))
        for theme_item in themes_array:
            # Get theme name (support both English and Portuguese keys)
            theme = theme_item.get("theme", theme_item.get("tema", "")).strip()

            # Get examples
            # Due variance in OpenAI API responses, it has to support:
            # Both English and Portuguese keys
            # Both single and array formats
            examples = theme_item.get(
                "examples", theme_item.get("exemplos", theme_item.get("example", []))
            )

            # Convert single string to list for consistent handling
            if isinstance(examples, str):
                examples = [examples]

            # Join examples with separator if we have valid theme and examples
            if theme and examples:
                themes_with_examples[theme] = " | ".join(examples).strip()

    except Exception as e:
        logger.error(f"Error parsing themes response: {str(e)}")

    return themes_with_examples


def extract_themes(conversation: List[Message], model: str = "gpt-3.5-turbo") -> Dict[str, str]:
    """
    Extract main themes from a conversation using specified OpenAI model with structured output
    """
    MAX_OUTPUT_TOKENS = 1000

    if not conversation:
        logger.warning("Empty conversation provided to extract_themes")
        return {}

    logger.info(f"Extracting themes from conversation with {len(conversation)} messages")

    sampled_messages = sample_conversation(conversation)
    logger.info(f"Created {len(sampled_messages)} message samples for theme analysis")

    try:
        client = openai.OpenAI()
        language = detect_language(sampled_messages)
        prompt_data = create_prompt(sampled_messages, language, MAX_OUTPUT_TOKENS)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt_data["system_message"]},
                {"role": "user", "content": prompt_data["user_message"]},
            ],
            temperature=0.7,
            max_tokens=MAX_OUTPUT_TOKENS,
            response_format={"type": "json_object"},
        )

        response_json = response.choices[0].message.content
        logger.info(f"Extract themes Response: {response_json}")

        themes_with_examples = parse_themes_response(json.loads(response_json))

        return themes_with_examples
    except Exception as e:
        logger.error(f"Error in extract_themes: {str(e)}")
        return {}


def sample_conversation(
    conversation: List[Message], sample_size: int = 50, num_samples: int = 20
) -> List[Message]:
    """
    Sample the conversation into smaller chunks for analysis.
    Returns a list of messages containing multiple consecutive chunks of the conversation.

    Args:
        conversation: Full list of messages
        sample_size: Size of each consecutive message chunk
        num_samples: Number of chunks to sample
    """
    if len(conversation) <= sample_size * num_samples:
        return conversation

    samples = []
    # Create samples of consecutive messages
    valid_start_indices = range(len(conversation) - sample_size)
    selected_starts = random.sample(valid_start_indices, min(num_samples, len(valid_start_indices)))

    for start_idx in selected_starts:
        samples.extend(conversation[start_idx : start_idx + sample_size])

    return samples


def extract_examples_from_themes(theme: str, language: str) -> Tuple[str, str]:
    """
    Extract an example for a theme from a conversation
    """
    # Return empty strings if theme is empty
    if not theme.strip():
        return "", ""

    split_word = "Exemplo:" if language == "pt" else "Example:"

    # Split by example marker, with fallback if no example is found
    parts = theme.split(split_word, 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    else:
        return parts[0].strip(), ""  # Return theme without example


def simulate_author_message(
    conversation: List[Message],
    author: str,
    prompt: str,
    language: str = "pt",
    model: str = "gpt-3.5-turbo",
) -> str:
    """
    Simulate a message from a specific author using specified OpenAI model
    """
    # Get messages from the specific author to analyze their style
    author_messages = [msg for msg in conversation if msg.author == author]

    if not author_messages:
        return "Author not found in conversation"

    # Create a prompt that includes author's style examples and the user's prompt
    style_examples = "\n".join([f"{msg.content}" for msg in author_messages[:5]])

    system_prompts = {
        "pt": (
            f"Você é {author} em uma conversa de WhatsApp.\n"
            f"Analise as seguintes mensagens reais de {author}:\n\n"
            f"{style_examples}\n\n"
            "Baseado nessas mensagens, responda mantendo o mesmo estilo de escrita, incluindo:\n"
            "- Uso similar de emojis\n"
            "- Mesmo nível de formalidade\n"
            "- Mesmos padrões de pontuação\n"
            "- Gírias ou expressões características\n"
            "- Comprimento típico das mensagens\n\n"
            f"Responda como {author} responderia à seguinte mensagem:"
        ),
        "en": (
            f"You are {author} in a WhatsApp conversation.\n"
            f"Analyze these real messages from {author}:\n\n"
            f"{style_examples}\n\n"
            "Based on these messages, respond maintaining the same writing style, including:\n"
            "- Similar emoji usage\n"
            "- Same level of formality\n"
            "- Same punctuation patterns\n"
            "- Characteristic slang or expressions\n"
            "- Typical message length\n\n"
            f"Respond as {author} would respond to the following message:"
        ),
    }

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompts.get(language, system_prompts["en"]),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=150,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error simulating message: {str(e)}")
        return "Error generating message"
