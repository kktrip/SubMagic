import os
import subprocess
from pathlib import Path


def extract_audio(video_path: str, output_dir: str = "outputs") -> str:
    """Extract audio from video as WAV (16kHz mono) for Whisper."""
    os.makedirs(output_dir, exist_ok=True)
    stem = Path(video_path).stem
    audio_path = os.path.join(output_dir, f"{stem}_audio.wav")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extraction failed:\n{result.stderr}")
    return audio_path


def extract_frames(video_path: str, interval_sec: int = 30, output_dir: str = "outputs") -> list[dict]:
    """
    Extract one frame every `interval_sec` seconds from the video.
    Returns list of {"path": ..., "timestamp": ...}.
    """
    os.makedirs(output_dir, exist_ok=True)
    stem = Path(video_path).stem
    frames_dir = os.path.join(output_dir, f"{stem}_frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Get video duration
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    if probe_result.returncode != 0:
        raise RuntimeError(f"ffprobe failed:\n{probe_result.stderr}")

    duration = float(probe_result.stdout.strip())

    frames = []
    timestamp = 0
    while timestamp < duration:
        frame_path = os.path.join(frames_dir, f"frame_{int(timestamp):06d}.jpg")
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(timestamp),
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "3",
            frame_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(frame_path):
            frames.append({"path": frame_path, "timestamp": timestamp})
        timestamp += interval_sec

    return frames


def get_video_duration(video_path: str) -> float:
    """Return video duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed:\n{result.stderr}")
    return float(result.stdout.strip())
