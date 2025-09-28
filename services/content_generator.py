"""
Enhanced content generation service for podcast episodes
"""
import os
import json
import re
from google import genai

class ContentGeneratorService:
    """Enhanced service for generating comprehensive podcast content using Gemini API"""

    def __init__(self, api_key):
        """Initialize Gemini client"""
        self.client = genai.Client(api_key=api_key)

    def generate_content(self, transcript_text, episode_info=None, language="en"):
        """
        Generate comprehensive episode content from transcript using Gemini API

        Args:
            transcript_text: The full transcript text
            episode_info: Dict with episode metadata (show, host, guest, episode_number, etc.)
            language: Language code for content generation (en, he, etc.)

        Returns:
            dict: Generated comprehensive content with all elements
        """
        print(f"🧠 Generating comprehensive episode content with Gemini ({language})...")

        # Build enhanced prompt
        prompt = self._build_comprehensive_prompt(transcript_text, episode_info, language)

        try:
            # Use Gemini 2.5 Pro with thinking capabilities for better accuracy
            from google.genai.types import GenerateContentConfig

            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=GenerateContentConfig(
                    temperature=0.1,  # Lower temperature for more accurate, consistent outputs
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192,
                    response_mime_type="application/json"  # Request JSON format
                )
            )

            # Extract and parse JSON from response
            content_data = self._parse_json_response(response.text)
            return content_data

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print(f"Raw response: {response.text[:500]}...")
            # Fallback: return minimal structure
            return {
                "error": "Failed to parse AI response",
                "raw_response": response.text,
                "episode_titles": [],
                "reels": []
            }
        except Exception as e:
            print(f"⚠️ Unexpected error during content generation: {e}")
            return {
                "error": f"Content generation failed: {str(e)}",
                "episode_titles": [],
                "reels": []
            }

    def _build_comprehensive_prompt(self, transcript_text, episode_info, language):
        """Build comprehensive prompt for episode content generation"""

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
- Additional Notes: {episode_info.get('notes', 'None')}
"""

        # Determine output language instructions
        language_instruction = self._get_language_instruction(language)

        prompt = f"""You are an expert podcast editor and content strategist. Create comprehensive episode content for this podcast.

{info_text}

**TRANSCRIPT:**
{transcript_text}

**INSTRUCTIONS:**
{language_instruction}

Generate a JSON response with the following structure:

{{
    "content_warnings": ["List any inappropriate content that should be flagged"],
    "episode_titles": [
        "Guest Name: Viral Summary - #Episode",
        "Guest Name: Different Viral Angle - #Episode",
        "Guest Name: Another Compelling Hook - #Episode",
        "Guest Name: Fourth Option - #Episode",
        "Guest Name: Fifth Creative Title - #Episode"
    ],
    "platform_descriptions": {{
        "youtube": "Description optimized for YouTube discovery",
        "spotify": "Description optimized for Spotify"
    }},
    "episode_summary": "Brief episode overview",
    "key_topics": ["topic1", "topic2", "topic3"],
    "guest_bio_placeholder": "NOTE: Guest bio will be generated via RAG verification in Phase 3",
    "platform_timestamps": {{
        "youtube": [
            "HH:MM:SS Chapter Title",
            "HH:MM:SS Another Chapter"
        ],
        "spotify": [
            "(HH:MM:SS) Chapter Title",
            "(HH:MM:SS) Another Chapter"
        ]
    }},
    "quotable_moments": [
        {{
            "quote": "Exact impactful quote from transcript",
            "timestamp": "MM:SS",
            "context": "Brief context for the quote"
        }}
    ],
    "reel_suggestions": [
        {{
            "title": "Viral reel title",
            "description": "Why this would make a good reel",
            "start_time": "MM:SS",
            "end_time": "MM:SS",
            "hook": "Opening sentence to grab attention",
            "closing": "Closing sentence for the reel",
            "editing_instructions": "Specific instructions for video editor"
        }}
    ],
    "teaser_recommendations": [
        {{
            "title": "Multi-clip teaser title",
            "clips": [
                {{"start": "MM:SS", "end": "MM:SS", "reason": "Why this clip"}}
            ],
            "editing_style": "Fast cuts, dramatic music, etc."
        }}
    ],
    "social_media": {{
        "instagram_caption": "Caption for Instagram post",
        "twitter_thread": ["Tweet 1", "Tweet 2", "Tweet 3"],
        "linkedin_post": "Professional LinkedIn post"
    }},
    "tags": ["hashtag1", "hashtag2", "hashtag3"]
}}

