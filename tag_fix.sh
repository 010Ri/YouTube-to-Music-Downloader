#!/bin/bash

MUSIC_DIR="/home/ubuntu/music"
IMAGE_NAME="youtube-to-music"

docker run --rm \
    -v "$MUSIC_DIR":/music \
    -v "$(pwd)/tag_fix.py":/tag_fix.py \
    $IMAGE_NAME python /tag_fix.py
