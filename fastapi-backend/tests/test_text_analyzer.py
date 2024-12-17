import pytest
from app.services.text_analyzer import analyze_text

def test_analyze_text():
    text = "Hello, world!"
    result = analyze_text(text)
    assert result['word_count'] == 2
    assert result['character_count'] == 13

def test_analyze_empty_text():
    text = ""
    result = analyze_text(text)
    assert result['word_count'] == 0
    assert result['character_count'] == 0