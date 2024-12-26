from fastapi import APIRouter
from pydantic import BaseModel
from app.services.text_analyzer import analyze_text, get_most_frequent_words

class FileRequest(BaseModel):
    content: str

router = APIRouter()

@router.post("/analyze")
async def analyze(file: FileRequest):
    print(f"File length received: {len(file.content)}")
    most_common_words = get_most_frequent_words(file.content)
    return {
        "status": "completed",
        "result": {
            "word_cloud_data": most_common_words
        }
    }