# 🎬 AI Video & Meeting Assistant (RAG)

An end-to-end intelligent assistant that transforms long YouTube videos and recorded meetings into an interactive knowledge base. Instead of watching hours of video, users can instantly read the full transcript and chat directly with the video content using Retrieval-Augmented Generation (RAG).

---

## 🎯 What This Project Does

1. **Ingests Video/Audio**: Takes a YouTube link or local file and extracts clean audio.
2. **Automates Transcription**: Transcribes speech into text (English via Whisper, Hinglish via Sarvam AI).
3. **Indexes Content for Search**: Splits transcript into semantic chunks and builds vector embeddings.
4. **Enables Grounded Q&A**: Lets users query the meeting context with answers grounded strictly in the transcript, preventing hallucinations.

---

## 🔄 RAG Pipeline Architecture Flow

```
[YouTube URL / Audio File]
         │
         ▼ (yt-dlp + FFmpeg)
   [Audio Stream] ──► Split into 10-min audio chunks
         │
         ▼ (OpenAI Whisper / Sarvam AI)
   [Full Transcript]
         │
         ▼ (Recursive Character Splitter: 500 chars / 50 overlap)
   [Text Chunks]
         │
         ▼ (HuggingFace all-MiniLM-L6-v2 Embeddings)
   [ChromaDB Vector Store]
         │
 ┌───────┴────────────────────────┐
 │          User Question         │
 └───────┬────────────────────────┘
         ▼
   [Similarity Search: Top-4 Chunks]
         │
         ▼ (Prompt + Retrieved Context)
   [Groq LLM: openai/gpt-oss-120b]
         │
         ▼
   [Instant Grounded Answer]
```

---

## ✨ Features

- 🔊 **Automated Audio Ingestion**: Downloads and formats audio from YouTube URLs or local files.
- 📝 **Dual-Engine Speech-to-Text**: Local Whisper (English) and Sarvam AI (Hinglish/Hindi).
- 🧠 **Vector Search & Storage**: Embeds and stores chunks in persistent ChromaDB.
- ⚡ **High-Speed RAG Chat**: Sub-second answers powered by Groq LPU inference.
- 🎨 **Cyberpunk Web UI**: Built with Streamlit featuring dark mode, status bars, and collapsible transcripts.

---

## 🛠️ Tech Stack

- **UI**: Streamlit
- **Transcription**: OpenAI Whisper, Sarvam AI
- **Embeddings & Vector Store**: `sentence-transformers` (`all-MiniLM-L6-v2`), ChromaDB
- **LLM & Pipeline**: LangChain LCEL, Groq API (`openai/gpt-oss-120b`)
- **Audio Processing**: FFmpeg, PyDub, yt-dlp

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
# Ensure FFmpeg is installed on your machine
pip install -r requirements.txt
```

### 2. Configure `.env`
```env
GROQ_API_KEY=your_groq_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here   # optional, for Hinglish
```

### 3. Launch App
```bash
streamlit run app.py
```

---

## 🌐 Deployment

Ready for one-click deployment on **Streamlit Community Cloud**:
- Preconfigured `packages.txt` automatically installs `ffmpeg` on cloud startup.
- Set API keys in your Streamlit Cloud dashboard under **Secrets**.
