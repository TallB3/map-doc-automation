"""
Gemini API service for generating map-docs
"""
import os
import json
from google import genai

class MapDocService:
    """Service for generating map-docs using Gemini API"""

    def __init__(self, api_key):
        """Initialize Gemini client"""
        self.client = genai.Client(api_key=api_key)

    def generate_map_doc(self, transcript_text, episode_info=None):
        """
        Generate map-doc from transcript using Gemini API

        Args:
            transcript_text: The full transcript text
            episode_info: Optional dict with episode metadata (guest, show, etc.)

        Returns:
            dict: Generated map-doc content with reels suggestions
        """
        print(f"🧠 Generating map-doc with Gemini...")

        # Build prompt
        prompt = self._build_map_doc_prompt(transcript_text, episode_info)

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            # Parse response as JSON
            map_doc_data = json.loads(response.text)
            return map_doc_data

        except json.JSONDecodeError:
            # Fallback: return as text if not valid JSON
            return {
                "map_doc": response.text,
                "reels": []
            }

    def _build_map_doc_prompt(self, transcript_text, episode_info):
        """Build the prompt for map-doc generation"""

        info_text = ""
        if episode_info:
            info_text = f"""
Episode Information:
- Guest: {episode_info.get('guest', 'Unknown')}
- Show: {episode_info.get('show', 'Unknown')}
- Additional Notes: {episode_info.get('notes', 'None')}
"""

        prompt = f"""You are an expert podcast editor and content strategist. Create a comprehensive map-doc for this podcast episode.

{info_text}

**TRANSCRIPT:**
{transcript_text}

**INSTRUCTIONS:**
Generate a JSON response with the following structure:

{{
    "episode_title": "Suggested episode title",
    "description": "Episode description for platforms",
    "summary": "Brief episode summary",
    "key_topics": ["topic1", "topic2", "topic3"],
    "guest_bio": "Brief guest biography if applicable",
    "reels": [
        {{
            "title": "Suggested reel title",
            "description": "Why this would make a good reel",
            "start_time": "timestamp in format MM:SS",
            "end_time": "timestamp in format MM:SS",
            "hook": "Opening sentence to grab attention",
            "closing": "Closing sentence for the reel"
        }}
    ],
    "social_media": {{
        "instagram_caption": "Caption for Instagram post",
        "twitter_thread": ["Tweet 1", "Tweet 2", "Tweet 3"],
        "linkedin_post": "Professional LinkedIn post"
    }},
    "tags": ["hashtag1", "hashtag2", "hashtag3"]
}}

Focus on finding 3-5 high-impact moments that would work well as short-form content (30-90 seconds each).
Make sure timestamps are accurate and refer to engaging, standalone moments.
"""

        return prompt

    def save_map_doc(self, map_doc_data, output_dir, base_filename):
        """Save map-doc to files"""
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON
        json_path = os.path.join(output_dir, f"{base_filename}_mapdog.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(map_doc_data, f, ensure_ascii=False, indent=2)

        # Save human-readable markdown
        md_path = os.path.join(output_dir, f"{base_filename}_mapdog.md")
        markdown_content = self._format_as_markdown(map_doc_data)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"✅ Saved map-doc to {json_path}")
        print(f"✅ Saved markdown to {md_path}")

        return json_path, md_path

    def _format_as_markdown(self, data):
        """Format map-doc data as readable markdown"""
        md = f"""# {data.get('episode_title', 'Episode Map-Doc')}

## Description
{data.get('description', 'No description available')}

## Summary
{data.get('summary', 'No summary available')}

## Key Topics
"""
        for topic in data.get('key_topics', []):
            md += f"- {topic}\n"

        if data.get('guest_bio'):
            md += f"\n## Guest Bio\n{data['guest_bio']}\n"

        md += "\n## Reel Suggestions\n"
        for i, reel in enumerate(data.get('reels', []), 1):
            md += f"""
### Reel {i}: {reel.get('title', 'Untitled')}
- **Time**: {reel.get('start_time', '00:00')} - {reel.get('end_time', '00:00')}
- **Hook**: "{reel.get('hook', 'No hook provided')}"
- **Closing**: "{reel.get('closing', 'No closing provided')}"
- **Why**: {reel.get('description', 'No description')}
"""

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