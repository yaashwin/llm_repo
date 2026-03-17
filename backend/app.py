# from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# import whisper
# import torch
# import os
# import tempfile
# import shutil
# from pathlib import Path
# import yt_dlp
# import requests
# from bs4 import BeautifulSoup
# import moviepy.editor as mp
# from datetime import datetime
# import asyncio
# from typing import Optional, Dict, Any
# import uuid
# import time
# from urllib.parse import urlparse
# from meeting_summarizer import MeetingSummarizer
# import json
# from config import Config
# import re
# model_name = 'phi'  # Default model name
# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize Whisper model
# print("Loading Whisper model...")
# device = "cuda" if torch.cuda.is_available() else "cpu"
# whisper_model = whisper.load_model("base", device=device)

# # Create directories
# UPLOAD_DIR = Path("uploads")
# OUTPUT_DIR = Path("outputs")
# UPLOAD_DIR.mkdir(exist_ok=True)
# OUTPUT_DIR.mkdir(exist_ok=True)

# # Initialize the meeting summarizer (add after other initializations)
# meeting_summarizer = MeetingSummarizer(llm_provider="gemini")  # Default to Gemini

# # Initialize LLM as None first
# llm = None
# llm_available = False

# class TranscriptionService:
#     @staticmethod
#     async def transcribe_audio(file_path: str, source_type: str) -> dict:
#         """Transcribe audio file using Whisper"""
#         try:
#             result = whisper_model.transcribe(
#                 file_path,
#                 language="en",
#                 task="transcribe",
#                 verbose=False
#             )
            
#             # Format output with timestamps
#             formatted_text = f"Source Type: {source_type}\n"
#             formatted_text += f"Transcription Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
#             formatted_text += "="*50 + "\n\n"
            
#             # Add segments with timestamps
#             for segment in result["segments"]:
#                 start_time = f"{int(segment['start']//60):02d}:{int(segment['start']%60):02d}"
#                 end_time = f"{int(segment['end']//60):02d}:{int(segment['end']%60):02d}"
#                 formatted_text += f"[{start_time} - {end_time}] {segment['text'].strip()}\n\n"
            
#             return {
#                 "text": result["text"],
#                 "formatted_text": formatted_text,
#                 "segments": result["segments"]
#             }
#         except Exception as e:
#             raise Exception(f"Transcription failed: {str(e)}")
    
#     @staticmethod
#     async def extract_audio_from_video(video_path: str) -> str:
#         """Extract audio from video file"""
#         try:
#             audio_path = video_path.replace(Path(video_path).suffix, ".wav")
#             video = mp.VideoFileClip(video_path)
#             video.audio.write_audiofile(audio_path, verbose=False, logger=None)
#             video.close()
#             return audio_path
#         except Exception as e:
#             raise Exception(f"Audio extraction failed: {str(e)}")
    
#     @staticmethod
#     async def download_youtube_audio(url: str) -> str:
#         """Download audio from YouTube with updated options"""
#         try:
#             output_filename = f"youtube_{uuid.uuid4().hex}"
#             output_path = str(UPLOAD_DIR / f"{output_filename}.wav")
            
#             # Simplified yt-dlp options that work better with current YouTube
#             ydl_opts = {
#                 'format': 'bestaudio/best',
#                 'outtmpl': str(UPLOAD_DIR / output_filename),
#                 'quiet': True,
#                 'no_warnings': True,
#                 'extract_flat': False,
#                 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#                 'age_limit': None,
#                 'geo_bypass': True,
#                 'postprocessors': [{
#                     'key': 'FFmpegExtractAudio',
#                     'preferredcodec': 'wav',
#                 }],
#             }
            
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 ydl.download([url])
            
#             # Check if file was created
#             if os.path.exists(output_path):
#                 return output_path
                
#             # Check for file without extension
#             base_path = str(UPLOAD_DIR / output_filename)
#             if os.path.exists(base_path + '.wav'):
#                 return base_path + '.wav'
                
#             raise Exception("Downloaded file not found")
            
#         except Exception as e:
#             error_msg = str(e).replace('[0;31mERROR:[0m', 'ERROR:')
#             raise Exception(f"YouTube download failed: {error_msg}")

# async def download_youtube_alternative(url: str) -> str:
#     """Alternative YouTube download method using pytubefix"""
#     try:
#         from pytubefix import YouTube
#         from pytubefix.cli import on_progress
        
#         # Clean the URL
#         url = url.strip()
        
#         # Create a unique filename
#         output_filename = f"youtube_{uuid.uuid4().hex}.wav"
#         output_path = str(UPLOAD_DIR / output_filename)
#         temp_filename = f"temp_{uuid.uuid4().hex}"
        
#         print(f"Attempting to download from YouTube using pytubefix: {url}")
        
#         # Create YouTube object
#         yt = YouTube(url, on_progress_callback=on_progress)
        
#         print(f"Video Title: {yt.title}")
#         print(f"Video Length: {yt.length} seconds")
        
#         # Get the audio stream - try different options
#         audio_stream = None
        
#         # Try to get audio-only stream
#         audio_streams = yt.streams.filter(only_audio=True)
#         if audio_streams:
#             # Prefer m4a format
#             audio_stream = audio_streams.filter(file_extension='m4a').first()
#             if not audio_stream:
#                 # Try mp4
#                 audio_stream = audio_streams.filter(file_extension='mp4').first()
#             if not audio_stream:
#                 # Get any audio stream
#                 audio_stream = audio_streams.first()
        
#         if not audio_stream:
#             # If no audio-only stream, get lowest quality video stream (smaller file)
#             print("No audio-only stream found, trying video stream...")
#             audio_stream = yt.streams.get_lowest_resolution()
        
#         if not audio_stream:
#             raise Exception("No suitable stream available for this video")
        
#         print(f"Selected stream: {audio_stream}")
        
#         # Download the stream
#         print("Downloading...")
#         downloaded_file = audio_stream.download(
#             output_path=str(UPLOAD_DIR),
#             filename=temp_filename
#         )
        
#         print(f"Downloaded to: {downloaded_file}")
        
#         # Convert to WAV using moviepy
#         print("Converting to WAV format...")
#         try:
#             if audio_stream.includes_video_track:
#                 # Extract audio from video
#                 video = mp.VideoFileClip(downloaded_file)
#                 video.audio.write_audiofile(output_path, verbose=False, logger=None)
#                 video.close()
#             else:
#                 # Convert audio format
#                 audio = mp.AudioFileClip(downloaded_file)
#                 audio.write_audiofile(output_path, verbose=False, logger=None)
#                 audio.close()
#         except Exception as e:
#             print(f"MoviePy conversion failed: {e}, trying alternative method...")
#             # Alternative conversion using ffmpeg directly
#             import subprocess
#             subprocess.run([
#                 'ffmpeg', '-i', downloaded_file, '-acodec', 'pcm_s16le', 
#                 '-ar', '16000', '-ac', '1', output_path, '-y'
#             ], check=True, capture_output=True)
        
#         # Remove the temporary file
#         if os.path.exists(downloaded_file):
#             os.remove(downloaded_file)
        
#         print(f"Successfully converted to: {output_path}")
#         return output_path
        
#     except ImportError:
#         raise Exception("pytubefix is not installed. Please run: pip install pytubefix")
#     except Exception as e:
#         raise Exception(f"Alternative YouTube download failed: {str(e)}")

# @app.post("/transcribe/audio")
# async def transcribe_audio_file(file: UploadFile = File(...)):
#     """Handle audio file upload and transcription"""
#     temp_file = None
#     try:
#         # Validate file type
#         allowed_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']
#         file_ext = Path(file.filename).suffix.lower()
#         if file_ext not in allowed_extensions:
#             raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")
        
