# 📘 Cross-Lingual Academic RAG: The Ultimate Visual Guide
## Simple, Step-by-Step Code Walkthrough with Complete Architecture Diagrams

---

### 🌟 Executive Summary: What is this Project in Simple Words?

Imagine an Indian engineering student studying for a Computer Science university exam. 
- All standard textbooks (Cormen for Algorithms, Galvin for OS, Tanenbaum for Networks) are written in **English**.
- But the student understands, thinks, and asks questions in **Hindi**:
  > *"डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक किनारों (negative edges) पर क्यों विफल हो जाता है?"*

How should an AI answer this question using the English textbooks?

```
                     THE CORE RESEARCH CHALLENGE
                     
  [Hindi Question]                                   [English Textbooks]
  "डाइक्स्ट्रा का एल्गोरिदम                             "Dijkstra's algorithm fails
   ऋणात्मक किनारों पर क्यों                             on negative edge weights 
   विफल हो जाता है?"                                    because the greedy choice..."
         │                                                        ▲
         │                                                        │
         └───────────── HOW DO WE BRIDGE THIS GAP? ───────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
   [METHOD 1: TRANSLATION]                   [METHOD 2: BILINGUAL AI]
       (System C)                                (System D)
 Translate Hindi to English first,        Use a multilingual AI that directly
 then search the English books.           understands Hindi and English in the
                                          same mental vector space!
```

This research project tests **which method works better, faster, and more accurately** through rigorous, automated experiments.

---

## 🗺️ Master System Map: The 4 Experimental Pipelines

We compare four distinct systems under identical, strictly controlled conditions:

```
==================================================================================================
                                    THE 4 SYSTEM TOPOLOGIES
==================================================================================================

[System A: Direct LLM Baseline] (No Textbook / Closed-Book Exam)
 Hindi Question ─────────────────────────► [ LLM Brain ] ─────────────► Hindi Answer
                                          (No search at all)

──────────────────────────────────────────────────────────────────────────────────────────────────

[System B: Monolingual English RAG] (The English Control Baseline)
 English Question ──► [English Embedder] ──► [English FAISS] ──► Top Chunks ──┐
                                                                              ├──► [ LLM ] ──► English Answer
                                                             English Question ┘

──────────────────────────────────────────────────────────────────────────────────────────────────

[System C: Translation-Mediated RAG] (The Translator Pipeline)
 Hindi Question ──► [Google Translate] ──► English Query ──┐
                                                           ▼
                     [English Embedder] ──► [English FAISS] ──► Top Chunks ──┐
                                                                             ├──► [ LLM ] ──► Hindi Answer
                                                                Hindi Query ─┘

──────────────────────────────────────────────────────────────────────────────────────────────────

[System D: Direct Multilingual RAG] (The Bilingual Shared-Mind Pipeline)
 Hindi Question ──► [Multilingual Embedder] ──► [Multi FAISS] ──► Top Chunks ──┐
                         (No translation!)                                     ├──► [ LLM ] ──► Hindi Answer
                                                                  Hindi Query ─┘
==================================================================================================
```

---

## 📂 Project Directory Tour: Where Does Everything Live?

