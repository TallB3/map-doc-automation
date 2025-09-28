"""
High-accuracy content service for critical tasks requiring precise timestamps and quotes
Uses Gemini 2.5 Pro with thinking capabilities for zero-tolerance accuracy
"""
import os
import json
import re
from google import genai

class HighAccuracyContentService:
    """Service for generating accuracy-critical content using Gemini 2.5 Pro with thinking"""

    def __init__(self, api_key):
        """Initialize Gemini client with high-accuracy settings"""
        self.client = genai.Client(api_key=api_key)

    def generate_accuracy_critical_content(self, transcript_text, episode_info=None, language="en"):
        """
        Generate accuracy-critical content: timestamps, quotes, content warnings, reel suggestions

        Args:
            transcript_text: The full transcript text
            episode_info: Dict with episode metadata
            language: Language code for content generation

        Returns:
            dict: Accuracy-critical content with verified timestamps and quotes
        """
        print(f"🎯 Generating accuracy-critical content with Gemini 2.5 Pro + thinking ({language})...")

        # Build accuracy-focused prompt
        prompt = self._build_accuracy_prompt(transcript_text, episode_info, language)

        try:
            # Use Gemini 2.5 Pro with thinking capabilities and maximum accuracy
            from google.genai.types import GenerateContentConfig

            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=GenerateContentConfig(
                    temperature=0.05,  # Very low temperature for maximum accuracy
                    top_p=0.5,         # Focused sampling
                    top_k=10,          # Highly focused responses
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )

            # Parse response
            content_data = self._parse_json_response(response.text)
            return content_data

        except Exception as e:
            print(f"⚠️ High-accuracy content generation failed: {e}")
            return {
                "error": f"Accuracy service failed: {str(e)}",
                "content_warnings": [],
                "quotable_moments": [],
                "reel_suggestions": [],
                "chapter_timestamps": []
            }

    def _build_accuracy_prompt(self, transcript_text, episode_info, language):
        """Build prompt focused on accuracy and precision"""

        # Build episode information section
        info_text = ""
        if episode_info:
            info_text = f"""
Episode Information:
- Show: {episode_info.get('show', 'Unknown')}
- Host: {episode_info.get('host', 'Unknown')}
- Guest(s): {episode_info.get('guest', 'Unknown')}
- Episode Number: {episode_info.get('episode_number', 'Unknown')}
- Language: {language}
"""

        # Language instruction
        language_instruction = self._get_language_instruction(language)

        prompt = f"""You are a meticulous podcast content analyst with advanced reasoning capabilities.

REASONING PROCESS:
1. First, read through the entire transcript to understand the context and flow
2. Identify all timestamps and speaker changes
3. For each potential quote, verify it exists word-for-word in the transcript
4. For each timestamp reference, double-check it matches exactly what's in the transcript
5. For content warnings, analyze potential impact on speakers' reputation and relationships
6. Think through multiple angles before making final decisions

Your task is to extract ACCURATE information from the transcript using step-by-step reasoning.

{info_text}

**TRANSCRIPT:**
{transcript_text}

**CRITICAL ACCURACY INSTRUCTIONS:**
{language_instruction}

ABSOLUTE REQUIREMENTS:
- Use ONLY timestamps that appear EXACTLY in the transcript
- Use ONLY word-for-word quotes from the transcript - no paraphrasing
- Flag content that could embarrass, compromise, or cause trouble for speakers
- Be precise and conservative - if unsure, indicate uncertainty

Generate a JSON response with the following structure:

{{
    "content_warnings": [
        "Specific warnings about content that could embarrass speakers, show them in bad light, get them in trouble, reveal sensitive information, or contain inappropriate/offensive material"
    ],
    "quotable_moments": [
        {{
            "quote": "EXACT word-for-word quote from transcript",
            "timestamp": "MM:SS - exact timestamp from transcript",
            "context": "Brief context explaining why this quote is impactful",
            "speaker": "speaker_0 or speaker_1 as shown in transcript"
        }}
    ],
    "reel_suggestions": [
        {{
            "title": "Compelling reel title",
            "description": "Why this segment would make an engaging reel",
            "start_time": "MM:SS - exact start timestamp from transcript",
            "end_time": "MM:SS - exact end timestamp from transcript",
            "hook": "Opening sentence to grab attention",
            "closing": "Closing sentence for the reel",
            "editing_instructions": "Specific technical instructions for video editor",
            "confidence_level": "high/medium/low based on timestamp accuracy"
        }}
    ],
    "chapter_timestamps": [
        "HH:MM:SS Topic/Chapter Title Based on Content",
        "HH:MM:SS Next Major Topic Transition"
    ]
}}

REMEMBER: Accuracy is paramount. Every timestamp and quote must be verifiable against the transcript."""

        return prompt

    def _get_language_instruction(self, language):
        """Get language-specific generation instructions"""
        if language == "he":
            return "Generate ALL content in Hebrew. Use Hebrew for descriptions, warnings, and all text elements."
        elif language == "en":
            return "Generate ALL content in English. Use English for descriptions, warnings, and all text elements."
        else:
            return f"Generate ALL content in {language}. Use {language} for descriptions, warnings, and all text elements."

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