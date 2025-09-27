#!/usr/bin/env python3
"""
Map-Doc Automation Script
Main entry point for the podcast post-production workflow
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our services
from services.download import download_file_from_source
from services.transcription import TranscriptionService
from services.mapdog import MapDocService
from services.audio_service import process_audio_file, get_audio_duration
from utils.file_utils import clean_filename, get_base_filename, is_audio_file, is_video_file, detect_file_source

def main():
    """Main entry point"""
    print("🎧 Map-Doc Automation Script")
    print("=" * 50)

    # Check API keys
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')

    if not elevenlabs_key:
        print("❌ ELEVENLABS_API_KEY not found in .env file")
        return

    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return

    # Get URL from user (supports multiple cloud providers)
    file_url = input("Enter file URL (Google Drive, Dropbox, WeTransfer): ").strip()

    if not file_url:
        print("❌ No URL provided. Exiting.")
        return

    # Get episode name
    episode_name = input("Enter episode name: ").strip()
    if not episode_name:
        episode_name = "untitled_episode"

    print(f"📁 Processing: {file_url}")
    print(f"📝 Episode: {episode_name}")

    try:
        # Step 1: Download file
        clean_name = clean_filename(episode_name)

        # Detect file source and download appropriately
        source_type = detect_file_source(file_url)
        print(f"🔍 Detected source: {source_type}")

        # Determine file extension (or use generic)
        download_path = f"output/downloads/{clean_name}_source"

        print("\n" + "="*50)
        print("STEP 1: DOWNLOADING FILE")
        print("="*50)

        downloaded_file = download_file_from_source(file_url, download_path, source_type)

        # Step 2: Audio Processing
        print("\n" + "="*50)
        print("STEP 2: AUDIO PROCESSING")
        print("="*50)

        if not (is_audio_file(downloaded_file) or is_video_file(downloaded_file)):
            print("❌ Downloaded file is not audio or video format")
            return

        # Get audio duration before conversion
        audio_duration = get_audio_duration(downloaded_file)
        if audio_duration:
            print(f"📊 Audio duration: {audio_duration:.2f} seconds ({audio_duration/60:.1f} minutes)")

        # Process audio file (convert to optimal format)
        temp_dir = "output/temp"
        processed_audio = process_audio_file(downloaded_file, temp_dir, clean_name)

        # Step 3: Transcribe
        print("\n" + "="*50)
        print("STEP 3: TRANSCRIPTION")
        print("="*50)

        transcription_service = TranscriptionService(elevenlabs_key)
        response = transcription_service.transcribe_audio(processed_audio)
        transcript_text, words_data, response_dict = transcription_service.extract_transcription_data(response)

        # Analyze transcript quality
        from processors.transcript_processor import analyze_transcript_quality, count_unique_speakers
        quality_warnings = analyze_transcript_quality(words_data, audio_duration)

        # Save transcript
        transcript_dir = "output/transcripts"
        txt_path, json_path = transcription_service.save_transcript(
            transcript_text, words_data, transcript_dir, clean_name
        )

        # Display quality analysis
        unique_speakers_count = count_unique_speakers(words_data)
        print(f"📊 Speakers detected: {unique_speakers_count}")

        if quality_warnings:
            print("\n".join(quality_warnings))

        # Step 4: Generate map-doc
        print("\n" + "="*50)
        print("STEP 4: MAP-DOC GENERATION")
        print("="*50)

        mapdog_service = MapDocService(gemini_key)

        # Get optional episode info
        guest = input("Guest name (optional): ").strip()
        show = input("Show name (optional): ").strip()

        episode_info = {}
        if guest:
            episode_info['guest'] = guest
        if show:
            episode_info['show'] = show

        map_doc_data = mapdog_service.generate_map_doc(transcript_text, episode_info)

        # Save map-doc
        mapdog_dir = "output/map-docs"
        json_path, md_path = mapdog_service.save_map_doc(map_doc_data, mapdog_dir, clean_name)

        print("\n" + "="*50)
        print("✅ PROCESSING COMPLETE!")
        print("="*50)
        print(f"📄 Transcript: {txt_path}")
        print(f"📋 Map-doc: {md_path}")
        print(f"🎤 Speakers detected: {unique_speakers_count}")
        if audio_duration:
            print(f"⏱️ Audio duration: {audio_duration/60:.1f} minutes")

        # Show reel suggestions
        reels = map_doc_data.get('reels', [])
        if reels:
            print(f"\n🎬 Found {len(reels)} reel suggestions:")
            for i, reel in enumerate(reels, 1):
                print(f"  {i}. {reel.get('title', 'Untitled')} ({reel.get('start_time', '00:00')} - {reel.get('end_time', '00:00')})")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()