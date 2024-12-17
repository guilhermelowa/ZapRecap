from fastapi import APIRouter
from pydantic import BaseModel
from app.services.text_analyzer import analyze_text

class FileRequest(BaseModel):
    content: str

router = APIRouter()

@router.post("/analyze")
async def analyze(file: FileRequest):
    print("File received:", file)
    return {"status": "processing"}