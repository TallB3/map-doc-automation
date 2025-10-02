# Accuracy Enhancement - Implementation Progress

**Project**: Map-Doc Automation - Timestamp & Quote Accuracy Improvement
**Goal**: Achieve 95%+ timestamp accuracy and 90%+ quote accuracy

---

## 📊 Project Status

**Current Phase**: Phase 0 - Documentation & Setup
**Status**: ✅ IN PROGRESS
**Last Updated**: 2025-10-01
**Next Session Priority**: Complete Phase 0, prepare test fixtures

---

## 🎯 Success Criteria

### Quantitative Targets
- ✅ **Timestamp Accuracy**: 95%+ within 5-second window (across full episode)
- ✅ **Quote Accuracy**: 90%+ exact matches (10% acceptable minor filler word removal)
- ✅ **Late-Episode Performance**: Works for quotes at 3min, 5min, 15min, 25min, 40min+ marks
- ✅ **Cost**: Similar or better than current approach (focused context uses fewer tokens)

### Qualitative Targets
- ✅ Every output includes confidence scores
- ✅ Verification metadata in map-docs
- ✅ Failed verifications trigger automatic refinement
- ✅ Works for both Hebrew and English
- ✅ Structured error feedback (not generic "try again")

---

## 🏗️ Architecture Overview

### Current Architecture (BROKEN)
```
┌─────────────────────────────────────────────────────────┐
│  Single API Call with Full Transcript (6000+ tokens)    │
│                                                          │
│  Gemini 2.5 Pro                                          │
│  Input: Entire 30-60 min transcript                      │
│  Output: quotes + reels + chapters                       │
│                                                          │
│  Problem: Attention dilution                            │
│  - Accurate for 0-3 minutes                             │
│  - Degrades after 3-5 minutes                            │
│  - "Wildly off" after 5+ minutes                         │
└─────────────────────────────────────────────────────────┘
```

### New Architecture (PROPOSED)

```
┌─────────────────────────────────────────────────────────┐
│             RAG-Based Chunked Retrieval                  │
│                                                          │
│  1. Semantic Chunking (200-400 tokens)                   │
│     └─> Include timestamp metadata                      │
│                                                          │
│  2. Vector Indexing (ChromaDB)                           │
│     └─> paraphrase-multilingual-MiniLM-L12-v2          │
│                                                          │
│  3. Task-Specific Retrieval                              │
│     ├─> Find quotable moments → Search relevant chunks  │
│     ├─> Find reels → Search engaging segments           │
│     └─> Chapter breaks → Search topic transitions       │
│                                                          │
│  4. Focused Generation                                   │
│     └─> Gemini sees ONLY 200-400 tokens + timestamps   │
│                                                          │
│  5. Verification (Critic Agent)                          │
│     └─> Validate against raw-transcript.json            │
│                                                          │
│  6. Reflection Loop (max 3 iterations)                   │
│     └─> Refine based on structured feedback             │
└─────────────────────────────────────────────────────────┘
```

### Producer-Critic-Verifier Flow

```
┌──────────────┐
│   Producer   │  Gemini 2.5 Pro with RAG
│   (Accuracy  │  - Receives focused chunks (200-400 tokens)
│    Service)  │  - Generates quotes/reels with timestamps
└──────┬───────┘
       │
       │ Output: quotes, reels, timestamps
       ▼
┌──────────────┐
│    Critic    │  Verification Service
│ (Verification│  - Checks timestamps against raw JSON
│   Service)   │  - Validates quotes exist word-for-word
└──────┬───────┘
       │
       │ Structured Feedback
       ▼
┌──────────────┐
│  Reflection  │  Max 3 iterations
│     Loop     │  - If errors: Producer refines
│              │  - If accurate: Return output
└──────────────┘
```

---

## 📅 Implementation Roadmap

### ✅ Phase 0: Documentation & Setup (CURRENT)
**Goal**: Create persistent tracking and ground truth test data
**Status**: IN PROGRESS
**Duration**: 1 session

