interface Props {
  status: string;
  progress: number;
  step: string;
}

const STEPS = [
  { label: "音声抽出", threshold: 5 },
  { label: "文字起こし", threshold: 20 },
  { label: "話者分析", threshold: 50 },
  { label: "フレーム抽出", threshold: 65 },
  { label: "画面分析", threshold: 75 },
  { label: "出力生成", threshold: 90 },
  { label: "完了", threshold: 100 },
];

export function ProcessingStatus({ status, progress, step }: Props) {
  const isError = status === "error";

  return (
    <div className="max-w-xl mx-auto">
      <div className={`rounded-2xl p-8 border ${isError ? "border-red-500/30 bg-red-500/10" : "border-slate-700 bg-slate-900"}`}>
        <div className="flex items-center gap-3 mb-6">
          {isError ? (
            <span className="text-3xl">❌</span>
          ) : status === "completed" ? (
            <span className="text-3xl">✅</span>
          ) : (
            <div className="w-8 h-8 border-4 border-violet-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
          )}
          <div>
            <div className={`font-semibold text-lg ${isError ? "text-red-300" : "text-slate-100"}`}>
              {isError ? "エラーが発生しました" : status === "completed" ? "処理完了！" : "処理中..."}
            </div>
            <div className={`text-sm ${isError ? "text-red-400" : "text-slate-400"}`}>{step}</div>
          </div>
        </div>

        {!isError && (
          <>
            <div className="relative w-full bg-slate-800 rounded-full h-3 overflow-hidden mb-2">
              <div
                className="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-violet-600 to-indigo-500 transition-all duration-700"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="text-right text-sm text-slate-500 mb-6">{progress}%</div>

            <div className="flex justify-between">
              {STEPS.map((s, i) => {
                const done = progress >= s.threshold;
                const active = progress >= (STEPS[i - 1]?.threshold ?? 0) && progress < s.threshold;
                return (
                  <div key={s.label} className="flex flex-col items-center gap-1">
                    <div
                      className={`w-3 h-3 rounded-full transition-all duration-500
                        ${done ? "bg-violet-500" : active ? "bg-violet-500 animate-pulse" : "bg-slate-700"}`}
                    />
                    <span className={`text-[10px] leading-tight text-center max-w-[50px]
                      ${done ? "text-violet-400" : "text-slate-600"}`}>
                      {s.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
