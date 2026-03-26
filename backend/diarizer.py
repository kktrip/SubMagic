import os
import warnings


def diarize(audio_path: str, segments: list[dict]) -> dict[int, str]:
    """
    Perform speaker diarization using pyannote.audio (free, open-source).
    Maps each segment index to a speaker label like 'Speaker A', 'Speaker B', etc.

    Requires HUGGINGFACE_TOKEN in environment and accepting terms at:
    https://huggingface.co/pyannote/speaker-diarization-3.1
    """
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        warnings.warn(
            "HUGGINGFACE_TOKEN not set. Skipping speaker diarization. "
            "All segments will be labeled as 'Speaker A'."
        )
        return {i: "Speaker A" for i in range(len(segments))}

    try:
        from pyannote.audio import Pipeline
        import torch

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token,
        )

        # Use GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        pipeline.to(device)

        diarization = pipeline(audio_path)

        # Build timeline: list of (start, end, speaker_label)
        turns = [
            (turn.start, turn.end, speaker)
            for turn, _, speaker in diarization.itertracks(yield_label=True)
        ]

        # Map internal pyannote speaker IDs to A, B, C, ...
        speaker_id_map: dict[str, str] = {}

        speaker_map: dict[int, str] = {}
        for i, seg in enumerate(segments):
            mid = (seg["start"] + seg["end"]) / 2
            best_speaker = _find_speaker(mid, turns)
            if best_speaker is None:
                # Fallback: find closest segment
                best_speaker = _find_closest_speaker(mid, turns)

            if best_speaker is not None:
                if best_speaker not in speaker_id_map:
                    idx = len(speaker_id_map)
                    # A, B, C, ... Z, AA, AB, ...
                    speaker_id_map[best_speaker] = _index_to_label(idx)
                speaker_map[i] = f"Speaker {speaker_id_map[best_speaker]}"
            else:
                speaker_map[i] = "Speaker ?"

        return speaker_map

    except Exception as e:
        warnings.warn(f"Speaker diarization failed: {e}. Falling back to single speaker.")
        return {i: "Speaker A" for i in range(len(segments))}


def _find_speaker(timestamp: float, turns: list) -> str | None:
    """Return speaker active at timestamp, or None."""
    for start, end, speaker in turns:
        if start <= timestamp <= end:
            return speaker
    return None


def _find_closest_speaker(timestamp: float, turns: list) -> str | None:
    """Return speaker of the closest turn to timestamp."""
    if not turns:
        return None
    return min(
        turns,
        key=lambda t: min(abs(timestamp - t[0]), abs(timestamp - t[1]))
    )[2]


def _index_to_label(idx: int) -> str:
    """Convert 0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA, ..."""
    result = ""
    idx += 1
    while idx > 0:
        idx -= 1
        result = chr(65 + idx % 26) + result
        idx //= 26
    return result
