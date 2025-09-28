# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Map-Doc Automation Project

## Project Overview
Local script development for Valuebell's podcast post-production workflow automation.

**Approach**: Start with a simple local script that runs manually, then gradually add features and automation.

## Current Workflow Analysis
Based on valuebell-transcriber codebase:

### What Works Well
- ElevenLabs integration for high-quality transcription
- Speaker diarization and word-level timestamps
- Multiple output formats (TXT, SRT, JSON)
- Modular architecture with separate services

### Target Local Script Workflow
1. **Manual Script Execution**: Run script when ready to process
2. **URL Input**: Provide public Google Drive URL for media file
3. **Download & Transcribe**: Download file, generate transcript using ElevenLabs
4. **Map-Doc Generation**: Send transcript to Gemini API for map-doc + reel suggestions JSON
5. **Clip Cutting**: Use FFmpeg to cut suggested clips based on timestamps
6. **Local Output**: Save all files locally in organized folders

## Revised Implementation Plan

### Phase 1: Basic Script (Week 1)
**Goal**: Manual script that downloads, transcribes, and generates map-doc

**Components**:
1. Simple CLI script that prompts for Google Drive URL
2. Download public Google Drive files
3. Reuse transcription logic from valuebell-transcriber
4. Basic Gemini API integration for map-doc generation

**What you'll need**:
- ElevenLabs API key (you have this)
- Google AI Studio API key for Gemini
- Python environment setup

### Phase 2: Content Processing (Week 2)
**Goal**: Add clip cutting and better output organization

**Components**:
1. FFmpeg integration for video/audio clip cutting
2. JSON parsing for reel suggestions with timestamps
3. Local folder organization (map-docs/, clips/, transcripts/)

**What you'll need**:
- FFmpeg installation
- Define reel suggestion JSON format

### Phase 3: Enhanced Features (Week 2-3)
**Goal**: Polish and optimize the local workflow

**Components**:
1. Better error handling and logging
2. Support for different media formats
3. Quality checks and validation
4. Configuration file for settings

## Simple File Structure
```
map-doc-automation/
├── main.py                 # Main script entry point
├── services/
│   ├── download.py         # Google Drive public file download
│   ├── transcription.py    # ElevenLabs integration (from valuebell-transcriber)
│   ├── mapdog.py          # Gemini API for map-doc generation
│   └── clips.py           # FFmpeg clip cutting
├── utils/
│   └── file_utils.py      # Helper functions
├── requirements.txt
├── .env                   # API keys
└── output/                # Local output folder
    ├── transcripts/
    ├── map-docs/
    └── clips/
```

## Development Strategy
1. **Start Simple**: Basic download → transcribe → map-doc pipeline
2. **Test Each Step**: Verify each component works before adding the next
3. **Local First**: No cloud automation until local script is solid
4. **Manual Triggers**: Run when you want, provide inputs as needed
5. **Iterative**: Add features one at a time, test thoroughly

## Immediate Next Steps
1. Set up git repository
2. Create basic project structure
3. Start with simple download + transcription test
4. Get your Gemini API key ready

Ready to start building?

---

# Claude Code Technical Reference

## Key Commands

### Running the Application
```bash
python main.py
```
The main script runs interactively, prompting for:
- File URL (supports Google Drive, Dropbox, WeTransfer)
- Episode name
- File type selection (Video .mp4 or Audio .mp3)
- Optional guest and show information

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
ELEVENLABS_API_KEY=your_elevenlabs_key
GEMINI_API_KEY=your_gemini_key
```

### Testing Individual Components
Since this is a monolithic script, test components by running the main script with different file types and sources.

## Architecture Overview

### Core Workflow Pipeline
The application follows a 4-step linear pipeline:
1. **Download**: Multi-provider file download (`services/download.py`)
2. **Audio Processing**: Format conversion and optimization (`services/audio_service.py`)
3. **Transcription**: ElevenLabs speech-to-text with speaker diarization (`services/transcription.py`)
4. **Map-Doc Generation**: Gemini AI content generation (`services/mapdog.py`)

### Service Layer Architecture
- **`services/download.py`**: Handles Google Drive (gdown), Dropbox (direct conversion), and WeTransfer downloads
- **`services/transcription.py`**: ElevenLabs integration with speaker diarization, generates TXT, SRT, and JSON outputs
- **`services/mapdog.py`**: Gemini API client that generates structured JSON with episode metadata, reel suggestions, and social media content
- **`services/audio_service.py`**: FFmpeg wrapper for audio/video processing and format conversion

### Data Processing Architecture
- **`processors/transcript_processor.py`**: Quality analysis, speaker grouping, and transcript enhancement
- **`utils/file_utils.py`**: File operations, source detection, and filename handling
- **`utils/format_utils.py`**: Timestamp formatting and output format utilities
- **`config/settings.py`**: Application constants and configuration

### Output Organization
All outputs are organized in `output/` with subdirectories:
- `downloads/`: Original downloaded files
- `temp/`: Processed audio files
- `transcripts/`: TXT, SRT, and JSON transcript files
- `map-docs/`: Generated map-doc JSON and markdown files

## Key Implementation Details

### Multi-Provider Download System
The download service auto-detects file sources and handles different authentication mechanisms:
- Google Drive: Uses `gdown` with fuzzy matching for public URLs
- Dropbox: Converts share URLs to direct download URLs
- WeTransfer: Scrapes download links with session handling

### ElevenLabs Integration
Uses `scribe_v1_experimental` model with:
- Word-level timestamps
- Speaker diarization
- Custom timeout handling (60s connect, 900s read)
- Multiple output formats (TXT with speaker identification, SRT subtitles, raw JSON)

### Gemini AI Map-Doc Generation
Structured prompt engineering generates JSON with:
- Episode metadata (title, description, summary)
- Reel suggestions with precise timestamps
- Social media content (Instagram, Twitter, LinkedIn)
- Content tags and topics

### Quality Analysis System
Transcript processor analyzes:
- Speaker detection and counting
- Audio duration vs transcript coverage
- Word-level confidence scoring
- Outlier detection for poor quality segments

### File Type Support
- **Audio**: .mp3, .wav, .m4a, .aac, .flac
- **Video**: .mp4, .avi, .mov, .mkv, .webm
- Auto-conversion to optimal formats for transcription

## Important Configuration

### API Requirements
- **ElevenLabs**: Speech-to-text transcription service
- **Gemini**: Content generation and analysis

### Audio Processing Settings
- Default sample rate: 16kHz (optimized for speech-to-text)
- Mono channel conversion for transcription
- MP3 conversion for files over 1GB
- High-quality bitrate: 320k for final outputs

### SRT Subtitle Generation
- Max cue duration: 7 seconds
- Max characters per cue: 120
- Speaker identification in subtitles

## Development Notes

### Error Handling Strategy
The application uses a fail-fast approach with comprehensive error messages. Each major step is isolated and logged separately.

### File Processing Pipeline
Files are processed through multiple stages with intermediate outputs preserved for debugging and quality control.

### Speaker Diarization
The system groups words by speaker and formats outputs with speaker identification. Quality warnings are displayed for transcripts with unclear speaker detection.

### Content Generation Prompt
The Gemini prompt is specifically engineered for podcast content, focusing on finding 3-5 high-impact moments suitable for 30-90 second short-form content.