#         # Save uploaded file
#         temp_file = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
#         with open(temp_file, "wb") as f:
#             content = await file.read()
#             f.write(content)
        
#         # Transcribe
#         result = await TranscriptionService.transcribe_audio(str(temp_file), "Audio File")
        
#         # Save output
#         output_filename = f"{Path(file.filename).stem}_transcript.txt"
#         output_path = OUTPUT_DIR / output_filename
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(result["formatted_text"])
        
#         return JSONResponse({
#             "status": "success",
#             "filename": output_filename,
#             "text": result["text"],
#             "formatted_text": result["formatted_text"]
#         })
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         if temp_file and temp_file.exists():
#             os.remove(temp_file)

# @app.post("/transcribe/video")
# async def transcribe_video_file(file: UploadFile = File(...)):
#     """Handle video file upload and transcription"""
#     temp_video = None
#     temp_audio = None
#     try:
#         # Validate file type
#         allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
#         file_ext = Path(file.filename).suffix.lower()
#         if file_ext not in allowed_extensions:
#             raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")
        
#         # Save uploaded file
#         temp_video = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
#         with open(temp_video, "wb") as f:
#             content = await file.read()
#             f.write(content)
        
#         # Extract audio
#         temp_audio = await TranscriptionService.extract_audio_from_video(str(temp_video))
        
#         # Transcribe
#         result = await TranscriptionService.transcribe_audio(temp_audio, "Video File")
        
#         # Save output
#         output_filename = f"{Path(file.filename).stem}_transcript.txt"
#         output_path = OUTPUT_DIR / output_filename
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(result["formatted_text"])
        
#         return JSONResponse({
#             "status": "success",
#             "filename": output_filename,
#             "text": result["text"],
#             "formatted_text": result["formatted_text"]
#         })
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         if temp_video and temp_video.exists():
#             os.remove(temp_video)
#         if temp_audio and Path(temp_audio).exists():
#             os.remove(temp_audio)

# @app.post("/transcribe/youtube")
# async def transcribe_youtube(data: dict):
#     """Handle YouTube URL transcription with pytubefix as primary method"""
#     temp_audio = None
#     try:
#         url = data.get("url")
#         if not url:
#             raise HTTPException(status_code=400, detail="URL is required")
        
#         # Clean and validate URL
#         url = url.strip()
#         if not ('youtube.com' in url or 'youtu.be' in url):
#             raise HTTPException(status_code=400, detail="Please provide a valid YouTube URL")
        
#         print(f"Processing YouTube URL: {url}")
        
#         # Try pytubefix first (since it's working well)
#         try:
#             print("Attempting download with pytubefix...")
#             temp_audio = await download_youtube_alternative(url)
#             print("Download successful")
#         except Exception as e:
#             print(f"Pytubefix failed: {e}")
            
#             # Try yt-dlp as fallback
#             try:
#                 print("Attempting download with yt-dlp...")
#                 temp_audio = await TranscriptionService.download_youtube_audio(url)
#                 print("yt-dlp successful")
#             except Exception as e2:
#                 print(f"yt-dlp also failed: {e2}")
#                 raise Exception(f"Could not download YouTube video. Please try a different video or check if the video is available in your region.")
        
#         if not temp_audio or not os.path.exists(temp_audio):
#             raise Exception("Download completed but audio file not found")
        
#         # Check file size
#         file_size_mb = os.path.getsize(temp_audio) / (1024 * 1024)
#         print(f"Audio file size: {file_size_mb:.2f} MB")
        
#         # Warn if file is very large
#         if file_size_mb > 500:
#             print(f"Warning: Large audio file ({file_size_mb:.2f} MB). Transcription may take a while...")
        
#         # Transcribe
#         print("Starting transcription...")
#         result = await TranscriptionService.transcribe_audio(temp_audio, "YouTube Video")
        
#         # Save output
#         output_filename = f"youtube_{uuid.uuid4().hex}_transcript.txt"
#         output_path = OUTPUT_DIR / output_filename
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(result["formatted_text"])
        
#         return JSONResponse({
#             "status": "success",
#             "filename": output_filename,
#             "text": result["text"],
#             "formatted_text": result["formatted_text"]
#         })
    
#     except Exception as e:
#         error_msg = str(e)
#         print(f"YouTube transcription error: {error_msg}")
#         raise HTTPException(status_code=500, detail=error_msg)
#     finally:
#         if temp_audio and Path(temp_audio).exists():
#             try:
#                 os.remove(temp_audio)
#                 print("Cleaned up temporary audio file")
#             except:
#                 pass

# def extract_structured_content(soup):
#     """Extract structured content with headers and their associated text"""
#     structured_content = []
    
#     # Find all headers
#     headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
#     for header in headers:
#         header_level = int(header.name[1])
#         header_text = header.get_text(strip=True)
        
#         if not header_text:
#             continue
#                 # Get content after this header until the next header
#         content_parts = []
#         current = header.next_sibling
        
#         while current:
#             if current.name and current.name.startswith('h'):
#                 # Stop if we hit another header of same or higher level
#                 next_level = int(current.name[1])
#                 if next_level <= header_level:
#                     break
            
#             if hasattr(current, 'get_text'):
#                 text = current.get_text(strip=True)
#                 if text:
#                     # Check for code blocks
#                     if current.name == 'pre' or (current.name == 'code' and current.parent.name != 'pre'):
#                         content_parts.append(f"```\n{text}\n```")
#                     # Check for lists
#                     elif current.name in ['ul', 'ol']:
#                         list_items = current.find_all('li')
#                         for li in list_items:
#                             content_parts.append(f"• {li.get_text(strip=True)}")
#                     # Regular paragraphs
#                     elif current.name == 'p':
#                         content_parts.append(text)
#                     # Other text content
#                     elif text and current.name not in ['script', 'style']:
#                         content_parts.append(text)
            
#             current = current.next_sibling
        
#         structured_content.append({
#             'level': header_level,
#             'title': header_text,
#             'content': '\n'.join(content_parts)
#         })
    
#     return structured_content

# def format_structured_content(structured_content):
#     """Format structured content for display"""
#     formatted = []
    
#     for section in structured_content:
#         indent = "  " * (section['level'] - 1)
#         formatted.append(f"{indent}{'#' * section['level']} {section['title']}")
#         if section['content']:
#             # Indent content properly
#             content_lines = section['content'].split('\n')
#             for line in content_lines[:5]:  # Limit to first 5 lines per section
#                 if line.strip():
#                     formatted.append(f"{indent}  {line}")
    
#     return '\n'.join(formatted)

# def create_fallback_summary(structured_content, full_text):
#     """Create a summary without LLM"""
#     summary = "## Document Structure and Content\n\n"
    
#     # Add table of contents
#     summary += "### Table of Contents\n"
#     for section in structured_content:
#         indent = "  " * (section['level'] - 1)
#         summary += f"{indent}- {section['title']}\n"
    
#     summary += "\n### Detailed Content\n\n"
    
#     # Add detailed content for each section
#     for section in structured_content:
#         header_marker = "#" * (section['level'] + 2)
#         summary += f"{header_marker} {section['title']}\n\n"
        
#         if section['content']:
#             # Include full content for important sections
#             summary += f"{section['content']}\n\n"
#         else:
#             summary += "*(No content found for this section)*\n\n"
    
#     # Add raw text excerpt if structured extraction was limited
#     if len(structured_content) < 3:
#         summary += "\n### Additional Content\n\n"
#         summary += full_text[:5000] + "...\n"
    