#### Tasks:
- [x] Research reflection patterns (Chapter 4 PDF)
- [x] Research RAG patterns (Chapter 14 PDF)
- [x] Research chunking strategies (web search)
- [x] Research vector databases (ChromaDB vs Weaviate vs FAISS)
- [x] Research multilingual embeddings (Hebrew + English)
- [x] Create `knowledge/ACCURACY_ENHANCEMENT_FINDINGS.md`
- [ ] Create `ACCURACY_ENHANCEMENT_PROGRESS.md` (this file)
- [ ] Create `tests/fixtures/README.md`
- [ ] Prepare 2-3 test fixtures with ground truth data

#### Deliverables:
- ✅ `knowledge/ACCURACY_ENHANCEMENT_FINDINGS.md` (~2000 lines)
- 🔄 `ACCURACY_ENHANCEMENT_PROGRESS.md` (this file)
- ⏳ `tests/fixtures/README.md`
- ⏳ Test fixtures with manually verified ground truth

---

### ⏳ Phase 0.5: Chain Prompting Experiment (NEW - INSERTED 2025-10-02)
**Goal**: Test if separating tasks into individual API calls improves accuracy BEFORE building full RAG system
**Status**: IN PROGRESS
**Duration**: 1-2 sessions
**Approach**: Create new experimental service alongside existing one for A/B comparison

**Rationale**: Test simpler hypothesis first - maybe the issue isn't the 6000 token context itself, but trying to do ALL tasks (quotes + reels + chapters + warnings) in ONE call. Separating tasks could dramatically reduce cognitive load without needing full RAG architecture.

#### 0.5.1 Update Documentation
**Task**: Insert Phase 0.5 into roadmap and document experiment rationale
**Status**: ✅ COMPLETE

#### 0.5.2 Create Experimental Chain Prompting Service
**File**: `services/accuracy_service_chain_prompting.py`
**Approach**: TDD with @agent-tdd-enforcer

**Interface** (matches original for easy swapping):
```python
class ChainPromptingAccuracyService:
    def generate_accuracy_critical_content(transcript_text, episode_info, language):
        """Same interface as HighAccuracyContentService for easy A/B testing"""
```

**Internal Methods** (each = separate focused API call):
- `_generate_quotable_moments()` - One focused call for quotes only
- `_generate_reel_suggestions()` - One focused call for reels only
- `_generate_content_warnings()` - One focused call for warnings only
- `_generate_chapter_timestamps()` - **TWO-STEP CHAIN**:
  1. API Call 1: Get chapter titles WITHOUT timestamps (JSON array of titles)
  2. Loop: For each title → API Call to find SPECIFIC timestamp for that chapter

**Why Two-Step Chain for Chapters?**
```
Instead of: "Find all chapters with timestamps in 6000 token context"
Do this:
  Step 1: "What are the main chapter topics?"
    → ["החידלון הרעיוני", "משל הצוללת", "שלושת הרעיונות המתים"]

  Step 2a: "Find timestamp where 'החידלון הרעיוני' begins"
  Step 2b: "Find timestamp where 'משל הצוללת' begins"
  Step 2c: "Find timestamp where 'שלושת הרעיונות המתים' begins"
```
This gives Gemini a **focused search task** instead of "find everything at once".

**Tests to Write FIRST**:
```python
def test_each_task_uses_separate_api_call()
def test_quotable_moments_call_is_independent()
def test_reel_suggestions_call_is_independent()
def test_chapter_generation_is_two_step_chain()
def test_chapter_step1_returns_titles_without_timestamps()
def test_chapter_step2_finds_timestamp_for_specific_title()
def test_timestamps_accurate_for_quotes_at_3min()
def test_timestamps_accurate_for_quotes_at_15min()
def test_timestamps_accurate_for_quotes_at_40min()
```

**Status**: ⏳ PENDING

#### 0.5.3 Add A/B Testing Flag to Orchestrator
**File**: `services/content_orchestrator.py`

**Changes**:
- Add parameter: `use_chain_prompting=False` (default to original for safety)
- If True → instantiate and use `ChainPromptingAccuracyService`
- If False → use original `HighAccuracyContentService`

**Purpose**: Allows running BOTH services on same transcript for direct comparison.

**Status**: ⏳ PENDING

#### 0.5.4 Manual Testing & Verification
**Goal**: A/B test both services on real 30+ minute transcript

