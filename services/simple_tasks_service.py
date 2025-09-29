"""
Simple tasks service for basic operations like tags and formatting
Uses Gemini 2.5 Flash-Lite for maximum cost efficiency
"""
import os
import json
import re
from google import genai

class SimpleTasksService:
    """Service for simple tasks using Gemini 2.5 Flash-Lite"""

    def __init__(self, api_key):
        """Initialize Gemini client with efficient settings"""
        self.client = genai.Client(api_key=api_key)

    def generate_simple_content(self, transcript_text, episode_info=None, language="en"):
        """
        Generate simple content: tags, basic formatting, simple extractions

        Args:
            transcript_text: The full transcript text
            episode_info: Dict with episode metadata
            language: Language code for content generation

        Returns:
            dict: Simple content elements
        """
        print(f"⚡ Generating simple content with Gemini 2.5 Flash-Lite ({language})...")

        # Build simple prompt
        prompt = self._build_simple_prompt(transcript_text, episode_info, language)

        try:
            # Use Gemini 2.5 Flash-Lite with efficiency settings
            from google.genai.types import GenerateContentConfig

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",  # Note: Flash-Lite may not be available, using Flash as fallback
                contents=prompt,
                config=GenerateContentConfig(
                    temperature=0.3,   # Lower temperature for consistent output
                    top_p=0.8,         # Focused but not too narrow
                    top_k=20,          # Limited options for efficiency
                    max_output_tokens=2048,  # Increased for long content processing
                    response_mime_type="application/json"
                )
            )

            # Validate response
            if not hasattr(response, 'text') or response.text is None or response.text.strip() == "":
                raise ValueError("Response text is None or empty - model may have been blocked by safety filters, failed to generate content, or hit token limits")

            # Parse response
            content_data = self._parse_json_response(response.text)
            return content_data

        except Exception as e:
            print(f"⚠️ Simple tasks generation failed: {e}")
            return {
                "error": f"Simple tasks service failed: {str(e)}",
                "tags": [],
                "guest_bio_placeholder": "NOTE: Guest bio will be generated via RAG verification in Phase 3"
            }

    def format_timestamps(self, chapter_timestamps):
        """
        Format timestamps for different platforms

        Args:
            chapter_timestamps: List of timestamps in format "HH:MM:SS Title"

        Returns:
            dict: Platform-specific formatted timestamps
        """
        try:
            youtube_format = []
            spotify_format = []

            for timestamp in chapter_timestamps:
                if timestamp.strip():
                    # YouTube format: "HH:MM:SS Title"
                    youtube_format.append(timestamp)

                    # Spotify format: "(HH:MM:SS) Title"
                    if timestamp.startswith("(") and ")" in timestamp:
                        spotify_format.append(timestamp)
                    else:
                        # Convert from YouTube to Spotify format
                        parts = timestamp.split(" ", 1)
                        if len(parts) == 2:
                            time_part, title_part = parts
                            spotify_format.append(f"({time_part}) {title_part}")
                        else:
                            spotify_format.append(f"({timestamp})")

            return {
                "platform_timestamps": {
                    "youtube": youtube_format,
                    "spotify": spotify_format
                }
            }

        except Exception as e:
            print(f"⚠️ Timestamp formatting failed: {e}")
            return {
                "platform_timestamps": {
                    "youtube": chapter_timestamps,
                    "spotify": chapter_timestamps
                }
            }

    def _build_simple_prompt(self, transcript_text, episode_info, language):
        """Build prompt for simple tasks"""

        # Build episode information section
        info_text = ""
        if episode_info:
            info_text = f"""
Episode Information:
- Show: {episode_info.get('show', 'Unknown')}
- Guest(s): {episode_info.get('guest', 'Unknown')}
- Language: {language}
"""

        # Language instruction
        language_instruction = self._get_language_instruction(language)

        prompt = f"""You are an efficient content processor. Extract simple information quickly and accurately.

{info_text}

**TRANSCRIPT:**
{transcript_text}

**SIMPLE TASK INSTRUCTIONS:**
{language_instruction}

Generate a JSON response with the following structure:

{{
    "tags": [
        "relevant hashtag without #",
        "topic keyword",
        "guest name",
        "show name",
        "industry term",
        "main theme"
    ],
    "guest_bio_placeholder": "NOTE: Guest bio will be generated via RAG verification in Phase 3"
}}

Focus on: Relevant keywords, industry terms, topics discussed, people mentioned, and concepts covered."""

        return prompt

    def _get_language_instruction(self, language):
        """Get language-specific generation instructions"""
        if language == "he":
            return "Generate tags in Hebrew."
        elif language == "en":
            return "Generate tags in English."
        else:
            return f"Generate tags in {language}."

    def _parse_json_response(self, response_text):
        """Parse JSON from AI response, handling markdown code blocks"""

        # First, try to parse as raw JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # If that fails, try to extract JSON from markdown code blocks
        json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_pattern, response_text, re.DOTALL | re.IGNORECASE)

        if matches:
            for match in matches:
                try:
                    cleaned_json = match.strip()
                    return json.loads(cleaned_json)
                except json.JSONDecodeError:
                    continue

        # If no markdown blocks found, try to find JSON-like content
        json_start = response_text.find('{')
        json_end = response_text.rfind('}')

        if json_start != -1 and json_end != -1 and json_end > json_start:
            try:
                potential_json = response_text[json_start:json_end+1]
                return json.loads(potential_json)
            except json.JSONDecodeError:
                pass

        # If all parsing attempts fail, raise an exception
        raise json.JSONDecodeError(f"Could not extract valid JSON from response", response_text, 0)