# 📘 Complete Codebase Visual Masterguide: Every File Explained Simply & In-Depth
## English–Hindi Cross-Lingual Academic RAG Experimentation Platform

---

## 1. The Big Picture: What Does This Codebase Actually Do?

### 1.1 The Everyday Analogy
Imagine a university library where all the best Computer Science textbooks (**Cormen** for Algorithms, **Galvin** for Operating Systems, **Ramakrishnan** for DBMS, **Tanenbaum** for Networks, **Sipser** for Automata) are written in **English**.

A student walks up to the library help desk and asks a question in **Hindi**:
> *"डेडलॉक की चार आवश्यक कॉफमैन शर्तें क्या हैं?"*  
> *(What are Coffman's four necessary conditions for deadlock?)*

How should our AI help desk find the exact English textbook page and answer the student in Hindi?

```
+-----------------------------------------------------------------------------------------+
|                         THE 4 SYSTEMS WE BUILT & COMPARE                                |
+-----------------------------------------------------------------------------------------+

  [SYSTEM A: Direct LLM Baseline] -> "The Closed-Book Guesser"
  Hindi Question ───────────────────────────────────────► [LLM] ──► Hindi Answer
  (No textbook search at all! Tests what the AI remembers from pre-training.)

  ---------------------------------------------------------------------------------------

  [SYSTEM B: English RAG Baseline] -> "The Native English Upper-Bound"
  English Question ──► [English Embedder] ──► [English FAISS] ──► Top-5 Pages ──► [LLM] ──► English Answer
  (Shows how well the system works when there is NO language barrier.)

  ---------------------------------------------------------------------------------------

  [SYSTEM C: Translation-Mediated RAG] -> "Translate First, Search Second"
  Hindi Question ──► [Google Translate] ──► English Query ──► [English Embedder]
                                                                     │
  Hindi Answer ◄── [LLM] ◄── Top-5 English Pages ◄── [English FAISS] ┘
  (Translates the Hindi words into English before searching the English database.)

  ---------------------------------------------------------------------------------------

  [SYSTEM D: Direct Multilingual RAG] -> "The Bilingual Mind (No Translation!)"
  Hindi Question ──► [Multilingual Embedder] ──► [Multilingual FAISS] ──► Top-5 Pages ──► [LLM] ──► Hindi Answer
  (Maps Hindi and English into the SAME mathematical coordinate space—zero translation!)
+-----------------------------------------------------------------------------------------+
```

---

## 2. How All Files Connect: The Complete Folder & File Map

```text
rag research/
│
├── 📄 FINAL_PROJECT_REPORT_AND_TESTING_GUIDE.md   # Your submission report & empirical findings
├── 📄 COMPLETE_CODEBASE_VISUAL_MASTERGUIDE.md     # This visual guide explaining every file
├── 📄 AGENT_MASTER_PROMPT.md                      # Prompt for your coding agent
├── 🌐 index.html / documentation.html / testit.html / research_paper.html # Interactive HTML portals
│
└── 📁 cross_lingual_rag/                          # THE MAIN PYTHON ENGINE
    ├── ⚙️ config.yaml                             # 1. Frozen settings & model names
    ├── 📦 requirements.txt                        # 2. Python library dependencies
    ├── 🚀 run_complete_experiment.py              # 3. One-click master test & benchmark runner
    ├── 🖥️ app.py                                  # 4. 3-Tab Streamlit visual web dashboard
    │
    ├── 📁 data/
    │   ├── 📚 corpus/                             # 5 CS subject folders (.txt / .pdf textbooks)
    │   ├── 📄 processed/                          # chunks_manifest.json (15 flashcards) & metadata
    │   ├── 🗄️ indexes/                            # english/ (768d) and multilingual/ (384d) FAISS stores
    │   └── 🎯 benchmark/questions.csv             # 17 paired English-Hindi test questions + answer keys
    │
    ├── 📁 prompts/                                # Fixed instruction templates for the LLM
    │   ├── direct_llm_prompt.txt                  # Used by System A
    │   ├── rag_prompt_english.txt                 # Used by System B
    │   └── rag_prompt_hindi.txt                   # Used by Systems C & D
    │
    ├── 📁 src/                                    # CORE SOURCE MODULES (11 Python files)
    │   ├── utils.py                               # Path finder, random seed locker, stopwatch
    │   ├── chunking.py                            # Slices textbook pages into numbered flashcards
    │   ├── ingestion.py                           # Reads files from data/corpus/ & saves manifest
    │   ├── embeddings.py                          # Converts text into L2-normalized math vectors
    │   ├── vector_store.py                        # Builds & searches FAISS indexes (+ NumPy fallback)
    │   ├── translation.py                         # Translates Hindi -> English for System C
    │   ├── retrieval.py                           # Searches FAISS & formats evidence passages
    │   ├── generation.py                          # Calls LLM (Gemini/OpenAI/Ollama/Mock) at temp=0.0
    │   ├── logging_utils.py                       # Saves 1 JSON file per run in results/raw/
    │   ├── observability.py                       # Records X-ray waterfall spans in results/traces/
    │   ├── pipelines.py                           # Orchestrates Systems A, B, C, and D
    │   └── evaluation.py                          # Calculates Recall@k, MRR, nDCG@5 & E1-E4 errors
    │
    ├── 📁 results/
    │   ├── 📝 raw/                                # Atomic JSON logs for every run (system_A..D)
    │   ├── 🌊 traces/                             # Waterfall span traces for observability
    │   ├── 📊 csv/benchmark_results.csv           # Spreadsheet of all 68 runs & scores
    │   └── 📑 summaries/evaluation_report.md      # Final Markdown comparison tables
    │
    └── 📁 tests/
        └── test_basic_pipeline.py                 # 7-point automated pytest health check
```

---

## 3. Deep-Dive & Simple Walkthrough of Every Single Code File

---

### File 1: `cross_lingual_rag/config.yaml` — The Master Control Room

#### 💡 In Simple Words
In a scientific experiment, if you change settings halfway through, your comparison is unfair. `config.yaml` locks all settings in one place so Systems A, B, C, and D play by the exact same rules.

#### 🔍 What Inside It Matters Most?
```yaml
embedding:
  english_model: "sentence-transformers/all-mpnet-base-v2"                  # 768 dimensions (for B & C)
  multilingual_model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" # 384 dimensions (for D)
  normalize_embeddings: true                                                # Makes vector length = 1.0

retrieval:
  top_k: 5           # Always retrieve top 5 chunks
  chunk_size: 700    # Max ~700 tokens per chunk
  chunk_overlap: 80  # 80 tokens shared between adjacent chunks on the same page

generation:
  provider: "openai" # Can be "gemini", "ollama", "openai", or "mock"
  temperature: 0.0   # CRITICAL: 0.0 means zero randomness!
```
- **Why `temperature: 0.0`?** If temperature is higher than `0.0`, the LLM rolls dice when picking words. By locking it to `0.0`, asking the same question with the same retrieved context always produces the exact same answer.

---

### File 2: `cross_lingual_rag/src/utils.py` — The Compass, Seed Locker & Stopwatch

#### 💡 In Simple Words
This file provides four utility tools used by every other file:
1. **`get_project_root()` (The Compass):** Whether you run Python from `D:\ai projects\rag research` or inside `D:\ai projects\rag research\cross_lingual_rag`, it automatically finds `config.yaml` so you never get `FileNotFoundError`.
2. **`load_config()`:** Reads `config.yaml` and converts relative paths (like `"data/corpus"`) into full absolute Windows/Linux paths.
3. **`set_seed(42)` (The Seed Locker):** Locks random number generators in Python, NumPy, and PyTorch so results never change between runs.
4. **`TimeTracker` (The Sub-Millisecond Stopwatch):** Uses `time.perf_counter()` to measure how many milliseconds translation, retrieval, and generation take.

---

### File 3: `cross_lingual_rag/src/chunking.py` — The Page-Aware Flashcard Maker

#### 💡 In Simple Words
An AI embedder works best on focused paragraphs (~200–700 tokens), not entire textbooks. However, if you chop a book blindly, a chunk might start on Page 1 and end on Page 2, and you lose track of the page number. `PageAwareChunker` slices text **strictly inside each page** and stamps every flashcard (`DocumentChunk`) with a permanent ID.

#### 🖼️ How It Works Visually
```
  [Input: Page 2 of operating_systems.txt]
  "Coffman's Four Conditions for Deadlock: 1. Mutual Exclusion... 2. Hold and Wait..."
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 1. _clean_text(): Fixes broken hyphenated words ("algo-\nrithm")    │
  │ 2. Splits by paragraphs ("\n\n"), packs up to 700 tokens            │
  │ 3. Assigns deterministic ID: f"{doc_id}_p{page_number}_c{idx}"      │
  └─────────────────────────────────────────────────────────────────────┘
          │
          ▼
  [Output: DocumentChunk Object]
  - chunk_id:    "operating_systems_operating_systems_p2_c0"
  - doc_id:      "operating_systems_operating_systems"
  - subject:     "operating_systems"
  - page:        2
  - chunk_index: 0
  - token_count: 223
```

---

### File 4: `cross_lingual_rag/src/ingestion.py` — The Textbook Scanner

#### 💡 In Simple Words
`CorpusIngestor` walks through `data/corpus/` (which has 5 folders: `algorithms`, `automata`, `computer_networks`, `dbms`, `operating_systems`), reads every `.pdf` or `.txt` file page-by-page, hands each page to `PageAwareChunker`, and saves two master files into `data/processed/`:
1. **`chunks_manifest.json`:** All 15 flashcards with their text, page numbers, and IDs.
2. **`corpus_metadata.json`:** A summary of the 5 textbooks (file names, page counts, chunk counts).

---

### File 5: `cross_lingual_rag/src/embeddings.py` — Turning Words into Math Coordinates

#### 💡 In Simple Words
Computers cannot directly measure whether *"ऋणात्मक किनारों"* and *"negative edge weights"* mean the same thing using letters. An **Embedding Model** converts a sentence into a list of numbers (a vector, like GPS coordinates on a globe). Sentences with similar meanings land right next to each other!

```
+-----------------------------------------------------------------------------------+
|                     WHY WE USE TWO DIFFERENT EMBEDDING MODELS                     |
+-----------------------------------------------------------------------------------+

  1. English Embedder (Used by Systems B & C):
     Model: "sentence-transformers/all-mpnet-base-v2" (768 numbers per chunk)
     - Understands deep English Computer Science terminology very accurately.
     - DOES NOT understand Hindi Devanagari script directly!

  2. Multilingual Embedder (Used by System D):
     Model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" (384 numbers)
     - Trained on 50+ languages simultaneously.
     - Maps the Hindi sentence "डेडलॉक की चार आवश्यक शर्तें क्या हैं?" and the English
       sentence "Coffman's Four Conditions for Deadlock" to the SAME spot!
+-----------------------------------------------------------------------------------+
```

#### 📐 Why Do We Normalize Vectors ($L_2$ Normalization)?
The angle between two vectors $\vec{u}$ and $\vec{v}$ is measured by **Cosine Similarity**:
$$\text{Cosine}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2}$$
In `embeddings.py`, we divide every vector by its length ($\|\vec{v}\|_2$) so every vector has a length of exactly $1.0$. Because the bottom of the fraction becomes $1.0 \times 1.0 = 1$, Cosine Similarity simplifies to a fast **dot product**:
$$\text{Cosine}(\vec{u}, \vec{v}) = \vec{u} \cdot \vec{v}$$

