import { useState, useEffect, useCallback } from "react";
import { VideoUpload } from "./components/VideoUpload";
import { ProcessingStatus } from "./components/ProcessingStatus";
import { SubtitleViewer } from "./components/SubtitleViewer";
import { FrameAnalysisViewer } from "./components/FrameAnalysisViewer";

type Phase = "upload" | "processing" | "results";
type Tab = "subtitles" | "frames";

interface JobStatus {
  status: string;
  progress: number;
  step: string;
  filename?: string;
}

interface Segment {
  index: number;
  start: number;
  end: number;
  text: string;
  speaker: string;
}

interface FrameAnalysis {
  timestamp: number;
  timestamp_str: string;
  description: string;
}

interface Results {
  segments: Segment[];
  frame_analyses: FrameAnalysis[];
  speaker_count: number;
  srt_path: string;
  report_path: string;
}

export default function App() {
  const [phase, setPhase] = useState<Phase>("upload");
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [results, setResults] = useState<Results | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("subtitles");

  const pollStatus = useCallback(async (id: string) => {
    try {
      const res = await fetch(`/api/status/${id}`);
      if (!res.ok) return;
      const data: JobStatus = await res.json();
      setJobStatus(data);

      if (data.status === "completed") {
        const resR = await fetch(`/api/results/${id}`);
        if (resR.ok) {
          const r: Results = await resR.json();
          setResults(r);
          setPhase("results");
        }
      } else if (data.status === "error") {
        // Stay on processing phase to show error
      } else {
        // Continue polling
        setTimeout(() => pollStatus(id), 2000);
      }
    } catch {
      setTimeout(() => pollStatus(id), 3000);
    }
  }, []);

  const handleJobStart = useCallback(
    (id: string) => {
      setJobId(id);
      setPhase("processing");
      setJobStatus({ status: "queued", progress: 0, step: "処理を開始します..." });
      pollStatus(id);
    },
    [pollStatus]
  );

  const handleReset = () => {
    setPhase("upload");
    setJobId(null);
    setJobStatus(null);
    setResults(null);
    setActiveTab("subtitles");
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎬</span>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
                SubMagic
              </h1>
              <p className="text-xs text-slate-500">動画字幕生成＆画面分析</p>
            </div>
          </div>
          {phase !== "upload" && (
            <button
              onClick={handleReset}
              className="text-sm text-slate-400 hover:text-slate-200 transition-colors px-3 py-1.5 rounded-lg hover:bg-slate-800"
            >
              ← 新しい動画
            </button>
          )}
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 px-6 py-10">
        <div className="max-w-5xl mx-auto">
          {/* Upload */}
          {phase === "upload" && (
            <div>
              <div className="text-center mb-10">
                <h2 className="text-3xl font-bold text-slate-100 mb-3">
                  動画をアップロード
                </h2>
                <p className="text-slate-400 max-w-lg mx-auto">
                  動画をアップロードすると、Whisperで文字起こし・話者識別・画面分析を自動で行います
                </p>
              </div>
              <VideoUpload onJobStart={handleJobStart} />
            </div>
          )}

          {/* Processing */}
          {phase === "processing" && jobStatus && (
            <div>
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-slate-100 mb-2">処理中</h2>
                <p className="text-slate-400 text-sm">
                  {jobStatus.filename && <>「{jobStatus.filename}」を処理しています</>}
                </p>
              </div>
              <ProcessingStatus
                status={jobStatus.status}
                progress={jobStatus.progress}
                step={jobStatus.step}
              />
            </div>
          )}

          {/* Results */}
          {phase === "results" && results && jobId && (
            <div>
              {/* Summary bar */}
              <div className="flex flex-wrap gap-4 mb-8">
                <div className="flex-1 min-w-[140px] bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-violet-400">{results.segments.length}</div>
                  <div className="text-xs text-slate-500 mt-1">字幕セグメント</div>
                </div>
                <div className="flex-1 min-w-[140px] bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-pink-400">{results.speaker_count}</div>
                  <div className="text-xs text-slate-500 mt-1">検出した話者数</div>
                </div>
                <div className="flex-1 min-w-[140px] bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-emerald-400">{results.frame_analyses.length}</div>
                  <div className="text-xs text-slate-500 mt-1">分析フレーム数</div>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex gap-1 p-1 bg-slate-900 rounded-xl mb-6 border border-slate-800">
                {(
                  [
                    { id: "subtitles" as Tab, label: "🎙️ 字幕・トランスクリプト" },
                    { id: "frames" as Tab, label: "🖼️ 画面分析" },
                  ] as const
                ).map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all
                      ${activeTab === tab.id
                        ? "bg-violet-600 text-white shadow"
                        : "text-slate-400 hover:text-slate-200"}`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                {activeTab === "subtitles" && (
                  <SubtitleViewer segments={results.segments} jobId={jobId} />
                )}
                {activeTab === "frames" && (
                  <FrameAnalysisViewer analyses={results.frame_analyses} jobId={jobId} />
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-4 text-center text-xs text-slate-600">
        SubMagic — Whisper (local) + pyannote.audio + Claude AI
      </footer>
    </div>
  );
}
