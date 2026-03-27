import base64
import os


PROMPT = (
    "この動画のフレームを分析してください。\n"
    "以下を簡潔に日本語で説明してください：\n"
    "1. 画面に何が表示されているか\n"
    "2. どのような操作や作業が行われているか\n"
    "3. 重要なUI要素やコンテンツ\n\n"
    "200字以内でまとめてください。"
)


def analyze_frames(frames: list[dict]) -> list[dict]:
    """
    Analyze video frames using a vision AI.
    Provider is selected by VISION_PROVIDER env var:
      - gemini  (default, free) — Google Gemini API
      - claude  (paid)          — Anthropic Claude API
      - ollama  (free, local)   — Ollama + LLaVA
    """
    if not frames:
        return []

    provider = os.getenv("VISION_PROVIDER", "gemini").lower()

    if provider == "claude":
        return _analyze_with_claude(frames)
    elif provider == "ollama":
        return _analyze_with_ollama(frames)
    else:
        return _analyze_with_gemini(frames)


# ── Gemini（無料） ────────────────────────────────────────────────────────────

def _analyze_with_gemini(frames: list[dict]) -> list[dict]:
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError("google-generativeai をインストールしてください: pip install google-generativeai")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY が設定されていません。\n"
            "取得方法: https://aistudio.google.com/app/apikey"
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    analyses = []
    for frame in frames:
        with open(frame["path"], "rb") as f:
            image_bytes = f.read()

        response = model.generate_content([
            {"mime_type": "image/jpeg", "data": image_bytes},
            PROMPT,
        ])

        analyses.append({
            "timestamp": frame["timestamp"],
            "timestamp_str": _fmt(frame["timestamp"]),
            "description": response.text.strip(),
        })

    return analyses


# ── Ollama（完全無料・ローカル） ──────────────────────────────────────────────

def _analyze_with_ollama(frames: list[dict]) -> list[dict]:
    import urllib.request
    import json

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llava")
    url = f"{base_url}/api/generate"

    analyses = []
    for frame in frames:
        with open(frame["path"], "rb") as f:
            image_b64 = base64.standard_b64encode(f.read()).decode()

        payload = json.dumps({
            "model": model,
            "prompt": PROMPT,
            "images": [image_b64],
            "stream": False,
        }).encode()

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as res:
            data = json.loads(res.read())

        analyses.append({
            "timestamp": frame["timestamp"],
            "timestamp_str": _fmt(frame["timestamp"]),
            "description": data.get("response", "").strip(),
        })

    return analyses


# ── Claude（有料） ────────────────────────────────────────────────────────────

def _analyze_with_claude(frames: list[dict]) -> list[dict]:
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic をインストールしてください: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY が設定されていません。")

    client = anthropic.Anthropic(api_key=api_key)
    analyses = []

    for frame in frames:
        with open(frame["path"], "rb") as f:
            image_b64 = base64.standard_b64encode(f.read()).decode()

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                    {"type": "text", "text": PROMPT},
                ],
            }],
        )

        analyses.append({
            "timestamp": frame["timestamp"],
            "timestamp_str": _fmt(frame["timestamp"]),
            "description": response.content[0].text.strip(),
        })

    return analyses


# ── Util ─────────────────────────────────────────────────────────────────────

def _fmt(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
