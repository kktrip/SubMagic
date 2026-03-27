# SubMagic 🎬

動画をアップロードするだけで以下を自動生成するWebアプリ：

- **字幕（SRT）** — OpenAI Whisper（無料・ローカル実行）で文字起こし
- **話者識別** — pyannote.audio で Speaker A, B, C… を自動分類
- **画面分析レポート** — AI が各フレームの画面内容を日本語で解説

---

## セットアップ

### 必要なもの

| ツール | 用途 |
|--------|------|
| Python 3.10+ | バックエンド |
| Node.js 18+ | フロントエンド |
| ffmpeg | 音声・フレーム抽出 |
| Google API キー（無料）| 画面分析（Gemini） |
| HuggingFace トークン（無料） | 話者識別（pyannote） |

### 1. ffmpeg をインストール

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows: https://ffmpeg.org/download.html
```

### 2. バックエンドのセットアップ

```bash
cd backend

# 仮想環境を作成
python3 -m venv .venv

# 仮想環境を有効化
source .venv/bin/activate       # Linux / macOS
# .venv\Scripts\activate        # Windows (PowerShell)

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .env を編集して APIキーを設定
```

#### 画面分析プロバイダーの選択（`.env`）

3種類から選べます：

| プロバイダー | 料金 | 設定 |
|------------|------|------|
| **Gemini**（デフォルト） | **無料**（1500回/日） | `VISION_PROVIDER=gemini` |
| **Ollama**（ローカル） | **完全無料** | `VISION_PROVIDER=ollama` |
| Claude | 有料 | `VISION_PROVIDER=claude` |

**Gemini API キーの取得（無料）:**
1. [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) にアクセス
2. 「Create API key」をクリック
3. 発行されたキーを `.env` の `GOOGLE_API_KEY` に設定

**Ollama（完全無料・ローカル）を使う場合:**
```bash
# Ollama をインストール: https://ollama.com/
ollama pull llava   # 画像認識モデルをダウンロード
# .env で VISION_PROVIDER=ollama に設定
```

#### HuggingFace の設定（話者識別・無料）

1. [huggingface.co](https://huggingface.co) でアカウント作成
2. [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) の利用規約に同意
3. [Settings > Tokens](https://huggingface.co/settings/tokens) でトークンを発行して `.env` に設定

> **注意:** HuggingFace トークンを設定しない場合は全セグメントが「Speaker A」になります（話者識別スキップ）。

### 3. フロントエンドのセットアップ

```bash
cd frontend
npm install
```

---

## 起動方法

### バックエンド（ポート 8000）

```bash
cd backend
source .venv/bin/activate
python main.py
```

### フロントエンド（ポート 3000）

```bash
cd frontend
npm run dev
```

ブラウザで `http://localhost:3000` を開く。

---

## 使い方

1. 動画ファイルをドラッグ＆ドロップ（または クリックして選択）
2. 処理が自動で進む（文字起こし → 話者識別 → 画面分析）
3. 完了後、以下を確認・ダウンロード：
   - **字幕タブ**: 話者ラベル付き字幕（SRTダウンロード可）
   - **画面分析タブ**: タイムライン形式の画面解説（HTMLレポートダウンロード可）

---

## 技術スタック

| 機能 | 技術 |
|------|------|
| 文字起こし | [openai/whisper](https://github.com/openai/whisper)（ローカル・無料） |
| 話者識別 | [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)（無料） |
| 画面分析 | Gemini 2.0 Flash（無料）/ Ollama LLaVA（完全無料）/ Claude（有料） |
| 音声/動画処理 | ffmpeg |
| バックエンド | FastAPI + Python |
| フロントエンド | React + TypeScript + Tailwind CSS |

---

## Whisper モデルサイズの目安

| モデル | サイズ | 速度 | 精度 |
|--------|--------|------|------|
| tiny | 39MB | 最速 | 低 |
| base | 74MB | 速い | 中 |
| small | 244MB | 普通 | 良好 |
| medium | 769MB | 遅い | 高 |
| large | 1.5GB | 最遅 | 最高 |

日本語の場合は `small` 以上を推奨。
