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

    def transcribe_audio(self, audio_file_path, language_code="en", diarize=True):
        """
        Transcribe audio file using ElevenLabs API

        Args:
            audio_file_path: Path to the audio file
            language_code: Language code for transcription
            diarize: Whether to perform speaker diarization

        Returns:
            Transcription response object with text and words
        """
        print(f"🎙️ Transcribing audio with ElevenLabs...")

        with open(audio_file_path, "rb") as audio_file_object:
            response = self.client.speech_to_text.convert(
                file=audio_file_object,
                model_id="scribe_v1_experimental",
                language_code=language_code,
                diarize=diarize,
                tag_audio_events=False,
                timestamps_granularity="word"
            )

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