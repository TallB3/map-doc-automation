"""Run ONLY the chain prompting service - for parallel execution"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.accuracy_service_chain_prompting import ChainPromptingAccuracyService


def main():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        sys.exit(1)

    # Load transcript
    transcript_path = os.path.join(os.path.dirname(__file__), 'test_data', 'מרב-בהט_transcript.txt')
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_text = f.read()

    episode_info = {
        "show": "פודקאסט מרב בהט",
        "host": "גיא",
        "guest": "מירב בהט",
        "episode_number": "Test"
    }

    print("🔗 CHAIN PROMPTING SERVICE - Starting...")
    service = ChainPromptingAccuracyService(api_key)

    results = service.generate_accuracy_critical_content(
        transcript_text=transcript_text,
        episode_info=episode_info,
        language="he"
    )

    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), 'ab_test_results')
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f'{timestamp}_chain_prompting.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"service": "ChainPrompting", "results": results}, f, ensure_ascii=False, indent=2)

    print(f"✅ CHAIN PROMPTING SERVICE - Completed! Saved to {output_path}")
    print(f"   Chapters: {len(results.get('chapter_timestamps', []))}")
    print(f"   Quotes: {len(results.get('quotable_moments', []))}")


if __name__ == "__main__":
    main()
