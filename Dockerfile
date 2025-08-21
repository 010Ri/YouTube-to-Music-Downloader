FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir yt-dlp mutagen musicbrainzngs && \
    apt-get clean

WORKDIR /music
