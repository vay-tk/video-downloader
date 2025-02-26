
import streamlit as st
import subprocess
import os
import yt_dlp
from pathlib import Path

# Directory to store downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(url, resolution=None, audio_only=False):
    ydl_opts = {
        'format': 'bestaudio' if audio_only else f'bestvideo[height={resolution}]+bestaudio/best' if resolution else 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"downloads/{info['title']}.mp4" if not audio_only else f"downloads/{info['title']}.m4a"


def convert_format(input_path, output_format):
    """Convert downloaded file to specified format using FFmpeg."""
    output_path = str(Path(input_path).with_suffix(f".{output_format}"))
    ffmpeg_cmd = ["ffmpeg", "-i", input_path, "-c:v", "libx265", "-c:a", "copy", output_path]
    subprocess.run(ffmpeg_cmd)
    return output_path

def extract_audio(input_path, output_format="mp3"):
    """Extract audio from a video file."""
    output_path = str(Path(input_path).with_suffix(f".{output_format}"))
    ffmpeg_cmd = ["ffmpeg", "-i", input_path, "-vn", "-acodec", "libmp3lame", output_path]
    subprocess.run(ffmpeg_cmd)
    return output_path

# Streamlit UI
st.title("YouTube Video Downloader")

urls = st.text_area("Enter YouTube URLs (one per line)")
resolution = st.selectbox("Select Resolution", ["Auto", "360p", "480p", "720p", "1080p"])
format_option = st.selectbox("Select Format", ["mp4", "mkv", "avi", "mov", "mp3", "aac"])
audio_only = st.checkbox("Audio Only")

if st.button("Download & Convert"):
    urls = urls.split("\n")
    for url in urls:
        url = url.strip()
        if url:
            st.write(f"Processing: {url}")
            file_path = download_video(url, resolution if resolution != "Auto" else None, audio_only)
            if file_path:
                if format_option in ["mp3", "aac"]:
                    file_path = extract_audio(file_path, format_option)
                elif format_option != "mp4":
                    file_path = convert_format(file_path, format_option)
                st.success(f"Download Complete: [Click Here](/{file_path})")
