#!/usr/bin/env python3
import os
import shutil
import subprocess
import musicbrainzngs
from mutagen.mp4 import MP4, MP4FreeForm

# MusicBrainzの設定
musicbrainzngs.set_useragent("YouTubeNavidrome", "1.0", "youremail@example.com")

# 音楽フォルダ
MUSIC_DIR = "/music"
TARGET_LUFS = -14.0   # 基準ラウドネス値（dB）
FFMPEG_CMD = "ffmpeg"  # ffmpegコマンド

def search_artist(title, artist_hint=None):
    try:
        if artist_hint:
            result = musicbrainzngs.search_recordings(recording=title, artist=artist_hint, limit=1)
        else:
            result = musicbrainzngs.search_recordings(recording=title, limit=1)
        recording = result['recording-list'][0]
        artist_name = recording['artist-credit'][0]['artist']['name']
        album_name = recording['release-list'][0]['title']
        return artist_name, album_name
    except Exception:
        return artist_hint or "Unknown Artist", "Single"

def normalize_audio(input_path, output_path):
    """動画付きM4Aも対応して音声だけ正規化"""
    cmd = [
        FFMPEG_CMD,
        "-i", input_path,
        "-vn",  # 動画ストリームを無視
        "-af", f"loudnorm=I={TARGET_LUFS}:LRA=7:TP=-2",
        "-c:a", "aac",
        "-b:a", "256k",
        "-y",
        output_path
    ]
    subprocess.run(cmd, check=True)

for root, dirs, files in os.walk(MUSIC_DIR):
    for file in files:
        if not file.endswith(".m4a"):
            continue

        path = os.path.join(root, file)
        try:
            audio = MP4(path)
        except Exception as e:
            print(f"[INFO] Skipping {file}: {e}")
            continue

        # すでに正規化済みか確認
        if "----:com.apple.iTunes:replaygain_track_gain" in audio.tags:
            print(f"[INFO] Skipping {file}: already normalized")
            continue

        title_tag = audio.tags.get("\xa9nam", ["Unknown Title"])[0]
        artist_hint = audio.tags.get("\xa9ART", ["Unknown Artist"])[0]

        artist_name, album_name = search_artist(title_tag, artist_hint)

        # タグ更新
        audio["\xa9ART"] = artist_name
        audio["\xa9alb"] = album_name
        audio["\xa9nam"] = title_tag
        audio.save()

        # 音量正規化して再エンコード（動画ストリーム無視）
        temp_path = path + ".tmp.m4a"
        try:
            normalize_audio(path, temp_path)
            shutil.move(temp_path, path)

            # 正規化済みタグを追加
            audio = MP4(path)
            audio["----:com.apple.iTunes:replaygain_track_gain"] = [MP4FreeForm(b"-14.00 dB")]
            audio.save()

        except subprocess.CalledProcessError as e:
            print(f"[INFO] Normalization failed for {file}: {e}")

        # 新しいパスを作成
        artist_dir = os.path.join(MUSIC_DIR, artist_name)
        album_dir = os.path.join(artist_dir, album_name)
        os.makedirs(album_dir, exist_ok=True)
        new_path = os.path.join(album_dir, file)

        # ファイルを移動
        if path != new_path:
            shutil.move(path, new_path)
            print(f"[INFO] Moved {file} to {new_path}")
        else:
            print(f"[INFO] Updated tags and normalized audio for {file} in place")
