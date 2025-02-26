# Use official Python image
FROM python:3.10

# Install FFmpeg & yt-dlp
RUN apt-get update && apt-get install -y ffmpeg && pip install yt-dlp

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
