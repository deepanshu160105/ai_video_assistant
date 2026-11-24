import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

def get_cookies_path() -> str | None:
    """Check if cookies are provided in environment or local cookies.txt file."""
    if os.path.exists("cookies.txt") and os.path.getsize("cookies.txt") > 0:
        return "cookies.txt"
    cookie_content = os.getenv("YOUTUBE_COOKIES")
    if cookie_content:
        path = os.path.join(DOWNLOAD_DIR, "yt_cookies.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(cookie_content)
        return path
    return None

def download_youtube_audio(url :str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")
    cookiefile = get_cookies_path()
    
    # Try different player clients if one fails with 403
    client_configs = [
        ["mweb"],
        ["android"],
        ["ios"],
        ["tv"],
    ]
    
    last_err = None
    for clients in client_configs:
        try:
            ydl_opts = {
                "format": "ba/b",
                "outtmpl": output_path,
                "extractor_args": {
                    "youtube": {
                        "player_client": clients,
                        "player_skip": ["webpage", "configs"],
                    }
                },
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
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
            }
            if cookiefile:
                ydl_opts["cookiefile"] = cookiefile
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # Ensure .wav extension after postprocessing
                wav_file = os.path.splitext(filename)[0] + ".wav"
                if os.path.exists(wav_file):
                    return wav_file
                return filename
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(
        f"YouTube blocked the cloud server request ({last_err}). "
        "YouTube enforces strict IP blocks on cloud hosting providers like AWS/Streamlit. "
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


