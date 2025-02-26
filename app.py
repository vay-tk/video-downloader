import streamlit as st
import subprocess
import os
from pathlib import Path

# Create download directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(url, resolution=None, audio_only=False):
    """Download video or audio from YouTube using yt-dlp."""
    output_template = f"{DOWNLOAD_DIR}/%(title)s.%(ext)s"
    resolution_filter = f"bestvideo[height<={resolution}]+bestaudio/best" if resolution else "best"

    if audio_only:
        command = ["yt-dlp", "-f", "bestaudio", "-o", output_template, url]
    else:
        command = ["yt-dlp", "-f", resolution_filter, "-o", output_template, url]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        st.write(result.stdout)  # Display yt-dlp output in Streamlit
        downloaded_files = list(Path(DOWNLOAD_DIR).glob("*.*"))  # Get downloaded files
        return str(downloaded_files[-1]) if downloaded_files else None  # Return latest file
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Download failed: {e}")
        st.error(f"🔍 yt-dlp Error Output:\n{e.stderr}")
        return None

def convert_format(input_path, output_format):
    """Convert downloaded file to specified format using FFmpeg."""
    output_path = str(Path(input_path).with_suffix(f".{output_format}"))
    ffmpeg_cmd = ["ffmpeg", "-i", input_path, "-c:v", "libx265", "-c:a", "copy", output_path]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Conversion failed: {e}")
        return None

def extract_audio(input_path, output_format="mp3"):
    """Extract audio from a video file using FFmpeg."""
    output_path = str(Path(input_path).with_suffix(f".{output_format}"))
    ffmpeg_cmd = ["ffmpeg", "-i", input_path, "-vn", "-acodec", "libmp3lame", output_path]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Audio extraction failed: {e}")
        return None

# Streamlit UI
st.title("📥 YouTube Video Downloader")

urls = st.text_area("Enter YouTube URLs (one per line)")
resolution = st.selectbox("Select Resolution", ["Auto", "360p", "480p", "720p", "1080p"])
format_option = st.selectbox("Select Format", ["mp4", "mkv", "avi", "mov", "mp3", "aac"])
audio_only = st.checkbox("Audio Only")

if st.button("Download & Convert"):
    urls = urls.split("\n")
    for url in urls:
        url = url.strip()
        if url:
            st.write(f"🔄 Processing: {url}")
            file_path = download_video(url, resolution if resolution != "Auto" else None, audio_only)
            if file_path:
                if format_option in ["mp3", "aac"]:
                    file_path = extract_audio(file_path, format_option)
                elif format_option != "mp4":
                    file_path = convert_format(file_path, format_option)
                
                if file_path:
                    file_name = Path(file_path).name
                    st.success(f"✅ Download Complete: [Click Here to Download](/{file_path})")
                else:
                    st.error("❌ Failed to process the file.")
