"""
Chain Prompting Accuracy Service - Experimental approach for timestamp accuracy

This service tests if separating tasks into individual API calls improves accuracy
vs the current single-call approach that processes 6000+ tokens at once.

Key Innovation: Two-step chapter generation
- Step 1: Get chapter titles (no timestamps)
- Step 2: For each title, find its specific timestamp

This is Phase 0.5 - an experiment before building full RAG system.
"""

import json
import re
from google import genai
from google.genai.types import GenerateContentConfig


class ChainPromptingAccuracyService:
    """
    Service for generating accuracy-critical content using chain prompting architecture.

    Each task (quotes, reels, warnings, chapters) gets a separate, focused API call
    to improve accuracy and reduce cognitive load on the model.
    """

    def __init__(self, api_key):
        """Initialize Gemini client with high-accuracy settings"""
        self.client = genai.Client(api_key=api_key)

    def generate_accuracy_critical_content(self, transcript_text, episode_info=None, language="en"):
        """
        Generate accuracy-critical content using chain prompting architecture.

        Same signature as HighAccuracyContentService.generate_accuracy_critical_content
        for drop-in A/B testing compatibility.

        Args:
            transcript_text: The full transcript text
            episode_info: Dict with episode metadata
            language: Language code for content generation

        Returns:
            dict: Accuracy-critical content with verified timestamps and quotes
        """
        print(f"🔗 Generating accuracy-critical content with chain prompting ({language})...")

        try:
            # Execute each task as separate API call
            quotable_moments = self._generate_quotable_moments(transcript_text, language)
            reel_suggestions = self._generate_reel_suggestions(transcript_text, language)
            content_warnings = self._generate_content_warnings(transcript_text, language)
            chapter_timestamps = self._generate_chapter_timestamps(transcript_text, language)

            # Combine results
            return {
                "quotable_moments": quotable_moments,
                "reel_suggestions": reel_suggestions,
                "content_warnings": content_warnings,
                "chapter_timestamps": chapter_timestamps
            }

        except Exception as e:
            print(f"⚠️ Chain prompting content generation failed: {e}")
            return {
                "error": f"Chain prompting service failed: {str(e)}",
                "content_warnings": [],
                "quotable_moments": [],
                "reel_suggestions": [],
                "chapter_timestamps": []
            }

    def _generate_quotable_moments(self, transcript_text, language):
        """
        Generate quotable moments using focused prompt.
        Asks ONLY for quotes - no other tasks.

        Returns:
            list: Quotable moments with exact quotes and timestamps
        """
        language_instruction = self._get_language_instruction(language)

        prompt = f"""You are a meticulous podcast content analyst.

Your ONLY task: Find 3-4 quotable moments from this transcript.

**TRANSCRIPT:**
{transcript_text}

**CRITICAL ACCURACY INSTRUCTIONS:**
{language_instruction}

ABSOLUTE REQUIREMENTS:
- Use ONLY timestamps that appear EXACTLY in the transcript
- Use ONLY word-for-word quotes from the transcript - no paraphrasing
- Be precise and conservative

Generate a JSON response with this structure:

{{
    "quotable_moments": [
        {{
            "quote": "EXACT word-for-word quote from transcript",
            "timestamp": "MM:SS - exact timestamp from transcript",
            "context": "Brief context explaining why this quote is impactful",
            "speaker": "speaker_0 or speaker_1 as shown in transcript"
        }}
    ]
}}

REMEMBER: Focus ONLY on finding quotable moments. Accuracy is paramount."""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=self._get_accuracy_config()
        )

        result = self._parse_json_response(response.text)
        return result.get("quotable_moments", [])

    def _generate_reel_suggestions(self, transcript_text, language):
        """
        Generate reel suggestions using focused prompt.
        Asks ONLY for reel suggestions - no other tasks.

        Returns:
            list: Reel suggestions with exact timestamps
        """
        language_instruction = self._get_language_instruction(language)

        prompt = f"""You are a meticulous podcast content analyst specializing in short-form video content.

Your ONLY task: Find 1-2 segments suitable for 30-90 second reels/shorts.

**TRANSCRIPT:**
{transcript_text}

**CRITICAL ACCURACY INSTRUCTIONS:**
{language_instruction}

ABSOLUTE REQUIREMENTS:
- Use ONLY timestamps that appear EXACTLY in the transcript
- Find compelling, self-contained segments suitable for short-form video
- Each reel should be 30-90 seconds long
- Be precise with timestamps

Generate a JSON response with this structure:

{{
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
    ]
}}

REMEMBER: Focus ONLY on finding reel-worthy segments. Accuracy is paramount."""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=self._get_accuracy_config()
        )

        result = self._parse_json_response(response.text)
        return result.get("reel_suggestions", [])

    def _generate_content_warnings(self, transcript_text, language):
        """
        Generate content warnings using focused prompt.
        Asks ONLY for content warnings - no other tasks.

        Returns:
            list: Content warnings about potentially problematic content
        """
        language_instruction = self._get_language_instruction(language)

        prompt = f"""You are a meticulous podcast content analyst specializing in content moderation.

Your ONLY task: Identify content that could be problematic or require warnings.

**TRANSCRIPT:**
{transcript_text}

**CRITICAL ACCURACY INSTRUCTIONS:**
{language_instruction}

ABSOLUTE REQUIREMENTS:
- Flag content that could embarrass speakers
- Flag content that shows speakers in bad light
- Flag content that could get speakers in trouble
- Flag sensitive or inappropriate material
- Be conservative and thorough

Generate a JSON response with this structure:

{{
    "content_warnings": [
        "Specific warning about content that could cause issues"
    ]
}}

If no warnings are needed, return an empty array.

REMEMBER: Focus ONLY on identifying content warnings. Be thorough and conservative."""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=self._get_accuracy_config()
        )

        result = self._parse_json_response(response.text)
        return result.get("content_warnings", [])

    def _generate_chapter_timestamps(self, transcript_text, language):
        """
        Generate chapter timestamps using TWO-STEP CHAIN PROMPTING.

        This is the key innovation:
        Step 1: Get chapter titles (no timestamps)
        Step 2: For each title, find its specific timestamp

        Returns:
            list: Chapter strings in format "HH:MM:SS Topic Title"
        """
        # Step 1: Get chapter titles without timestamps
        titles = self._get_chapter_titles(transcript_text, language)

        # Step 2: For each title, find its specific timestamp
        chapters = []
        for title in titles:
            try:
                timestamp = self._find_chapter_timestamp(transcript_text, title, language)
                chapters.append(f"{timestamp} {title}")
            except Exception as e:
                print(f"⚠️ Could not find timestamp for chapter '{title}': {e}")
                # Skip chapters where we can't find accurate timestamps
                continue

        return chapters

    def _get_chapter_titles(self, transcript_text, language):
        """
        Step 1 of chapter generation: Get chapter titles WITHOUT timestamps.

        Returns:
            list: Chapter title strings (no timestamps)
        """
        language_instruction = self._get_language_instruction(language)

        prompt = f"""You are a meticulous podcast content analyst.

Your ONLY task: Identify 3-8 major topic transitions or chapters in this transcript.

**TRANSCRIPT:**
{transcript_text}

**CRITICAL ACCURACY INSTRUCTIONS:**
{language_instruction}

REQUIREMENTS:
- Identify major topic shifts or discussion themes
- Create clear, descriptive chapter titles
- DO NOT include timestamps yet - just the topic titles
- Focus on meaningful content divisions

Generate a JSON response with this structure:

{{
    "chapter_titles": [
        "Introduction and Welcome",
        "Main Topic Discussion",
        "Deep Dive into Specifics",
        "Q&A and Conclusion"
    ]
}}

REMEMBER: Provide ONLY the topic titles. No timestamps."""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=self._get_accuracy_config()
        )

        result = self._parse_json_response(response.text)
        return result.get("chapter_titles", [])

    def _find_chapter_timestamp(self, transcript_text, chapter_title, language):
        """
        Step 2 of chapter generation: Find timestamp for specific chapter title.

        Args:
            transcript_text: Full transcript
            chapter_title: Specific chapter title to find timestamp for
            language: Language code

        Returns:
            str: Timestamp in MM:SS or HH:MM:SS format
        """
        language_instruction = self._get_language_instruction(language)

        prompt = f"""You are a meticulous podcast content analyst.

Your ONLY task: Find the exact timestamp where this chapter/topic begins in the transcript.

**CHAPTER TITLE TO FIND:**
{chapter_title}

**TRANSCRIPT:**
{transcript_text}

**CRITICAL ACCURACY INSTRUCTIONS:**
{language_instruction}

REQUIREMENTS:
- Find the EXACT timestamp where this topic/chapter begins
- Use ONLY timestamps that appear in the transcript
- Look for where the discussion transitions to this topic
- Be precise and conservative

Generate a JSON response with this structure:

{{
    "timestamp": "MM:SS"
}}

REMEMBER: Provide ONLY the exact timestamp from the transcript."""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=self._get_accuracy_config()
        )

        result = self._parse_json_response(response.text)
        return result.get("timestamp", "00:00")

    def _get_accuracy_config(self):
        """
        Get Gemini configuration optimized for maximum accuracy.

        Returns:
            GenerateContentConfig: High-accuracy configuration
        """
        return GenerateContentConfig(
            temperature=0.05,  # Very low temperature for maximum accuracy
            top_p=0.5,         # Focused sampling
            top_k=10,          # Highly focused responses
            max_output_tokens=8192,
            response_mime_type="application/json"
        )

    def _get_language_instruction(self, language):
        """Get language-specific generation instructions"""
        if language == "he":
            return "Generate ALL content in Hebrew. Use Hebrew for descriptions, warnings, and all text elements."
        elif language == "en":
            return "Generate ALL content in English. Use English for descriptions, warnings, and all text elements."
        else:
            return f"Generate ALL content in {language}. Use {language} for descriptions, warnings, and all text elements."

    def _parse_json_response(self, response_text):
        """
        Parse JSON from AI response, handling markdown code blocks.
        Reused from HighAccuracyContentService for consistency.
        """
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
