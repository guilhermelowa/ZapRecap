from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional

class Message(BaseModel):
    date: datetime
    author: str
    content: str

class PeriodStats(BaseModel):
    period: int # weekday, week number or month number
    count: int

class ConversationStats(BaseModel):
    total_messages: int
    participant_count: int
    average_length: float
    longest_conversation_length: int
    longest_conversation_start: datetime
    longest_conversation_end: datetime
    most_active_weekday: PeriodStats
    least_active_weekday: PeriodStats
    most_active_week: PeriodStats
    least_active_week: PeriodStats
    most_active_month: PeriodStats
    least_active_month: PeriodStats

class ConversationThemesResponse(BaseModel):
    themes: Dict[str, str]

class SimulatedMessageResponse(BaseModel):
    simulated_message: str

class HeatmapData(BaseModel):
    z: List[List[float]]          # message counts
    x: List[str]                  # week labels
    y: List[str]                  # day labels
    dates: List[List[str]]        # formatted dates
    zmin: float
    zmax: float

class WordMetrics(BaseModel):
    messages_per_author: Dict[str, int]
    average_message_length: Dict[str, float]
    curse_words_per_author: Dict[str, int]
    curse_words_by_author: Dict[str, Dict[str, int]]
    curse_words_frequency: Dict[str, int]

class AnalysisResponse(BaseModel):
    conversation_stats: ConversationStats
    word_metrics: WordMetrics
    heatmap_data: HeatmapData
    common_words: Dict[str, int]
    author_messages: Dict[str, List[Message]]
    conversation_id: Optional[str] = None

class ConversationThemesRequest(BaseModel):
    conversation_id: str
    model: str

class SimulationRequest(BaseModel):
    conversation: List[Message]
    author: str
    model: str