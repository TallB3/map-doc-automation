# Test Fixtures for Accuracy Enhancement

**Purpose**: Provide ground truth data for testing timestamp and quote accuracy improvements

---

## 🎯 Test Strategy

### Why These Fixtures Matter

Our accuracy enhancement specifically targets **Gemini's timestamp failure pattern**:

```
Time Range       | Current Accuracy | Target Accuracy
-----------------|------------------|----------------
0-3 minutes      | ~80-90%         | 95%+
3-5 minutes      | ~40-60%         | 95%+
5-15 minutes     | ~20-40%         | 95%+
15+ minutes      | ~5-15%          | 95%+
```

**Critical Insight**: Gemini doesn't just fail "late in the episode" - it starts degrading **after 3 minutes** and gets progressively worse.

Therefore, our test fixtures must specifically target these time ranges to prove the enhancement works.

---

## 📋 Fixture Requirements

### Episode Selection Criteria

Each test episode MUST meet these requirements:

1. **LENGTH**: 30+ minutes
   - **Why**: Forces model to handle long context
   - **Rationale**: Short episodes (<10min) don't expose the attention dilution problem

2. **LANGUAGE**: Mix of Hebrew and English
   - **Why**: Ensures multilingual embeddings work correctly
   - **Rationale**: Our production system handles both languages

3. **BOTH FORMATS**:
   - `transcript.txt` (formatted text with timestamps like "00:05:23")
   - `raw-transcript.json` (word-level timestamps with exact start/end times)
   - **Why**: txt for chunking, json for ground truth verification

4. **REAL PRODUCTION DATA**:
   - Actual podcast episodes from production
   - **Why**: Realistic failure patterns, authentic language use
   - **Rationale**: Synthetic data won't expose real-world issues

---

## 🎯 Ground Truth Data Point Distribution

**CRITICAL**: We must test quotes at specific time marks that expose Gemini's failures!

### Required Ground Truth Per Episode

| Data Type | Quantity | Time Distribution | Purpose |
|-----------|----------|------------------|---------|
| Quotes | 5 | 3min, 8min, 15min, 25min, 40min+ | Test timestamp accuracy across full episode |
| Reels | 2-3 | 10min+ onwards | Test start/end timestamp accuracy for ranges |
| Chapters | 3-5 | Throughout episode | Test topic transition detection |

**Total**: 10-13 manually verified data points per episode

### Time Mark Strategy

**Quote 1 (~3:30 mark)** - MEDIUM DIFFICULTY
- **Purpose**: Test the "accuracy degradation threshold"
- **Expected Gemini Behavior**: Usually correct, but starting to show errors
- **Why This Matters**: Proves improvement even at early degradation point

**Quote 2 (~8:00 mark)** - HARD DIFFICULTY
- **Purpose**: Mid-early section where errors become common
- **Expected Gemini Behavior**: Often off by 2-5 minutes
- **Why This Matters**: Common failure zone needs reliable fix

**Quote 3 (~15:00 mark)** - VERY HARD DIFFICULTY
- **Purpose**: Middle of long transcript
- **Expected Gemini Behavior**: Often returns timestamps from first 10 minutes
- **Why This Matters**: High error rate, critical to fix

**Quote 4 (~25:00 mark)** - EXTREME DIFFICULTY
- **Purpose**: Late-middle section
- **Expected Gemini Behavior**: Almost always wildly off (returns 5-15 min timestamps)
- **Why This Matters**: Proves system works even for very late content

**Quote 5 (~40:00+ mark)** - CRITICAL DIFFICULTY
- **Purpose**: Near end of episode (worst accuracy zone)
- **Expected Gemini Behavior**: Consistently returns early timestamps (0-20 min range)
- **Why This Matters**: If this works, everything works

---

## 📁 Fixture Structure

