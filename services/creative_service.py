"""
Creative content service for flexible tasks like titles, descriptions, and social media
Uses Gemini 2.5 Flash for balanced cost and creativity
"""
import os
import json
import re
from google import genai

class CreativeContentService:
    """Service for generating creative content using Gemini 2.5 Flash"""

    def __init__(self, api_key):
        """Initialize Gemini client with balanced settings"""
        self.client = genai.Client(api_key=api_key)

    def generate_creative_content(self, transcript_text, episode_info=None, language="en"):
        """
        Generate creative content: titles, descriptions, social media content

        Args:
            transcript_text: The full transcript text
            episode_info: Dict with episode metadata
            language: Language code for content generation

        Returns:
            dict: Creative content for marketing and distribution
        """
        print(f"🎨 Generating creative content with Gemini 2.5 Flash ({language})...")

        # Build creativity-focused prompt
        prompt = self._build_creative_prompt(transcript_text, episode_info, language)

        try:
            # Use Gemini 2.5 Flash with balanced creativity settings
            from google.genai.types import GenerateContentConfig

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=GenerateContentConfig(
                    temperature=0.7,   # Higher temperature for creativity
                    top_p=0.9,         # More diverse sampling
                    top_k=40,          # Broader response options
                    max_output_tokens=6144,  # Increased for long Hebrew content
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
            print(f"⚠️ Creative content generation failed: {e}")
            return {
                "error": f"Creative service failed: {str(e)}",
                "episode_titles": [],
                "episode_description": "",
                "episode_summary": "",
                "key_topics": []
            }

    def _build_creative_prompt(self, transcript_text, episode_info, language):
        """Build prompt focused on creativity and engagement"""

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

        prompt = f"""You are a creative podcast marketing specialist. Generate compelling episode titles and descriptions.

{info_text}

**TRANSCRIPT:**
{transcript_text}

**INSTRUCTIONS:**
{language_instruction}

Create engaging, viral content that makes people want to listen. Focus on emotional hooks and clear value propositions.

Generate ONLY titles and descriptions in this JSON format:

{{
    "episode_titles": [
        "Guest Name: Compelling Hook That Makes People Want to Listen - #Episode",
        "Guest Name: Different Viral Angle That Stands Out - #Episode",
        "Guest Name: Third Creative Approach - #Episode",
        "Guest Name: Fourth Unique Perspective - #Episode",
        "Guest Name: Fifth Catchy Option - #Episode"
    ],
    "episode_description": "Single comprehensive and engaging description suitable for both YouTube and Spotify. Make it compelling and informative, highlighting key insights and value for listeners. NO hashtags at the end.",
    "episode_summary": "Brief, punchy episode overview that captures the essence and main value",
    "key_topics": [
        "Main Topic 1",
        "Key Theme 2",
        "Important Subject 3"
    ]
}}"""

        return prompt

    def _get_language_instruction(self, language):
        """Get language-specific generation instructions"""
        if language == "he":
            return "Generate ALL content in Hebrew. Use Hebrew for titles, descriptions, social media content, and all text elements."
        elif language == "en":
            return "Generate ALL content in English. Use English for titles, descriptions, social media content, and all text elements."
        else:
            return f"Generate ALL content in {language}. Use {language} for titles, descriptions, social media content, and all text elements."

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