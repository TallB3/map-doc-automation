"""
File utility functions
"""
import os
import re
from pathlib import Path

def clean_filename(filename):
    """Clean filename for safe file system usage"""
    # Remove file extension if present
    name = os.path.splitext(filename)[0]

    # Replace spaces and special characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)

    return name.strip('-').lower()

def get_file_extension(file_path):
    """Get file extension from path"""
    return os.path.splitext(file_path)[1].lower()

def is_audio_file(file_path):
    """Check if file is an audio format"""
    audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.flac']
    return get_file_extension(file_path) in audio_extensions

def is_video_file(file_path):
    """Check if file is a video format"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    return get_file_extension(file_path) in video_extensions

def ensure_directory(path):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
    return path

def get_base_filename(file_path):
    """Get base filename without extension"""
    return os.path.splitext(os.path.basename(file_path))[0]

def parse_timestamp(timestamp_str):
    """Parse timestamp string (MM:SS or HH:MM:SS) to seconds"""
    if not timestamp_str:
        return 0

    parts = timestamp_str.split(':')
    if len(parts) == 2:  # MM:SS
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        return 0

def seconds_to_timestamp(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def get_word_attr(word_item, attr_name, default=None):
    """Helper function to access word attributes flexibly"""
    if isinstance(word_item, dict):
        return word_item.get(attr_name, default)
    elif hasattr(word_item, attr_name):
        return getattr(word_item, attr_name, default)
    return default

def generate_output_filenames(base_name):
    """Generate output filenames for different formats"""
    return {
        'txt': f"{base_name}_transcript.txt",
        'srt': f"{base_name}_subtitles.srt",
        'json': f"{base_name}_raw_transcript.json"
    }