```
cross_lingual_rag/
│
├── ⚙️ config.yaml            # The Master Control Room (frozen settings)
├── 📦 requirements.txt       # All required Python packages
├── 🖥️ app.py                 # The Visual Web Dashboard (Streamlit)
│
├── 📁 data/
│   ├── 📚 corpus/            # Raw academic textbooks (Algorithms, OS, DBMS, etc.)
│   ├── 📄 processed/         # Text broken down into numbered flashcards (Chunks)
│   ├── 🗄️ indexes/           # FAISS Search Indexes (English and Multilingual)
│   └── 🎯 benchmark/         # 120 Exam questions with verified answer keys
│
├── 📁 prompts/               # Exact question-answering instruction templates
│   ├── rag_prompt_english.txt
│   ├── rag_prompt_hindi.txt
│   └── direct_llm_prompt.txt
│
├── 📁 src/                   # The Core Engine (Python Code)
│   ├── utils.py              # Helper tools (timing, paths, seeds)
│   ├── chunking.py           # Cuts long pages into clean text flashcards
│   ├── ingestion.py          # Reads PDFs and notes, preserving page numbers
│   ├── embeddings.py         # Converts words into mathematical coordinates
│   ├── vector_store.py       # The High-Speed Vector Library Search (FAISS)
│   ├── translation.py        # Translates Hindi to English with safety fallbacks
│   ├── generation.py         # The AI answering engine (Gemini / Ollama / OpenAI)
│   ├── retrieval.py          # Coordinates vector searches and formats evidence
│   ├── pipelines.py          # Orchestrates Systems A, B, C, and D
│   ├── logging_utils.py      # Saves every single execution to a JSON log
│   ├── observability.py      # The X-Ray Trace Camera (LangSmith alternative)
│   └── evaluation.py         # Grades the exam (Recall@k, MRR, Error Taxonomy)
│
├── 📁 results/
│   ├── 📝 raw/               # Individual JSON logs for every run
│   ├── 🌊 traces/            # Granular step-by-step waterfall traces
│   ├── 📊 csv/               # Final aggregated spreadsheets
│   └── 📑 summaries/         # Automated scientific markdown reports
│
└── 📁 tests/
    └── test_basic_pipeline.py# 7-point automated health check test suite
```

---

## 🔍 Detailed Component Walkthrough: Code & Diagrams

---

### 1. `config.yaml` — The Master Control Center

#### 🎯 What is it?
The single file that locks down all model names, file paths, and hyperparameters so experiments cannot accidentally change midway.

```
+-----------------------------------------------------------------------+
|                             CONFIG.YAML                               |
|                                                                       |
|  [Paths]        -> Where raw PDFs, indexes, and logs are stored.     |
|  [Embedding]    -> English: all-mpnet-base-v2                         |
|                    Multilingual: paraphrase-multilingual-MiniLM-L12   |
|  [Retrieval]    -> Top-K = 5, Chunk size = 700 tokens                 |
|  [Generation]   -> Provider: Gemini / Ollama / OpenAI                 |
|                    Temperature: 0.0 (Strictly deterministic!)         |
|  [Translation]  -> deep-translator (Google Translate Web API, Free)   |
+-----------------------------------------------------------------------+
```

#### 💡 Why Temperature = 0.0?
If you ask an AI the same question twice with `temperature = 0.7`, it gives two slightly different answers. In scientific research, **stochastic noise ruins experiments**. With `temperature = 0.0`, the LLM behaves like a mathematical function: same input context always yields the exact same answer.

---

### 2. `src/chunking.py` — Turning Textbooks into Numbered Flashcards

#### 🎯 What is it?
An AI cannot read a 1,000-page book in one glance. We must slice the book into bite-sized "chunks" (flashcards) of ~700 tokens (~500 words).

#### 🖼️ The Page-Aware Chunking Process:
```
  [Physical Page 45 of Textbook]
  ┌──────────────────────────────────────────────────────────────────┐
  │ Dijkstra's algorithm solves single-source shortest paths...      │
  │ It maintains a priority queue of vertices...                     │
  │ However, if an edge has a negative weight, the greedy...         │
  └──────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                      PageAwareChunker.split_page_text()
                                   │
           ┌───────────────────────┴───────────────────────┐
           ▼                                               ▼
  [Flashcard 0]                                   [Flashcard 1]
  ┌──────────────────────────────┐                ┌──────────────────────────────┐
  │ ID: algo_clrs_p45_c0         │                │ ID: algo_clrs_p45_c1         │
  │ Page: 45 | Subject: Algo     │ ── 80 tokens ─►│ Page: 45 | Subject: Algo     │
  │ Text: "Dijkstra's algorithm  │    overlap     │ Text: "...priority queue...  │
  │ solves single-source..."     │                │ negative edge weights..."    │
  └──────────────────────────────┘                └──────────────────────────────┘
```

