from fastapi import APIRouter
from pydantic import BaseModel
from app.services.text_analyzer import calculate_all_metrics

class FileRequest(BaseModel):
    content: str

router = APIRouter()

@router.post("/analyze")
async def analyze(file: FileRequest):
    print(f"File length received: {len(file.content)}")
    return calculate_all_metrics(file.content)