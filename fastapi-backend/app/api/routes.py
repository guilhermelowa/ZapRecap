from fastapi import APIRouter
from pydantic import BaseModel
from app.services.text_analyzer import calculate_all_metrics
from app.services.chatgpt_utils import simulate_author_message
from app.models.data_formats import Message
from typing import List
import logging

logger = logging.getLogger(__name__)

class FileRequest(BaseModel):
    content: str

class SimulationRequest(BaseModel):
    conversation: List[Message]
    author: str
    prompt: str
    language: str = 'pt'

router = APIRouter()

@router.post("/analyze")
async def analyze(file: FileRequest):
    logger.info("Analyze endpoint hit")
    logger.info(f"Received content length: {len(file.content)}")
    try:
        logger.info("Analyze endpoint hit")
        logger.info(f"File length received: {len(file.content)}")
        result = calculate_all_metrics(file.content)
        logger.info("Analysis completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        print(f"Error during analysis: {str(e)}")
        raise

@router.post("/simulate-message")
async def simulate_message(request: SimulationRequest):
    logger.info("Simulate message endpoint hit")
    return {
        "message": simulate_author_message(
            request.conversation,
            request.author,
            request.prompt,
            request.language
        )
    }