---

### File 6: `cross_lingual_rag/src/vector_store.py` — The Twin FAISS Search Engines

#### 💡 In Simple Words
Once `embeddings.py` turns our 15 textbook chunks into math vectors, `FAISSVectorStore` stores them in a high-speed search index (`faiss.IndexFlatIP`, where `IP` stands for Inner Product / Dot Product).

#### 🖼️ The Twin Index Design (Crucial Experimental Control)
```
                [data/processed/chunks_manifest.json]
                     (The Exact Same 15 Chunks)
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
   [data/indexes/english/]             [data/indexes/multilingual/]
   ├── index.faiss (15 x 768d)         ├── index.faiss (15 x 384d)
   └── metadata_map.pkl                └── metadata_map.pkl
   (Searched by Systems B & C)         (Searched by System D)
```
- **Why is there both `index.faiss` and `metadata_map.pkl`?**
  FAISS only stores raw numbers (Vector `#0`, Vector `#1`, ..., Vector `#14`). When FAISS says *"Vector #13 is the best match with score 0.7866"*, `vector_store.py` looks up `#13` in `metadata_map.pkl` to get back the full `DocumentChunk` object (`operating_systems_operating_systems_p2_c0`).
- **Built-in NumPy Safety Net:** If a computer doesn't have FAISS installed, `vector_store.py` automatically uses `np.dot(self.vectors_np, query_vector.T)` so the code still runs with the exact same math!

