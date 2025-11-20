# main.py

from fastapi import APIRouter
from pydantic import BaseModel
from ollama import chat
import base64

router = APIRouter(prefix="/ai")


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    thinking: str
    content: str


@router.post("/chat", response_model=ChatResponse)
def chat_with_ollama(req: ChatRequest):
    in_thinking = False
    thinking = ""
    content = ""

    stream = chat(
        model="qwen3-vl:8b",
        messages=[{"role": "user", "content": req.prompt}],
        stream=True,
    )

    for chunk in stream:
        if getattr(chunk.message, "thinking", None):
            if not in_thinking:
                in_thinking = True
            thinking += chunk.message.thinking

        elif getattr(chunk.message, "content", None):
            if in_thinking:
                in_thinking = False
            content += chunk.message.content

    return ChatResponse(thinking=thinking, content=content)