```
tests/fixtures/
├── README.md (this file)
│
├── episode_001_political_hebrew/
│   ├── transcript.txt              ← Full formatted transcript
│   ├── raw-transcript.json         ← Word-level timestamps (ground truth source)
│   └── ground_truth.json           ← Manually verified test data
│
├── episode_002_tech_english/
│   ├── transcript.txt
│   ├── raw-transcript.json
│   └── ground_truth.json
│
└── episode_003_interview_hebrew/
    ├── transcript.txt
    ├── raw-transcript.json
    └── ground_truth.json
```

---

## 📝 Ground Truth JSON Format

### Complete Example

```json
{
  "episode_info": {
    "title": "Political Discussion - Israeli Foreign Policy",
    "duration_minutes": 58.5,
    "duration_seconds": 3510,
    "language": "he",
    "difficulty": "hard - long transcript with late quotes",
    "verified_by": "Orr",
    "verification_date": "2025-10-01"
  },

  "verified_quotes": [
    {
      "id": "quote_1_early",
      "text": "אנחנו צריכים לדבר על זה ברצינות",
      "correct_timestamp_seconds": 210.0,
      "correct_timestamp_formatted": "03:30",
      "speaker": "speaker_0",
      "difficulty": "medium",
      "location_in_transcript": "early",
      "time_category": "3-5_minutes",
      "expected_gemini_error": "usually correct at this position, sometimes off by 30-60 seconds",
      "context": "Discussion about diplomatic relations"
    },
    {
      "id": "quote_2_mid_early",
      "text": "זה משנה את כל התמונה",
      "correct_timestamp_seconds": 480.0,
      "correct_timestamp_formatted": "08:00",
      "speaker": "speaker_1",
      "difficulty": "hard",
      "location_in_transcript": "mid-early",
      "time_category": "5-15_minutes",
      "expected_gemini_error": "often returns 03:45 or 05:23 instead",
      "context": "Analysis of policy changes"
    },
    {
      "id": "quote_3_middle",
      "text": "זה לא משהו שאנחנו יכולים להתעלם ממנו",
      "correct_timestamp_seconds": 900.0,
      "correct_timestamp_formatted": "15:00",
      "speaker": "speaker_0",
      "difficulty": "very_hard",
      "location_in_transcript": "middle",
      "time_category": "15-25_minutes",
      "expected_gemini_error": "consistently returns early timestamp like 05:30-10:00",
      "context": "Debate about regional security"
    },
    {
      "id": "quote_4_late_middle",
      "text": "כל המומחים מסכימים על הנקודה הזאת",
      "correct_timestamp_seconds": 1500.0,
      "correct_timestamp_formatted": "25:00",
      "speaker": "speaker_1",
      "difficulty": "extreme",
      "location_in_transcript": "late-middle",
      "time_category": "25-40_minutes",
      "expected_gemini_error": "almost always wildly off, returns 08:00-15:00 range",
      "context": "Expert consensus discussion"
    },
    {
      "id": "quote_5_near_end",
      "text": "בסופו של דבר, זה מסתכם בבחירה שלנו",
      "correct_timestamp_seconds": 2400.0,
      "correct_timestamp_formatted": "40:00",
      "speaker": "speaker_0",
      "difficulty": "critical",
      "location_in_transcript": "near_end",
      "time_category": "40+_minutes",
      "expected_gemini_error": "consistently returns timestamp from first 20 minutes",
      "context": "Concluding remarks about decision-making"
    }
  ],

  "verified_reels": [
    {
      "id": "reel_1_mid_episode",
      "title": "הרגע המכריע - ויכוח על המדיניות",
      "correct_start_seconds": 720.0,
      "correct_end_seconds": 780.0,
      "correct_start_formatted": "12:00",
      "correct_end_formatted": "13:00",
      "duration_seconds": 60,
      "difficulty": "very_hard",
      "location_in_transcript": "middle",
      "expected_gemini_error": "returns start at 04:30 or 06:15 instead of 12:00",
      "description": "Heated debate about foreign policy approach"
    },
    {
      "id": "reel_2_late_episode",
      "title": "המסקנה המפתיעה",
      "correct_start_seconds": 2550.0,
      "correct_end_seconds": 2640.0,
      "correct_start_formatted": "42:30",
      "correct_end_formatted": "44:00",
      "duration_seconds": 90,
      "difficulty": "critical",
      "location_in_transcript": "near_end",
      "expected_gemini_error": "returns timestamps from early/middle of episode (10:00-20:00)",
      "description": "Surprising conclusion that changes the discussion"
    }
  ],

  "verified_chapters": [
    {
      "timestamp_seconds": 0,
      "timestamp_formatted": "00:00",
      "title": "פתיחה - הקדמה לנושא",
      "difficulty": "easy"
    },
    {
      "timestamp_seconds": 420,
      "timestamp_formatted": "07:00",
      "title": "רקע היסטורי",
      "difficulty": "medium"
    },
    {
      "timestamp_seconds": 1080,
      "timestamp_formatted": "18:00",
      "title": "ניתוח המצב הנוכחי",
      "difficulty": "hard"
    },
    {
      "timestamp_seconds": 2160,
      "timestamp_formatted": "36:00",
      "title": "השלכות עתידיות",
      "difficulty": "very_hard"
    },
    {
      "timestamp_seconds": 3300,
      "timestamp_formatted": "55:00",
      "title": "סיכום ומסקנות",
      "difficulty": "critical"
    }
  ]
}
```