---

### File 7: `cross_lingual_rag/src/translation.py` — The Language Bridge (System C Only)

#### 💡 In Simple Words
System C needs to translate the student's Hindi question into English before searching the English FAISS index. `TranslationService` calls `deep_translator.GoogleTranslator(source='hi', target='en')` and measures the exact `translation_latency_ms`.

#### 🛡️ How It Handles Rate Limits (`HTTP 429`)
Free Google Translate web endpoints block you if you send more than ~5 requests per second. `translation.py` includes:
1. **Retry with Backoff:** Waits and retries if the network hiccups.
2. **Academic Dictionary Fallback (`_mock_translate`):** Replaces Hindi CS terms (`"डाइक्स्ट्रा"` $\to$ `"Dijkstra"`, `"ऋणात्मक किनारों"` $\to$ `"negative edges"`, `"डेडलॉक"` $\to$ `"deadlock"`) so System C can still retrieve the right English chunk even when offline or rate-limited!

---

### File 8: `cross_lingual_rag/src/retrieval.py` — The Librarian & Evidence Formatter

#### 💡 In Simple Words
`Retriever` connects the Embedder and the FAISS Vector Store:
1. **`retrieve(query)`:** Takes a question string $\to$ embeds it into a vector $\to$ searches FAISS for the top 5 chunks $\to$ returns `(chunks, scores, retrieval_latency_ms)`.
2. **`format_context(chunks)`:** Formats the 5 retrieved chunks into a clean text block with explicit citations so the LLM knows exactly where each paragraph came from:
   ```text
   --- [Document Passage 1 | ID: operating_systems_operating_systems_p2_c0 | Page: 2 | Subject: operating_systems] ---
   Coffman's Four Conditions for Deadlock A deadlock is a state in which...
   ```

