import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

def get_cookies_path() -> str | None:
    """Check if cookies are provided in Streamlit secrets, environment, or local cookies.txt."""
    if os.path.exists("cookies.txt") and os.path.getsize("cookies.txt") > 0:
        return "cookies.txt"

    cookie_content = None
    try:
        import streamlit as st
        cookie_content = st.secrets.get("YOUTUBE_COOKIES")
    except Exception:
        pass

    if not cookie_content:
        cookie_content = os.getenv("YOUTUBE_COOKIES")

    if cookie_content:
        path = os.path.join(DOWNLOAD_DIR, "yt_cookies.txt")
        lines = ["# Netscape HTTP Cookie File"]
        for line in str(cookie_content).strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 7:
                # Format: domain, flag, path, secure, expiration, name, value (tab-delimited)
                lines.append("\t".join(parts[:6] + [" ".join(parts[6:])]))
            else:
                lines.append(line)

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Loaded YouTube cookies into {path}")
        return path
    return None

def download_youtube_audio(url :str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")
    cookiefile = get_cookies_path()
    
    base_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
    }
    if cookiefile:
        base_opts["cookiefile"] = cookiefile

    # First attempt: standard download (with cookies if available)
    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            wav_file = os.path.splitext(filename)[0] + ".wav"
            if os.path.exists(wav_file):
                return wav_file
            return filename
    except Exception as e:
        last_err = e

    # Fallback attempts: try client rotation
    for client in ["ios", "android", "mweb"]:
        try:
            opts = dict(base_opts)
            opts["extractor_args"] = {"youtube": {"player_client": [client]}}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                wav_file = os.path.splitext(filename)[0] + ".wav"
                if os.path.exists(wav_file):
                    return wav_file
                return filename
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(
        f"YouTube blocked the cloud server request ({last_err}). "
        "Please use the 'Upload audio/video file' option in the sidebar to analyze your file directly!"
    )



def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path



def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks


