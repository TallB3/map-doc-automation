# Map-Doc Automation Enhancement Plan

## Project Overview
Comprehensive enhancement of the map-doc automation project to support multi-language content generation, cost optimization, and entity verification.

## Current Status
- **Phase**: 2 (Model Optimization) ⚠️ IMPLEMENTATION COMPLETE, QUALITY ISSUES IDENTIFIED
- **Start Date**: 2025-09-28
- **Last Updated**: 2025-09-30

## Phase Breakdown

### Phase 1: Core Improvements ✅ COMPLETED
**Goal**: Rename service, add language support, enhance user input, implement multi-title generation

**Tasks**:
- [x] Create enhancement tracking document
- [x] Clean up existing asset folders
- [x] Explain LangChain + Web Search RAG architecture
- [x] Rename mapdog.py → content_generator.py
- [x] Add language parameter throughout pipeline
- [x] Enhance user input collection (show, host, guest, episode number)
- [x] Implement multi-title generation (5 viral options)
- [x] Update main.py integration

**Completed**: 2025-09-28

**Changes Made**:
- Renamed `MapDocService` → `ContentGeneratorService`
- Added comprehensive language support (English, Hebrew, other languages)
- Enhanced user input: show name, host name, guest names, episode number
- Implemented 5 viral title generation with format: "Guest: Summary - #Episode"
- Added comprehensive JSON structure with all new elements
- Updated main.py with enhanced workflow

**Testing Requirements**: ✅ Completed - JSON parsing issue fixed and tested with Hebrew transcript

**Post-Completion Fix**:
- **Issue Found**: Gemini API returns JSON wrapped in markdown code blocks (```json ... ```)
- **Fix Applied**: Added robust JSON parsing with markdown extraction
- **Testing**: Successfully tested with existing Hebrew transcript from Meirav Bahat interview
- **Verification**: All content elements generated correctly in Hebrew
- **Status**: ✅ Ready for Phase 2

### Phase 2: Model Optimization ⚠️ IMPLEMENTATION COMPLETE, QUALITY ASSURANCE REQUIRED
**Goal**: Implement cost-optimized model routing

**Implementation Tasks**:
- [x] Split JSON generation by accuracy requirements
- [x] Implement model routing (Pro/Flash/Flash-Lite)
- [x] Add response validation
- [x] Performance testing and cost analysis

**Architecture Implemented**:
- **HighAccuracyContentService**: Gemini 2.5 Pro + thinking for quotes, reel suggestions, content warnings
- **CreativeContentService**: Gemini 2.5 Flash for titles, descriptions, summaries
- **SimpleTasksService**: Gemini 2.5 Flash-Lite for tags and basic formatting
- **ContentOrchestrator**: Coordinates all services with comprehensive error handling

**Cost Optimization Results**:
- **~75% cost reduction** vs single Pro model approach
- **Hebrew language support** with proper token allocation
- **Technical architecture functioning** as designed

**Technical Solutions**:
- Fixed Hebrew token requirements (3072 tokens for Creative service)
- Implemented comprehensive debugging and error handling
- Added proper response validation for all services
- Split complex JSON generation into focused micro-services

**⚠️ QUALITY ISSUES IDENTIFIED**:
- **Timestamp accuracy problems**: Generated timestamps may not match actual content
- **Quote fabrication**: Some quotes appear to be paraphrased or invented rather than exact transcriptions
- **Non-functioning elements**: Several content generation components not working properly
- **Production readiness**: System requires extensive testing before production use

**Quality Assurance Tasks** (PENDING):
- [ ] Comprehensive accuracy testing with multiple transcripts
- [ ] Timestamp verification against actual audio content
- [ ] Quote authenticity validation
- [ ] Element functionality testing
- [ ] Production readiness assessment
- [ ] Error rate analysis across different content types

**Status**: ⚠️ Technical implementation complete, quality assurance required before Phase 3

### Phase 2.5: Quality Assurance (CURRENT PRIORITY)
**Goal**: Ensure production-ready quality and accuracy

**Critical Testing Tasks**:
- [ ] Run system with 5+ different podcast transcripts
- [ ] Manually verify timestamp accuracy for each reel suggestion
- [ ] Validate that quotes are word-for-word from transcripts (no paraphrasing)
- [ ] Test all content generation elements for functionality
- [ ] Document error rates and failure patterns
- [ ] Create quality benchmarks and acceptance criteria
- [ ] Fix identified accuracy issues
- [ ] Implement timestamp validation system
- [ ] Add quote verification against original transcript

**Acceptance Criteria for Phase 2 Completion**:
- 95%+ timestamp accuracy for reel suggestions
- 100% quote authenticity (exact transcription)
- All content elements functioning properly
- Comprehensive error handling for edge cases
- Production deployment readiness

### Phase 3: Entity Verification (BLOCKED - PENDING PHASE 2.5)
**Goal**: Implement RAG-based entity verification

**Tasks**:
- [ ] Implement LangChain + WebSearch RAG
- [ ] Add name/entity verification
- [ ] Include confidence scoring
- [ ] RAG-based guest bio generation

**Prerequisites**: Phase 2.5 quality assurance must be completed first

### Phase 4: Hebrew Prompt Integration (PENDING)
**Goal**: Add all Hebrew prompt elements and platform-specific formatting

**Tasks**:
- [ ] Add content warning system
- [ ] Implement platform-specific timestamps (YouTube/Spotify)
- [ ] Add quotable moments extraction
- [ ] Add teaser recommendations
- [ ] Implement editing instructions

## Model Selection Strategy

### High-Accuracy Tasks (Gemini 2.5 Pro - $2.50/M tokens)
- Timestamp accuracy for reel suggestions
- Content warnings detection
- Critical accuracy requirements

### Balanced Tasks (Gemini 2.5 Flash - $0.625/M tokens)
- Episode titles and descriptions
- Social media content
- Key topics extraction

### Simple Tasks (Gemini 2.5 Flash-Lite - $0.25/M tokens)
- Basic formatting
- Simple translations
- Tag generation

## Enhanced Elements List

### Core Episode Data
1. **Multiple Title Options** - 5 viral options with format: "Guest: Viral Summary - #Episode"
2. **Platform-Specific Descriptions** - YouTube vs Spotify optimized
3. **Episode Summary** - Brief episode overview
4. **Key Topics** - Main discussion points
5. **Guest Bio** - RAG-verified, not transcript-inferred
6. **Show/Host/Guest Info** - Properly collected metadata

### Content Generation
7. **Platform-Specific Timestamps** - YouTube vs Spotify formats
8. **Quotable Moments** - 5 short quotes for social media
9. **Reel Suggestions** - 3 viral shorts with editing instructions
10. **Teaser Recommendations** - 2 multi-clip viral teasers
11. **Social Media Content** - Platform-specific posts
12. **Tags** - Relevant hashtags

### Quality Control
13. **Content Warnings** - Inappropriate content detection
14. **Entity Verification** - RAG-based name/title verification

## Language Support
- **Input**: User selects language during processing
- **Transcription**: Language passed to ElevenLabs API
- **Generation**: Language specified in Gemini prompts
- **Output**: All content generated in specified language

## File Structure Changes
```
services/
├── content_generator.py    # Renamed from mapdog.py
├── transcription.py        # Enhanced with language support
├── download.py
├── audio_service.py
└── entity_verification.py # NEW - RAG implementation
```

## Testing Protocol
After each phase:
1. User runs complete pipeline test
2. Verify all new features work correctly
3. Check output quality and format
4. Explicit approval required before next phase

## Quality Standards
- **Zero tolerance for timestamp inaccuracies** - All timestamps must be verified against source audio
- **100% quote authenticity required** - No paraphrasing or fabrication allowed
- **All names/entities must be RAG-verified** - Not inferred from transcripts
- **Production-ready error handling** - System must gracefully handle all edge cases
- **Cost optimization without quality compromise** - Efficiency cannot come at expense of accuracy
- **Hebrew/multi-language support throughout** - Full localization required

## Current Priorities
1. **Phase 2.5 Quality Assurance** - Critical testing and validation before any new features
2. **Accuracy verification systems** - Automated validation of timestamps and quotes
3. **Production readiness assessment** - Comprehensive evaluation of system reliability

---
*This document will be updated after each phase completion. Current focus: Quality over speed.*