**Test Data Points** (manually verify):
- Quote at ~3 minutes (where Gemini starts degrading)
- Quote at ~8 minutes
- Quote at ~15 minutes (medium difficulty)
- Quote at ~25 minutes (hard)
- Quote/reel at ~40+ minutes (critical - worst accuracy zone)
- 2 chapter timestamps from mid/late episode

**Comparison Metrics**:
- Timestamp accuracy (within 5 seconds = pass)
- Quote exact match (word-for-word = pass)
- Old service vs New service side-by-side

**Document in**: PROGRESS.md under "Phase 0.5 Results"

**Status**: ⏳ PENDING

#### 0.5.5 Decision Point

**Measure**: Timestamp accuracy across different time ranges

**Outcome 1 - SUCCESS (90%+ accuracy across full episode)**:
- ✅ Ship it! Update orchestrator to default `use_chain_prompting=True`
- ✅ Defer RAG to future enhancement (if ever needed)
- ✅ Document findings: Task separation solved the problem

**Outcome 2 - PARTIAL IMPROVEMENT (works 0-10min, still fails 15min+)**:
- ✅ Document findings: Task separation helps but insufficient for long context
- ✅ Proves reducing cognitive load per call improves accuracy
- ✅ Proceed to Phase 1 (RAG) knowing we need chunked retrieval
- ✅ Consider: Combine chain prompting + RAG for best results

**Outcome 3 - NO IMPROVEMENT**:
- ✅ Delete experimental file
- ✅ Proceed to Phase 1 (RAG) - confirms long context is the core issue
- ✅ Document: Task separation alone insufficient

**Status**: ⏳ PENDING

---

### ⏳ Phase 1: RAG-Based Chunked Retrieval System
**Goal**: Prevent errors by giving Gemini focused context through vector retrieval
**Status**: PENDING (may be skipped if Phase 0.5 succeeds)
**Duration**: 2-3 sessions
**Approach**: TDD with @agent-tdd-enforcer throughout

#### 1.1 Create Transcript Chunking Service
**File**: `services/transcript_chunker.py`

**Tests to Write FIRST** (with tdd-enforcer):
```python
def test_semantic_chunking_preserves_speaker_boundaries()
def test_each_chunk_includes_timestamp_metadata()
def test_chunk_size_is_200_to_400_tokens()
def test_hebrew_and_english_chunking_works_identically()
def test_chunk_overlap_provides_context()
```

**Technical Specs**:
- Semantic chunking (not fixed-size)
- Include timestamp metadata (start_time, end_time, speaker)
- Target: 200-400 tokens per chunk
- 10-20% overlap between chunks for context
- Preserve speaker boundaries

**Implementation**:
- Use sentence embeddings to detect topic shifts
- Split at semantic boundaries
- Add metadata from raw-transcript.json

#### 1.2 Create Vector Search Service
**File**: `services/vector_search_service.py`

**Tests to Write FIRST** (with tdd-enforcer):
```python
def test_index_transcript_chunks_with_timestamp_metadata()
def test_search_returns_top_k_relevant_chunks_with_timestamps()
def test_metadata_filtering_by_time_range_works()
def test_works_for_both_hebrew_and_english()
def test_semantic_search_finds_meaning_not_keywords()
```

**Technical Specs**:
- Use ChromaDB for vector storage
- Use `paraphrase-multilingual-MiniLM-L12-v2` for embeddings
- Support metadata filtering (time range, speaker)
- Pre-filtering approach (filter → search)

**Implementation**:
```python
import chromadb
from sentence_transformers import SentenceTransformer

class VectorSearchService:
    def __init__(self):
        self.client = chromadb.Client()
        self.embedding_model = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'
        )

    def index_transcript(self, chunks):
        """Index chunks with timestamp metadata"""

    def search(self, query, time_range=None, top_k=5):
        """Search with optional time filtering"""
```

#### 1.3 Redesign Accuracy Service with RAG
**File**: `services/accuracy_service_v2.py`

**Tests to Write FIRST** (with tdd-enforcer):
```python
def test_finding_quotes_uses_vector_search_not_full_transcript()
def test_each_task_gets_separate_focused_call()
def test_timestamps_verified_against_chunk_metadata()
def test_works_for_quotes_at_3min_15min_40min_marks()
def test_focused_context_reduces_token_usage()
```

