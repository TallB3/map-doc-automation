# Chain Prompting Accuracy Service - Phase 0.5 Experiment

## Overview

This document describes the **Chain Prompting Accuracy Service**, an experimental approach to improve timestamp accuracy in AI-generated podcast content by separating tasks into individual, focused API calls.

**Status**: ✅ Implemented with TDD - All 14 tests passing
**Phase**: 0.5 (Pre-RAG experimentation)
**Goal**: Test if chain prompting improves accuracy vs single-call approach

## The Problem

The current `HighAccuracyContentService` processes 6000+ tokens in a single API call, asking the model to simultaneously:
- Find quotable moments with exact timestamps
- Generate reel suggestions with precise time ranges
- Identify content warnings
- Create chapter timestamps

This cognitive overload may contribute to timestamp accuracy issues.

## The Hypothesis

**Chain prompting** - breaking down tasks into separate, focused API calls - may improve accuracy by:
1. Reducing cognitive load per call
2. Allowing focused prompts for each task
3. Enabling two-step reasoning for complex tasks (chapters)

## Architecture

### Single-Call Approach (Current)
```
One API Call
├── Quotable moments
├── Reel suggestions
├── Content warnings
└── Chapter timestamps
```

### Chain Prompting Approach (New)
```
Call 1: Quotable moments only
Call 2: Reel suggestions only
Call 3: Content warnings only
Call 4: Chapter titles (no timestamps)
Call 5: Timestamp for chapter 1
Call 6: Timestamp for chapter 2
...
Call N: Timestamp for chapter N
```

## Key Innovation: Two-Step Chapter Generation

The most important innovation is splitting chapter generation into two steps:

### Step 1: Get Chapter Titles (No Timestamps)
```json
{
  "chapter_titles": [
    "Introduction and Welcome",
    "AI in Healthcare",
    "Ethical Considerations",
    "Future Predictions"
  ]
}
```

### Step 2: Find Timestamp for Each Title
For each title, make a focused call:
```
Prompt: "Find the exact timestamp where 'AI in Healthcare' begins"
Response: {"timestamp": "03:00"}
```

This approach:
- Separates topic identification from timestamp finding
- Allows model to focus solely on finding when a specific topic starts
- Reduces likelihood of hallucinated timestamps

## Implementation Details

### File Locations
- **Service**: `/home/tallb/projects/reflection/services/accuracy_service_chain_prompting.py`
- **Tests**: `/home/tallb/projects/reflection/tests/test_accuracy_service_chain_prompting.py`
- **Demo**: `/home/tallb/projects/reflection/tests/demo_chain_prompting.py`

### Interface Compatibility

The service implements the **exact same interface** as `HighAccuracyContentService`:

```python
class ChainPromptingAccuracyService:
    def __init__(self, api_key):
        """Initialize Gemini client"""

    def generate_accuracy_critical_content(
        self,
        transcript_text,
        episode_info=None,
        language="en"
    ):
        """
        Same signature as HighAccuracyContentService
        Returns same JSON structure for drop-in compatibility
        """
```

This enables easy A/B testing without changing calling code.

### Internal Methods

Each task gets its own focused method:

```python
def _generate_quotable_moments(transcript_text, language)
    """Focused prompt asking ONLY for quotes"""

def _generate_reel_suggestions(transcript_text, language)
    """Focused prompt asking ONLY for reels"""

def _generate_content_warnings(transcript_text, language)
    """Focused prompt asking ONLY for warnings"""

def _generate_chapter_timestamps(transcript_text, language)
    """Two-step chain: titles first, then timestamps"""
```

### Model Configuration

Uses identical settings to `HighAccuracyContentService`:
- Model: `gemini-2.5-pro`
- Temperature: `0.05` (very low for accuracy)
- Top-p: `0.5` (focused sampling)
- Top-k: `10` (highly focused)
- Response format: `application/json`

## Test Coverage

### Test Suite: 14 Tests, 100% Passing

