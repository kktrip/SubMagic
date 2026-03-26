import base64
import os
import anthropic


def analyze_frames(frames: list[dict]) -> list[dict]:
    """
    Analyze video frames using Claude vision API.
    Returns list of {timestamp, description} dicts.
    """
    if not frames:
        return []

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. "
            "Frame analysis requires an Anthropic API key."
        )

    client = anthropic.Anthropic(api_key=api_key)
    analyses = []

    for frame in frames:
        frame_path = frame["path"]
        timestamp = frame["timestamp"]

        with open(frame_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=600,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "この動画のフレームを分析してください。\n"
                                "以下を簡潔に日本語で説明してください：\n"
                                "1. 画面に何が表示されているか\n"
                                "2. どのような操作や作業が行われているか\n"
                                "3. 重要なUI要素やコンテンツ\n\n"
                                "200字以内でまとめてください。"
                            ),
                        },
                    ],
                }
            ],
        )

        analyses.append({
            "timestamp": timestamp,
            "timestamp_str": _format_timestamp(timestamp),
            "description": response.content[0].text.strip(),
        })

    return analyses


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
