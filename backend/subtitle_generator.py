import os


def _format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(
    segments: list[dict],
    speaker_map: dict[int, str],
    job_id: str,
    output_dir: str = "outputs",
) -> str:
    """Generate SRT subtitle file with speaker labels."""
    os.makedirs(output_dir, exist_ok=True)
    srt_path = os.path.join(output_dir, f"{job_id}_subtitles.srt")

    lines = []
    for i, seg in enumerate(segments):
        speaker = speaker_map.get(i, "Speaker ?")
        start_str = _format_srt_time(seg["start"])
        end_str = _format_srt_time(seg["end"])
        text = seg["text"]

        lines.append(str(i + 1))
        lines.append(f"{start_str} --> {end_str}")
        lines.append(f"[{speaker}] {text}")
        lines.append("")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return srt_path


def generate_report(
    segments: list[dict],
    speaker_map: dict[int, str],
    frame_analyses: list[dict],
    job_id: str,
    output_dir: str = "outputs",
) -> str:
    """Generate an HTML report combining transcript and frame analysis."""
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, f"{job_id}_report.html")

    # Build transcript section
    transcript_rows = []
    for i, seg in enumerate(segments):
        speaker = speaker_map.get(i, "Speaker ?")
        start = _format_srt_time(seg["start"]).replace(",", ".")
        end = _format_srt_time(seg["end"]).replace(",", ".")
        text = seg["text"]
        # Color by speaker
        speaker_class = f"speaker-{speaker.split()[-1].lower()}"
        transcript_rows.append(
            f'<tr class="{speaker_class}">'
            f'<td class="time">{start}</td>'
            f'<td class="time">{end}</td>'
            f'<td class="speaker">{speaker}</td>'
            f'<td class="text">{text}</td>'
            f'</tr>'
        )

    # Build frame analysis section
    frame_rows = []
    for fa in frame_analyses:
        frame_rows.append(
            f'<div class="frame-card">'
            f'<div class="frame-time">{fa["timestamp_str"]}</div>'
            f'<div class="frame-desc">{fa["description"]}</div>'
            f'</div>'
        )

    # Speaker legend
    unique_speakers = sorted(set(speaker_map.values()))
    legend_items = "".join(
        f'<span class="legend-item speaker-{s.split()[-1].lower()}">{s}</span>'
        for s in unique_speakers
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SubMagic Report - {job_id}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
    h1 {{ text-align: center; font-size: 2rem; margin-bottom: 0.5rem;
          background: linear-gradient(135deg, #6366f1, #8b5cf6); -webkit-background-clip: text;
          -webkit-text-fill-color: transparent; }}
    .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 2rem; }}
    h2 {{ font-size: 1.3rem; color: #a5b4fc; margin: 2rem 0 1rem; border-left: 4px solid #6366f1; padding-left: 0.75rem; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.5rem; }}
    .legend-item {{ padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 0.75rem; overflow: hidden; }}
    th {{ background: #334155; padding: 0.75rem 1rem; text-align: left; font-size: 0.8rem; text-transform: uppercase; color: #94a3b8; }}
    td {{ padding: 0.6rem 1rem; border-bottom: 1px solid #334155; font-size: 0.9rem; }}
    td.time {{ color: #94a3b8; font-family: monospace; white-space: nowrap; font-size: 0.8rem; }}
    td.speaker {{ font-weight: 700; white-space: nowrap; }}
    td.text {{ line-height: 1.6; }}
    tr:last-child td {{ border-bottom: none; }}
    /* Speaker colors */
    .speaker-a td.speaker {{ color: #60a5fa; }}
    .speaker-a {{ background: rgba(96,165,250,0.04); }}
    .speaker-a .legend-item, .legend-item.speaker-a {{ background: rgba(96,165,250,0.15); color: #60a5fa; }}
    .speaker-b td.speaker {{ color: #f472b6; }}
    .speaker-b {{ background: rgba(244,114,182,0.04); }}
    .speaker-b .legend-item, .legend-item.speaker-b {{ background: rgba(244,114,182,0.15); color: #f472b6; }}
    .speaker-c td.speaker {{ color: #34d399; }}
    .speaker-c {{ background: rgba(52,211,153,0.04); }}
    .speaker-c .legend-item, .legend-item.speaker-c {{ background: rgba(52,211,153,0.15); color: #34d399; }}
    .speaker-d td.speaker {{ color: #fbbf24; }}
    .speaker-d {{ background: rgba(251,191,36,0.04); }}
    .speaker-d .legend-item, .legend-item.speaker-d {{ background: rgba(251,191,36,0.15); color: #fbbf24; }}
    .speaker-e td.speaker {{ color: #a78bfa; }}
    .speaker-e {{ background: rgba(167,139,250,0.04); }}
    .speaker-e .legend-item, .legend-item.speaker-e {{ background: rgba(167,139,250,0.15); color: #a78bfa; }}
    .frame-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }}
    .frame-card {{ background: #1e293b; border-radius: 0.75rem; padding: 1.25rem; border: 1px solid #334155; }}
    .frame-time {{ font-family: monospace; color: #6366f1; font-weight: 700; margin-bottom: 0.5rem; font-size: 0.9rem; }}
    .frame-desc {{ color: #cbd5e1; line-height: 1.7; font-size: 0.9rem; }}
    .no-data {{ color: #64748b; font-style: italic; padding: 1rem; text-align: center; }}
  </style>
</head>
<body>
  <h1>SubMagic Report</h1>
  <p class="subtitle">Job ID: {job_id}</p>

  <h2>話者一覧</h2>
  <div class="legend">{legend_items}</div>

  <h2>字幕・トランスクリプト</h2>
  <table>
    <thead>
      <tr>
        <th>開始</th>
        <th>終了</th>
        <th>話者</th>
        <th>発言内容</th>
      </tr>
    </thead>
    <tbody>
      {"".join(transcript_rows) if transcript_rows else '<tr><td colspan="4" class="no-data">トランスクリプトがありません</td></tr>'}
    </tbody>
  </table>

  <h2>画面分析</h2>
  {"<div class='frame-grid'>" + "".join(frame_rows) + "</div>" if frame_rows else "<p class='no-data'>フレーム分析がありません</p>"}

</body>
</html>"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path