#### 1. Architecture Tests (6 tests)
- ✅ `test_each_task_uses_separate_api_call` - Verifies multiple API calls are made
- ✅ `test_quotable_moments_focused_prompt` - Quote prompt asks ONLY for quotes
- ✅ `test_reel_suggestions_focused_prompt` - Reel prompt asks ONLY for reels
- ✅ `test_chapter_generation_is_two_step_chain` - Chapters use two-step process
- ✅ `test_chapter_step1_returns_titles_without_timestamps` - Step 1 returns only titles
- ✅ `test_chapter_step2_finds_timestamp_for_specific_title` - Step 2 finds specific timestamp

#### 2. Compatibility Tests (1 test)
- ✅ `test_output_format_matches_original_service` - Output matches original format

#### 3. Language Support Tests (2 tests)
- ✅ `test_handles_hebrew_language` - Hebrew content generation
- ✅ `test_handles_english_language` - English content generation

#### 4. Error Handling Tests (2 tests)
- ✅ `test_handles_api_failure_gracefully` - Graceful error responses
- ✅ `test_handles_empty_transcript` - Handles edge cases

#### 5. Model Configuration Tests (3 tests)
- ✅ `test_uses_gemini_25_pro_model` - Uses correct model
- ✅ `test_uses_high_accuracy_settings` - Correct temperature/sampling
- ✅ `test_requests_json_response_format` - JSON output format

## Usage

### As Drop-In Replacement

```python
from services.accuracy_service_chain_prompting import ChainPromptingAccuracyService

# Initialize (same as original service)
service = ChainPromptingAccuracyService(api_key=gemini_key)

# Generate content (same interface)
result = service.generate_accuracy_critical_content(
    transcript_text=transcript,
    episode_info={"show": "My Podcast", "host": "John Doe"},
    language="en"
)

# Same output format
print(result["quotable_moments"])
print(result["reel_suggestions"])
print(result["content_warnings"])
print(result["chapter_timestamps"])
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/test_accuracy_service_chain_prompting.py -v

# Run specific test
python -m pytest tests/test_accuracy_service_chain_prompting.py::TestChainPromptingArchitecture::test_chapter_generation_is_two_step_chain -v

# Run demo (requires GEMINI_API_KEY)
python tests/demo_chain_prompting.py
```

## Expected API Call Pattern

For a typical podcast transcript:

```
Total API Calls: 5-10 (depending on number of chapters)

Call 1: Generate quotable moments
Call 2: Generate reel suggestions
Call 3: Generate content warnings
Call 4: Get chapter titles (returns 3-8 titles)
Call 5: Find timestamp for chapter 1
Call 6: Find timestamp for chapter 2
...
Call N: Find timestamp for chapter N
```

## Output Format

Same structure as `HighAccuracyContentService`:

```json
{
  "quotable_moments": [
    {
      "quote": "Ethics must be our top priority",
      "timestamp": "05:00",
      "context": "Discussion about AI development principles",
      "speaker": "speaker_1"
    }
  ],
  "reel_suggestions": [
    {
      "title": "AI in Healthcare Revolution",
      "start_time": "03:00",
      "end_time": "04:15",
      "description": "Compelling discussion about AI diagnosing cancer",
      "hook": "AI is now diagnosing cancers more accurately than doctors",
      "closing": "That's not science fiction - that's happening today",
      "editing_instructions": "Focus on speaker_1 during key quote",
      "confidence_level": "high"
    }
  ],
  "content_warnings": [
    "No warnings"
  ],
  "chapter_timestamps": [
    "00:15 Welcome and Introduction",
    "01:15 AI Industry Transformation",
    "03:00 Healthcare Applications",
    "04:15 Ethical Considerations",
    "06:30 Future Predictions"
  ]
}
```

## Trade-offs

