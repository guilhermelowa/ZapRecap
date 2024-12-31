from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List


# class HeatmapPoint(BaseModel):
#     x: int  # week number (0-52)
#     y: int  # weekday (0-6)
#     v: float  # normalized value (0-100)
#     vmin: int
#     vmax: int

class HeatmapData(BaseModel):
    z: List[List[float]]          # message counts
    x: List[str]                  # week labels
    y: List[str]                  # day labels
    dates: List[List[str]]        # formatted dates
    zmin: float
    zmax: float

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
    heatmap_data: HeatmapData
    conversation_stats: ConversationStats
    word_metrics: WordMetrics
    common_words: List[CommonWord]