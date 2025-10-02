"""
Demonstration script showing ChainPromptingAccuracyService as drop-in replacement

This script shows:
1. Interface compatibility with HighAccuracyContentService
2. Chain prompting architecture in action
3. Two-step chapter generation process
"""

from services.accuracy_service_chain_prompting import ChainPromptingAccuracyService
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Sample transcript for testing
SAMPLE_TRANSCRIPT = """00:00:15 speaker_0: Welcome to the Tech Insights podcast! I'm your host, Sarah Chen.
00:00:30 speaker_1: Thanks for having me, Sarah. I'm excited to discuss AI advancements.
00:01:15 speaker_0: Let's start with the elephant in the room - is AI really transforming every industry?
00:01:45 speaker_1: Absolutely. We're seeing AI integration in healthcare, finance, education, and manufacturing. It's not hype anymore, it's reality.
00:02:30 speaker_0: That's a powerful statement. Can you give us a specific example?
00:03:00 speaker_1: Sure. In healthcare, AI is now diagnosing certain cancers more accurately than human doctors. That's not science fiction - that's happening today.
00:04:15 speaker_0: Incredible. What about the ethical concerns around AI deployment?
00:05:00 speaker_1: Ethics must be our top priority. We can't just optimize for performance. We need fairness, transparency, and accountability built into every system.
00:06:30 speaker_0: Let's talk about the future. Where do you see AI in five years?
00:07:15 speaker_1: I predict AI will become as ubiquitous as smartphones. Every professional will have AI assistants helping with their daily work.
00:08:00 speaker_0: That's both exciting and a bit scary. What should people do to prepare?
00:08:45 speaker_1: Learn the fundamentals. You don't need to be a data scientist, but understanding how AI makes decisions is crucial for the future workforce."""

def demo_chain_prompting():
    """Demonstrate chain prompting service"""

    print("=" * 80)
    print("CHAIN PROMPTING ACCURACY SERVICE DEMONSTRATION")
    print("=" * 80)
    print()

    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  No GEMINI_API_KEY found in environment")
        print("This demo requires a valid API key to make actual calls")
        print()
        print("To run this demo:")
        print("1. Set GEMINI_API_KEY in your .env file")
        print("2. Run: python tests/demo_chain_prompting.py")
        return

    # Initialize service
    print("1️⃣  Initializing ChainPromptingAccuracyService...")
    service = ChainPromptingAccuracyService(api_key=api_key)
    print("   ✓ Service initialized with Gemini 2.5 Pro")
    print()

    # Episode info
    episode_info = {
        "show": "Tech Insights",
        "host": "Sarah Chen",
        "guest": "Dr. Alex Rivera",
        "episode_number": "42"
    }

    # Generate content using chain prompting
    print("2️⃣  Generating content using chain prompting architecture...")
    print("   This will make 5-10 separate API calls:")
    print("   - Call 1: Quotable moments")
    print("   - Call 2: Reel suggestions")
    print("   - Call 3: Content warnings")
    print("   - Call 4: Chapter titles")
    print("   - Calls 5+: Timestamp for each chapter")
    print()

    result = service.generate_accuracy_critical_content(
        transcript_text=SAMPLE_TRANSCRIPT,
        episode_info=episode_info,
        language="en"
    )

    # Display results
    print("3️⃣  RESULTS:")
    print()

    print("📝 QUOTABLE MOMENTS:")
    for i, quote in enumerate(result.get("quotable_moments", []), 1):
        print(f"   {i}. [{quote.get('timestamp')}] {quote.get('speaker')}")
        print(f"      \"{quote.get('quote')}\"")
        print(f"      Context: {quote.get('context')}")
        print()

    print("🎬 REEL SUGGESTIONS:")
    for i, reel in enumerate(result.get("reel_suggestions", []), 1):
        print(f"   {i}. {reel.get('title')}")
        print(f"      Time: {reel.get('start_time')} → {reel.get('end_time')}")
        print(f"      Confidence: {reel.get('confidence_level')}")
        print(f"      Hook: {reel.get('hook')}")
        print()

    print("⚠️  CONTENT WARNINGS:")
    warnings = result.get("content_warnings", [])
    if warnings:
        for warning in warnings:
            print(f"   - {warning}")
    else:
        print("   - No warnings")
    print()

    print("📚 CHAPTER TIMESTAMPS:")
    for i, chapter in enumerate(result.get("chapter_timestamps", []), 1):
        print(f"   {i}. {chapter}")
    print()

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Key Features Demonstrated:")
    print("✓ Drop-in replacement for HighAccuracyContentService")
    print("✓ Separate API calls for each task (chain prompting)")
    print("✓ Two-step chapter generation (titles → timestamps)")
    print("✓ Same output format for A/B testing compatibility")
    print()

if __name__ == "__main__":
    demo_chain_prompting()
