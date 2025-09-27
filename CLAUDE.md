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