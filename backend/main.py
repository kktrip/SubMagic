import os
import uuid
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import aiofiles
from dotenv import load_dotenv

load_dotenv()

# In-memory job store (use Redis/DB for production)
jobs: dict[str, dict] = {}

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500")) * 1024 * 1024
FRAME_INTERVAL = int(os.getenv("FRAME_INTERVAL", "30"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    yield


app = FastAPI(title="SubMagic API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Upload ──────────────────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(400, "動画ファイルをアップロードしてください")

    job_id = str(uuid.uuid4())
    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    video_path = f"uploads/{job_id}{suffix}"

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"ファイルサイズが上限（{MAX_UPLOAD_BYTES // 1024 // 1024}MB）を超えています")

    async with aiofiles.open(video_path, "wb") as f:
        await f.write(content)

    jobs[job_id] = {
        "status": "queued",
        "progress": 0,
        "step": "アップロード完了",
        "filename": file.filename,
    }

    background_tasks.add_task(_process_video, job_id, video_path)

    return {"job_id": job_id}


# ─── Status ──────────────────────────────────────────────────────────────────

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "ジョブが見つかりません")
    return job


# ─── Results ─────────────────────────────────────────────────────────────────

@app.get("/api/results/{job_id}")
async def get_results(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "ジョブが見つかりません")
    if job["status"] != "completed":
        raise HTTPException(400, f"処理中です: {job['step']}")
    return job.get("results", {})


# ─── Downloads ───────────────────────────────────────────────────────────────

@app.get("/api/download/subtitles/{job_id}")
async def download_subtitles(job_id: str):
    job = _require_completed(job_id)
    path = job["results"]["srt_path"]
    return FileResponse(path, filename=f"subtitles_{job_id}.srt", media_type="text/plain")


@app.get("/api/download/report/{job_id}")
async def download_report(job_id: str):
    job = _require_completed(job_id)
    path = job["results"]["report_path"]
    return FileResponse(path, filename=f"report_{job_id}.html", media_type="text/html")


def _require_completed(job_id: str) -> dict:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "ジョブが見つかりません")
    if job["status"] != "completed":
        raise HTTPException(400, "処理が完了していません")
    return job


# ─── Background processing ───────────────────────────────────────────────────

async def _process_video(job_id: str, video_path: str):
    def update(status: str, progress: int, step: str):
        jobs[job_id].update({"status": status, "progress": progress, "step": step})

    try:
        update("processing", 5, "音声を抽出中...")
        from video_processor import extract_audio, extract_frames

        audio_path = await asyncio.to_thread(extract_audio, video_path)

        update("processing", 20, "Whisperで文字起こし中（ローカル処理）...")
        from transcriber import transcribe

        segments = await asyncio.to_thread(transcribe, audio_path)

        update("processing", 50, "話者を分析中...")
        from diarizer import diarize

        speaker_map = await asyncio.to_thread(diarize, audio_path, segments)

        update("processing", 65, "動画フレームを抽出中...")
        frames = await asyncio.to_thread(extract_frames, video_path, FRAME_INTERVAL)

        update("processing", 75, "画面をAIが分析中...")
        from frame_analyzer import analyze_frames

        frame_analyses = await asyncio.to_thread(analyze_frames, frames)

        update("processing", 90, "字幕・レポートを生成中...")
        from subtitle_generator import generate_srt, generate_report

        srt_path = generate_srt(segments, speaker_map, job_id)
        report_path = generate_report(segments, speaker_map, frame_analyses, job_id)

        # Build enriched segment list for frontend
        enriched_segments = [
            {
                "index": i,
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "speaker": speaker_map.get(i, "Speaker ?"),
            }
            for i, seg in enumerate(segments)
        ]

        jobs[job_id].update({
            "status": "completed",
            "progress": 100,
            "step": "完了",
            "results": {
                "segments": enriched_segments,
                "frame_analyses": frame_analyses,
                "srt_path": srt_path,
                "report_path": report_path,
                "speaker_count": len(set(speaker_map.values())),
            },
        })

        # Cleanup uploaded video
        try:
            os.remove(video_path)
        except OSError:
            pass

    except Exception as exc:
        jobs[job_id].update({
            "status": "error",
            "step": f"エラー: {exc}",
            "error": str(exc),
        })
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