#### 🔑 The Stable Chunk ID Formula:
$$\text{Chunk ID} = \underbrace{\text{doc\_id}}_{\text{Book Name}} + \text{"\_p"} + \underbrace{\text{page\_num}}_{\text{Physical Page}} + \text{"\_c"} + \underbrace{\text{chunk\_index}}_{\text{Card Number}}$$
*Example:* `algo_clrs_p45_c0` tells you immediately: **Algorithms book, Page 45, Chunk 0**.

---

### 3. `src/ingestion.py` — The Book Scanner

#### 🎯 What is it?
Discovers all PDF documents and lecture notes in `data/corpus/`, parses their text, cleans up OCR noise (like hyphenated line breaks: `algo-\nrithm` $\to$ `algorithm`), runs the chunker, and builds a master catalog.

```
       [Raw Files]                          [Parser]                      [Output Manifest]
  data/corpus/algorithms/*.pdf  ──►   pypdf.PdfReader   ──┐
  data/corpus/os/*.txt          ──►   Virtual Page Slicer ─┼──► data/processed/chunks_manifest.json
  data/corpus/dbms/*.txt        ──►   Text Cleaners     ──┘     (15-20 academic books -> thousands of cards)
```

---

### 4. `src/embeddings.py` — Turning Words into Mathematical GPS Coordinates

#### 🎯 What is it?
Computers cannot compare raw letters. They compare vectors (lists of numbers). An embedding model maps text onto a high-dimensional sphere.

```
                               THE EMBEDDING HYPERSPHERE
                               
                                    (Operating Systems)
                                     [Deadlock] (Vector A)
                                         *
                                        /
                                       / 
                                      /   Angle θ (Small angle = High similarity!)
                                     /
                                    * [Mutual Exclusion] (Vector B)
       
       (Far away in vector space)
         * [Dijkstra Algorithm] (Vector C)
```

#### 📐 Why L2 Normalization Matters:
Every vector is normalized so its length equals 1.0 ($\|v\|_2 = 1$). When vectors have length 1, their dot product equals their **Cosine Similarity**:
$$\text{Similarity}(u, v) = u \cdot v = \cos(\theta)$$
- **Score = 1.0:** Perfect exact semantic match.
- **Score = 0.0:** Completely unrelated topics.

#### The Dual Embedder Choice:
1. **English Embedder (`all-mpnet-base-v2`):** 768 dimensions. Specialized in deep English technical comprehension.
2. **Multilingual Embedder (`paraphrase-multilingual-MiniLM-L12-v2`):** 384 dimensions. Maps Hindi concepts and English concepts into the **exact same neighborhood**!

---

### 5. `src/vector_store.py` — The High-Speed Library Search Engine (FAISS)

#### 🎯 What is it?
Stores thousands of vector coordinates in memory and finds the nearest neighbors in under **10 milliseconds** using Facebook AI Similarity Search (FAISS).

```
                 FAISS IndexFlatIP                           metadata_map.pkl
          ┌─────────────────────────────┐             ┌─────────────────────────────┐
          │ Vector 0: [ 0.04, -0.12...] │ ──────────► │ Key 0 -> algo_clrs_p45_c0   │
          │ Vector 1: [ 0.81,  0.23...] │ ──────────► │ Key 1 -> algo_clrs_p45_c1   │
          │ Vector 2: [-0.05,  0.72...] │ ──────────► │ Key 2 -> os_galvin_p12_c0   │
          └─────────────────────────────┘             └─────────────────────────────┘
                         ▲
                         │ Search Query Vector: [ 0.80, 0.21... ]
                         │
             "Top Match Found: Vector 1 (Similarity: 0.94)!"
```

If FAISS C++ binaries are unavailable on a system, the code seamlessly falls back to a built-in pure NumPy dot-product engine with **zero downtime**.

---