**CRITICAL REQUIREMENTS:**
- Generate exactly 5 episode title options following the format: "Guest Name: Viral Summary - #Episode"
- Ensure timestamps are ABSOLUTELY ACCURATE - zero tolerance for errors
- Find 3 viral reel suggestions (30-90 seconds each)
- Create 2 teaser recommendations with multiple clips
- Extract 5 quotable moments perfect for social media
- Platform-specific formatting for timestamps (YouTube vs Spotify)
- Include detailed editing instructions for each reel
"""

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
        # Look for ```json ... ``` patterns
        json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_pattern, response_text, re.DOTALL | re.IGNORECASE)

        if matches:
            # Try to parse each match
            for match in matches:
                try:
                    cleaned_json = match.strip()
                    return json.loads(cleaned_json)
                except json.JSONDecodeError:
                    continue

        # If no markdown blocks found, try to find JSON-like content
        # Look for content between { and } (this is more risky but can work)
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

    def save_content(self, content_data, output_dir, base_filename):
        """Save generated content to files"""
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON
        json_path = os.path.join(output_dir, f"{base_filename}_content.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)

        # Save human-readable markdown
        md_path = os.path.join(output_dir, f"{base_filename}_content.md")
        markdown_content = self._format_as_markdown(content_data)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"✅ Saved episode content to {json_path}")
        print(f"✅ Saved markdown to {md_path}")

        return json_path, md_path

    def _format_as_markdown(self, data):
        """Format comprehensive content data as readable markdown"""
        # Handle episode titles (multiple options)
        titles_section = "## Episode Title Options\n"
        for i, title in enumerate(data.get('episode_titles', []), 1):
            titles_section += f"{i}. {title}\n"

        md = f"""# Episode Content Generation Report

{titles_section}

## Content Warnings
"""
        warnings = data.get('content_warnings', [])
        if warnings:
            for warning in warnings:
                md += f"⚠️ {warning}\n"
        else:
            md += "✅ No content warnings detected\n"

        md += f"""

## Platform Descriptions

### YouTube
{data.get('platform_descriptions', {}).get('youtube', 'No YouTube description')}

### Spotify
{data.get('platform_descriptions', {}).get('spotify', 'No Spotify description')}

## Episode Summary
{data.get('episode_summary', 'No summary available')}

## Key Topics
"""
        for topic in data.get('key_topics', []):
            md += f"- {topic}\n"

        # Platform-specific timestamps
        md += "\n## Chapter Timestamps\n\n### YouTube Format\n"
        youtube_chapters = data.get('platform_timestamps', {}).get('youtube', [])
        for chapter in youtube_chapters:
            md += f"- {chapter}\n"

        md += "\n### Spotify Format\n"
        spotify_chapters = data.get('platform_timestamps', {}).get('spotify', [])
        for chapter in spotify_chapters:
            md += f"- {chapter}\n"

        # Quotable moments
        md += "\n## Quotable Moments\n"
        for i, moment in enumerate(data.get('quotable_moments', []), 1):
            md += f"""
### Quote {i} ({moment.get('timestamp', '00:00')})
> "{moment.get('quote', 'No quote')}"

*Context: {moment.get('context', 'No context')}*
"""

        # Reel suggestions
        md += "\n## Reel Suggestions\n"
        for i, reel in enumerate(data.get('reel_suggestions', []), 1):
            md += f"""
### Reel {i}: {reel.get('title', 'Untitled')}
- **Time**: {reel.get('start_time', '00:00')} - {reel.get('end_time', '00:00')}
- **Hook**: "{reel.get('hook', 'No hook provided')}"
- **Closing**: "{reel.get('closing', 'No closing provided')}"
- **Why**: {reel.get('description', 'No description')}
- **Editing**: {reel.get('editing_instructions', 'No instructions')}
"""

        # Teaser recommendations
        md += "\n## Teaser Recommendations\n"
        for i, teaser in enumerate(data.get('teaser_recommendations', []), 1):
            md += f"\n### Teaser {i}: {teaser.get('title', 'Untitled')}\n"
            md += f"**Style**: {teaser.get('editing_style', 'No style specified')}\n\n**Clips**:\n"
            for clip in teaser.get('clips', []):
                md += f"- {clip.get('start', '00:00')} - {clip.get('end', '00:00')}: {clip.get('reason', 'No reason')}\n"

        # Social media content
        md += "\n## Social Media Content\n"
        social = data.get('social_media', {})
        if social.get('instagram_caption'):
            md += f"\n### Instagram Caption\n{social['instagram_caption']}\n"

        if social.get('twitter_thread'):
            md += f"\n### Twitter Thread\n"
            for i, tweet in enumerate(social['twitter_thread'], 1):
                md += f"{i}. {tweet}\n"

        if social.get('linkedin_post'):
            md += f"\n### LinkedIn Post\n{social['linkedin_post']}\n"

        if data.get('tags'):
            md += f"\n## Tags\n{' '.join(['#' + tag for tag in data['tags']])}\n"

        return md