import { useState } from "react";

interface Segment {
  index: number;
  start: number;
  end: number;
  text: string;
  speaker: string;
}

interface Props {
  segments: Segment[];
  jobId: string;
}

const SPEAKER_COLORS: Record<string, string> = {
  "Speaker A": "bg-blue-500/15 border-blue-500/30 text-blue-300",
  "Speaker B": "bg-pink-500/15 border-pink-500/30 text-pink-300",
  "Speaker C": "bg-emerald-500/15 border-emerald-500/30 text-emerald-300",
  "Speaker D": "bg-amber-500/15 border-amber-500/30 text-amber-300",
  "Speaker E": "bg-purple-500/15 border-purple-500/30 text-purple-300",
  "Speaker F": "bg-cyan-500/15 border-cyan-500/30 text-cyan-300",
};

const COLOR_FALLBACK = "bg-slate-500/15 border-slate-500/30 text-slate-300";

function formatTime(sec: number): string {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function SubtitleViewer({ segments, jobId }: Props) {
  const [search, setSearch] = useState("");
  const [filterSpeaker, setFilterSpeaker] = useState<string>("all");

  const speakers = Array.from(new Set(segments.map((s) => s.speaker))).sort();

  const filtered = segments.filter((seg) => {
    const matchText = seg.text.toLowerCase().includes(search.toLowerCase());
    const matchSpeaker = filterSpeaker === "all" || seg.speaker === filterSpeaker;
    return matchText && matchSpeaker;
  });

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="テキストを検索..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500"
          />
        </div>
        <select
          value={filterSpeaker}
          onChange={(e) => setFilterSpeaker(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
        >
          <option value="all">全話者</option>
          {speakers.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <a
          href={`/api/download/subtitles/${jobId}`}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg text-sm font-medium transition-colors"
        >
          <span>⬇️</span> SRT ダウンロード
        </a>
      </div>

      {/* Speaker legend */}
      <div className="flex flex-wrap gap-2 mb-4">
        {speakers.map((sp) => (
          <button
            key={sp}
            onClick={() => setFilterSpeaker(filterSpeaker === sp ? "all" : sp)}
            className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all
              ${filterSpeaker === sp || filterSpeaker === "all"
                ? (SPEAKER_COLORS[sp] ?? COLOR_FALLBACK)
                : "bg-slate-800 border-slate-700 text-slate-500"}`}
          >
            {sp}
          </button>
        ))}
      </div>

      <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
        {filtered.length === 0 ? (
          <div className="text-center text-slate-500 py-8">該当する字幕がありません</div>
        ) : (
          filtered.map((seg) => (
            <div
              key={seg.index}
              className={`flex gap-3 p-3 rounded-xl border transition-all hover:brightness-110 ${SPEAKER_COLORS[seg.speaker] ?? COLOR_FALLBACK}`}
            >
              <div className="flex-shrink-0 text-xs font-mono opacity-60 pt-0.5 w-16 text-right">
                {formatTime(seg.start)}
              </div>
              <div className="flex-shrink-0 text-xs font-bold pt-0.5 w-24">
                {seg.speaker}
              </div>
              <div className="flex-1 text-sm leading-relaxed text-slate-100">
                {seg.text}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="mt-4 text-slate-500 text-xs">
        {filtered.length} / {segments.length} セグメント表示中
      </div>
    </div>
  );
}