### 6. `src/translation.py` — The Language Bridge with Safety Net

#### 🎯 What is it?
Translates Hindi academic questions into English for System C.

```
  [Hindi Question]
  "डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक किनारों पर क्यों विफल हो जाता है?"
                       │
                       ▼
              [Google Translate Web API]
                       │
         ┌─────────────┴─────────────┐
         ▼ (Success)                 ▼ (Rate-Limited / Offline)
  "Why does Dijkstra's       [Academic Fallback Dictionary]
   algorithm fail on          Replaces technical terms:
   negative edges?"           "ऋणात्मक किनारों" -> "negative edges"
                              "डाइक्स्ट्रा" -> "Dijkstra"
```
It tracks translation latency down to the millisecond and logs errors instead of crashing.

---

### 7. `src/retrieval.py` — Finding and Packaging the Best Evidence

#### 🎯 What is it?
Takes the query vector, retrieves the top-$k$ (e.g., 5) best chunks from FAISS, and formats them into clean academic evidence blocks for the LLM.

```
  Retrieved Chunks ──► format_context() ──►
  
  --- [Passage 1 | ID: algo_clrs_p45_c1 | Page: 45 | Subject: Algorithms] ---
  Dijkstra's algorithm strictly fails when a graph contains negative edge weights...
  
  --- [Passage 2 | ID: algo_clrs_p45_c2 | Page: 46 | Subject: Algorithms] ---
  The Bellman-Ford algorithm must be used instead for negative edge weights...
```

---

### 8. `src/generation.py` — The Academic Question-Answering AI

#### 🎯 What is it?
Sends the retrieved context and question to the LLM (Gemini, Ollama, or OpenAI) with a strict academic prompt:

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │ Prompt Template:                                                       │
  │ "You are an academic Computer Science assistant.                       │
  │  Use ONLY the supplied retrieved context below to answer.              │
  │  If the context is insufficient, say so rather than inventing facts.   │
  │  Answer in accurate, technical Hindi."                                 │
  │                                                                        │
  │ Context: [Passage 1, Passage 2...]                                     │
  │ Question: [Hindi Question]                                             │
  └────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                       [LLM Inference (Temp = 0.0)]
                                   │
                                   ▼
  "डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक किनारों (negative edges) पर विफल हो जाता है 
   क्योंकि यह एक बार चुने गए शीर्ष की दूरी को अंतिम मान लेता है..."
```

---

### 9. `src/observability.py` — The X-Ray Camera (LangSmith Equivalent)

#### 🎯 What is it?
When a query runs, how long did translation take? How long did retrieval take? Did an error occur? 
`observability.py` captures a **hierarchical tree of execution spans**:

```
[Trace: ALGO_01 Execution (Total: 1,120 ms)]
  ├── 🌐 Span 1: machine_translation  [142 ms]  (Hi -> En)
  ├── 🔍 Span 2: english_retrieval    [ 18 ms]  (FAISS Top-5 chunks)
  ├── 📝 Span 3: prompt_assembly      [  2 ms]  (Formatted context)
  └── 🤖 Span 4: llm_generation       [958 ms]  (Synthesized Hindi answer)
```

- **100% Free Local Mode:** Saves complete trace files to `results/traces/{trace_id}.json`.
- **LangSmith Cloud Mode:** If you set `LANGSMITH_API_KEY`, it automatically streams these traces to your [smith.langchain.com](https://smith.langchain.com) dashboard!

---

### 10. `src/evaluation.py` — The Automated Professor Grading the Exam

#### 🎯 What is it?
Compares the system's retrieved chunks and generated answers against the gold standard in `data/benchmark/questions.csv`.

```
                               EVALUATION METRICS
                               
  1. Recall@1:  Was the Gold Chunk ranked #1? (Yes = 1.0, No = 0.0)
  2. Recall@3:  Was the Gold Chunk in the Top 3?
  3. Recall@5:  Was the Gold Chunk in the Top 5?
  4. MRR:       Mean Reciprocal Rank (1 / Rank of first correct chunk).
  5. nDCG@5:    Graded relevance across all positions.
