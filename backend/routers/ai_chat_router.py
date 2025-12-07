# main.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from ollama import chat
import base64
from typing import Optional
from controllers import ai_chat_controller as controller

router = APIRouter(prefix="/ai")


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    thinking: str
    content: str

class NewsSummaryRequest(BaseModel):
    title: str
    url: str
    fetch_full: Optional[bool] = False
    max_summary_chars: Optional[int] = 800
    model: Optional[str] = "qwen3-vl:4b"

class NewsSummaryResponse(BaseModel):
    title: str
    url: str
    summary: str

class NewsSummaryGeminiRequest(BaseModel):
    title: str
    url: str

@router.post("/summarize", response_model=NewsSummaryResponse, status_code=status.HTTP_200_OK)
def summarize_news(req: NewsSummaryGeminiRequest):
    try:
        result = controller.summarize_news(
            title=req.title,
            url=req.url
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return NewsSummaryResponse(
        title=result.get("title"),
        url=result.get("url"),
        summary=result.get("summary")
    )