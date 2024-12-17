from typing import List

def analyze_text(file_path: str) -> dict:
    """Analyze the text file and return statistics."""
    with open(file_path, 'r') as file:
        text = file.read()
    
    word_count = len(text.split())
    line_count = len(text.splitlines())
    char_count = len(text)

    return {
        'word_count': word_count,
        'line_count': line_count,
        'char_count': char_count
    }

def get_most_frequent_words(text: str, top_n: int = 10) -> List[str]:
    """Return the most frequent words in the given text."""
    from collections import Counter
    words = text.split()
    word_counts = Counter(words)
    most_common = word_counts.most_common(top_n)
    
    return [word for word, count in most_common]