#     return summary

# # URL Analysis Endpoint - Enhanced version
# @app.post("/analyze/url")
# async def analyze_url(data: Dict[str, Any]) -> JSONResponse:
#     """Analyze any URL and provide a comprehensive structured summary"""
#     try:
#         url = data.get("url")
#         if not url:
#             raise HTTPException(status_code=400, detail="URL is required")
        
#         # Validate URL
#         parsed_url = urlparse(url)
#         if not parsed_url.scheme:
#             url = f"https://{url}"
            
#         print(f"Analyzing URL: {url}")
        
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.5',
#             'Accept-Encoding': 'gzip, deflate',
#             'Connection': 'keep-alive',
#         }
        
#         # Fetch the content
#         response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
#         response.raise_for_status()
        
#         # Parse HTML
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Remove script and style elements
#         for script in soup(["script", "style", "meta", "link", "noscript", "svg"]):
#             script.decompose()
        
#         # Extract title
#         title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        
#         # Extract structured content
#         structured_content = extract_structured_content(soup)
        
#         # Find main content area
#         main_content = None
#         content_selectors = [
#             'main', 'article', '[role="main"]', '.content', '#content', 
#             '.post', '.entry-content', '.article-body', '.post-content',
#             '.markdown-body', '.documentation-content', '.docs-content',
#             '.prose', '[class*="content"]', '[id*="content"]'
#         ]
        
#         for selector in content_selectors:
#             elements = soup.select(selector)
#             if elements:
#                 main_content = max(elements, key=lambda x: len(x.get_text(strip=True)))
#                 if len(main_content.get_text(strip=True)) > 500:
#                     break
        
#         if not main_content:
#             main_content = soup.body if soup.body else soup
        
#         # Extract full text for context
#         full_text = main_content.get_text(separator='\n', strip=True)
        
#         # Generate comprehensive summary
#         summary = ""
        
#         if meeting_summarizer and meeting_summarizer.llm_manager.current_provider:
#             try:
#                 # Create a detailed prompt with structured content
#                 prompt = f"""Analyze this webpage and extract ALL important information in a structured format:

# URL: {url}
# Title: {title}

# STRUCTURED CONTENT FOUND:
# {format_structured_content(structured_content)}

# FULL CONTENT:
# {full_text[:20000]}

# Please provide a COMPREHENSIVE analysis with:

# 1. **Overview**: Brief description of what this page/document is about

# 2. **Main Topics and Details**: Extract ALL main topics with their complete information
#    - Include all subtopics and their explanations
#    - Include any code examples, commands, or technical details
#    - Include any important definitions or concepts
#    - Preserve the hierarchical structure

# 3. **Key Concepts Explained**: List and explain all important concepts mentioned

# 4. **Technical Details**: 
#    - Any code snippets, commands, or configurations
#    - API endpoints, parameters, or specifications
#    - Installation or setup instructions

# 5. **Important Points**: Any warnings, best practices, or crucial information

# 6. **Resources and Links**: Any referenced resources, tools, or related links

# Format the response with clear headers and bullet points. Include as much detail as possible from the original content."""
                
#                 print("Generating comprehensive structured summary with LLM...")
#                 summary = meeting_summarizer.llm_manager.generate(prompt, temperature=0.2, max_tokens=4000)
#             except Exception as e:
#                 print(f"LLM summarization failed: {e}")
#                 # Fallback to structured extraction
#                 summary = create_fallback_summary(structured_content, full_text)
#         else:
#             # Fallback without LLM
#             summary = create_fallback_summary(structured_content, full_text)
        
#         # Format the output
#         formatted_summary = f"URL Analysis Summary\n"
#         formatted_summary += f"URL: {url}\n"
#         formatted_summary += f"Title: {title}\n"
#         formatted_summary += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
#         formatted_summary += f"Content Structure: {len(structured_content)} sections found\n"
#         formatted_summary += "="*70 + "\n\n"
#         formatted_summary += f"{summary}\n"
        
#         # Save output
#         output_filename = f"url_analysis_{uuid.uuid4().hex}.txt"
#         output_path = OUTPUT_DIR / output_filename
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(formatted_summary)
        
#         print(f"URL analysis completed successfully")
        
#         return JSONResponse({
#             "status": "success",
#             "filename": output_filename,
#             "summary": formatted_summary,
#             "title": title,
#             "url": url,
#             "sections_found": len(structured_content)
#         })
            
#     except requests.exceptions.Timeout:
#         raise HTTPException(status_code=500, detail="Request timed out. The website took too long to respond.")
#     except requests.exceptions.ConnectionError:
#         raise HTTPException(status_code=500, detail="Could not connect to the URL. Please check if the URL is correct and accessible.")
#     except requests.exceptions.HTTPError as e:
#         raise HTTPException(status_code=500, detail=f"HTTP error {e.response.status_code}: {e.response.reason}")
#     except Exception as e:
#         print(f"URL analysis error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/meeting/summarize")
# async def summarize_meeting(data: dict):
#     """Generate professional meeting summary with pluggable LLM"""
#     try:
#         # Extract data
#         main_transcript = data.get("main_transcript", {})
#         attachments = data.get("attachments", [])
#         meeting_context = data.get("context", "")
#         custom_instructions = data.get("instructions", "")
#         provider = data.get("provider", "gemini")
        
#         # Switch provider if different from current
#         if provider != meeting_summarizer.llm_manager.current_provider_name:
#             try:
#                 provider_config = data.get("provider_config", {})
#                 meeting_summarizer.switch_provider(provider, **provider_config)
#             except Exception as e:
#                 return JSONResponse({
#                     "status": "error",
#                     "message": f"Failed to switch to {provider}: {str(e)}",
#                     "available_providers": meeting_summarizer.get_available_providers()
#                 })
        
#         # Prepare transcript data
#         main_text = main_transcript.get("text", "") or main_transcript.get("formatted_text", "")
        
#         # Prepare attachments
#         processed_attachments = []
#         for att in attachments:
#             processed_attachments.append({
#                 "type": att.get("type", "unknown"),
#                 "text": att.get("text", "") or att.get("formatted_text", ""),
#                 "url": att.get("url", ""),
#                 "summary": att.get("summary", "")
#             })
        
#         # Generate summary
#         result = meeting_summarizer.generate_meeting_summary(
#             main_transcript=main_text,
#             attachments=processed_attachments,
#             meeting_context=meeting_context,
#             custom_instructions=custom_instructions
#         )
        
#         if result["status"] == "error":
#             raise Exception(result["error"])
        
#         # Save the summary
#         output_filename = f"meeting_summary_{uuid.uuid4().hex}.txt"
#         output_path = OUTPUT_DIR / output_filename
        
#         # Format output
#         formatted_output = f"""Professional Meeting Summary
# Generated by: {result['provider'].upper()}
# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# {'='*60}

# EXECUTIVE SUMMARY:
# {result['summary']}

# {'='*60}

# STRATEGIC INSIGHTS:
# {result['insights']}

# {'='*60}

# ACTION ITEMS:
# {result['action_items']}

# {'='*60}

# TRANSCRIPT STATISTICS:
# - Original Length: {result['original_length']} characters
# - Cleaned Length: {result['cleaned_length']} characters
# - Reduction: {((result['original_length'] - result['cleaned_length']) / result['original_length'] * 100):.1f}%

# {'='*60}

# CLEANED TRANSCRIPT:
# {result['cleaned_transcript'][:5000]}...
# """
        
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(formatted_output)
        
