# Accuracy Enhancement Research Findings

**Date**: 2025-10-01
**Project**: Map-Doc Automation - Timestamp & Quote Accuracy Improvement
**Goal**: Achieve 95%+ timestamp accuracy and 90%+ quote accuracy across full podcast episodes

---

## Table of Contents
1. [Problem Analysis](#problem-analysis)
2. [Reflection Pattern](#reflection-pattern)
3. [RAG Pattern (Retrieval-Augmented Generation)](#rag-pattern)
4. [Chunking Strategies](#chunking-strategies)
5. [Vector Database Selection](#vector-database-selection)
6. [Multilingual Embeddings](#multilingual-embeddings)
7. [Technical Implementation Details](#technical-implementation-details)
8. [Research Sources](#research-sources)

---

## Problem Analysis

### Current Issue
The `accuracy_service.py` currently uses Gemini 2.5 Pro to generate **ALL accuracy-critical content in a SINGLE API call**:

```python
# services/accuracy_service.py (line 38-48)
response = self.client.models.generate_content(
    model="gemini-2.5-pro",
    contents=prompt,  # Contains ENTIRE transcript (6000+ tokens!)
    config=GenerateContentConfig(...)
)
```

The prompt includes:
- Full transcript text (could be 30-60 minutes = 6,000+ tokens)
- Tasks: quotable_moments, reel_suggestions, chapter_timestamps, content_warnings

### Why This Fails

**Attention Dilution Problem:**
- For a 30-minute episode: ~4,500 words = ~6,000 tokens
- Model must hold entire context in attention
- When generating quote at minute 25, it has to "remember" where that was in the original 6,000 tokens
- **Result**: Timestamp accuracy degrades severely

**Observed Failure Pattern:**
- **0-3 minutes**: Gemini is roughly accurate
- **3-5 minutes**: Accuracy starts degrading noticeably
- **5+ minutes**: Timestamps are "wildly off" - often returns timestamps from early in episode
- **15+ minutes**: Very high error rate
- **40+ minutes**: Extreme inaccuracy

### Why Gemini Fails
1. **Quote at beginning** of transcript → Fresh in attention window → Accurate timestamp
2. **Quote after 5+ minutes** → Model must "look back" through thousands of tokens → Attention dilutes → Guesses or returns early timestamp

This is not a quality issue with the model - it's an **architectural problem** with how we're using it.

---

## Reflection Pattern

### Overview
The Reflection pattern involves an agent evaluating its own work and using that evaluation to improve its performance through iterative refinement.

**Source**: Chapter 4: Reflection (Google Docs PDF)

### Key Process Steps
1. **Execution**: Agent performs task or generates initial output
2. **Evaluation/Critique**: Agent (or separate critic) analyzes the result
3. **Reflection/Refinement**: Based on critique, determines how to improve
4. **Iteration**: Refined output can be re-evaluated until satisfactory

### Producer-Critic Architecture

**Most Effective Implementation**: Separate the process into two distinct roles:

#### The Producer Agent
- Primary responsibility: Perform initial execution of task
- Focuses on generating content (code, text, plans)
- Takes initial prompt and produces first version

#### The Critic Agent
- Sole purpose: Evaluate the Producer's output
- Given different instructions/persona (e.g., "You are a meticulous fact-checker")
- Analyzes work against specific criteria
- Designed to find flaws and suggest improvements

**Key Benefit**: Prevents "cognitive bias" of agent reviewing its own work. Critic approaches output with fresh perspective.

### Workflow
```
Producer generates → Critic validates → Producer refines → Repeat
```

**Stopping Conditions**:
- Critic confirms satisfactory quality
- Maximum iterations reached (typically 3-5)

### Application to Timestamp Accuracy

**Producer**: Gemini 2.5 Pro generating quotes/reels with timestamps
**Critic**: Verification agent that:
- Checks each timestamp against raw-transcript.json (word-level timestamps)
- Validates quotes exist word-for-word
- Identifies errors and provides specific corrections
- Returns structured feedback

**Example Critic Output**:
```json
{
  "quote_1": {
    "status": "TIMESTAMP_ERROR",
    "claimed_timestamp": "05:23",
    "actual_timestamp": "32:15",
    "error_delta": "26:52",
    "correction": "Quote appears at 32:15, not 05:23"
  },
  "quote_2": {
    "status": "ACCURATE",
    "confidence": 0.98
  }
}
```

### RAG-Critic: Advanced Implementation

**Source**: ACL 2025 - "RAG-Critic: Leveraging Automated Critic-Guided Agentic Workflow for Retrieval Augmented Generation"

**Key Innovation**: Designs a critic-guided agentic RAG workflow that:
- Customizes executor-based solution flows based on error-critic model feedback
- Facilitates error-driven self-correction process
- Progressively aligns error-critic model using coarse-to-fine training

**Research Code**: https://github.com/RUC-NLPIR/RAG-Critic

### Structured Reflection for Error Recovery

**Source**: ArXiv 2509.18847 - "Failure Makes the Agent Stronger: Enhancing Accuracy through Structured Reflection"

**Key Findings**:
- Structured reflection turns the path from error to repair into an explicit, controllable, trainable action
- Agent produces short yet precise reflection:
  - Diagnoses failure using evidence from previous step
  - Proposes correct, executable follow-up call
- Experiments show large gains in multi-turn tool-call success and error recovery

**Implication for Our Project**: We should make reflection explicit with specific error diagnoses and repair actions, not just generic "try again" feedback.

---

## RAG Pattern (Retrieval-Augmented Generation)

### Overview
RAG enables LLMs to access and integrate external, current, and context-specific information before generating responses.

**Source**: Chapter 14: Knowledge Retrieval (RAG) - Google Docs PDF

### Core Process
1. **User Query** → System doesn't send directly to LLM
2. **Retrieval** → Search external knowledge base for relevant information
3. **Augmentation** → Add retrieved snippets to original prompt
4. **Generation** → LLM generates response grounded in retrieved data

### Core Concepts

#### Embeddings
Numerical representations of text in vector form. Words/phrases with similar meanings have embeddings close together in vector space.

Example (simplified 2D):
- "cat" → (2.0, 3.0)
- "kitten" → (2.1, 3.1)
- "car" → (8.0, 1.0)

Real embeddings: 384-768+ dimensions

#### Semantic Similarity
Measure of how alike two pieces of text are based on **meaning**, not just word overlap.

Example:
- "furry feline companion" vs "domestic cat" → HIGH semantic similarity despite no word overlap
- Calculated using distance between embeddings (cosine similarity)

#### Text Chunking
Breaking large documents into smaller pieces that preserve context.

**Why Critical for RAG**:
- Can't feed entire 60-minute transcript to LLM in every query
- Chunk into manageable pieces (e.g., by paragraph, topic, time segment)
- Retrieve only relevant chunks for each query

#### Vector Databases
Specialized databases for storing and querying embeddings efficiently.

**Key Capability**: Semantic search
- Traditional search: Find exact words
- Vector search: Find similar **meanings**
- Can find results even if user's phrasing is completely different from source

### Agentic RAG

**Standard RAG**: Retrieve → Augment → Generate (passive pipeline)

**Agentic RAG**: Introduces reasoning layer that actively:
1. **Evaluates** source quality and relevance
2. **Reconciles** conflicting information
3. **Decomposes** complex queries into sub-queries
4. **Uses external tools** to fill knowledge gaps

**Source**: MarkTechPost, Weaviate, IBM - "What is Agentic RAG? (2025)"

#### Key Capabilities

**1. Reflection and Source Validation**
Example: User asks "What is our remote work policy?"
- Standard RAG: Pulls up 2020 blog post AND 2025 official policy
- Agentic RAG: Analyzes metadata, recognizes 2025 policy as authoritative, discards blog

**2. Knowledge Conflict Resolution**
Example: Two documents claim different budget amounts
- Identifies contradiction
- Prioritizes more reliable source (financial report over proposal)
- Provides verified figure

**3. Multi-Step Reasoning**
Example: "Compare our product to Competitor X"
- Decomposes into sub-queries:
  - Search our product features
  - Search our pricing
  - Search competitor features
  - Search competitor pricing
- Synthesizes comprehensive comparison

**4. Knowledge Gap Identification**
Example: "Market reaction to product launched yesterday?"
- Searches internal knowledge base → No recent info
- Recognizes gap
- Activates external tool (web search API)
- Provides up-to-date answer

### Application to Timestamp Accuracy

**Our RAG Strategy**:
1. **Chunk transcript** into semantically meaningful segments with timestamp metadata
2. **Index chunks** in vector database (ChromaDB)
3. **For each task** (quotes, reels, chapters):
   - Search for relevant chunks
   - Retrieve ONLY relevant segments with timestamps
   - Give Gemini focused context instead of full transcript
4. **Verify** timestamps against raw-transcript.json

**Example - Finding Quotable Moment**:
```python
# Instead of full transcript (6000 tokens):
prompt = f"TRANSCRIPT: {entire_transcript}\n Find quotable moments..."

# Use RAG:
relevant_chunks = vector_search("viral quotable impactful statements", top_k=5)

for chunk in relevant_chunks:
    prompt = f"""
    SEGMENT ({chunk.start_time} - {chunk.end_time}):
    {chunk.text}

    Find ONE quotable moment in THIS SEGMENT ONLY.
    Timestamp must be between {chunk.start_time} and {chunk.end_time}.
    """
    # Model only sees 200-400 tokens with exact time boundaries
```

---

## Chunking Strategies

**Sources**: Pinecone, Weaviate, Analytics Vidhya, Databricks - "Chunking Strategies for RAG 2025"

### Fixed-Size Chunking

**Approach**: Split text into predetermined sizes (e.g., 512 tokens)

**Pros**:
- Simple, fast, computationally cheap
- Consistent chunk sizes
- No NLP libraries needed

**Cons**:
- Can cut mid-sentence or mid-word
- Breaks semantic units
- May contain unrelated information
- Poor retrieval accuracy

**Best For**: Simple use cases, prototyping

### Semantic Chunking

**Approach**: Break text at meaningful boundaries based on semantic shifts

**How It Works**:
1. Embed each sentence
2. Calculate cosine distance between consecutive sentence embeddings
3. Identify large distance jumps (topic changes)
4. Split at those boundaries

**Pros**:
- Preserves meaning and context
- Natural conversation flow maintained
- Better retrieval accuracy
- Each chunk is coherent semantic unit

**Cons**:
- More computationally expensive
- Requires embedding model
- Variable chunk sizes

**Best For**: Long-form content, conversations, maintaining context

### Recursive Chunking

**Approach**: Iterate through separators ("\n\n", "\n", " ", "") until preferred chunk size achieved

**Benefit**: Keeps paragraphs, sentences, words together as much as possible

### Document-Based / Markdown-Aware Chunking

**Approach**: Respect document structure (headers, sections, paragraphs)

**Benefit**: Outperforms naive splits by 5-10 percentage points when metadata preserved

### Agentic Chunking

**Approach**: LLM dynamically decides how to split based on:
- Semantic meaning
- Content structure
- Density

**Benefit**: Most intelligent but most expensive

### Recommendation for Podcast Transcripts

**Use Semantic Chunking** because:
1. Preserves conversational flow
2. Keeps related topics together
3. Respects speaker changes
4. Better for finding coherent quotes/moments

**Specifications**:
- Target chunk size: 200-400 tokens
- Embed using multilingual model
- Include timestamp metadata (start_time, end_time)
- Preserve speaker boundaries
- Allow 10-20% overlap between chunks for context

**Why 200-400 tokens?**
- Large enough for meaningful context
- Small enough for model to focus
- Balances retrieval precision and context preservation

---

## Vector Database Selection

**Sources**: DataCamp, Medium, LiquidMetal AI - "Vector Database Comparison 2025"

### Comparison: ChromaDB vs Weaviate vs FAISS

#### ChromaDB ✅ **CHOSEN**

**Strengths**:
- **Metadata filtering during search** (critical for timestamps!)
- Built-in persistence with DuckDB and Parquet
- Designed specifically for RAG systems
- Seamless LangChain integration
- Low-latency performance
- Easy setup for prototyping

**Best For**:
- Small to medium datasets (10k-200k vectors)
- Real-time applications
- Timestamp/metadata filtering requirements ← **Our use case!**

**Why Chosen**:
- Supports metadata filtering natively
- Can filter by time range: `where={"start_time": {"$gte": 300, "$lte": 600}}`
- Perfect for RAG systems that need filtered retrieval

#### Weaviate (Strong Alternative)

**Strengths**:
- Combines vector search with keyword filtering
- GraphQL APIs
- Real-time querying
- Multi-modal data support
- Production-ready features

**Best For**:
- Enterprise applications
- Complex metadata relationships
- Hybrid search (semantic + filtered)

**Why Not Chosen**: More complex setup, overkill for our needs

#### FAISS (Not Suitable)

**Strengths**:
- Extremely fast (200k-10M+ vectors)
- GPU acceleration
- Low-level optimization

**Cons**:
- **No built-in metadata support** ← Deal-breaker!
- Requires external database for metadata
- More complex architecture

**Why Not Chosen**: Lack of native metadata filtering

### Metadata Filtering Approaches

**Pre-filtering** (Our choice):
1. Filter chunks by metadata (time range, speaker)
2. Then apply vector similarity search on filtered set
3. More efficient when filtering significantly reduces candidate set

**Post-filtering**:
1. Vector similarity search first
2. Filter results by metadata after
3. Better when most results pass filter

**Hybrid**:
- Combine both based on query characteristics

### ChromaDB Implementation Details

**Collection Setup**:
```python
import chromadb
client = chromadb.Client()

collection = client.create_collection(
    name="podcast_transcript_chunks",
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)
```

**Adding Chunks with Metadata**:
```python
collection.add(
    documents=[chunk.text],
    metadatas=[{
        "start_time": chunk.start_seconds,
        "end_time": chunk.end_seconds,
        "speaker": chunk.speaker,
        "episode_id": episode.id
    }],
    ids=[chunk.id]
)
```

**Querying with Time Range Filter**:
```python
results = collection.query(
    query_texts=["viral quotable moment"],
    n_results=5,
    where={
        "$and": [
            {"start_time": {"$gte": 180}},  # After 3 minutes
            {"end_time": {"$lte": 600}}      # Before 10 minutes
        ]
    }
)
```

---

## Multilingual Embeddings

**Sources**: Sentence-Transformers docs, Hugging Face, Hebrew NLP Resources

### Requirements
- Support **Hebrew** and **English** in same model
- Compatible with sentence-transformers library
- Good semantic understanding for both languages
- Reasonable model size for local embedding

### Model Options

#### Option 1: paraphrase-multilingual-MiniLM-L12-v2 ✅ **CHOSEN**

**Specs**:
- **384-dimensional** embeddings
- Supports 50+ languages including Hebrew and English
- **Evaluated on 15+ languages** including Hebrew
- Part of sentence-transformers ecosystem
- Model size: ~120MB

**Performance**:
- Balanced accuracy and speed
- Good for clustering and semantic search
- Pretrained on paraphrase data

**Usage**:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Works for both Hebrew and English
embeddings_he = model.encode(["שלום עולם", "זה טקסט בעברית"])
embeddings_en = model.encode(["hello world", "this is English text"])
```

**Why Chosen**:
- Official sentence-transformers model
- Proven multilingual support
- Lightweight and fast
- Compatible with ChromaDB

#### Option 2: imvladikon/sentence-transformers-alephbert

**Specs**:
- Hebrew-specific model
- Distillation of LaBSE model
- 768-dimensional embeddings

**When to Use**: If Hebrew-only or Hebrew performance critical

#### Option 3: LaBSE (Language-Agnostic BERT Sentence Embedding)

**Specs**:
- 768-dimensional embeddings
- Trained on 109 languages
- Larger model size

**Why Not Chosen**: Overkill, larger size, similar performance

### Integration with ChromaDB

ChromaDB uses `sentence-transformers` by default:

```python
import chromadb
from chromadb.utils import embedding_functions

# Use multilingual model
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

collection = client.create_collection(
    name="podcast_chunks",
    embedding_function=embedding_function
)
```

---

## Technical Implementation Details

### Quote Extraction Accuracy Improvement

**Source**: MarkTechPost - "Enhancing Retrieval-Augmented Generation: Efficient Quote Extraction" (January 2025)

**LLMQuoter Approach**:
- Built on LLaMA-3B architecture
- Fine-tuned with Low-Rank Adaptation (LoRA)
- Identifies key textual evidence **before** reasoning
- Reduces cognitive load on model

**Results**:
- LLAMA 1B with extracted quotes: **62.2% accuracy**
- LLAMA 1B with full context: **24.4% accuracy**
- **2.5x improvement** by using quotes instead of full context!

**Implication**: Our RAG-based approach (focused chunks) should dramatically improve accuracy vs full transcript.

### Timestamp Verification Strategy

**Approach**: Use raw-transcript.json with word-level timestamps as ground truth

**raw-transcript.json Structure**:
```json
{
  "words": [
    {"word": "hello", "start": 5.2, "end": 5.4, "speaker": "speaker_0"},
    {"word": "world", "start": 5.5, "end": 5.8, "speaker": "speaker_0"}
  ]
}
```

**Verification Process**:
1. Extract quote text from generated output
2. Search for exact phrase in raw JSON
3. Compare claimed timestamp vs actual start time
4. Calculate error delta
5. If delta > 5 seconds → Flag as error and provide correction

**Example Code**:
```python
def verify_timestamp(quote_text, claimed_timestamp_seconds, raw_transcript_json):
    # Find quote in word-level transcript
    actual_position = find_phrase_in_transcript(quote_text, raw_transcript_json)

    if not actual_position:
        return {"error": "QUOTE_NOT_FOUND", "confidence": 0.0}

    actual_timestamp = actual_position['start_time']
    delta = abs(claimed_timestamp_seconds - actual_timestamp)

    if delta < 5:
        return {"status": "ACCURATE", "confidence": 0.95, "delta": delta}
    else:
        return {
            "status": "TIMESTAMP_ERROR",
            "claimed": claimed_timestamp_seconds,
            "actual": actual_timestamp,
            "delta": delta,
            "correction": format_timestamp(actual_timestamp)
        }
```

### Semantic Search Implementation

**Query Strategy**:
```python
# For finding quotable moments
query = "impactful viral quotable controversial surprising statement"

# For finding reel-worthy segments
query = "engaging entertaining funny dramatic emotional conflict"

# For finding chapter boundaries
query = "topic change subject transition new discussion theme"
```

**Hybrid Retrieval**:
- Semantic search for general relevance
- Metadata filtering for time constraints
- Combine scores for final ranking

---

## Research Sources

### Academic Papers

1. **RAG-Critic: Leveraging Automated Critic-Guided Agentic Workflow for RAG**
   - ACL 2025 (Vienna, Austria)
   - https://aclanthology.org/2025.acl-long.179/
   - Code: https://github.com/RUC-NLPIR/RAG-Critic

2. **Failure Makes the Agent Stronger: Structured Reflection for Reliable Tool Interactions**
   - ArXiv 2509.18847
   - https://arxiv.org/abs/2509.18847

3. **Enhancing RAG: Efficient Quote Extraction for Scalable and Accurate NLP Systems**
   - MarkTechPost, January 2025
   - LLMQuoter: 62.2% vs 24.4% accuracy improvement

4. **Training Language Models to Self-Correct via Reinforcement Learning**
   - https://arxiv.org/abs/2409.12917

### Knowledge Base PDFs

1. **Chapter 4: Reflection - Google Docs**
   - Producer-Critic architecture
   - Reflection pattern overview
   - Iterative refinement process
   - Memory and goal-setting integration

2. **Chapter 14: Knowledge Retrieval (RAG) - Google Docs**
   - RAG core concepts (embeddings, semantic similarity)
   - Chunking strategies
   - Vector databases
   - Agentic RAG
   - GraphRAG

### Technical Documentation

1. **Sentence-Transformers Documentation**
   - https://sbert.net/
   - Multilingual models
   - Hebrew NLP resources

2. **ChromaDB Documentation**
   - Metadata filtering
   - Collection management
   - Pre/post filtering strategies

3. **LangChain RAG Tutorials**
   - https://python.langchain.com/docs/tutorials/rag/
   - Build RAG applications
   - Vector store integration

### Industry Resources (2025)

1. **"Chunking Strategies for RAG Applications"** - Databricks, Pinecone, Weaviate
2. **"Vector Database Comparison 2025"** - DataCamp, Medium, LiquidMetal AI
3. **"Agentic RAG: Use Cases and Tools"** - MarkTechPost, IBM, Weaviate
4. **"Timestamp-Aware RAG with Metadata Filtering"** - Multiple sources (2025)
5. **"25 Chunking Tricks for RAG That Devs Actually Use"** - Medium, August 2025

### Web Search Results Archive

All web searches performed 2025-10-01:
- "timestamp verification accuracy LLM RAG 2025"
- "quote extraction accuracy verification agent reflection pattern 2025"
- "agentic RAG verification critic agent timestamp podcast transcription 2025"
- "chunking strategies for long transcripts RAG semantic search 2025"
- "timestamp-aware RAG vector search with metadata filtering 2025"
- "semantic chunking vs fixed-size chunking for podcast transcripts RAG"
- "sentence-transformers embeddings for Hebrew and English multilingual 2025"
- "ChromaDB Weaviate FAISS best for timestamp metadata filtering RAG 2025"

---

## Key Takeaways

### Architecture Decision
**Move from**: Single API call with full transcript (6000 tokens)
**Move to**: RAG-based chunked retrieval (200-400 tokens per call)

### Technology Stack
- **Vector DB**: ChromaDB (metadata filtering)
- **Embeddings**: paraphrase-multilingual-MiniLM-L12-v2 (Hebrew + English)
- **Chunking**: Semantic chunking (200-400 tokens)
- **Verification**: raw-transcript.json word-level timestamps

### Patterns Applied
1. **Reflection Pattern**: Producer-Critic architecture with structured feedback
2. **RAG Pattern**: Chunk → Index → Retrieve → Generate
3. **Agentic RAG**: Active reasoning, verification, multi-step decomposition

### Expected Improvements
- **Timestamp accuracy**: From "wildly off after 3min" to **95%+ within 5 seconds**
- **Quote accuracy**: **90%+ exact matches** (vs current paraphrasing issues)
- **Cost**: Similar or better (focused context = fewer tokens)
- **Confidence**: Every output includes verification scores

---

**End of Research Findings Document**
**Next**: See `ACCURACY_ENHANCEMENT_PROGRESS.md` for implementation roadmap