**Architecture Change**:
```python
# OLD: Single call with full transcript
def generate_accuracy_critical_content(transcript_text):
    prompt = f"TRANSCRIPT: {transcript_text}\nFind quotes, reels, chapters..."
    return gemini.generate(prompt)

# NEW: RAG-based with focused chunks
def generate_accuracy_critical_content(transcript_text, raw_transcript_json):
    # 1. Chunk and index
    chunks = chunker.chunk_transcript(transcript_text, raw_transcript_json)
    vector_search.index_transcript(chunks)

    # 2. Task-specific retrieval and generation
    quotes = self._find_quotable_moments(vector_search)
    reels = self._find_reel_suggestions(vector_search)
    chapters = self._generate_chapter_timestamps(vector_search)

    return {quotes, reels, chapters}

def _find_quotable_moments(self, vector_search):
    # Search for impactful statements
    relevant_chunks = vector_search.search(
        query="viral quotable impactful controversial surprising",
        top_k=5
    )

    quotes = []
    for chunk in relevant_chunks:
        # Give Gemini ONLY this chunk with timestamps
        prompt = f"""
        SEGMENT ({chunk.start_time} - {chunk.end_time}):
        {chunk.text}

        Find ONE quotable moment in THIS SEGMENT ONLY.
        Return exact quote and timestamp between {chunk.start_time} and {chunk.end_time}.
        """
        quote = self.gemini.generate(prompt)
        quotes.append(quote)

    return quotes
```

#### Dependencies to Add:
```
chromadb>=0.4.0
sentence-transformers>=2.3.0
```

---

### ⏳ Phase 2: Verification & Critic Services
**Goal**: Catch remaining errors through validation
**Status**: PENDING
**Duration**: 2 sessions
**Approach**: TDD with @agent-tdd-enforcer

#### 2.1 Create Verification Service
**File**: `services/verification_service.py`

**Tests to Write FIRST** (with tdd-enforcer):
```python
def test_finds_exact_timestamp_for_quoted_text_in_raw_json()
def test_detects_when_claimed_timestamp_is_off_by_more_than_5_seconds()
def test_returns_correction_suggestion()
def test_verifies_quote_exists_word_for_word_in_transcript()
def test_detects_acceptable_vs_unacceptable_paraphrasing()
def test_calculates_confidence_scores_correctly()
```

**Technical Approach**:
```python
class VerificationService:
    def __init__(self, raw_transcript_json, transcript_text):
        self.raw_json = raw_transcript_json
        self.transcript_text = transcript_text

    def verify_timestamp(self, quote_text, claimed_timestamp):
        """
        Returns:
        {
            "status": "ACCURATE" | "TIMESTAMP_ERROR" | "QUOTE_NOT_FOUND",
            "claimed": 325.0,
            "actual": 1935.0,
            "delta": 1610.0,
            "correction": "32:15",
            "confidence": 0.0
        }
        """

    def verify_quote_accuracy(self, quote_text):
        """
        Returns:
        {
            "match_type": "EXACT" | "PARAPHRASE_ACCEPTABLE" | "PARAPHRASE_UNACCEPTABLE",
            "original_text": "...",
            "confidence": 0.95
        }
        """
```

#### 2.2 Create Critic Service (Reflection Pattern)
**File**: `services/critic_service.py`

**Tests to Write FIRST** (with tdd-enforcer):
```python
def test_critic_receives_accuracy_service_output()
def test_runs_verification_on_each_timestamp_and_quote()
def test_returns_structured_critique_with_specific_errors()
def test_calculates_confidence_scores()
def test_provides_actionable_repair_suggestions()
def test_identifies_multiple_error_types()
```

**Critic Agent Persona**: "Meticulous timestamp auditor and fact-checker with zero tolerance for errors"

**Implementation**:
```python
class CriticService:
    def __init__(self, verification_service):
        self.verifier = verification_service

    def critique(self, accuracy_output):
        """
        Returns structured critique:
        {
            "overall_confidence": 0.67,
            "errors_found": 3,
            "critiques": [
                {
                    "item_id": "quote_1",
                    "error_type": "TIMESTAMP_ERROR",
                    "severity": "HIGH",
                    "claimed": "05:23",
                    "actual": "32:15",
                    "repair_action": "Update timestamp to 32:15"
                }
            ],
            "approved": False
        }
        """
```

