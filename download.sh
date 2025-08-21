#!/bin/bash

MUSIC_DIR="/home/ubuntu/music"
DATA_DIR="$(pwd)"
COOKIE_FILE="$DATA_DIR/cookies.txt"
IMAGE_NAME="youtube-to-music"
DOWNLOAD_ARCHIVE="$DATA_DIR/downloaded.txt"

SAVE_DIR="$MUSIC_DIR"
FORMAT_OPTIONS="-x --audio-format m4a --audio-quality 0"

mkdir -p "$SAVE_DIR"

echo "[INFO] Building Docker image..."
docker build -t $IMAGE_NAME .

echo "[INFO] Starting download..."
docker run --rm \
    -v "$SAVE_DIR":/music \
    -v "$DATA_DIR":/data \
    -v "$COOKIE_FILE":/cookies.txt \
    -v "$DOWNLOAD_ARCHIVE":/downloaded.txt \
    $IMAGE_NAME yt-dlp \
    $FORMAT_OPTIONS \
    --add-metadata \
    --embed-thumbnail \
    --cookies /cookies.txt \
    --download-archive /downloaded.txt \
    --restrict-filenames \
    --no-playlist \
    -a /data/urls.txt

echo "[INFO] Download complete! Saved to: $SAVE_DIR"