---

### File 9: `cross_lingual_rag/src/generation.py` — The Zero-Temperature Professor

#### 💡 In Simple Words
`LLMGenerator` takes the formatted prompt (the question + the 5 retrieved textbook passages) and sends it to the LLM with `temperature = 0.0`.
- It supports **4 modes** configured in `config.yaml`:
  1. **`gemini`:** Free Google Gemini API (`GEMINI_API_KEY`).
  2. **`ollama`:** 100% Free offline local LLM (`http://localhost:11434`).
  3. **`openai`:** OpenAI `gpt-4o-mini` (`OPENAI_API_KEY`).
  4. **`mock`:** Automatic offline fallback when no API key is set, ensuring tests and pipeline demos never crash.

---

### File 10: `cross_lingual_rag/src/logging_utils.py` & `observability.py` — The Flight Recorder & X-Ray Camera

#### 💡 Why Do We Have Both?
1. **`logging_utils.py` (`ExperimentLogger`):** Writes **one flat JSON file per run** into `results/raw/system_{A,B,C,D}/{run_id}.json`. This matches the exact 22-field research schema required by your PDF specification (saving `run_id`, `question_id`, `retrieved_chunks`, `retrieval_scores`, `latencies`, etc.) and is read by `evaluation.py` to compute your grades.
2. **`observability.py` (`ObservabilityTracer`):** Records **step-by-step waterfall spans** into `results/traces/{trace_id}.json` (and optionally streams them to **LangSmith Cloud** if `LANGSMITH_API_KEY` is set). This powers Tab 2 of your Streamlit UI so you can inspect the exact inputs, outputs, token counts, and millisecond duration of every internal step!

---

### File 11: `cross_lingual_rag/src/pipelines.py` — The Master Conductor

#### 💡 In Simple Words
`PipelineOrchestrator` loads all components once during `__init__()` and exposes four clean methods:
- **`execute_system_A(question_hi, ...)`**: Formats `direct_llm_prompt.txt` $\to$ calls `generator.generate()` $\to$ logs to `results/raw/system_A/`.
- **`execute_system_B(question_en, ...)`**: Calls `eng_retriever.retrieve(question_en)` $\to$ formats `rag_prompt_english.txt` $\to$ calls `generator.generate()` $\to$ logs to `results/raw/system_B/`.
- **`execute_system_C(question_hi, ...)`**: Calls `translator.translate_hi_to_en(question_hi)` $\to$ calls `eng_retriever.retrieve(translated_en)` $\to$ formats `rag_prompt_hindi.txt` $\to$ calls `generator.generate()` $\to$ logs to `results/raw/system_C/`.
- **`execute_system_D(question_hi, ...)`**: Calls `multi_retriever.retrieve(question_hi)` directly (zero translation!) $\to$ formats `rag_prompt_hindi.txt` $\to$ calls `generator.generate()` $\to$ logs to `results/raw/system_D/`.

