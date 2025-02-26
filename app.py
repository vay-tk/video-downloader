import os
import streamlit as st
import subprocess
from pytube import YouTube

# Set FFmpeg path (installed in Docker)
FFMPEG_PATH = "/usr/bin/ffmpeg"

def download_video(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
        filename = stream.download(output_path="downloads/")
        return filename
    except Exception as e:
        st.error(f"Error downloading video: {e}")
        return None

def convert_format(input_file, output_format):
    output_file = f"downloads/{os.path.basename(input_file).rsplit('.', 1)[0]}.{output_format}"
    ffmpeg_cmd = [FFMPEG_PATH, "-i", input_file, output_file]
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        st.error(f"Error converting file: {e}")
        return None

# Streamlit UI
st.title("🎥 YouTube Video Downloader with FFmpeg")
url = st.text_input("🔗 Enter YouTube Video URL:")

if st.button("⬇ Download"):
    if url:
        file_path = download_video(url)
        if file_path:
            st.success(f"Downloaded: {file_path}")
            st.session_state["file_path"] = file_path
        else:
            st.error("Failed to download the video.")
    else:
        st.error("Please enter a valid YouTube URL.")

# Format Conversion
if "file_path" in st.session_state:
    format_option = st.selectbox("🎼 Convert to:", ["mp4", "mp3"])
    
    if st.button("🎵 Convert"):
        converted_file = convert_format(st.session_state["file_path"], format_option)
        if converted_file:
            st.success(f"Converted: {converted_file}")
            with open(converted_file, "rb") as file:
                st.download_button(label="📥 Download Converted File", data=file, file_name=os.path.basename(converted_file))