#         return JSONResponse({
#             "status": "success",
#             "filename": output_filename,
#             "summary": result["summary"],
#             "insights": result["insights"],
#             "action_items": result["action_items"],
#             "provider": result["provider"],
#             "statistics": {
#                 "original_length": result["original_length"],
#                 "cleaned_length": result["cleaned_length"],
#                 "reduction_percentage": round((result['original_length'] - result['cleaned_length']) / result['original_length'] * 100, 1)
#             }
#         })
        
#     except Exception as e:
#         print(f"Meeting summarization error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/meeting/providers")
# async def get_llm_providers():
#     """Get available LLM providers and their status"""
#     try:
#         providers = meeting_summarizer.get_available_providers()
#         current_provider = meeting_summarizer.llm_manager.current_provider_name
        
#         return JSONResponse({
#             "status": "success",
#             "current_provider": current_provider,
#             "providers": providers,
#             "provider_details": {
#                 "gemini": {
#                     "name": "Google Gemini",
#                     "requires": "GEMINI_API_KEY",
#                     "models": ["gemini-1.5-flash", "gemini-1.5-pro"]
#                 },
#                 "openai": {
#                     "name": "OpenAI GPT",
#                     "requires": "OPENAI_API_KEY",
#                     "models": ["gpt-4", "gpt-3.5-turbo"]
#                 },
#                 "claude": {
#                     "name": "Anthropic Claude",
#                     "requires": "ANTHROPIC_API_KEY",
#                     "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
#                 },
#                 "ollama": {
#                     "name": "Local Ollama",
#                     "requires": "Ollama service running",
#                     "models": ["llama2", "mistral", "codellama"]
#                 }
#             }
#         })
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/meeting/switch-provider")
# async def switch_llm_provider(data: dict):
#     """Switch to a different LLM provider"""
#     try:
#         provider = data.get("provider")
#         config = data.get("config", {})
        
#         if not provider:
#             raise HTTPException(status_code=400, detail="Provider name is required")
        
#         meeting_summarizer.switch_provider(provider, **config)
        
#         return JSONResponse({
#             "status": "success",
#             "message": f"Switched to {provider}",
#             "current_provider": provider
#         })
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/download/{filename}")
# async def download_file(filename: str):
#     """Download transcribed file"""
#     file_path = OUTPUT_DIR / filename
#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="File not found")
    
#     return FileResponse(
#         path=file_path,
#         filename=filename,
#         media_type="text/plain"
#             )

# try:
#     from langchain.llms import Ollama
    
#     # Prefer these models in order (better models first)
#     preferred_models = [
#         'tinyllama:latest',     # 1.1 GB - more stable
#         'qwen:0.5b',           # 394 MB - very small
#         'gemma:2b',            # 1.4 GB - good quality
#         'phi:latest',          # 1.6 GB - fallback only
#     ]
    
#     model_name = None
    
#     # Check which models are available
#     import subprocess
#     try:
#         result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
#         if result.returncode == 0:
#             available_models = result.stdout.lower()
#             print(f"Available Ollama models:\n{result.stdout}")
            
#             # Use the first available preferred model
#             for model in preferred_models:
#                 model_base = model.split(':')[0]
#                 if model_base in available_models:
#                     model_name = model
#                     print(f"Selected model: {model_name}")
#                     break
            
#             if not model_name:
#                 print("No preferred models found. Please install tinyllama:")
#                 print("ollama pull tinyllama")
#                 model_name = 'tinyllama:latest'
#     except:
#         model_name = 'tinyllama:latest'
    
#     # Initialize with simpler configuration
#     llm = Ollama(
#         model=model_name,
#         temperature=0.7,
#         num_ctx=2048,
#         verbose=False,
#     )
#     llm_available = True
#     print(f"LLM initialized with model: {model_name}")
    
#     # Test the model
#     try:
#         test_response = llm.invoke("Hello")
#         print(f"Model test successful")
#     except Exception as e:
#         print(f"Model test failed: {e}")
#         llm_available = False
    
# except Exception as e:
#     print(f"Could not initialize Ollama: {e}")
#     llm_available = False
# @app.post("/chat")
# async def chat_with_llm(data: dict):
#     """Chat with local LLM"""
#     try:
#         if not llm_available:
#             raise HTTPException(
#                 status_code=503, 
#                 detail="LLM service is not available. Please ensure Ollama is installed and running with 'ollama serve'"
#             )
        
#         message = data.get("message")
#         if not message:
#             raise HTTPException(status_code=400, detail="Message is required")
        
#         # Clean input
#         message = message.strip()
        
#         # Get response from LLM - direct approach without system prompts
#         try:
#             # Direct invocation without any formatting
#             response = llm.invoke(message)
            
#             # Clean the response
#             if isinstance(response, str):
#                 # Remove control characters
#                 response = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response)
#                 # Remove ^C, ^X patterns
#                 response = re.sub(r'\^[A-Z]', '', response)
                
#                 # Remove common phi model artifacts
#                 unwanted_phrases = [
#                     "Certainly! Here's a clear and concise response",
#                     "You are a helpful assistant",
#                     "Please provide a clear and concise response",
#                     "User:",
#                     "Assistant:",
#                     "Human:",
#                     "Response:",
#                     "Answer:",
#                 ]
                
#                 for phrase in unwanted_phrases:
#                     response = response.replace(phrase, "")
                
#                 # Clean up extra whitespace
#                 response = re.sub(r'\n{2,}', '\n', response)
#                 response = re.sub(r' {2,}', ' ', response)
#                 response = response.strip()
                
#                 # If response is too short or empty after cleaning
#                 if len(response) < 2:
#                     # Try a different approach - use the raw output
#                     response = llm.invoke(message)
#                     # Just do basic cleaning
#                     response = response.strip()
            
#         except Exception as e:
#             error_msg = str(e)
#             if "memory" in error_msg.lower():
#                 raise HTTPException(
#                     status_code=503,
#                     detail=f"Not enough memory. Try a smaller model: ollama pull qwen:0.5b"
#                 )
#             else:
#                 raise HTTPException(status_code=500, detail=f"Ollama error: {error_msg}")
        
#         return JSONResponse({
#             "status": "success",
#             "response": response,
#             "model": model_name
#         })
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     # Check Ollama status
#     ollama_status = "not available"
#     ollama_models = []
    
#     if llm_available:
#         try:
#             # Test if Ollama is actually working
#             test_response = llm("test")
#             ollama_status = "ready"
            
#             # Get list of models
#             result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
#             if result.returncode == 0:
#                 lines = result.stdout.strip().split('\n')
#                 if len(lines) > 1:  # Skip header
#                     for line in lines[1:]:
#                         if line.strip():
#                             model_info = line.split()
#                             if model_info:
#                                 ollama_models.append(model_info[0])
#         except:
#             ollama_status = "error"
    
#     return JSONResponse({
#         "status": "healthy",
#         "whisper_model": "loaded",
#         "llm_available": llm_available,
#         "ollama_status": ollama_status,
#         "ollama_models": ollama_models,
#         "device": device
#     })

# # Root endpoint for testing
# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {
#         "message": "Multimodal Transcription API", 
#         "version": "1.0.0",
#         "endpoints": {
#             "transcription": [
#                 "POST /transcribe/audio",
#                 "POST /transcribe/video", 
#                 "POST /transcribe/youtube"
#             ],
#             "analysis": [
#                 "POST /analyze/url"
#             ],
#             "meeting": [
#                 "POST /meeting/summarize",
#                 "GET /meeting/providers",
#                 "POST /meeting/switch-provider"
#             ],
#             "chat": [
#                 "POST /chat"
#             ],
#             "utility": [
#                 "GET /health",
#                 "GET /download/{filename}"
#             ]
#         }
#     }