---

## ✅ Manual Verification Process

### Step-by-Step Guide

1. **Choose Episode**
   - Select 30+ minute podcast
   - Ensure you have both transcript.txt and raw-transcript.json
   - Verify language (Hebrew or English)

2. **Listen and Identify Quotes** (Target time marks: 3min, 8min, 15min, 25min, 40min+)
   - Play episode in podcast player with timestamp display
   - Find impactful/quotable moments at each target time
   - Note exact timestamp from player

3. **Verify in raw-transcript.json**
   - Open raw-transcript.json
   - Search for the exact quote text
   - Find the `"start"` timestamp in the JSON
   - **This is your ground truth!**

4. **Cross-Check with transcript.txt**
   - Verify quote appears in formatted transcript
   - Note the formatted timestamp (MM:SS or HH:MM:SS)

5. **Document Expected Gemini Errors**
   - Run current accuracy_service.py on the episode
   - Note what timestamps Gemini returns for each quote
   - Document the error pattern (e.g., "returns 05:23 instead of 32:15")

6. **Create ground_truth.json**
   - Use the format shown above
   - Include all metadata (difficulty, expected errors, etc.)

---

## 🧪 How Tests Will Use These Fixtures

### Unit Tests (Services)
```python
def test_timestamp_verification_at_40_minutes():
    """Test that verification detects errors for late-episode quotes"""
    fixture = load_fixture('episode_001_political_hebrew')
    ground_truth = fixture['verified_quotes'][4]  # 40min quote

    # Simulate Gemini returning wrong timestamp
    claimed_timestamp = 600.0  # 10:00 (wrong!)
    actual_timestamp = ground_truth['correct_timestamp_seconds']  # 2400.0 (40:00)

    result = verification_service.verify_timestamp(
        quote_text=ground_truth['text'],
        claimed_timestamp=claimed_timestamp
    )

    assert result['status'] == 'TIMESTAMP_ERROR'
    assert result['actual'] == actual_timestamp
    assert result['delta'] > 1800  # Off by 30+ minutes!
```

