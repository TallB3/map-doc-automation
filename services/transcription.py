"""
ElevenLabs transcription service
Adapted from valuebell-transcriber
"""
import os
import json
from elevenlabs.client import ElevenLabs
import httpx

class TranscriptionService:
    """Service for handling ElevenLabs transcription"""

    def __init__(self, api_key):
        """Initialize the transcription service with API key"""
        self.api_key = api_key
        custom_timeout = httpx.Timeout(60.0, read=900.0, connect=10.0)
        self.client = ElevenLabs(api_key=api_key, timeout=custom_timeout)

    def transcribe_audio(self, audio_file_path, language_code="en", diarize=True, num_speakers=None):
        """
        Transcribe audio file using ElevenLabs API

        Args:
            audio_file_path: Path to the audio file
            language_code: Language code for transcription
            diarize: Whether to perform speaker diarization
            num_speakers: Expected number of speakers (None for auto-detect)

        Returns:
            Transcription response object with text and words
        """
        print(f"🎙️ Transcribing audio with ElevenLabs...")
        if num_speakers:
            print(f"👥 Optimizing for {num_speakers} speakers...")

        # Build API parameters
        api_params = {
            "file": None,  # Will be set below
            "model_id": "scribe_v1_experimental",
            "language_code": language_code,
            "diarize": diarize,
            "tag_audio_events": False,
            "timestamps_granularity": "word"
        }

        # Add num_speakers if specified
        if num_speakers:
            api_params["num_speakers"] = num_speakers

        with open(audio_file_path, "rb") as audio_file_object:
            api_params["file"] = audio_file_object
            response = self.client.speech_to_text.convert(**api_params)

        return response

    def extract_transcription_data(self, response):
        """
        Extract text and words data from transcription response

        Args:
            response: ElevenLabs transcription response

        Returns:
            tuple: (full_transcript_text, words_data, response_dict)
        """
        full_transcript_text = ""
        words_data = []

        if hasattr(response, 'text'):
            full_transcript_text = response.text
        if hasattr(response, 'words'):
            words_data = response.words

        # Convert to dictionary for caching
        response_dict = response.model_dump()

        return full_transcript_text, words_data, response_dict

    def save_transcript_with_timestamps(self, transcript_text, words_data, output_dir, base_filename):
        """
        Save transcript with enhanced timestamp management (every 15 minutes)

        Args:
            transcript_text: The full transcript text
            words_data: List of word objects with timestamps
            output_dir: Directory to save files
            base_filename: Base name for files

        Returns:
            tuple: (txt_path, json_path)
        """
        os.makedirs(output_dir, exist_ok=True)

        # Generate enhanced transcript with periodic timestamps
        enhanced_transcript = self._generate_enhanced_transcript(words_data)

        # Save enhanced TXT
        txt_path = os.path.join(output_dir, f"{base_filename}_transcript.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(self._format_transcript_header())
            f.write(enhanced_transcript)

        # Save JSON
        json_path = os.path.join(output_dir, f"{base_filename}_raw_transcript.json")
        transcript_data = {
            "text": transcript_text,
            "words": [word.model_dump() if hasattr(word, 'model_dump') else word for word in words_data],
            "enhanced_transcript": enhanced_transcript
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved enhanced transcript to {txt_path}")
        print(f"✅ Saved raw data to {json_path}")

        return txt_path, json_path

    def _get_word_attr(self, word, attr, default=None):
        """Get attribute from word object or dictionary"""
        # Try object attribute first (for ElevenLabs API response objects)
        if hasattr(word, attr):
            return getattr(word, attr, default)
        # Try dictionary access (for JSON loaded data)
        elif isinstance(word, dict):
            return word.get(attr, default)
        # Fallback
        return default

    def _generate_enhanced_transcript(self, words_data):
        """Generate transcript with periodic timestamps every 15 seconds"""
        if not words_data:
            return "No transcript data available"

        transcript_lines = []
        current_speaker = None
        current_time = None
        current_sentence = []
        last_forced_timestamp = 0  # Track when we last forced a timestamp (in seconds)

        for word in words_data:
            word_text = self._get_word_attr(word, 'text', str(word))
            word_start = self._get_word_attr(word, 'start', 0)
            word_speaker = self._get_word_attr(word, 'speaker_id', 'speaker_0')

            # Check if we need to add periodic timestamp (every 15 seconds)
            if word_start - last_forced_timestamp >= 15:
                if current_sentence:  # Finish current sentence first
                    speaker_text = ' '.join(current_sentence)
                    timestamp = self._format_time(current_time)
                    transcript_lines.append(f"[{timestamp}] {current_speaker}:")
                    transcript_lines.append(f"{speaker_text}")
                    transcript_lines.append("")
                    current_sentence = []

                # Add periodic timestamp marker
                forced_timestamp = self._format_time(word_start)
                transcript_lines.append(f"[{forced_timestamp}] [15-second marker]")
                transcript_lines.append("")
                last_forced_timestamp = word_start

                # Reset current_time to the current word's timestamp to ensure proper continuation
                current_time = word_start

            # Check for speaker change
            if word_speaker != current_speaker:
                # Finish previous speaker's sentence
                if current_sentence and current_speaker:
                    speaker_text = ' '.join(current_sentence)
                    timestamp = self._format_time(current_time if current_time is not None else word_start)
                    transcript_lines.append(f"[{timestamp}] {current_speaker}:")
                    transcript_lines.append(f"{speaker_text}")
                    transcript_lines.append("")

                # Start new speaker
                current_speaker = word_speaker
                current_time = word_start
                current_sentence = [word_text]
            else:
                # Same speaker, add to current sentence
                current_sentence.append(word_text)

        # Add final sentence
        if current_sentence and current_speaker:
            speaker_text = ' '.join(current_sentence)
            timestamp = self._format_time(current_time if current_time is not None else 0)
            transcript_lines.append(f"[{timestamp}] {current_speaker}:")
            transcript_lines.append(f"{speaker_text}")

        return '\n'.join(transcript_lines)

    def _format_time(self, seconds):
        """Format seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _format_transcript_header(self):
        """Generate transcript header with disclaimer"""
        return """⚠️  TRANSCRIPT DISCLAIMER ⚠️
This transcript was generated using AI technology and may contain errors,
inaccuracies, or misinterpretations. Please review and verify the content
before using it for any official, legal, or critical purposes.
Generated by: Map-Doc Automation
═══════════════════════════════════════════════════════════════════════════

"""

    def save_transcript(self, transcript_text, words_data, output_dir, base_filename):
        """Save transcript in multiple formats with enhanced speaker processing"""
        from processors.transcript_processor import group_words_by_speaker
        from utils.format_utils import format_txt_timestamp, format_srt_time
        from utils.file_utils import get_word_attr, generate_output_filenames
        from config.settings import TRANSCRIPT_DISCLAIMER, MAX_CUE_DURATION_SECONDS, MAX_CUE_CHARACTERS

        os.makedirs(output_dir, exist_ok=True)
        filenames = generate_output_filenames(base_filename)

        # Generate enhanced TXT transcript with speaker identification
        txt_content = TRANSCRIPT_DISCLAIMER
        if words_data:
            speaker_segments = group_words_by_speaker(words_data)
            for segment in speaker_segments:
                txt_content += f"[{format_txt_timestamp(segment['start_time'])}] {segment['speaker']}:\n"
                txt_content += f"{' '.join(segment['text_parts'])}\n\n"
        else:
            txt_content += transcript_text

        # Save TXT file
        txt_path = os.path.join(output_dir, filenames['txt'])
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)

        # Generate SRT subtitles
        srt_content = self._generate_srt_subtitles(words_data)

        # Save SRT file (if content exists)
        srt_path = None
        if srt_content:
            srt_path = os.path.join(output_dir, filenames['srt'])
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)

        # Save JSON with word-level data
        json_path = os.path.join(output_dir, filenames['json'])
        transcript_data = {
            "text": transcript_text,
            "words": [word.model_dump() if hasattr(word, 'model_dump') else word for word in words_data]
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved transcript to {txt_path}")
        if srt_path:
            print(f"✅ Saved SRT subtitles to {srt_path}")
        print(f"✅ Saved JSON data to {json_path}")

        return txt_path, json_path

    def _generate_srt_subtitles(self, words_data):
        """Generate SRT format subtitles with speaker identification"""
        from utils.file_utils import get_word_attr
        from utils.format_utils import format_srt_time
        from config.settings import MAX_CUE_DURATION_SECONDS, MAX_CUE_CHARACTERS

        if not words_data:
            return ""

        srt_cues = []
        cue_number = 1
        current_cue_words_info = []
        current_cue_speaker = None
        current_cue_start_time = None

        for word_obj in words_data:
            word_text_val = get_word_attr(word_obj, 'text')
            word_start_val = get_word_attr(word_obj, 'start')
            word_end_val = get_word_attr(word_obj, 'end')
            speaker_id_val = get_word_attr(word_obj, 'speaker_id', "speaker_unknown")

            if not (word_text_val and word_start_val is not None and word_end_val is not None):
                continue

            finalize_current_cue = False

            if not current_cue_words_info:
                current_cue_speaker = speaker_id_val
                current_cue_start_time = word_start_val
            elif (speaker_id_val != current_cue_speaker or
                    (word_end_val - current_cue_start_time) > MAX_CUE_DURATION_SECONDS or
                    len(" ".join([w['text'] for w in current_cue_words_info] + [word_text_val])) > MAX_CUE_CHARACTERS):
                finalize_current_cue = True

            if finalize_current_cue and current_cue_words_info:
                cue_text_str = " ".join([w['text'] for w in current_cue_words_info])
                srt_cues.append(
                    f"{cue_number}\n"
                    f"{format_srt_time(current_cue_start_time)} --> {format_srt_time(current_cue_words_info[-1]['end_time'])}\n"
                    f"{current_cue_speaker}: {cue_text_str}\n"
                )
                cue_number += 1
                current_cue_words_info = []
                current_cue_speaker = speaker_id_val
                current_cue_start_time = word_start_val

            current_cue_words_info.append({'text': word_text_val, 'end_time': word_end_val})

        # Handle final cue
        if current_cue_words_info:
            cue_text_str = " ".join([w['text'] for w in current_cue_words_info])
            srt_cues.append(
                f"{cue_number}\n"
                f"{format_srt_time(current_cue_start_time)} --> {format_srt_time(current_cue_words_info[-1]['end_time'])}\n"
                f"{current_cue_speaker}: {cue_text_str}\n"
            )

        return "\n".join(srt_cues)