# # Suppress gRPC and Google warnings
# import os
# import warnings

# os.environ['GRPC_VERBOSITY'] = 'ERROR'
# os.environ['GLOG_minloglevel'] = '2'

# # Suppress absl warnings
# try:
#     import absl.logging
#     absl.logging.set_verbosity(absl.logging.ERROR)
# except:
#     pass

# # Debug: Print all registered routes
# print("\nRegistered endpoints:")
# for route in app.routes:
#     if hasattr(route, 'methods') and hasattr(route, 'path'):
#         print(f"{route.methods} {route.path}")

# if __name__ == "__main__":
#     import uvicorn
#     print(f"\nStarting server on http://localhost:8000")
#     print(f"Using device: {device}")
#     print(f"LLM available: {llm_available}")
#     if llm_available:
#         print(f"Ollama model: {model_name}")
#     else:
#         print("To enable chat functionality:")
#         print("1. Install Ollama: https://ollama.ai")
#         print("2. Start Ollama: ollama serve")
#         print("3. Pull a model: ollama pull llama2")
    
#     uvicorn.run(app, host="0.0.0.0", port=8000)

## Complete app.py

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import torch
import os
import tempfile
import shutil
from pathlib import Path
import yt_dlp
import requests
from bs4 import BeautifulSoup
import moviepy.editor as mp
from datetime import datetime
import asyncio
from typing import Optional, Dict, Any, List
import uuid
import time
from urllib.parse import urlparse
from meeting_summarizer import MeetingSummarizer
import json
from config import Config
import re

