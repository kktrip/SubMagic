import os
import whisper


def transcribe(audio_path: str) -> list[dict]:
    """
    Transcribe audio using local Whisper model (free, GitHub version).
    Returns list of segments: [{start, end, text}, ...]
    """
    model_name = os.getenv("WHISPER_MODEL", "base")
    model = whisper.load_model(model_name)

    result = model.transcribe(
        audio_path,
        task="transcribe",
        verbose=False,
        word_timestamps=True,
    )

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })

    return segments
