# 🧪 TESTIT.MD — The Complete Beginner-to-Intermediate Guide & Testing Manual

> **Project:** English–Hindi Cross-Lingual Academic Textbook RAG (Retrieval-Augmented Generation)  
> **Target Audience:** Anyone with intermediate AI/software knowledge who wants an intuitive, crystal-clear explanation of the whole system without academic gatekeeping.  
> **Includes:** Step-by-step testing commands, ASCII architectural diagrams for every module, real code walkthroughs, and error diagnostics.

---

## 📑 Table of Contents

1. [The Big Picture: What Problem Are We Solving?](#1-the-big-picture-what-problem-are-we-solving)
2. [The 4 Systems at a Glance](#2-the-4-systems-at-a-glance)
3. [Quickstart: How to Test the Project in 5 Minutes](#3-quickstart-how-to-test-the-project-in-5-minutes)
4. [Master End-to-End Dataflow Diagram](#4-master-end-to-end-dataflow-diagram)
5. [Module-by-Module Deep Dive (with ASCII Diagrams)](#5-module-by-module-deep-dive-with-ascii-diagrams)
   - [§ 5.1 `config.yaml` — Master Blueprint](#-51-configyaml--master-blueprint)
   - [§ 5.2 `src/utils.py` — Foundation & Stopwatch](#-52-srcutilspy--foundation--stopwatch)
   - [§ 5.3 `src/chunking.py` — Page-Aware Flashcard Cutter](#-53-srcchunkingpy--page-aware-flashcard-cutter)
   - [§ 5.4 `src/ingestion.py` — PDF & Note Extractor](#-54-srcingestionpy--pdf--note-extractor)
   - [§ 5.5 `src/embeddings.py` — Words to Hypersphere Coordinates](#-55-srcembeddingspy--words-to-hypersphere-coordinates)
   - [§ 5.6 `src/vector_store.py` — FAISS Fast Search & NumPy Fallback](#-56-srcvector_storepy--faiss-fast-search--numpy-fallback)
   - [§ 5.7 `src/translation.py` — Google Translate Bridge](#-57-srctranslationpy--google-translate-bridge)
   - [§ 5.8 `src/retrieval.py` — Search Coordinator & Evidence Formatter](#-58-srcretrievalpy--search-coordinator--evidence-formatter)
   - [§ 5.9 `src/generation.py` — Zero-Temperature LLM Engine](#-59-srcgenerationpy--zero-temperature-llm-engine)
   - [§ 5.10 `src/pipelines.py` — Master Conductor (Systems A, B, C, D)](#-510-srcpipelinespy--master-conductor-systems-a-b-c-d)
   - [§ 5.11 `src/logging_utils.py` — Atomic Flight Recorder](#-511-srclogging_utilspy--atomic-flight-recorder)
   - [§ 5.12 `src/observability.py` — X-Ray Waterfall Tracer](#-512-srcobservabilitypy--x-ray-waterfall-tracer)
   - [§ 5.13 `src/evaluation.py` — Exam Grader & E1–E4 Taxonomy](#-513-srcevaluationpy--exam-grader--e1e4-taxonomy)
   - [§ 5.14 `app.py` — Interactive Streamlit Dashboard](#-514-apppy--interactive-streamlit-dashboard)
   - [§ 5.15 `tests/test_basic_pipeline.py` — 7-Stage Health Checker](#-515-teststest_basic_pipelinepy--7-stage-health-checker)
6. [The E1–E4 Scientific Error Taxonomy](#6-the-e1e4-scientific-error-taxonomy)
7. [Hands-On Manual Testing Recipes](#7-hands-on-manual-testing-recipes)
8. [Troubleshooting & Common Gotchas](#8-troubleshooting--common-gotchas)

---

## 1. The Big Picture: What Problem Are We Solving?

Imagine an Indian engineering undergraduate studying for an Operating Systems or Algorithms university exam.

```
+-----------------------------------------------------------------------------------------+
|                               THE CORE RESEARCH PROBLEM                                 |
+-----------------------------------------------------------------------------------------+

     [STUDENT'S BRAIN]                                         [THE TEXTBOOKS]
Thinks, deliberates, and asks                            Cormen (Algorithms), Galvin (OS),
      questions in HINDI:                               Tanenbaum (Networks) written in:
               |                                                       |
               v                                                       v
  "डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक                             "Dijkstra's algorithm fails on
   किनारों पर क्यों विफल हो जाता है?"                          negative edge weights because
               |                                                the greedy choice property..."
               |                                                       ^
               |                                                       |
               +=================== THE LANGUAGE GAP ==================+
                                           |
                                           |
                     How do we connect this Hindi question 
                     to the exact English textbook page?
```

There are two primary ways an AI can solve this:

```
                      +---------------------------------------+
                      |       TWO WAYS TO BRIDGE THE GAP      |
                      +---------------------------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
                v                                                   v
   [STRATEGY 1: TRANSLATION]                           [STRATEGY 2: BILINGUAL AI]
         (System C)                                           (System D)
                |                                                   |
 1. Translate Hindi question to                      1. Don't translate words!
    English first via Google Translate.              2. Project both Hindi and English
 2. Search English textbook index with                  into the SAME shared mental
    English words.                                      concept space (vectors).
 3. Feed evidence to LLM & answer in Hindi.          3. Direct search -> Answer in Hindi.
                |                                                   |
      "Slower (3.3 seconds),                              "Lightning fast (0.19 sec),
       risks translation errors"                           zero translation step!"
```

This research project tests **which method is faster, more accurate, and cheaper**, comparing them against standard baselines.

---

## 2. The 4 Systems at a Glance

We test **4 distinct pipelines** on the exact same questions:

```
===========================================================================================
                                 THE 4 SYSTEM TOPOLOGIES
===========================================================================================

[System A: Direct LLM Baseline] (Closed-Book Exam / Zero Retrieval)
 Hindi Question ──────────────────────────► [ LLM Brain ] ─────────────► Hindi Answer
                                          (No books consulted!)
 Risk: High hallucination rate.

-------------------------------------------------------------------------------------------

[System B: Monolingual English RAG] (The English Control Ceiling)
 English Question ──► [English Embedder] ──► [English FAISS] ──► Top Chunks ──┐
                                                                               ├──► [ LLM ] ──► En Answer
                                                              English Question ┘
 Role: Theoretical maximum accuracy (gold standard).

-------------------------------------------------------------------------------------------

[System C: Translation-Mediated RAG] (The Sequential Translator)
 Hindi Question ──► [Google Translate] ──► English Query ──┐
                                                           ▼
                     [English Embedder] ──► [English FAISS] ──► Top Chunks ──┐
                                                                             ├──► [ LLM ] ──► Hi Answer
                                                                Hindi Query ─┘
 Pros: Reuses English indexes. Cons: ~3.3 seconds slow, translation errors.

-------------------------------------------------------------------------------------------

[System D: Direct Multilingual RAG] (The Shared Bilingual Vector Space) ⚡
 Hindi Question ──► [Multilingual Embedder] ──► [Multi FAISS] ──► Top Chunks ──┐
                          (NO translation!)                                    ├──► [ LLM ] ──► Hi Answer
                                                                  Hindi Query ─┘
 Pros: 17.2x faster (193 ms!), immune to translation distortion.
===========================================================================================
```

---

## 3. Quickstart: How to Test the Project in 5 Minutes

All commands are run from the repository root: `d:\ai projects\rag research` using PowerShell.

```
       +-------------------------------------------------------+
       |             THE 6-STEP TESTING LADDER                 |
       +-------------------------------------------------------+
       |                                                       |
       |  [Step 1]  pytest test_basic_pipeline.py              |
       |            (Verify all 7 internal modules pass 100%)  |
       |                                   |                   |
       |  [Step 2]  python -m cross_lingual_rag.src.ingestion  |
       |            (Slice PDFs into page-bounded flashcards)  |
       |                                   |                   |
       |  [Step 3]  python -m cross_lingual_rag.src.vector_store|
       |            (Build English 768d & Multi 384d FAISS)    |
       |                                   |                   |
       |  [Step 4]  python -m cross_lingual_rag.src.pipelines  |
       |            (Run Systems A, B, C, D on benchmark)      |
       |                                   |                   |
       |  [Step 5]  python -m cross_lingual_rag.src.evaluation |
       |            (Score Recall@k, MRR, & E1-E4 errors)      |
       |                                   |                   |
       |  [Step 6]  streamlit run cross_lingual_rag/app.py     |
       |            (Launch interactive visual web dashboard)  |
       +-------------------------------------------------------+
```

### Step 1: Run the Automated Health-Check Tests
Checks unit normalization, page chunking, FAISS search, translation, and JSON schemas:
```powershell
python -m pytest cross_lingual_rag/tests/test_basic_pipeline.py -v
```
**Expected Output:**
```
collected 7 items
test_page_aware_chunking               PASSED [ 14%]
test_embeddings_normalization          PASSED [ 28%]
test_vector_store_build_and_search     PASSED [ 42%]
test_translation_service               PASSED [ 57%]
test_all_four_pipelines                PASSED [ 71%]
test_json_logging_schema               PASSED [ 85%]
test_evaluation_metrics_computation    PASSED [100%]
================ 7 passed in 22.15s ================
```

### Step 2: Ingest Textbooks & Generate Chunks Manifest
Scans `data/corpus/`, parses PDFs, fixes OCR hyphens, and creates flashcards:
```powershell
python -m cross_lingual_rag.src.ingestion
```
**Expected Output:**
```
[Ingestion] Scanning data/corpus across 5 subjects...
[Ingestion] Ingested 15 documents. Total Chunks: 84
[Ingestion] Saved manifest to: data/processed/chunks_manifest.json
[Ingestion] Saved metadata to: data/processed/corpus_metadata.json
```

### Step 3: Build the Dual FAISS Vector Indexes
Generates two separate FAISS vector databases from the exact same text chunks:
```powershell
python -m cross_lingual_rag.src.vector_store
```
**Expected Output:**
```
[VectorStore] Building English index (all-mpnet-base-v2, 768d)...
[VectorStore] Saved: data/indexes/english/index.faiss (84 vectors)
[VectorStore] Building Multilingual index (paraphrase-MiniLM-L12, 384d)...
[VectorStore] Saved: data/indexes/multilingual/index.faiss (84 vectors)
```

### Step 4: Run the Benchmark Across Systems A, B, C, & D
Executes questions against all 4 systems and logs atomic JSON files:
```powershell
python -m cross_lingual_rag.src.pipelines
```
**Expected Output:**
```
[Pipelines] Loaded 18 benchmark questions from data/benchmark/questions.csv
[Pipelines] Executing System A (Direct LLM)... Done (18 runs)
[Pipelines] Executing System B (Monolingual English)... Done (18 runs)
[Pipelines] Executing System C (Translation-Mediated)... Done (18 runs)
[Pipelines] Executing System D (Direct Multilingual)... Done (18 runs)
[Pipelines] All raw runs written to: results/raw/
```

### Step 5: Grade the Benchmark & Generate Reports
Scores Recall@1, Recall@3, Recall@5, MRR, nDCG@5, and classifies E1–E4 errors:
```powershell
python -m cross_lingual_rag.src.evaluation
```
**Expected Output:**
```
[Evaluation] Parsing raw logs from results/raw/...
[Evaluation] System C - Mean Recall@5: 0.8889 | MRR: 0.8333 | Mean Latency: 3327.6 ms
[Evaluation] System D - Mean Recall@5: 0.8333 | MRR: 0.7778 | Mean Latency: 193.0 ms
[Evaluation] Saved summary CSV to: results/csv/benchmark_results.csv
[Evaluation] Generated Markdown report: results/summaries/evaluation_report.md
```

### Step 6: Launch the Interactive Visual Lab
Opens the Streamlit visual workbench in your browser:
```powershell
streamlit run cross_lingual_rag/app.py
```
Open your browser to: `http://localhost:8501` to test queries visually, inspect traces, and view benchmark charts!

---

## 4. Master End-to-End Dataflow Diagram

```
+-----------------------------------------------------------------------------------------+
|                           COMPLETE SYSTEM ARCHITECTURE                                  |
+-----------------------------------------------------------------------------------------+

  [RAW TEXTBOOKS]                                                [BENCHMARK EXAM]
  data/corpus/*.pdf                                          data/benchmark/questions.csv
         │                                                               │
         ▼                                                               ▼
 ┌───────────────┐                                               ┌───────────────┐
 │ ingestion.py  │                                               │  question_hi  │
 └───────┬───────┘                                               └───────┬───────┘
         │                                                               │
         ▼                                                               │
 ┌───────────────┐                                                       │
 │  chunking.py  │ ──► chunks_manifest.json                              │
 └───────┬───────┘     (stable ID: {doc}_p{page}_c{idx})                 │
         │                                                               │
         ├───────────────────────────────┐                               │
         ▼                               ▼                               │
 ┌──────────────────────┐    ┌──────────────────────┐                    │
 │    embeddings.py     │    │    embeddings.py     │                    │
 │ (English MPNet 768d) │    │ (Multi MiniLM 384d)  │                    │
 └──────────┬───────────┘    └──────────┬───────────┘                    │
            │                           │                                │
            ▼                           ▼                                │
 ┌──────────────────────┐    ┌──────────────────────┐                    │
 │   vector_store.py    │    │   vector_store.py    │                    │
 │ data/indexes/english │    │data/indexes/multi    │                    │
 └──────────┬───────────┘    └──────────┬───────────┘                    │
            │                           │                                │
            │                           │      ┌─────────────────────────┘
            │                           │      │
            │                           │      │
     [FOR SYSTEM C]                     [FOR SYSTEM D]
            │                                  │
            ▼                                  ▼
 ┌──────────────────────┐            ┌──────────────────────┐
 │    translation.py    │            │    retrieval.py      │
 │ deep-translator (Hi->En)          │ (Direct Multi FAISS) │
 └──────────┬───────────┘            └──────────┬───────────┘
            │                                   │
            ▼                                   │
 ┌──────────────────────┐                       │
 │    retrieval.py      │                       │
 │ (English FAISS Top-5)│                       │
 └──────────┬───────────┘                       │
            │                                   │
            └─────────────────┬─────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  generation.py   │ ◄── prompts/rag_prompt_hindi.txt
                     │ (Gemini/Ollama)  │     (temperature: 0.0)
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   Hindi Answer   │ + Exact Book & Page Citation
                     └────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     ┌─────────────────┐             ┌─────────────────┐
     │ logging_utils.py│             │observability.py │
     │results/raw/*.json             │results/traces/* │
     └────────┬────────┘             └─────────────────┘
              ▼
     ┌─────────────────┐
     │ evaluation.py   │ ──► results/summaries/evaluation_report.md
     └─────────────────┘     results/csv/benchmark_results.csv
```

---

## 5. Module-by-Module Deep Dive (with ASCII Diagrams)

---

### § 5.1 `config.yaml` — Master Blueprint

#### 🎯 What is it?
The single file that locks down all model names, file paths, and hyperparameters so experiments are 100% reproducible and have zero "magic numbers" hardcoded in Python.

```
+-----------------------------------------------------------------------------------+
|                                    CONFIG.YAML                                    |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Paths]        -> Where raw PDFs, indexes, and logs are stored.                  |
|  [Embedding]    -> English: sentence-transformers/all-mpnet-base-v2 (768d)        |
|                    Multilingual: paraphrase-multilingual-MiniLM-L12-v2 (384d)     |
|                    normalize_embeddings: true                                     |
|  [Retrieval]    -> Top-K = 5, Chunk size = 700 tokens, Overlap = 80 tokens        |
|  [Generation]   -> Provider: "gemini" / "ollama" / "openai" / "mock"              |
|                    Temperature: 0.0 (Strictly deterministic!)                     |
|  [Translation]  -> deep-translator (Google Translate Web API, Free)                |
+-----------------------------------------------------------------------------------+
```

#### 💡 Why is `temperature = 0.0` critical?
If temperature is 0.7, asking the exact same question twice gives two slightly different answers because of random sampling. In scientific research, **sampling randomness ruins experiments**. Setting `temperature: 0.0` forces greedy decoding: the LLM becomes a deterministic mathematical function.

---

### § 5.2 `src/utils.py` — Foundation & Stopwatch

#### 🎯 What is it?
Foundational helper tools used by every other file.

```
+-----------------------------------------------------------------------------------+
|                                    UTILS.PY                                       |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  1. get_project_root() -> Dynamically finds config.yaml so relative file paths    |
|                           never crash regardless of where you run the script from.|
|  2. set_seed(42)       -> Locks random seeds for Python, NumPy, and PyTorch so    |
|                           vectors and math are identical across runs.             |
|  3. TimeTracker        -> High-precision stopwatch (time.perf_counter) context   |
|                           manager measuring sub-millisecond latencies.           |
+-----------------------------------------------------------------------------------+
```

---

### § 5.3 `src/chunking.py` — Page-Aware Flashcard Cutter

#### 🎯 What is it?
Cuts long textbook pages into clean text "flashcards" without ever crossing physical page boundaries.

```
+-----------------------------------------------------------------------------------+
|                        PAGE-AWARE CHUNKING PIPELINE                               |
+-----------------------------------------------------------------------------------+

   [Raw Physical Page Text] (e.g. Page 45 of Cormen's Algorithms)
              │
              ▼
   [Text Artifact Cleaning]  Removes OCR line-breaks: "algo-\nrithm" -> "algorithm"
              │
              ▼
   [Paragraph Splitting]     Splits text on "\n\n" paragraph blocks
              │
              ▼
   ┌────────────────────────────────────────────────────────┐
   │ Does paragraph fit in remaining token budget (<= 700)? │
   │  - YES: Add words to current chunk buffer.             │
   │  - NO:  Flush buffer to DocumentChunk, retain 80-token │
   │         overlap, and start next chunk.                 │
   └────────────────────────────────────────────────────────┘
              │
              ▼
   [Stable Deterministic Identifier Formula]
   chunk_id = doc_id + "_p" + page_number + "_c" + chunk_index
   Example:   "algo_clrs_p45_c1"
```

#### 💡 Why does this matter?
If an AI answers a student's question, it doesn't just say "I read this somewhere." It cites: **"Cormen Algorithms, Page 45, Chunk 1"**.

---

### § 5.4 `src/ingestion.py` — PDF & Note Extractor

#### 🎯 What is it?
Discovers all PDF textbooks and lecture notes in `data/corpus/`, reads them page-by-page using `pypdf`, passes them to `chunking.py`, and serializes the master catalog into `data/processed/chunks_manifest.json`.

```
  data/corpus/
  ├── algorithms/*.pdf         ──┐
  ├── automata/*.pdf           ──┤
  ├── dbms/*.pdf               ──┼──► [ ingestion.py ] ──► chunks_manifest.json
  ├── operating_systems/*.pdf  ──┤                        (All 84 flashcards saved)
  └── computer_networks/*.pdf  ──┘
```

---

### § 5.5 `src/embeddings.py` — Words to Hypersphere Coordinates

#### 🎯 What is it?
Turns text strings into lists of numbers (dense vectors) so a computer can compare meanings mathematically.

```
+-----------------------------------------------------------------------------------+
|                           EMBEDDING ARCHITECTURE                                  |
+-----------------------------------------------------------------------------------+

                    ┌───────────────────────────────┐
                    │    BaseEmbedder (Abstract)    │
                    └───────────────┬───────────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   ▼                                 ▼
  ┌─────────────────────────────────┐   ┌───────────────────────────┐
  │   SentenceTransformerEmbedder   │   │       MockEmbedder        │
  │  - all-mpnet-base-v2 (768d)     │   │ - Deterministic Hashing   │
  │  - paraphrase-multi-mpnet (384d)│   │ - Instant Offline / CI    │
  │  - L2-Unit Normalization        │   │ - Zero Dependencies       │
  └─────────────────────────────────┘   └───────────────────────────┘
```

#### 💡 The Math Made Simple: Why L2 Normalization is Genius
Cosine similarity measures the angle between two vectors:
$$\text{Cosine}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$
If we divide each vector by its length upon creation so its length is always exactly $1.0$ ($\|u\|_2 = 1.0$), the denominator becomes $1$:
$$\text{Cosine}(u, v) = u \cdot v = \sum u_i v_i$$
**Result:** Vector search becomes a simple multiplication and addition that runs in nanoseconds on CPU!

---

### § 5.6 `src/vector_store.py` — FAISS Fast Search & NumPy Fallback

#### 🎯 What is it?
The library catalog that stores millions of vectors and finds the top-5 closest matches in under 20 milliseconds using Meta's FAISS library.

```
+-----------------------------------------------------------------------------------+
|                         DUAL FAISS VECTOR STORES                                  |
+-----------------------------------------------------------------------------------+

     [English FAISS Store]                           [Multilingual FAISS Store]
     data/indexes/english/                           data/indexes/multilingual/
  - Model: all-mpnet-base-v2                      - Model: paraphrase-MiniLM-L12
  - Dimension: 768 float numbers                  - Dimension: 384 float numbers
  - Used by: Systems B and C                      - Used by: System D

  FAISS IndexFlatIP                               metadata_map.pkl
  ┌─────────────────────────┐                     ┌────────────────────────────────┐
  │ Vector ID 0: [0.12, ...]│ ──────────────────► │ DocumentChunk: algo_clrs_p45_c0│
  │ Vector ID 1: [0.89, ...]│ ──────────────────► │ DocumentChunk: algo_clrs_p45_c1│
  └─────────────────────────┘                     └────────────────────────────────┘
```

#### 🛡️ Built-in Safety Net: Pure NumPy Fallback
If FAISS C++ binaries are not installed or fail on Windows, `FAISSVectorStore` automatically switches to an in-memory NumPy dot-product engine. Zero crashes, 100% uptime!

---

### § 5.7 `src/translation.py` — Google Translate Bridge

#### 🎯 What is it?
Used exclusively by **System C**. Translates Hindi questions into English before querying the English FAISS index.

```
+-----------------------------------------------------------------------------------+
|                         TRANSLATION ENGINE (SYSTEM C)                             |
+-----------------------------------------------------------------------------------+

  Hindi Query: "डेडलॉक की चार आवश्यक कॉफमैन शर्तें क्या हैं?"
       │
       ▼
  ┌─────────────────────────────────────────────────────────┐
  │ deep-translator (Google Translate Web Endpoint, Free)   │
  │ - Sub-millisecond latency timer (time.perf_counter)     │
  │ - Automatic retry with exponential backoff on network   │
  └──────────────────────────┬──────────────────────────────┘
                             │
     [Success?] ─────────────┼────────────── [Network Failure?]
          │                                         │
          ▼                                         ▼
  English Query:                            [Academic Term Fallback]
  "What are the four necessary Coffman      Substitutes known CS keywords
   conditions for deadlock?"                from local dictionary
```

---

### § 5.8 `src/retrieval.py` — Search Coordinator & Evidence Formatter

#### 🎯 What is it?
Takes a query, calls the embedder, searches FAISS, gets top-$k$ chunks, and glues them into a clean academic evidence block for the LLM.

```
  Query String ──► Embedder ──► 768d Vector ──► FAISS Search ──► Top 5 Chunks
                                                                      │
                                                                      ▼
  Formatted Context Block:
  --- [Document Passage 1 | ID: algo_clrs_p45_c1 | Page: 45 | Subject: algorithms] ---
  Dijkstra's algorithm strictly fails when a graph contains negative edge weights...
  --- [Document Passage 2 | ID: algo_clrs_p46_c0 | Page: 46 | Subject: algorithms] ---
  The Bellman-Ford algorithm must be used instead when negative edges are present...
```

---

### § 5.9 `src/generation.py` — Zero-Temperature LLM Engine

#### 🎯 What is it?
Feeds the retrieved evidence and the student's question into the LLM with a strict academic system prompt.

```
+-----------------------------------------------------------------------------------+
|                           PROMPT & GENERATION ENGINE                              |
+-----------------------------------------------------------------------------------+

  [PROMPT TEMPLATE: prompts/rag_prompt_hindi.txt]
  "You are an academic Computer Science textbook assistant.
   Use ONLY the supplied retrieved textbook context below to answer.
   If the context does not contain sufficient facts, explicitly state so.
   Answer in clear, technically precise Hindi.
   Context: {context}
   Question: {question}"
               │
               ▼
  [MULTI-PROVIDER DISPATCHER] (Temperature strictly locked at 0.0!)
  ├── Provider: "gemini" -> Google Gemini 2.0 / 1.5 Flash (Free tier)
  ├── Provider: "ollama" -> Local Ollama (qwen2.5:7b / llama3) (100% offline)
  ├── Provider: "openai" -> GPT-4o-mini / GPT-4o
  └── Provider: "mock"   -> Deterministic instant mock for offline CI tests
```

---

### § 5.10 `src/pipelines.py` — Master Conductor (Systems A, B, C, D)

#### 🎯 What is it?
The central orchestrator that ties all modules together into the 4 experimental systems:

```
  System A: Query ──────────────────────────────────────────► LLM ──► Answer
  System B: Query_en ──► Eng Embed ──► Eng FAISS ───────────► LLM ──► En Answer
  System C: Query_hi ──► Translate ──► Eng FAISS ───────────► LLM ──► Hi Answer
  System D: Query_hi ──► Multi Embed ─► Multi FAISS ─────────► LLM ──► Hi Answer
```

---

### § 5.11 `src/logging_utils.py` — Atomic Flight Recorder

#### 🎯 What is it?
Every single question run across any system is saved as a complete, self-contained JSON file in `results/raw/system_{id}/{run_id}.json`.

```json
{
  "run_id": "8fa134d1-5627-4a01-8b29-379e49a8b111",
  "question_id": "OS_01",
  "system_id": "C",
  "original_question": "डेडलॉक की चार आवश्यक कॉफमैन शर्तें क्या हैं?",
  "translated_question": "What are the four necessary Coffman conditions for deadlock?",
  "top_k": 5,
  "retrieved_chunks": ["operating_systems_p2_c0", "operating_systems_p1_c0"],
  "retrieval_scores": [0.8912, 0.7431],
  "generated_answer": "डेडलॉक के लिए चार आवश्यक कॉफमैन शर्तें हैं: 1. म्युचुअल एक्सक्लूजन...",
  "latencies": {
    "translation_latency_ms": 128.4,
    "retrieval_latency_ms": 14.2,
    "generation_latency_ms": 842.1,
    "total_latency_ms": 984.7
  },
  "error_status": "SUCCESS"
}
```

---

### § 5.12 `src/observability.py` — X-Ray Waterfall Tracer

#### 🎯 What is it?
Tracks the exact execution graph with OpenTelemetry / LangSmith compliant spans.

```
+-----------------------------------------------------------------------------------+
|                        WATERFALL EXECUTION TIMELINE                               |
+-----------------------------------------------------------------------------------+
0 ms              200 ms            400 ms            600 ms            800 ms    1000 ms
├─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────┤
[=== translation (128 ms) ===]
                  [= faiss (14 ms) =]
                                    [================= llm_generation (842 ms) ===]
                                    
  Total Elapsed: 984.7 ms | Exporter: results/traces/*.json (Free Local Store)
```

---

### § 5.13 `src/evaluation.py` — Exam Grader & E1–E4 Taxonomy

#### 🎯 What is it?
Reads all logged runs and matches retrieved chunks against `data/benchmark/questions.csv`.

```
  1. Recall@k: Did the gold textbook chunk appear in the top-k results? (1.0 or 0.0)
  2. MRR (Mean Reciprocal Rank): 1 / rank of the first relevant chunk (1st = 1.0, 2nd = 0.5)
  3. nDCG@5: Discounted ranking quality metric giving higher points to higher positions.
```

---

### § 5.14 `app.py` — Interactive Streamlit Dashboard

#### 🎯 What is it?
A visual web interface with 3 tabs:
- **Tab 1 (Live Experiment Lab):** Run System C and System D side-by-side on any question and watch the answers stream in.
- **Tab 2 (Observability Workbench):** Inspect waterfall Gantt charts and JSON traces.
- **Tab 3 (Benchmark Analytics):** Bar charts of Recall@k and latencies across all 5 subjects.

---

### § 5.15 `tests/test_basic_pipeline.py` — 7-Stage Health Checker

#### 🎯 What is it?
Automated test suite guarding the entire codebase:
1. `test_page_aware_chunking`: Validates page bounds and ID format.
2. `test_embeddings_normalization`: Validates $\|v\|_2 = 1.0$.
3. `test_vector_store_build_and_search`: Validates FAISS cosine math.
4. `test_translation_service`: Validates latency tracking and error handling.
5. `test_all_four_pipelines`: Runs Systems A, B, C, and D end-to-end.
6. `test_json_logging_schema`: Validates mandatory JSON fields.
7. `test_evaluation_metrics_computation`: Validates Recall@k, MRR, and nDCG calculations.

---

## 6. The E1–E4 Scientific Error Taxonomy

When a cross-lingual RAG system fails, **why** did it fail? This decision tree diagnoses the exact root cause:

```
+-----------------------------------------------------------------------------------+
|                         E1–E4 ERROR DIAGNOSIS TREE                                |
+-----------------------------------------------------------------------------------+

                          Student asks in Hindi
                                    │
                                    ▼
                     Did Machine Translation distort
                        key technical terminology?
                               /         \
                            YES           NO
                            /               \
            ┌──────────────────┐             ▼
            │ [E1] Translation │     Did FAISS find the gold
            │      Drift       │     textbook chunk in top-5?
            └──────────────────┘             /         \
                                           NO          YES
                                          /               \
                          ┌──────────────────┐             ▼
                          │  [E2] Retrieval  │    Did LLM hallucinate or
                          │      Failure     │    refuse despite context?
                          └──────────────────┘             /         \
                                                         YES          NO
                                                         /              \
                                         ┌──────────────────┐            ▼
                                         │  [E3] Generation │   Is Hindi grammar
                                         │      Failure     │   corrupted or broken?
                                         └──────────────────┘          /        \
                                                                     YES         NO
                                                                     /             \
                                                     ┌──────────────────┐    ┌───────────┐
                                                     │  [E4] Language   │    │  SUCCESS! │
                                                     │      Failure     │    │ (Rank 1)  │
                                                     └──────────────────┘    └───────────┘
```

---

## 7. Hands-On Manual Testing Recipes

You can run individual parts of the codebase interactively inside Python:

### Recipe 1: Test the Page-Aware Chunker Directly
```powershell
python -c "
from cross_lingual_rag.src.chunking import PageAwareChunker
chunker = PageAwareChunker(chunk_size=700, chunk_overlap=80)
chunks = chunker.split_page_text('Dijkstra algorithm finds shortest paths in graphs.', 'clrs', 'algo', 45)
print('Generated Chunk ID:', chunks[0].chunk_id)
print('Page Number:', chunks[0].page)
print('Text:', chunks[0].text)
"
```
**Expected Output:**
```
Generated Chunk ID: clrs_p45_c0
Page Number: 45
Text: Dijkstra algorithm finds shortest paths in graphs.
```

### Recipe 2: Test Cosine Vector Similarity
```powershell
python -c "
from cross_lingual_rag.src.embeddings import SentenceTransformerEmbedder
import numpy as np
embedder = SentenceTransformerEmbedder('sentence-transformers/all-mpnet-base-v2')
vecs = embedder.embed_texts(['Dijkstra shortest path algorithm', 'Graph shortest path algorithms'])
cos_sim = np.dot(vecs[0], vecs[1])
print(f'Cosine Similarity: {cos_sim:.4f} (Close to 1.0 = Highly Similar)')
"
```

### Recipe 3: Test Hindi-to-English Translation
```powershell
python -c "
from cross_lingual_rag.src.translation import TranslationService
from cross_lingual_rag.src.utils import load_config
ts = TranslationService(load_config())
en_text, lat, err = ts.translate_hi_to_en('डाइक्स्ट्रा का एल्गोरिदम क्या है?')
print(f'Translated: {en_text}')
print(f'Latency: {lat:.1f} ms')
"
```

---

## 8. Troubleshooting & Common Gotchas

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **`ImportError: DLL load failed while importing _swigfaiss`** | Missing C++ build tools on Windows. | **No action needed!** `vector_store.py` automatically detects this and switches to the pure NumPy fallback. |
| **`HTTP 429 Too Many Requests` in translation** | Web Google Translate rate-limiting. | `translation.py` automatically catches this, backs off exponentially, and activates the local academic dictionary fallback. |
| **LLM gives different answers on the same question** | Temperature is greater than 0. | Set `temperature: 0.0` in `config.yaml`. Research requires strict greedy decoding. |
| **Out of Memory (OOM) on GPU** | Embedding batch size too large. | `config.yaml` has `device: "cpu"` and `batch_size: 32`, which runs cleanly within 2 GB of RAM on any PC. |
| **Want 100% Free LLM without paying OpenAI?** | OpenAI API costs money. | In `config.yaml`, set `provider: "gemini"` and get a free key from [Google AI Studio](https://aistudio.google.com/), or set `provider: "ollama"` and run `ollama run qwen2.5:7b` locally. |

---

### 🏁 Summary Checklist

- [x] Run `python -m pytest cross_lingual_rag/tests/test_basic_pipeline.py -v` (7/7 Passing)
- [x] Build chunks and indexes: `python -m cross_lingual_rag.src.ingestion` & `python -m cross_lingual_rag.src.vector_store`
- [x] Execute benchmark: `python -m cross_lingual_rag.src.pipelines`
- [x] Grade results: `python -m cross_lingual_rag.src.evaluation`
- [x] Launch web dashboard: `streamlit run cross_lingual_rag/app.py`
- [x] View interactive visual lab: `documentation.html`
- [x] View formal research manual: `research_paper.html`
