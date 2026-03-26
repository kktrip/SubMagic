import { useCallback, useState, useRef } from "react";

interface Props {
  onJobStart: (jobId: string) => void;
}

export function VideoUpload({ onJobStart }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const uploadFile = useCallback(
    async (file: File) => {
      if (!file.type.startsWith("video/")) {
        setError("動画ファイルを選択してください（MP4, MOV, AVI など）");
        return;
      }
      setError(null);
      setUploading(true);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "アップロードに失敗しました");
        }
        const { job_id } = await res.json();
        onJobStart(job_id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "アップロードエラー");
      } finally {
        setUploading(false);
      }
    },
    [onJobStart]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) uploadFile(file);
    },
    [uploadFile]
  );

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) uploadFile(file);
    },
    [uploadFile]
  );

  return (
    <div className="max-w-2xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200
          ${dragging ? "border-violet-400 bg-violet-500/10 scale-[1.02]" : "border-slate-600 hover:border-violet-500 hover:bg-violet-500/5"}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={onInputChange}
        />

        <div className="text-6xl mb-4">🎬</div>

        {uploading ? (
          <>
            <div className="text-xl font-semibold text-violet-300 mb-2">アップロード中...</div>
            <div className="flex justify-center">
              <div className="w-8 h-8 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
            </div>
          </>
        ) : (
          <>
            <div className="text-xl font-semibold text-slate-200 mb-2">
              動画をドラッグ＆ドロップ
            </div>
            <div className="text-slate-400 text-sm mb-4">または クリックしてファイルを選択</div>
            <div className="text-slate-500 text-xs">
              MP4, MOV, AVI, MKV, WebM などに対応
            </div>
          </>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-500/15 border border-red-500/30 rounded-xl text-red-300 text-sm">
          {error}
        </div>
      )}

      <div className="mt-8 grid grid-cols-3 gap-4 text-center text-sm">
        {[
          { icon: "🎙️", title: "Whisper 文字起こし", desc: "無料・ローカル実行" },
          { icon: "👥", title: "話者識別", desc: "Speaker A, B, C…" },
          { icon: "🖼️", title: "画面分析", desc: "Claude AIが解説" },
        ].map((f) => (
          <div key={f.title} className="p-4 bg-slate-900 rounded-xl border border-slate-800">
            <div className="text-2xl mb-2">{f.icon}</div>
            <div className="font-medium text-slate-200">{f.title}</div>
            <div className="text-slate-500 text-xs mt-1">{f.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
