"""
A/B Test Script for Chain Prompting Accuracy Service (Phase 0.5)

This script runs BOTH services on the same transcript in parallel:
1. Original HighAccuracyContentService (baseline)
2. ChainPromptingAccuracyService (experiment)

Then saves outputs to separate files for manual comparison.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.accuracy_service import HighAccuracyContentService
from services.accuracy_service_chain_prompting import ChainPromptingAccuracyService


def load_transcript(file_path):
    """Load transcript from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def save_results(results, output_path, service_name):
    """Save results to JSON file"""
    output_data = {
        "service": service_name,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {service_name} results to {output_path}")


def print_summary(results, service_name):
    """Print summary of results for quick comparison"""
    print(f"\n{'='*60}")
    print(f"{service_name} - SUMMARY")
    print(f"{'='*60}")

    # Count items
    quotes = results.get('quotable_moments', [])
    reels = results.get('reel_suggestions', [])
    warnings = results.get('content_warnings', [])
    chapters = results.get('chapter_timestamps', [])

    print(f"Quotable Moments: {len(quotes)}")
    print(f"Reel Suggestions: {len(reels)}")
    print(f"Content Warnings: {len(warnings)}")
    print(f"Chapter Timestamps: {len(chapters)}")

    # Show chapter timestamps for manual verification
    if chapters:
        print(f"\n📍 Chapter Timestamps (for manual verification):")
        for i, chapter in enumerate(chapters, 1):
            print(f"   {i}. {chapter}")

    # Show first 3 quotes for quick check
    if quotes:
        print(f"\n💬 First 3 Quotes (for spot check):")
        for i, quote in enumerate(quotes[:3], 1):
            timestamp = quote.get('timestamp', 'N/A')
            text = quote.get('quote', 'N/A')[:80] + "..." if len(quote.get('quote', '')) > 80 else quote.get('quote', 'N/A')
            print(f"   {i}. [{timestamp}] {text}")


def main():
    """Run A/B test comparing both services"""

    # Load environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment")
        sys.exit(1)

    # Load transcript
    transcript_path = os.path.join(
        os.path.dirname(__file__),
        'test_data',
        'מרב-בהט_transcript.txt'
    )

    if not os.path.exists(transcript_path):
        print(f"❌ Error: Transcript not found at {transcript_path}")
        sys.exit(1)

    print(f"📄 Loading transcript from {transcript_path}")
    transcript_text = load_transcript(transcript_path)
    print(f"✅ Loaded {len(transcript_text)} characters")

    # Episode info
    episode_info = {
        "show": "פודקאסט מרב בהט",
        "host": "גיא",
        "guest": "מירב בהט",
        "episode_number": "Test Episode"
    }

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), 'ab_test_results')
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize both services
    print("\n" + "="*60)
    print("INITIALIZING SERVICES")
    print("="*60)

    original_service = HighAccuracyContentService(api_key)
    chain_service = ChainPromptingAccuracyService(api_key)

    print("✅ Original service initialized")
    print("✅ Chain prompting service initialized")

    # Run both services
    print("\n" + "="*60)
    print("RUNNING ORIGINAL SERVICE (BASELINE)")
    print("="*60)

    try:
        original_results = original_service.generate_accuracy_critical_content(
            transcript_text=transcript_text,
            episode_info=episode_info,
            language="he"
        )

        original_output = os.path.join(output_dir, f'{timestamp}_original.json')
        save_results(original_results, original_output, "Original HighAccuracyContentService")
        print_summary(original_results, "ORIGINAL SERVICE")

    except Exception as e:
        print(f"❌ Original service failed: {e}")
        original_results = {"error": str(e)}

    print("\n" + "="*60)
    print("RUNNING CHAIN PROMPTING SERVICE (EXPERIMENT)")
    print("="*60)

    try:
        chain_results = chain_service.generate_accuracy_critical_content(
            transcript_text=transcript_text,
            episode_info=episode_info,
            language="he"
        )

        chain_output = os.path.join(output_dir, f'{timestamp}_chain_prompting.json')
        save_results(chain_results, chain_output, "Chain Prompting Accuracy Service")
        print_summary(chain_results, "CHAIN PROMPTING SERVICE")

    except Exception as e:
        print(f"❌ Chain prompting service failed: {e}")
        chain_results = {"error": str(e)}

    # Final comparison summary
    print("\n" + "="*60)
    print("A/B TEST COMPLETED")
    print("="*60)
    print(f"\n📁 Results saved to: {output_dir}")
    print(f"   - Original: {timestamp}_original.json")
    print(f"   - Chain Prompting: {timestamp}_chain_prompting.json")
    print("\n📋 Next Steps:")
    print("   1. Open both JSON files")
    print("   2. Compare chapter_timestamps for accuracy")
    print("   3. Manually verify timestamps against transcript")
    print("   4. Focus on quotes/chapters from 3min, 8min, 15min, 25min+ marks")
    print("   5. Document findings in ACCURACY_ENHANCEMENT_PROGRESS.md")


if __name__ == "__main__":
    main()
