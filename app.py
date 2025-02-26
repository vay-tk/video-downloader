import streamlit as st
import subprocess
import os
from pathlib import Path

# Directory to store downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(url, resolution="best", audio_only=False):
    """Download video/audio using yt-dlp with authentication."""
    
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    # Set format based on resolution & audio-only option
    if audio_only:
        format_option = "bestaudio/best"
    else:
        format_option = f"bestvideo[height<={resolution}]+bestaudio/best"

    # YT-DLP command with authentication (cookies.txt)
    command = [
        "yt-dlp",
        "-f", format_option,
        "-o", output_template,
        "--cookies", "cookies.txt",  # Use cookies for authentication
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--referer", "https://www.youtube.com/",
        "--geo-bypass",
        url
    ]

    # Run command
    result = subprocess.run(command, capture_output=True, text=True)

    # Error handling
    if result.returncode != 0:
        st.error(f"❌ Download failed: {result.stderr}")
        return None
    
    # Get the downloaded filename
    output_filename = result.stdout.strip().split("\n")[-1]
    return output_filename

def convert_format(input_path, output_format):
    """Convert video to another format using FFmpeg."""
    output_path = str(Path(input_path).with_suffix(f".{output_format}"))
    ffmpeg_cmd = ["ffmpeg", "-i", input_path, "-c:v", "libx265", "-c:a", "copy", output_path]
    subprocess.run(ffmpeg_cmd)
    return output_path

def extract_audio(input_path, output_format="mp3"):
    """Extract audio from video using FFmpeg."""
    output_path = str(Path(input_path).with_suffix(f".{output_format}"))
    ffmpeg_cmd = ["ffmpeg", "-i", input_path, "-vn", "-acodec", "libmp3lame", output_path]
    subprocess.run(ffmpeg_cmd)
    return output_path

# Streamlit UI
st.title("🎥 YouTube Video Downloader")

urls = st.text_area("📌 Enter YouTube URLs (one per line)")
resolution = st.selectbox("🎯 Select Resolution", ["360p", "480p", "720p", "1080p", "1440p", "2160p"])  # Default resolutions
format_option = st.selectbox("🎵 Select Format", ["mp4", "mkv", "avi", "mov", "mp3", "aac"])
audio_only = st.checkbox("🎧 Audio Only")

if st.button("🚀 Download & Convert"):
    urls = urls.split("\n")
    for url in urls:
        url = url.strip()
        if url:
            st.write(f"📥 Downloading: {url}")
            file_path = download_video(url, resolution if resolution != "Auto" else "best", audio_only)
            if file_path:
                if format_option in ["mp3", "aac"]:
                    file_path = extract_audio(file_path, format_option)
                elif format_option != "mp4":
                    file_path = convert_format(file_path, format_option)
                st.success(f"✅ Download Complete: [Click Here](/{file_path})")