```

#### 🚨 The E1–E4 Scientific Error Taxonomy:
```
+---------------------------------------------------------------------------------+
|                                 ERROR TAXONOMY                                  |
+---------------------------------------------------------------------------------+
| Code | Error Name            | Real-World Example                               |
|------|-----------------------|--------------------------------------------------|
| [E1] | Translation Drift     | "ऋणात्मक किनारा" was mistranslated to             |
|      | (System C Only)       | "negative border" instead of "negative edge",    |
|      |                       | causing FAISS to search the wrong topic!         |
|------|-----------------------|--------------------------------------------------|
| [E2] | Retrieval Failure     | The translation was correct, but FAISS ranked the|
|      |                       | gold chunk at position #8 (outside top-5).       |
|------|-----------------------|--------------------------------------------------|
| [E3] | Generation Failure    | The gold chunk was at position #1, but the LLM   |
|      |                       | hallucinated or claimed it didn't know.          |
|------|-----------------------|--------------------------------------------------|
| [E4] | Language Failure      | The facts are correct, but the Hindi phrasing is |
|      |                       | broken, corrupted, or unintelligible.            |
+---------------------------------------------------------------------------------+
```

---

### 11. `app.py` — The Visual Streamlit Laboratory

#### 🎯 What is it?
A full-featured web app running on `http://localhost:8501` with 3 dedicated tabs:

```
+---------------------------------------------------------------------------------+
|       🔬 CROSS-LINGUAL ACADEMIC RAG EXPERIMENTATION & OBSERVABILITY LAB         |
+---------------------------------------------------------------------------------+
|  [Tab 1: Live Experiment Lab]  [Tab 2: Observability Traces]  [Tab 3: Analytics]|
+---------------------------------------------------------------------------------+
|                                                                                 |
|   Select Benchmark Question: [ ALGO_01: Dijkstra Negative Weights ... ▼ ]       |
|                                                                                 |
|   ┌───────────────────────────────────┐   ┌───────────────────────────────────┐ |
|   │ 🌐 System C: Translation RAG      │   │ 🔀 System D: Multilingual RAG     │ |
|   │ Translated Query:                 │   │ Zero-Shot Hindi Vector Search:    │ |
|   │ "Why does Dijkstra fail on..."    │   │ Direct multilingual alignment     │ |
|   │                                   │   │                                   │ |
|   │ Top Retrieved Chunks:             │   │ Top Retrieved Chunks:             │ |
|   │ 1. algo_clrs_p45_c1 (0.84) 🎯     │   │ 1. algo_clrs_p45_c1 (0.71) 🎯     │ |
|   │                                   │   │                                   │ |
|   │ Generated Hindi Answer:           │   │ Generated Hindi Answer:           │ |
|   │ "डाइक्स्ट्रा का एल्गोरिदम..."      │   │ "डाइक्स्ट्रा का एल्गोरिदम..."      │ |
|   │ Latency: 3,327 ms                 │   │ Latency: 193 ms ⚡                │ |
|   └───────────────────────────────────┘   └───────────────────────────────────┘ |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

---

## 🚀 How to Run and Test Everything (The 3-Minute Runbook)

### Step 1: Run the 7-Point Automated Health Check
```powershell
python -m pytest cross_lingual_rag/tests/test_basic_pipeline.py -v
```
*Expected Result:* All 7 tests pass (`100% passed in ~22s`).

### Step 2: Launch the Web Dashboard
```powershell
streamlit run cross_lingual_rag/app.py
```
Open `http://localhost:8501` in your browser to test any question interactively!

### Step 3: Run the Full Benchmark & Professor Evaluation
```powershell
python -m cross_lingual_rag.src.pipelines
python -m cross_lingual_rag.src.evaluation
```
Inspect the scientific evaluation report at:
`cross_lingual_rag/results/summaries/evaluation_report.md`
