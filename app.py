
import streamlit as st
import subprocess
import os
from pytube import YouTube
from pathlib import Path

# Directory to store downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(url, resolution=None, audio_only=False):
    """Download video or audio from YouTube."""
    yt = YouTube(url)
    if audio_only:
        stream = yt.streams.filter(only_audio=True).first()
    else:
        stream = yt.streams.filter(res=resolution, progressive=True, file_extension='mp4').first()
    
    if not stream:
        st.error("No stream found with the specified parameters.")
        return None
    
    return stream.download(output_path=DOWNLOAD_DIR)

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