---

### ⏳ Phase 3: Reflection Loop Integration
**Goal**: Iterative refinement until critic approves
**Status**: PENDING
**Duration**: 1-2 sessions
**Approach**: TDD with @agent-tdd-enforcer

#### 3.1 Add Reflection Loop to Accuracy Service V2

**Tests to Write FIRST** (with tdd-enforcer):
```python
def test_reflection_loop_runs_max_3_iterations()
def test_each_iteration_improves_based_on_critic_feedback()
def test_loop_exits_when_confidence_above_90_percent()
def test_prevents_infinite_loops()
def test_returns_metadata_with_iteration_count()
def test_structured_feedback_leads_to_specific_repairs()
```

**Workflow**:
```
1. Generate (RAG-based) → chunks retrieval → focused generation
2. Critic validates → verification service checks all timestamps/quotes
3. If errors found:
   - Provide structured feedback with specific repair actions
   - Producer refines using feedback
   - Go to step 2 (max 3 iterations)
4. If accurate (confidence > 0.90):
   - Return output with verification metadata
```

**Implementation**:
```python
def generate_with_reflection(self, transcript_text, raw_transcript_json, max_iterations=3):
    verifier = VerificationService(raw_transcript_json, transcript_text)
    critic = CriticService(verifier)

    for iteration in range(max_iterations):
        # Generate with RAG
        output = self.generate_accuracy_critical_content(
            transcript_text,
            raw_transcript_json
        )

        # Critic validates
        critique = critic.critique(output)

        if critique['approved']:
            # Success!
            return {
                **output,
                "verification_metadata": {
                    "iterations": iteration + 1,
                    "confidence": critique['overall_confidence'],
                    "verified": True
                }
            }

        # Not approved - refine based on structured feedback
        output = self._apply_critique_feedback(output, critique)

    # Max iterations reached
    return {
        **output,
        "verification_metadata": {
            "iterations": max_iterations,
            "confidence": critique['overall_confidence'],
            "verified": False,
            "warnings": "Max iterations reached without full approval"
        }
    }
```

---

### ⏳ Phase 4: Integration & Benchmarking
**Goal**: Wire everything together and measure success
**Status**: PENDING
**Duration**: 1 session

#### 4.1 Update Content Orchestrator
**File**: `services/content_orchestrator.py`

**Changes**:
- Add option to use `accuracy_service_v2.py` (RAG-based)
- Integrate verification metadata into output
- Add accuracy metrics reporting
- Flag low-confidence outputs

#### 4.2 Create Accuracy Benchmark Script
**File**: `tests/benchmark_accuracy.py`

**Not TDD** - this is measurement/reporting:
```python
def benchmark_accuracy():
    """
    Run on all test fixtures
    Compare generated vs ground truth

    Metrics:
    - Timestamp accuracy (% within 5 seconds)
    - Quote exact match rate
    - Average error delta
    - Performance by position (3min, 15min, 40min+)

    Output: Comparison report v1 vs v2
    """
```

#### 4.3 Generate Accuracy Reports
- Run benchmarks on all test fixtures
- Document improvements in this file
- Create comparison charts: old vs new approach

---

## 📁 Test Fixtures Strategy

### Fixture Requirements

**Critical**: Test fixtures must target Gemini's known failure patterns!

#### Episode Selection Criteria:
1. **LENGTH**: 30+ minutes (forces long context handling)
2. **LANGUAGE**: Mix of Hebrew and English episodes
3. **BOTH FORMATS**: transcript.txt + raw-transcript.json with word-level timestamps

#### Ground Truth Data Points Distribution:

**CRITICAL INSIGHT**: Gemini accuracy degrades after 3-5 minutes, not just late in episode!

For each test episode, manually verify:

| Time Mark | Difficulty | Test Purpose |
|-----------|-----------|--------------|
| ~3:30 | Medium | Where accuracy starts degrading |
| ~8:00 | Hard | Mid-early section |
| ~15:00 | Very Hard | Middle of long transcript |
| ~25:00 | Extreme | Late-middle section |
| ~40:00+ | Critical | Near end (worst accuracy) |

