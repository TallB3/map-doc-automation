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
from services.content_generator import ContentGeneratorService
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

    # Get file type (like valuebell-transcriber)
    print("\nFile type:")
    print("1. Video File (.mp4)")
    print("2. Audio File (.mp3)")
    file_type_choice = input("Select file type (1 or 2, default: 1): ").strip()

    if file_type_choice == "2":
        file_extension = ".mp3"
        file_type = "Audio File"
    else:
        file_extension = ".mp4"
        file_type = "Video File"

    # Get language (like valuebell-transcriber)
    print("\nLanguage:")
    print("1. English (en)")
    print("2. Hebrew (he)")
    print("3. Other (specify)")
    language_choice = input("Select language (1, 2, or 3, default: 1): ").strip()

    if language_choice == "2":
        language = "he"
        language_name = "Hebrew"
    elif language_choice == "3":
        language = input("Enter language code (e.g., es, fr, de): ").strip()
        language_name = language
        if not language:
            language = "en"
            language_name = "English"
    else:
        language = "en"
        language_name = "English"

    # Get number of speakers
    print("\nNumber of speakers:")
    num_speakers_input = input("Enter expected number of speakers (e.g., 2 for interview, 3 for panel, default: auto-detect): ").strip()

    if num_speakers_input and num_speakers_input.isdigit():
        num_speakers = int(num_speakers_input)
        print(f"👥 Will optimize for {num_speakers} speakers")
    else:
        num_speakers = None
        print("👥 Will auto-detect number of speakers")

    print(f"📁 Processing: {file_url}")
    print(f"📝 Episode: {episode_name}")
    print(f"🎬 File type: {file_type}")
    print(f"🌐 Language: {language_name} ({language})")
    if num_speakers:
        print(f"👥 Expected speakers: {num_speakers}")

    try:
        # Step 1: Download file
        clean_name = clean_filename(episode_name)

        # Detect file source and download appropriately
        source_type = detect_file_source(file_url)
        print(f"🔍 Detected source: {source_type}")

        # Determine file extension based on user input
        download_path = f"output/downloads/{clean_name}_source{file_extension}"

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
        response = transcription_service.transcribe_audio(processed_audio, language_code=language, num_speakers=num_speakers)
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

        # Step 4: Generate comprehensive content
        print("\n" + "="*50)
        print("STEP 4: EPISODE CONTENT GENERATION")
        print("="*50)

        content_service = ContentGeneratorService(gemini_key)

        # Get enhanced episode info
        print("Episode Information (enhanced metadata collection):")
        show = input("Show name: ").strip()
        host = input("Host name: ").strip()
        guest = input("Guest name(s): ").strip()
        episode_number = input("Episode number (optional): ").strip()
        notes = input("Additional notes (optional): ").strip()

        episode_info = {
            'show': show if show else 'Unknown Show',
            'host': host if host else 'Unknown Host',
            'guest': guest if guest else 'Unknown Guest',
            'episode_number': episode_number if episode_number else 'Unknown',
            'notes': notes if notes else 'None'
        }

        content_data = content_service.generate_content(transcript_text, episode_info, language)

        # Save content
        content_dir = "output/map-docs"
        json_path, md_path = content_service.save_content(content_data, content_dir, clean_name)

        print("\n" + "="*50)
        print("✅ PROCESSING COMPLETE!")
        print("="*50)
        print(f"📄 Transcript: {txt_path}")
        print(f"📋 Episode Content: {md_path}")
        print(f"🎤 Speakers detected: {unique_speakers_count}")
        print(f"🌐 Language: {language_name} ({language})")
        if audio_duration:
            print(f"⏱️ Audio duration: {audio_duration/60:.1f} minutes")

        # Show episode title options
        titles = content_data.get('episode_titles', [])
        if titles:
            print(f"\n📝 Generated {len(titles)} title options:")
            for i, title in enumerate(titles, 1):
                print(f"  {i}. {title}")

        # Show reel suggestions
        reels = content_data.get('reel_suggestions', [])
        if reels:
            print(f"\n🎬 Found {len(reels)} reel suggestions:")
            for i, reel in enumerate(reels, 1):
                print(f"  {i}. {reel.get('title', 'Untitled')} ({reel.get('start_time', '00:00')} - {reel.get('end_time', '00:00')})")

        # Show content warnings if any
        warnings = content_data.get('content_warnings', [])
        if warnings:
            print(f"\n⚠️  Content warnings detected:")
            for warning in warnings:
                print(f"  - {warning}")

        # Show quotable moments
        quotes = content_data.get('quotable_moments', [])
        if quotes:
            print(f"\n💬 Found {len(quotes)} quotable moments for social media")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()