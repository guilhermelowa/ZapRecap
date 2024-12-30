from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List

class ConversationStats(BaseModel):
    average_length: float
    longest_conversation_length: int
    longest_conversation_start: datetime
    longest_conversation_end: datetime

class WordMetrics(BaseModel):
    messages_per_author: Dict[str, int]
    average_message_length: Dict[str, float]
    curse_words_per_author: Dict[str, int]
    curse_words_by_author: Dict[str, Dict[str, int]]
    curse_words_frequency: Dict[str, int]

class CommonWord(BaseModel):
    word: str
    count: int

class AnalysisResponse(BaseModel):
    conversation_stats: ConversationStats
    word_metrics: WordMetrics
    common_words: List[CommonWord]