---

### File 12: `cross_lingual_rag/src/evaluation.py` — The Automated Exam Grader

#### 💡 In Simple Words
`EvaluationHarness` reads every JSON log from `results/raw/` and compares `retrieved_chunks` against the answer key (`gold_chunk_id`) in `data/benchmark/questions.csv`.

#### 📐 The 3 Retrieval Formulas It Computes:
1. **$\text{Recall}@k$ ($k \in \{1, 3, 5\}$):**
   Did the gold chunk appear anywhere in the top $k$ retrieved results? ($1.0$ if Yes, $0.0$ if No).
2. **$\text{MRR}$ (Mean Reciprocal Rank):**
   If the gold chunk is at Rank 1, score $= \frac{1}{1} = 1.0$. If Rank 2, score $= \frac{1}{2} = 0.5$. If Rank 3, score $= \frac{1}{3} = 0.333$.
3. **$\text{nDCG}@5$ (Normalized Discounted Cumulative Gain):**
   $$\text{nDCG}@5 = \frac{1}{\log_2(\text{rank} + 1)}$$
   Rewards systems that place the gold chunk near the top with a smoother decay than MRR.

#### 🐛 The Bug We Fixed in `evaluation.py` (Great Viva Talking Point!)
In your initial zip archive, `evaluation_report.md` showed `nDCG@5 = 2.948` and `Recall@5 = 0.0` on `SMOKE_01`. Why?
- `pytest` created logs with `question_id = "SMOKE_01"`.
- Because `"SMOKE_01"` wasn't in `questions.csv`, `gold_chunk` was `""` (empty string).
- In Python, `"any_chunk_id".startswith("")` is always `True`! So `compute_ndcg_at_k` thought all 5 retrieved chunks were gold hits and added them up ($1.0 + 0.63 + 0.50 + 0.43 + 0.39 = 2.95$).
- **Our Fix:** We added `if not gold_chunk or not gold_chunk.strip(): return 0.0` and excluded `SMOKE_*` unit-test logs from the official benchmark evaluation.

---

## 4. How to Share Your Project on GitHub & How Others Can Use It

### 4.1 What Should Be Pushed to GitHub?
When your Coding Agent (or you) pushes this repository to GitHub, make sure these folders and files are included:
- `cross_lingual_rag/src/` (All 11 core Python modules)
- `cross_lingual_rag/data/` (The 5 textbook files, `chunks_manifest.json`, the pre-built `english/` and `multilingual/` FAISS indexes, and `benchmark/questions.csv`)
- `cross_lingual_rag/prompts/` (All 3 frozen prompt templates)
- `cross_lingual_rag/results/csv/benchmark_results.csv` & `cross_lingual_rag/results/summaries/evaluation_report.md` (So anyone viewing your GitHub repo can immediately inspect your results!)
- `cross_lingual_rag/tests/test_basic_pipeline.py` & `cross_lingual_rag/run_complete_experiment.py`
- `cross_lingual_rag/app.py`, `config.yaml`, `requirements.txt`
- `README.md` & `FINAL_PROJECT_REPORT_AND_TESTING_GUIDE.md`

### 4.2 Manual Git Commands (If You Push It Yourself)
If you want to push it to your own GitHub account manually from PowerShell:

```powershell
cd "D:\ai projects\rag research"

# Remove unrelated file from root if present
Remove-Item -Path "chatgpt_ui_gap_analysis_and_ideation.md" -ErrorAction SilentlyContinue

# Initialize Git and commit everything cleanly
git init
git add .
git commit -m "Complete English-Hindi Cross-Lingual Academic RAG Platform & Benchmark Report"

# Link to a new empty repo you create on github.com and push
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/english-hindi-cross-lingual-rag.git
git push -u origin main
```

### 4.3 How Anyone Cloning Your GitHub Repo Can Run & Test It in 3 Commands
Share these 3 commands with your professor, evaluator, or teammates:

```bash
# 1. Clone and install dependencies
git clone https://github.com/<YOUR_GITHUB_USERNAME>/english-hindi-cross-lingual-rag.git
cd english-hindi-cross-lingual-rag
pip install -r cross_lingual_rag/requirements.txt

# 2. Run the complete 7-point test suite + 68-run benchmark + evaluation report
python cross_lingual_rag/run_complete_experiment.py

# 3. Launch the interactive Streamlit visual lab & trace explorer
streamlit run cross_lingual_rag/app.py
```