#!/usr/bin/env python3
"""Test YouTube download functionality"""

import yt_dlp
import sys

def test_youtube_download(url):
    """Test downloading from YouTube"""
    print(f"Testing YouTube download for: {url}")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info.get('title', 'N/A')}")
            print(f"Duration: {info.get('duration', 'N/A')} seconds")
            print(f"Uploader: {info.get('uploader', 'N/A')}")
            print("Download test successful!")
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_youtube_download(sys.argv[1])
    else:
        print("Usage: python test_youtube.py <youtube_url>")