**Per Episode Ground Truth**:
- 5 quotes at different time marks (3min, 8min, 15min, 25min, 40min+)
- 2-3 reel suggestions from 10min+ onwards
- 3-5 chapter timestamps throughout episode
- **Total**: 10-13 verified data points per episode

### Test Fixtures Structure

```
tests/fixtures/
├── README.md (test strategy explanation)
├── episode_001_political_hebrew/
│   ├── transcript.txt
│   ├── raw-transcript.json
│   └── ground_truth.json  ← Manually verified!
├── episode_002_tech_english/
│   ├── transcript.txt
│   ├── raw-transcript.json
│   └── ground_truth.json
└── episode_003_interview_hebrew/
    ├── transcript.txt
    ├── raw-transcript.json
    └── ground_truth.json
```

### Ground Truth JSON Format

```json
{
  "episode_info": {
    "title": "Political Discussion Episode",
    "duration_minutes": 58.5,
    "language": "he",
    "difficulty": "hard - long transcript"
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
      "expected_gemini_error": "usually correct at this position"
    },
    {
      "id": "quote_3_mid",
      "text": "זה לא משהו שאנחנו יכולים להתעלם ממנו",
      "correct_timestamp_seconds": 1935.0,
      "correct_timestamp_formatted": "32:15",
      "speaker": "speaker_1",
      "difficulty": "very_hard",
      "location_in_transcript": "middle",
      "expected_gemini_error": "often returns early timestamp like 05:23 or 12:45"
    },
    {
      "id": "quote_5_late",
      "text": "בסופו של דבר, זה מסתכם בבחירה שלנו",
      "correct_timestamp_seconds": 3301.0,
      "correct_timestamp_formatted": "55:01",
      "speaker": "speaker_0",
      "difficulty": "critical",
      "location_in_transcript": "near_end",
      "expected_gemini_error": "almost always returns timestamp from first 20 minutes"
    }
  ],
  "verified_reels": [
    {
      "id": "reel_1_late_content",
      "title": "הרגע המכריע",
      "correct_start_seconds": 2725.0,
      "correct_end_seconds": 2790.0,
      "correct_start_formatted": "45:25",
      "correct_end_formatted": "46:30",
      "difficulty": "critical",
      "expected_gemini_error": "returns timestamps from early in episode"
    }
  ]
}
```

---

## 🎯 Design Decisions Log

### Decision 1: ChromaDB over Weaviate/FAISS
**Date**: 2025-10-01
**Reason**:
- Best for metadata filtering (critical for timestamp ranges)
- Designed specifically for RAG systems
- Simpler setup than Weaviate
- FAISS lacks native metadata support
**Reference**: See FINDINGS.md - Vector Database Selection

### Decision 2: Semantic Chunking over Fixed-Size
**Date**: 2025-10-01
**Reason**:
- Preserves conversational flow and context
- Respects speaker boundaries
- Better retrieval accuracy for coherent quotes
- Worth the extra computational cost
**Reference**: See FINDINGS.md - Chunking Strategies

### Decision 3: paraphrase-multilingual-MiniLM-L12-v2 Embeddings
**Date**: 2025-10-01
**Reason**:
- Supports both Hebrew and English natively
- 384-dimensional (good balance size/accuracy)
- Official sentence-transformers model
- Compatible with ChromaDB
**Reference**: See FINDINGS.md - Multilingual Embeddings

### Decision 4: Separate API Calls Per Task
**Date**: 2025-10-01
**Reason**:
- Prevents attention dilution (root cause of current problem)
- Each task gets focused 200-400 token context
- Clearer timestamp boundaries per chunk
- More controllable and debuggable
**Reference**: See FINDINGS.md - Problem Analysis

### Decision 5: 200-400 Token Chunk Size
**Date**: 2025-10-01
**Reason**:
- Large enough for meaningful context
- Small enough for model to maintain focus
- Research shows this range balances precision and context
**Reference**: Web research on chunking best practices 2025

### Decision 6: Max 3 Reflection Iterations
**Date**: 2025-10-01
**Reason**:
- Cost control (each iteration = new API call)
- Diminishing returns after 3 iterations
- Prevents infinite loops
- Industry standard for reflection patterns
**Reference**: See FINDINGS.md - Reflection Pattern

