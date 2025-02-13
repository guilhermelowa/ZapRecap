import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime
from app.services.text_analyzer import Message
from app.services.chatgpt_utils import extract_themes, create_prompt, count_tokens


# Sample conversation data for tests
@pytest.fixture
def sample_conversation():
    return [
        Message(
            date=datetime(2024, 1, 1, 10, 0),
            author="Alice",
            content="Let's watch a movie tonight!",
        ),
        Message(
            date=datetime(2024, 1, 1, 10, 1),
            author="Bob",
            content="Sure! What about that new series?",
        ),
    ]


@pytest.fixture
def mock_openai_response_pt():
    # Create the nested structure properly
    message_mock = MagicMock()
    content_mock = PropertyMock(
        return_value="""{"themes": [
        {
            "theme": "Planejamento de encontros para assistir série juntos:",
            "example": "quer assistir disclosure beibe?"
        },
        {
            "theme": "Comentários sobre a qualidade da série assistida:",
            "example": "muito boa a safadeza dessa série"
        },
        {
            "theme": "Comentários sobre a interrupção da série para atividades cotidianas:",
            "example": "me chamaram pra comer agora de novo aaaaaa"
        }
    ]}"""
    )
    type(message_mock).content = content_mock

    choice_mock = MagicMock()
    type(choice_mock).message = PropertyMock(return_value=message_mock)

    response_mock = MagicMock()
    type(response_mock).choices = PropertyMock(return_value=[choice_mock])

    return response_mock


@pytest.fixture
def mock_openai_response_en():
    # Create the nested structure properly
    message_mock = MagicMock()
    content_mock = PropertyMock(
        return_value="""{"themes": [
        {
            "theme": "Planning movie nights together:",
            "example": "want to watch that new movie?"
        },
        {
            "theme": "Discussion about movie preferences:",
            "example": "I love action movies!"
        },
        {
            "theme": "Scheduling and timing discussions:",
            "example": "what time should we start?"
        }
    ]}"""
    )
    type(message_mock).content = content_mock

    choice_mock = MagicMock()
    type(choice_mock).message = PropertyMock(return_value=message_mock)

    response_mock = MagicMock()
    type(response_mock).choices = PropertyMock(return_value=[choice_mock])

    return response_mock


def test_extract_themes_portuguese(sample_conversation, mock_openai_response_pt):
    with patch("openai.OpenAI") as mock_openai, patch(
        "app.services.chatgpt_utils.detect_language", return_value="pt"
    ):
        # Setup mock
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response_pt
        mock_openai.return_value = mock_client

        # Run function
        result = extract_themes(sample_conversation)
        print("Test Result:", result)

        # Verify results
        assert isinstance(result, dict)
        assert "themes" in result
        assert len(result["themes"]) == 3
        assert (
            result["themes"][0]["theme"] == "Planejamento de encontros para assistir série juntos:"
        )
        assert result["themes"][0]["example"] == "quer assistir disclosure beibe?"


def test_extract_themes_english(sample_conversation, mock_openai_response_en):
    with patch("openai.OpenAI") as mock_openai, patch(
        "app.services.chatgpt_utils.detect_language", return_value="en"
    ):
        # Setup mock
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response_en
        mock_openai.return_value = mock_client

        # Run function
        result = extract_themes(sample_conversation)
        print("Test Result:", result)

        # Verify results
        assert isinstance(result, dict)
        assert "themes" in result
        assert len(result["themes"]) == 3
        assert result["themes"][0]["theme"] == "Planning movie nights together:"
        assert result["themes"][0]["example"] == "want to watch that new movie?"


def test_extract_themes_error_handling(sample_conversation):
    with patch("openai.OpenAI") as mock_openai:
        # Setup mock to raise an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        # Run function
        result = extract_themes(sample_conversation)

        # Verify error handling
        assert isinstance(result, dict)
        assert result == {}


def test_extract_themes_empty_response(sample_conversation):
    with patch("openai.OpenAI") as mock_openai:
        # Setup mock with empty response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = ""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Run function
        result = extract_themes(sample_conversation)

        # Verify handling of empty response
        assert isinstance(result, dict)
        assert result == {}


def test_extract_themes_malformed_response(sample_conversation):
    with patch("openai.OpenAI") as mock_openai:
        # Setup mock with malformed response (no examples)
        mock_response = MagicMock()
        mock_response.choices[
            0
        ].message.content = """Discussed Themes:
1. Theme without example
2. Another theme without example"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Run function
        result = extract_themes(sample_conversation)

        # Verify handling of malformed response
        assert isinstance(result, dict)
        assert result == {}  # Should handle malformed response gracefully


def test_prompt_token_limit():
    # Create a very long conversation
    long_conversation = []
    for i in range(10000):  # This should create more than 16385 tokens
        long_conversation.append(
            Message(
                date=datetime(2024, 1, 1, 10, 0),
                author="User",
                content=f"This is a very long message with lots of text to ensure we exceed "
                f"the token limit. Message number {i}",
            )
        )

    # Test with both languages
    for language in ["en", "pt"]:
        prompt = create_prompt(long_conversation, language, max_output_tokens=1000)
        assert isinstance(prompt, dict)
        assert "system_message" in prompt
        assert "user_message" in prompt
        assert count_tokens(prompt["user_message"]) <= 16385 - 1000  # Check if within token limit


def test_prompt_short_conversation(sample_conversation):
    # Test that short conversations are not truncated
    for language in ["en", "pt"]:
        prompt = create_prompt(sample_conversation, language, max_output_tokens=1000)
        assert isinstance(prompt, dict)
        assert "system_message" in prompt
        assert "user_message" in prompt
        # Verify all messages are included
        for message in sample_conversation:
            assert message.content in prompt["user_message"]