model_name = 'phi'  # Default model name
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Whisper model
print("Loading Whisper model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model = whisper.load_model("base", device=device)

# Create directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize the meeting summarizer
meeting_summarizer = MeetingSummarizer(llm_provider="gemini")

# Session storage for chat contexts (in production, use Redis or a database)
session_contexts = {}

# Initialize LLM as None first
llm = None
llm_available = False

class TranscriptionService:
    @staticmethod
    async def transcribe_audio(file_path: str, source_type: str) -> dict:
        """Transcribe audio file using Whisper"""
        try:
            result = whisper_model.transcribe(
                file_path,
                language="en",
                task="transcribe",
                verbose=False
            )
            
            # Format output with timestamps
            formatted_text = f"Source Type: {source_type}\n"
            formatted_text += f"Transcription Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            formatted_text += "="*50 + "\n\n"
            
            # Add segments with timestamps
            for segment in result["segments"]:
                start_time = f"{int(segment['start']//60):02d}:{int(segment['start']%60):02d}"
                end_time = f"{int(segment['end']//60):02d}:{int(segment['end']%60):02d}"
                formatted_text += f"[{start_time} - {end_time}] {segment['text'].strip()}\n\n"
            
            return {
                "text": result["text"],
                "formatted_text": formatted_text,
                "segments": result["segments"]
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    @staticmethod
    async def extract_audio_from_video(video_path: str) -> str:
        """Extract audio from video file"""
        try:
            audio_path = video_path.replace(Path(video_path).suffix, ".wav")
            video = mp.VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            return audio_path
        except Exception as e:
            raise Exception(f"Audio extraction failed: {str(e)}")
    
    @staticmethod
    async def download_youtube_audio(url: str) -> str:
        """Download audio from YouTube with updated options"""
        try:
            output_filename = f"youtube_{uuid.uuid4().hex}"
            output_path = str(UPLOAD_DIR / f"{output_filename}.wav")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(UPLOAD_DIR / output_filename),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'age_limit': None,
                'geo_bypass': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists(output_path):
                return output_path
                
            base_path = str(UPLOAD_DIR / output_filename)
            if os.path.exists(base_path + '.wav'):
                return base_path + '.wav'
                
            raise Exception("Downloaded file not found")
            
        except Exception as e:
            error_msg = str(e).replace('[0;31mERROR:[0m', 'ERROR:')
            raise Exception(f"YouTube download failed: {error_msg}")

async def download_youtube_alternative(url: str) -> str:
    """Alternative YouTube download method using pytubefix"""
    try:
        from pytubefix import YouTube
        from pytubefix.cli import on_progress
        
        url = url.strip()
        output_filename = f"youtube_{uuid.uuid4().hex}.wav"
        output_path = str(UPLOAD_DIR / output_filename)
        temp_filename = f"temp_{uuid.uuid4().hex}"
        
        print(f"Attempting to download from YouTube using pytubefix: {url}")
        
        yt = YouTube(url, on_progress_callback=on_progress)
        
        print(f"Video Title: {yt.title}")
        print(f"Video Length: {yt.length} seconds")
        
        audio_stream = None
        audio_streams = yt.streams.filter(only_audio=True)
        
        if audio_streams:
            audio_stream = audio_streams.filter(file_extension='m4a').first()
            if not audio_stream:
                audio_stream = audio_streams.filter(file_extension='mp4').first()
            if not audio_stream:
                audio_stream = audio_streams.first()
        
        if not audio_stream:
            print("No audio-only stream found, trying video stream...")
            audio_stream = yt.streams.get_lowest_resolution()
        
        if not audio_stream:
            raise Exception("No suitable stream available for this video")
        
        print(f"Selected stream: {audio_stream}")
        print("Downloading...")
        
        downloaded_file = audio_stream.download(
            output_path=str(UPLOAD_DIR),
            filename=temp_filename
        )
        
        print(f"Downloaded to: {downloaded_file}")
        print("Converting to WAV format...")
        
        try:
            if audio_stream.includes_video_track:
                video = mp.VideoFileClip(downloaded_file)
                video.audio.write_audiofile(output_path, verbose=False, logger=None)
                video.close()
            else:
                audio = mp.AudioFileClip(downloaded_file)
                audio.write_audiofile(output_path, verbose=False, logger=None)
                audio.close()
        except Exception as e:
            print(f"MoviePy conversion failed: {e}, trying alternative method...")
            import subprocess
            subprocess.run([
                'ffmpeg', '-i', downloaded_file, '-acodec', 'pcm_s16le', 
                '-ar', '16000', '-ac', '1', output_path, '-y'
            ], check=True, capture_output=True)
        
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        
        print(f"Successfully converted to: {output_path}")
        return output_path
        
    except ImportError:
        raise Exception("pytubefix is not installed. Please run: pip install pytubefix")
    except Exception as e:
        raise Exception(f"Alternative YouTube download failed: {str(e)}")

@app.post("/transcribe/audio")
async def transcribe_audio_file(file: UploadFile = File(...)):
    """Handle audio file upload and transcription"""
    temp_file = None
    try:
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")
        
        temp_file = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        result = await TranscriptionService.transcribe_audio(str(temp_file), "Audio File")
        
        output_filename = f"{Path(file.filename).stem}_transcript.txt"
        output_path = OUTPUT_DIR / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["formatted_text"])
        
        return JSONResponse({
            "status": "success",
            "filename": output_filename,
            "text": result["text"],
            "formatted_text": result["formatted_text"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file and temp_file.exists():
            os.remove(temp_file)

@app.post("/transcribe/video")
async def transcribe_video_file(file: UploadFile = File(...)):
    """Handle video file upload and transcription"""
    temp_video = None
    temp_audio = None
    try:
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")
        
        temp_video = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
        with open(temp_video, "wb") as f:
            content = await file.read()
            f.write(content)
        
        temp_audio = await TranscriptionService.extract_audio_from_video(str(temp_video))
        result = await TranscriptionService.transcribe_audio(temp_audio, "Video File")
        
        output_filename = f"{Path(file.filename).stem}_transcript.txt"
        output_path = OUTPUT_DIR / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["formatted_text"])
        
        return JSONResponse({
            "status": "success",
            "filename": output_filename,
            "text": result["text"],
            "formatted_text": result["formatted_text"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_video and temp_video.exists():
            os.remove(temp_video)
        if temp_audio and Path(temp_audio).exists():
            os.remove(temp_audio)

@app.post("/transcribe/youtube")
async def transcribe_youtube(data: dict):
    """Handle YouTube URL transcription"""
    temp_audio = None
    try:
        url = data.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        url = url.strip()
        if not ('youtube.com' in url or 'youtu.be' in url):
            raise HTTPException(status_code=400, detail="Please provide a valid YouTube URL")
        
        print(f"Processing YouTube URL: {url}")
        
        try:
            print("Attempting download with pytubefix...")
            temp_audio = await download_youtube_alternative(url)
            print("Download successful")
        except Exception as e:
            print(f"Pytubefix failed: {e}")
            try:
                print("Attempting download with yt-dlp...")
                temp_audio = await TranscriptionService.download_youtube_audio(url)
                print("yt-dlp successful")
            except Exception as e2:
                print(f"yt-dlp also failed: {e2}")
                raise Exception(f"Could not download YouTube video. Please try a different video or check if the video is available in your region.")
        
        if not temp_audio or not os.path.exists(temp_audio):
            raise Exception("Download completed but audio file not found")
        
        file_size_mb = os.path.getsize(temp_audio) / (1024 * 1024)
        print(f"Audio file size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 500:
            print(f"Warning: Large audio file ({file_size_mb:.2f} MB). Transcription may take a while...")
        
        print("Starting transcription...")
        result = await TranscriptionService.transcribe_audio(temp_audio, "YouTube Video")
        
        output_filename = f"youtube_{uuid.uuid4().hex}_transcript.txt"
        output_path = OUTPUT_DIR / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["formatted_text"])
        
        return JSONResponse({
            "status": "success",
            "filename": output_filename,
            "text": result["text"],
            "formatted_text": result["formatted_text"]
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"YouTube transcription error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if temp_audio and Path(temp_audio).exists():
            try:
                os.remove(temp_audio)
                print("Cleaned up temporary audio file")
            except:
                pass

def extract_structured_content(soup):
    """Extract structured content with headers and their associated text"""
    structured_content = []
    
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    for header in headers:
        header_level = int(header.name[1])
        header_text = header.get_text(strip=True)
        
        if not header_text:
            continue
        
        content_parts = []
        current = header.next_sibling
        
        while current:
            if current.name and current.name.startswith('h'):
                next_level = int(current.name[1])
                if next_level <= header_level:
                    break
            
            if hasattr(current, 'get_text'):
                text = current.get_text(strip=True)
                if text:
                    if current.name == 'pre' or (current.name == 'code' and current.parent.name != 'pre'):
                        content_parts.append(f"```\n{text}\n```")
                    elif current.name in ['ul', 'ol']:
                        list_items = current.find_all('li')
                        for li in list_items:
                            content_parts.append(f"• {li.get_text(strip=True)}")
                    elif current.name == 'p':
                        content_parts.append(text)
                    elif text and current.name not in ['script', 'style']:
                        content_parts.append(text)
            
            current = current.next_sibling
        structured_content.append({
            'level': header_level,
            'title': header_text,
            'content': '\n'.join(content_parts)
        })
    
    return structured_content

def format_structured_content(structured_content):
    """Format structured content for display"""
    formatted = []
    
    for section in structured_content:
        indent = "  " * (section['level'] - 1)
        formatted.append(f"{indent}{'#' * section['level']} {section['title']}")
        if section['content']:
            content_lines = section['content'].split('\n')
            for line in content_lines[:5]:
                if line.strip():
                    formatted.append(f"{indent}  {line}")
    
    return '\n'.join(formatted)

def create_fallback_summary(structured_content, full_text):
    """Create a summary without LLM"""
    summary = "## Document Structure and Content\n\n"
    
    summary += "### Table of Contents\n"
    for section in structured_content:
        indent = "  " * (section['level'] - 1)
        summary += f"{indent}- {section['title']}\n"
    
    summary += "\n### Detailed Content\n\n"
    
    for section in structured_content:
        header_marker = "#" * (section['level'] + 2)
        summary += f"{header_marker} {section['title']}\n\n"
        
        if section['content']:
            summary += f"{section['content']}\n\n"
        else:
            summary += "*(No content found for this section)*\n\n"
    
    if len(structured_content) < 3:
        summary += "\n### Additional Content\n\n"
        summary += full_text[:5000] + "...\n"
    
    return summary

@app.post("/analyze/url")
async def analyze_url(data: Dict[str, Any]) -> JSONResponse:
    """Analyze any URL and provide a comprehensive structured summary"""
    try:
        url = data.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = f"https://{url}"
            
        print(f"Analyzing URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script in soup(["script", "style", "meta", "link", "noscript", "svg"]):
            script.decompose()
        
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        
        structured_content = extract_structured_content(soup)
        
        main_content = None
        content_selectors = [
            'main', 'article', '[role="main"]', '.content', '#content', 
            '.post', '.entry-content', '.article-body', '.post-content',
            '.markdown-body', '.documentation-content', '.docs-content',
            '.prose', '[class*="content"]', '[id*="content"]'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                main_content = max(elements, key=lambda x: len(x.get_text(strip=True)))
                if len(main_content.get_text(strip=True)) > 500:
                    break
        
        if not main_content:
            main_content = soup.body if soup.body else soup
        
        full_text = main_content.get_text(separator='\n', strip=True)
        
        summary = ""
        
        if meeting_summarizer and meeting_summarizer.llm_manager.current_provider:
            try:
                prompt = f"""Analyze this webpage and extract ALL important information in a structured format:

URL: {url}
Title: {title}

STRUCTURED CONTENT FOUND:
{format_structured_content(structured_content)}

FULL CONTENT:
{full_text[:20000]}

Please provide a COMPREHENSIVE analysis with:

1. **Overview**: Brief description of what this page/document is about

2. **Main Topics and Details**: Extract ALL main topics with their complete information
   - Include all subtopics and their explanations
   - Include any code examples, commands, or technical details
   - Include any important definitions or concepts
   - Preserve the hierarchical structure

3. **Key Concepts Explained**: List and explain all important concepts mentioned

4. **Technical Details**: 
   - Any code snippets, commands, or configurations
   - API endpoints, parameters, or specifications
   - Installation or setup instructions

5. **Important Points**: Any warnings, best practices, or crucial information

6. **Resources and Links**: Any referenced resources, tools, or related links

Format the response with clear headers and bullet points. Include as much detail as possible from the original content."""
                
                print("Generating comprehensive structured summary with LLM...")
                summary = meeting_summarizer.llm_manager.generate(prompt, temperature=0.2, max_tokens=4000)
            except Exception as e:
                print(f"LLM summarization failed: {e}")
                summary = create_fallback_summary(structured_content, full_text)
        else:
            summary = create_fallback_summary(structured_content, full_text)
        
        formatted_summary = f"URL Analysis Summary\n"
        formatted_summary += f"URL: {url}\n"
        formatted_summary += f"Title: {title}\n"
        formatted_summary += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        formatted_summary += f"Content Structure: {len(structured_content)} sections found\n"
        formatted_summary += "="*70 + "\n\n"
        formatted_summary += f"{summary}\n"
        
        output_filename = f"url_analysis_{uuid.uuid4().hex}.txt"
        output_path = OUTPUT_DIR / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_summary)
        
        print(f"URL analysis completed successfully")
        
        return JSONResponse({
            "status": "success",
            "filename": output_filename,
            "summary": formatted_summary,
            "title": title,
            "url": url,
            "sections_found": len(structured_content)
        })
            
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=500, detail="Request timed out. The website took too long to respond.")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="Could not connect to the URL. Please check if the URL is correct and accessible.")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error {e.response.status_code}: {e.response.reason}")
    except Exception as e:
        print(f"URL analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meeting/summarize")
async def summarize_meeting(data: dict):
    """Generate professional meeting summary with pluggable LLM"""
    try:
        main_transcript = data.get("main_transcript", {})
        attachments = data.get("attachments", [])
        meeting_context = data.get("context", "")
        custom_instructions = data.get("instructions", "")
        provider = data.get("provider", "gemini")
        
        if provider != meeting_summarizer.llm_manager.current_provider_name:
            try:
                provider_config = data.get("provider_config", {})
                meeting_summarizer.switch_provider(provider, **provider_config)
            except Exception as e:
                return JSONResponse({
                    "status": "error",
                    "message": f"Failed to switch to {provider}: {str(e)}",
                    "available_providers": meeting_summarizer.get_available_providers()
                })
        
        main_text = main_transcript.get("text", "") or main_transcript.get("formatted_text", "")
        
        processed_attachments = []
        for att in attachments:
            processed_attachments.append({
                "type": att.get("type", "unknown"),
                "text": att.get("text", "") or att.get("formatted_text", ""),
                "url": att.get("url", ""),
                "summary": att.get("summary", "")
            })
        
        result = meeting_summarizer.generate_meeting_summary(
            main_transcript=main_text,
            attachments=processed_attachments,
            meeting_context=meeting_context,
            custom_instructions=custom_instructions
        )
        
        if result["status"] == "error":
            raise Exception(result["error"])
        
        output_filename = f"meeting_summary_{uuid.uuid4().hex}.txt"
        output_path = OUTPUT_DIR / output_filename
        
        formatted_output = f"""Professional Meeting Summary
Generated by: {result['provider'].upper()}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

EXECUTIVE SUMMARY:
{result['summary']}

{'='*60}

STRATEGIC INSIGHTS:
{result['insights']}

{'='*60}

ACTION ITEMS:
{result['action_items']}

{'='*60}

TRANSCRIPT STATISTICS:
- Original Length: {result['original_length']} characters
- Cleaned Length: {result['cleaned_length']} characters
- Reduction: {((result['original_length'] - result['cleaned_length']) / result['original_length'] * 100):.1f}%

{'='*60}

CLEANED TRANSCRIPT:
{result['cleaned_transcript'][:5000]}...
"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        
        return JSONResponse({
            "status": "success",
            "filename": output_filename,
            "summary": result["summary"],
            "insights": result["insights"],
            "action_items": result["action_items"],
            "provider": result["provider"],
            "statistics": {
                "original_length": result["original_length"],
                "cleaned_length": result["cleaned_length"],
                "reduction_percentage": round((result['original_length'] - result['cleaned_length']) / result['original_length'] * 100, 1)
            }
        })
        
    except Exception as e:
        print(f"Meeting summarization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meeting/providers")
async def get_llm_providers():
    """Get available LLM providers and their status"""
    try:
        providers = meeting_summarizer.get_available_providers()
        current_provider = meeting_summarizer.llm_manager.current_provider_name
        
        return JSONResponse({
            "status": "success",
            "current_provider": current_provider,
            "providers": providers,
            "provider_details": {
                "gemini": {
                    "name": "Google Gemini",
                    "requires": "GEMINI_API_KEY",
                    "models": ["gemini-pro", "gemini-1.5-pro"]
                },
                "openai": {
                    "name": "OpenAI GPT",
                    "requires": "OPENAI_API_KEY",
                    "models": ["gpt-4", "gpt-3.5-turbo"]
                },
                "claude": {
                    "name": "Anthropic Claude",
                    "requires": "ANTHROPIC_API_KEY",
                    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
                },
                "ollama": {
                    "name": "Local Ollama",
                    "requires": "Ollama service running",
                    "models": ["llama2", "mistral", "codellama"]
                }
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meeting/switch-provider")
async def switch_llm_provider(data: dict):
    """Switch to a different LLM provider"""
    try:
        provider = data.get("provider")
        config = data.get("config", {})
        
        if not provider:
            raise HTTPException(status_code=400, detail="Provider name is required")
        
        meeting_summarizer.switch_provider(provider, **config)
        
        return JSONResponse({
            "status": "success",
            "message": f"Switched to {provider}",
            "current_provider": provider
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW ENDPOINTS FOR CONTEXT-AWARE CHAT

# @app.post("/chat/context")
# async def chat_with_context(data: dict):
#     """Chat with LLM using transcription/summary context"""
#     try:
#         message = data.get("message")
#         session_id = data.get("session_id", "default")
#         context_data = data.get("context", {})
#         provider = data.get("provider", "gemini")
        
#         if not message:
#             raise HTTPException(status_code=400, detail="Message is required")
        
#         # Store or update context for this session
#         if context_data:
#             session_contexts[session_id] = context_data
        
#         # Get stored context
#         stored_context = session_contexts.get(session_id, {})
        
#         # Build context-aware prompt
#         context_prompt = ""
        
#         if stored_context.get("transcription"):
#             context_prompt += f"Original Transcription:\n{stored_context['transcription'][:3000]}\n\n"
        
#         if stored_context.get("summary"):
#             context_prompt += f"Meeting Summary:\n{stored_context['summary']}\n\n"
        
#         if stored_context.get("insights"):
#             context_prompt += f"Key Insights:\n{stored_context['insights']}\n\n"
        
#         if stored_context.get("action_items"):
#             context_prompt += f"Action Items:\n{stored_context['action_items']}\n\n"
        
#         if stored_context.get("attachments"):
#             context_prompt += "Additional Context from Attachments:\n"
#             for i, att in enumerate(stored_context['attachments'][:3]):  # Limit to 3 attachments
#                 context_prompt += f"\nAttachment {i+1} ({att.get('type', 'unknown')}):\n"
#                 context_prompt += f"{att.get('content', '')[:1000]}...\n"
        
#         # Create the full prompt
#         full_prompt = f"""You are an AI assistant with access to a meeting transcript and its analysis. Use this context to answer questions accurately.

# CONTEXT:
# {context_prompt}

# USER QUESTION: {message}

# Please provide a detailed and helpful response based on the context above. If asked for predictions or analysis, base them on the meeting content. If the question is outside the context, still try to be helpful but mention if you're going beyond the provided information."""

#         # Use the meeting summarizer's LLM manager for consistency
#         if provider != meeting_summarizer.llm_manager.current_provider_name:
#             meeting_summarizer.switch_provider(provider)
        
#         response = meeting_summarizer.llm_manager.generate(
#             full_prompt, 
#             temperature=0,
#             temperature=0.7, 
#             max_tokens=2000
#         )
        
#         return JSONResponse({
#             "status": "success",
#             "response": response,
#             "provider": provider,
#             "has_context": bool(stored_context)
#         })
        
#     except Exception as e:
#         print(f"Context chat error: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))
@app.post("/chat/context")
async def chat_with_context(data: dict):
    """Chat with LLM using transcription/summary context"""
    try:
        message = data.get("message")
        session_id = data.get("session_id", "default")
        context_data = data.get("context", {})
        provider = data.get("provider", "gemini")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Store or update context for this session
        if context_data:
            session_contexts[session_id] = context_data
        
        # Get stored context
        stored_context = session_contexts.get(session_id, {})
        
        # Build context-aware prompt
        context_prompt = ""
        
        if stored_context.get("transcription"):
            context_prompt += f"Original Transcription:\n{stored_context['transcription'][:3000]}\n\n"
        
        if stored_context.get("summary"):
            context_prompt += f"Meeting Summary:\n{stored_context['summary']}\n\n"
        
        if stored_context.get("insights"):
            context_prompt += f"Key Insights:\n{stored_context['insights']}\n\n"
        
        if stored_context.get("action_items"):
            context_prompt += f"Action Items:\n{stored_context['action_items']}\n\n"
        
        if stored_context.get("attachments"):
            context_prompt += "Additional Context from Attachments:\n"
            for i, att in enumerate(stored_context['attachments'][:3]):  # Limit to 3 attachments
                context_prompt += f"\nAttachment {i+1} ({att.get('type', 'unknown')}):\n"
                context_prompt += f"{att.get('content', '')[:1000]}...\n"
        
        # Create the full prompt
        full_prompt = f"""You are an AI assistant with access to a meeting transcript and its analysis. Use this context to answer questions accurately.

CONTEXT:
{context_prompt}

USER QUESTION: {message}

Please provide a detailed and helpful response based on the context above. If asked for predictions or analysis, base them on the meeting content. If the question is outside the context, still try to be helpful but mention if you're going beyond the provided information."""

        # Use the meeting summarizer's LLM manager for consistency
        if provider != meeting_summarizer.llm_manager.current_provider_name:
            meeting_summarizer.switch_provider(provider)
        
        response = meeting_summarizer.llm_manager.generate(
            full_prompt, 
            temperature=0.7, 
            max_tokens=2000
        )
        
        return JSONResponse({
            "status": "success",
            "response": response,
            "provider": provider,
            "has_context": bool(stored_context)
        })
        
    except Exception as e:
        print(f"Context chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/clear-context")
async def clear_chat_context(data: dict):
    """Clear the chat context for a session"""
    session_id = data.get("session_id", "default")
    if session_id in session_contexts:
        del session_contexts[session_id]
    return JSONResponse({"status": "success", "message": "Context cleared"})

@app.get("/chat/providers")
async def get_chat_providers():
    """Get available providers for chat"""
    return JSONResponse({
        "status": "success",
        "providers": meeting_summarizer.get_available_providers(),
        "current_provider": meeting_summarizer.llm_manager.current_provider_name
    })
@app.post("/chat/clear-context")
async def clear_chat_context(data: dict):
    """Clear the chat context for a session"""
    session_id = data.get("session_id", "default")
    if session_id in session_contexts:
        del session_contexts[session_id]
    return JSONResponse({"status": "success", "message": "Context cleared"})

@app.get("/chat/providers")
async def get_chat_providers():
    """Get available providers for chat"""
    return JSONResponse({
        "status": "success",
        "providers": meeting_summarizer.get_available_providers(),
        "current_provider": meeting_summarizer.llm_manager.current_provider_name
    })

# ORIGINAL CHAT ENDPOINT (for backward compatibility)

@app.post("/chat")
async def chat_with_llm(data: dict):
    """Chat with local LLM (Ollama)"""
    try:
        if not llm_available:
            raise HTTPException(
                status_code=503, 
                detail="LLM service is not available. Please ensure Ollama is installed and running with 'ollama serve'"
            )
        
        message = data.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        message = message.strip()
        
        try:
            response = llm.invoke(message)
            
            if isinstance(response, str):
                response = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response)
                response = re.sub(r'\^[A-Z]', '', response)
                
                unwanted_phrases = [
                    "Certainly! Here's a clear and concise response",
                    "You are a helpful assistant",
                    "Please provide a clear and concise response",
                    "User:",
                    "Assistant:",
                    "Human:",
                    "Response:",
                    "Answer:",
                ]
                
                for phrase in unwanted_phrases:
                    response = response.replace(phrase, "")
                
                response = re.sub(r'\n{2,}', '\n', response)
                response = re.sub(r' {2,}', ' ', response)
                response = response.strip()
                
                if len(response) < 2:
                    response = llm.invoke(message)
                    response = response.strip()
            
        except Exception as e:
            error_msg = str(e)
            if "memory" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail=f"Not enough memory. Try a smaller model: ollama pull qwen:0.5b"
                )
            else:
                raise HTTPException(status_code=500, detail=f"Ollama error: {error_msg}")
        
        return JSONResponse({
            "status": "success",
            "response": response,
            "model": model_name
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download transcribed file"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/plain"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = "not available"
    ollama_models = []
    
    if llm_available:
        try:
            test_response = llm("test")
            ollama_status = "ready"
            
            import subprocess
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    for line in lines[1:]:
                        if line.strip():
                            model_info = line.split()
                            if model_info:
                                ollama_models.append(model_info[0])
        except:
            ollama_status = "error"
    
    return JSONResponse({
        "status": "healthy",
        "whisper_model": "loaded",
        "llm_available": llm_available,
        "ollama_status": ollama_status,
        "ollama_models": ollama_models,
        "device": device
    })

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multimodal Transcription API", 
        "version": "1.0.0",
        "endpoints": {
            "transcription": [
                "POST /transcribe/audio",
                "POST /transcribe/video", 
                "POST /transcribe/youtube"
            ],
            "analysis": [
                "POST /analyze/url"
            ],
            "meeting": [
                "POST /meeting/summarize",
                "GET /meeting/providers",
                "POST /meeting/switch-provider"
            ],
            "chat": [
                "POST /chat",
                "POST /chat/context",  # Add this
                "POST /chat/clear-context",  # Add this
                "GET /chat/providers"  # Add this
            ],
            "utility": [
                "GET /health",
                "GET /download/{filename}"
            ]
        }
    }
# Initialize Ollama for local chat
try:
    from langchain.llms import Ollama
    
    preferred_models = [
        'tinyllama:latest',
        'qwen:0.5b',
        'gemma:2b',
        'phi:latest',
    ]
    
    model_name = None
    
    import subprocess
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            available_models = result.stdout.lower()
            print(f"Available Ollama models:\n{result.stdout}")
            
            for model in preferred_models:
                model_base = model.split(':')[0]
                if model_base in available_models:
                    model_name = model
                    print(f"Selected model: {model_name}")
                    break
            
            if not model_name:
                print("No preferred models found. Please install tinyllama:")
                print("ollama pull tinyllama")
                model_name = 'tinyllama:latest'
    except:
        model_name = 'tinyllama:latest'
    
    llm = Ollama(
        model=model_name,
        temperature=0.7,
        num_ctx=2048,
        verbose=False,
    )
    llm_available = True
    print(f"LLM initialized with model: {model_name}")
    
    try:
        test_response = llm.invoke("Hello")
        print(f"Model test successful")
    except Exception as e:
        print(f"Model test failed: {e}")
        llm_available = False
    
except Exception as e:
    print(f"Could not initialize Ollama: {e}")
    llm_available = False

# Suppress warnings
import warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

try:
    import absl.logging
    absl.logging.set_verbosity(absl.logging.ERROR)
except:
    pass

print("\nRegistered endpoints:")
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        print(f"{route.methods} {route.path}")

if __name__ == "__main__":
    import uvicorn
    print(f"\nStarting server on http://localhost:8000")
    print(f"Using device: {device}")
    print(f"LLM available: {llm_available}")
    if llm_available:
        print(f"Ollama model: {model_name}")
    else:
        print("To enable chat functionality:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Pull a model: ollama pull tinyllama")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)