### Advantages
✅ **Reduced cognitive load** - Each call focuses on one task
✅ **Focused prompts** - No task mixing or confusion
✅ **Two-step reasoning** - Chapters get dedicated timestamp finding
✅ **Drop-in compatible** - Same interface as original service
✅ **Same model settings** - Fair comparison for A/B testing

### Disadvantages
❌ **More API calls** - 5-10 calls vs 1 call
❌ **Higher latency** - Sequential calls take longer
❌ **Increased cost** - More calls = higher API costs
❌ **No cross-task context** - Tasks can't inform each other

## Cost Analysis

Assuming average podcast transcript (~5000 tokens):

### Single-Call Approach
- Input: ~5000 tokens × 1 call = 5,000 tokens
- Output: ~2000 tokens × 1 call = 2,000 tokens
- **Total: ~7,000 tokens**

### Chain Prompting Approach
- Input: ~5000 tokens × 8 calls = 40,000 tokens
- Output: ~500 tokens × 8 calls = 4,000 tokens
- **Total: ~44,000 tokens** (6.3× more)

**Cost increase**: Approximately 6× higher token usage

## Next Steps for Experimentation

### Phase 1: Basic Accuracy Testing
1. Run both services on same 10 transcripts
2. Compare timestamp accuracy manually
3. Measure precision of chapter timestamps
4. Compare quote accuracy

### Phase 2: Cost-Benefit Analysis
1. Measure actual API costs for both approaches
2. Quantify accuracy improvements (if any)
3. Calculate cost per accuracy point improvement
4. Determine if cost increase justifies accuracy gains

### Phase 3: Hybrid Approach
If chain prompting proves effective but too costly:
1. Use single-call for simple tasks (warnings)
2. Use chain prompting ONLY for chapters
3. Optimize prompt sizes to reduce token usage
4. Consider caching chapter titles

## Comparison to Original Service

| Aspect | HighAccuracyContentService | ChainPromptingAccuracyService |
|--------|---------------------------|-------------------------------|
| API Calls | 1 | 5-10 |
| Token Usage | ~7K | ~44K |
| Latency | Low (single call) | Higher (sequential calls) |
| Prompt Focus | Multi-task | Single-task |
| Chapter Generation | One-step | Two-step chain |
| Interface | Standard | Compatible |
| Cost | Baseline | ~6× higher |
| Accuracy | Baseline | **To be measured** |

## Development Methodology

This service was built using **strict Test-Driven Development (TDD)**:

1. **RED Phase**: Wrote 14 comprehensive tests FIRST
2. **CONFIRM Phase**: Verified tests failed for right reasons (module not found)
3. **GREEN Phase**: Implemented minimal code to pass all tests
4. **VERIFY Phase**: All 14 tests pass, zero diagnostics
5. **REFACTOR Phase**: Reviewed code quality, added documentation

All tests verify:
- Architectural correctness (chain prompting pattern)
- Interface compatibility (drop-in replacement)
- Prompt focus (single-task per call)
- Error handling (graceful failures)
- Language support (Hebrew, English)
- Model configuration (same settings as original)

## Conclusion

The `ChainPromptingAccuracyService` is **ready for experimentation** as Phase 0.5 before building the full RAG system. It provides:

✅ Drop-in replacement for easy A/B testing
✅ Comprehensive test coverage (14 tests, 100% pass)
✅ Two-step chapter generation innovation
✅ Focused prompts per task
✅ Same model configuration for fair comparison

**Next Action**: Run accuracy experiments on real podcast transcripts to determine if the 6× cost increase justifies potential accuracy improvements.

---

**Files Created (TDD Approach)**:
- `/home/tallb/projects/reflection/services/accuracy_service_chain_prompting.py` (428 lines)
- `/home/tallb/projects/reflection/tests/test_accuracy_service_chain_prompting.py` (499 lines)
- `/home/tallb/projects/reflection/tests/demo_chain_prompting.py` (142 lines)
- `/home/tallb/projects/reflection/CHAIN_PROMPTING_EXPERIMENT.md` (this document)

**Test Results**: 14/14 passing ✅
