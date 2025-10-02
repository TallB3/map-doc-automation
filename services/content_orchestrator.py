"""
Content Orchestrator - Coordinates all content generation services
Implements Phase 2 multi-service architecture with cost optimization
"""
import os
import json
from .accuracy_service import HighAccuracyContentService
from .accuracy_service_chain_prompting import ChainPromptingAccuracyService
from .creative_service import CreativeContentService
from .simple_tasks_service import SimpleTasksService

class ContentOrchestrator:
    """Orchestrates multiple content generation services for optimal cost and accuracy"""

    def __init__(self, api_key, use_chain_prompting=False):
        """
        Initialize all content generation services

        Args:
            api_key: Gemini API key
            use_chain_prompting: If True, use experimental ChainPromptingAccuracyService
                               If False (default), use original HighAccuracyContentService
        """
        # Choose accuracy service based on flag (Phase 0.5 A/B testing)
        if use_chain_prompting:
            self.accuracy_service = ChainPromptingAccuracyService(api_key)
            print("🔗 Using Chain Prompting Accuracy Service (Phase 0.5 Experiment)")
        else:
            self.accuracy_service = HighAccuracyContentService(api_key)
            print("🎯 Using Original High Accuracy Service")

        self.creative_service = CreativeContentService(api_key)
        self.simple_service = SimpleTasksService(api_key)
        self.use_chain_prompting = use_chain_prompting

    def generate_comprehensive_content(self, transcript_text, episode_info=None, language="en"):
        """
        Generate comprehensive episode content using optimized multi-service approach

        Args:
            transcript_text: The full transcript text
            episode_info: Dict with episode metadata
            language: Language code for content generation

        Returns:
            dict: Combined content from all services
        """
        print(f"🎯 Starting Phase 2 multi-service content generation ({language})...")
        print(f"📊 Cost optimization: Using targeted models for different accuracy requirements")

        results = {}
        errors = []

        # Step 1: High-accuracy content (Gemini 2.5 Pro + thinking)
        print("\n" + "="*60)
        print("STEP 1: HIGH-ACCURACY CONTENT (Gemini 2.5 Pro + Thinking)")
        print("="*60)
        try:
            accuracy_content = self.accuracy_service.generate_accuracy_critical_content(
                transcript_text, episode_info, language
            )
            if "error" not in accuracy_content:
                results.update(accuracy_content)
                print(f"✅ Generated {len(accuracy_content.get('quotable_moments', []))} verified quotes")
                print(f"✅ Generated {len(accuracy_content.get('reel_suggestions', []))} reel suggestions with verified timestamps")
                print(f"✅ Generated {len(accuracy_content.get('content_warnings', []))} content warnings")
            else:
                errors.append(f"Accuracy service: {accuracy_content['error']}")
        except Exception as e:
            errors.append(f"Accuracy service failed: {str(e)}")

        # Step 2: Creative content (Gemini 2.5 Flash)
        print("\n" + "="*60)
        print("STEP 2: CREATIVE CONTENT (Gemini 2.5 Flash)")
        print("="*60)
        try:
            creative_content = self.creative_service.generate_creative_content(
                transcript_text, episode_info, language
            )
            if "error" not in creative_content:
                results.update(creative_content)
                print(f"✅ Generated {len(creative_content.get('episode_titles', []))} viral title options")
                print(f"✅ Generated episode description (no hashtags)")
                print(f"✅ Generated {len(creative_content.get('teaser_recommendations', []))} teaser concepts")
            else:
                errors.append(f"Creative service: {creative_content['error']}")
        except Exception as e:
            errors.append(f"Creative service failed: {str(e)}")

        # Step 3: Simple tasks (Gemini 2.5 Flash for efficiency)
        print("\n" + "="*60)
        print("STEP 3: SIMPLE TASKS (Gemini 2.5 Flash - Efficient)")
        print("="*60)
        try:
            simple_content = self.simple_service.generate_simple_content(
                transcript_text, episode_info, language
            )
            if "error" not in simple_content:
                results.update(simple_content)
                print(f"✅ Generated {len(simple_content.get('tags', []))} relevant tags")
            else:
                errors.append(f"Simple tasks service: {simple_content['error']}")
        except Exception as e:
            errors.append(f"Simple tasks service failed: {str(e)}")

        # Step 4: Format timestamps (local processing)
        print("\n" + "="*60)
        print("STEP 4: TIMESTAMP FORMATTING (Local Processing)")
        print("="*60)
        try:
            if "chapter_timestamps" in results:
                timestamp_data = self.simple_service.format_timestamps(results["chapter_timestamps"])
                results.update(timestamp_data)
                print(f"✅ Formatted timestamps for YouTube and Spotify")
            else:
                print("⚠️ No chapter timestamps to format")
        except Exception as e:
            errors.append(f"Timestamp formatting failed: {str(e)}")

        # Step 5: Compile final results
        print("\n" + "="*60)
        print("STEP 5: COMPILATION & VALIDATION")
        print("="*60)

        # Add any missing required fields
        if "episode_titles" not in results:
            results["episode_titles"] = ["Title generation failed"]
        if "episode_description" not in results:
            results["episode_description"] = "Description generation failed"
        if "episode_summary" not in results:
            results["episode_summary"] = "Summary generation failed"
        if "key_topics" not in results:
            results["key_topics"] = ["Topics extraction failed"]

        # Add error summary if any errors occurred
        if errors:
            results["generation_errors"] = errors
            print(f"⚠️ {len(errors)} errors occurred during generation")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ All services completed successfully")

        # Add generation metadata
        accuracy_service_name = "Chain Prompting (Phase 0.5 Experiment)" if self.use_chain_prompting else "Gemini 2.5 Pro + Thinking"
        results["generation_metadata"] = {
            "phase": "Phase 2 - Multi-Service Architecture" + (" + Phase 0.5 Chain Prompting" if self.use_chain_prompting else ""),
            "services_used": {
                "accuracy": accuracy_service_name,
                "creative": "Gemini 2.5 Flash",
                "simple": "Gemini 2.5 Flash (Efficient)",
                "formatting": "Local Processing"
            },
            "cost_optimization": "~75% cost reduction vs single Pro model",
            "language": language,
            "chain_prompting_enabled": self.use_chain_prompting
        }

        print(f"\n🎉 Phase 2 content generation completed!")
        return results

    def save_content(self, content_data, output_dir, base_filename):
        """Save generated content to files with enhanced metadata"""
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON
        json_path = os.path.join(output_dir, f"{base_filename}_content_v2.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)

        # Save human-readable markdown
        md_path = os.path.join(output_dir, f"{base_filename}_content_v2.md")
        markdown_content = self._format_as_markdown(content_data)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"✅ Saved Phase 2 content to {json_path}")
        print(f"✅ Saved Phase 2 markdown to {md_path}")

        return json_path, md_path

    def _format_as_markdown(self, data):
        """Format Phase 2 content data as readable markdown"""

        # Generation metadata
        metadata = data.get('generation_metadata', {})
        services_info = ""
        if metadata:
            services_info = f"""
## Generation Info - {metadata.get('phase', 'Unknown Phase')}
- **Accuracy Service**: {metadata.get('services_used', {}).get('accuracy', 'Unknown')}
- **Creative Service**: {metadata.get('services_used', {}).get('creative', 'Unknown')}
- **Simple Tasks**: {metadata.get('services_used', {}).get('simple', 'Unknown')}
- **Cost Optimization**: {metadata.get('cost_optimization', 'Unknown')}
- **Language**: {metadata.get('language', 'Unknown')}
"""

        # Handle episode titles (multiple options)
        titles_section = "## Episode Title Options\n"
        for i, title in enumerate(data.get('episode_titles', []), 1):
            titles_section += f"{i}. {title}\n"

        md = f"""# Episode Content Generation Report - Phase 2

{services_info}

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

## Episode Description
{data.get('episode_description', 'No description available')}

## Episode Summary
{data.get('episode_summary', 'No summary available')}

## Key Topics
"""
        for topic in data.get('key_topics', []):
            md += f"- {topic}\n"

        # Platform-specific timestamps
        platform_timestamps = data.get('platform_timestamps', {})
        if platform_timestamps:
            md += "\n## Chapter Timestamps\n\n### YouTube Format\n"
            for chapter in platform_timestamps.get('youtube', []):
                md += f"- {chapter}\n"

            md += "\n### Spotify Format\n"
            for chapter in platform_timestamps.get('spotify', []):
                md += f"- {chapter}\n"
        else:
            # Fallback to legacy format
            md += "\n## Chapter Timestamps\n"
            for chapter in data.get('chapter_timestamps', []):
                md += f"- {chapter}\n"

        # Quotable moments
        md += "\n## Quotable Moments (Verified)\n"
        for i, moment in enumerate(data.get('quotable_moments', []), 1):
            confidence = moment.get('confidence_level', 'unknown')
            speaker = moment.get('speaker', 'unknown')
            md += f"""
### Quote {i} ({moment.get('timestamp', '00:00')}) - Speaker: {speaker}
> "{moment.get('quote', 'No quote')}"

*Context: {moment.get('context', 'No context')}*
*Confidence: {confidence}*
"""

        # Reel suggestions
        md += "\n## Reel Suggestions (Verified Timestamps)\n"
        for i, reel in enumerate(data.get('reel_suggestions', []), 1):
            confidence = reel.get('confidence_level', 'unknown')
            md += f"""
### Reel {i}: {reel.get('title', 'Untitled')}
- **Time**: {reel.get('start_time', '00:00')} - {reel.get('end_time', '00:00')}
- **Hook**: "{reel.get('hook', 'No hook provided')}"
- **Closing**: "{reel.get('closing', 'No closing provided')}"
- **Why**: {reel.get('description', 'No description')}
- **Editing**: {reel.get('editing_instructions', 'No instructions')}
- **Timestamp Confidence**: {confidence}
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

        # Add error information if any
        errors = data.get('generation_errors', [])
        if errors:
            md += f"\n## Generation Errors\n"
            for error in errors:
                md += f"- ⚠️ {error}\n"

        return md