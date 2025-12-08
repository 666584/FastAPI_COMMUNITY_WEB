from typing import Optional
from fastapi import HTTPException, status
import requests
import re
import os
from google import genai

try:
    from bs4 import BeautifulSoup  # optional
except Exception:
    BeautifulSoup = None

SYSTEM_PROMPT = (
    "당신은 한국어로 간결하고 정확하게 뉴스를 요약하는 요약 전문가입니다. "
    "제목, URL, 기사 본문, 사용자 의견 등이 주어지면 핵심 내용을 세 문장 내외로 요약하되, "
    "중요한 숫자/사실/결과는 명확하게 포함하세요. 불확실한 정보는 추정하지 말고 "
    "요약문은 한국어로 작성하세요."
)

DEFAULT_IMAGE_URL = "https://images.unsplash.com/photo-1569025698421-8822a1a07603"


def fetch_article_text(url: str, max_chars: int = 20000) -> Optional[str]:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsSummaryBot/1.0)"}
        resp = requests.get(url, timeout=8, headers=headers)
        resp.raise_for_status()
        html = resp.text

        if BeautifulSoup:
            soup = BeautifulSoup(html, "html.parser")
            article = soup.find("article")
            if article:
                parts = [
                    t.get_text(separator=" ", strip=True)
                    for t in article.find_all(["p", "h1", "h2", "h3"])
                ]
            else:
                parts = [
                    p.get_text(separator=" ", strip=True)
                    for p in soup.find_all("p")
                ]
            joined = "\n\n".join([p for p in parts if p])
        else:
            joined = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.S | re.I)
            joined = re.sub(r"<style.*?>.*?</style>", "", joined, flags=re.S | re.I)
            joined = re.sub(r"<[^>]+>", " ", joined)
            joined = re.sub(r"\s+", " ", joined).strip()

        if not joined:
            return None

        return joined[:max_chars]
    except Exception:
        return None


def extract_article_image(url: str) -> Optional[str]:
    if not BeautifulSoup:
        return None

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsSummaryBot/1.0)"}
        resp = requests.get(url, timeout=8, headers=headers)
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]

        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            return tw["content"]

        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

        return None
    except Exception:
        return None


def pick_related_image(title: str, opinion: Optional[str] = None) -> str:
    """
    URL에서 이미지를 못 가져온 경우,
    제목 + opinion을 합쳐서 주제 추정 후 관련 이미지 URL 리턴
    """
    base = (title or "") + " " + (opinion or "")
    text = base.lower()

    if any(k in text for k in ["금리", "기준금리", "채권"]):
        return "https://source.unsplash.com/featured/?interest,rate,finance"
    if any(k in text for k in ["환율", "달러", "달러-원", "외환"]):
        return "https://source.unsplash.com/featured/?forex,currency,usd,krw"
    if any(k in text for k in ["주식", "코스피", "코스닥", "etf"]):
        return "https://source.unsplash.com/featured/?stock,chart,market"
    if any(k in text for k in ["부동산", "아파트", "주택", "전세"]):
        return "https://source.unsplash.com/featured/?realestate,building,city"
    if any(k in text for k in ["비트코인", "암호화폐", "코인", "crypto"]):
        return "https://source.unsplash.com/featured/?bitcoin,crypto,blockchain"
    if any(k in text for k in ["경제", "물가", "경기", "성장률", "인플레이션"]):
        return "https://source.unsplash.com/featured/?economy,macro,finance"
    if any(k in text for k in ["ai", "인공지능", "테크", "기술"]):
        return "https://source.unsplash.com/featured/?technology,ai,data"

    return DEFAULT_IMAGE_URL


def summarize_news(
    title: str,
    url: Optional[str] = None,
    opinion: Optional[str] = None,
):
    """
    1) url 있으면:
       - 기사 본문 텍스트, 메타 이미지 최대한 활용
    2) url 없거나, 기사 본문/이미지 추출 실패 시:
       - 항상 title + opinion 기반으로 요약 + 관련 이미지 선택
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    max_items = 3

    article_text: Optional[str] = None
    article_image: Optional[str] = None

    # 1) URL 기반 정보 시도
    if url:
        article_text = fetch_article_text(url)
        article_image = extract_article_image(url)

    # 2) LLM 컨텍스트 구성 (항상 title + opinion 우선)
    context_parts = [f"제목: {title}"]

    if url and article_text:
        # URL 있고 본문도 있으면: 기사 본문 + (참고용 opinion)
        context_parts.append(f"URL: {url}")
        context_parts.append(f"기사 본문 일부:\n{article_text[:4000]}")
        if opinion:
            context_parts.append(f"사용자 의견(참고용):\n{opinion}")
    else:
        # URL이 없거나 / 본문이 없으면: title + opinion만으로 요약
        if url and not article_text:
            context_parts.append(f"URL: {url} (본문 추출 실패)")
        if opinion:
            context_parts.append(f"사용자 의견:\n{opinion}")
        # opinion이 없어도 일부 사이트는 있을 수 있지만,
        # 그래도 최소한 제목은 항상 포함되어 있음 (기본)

    context_block = "\n\n".join(context_parts)

    full_prompt = f"""{SYSTEM_PROMPT}

{context_block}

다음 형식으로 정확히 {max_items}개의 항목을 생성하세요.
각 항목은 한 줄로 작성하고, 번호는 '1.' ~ '{max_items}.' 형태로 표기하세요.
전체 요약은 한국어로, 각 항목은 최대 800자 이내로 작성하세요.

예시:
1. 요약문1
2. 요약문2
3. 요약문3
"""

    # 3) Gemini 호출
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"gemini_request_failed: {str(e)}",
        )

    # 4) 텍스트 추출
    text = None
    if hasattr(resp, "text") and resp.text:
        text = resp.text
    if not text and getattr(resp, "candidates", None):
        cand = resp.candidates[0]
        content = getattr(cand, "content", None)
        if content and getattr(content, "parts", None):
            for p in content.parts:
                if hasattr(p, "text") and p.text:
                    text = p.text
                    break

    if not text:
        raise HTTPException(status_code=500, detail="failed_to_extract_gemini_output")

    raw = text.strip()

    # 5) 정확히 max_items 줄로 맞추기
    lines = [l.strip() for l in re.split(r"\n+", raw) if l.strip()]

    if len(lines) < max_items:
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[\.\?\!]|다\.)\s+", raw)
            if s.strip()
        ]
        if len(sentences) >= max_items:
            lines = sentences[:max_items]
        else:
            n = len(raw)
            if n == 0:
                lines = [""] * max_items
            else:
                parts = []
                for i in range(max_items):
                    start = i * n // max_items
                    end = (i + 1) * n // max_items
                    parts.append(raw[start:end].strip())
                lines = parts
                while len(lines) < max_items:
                    lines.append("")

    normalized: list[str] = []
    for ln in lines[:max_items]:
        ln = re.sub(r"^\s*\d+[\.\)]\s*", "", ln)
        normalized.append(ln.replace("\n", " ").strip())

    # 6) 최종 이미지 URL 결정
    if article_image:
        final_image_url = article_image
    else:
        # URL이 없거나, 기사 이미지 못 찾으면: 제목 + opinion으로 관련 이미지 추론
        final_image_url = pick_related_image(title, opinion)

    return {
        "title": title,
        "url": url,
        "summary": normalized,        # 요약 3개 리스트
        "image_url": final_image_url, # 기사 or 관련 이미지
    }