### Integration Tests (Full Workflow)
```python
def test_rag_based_accuracy_service_handles_late_quotes():
    """Test that new RAG approach correctly handles 40min+ quotes"""
    fixture = load_fixture('episode_001_political_hebrew')
    ground_truth = fixture['verified_quotes'][4]  # 40min quote

    # Run new accuracy service v2 (RAG-based)
    output = accuracy_service_v2.generate_with_verification(
        transcript_text=fixture['transcript.txt'],
        raw_transcript_json=fixture['raw-transcript.json']
    )

    # Find the quote in output
    matching_quote = find_quote_by_text(output, ground_truth['text'])

    # Verify timestamp is within 5 seconds
    delta = abs(matching_quote['timestamp_seconds'] - ground_truth['correct_timestamp_seconds'])
    assert delta < 5.0, f"Timestamp off by {delta} seconds for late-episode quote"
```

### Benchmark Tests
```python
def test_accuracy_benchmark_all_fixtures():
    """Run comprehensive accuracy benchmark on all test fixtures"""
    results = []

    for fixture in load_all_fixtures():
        output = accuracy_service_v2.generate_with_verification(
            transcript_text=fixture['transcript.txt'],
            raw_transcript_json=fixture['raw-transcript.json']
        )

        accuracy = calculate_accuracy(output, fixture['ground_truth'])
        results.append({
            'episode': fixture['name'],
            'language': fixture['language'],
            'timestamp_accuracy_0_5min': accuracy.get_accuracy_range(0, 300),
            'timestamp_accuracy_5_15min': accuracy.get_accuracy_range(300, 900),
            'timestamp_accuracy_15_40min': accuracy.get_accuracy_range(900, 2400),
            'timestamp_accuracy_40min_plus': accuracy.get_accuracy_range(2400, 10000),
            'overall_timestamp_accuracy': accuracy.overall_timestamp,
            'quote_exact_match_rate': accuracy.quote_exact_match
        })

    # Assert overall targets
    overall = aggregate_results(results)
    assert overall['timestamp_accuracy'] >= 0.95
    assert overall['quote_accuracy'] >= 0.90
```

---

## 📊 Expected Test Coverage

### By Time Range
- ✅ 3-5 minutes: 3 quotes across all fixtures
- ✅ 5-15 minutes: 3 quotes across all fixtures
- ✅ 15-25 minutes: 3 quotes across all fixtures
- ✅ 25-40 minutes: 3 quotes across all fixtures
- ✅ 40+ minutes: 3 quotes across all fixtures

### By Language
- ✅ Hebrew: 2 episodes (10-13 data points each)
- ✅ English: 1 episode (10-13 data points)

### By Content Type
- ✅ Quotes: 15 total (5 per episode × 3 episodes)
- ✅ Reels: 6-9 total (2-3 per episode × 3 episodes)
- ✅ Chapters: 9-15 total (3-5 per episode × 3 episodes)

**Total Ground Truth Data Points**: ~30-40 manually verified items

---

## 🚧 Current Status

### Completed:
- ✅ Test strategy defined
- ✅ Ground truth format designed
- ✅ Verification process documented

### Pending:
- ⏳ Identify 3 suitable podcast episodes (30+ min, Hebrew + English)
- ⏳ Manual verification of ground truth data points
- ⏳ Create ground_truth.json for each episode
- ⏳ Document expected Gemini errors for each test case

---

## 💡 Tips for Creating Quality Fixtures

### Do's:
- ✅ **Target the failure zones**: Focus on 3min+, 15min+, 40min+ marks
- ✅ **Use real transcripts**: Authentic language patterns expose real issues
- ✅ **Verify with raw JSON**: Word-level timestamps are ground truth
- ✅ **Document expected errors**: Helps prove improvement
- ✅ **Mix difficulty levels**: Include some "easy" early quotes for baseline

### Don'ts:
- ❌ **Don't use only early quotes**: Won't expose the problem
- ❌ **Don't guess timestamps**: Always verify in raw-transcript.json
- ❌ **Don't skip context**: Context helps understand why quote matters
- ❌ **Don't forget metadata**: Difficulty, location, etc. help debugging

---

**End of Test Fixtures README**
**Next**: Prepare actual test fixture episodes with ground truth data
