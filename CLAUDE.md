# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Map-Doc Automation Project

## Project Overview
Production-ready podcast post-production workflow automation with multi-language support and cost-optimized AI content generation.

**Status**: Phase 2 Complete - Multi-service architecture with ~75% cost optimization
**Current**: Ready for Phase 3 (RAG entity verification)

## Current Workflow Analysis
Based on valuebell-transcriber codebase:

### What Works Well
- ElevenLabs integration for high-quality transcription
- Speaker diarization and word-level timestamps
- Multiple output formats (TXT, SRT, JSON)
- Modular architecture with separate services

### Production Workflow (Phase 2 Complete)
1. **Manual Script Execution**: Run `python main.py` when ready to process
2. **Multi-Language Input**: Provide URL, episode info, and select language (Hebrew/English/etc)
3. **Multi-Provider Download**: Download from Google Drive, Dropbox, or WeTransfer
4. **ElevenLabs Transcription**: High-quality transcription with speaker diarization
5. **Multi-Service AI Generation**: Cost-optimized content generation with 3 specialized services
6. **Comprehensive Output**: Episode titles, descriptions, quotes, reel suggestions, tags, content warnings

## Implementation Status

### Phase 1: Core Improvements ✅ COMPLETED
**Goal**: Multi-language support, enhanced user input, professional naming

**Completed Features**:
- Renamed mapdog.py → content_generator.py for professionalism
- Added comprehensive language support (Hebrew, English, etc.)
- Enhanced user input collection (show, host, guest, episode number)
- Implemented 5 viral title generation options
- Fixed JSON parsing with markdown extraction

### Phase 2: Model Optimization ✅ COMPLETED
**Goal**: Cost-optimized multi-service architecture

**Completed Architecture**:
- **HighAccuracyContentService**: Gemini 2.5 Pro + thinking for quotes, reel suggestions, content warnings
- **CreativeContentService**: Gemini 2.5 Flash for titles, descriptions, summaries
- **SimpleTasksService**: Gemini 2.5 Flash-Lite for tags and basic formatting
- **ContentOrchestrator**: Coordinates all services with comprehensive error handling

**Results**: ~75% cost reduction while maintaining quality, zero generation errors

### Phase 3: Entity Verification (PENDING)
**Goal**: RAG-based entity verification and advanced features

**Planned Components**:
- LangChain + WebSearch RAG implementation
- Name/entity verification with confidence scoring
- RAG-based guest bio generation

## Current File Structure (Phase 2)
```
map-doc-automation/
├── main.py                           # Main script entry point
├── services/
│   ├── download.py                   # Multi-provider file download (Google Drive, Dropbox, WeTransfer)
│   ├── transcription.py              # ElevenLabs integration with language support
│   ├── audio_service.py              # Audio processing and conversion
│   ├── content_generator.py          # Legacy single-service generator (Phase 1)
│   ├── accuracy_service.py           # High-accuracy content (Gemini 2.5 Pro + thinking)
│   ├── creative_service.py           # Creative content (Gemini 2.5 Flash)
│   ├── simple_tasks_service.py       # Simple tasks (Gemini 2.5 Flash-Lite)
│   └── content_orchestrator.py       # Multi-service coordinator
├── processors/
│   └── transcript_processor.py       # Quality analysis and enhancement
├── utils/
│   ├── file_utils.py                 # File operations and source detection
│   └── format_utils.py               # Timestamp and output formatting
├── config/
│   └── settings.py                   # Application constants
├── requirements.txt                  # Python dependencies
├── .env                             # API keys (ElevenLabs, Gemini)
├── ENHANCEMENT_PLAN.md              # Phase tracking and documentation
└── output/                          # Local output folder
    ├── downloads/                   # Original downloaded files
    ├── temp/                        # Processed audio files
    ├── transcripts/                 # TXT, SRT, and JSON transcript files
    └── map-docs/                    # Generated content (JSON and markdown)
```

## Key Capabilities (Phase 2 Complete)

### Multi-Language Content Generation
- **Hebrew**: Native support with proper token allocation
- **English**: Full support for all content types
- **Other Languages**: Extensible language system

### Cost-Optimized AI Architecture
- **~75% cost reduction** vs single Pro model
- **Perfect quality maintenance** across all content types
- **Smart model routing** based on accuracy requirements

### Content Types Generated
- **5 viral episode titles** with compelling hooks
- **Comprehensive episode descriptions** (no hashtags)
- **3-4 verified quotes** with perfect accuracy
- **1-2 reel suggestions** with verified timestamps
- **10+ relevant tags** for discoverability
- **Content warnings** for appropriate filtering
- **Episode summaries** and key topics

### Technical Features
- **Multi-provider downloads**: Google Drive, Dropbox, WeTransfer
- **Speaker diarization**: ElevenLabs transcription with speaker identification
- **Quality analysis**: Transcript confidence scoring and validation
- **Comprehensive error handling**: Robust validation across all services
- **Multiple output formats**: JSON and markdown files

## Usage
```bash
# Run the main workflow
python main.py

# The script will prompt for:
# - File URL (Google Drive, Dropbox, or WeTransfer)
# - Episode information (name, show, host, guest)
# - Language selection (Hebrew, English, etc.)
# - File type (Video .mp4 or Audio .mp3)
```

## Next Phase
Ready for **Phase 3: RAG Entity Verification** to add:
- Web search-based entity verification
- Guest bio generation with sources
- Enhanced accuracy for names and titles

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