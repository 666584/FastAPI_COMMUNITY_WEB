from typing import Optional, Tuple, Dict
from fastapi import HTTPException, status
import requests
import re
import os
from google import genai

try:
    from bs4 import BeautifulSoup  # optional
except Exception:
    BeautifulSoup = None

from ollama import chat

SYSTEM_PROMPT = (
    "당신은 한국어로 간결하고 정확하게 뉴스를 요약하는 요약 전문가입니다. "
    "출처(URL)과 제목이 주어지면 핵심 내용을 세 문장 내외로 요약하되, "
    "중요한 숫자/사실/결과는 명확하게 포함하세요. 불확실한 정보는 추정하지 말고 "
    "요약문은 한국어로 작성하세요."
)


def fetch_article_text(url: str, max_chars: int = 20000) -> Optional[str]:
    """
    URL에서 기사 본문을 시도해 추출하여 문자열로 반환합니다.
    실패하면 None을 반환합니다.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsSummaryBot/1.0)"}
        resp = requests.get(url, timeout=8, headers=headers)
        resp.raise_for_status()
        html = resp.text

        if BeautifulSoup:
            soup = BeautifulSoup(html, "html.parser")
            article = soup.find("article")
            if article:
                parts = [t.get_text(separator=" ", strip=True) for t in article.find_all(["p", "h1", "h2", "h3"])]
            else:
                parts = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
            joined = "\n\n".join([p for p in parts if p])
        else:
            # 간단 fallback: 태그 제거
            joined = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.S | re.I)
            joined = re.sub(r"<style.*?>.*?</style>", "", joined, flags=re.S | re.I)
            joined = re.sub(r"<[^>]+>", " ", joined)
            joined = re.sub(r"\s+", " ", joined).strip()

        if not joined:
            return None

        return joined[:max_chars]
    except Exception:
        return None

def summarize_news(title: str,
                          url: str):

    # 환경변수에서 키 가져오기 (GEMINI_API_KEY 사용)
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    full_prompt = f"""{SYSTEM_PROMPT}

                    제목: {title}
                    URL: {url}

                    다음 형식으로 정확히 4개의 항목을 생성하세요.
                    각 항목은 한 줄로 작성하고, 번호는 '1.' ~ '4.' 형태로 표기하세요.
                    전체 요약은 한국어로, 각 항목은 최대 800자 이내로 작성하세요.

                    예시:
                    1. 요약문1
                    2. 요약문2
                    3. 요약문3
                    4. 요약문4
                    """
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": full_prompt}
                    ],
                }
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"gemini_request_failed: {str(e)}",
        )

    # ------------------------
    # 1) Gemini 응답에서 텍스트 추출
    # ------------------------
    text = None

    # 가장 단순: SDK가 resp.text 제공하는 경우
    if hasattr(resp, "text") and resp.text:
        text = resp.text

    # 후보(candidates) 구조에서 꺼내기 (멀티모달/복잡 응답 대비)
    if not text and getattr(resp, "candidates", None):
        first = resp.candidates[0]
        content = getattr(first, "content", None)
        if content and getattr(content, "parts", None):
            for part in content.parts:
                # 텍스트 파트 찾기
                if hasattr(part, "text") and part.text:
                    text = part.text
                    break

    if not text:
        raise HTTPException(
            status_code=500,
            detail="failed_to_extract_gemini_output",
        )

    content = text.strip()

    # ------------------------
    # 2) 최대 4줄로 포맷 강제 
    # ------------------------
    lines = [l.strip() for l in re.split(r"\n+", content) if l.strip()]

    if len(lines) < 4:
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[\.\?\!]|다\.)\s+", content)
            if s.strip()
        ]
        if len(sentences) >= 4:
            lines = sentences[:4]
        else:
            n = len(content)
            if n == 0:
                lines = [""] * 4
            else:
                parts = []
                for i in range(4):
                    start = i * n // 4
                    end = (i + 1) * n // 4
                    parts.append(content[start:end].strip())
                lines = [p for p in parts if p]
                while len(lines) < 4:
                    lines.append(lines[-1] if lines else "")

    normalized_lines = []
    for ln in lines[:4]:
        ln_stripped = re.sub(r"^\s*\d+[\.\)]\s*", "", ln)
        normalized_lines.append(ln_stripped.replace("\n", " ").strip())

    numbered = "\n".join(f"{i+1}. {normalized_lines[i]}" for i in range(4))

    return {
        "title": title,
        "url": url,
        "summary": numbered
    }