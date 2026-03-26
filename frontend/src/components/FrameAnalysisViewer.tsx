interface FrameAnalysis {
  timestamp: number;
  timestamp_str: string;
  description: string;
}

interface Props {
  analyses: FrameAnalysis[];
  jobId: string;
}

export function FrameAnalysisViewer({ analyses, jobId }: Props) {
  if (analyses.length === 0) {
    return (
      <div className="text-center text-slate-500 py-8">
        フレーム分析データがありません
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <p className="text-slate-400 text-sm">
          動画から {analyses.length} フレームを抽出し、AIが画面内容を解説しました。
        </p>
        <a
          href={`/api/download/report/${jobId}`}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium transition-colors"
        >
          <span>📄</span> レポートをダウンロード
        </a>
      </div>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-[72px] top-0 bottom-0 w-px bg-slate-700" />

        <div className="space-y-6">
          {analyses.map((fa, i) => (
            <div key={i} className="flex gap-4 items-start relative">
              {/* Timestamp + dot */}
              <div className="flex-shrink-0 w-16 text-right">
                <span className="text-xs font-mono text-violet-400 bg-slate-900 px-1">
                  {fa.timestamp_str}
                </span>
              </div>
              <div className="flex-shrink-0 relative z-10 mt-1">
                <div className="w-3 h-3 rounded-full bg-violet-500 ring-4 ring-slate-950" />
              </div>

              {/* Card */}
              <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition-colors">
                <p className="text-slate-200 text-sm leading-relaxed">{fa.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