### Decision 7: Pre-Filtering Approach
**Date**: 2025-10-01
**Reason**:
- Filter by time range THEN search semantically
- More efficient when filtering reduces candidates significantly
- Better for our use case (often searching specific time segments)
**Reference**: See FINDINGS.md - Metadata Filtering

---

## 🗂️ Files Roadmap

### New Files to Create

**Documentation**:
- ✅ `knowledge/ACCURACY_ENHANCEMENT_FINDINGS.md` (research consolidation)
- 🔄 `ACCURACY_ENHANCEMENT_PROGRESS.md` (this file)
- ⏳ `tests/fixtures/README.md` (test strategy)

**Services** (Phase 1):
- ⏳ `services/transcript_chunker.py`
- ⏳ `services/vector_search_service.py`
- ⏳ `services/accuracy_service_v2.py`

**Services** (Phase 2):
- ⏳ `services/verification_service.py`
- ⏳ `services/critic_service.py`

**Tests**:
- ⏳ `tests/test_transcript_chunker.py`
- ⏳ `tests/test_vector_search_service.py`
- ⏳ `tests/test_accuracy_service_v2.py`
- ⏳ `tests/test_verification_service.py`
- ⏳ `tests/test_critic_service.py`
- ⏳ `tests/benchmark_accuracy.py`

**Test Fixtures**:
- ⏳ `tests/fixtures/episode_001_*/ground_truth.json`
- ⏳ `tests/fixtures/episode_002_*/ground_truth.json`
- ⏳ `tests/fixtures/episode_003_*/ground_truth.json`

### Files to Modify

- ⏳ `services/content_orchestrator.py` (integrate v2 services)
- ⏳ `requirements.txt` (add chromadb, sentence-transformers)

---

## 🚀 Next Session TODO

### Immediate Tasks:
1. ✅ Complete this document
2. ⏳ Create `tests/fixtures/README.md`
3. ⏳ Prepare test fixtures:
   - Find/create 2-3 real transcripts (30+ min, Hebrew + English)
   - Manually verify 10-13 ground truth data points per episode
   - Create `ground_truth.json` for each
4. ⏳ Review all documentation before starting Phase 1

### Phase 1 Kickoff:
1. Launch @agent-tdd-enforcer for `transcript_chunker.py`
2. Write tests first
3. Implement to pass tests
4. Move to `vector_search_service.py`

---

## 📊 Metrics Tracking

### Baseline (Current System)
- Timestamp accuracy 0-3min: ~80-90%
- Timestamp accuracy 3-5min: ~40-60%
- Timestamp accuracy 5-15min: ~20-40%
- Timestamp accuracy 15min+: ~5-15% ("wildly off")
- Quote accuracy: ~70% (many paraphrases)

### Target (New System)
- Timestamp accuracy (all ranges): 95%+ within 5 seconds
- Quote accuracy: 90%+ exact matches
- Confidence scores: Available for all outputs
- Verification rate: 100% of outputs validated

### Measurement Method
- Run `tests/benchmark_accuracy.py` on all test fixtures
- Compare generated vs ground truth
- Calculate accuracy by time position
- Generate comparison report

---

## 📝 Notes & Insights

### Key Insight 1: Root Cause
The problem isn't Gemini's quality - it's that we're asking it to hold 6,000 tokens in attention while generating timestamps. This is architectural, not a model limitation.

### Key Insight 2: RAG is the Solution
By giving Gemini focused 200-400 token chunks with explicit timestamp boundaries, we prevent the attention dilution that causes errors.

### Key Insight 3: Verification is Insurance
Even with RAG improvements, verification against raw-transcript.json provides ground truth validation and catches edge cases.

### Key Insight 4: Reflection Prevents Wasted Work
Rather than accepting first output, reflection loop ensures we don't return inaccurate data. Cost of 1-3 refinement iterations is far less than manual fixing later.

### Key Insight 5: Test Fixture Quality Matters
If we don't test specifically at 3min, 8min, 15min, 25min, 40min marks, we won't catch the failure patterns. Ground truth must target known weaknesses.

---

**End of Progress Tracking Document**
**Next**: Create `tests/fixtures/README.md` and prepare test fixtures
