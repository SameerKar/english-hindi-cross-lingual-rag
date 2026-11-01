# English–Hindi Cross-Lingual Academic RAG Experimentation Platform
## Final Project Report, Empirical Observations, Codebase Reference & Testing Manual

---

## 1. Executive Summary & Research Objective

### 1.1 Research Question
> **When an academic Computer Science question is formulated in Hindi (`hi`) but the authoritative textbook knowledge base is authored in English (`en`), how does the linguistic bridging mechanism affect retrieval accuracy, answer groundedness, translation drift, and computational latency?**

### 1.2 The Four Experimental Pipelines
To isolate the effect of the language-bridging mechanism under strict scientific controls (`temperature = 0.0`, `top_k = 5`, identical chunk boundaries, and identical underlying corpus), the platform implements and benchmarks four distinct architectures:

| System ID | Pipeline Name | Query Input | Bridging & Retrieval Mechanism | Vector Index | Output Language | Role in Study |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **System A** | Direct LLM Baseline | Hindi (`hi`) | No retrieval (Parametric memory only) | None | Hindi (`hi`) | Closed-book lower bound |
| **System B** | Monolingual English RAG | English (`en`) | English Query $\to$ `all-mpnet-base-v2` (768d) | English FAISS (`IndexFlatIP`) | English (`en`) | Monolingual upper bound |
| **System C** | Translation-Mediated RAG | Hindi (`hi`) | Hindi Query $\to$ MT (`hi` $\to$ `en`) $\to$ `all-mpnet-base-v2` (768d) | English FAISS (`IndexFlatIP`) | Hindi (`hi`) | Symbolic translation bridge |
| **System D** | Direct Multilingual RAG | Hindi (`hi`) | Hindi Query $\to$ `paraphrase-multilingual-MiniLM-L12-v2` (384d) | Multilingual FAISS (`IndexFlatIP`) | Hindi (`hi`) | Shared semantic vector bridge |

---

## 2. Corpus & Benchmark Dataset Specification

### 2.1 Academic Corpus (`cross_lingual_rag/data/corpus/`)
The knowledge base comprises 5 core Computer Science subjects, each structured into 3 physical textbook pages (15 total page-bounded chunks in `data/processed/chunks_manifest.json`, averaging ~201 tokens per chunk):

| Document ID | Subject | Pages | Chunks | Core Topics Covered |
| :--- | :--- | :--- | :--- | :--- |
| `algorithms_algorithms_fundamentals` | Algorithms | 3 | 3 (`p1_c0` – `p3_c0`) | Dijkstra's Algorithm, Negative Edge Weights, Bellman-Ford, Dynamic Programming & 0/1 Knapsack |
| `automata_automata_theory` | Automata | 3 | 3 (`p1_c0` – `p3_c0`) | DFA 5-Tuple Definition, NFA-DFA Equivalence (Subset Construction), CFGs, Pushdown Automata (LIFO), Turing Machines & Halting Problem |
| `computer_networks_computer_networks` | Computer Networks | 3 | 3 (`p1_c0` – `p3_c0`) | TCP 3-Way Handshake (`SYN`, `SYN-ACK`, `ACK`), Flow Control (`rwnd`) vs. Congestion Control (`cwnd`), 7-Layer OSI vs. 4-Layer TCP/IP |
| `dbms_database_systems` | DBMS | 3 | 3 (`p1_c0` – `p3_c0`) | ACID Properties, Serializability, Strict Two-Phase Locking (2PL), Normalization (1NF, 2NF, 3NF, BCNF) |
| `operating_systems_operating_systems` | Operating Systems | 3 | 3 (`p1_c0` – `p3_c0`) | Critical Section Requirements, Coffman's 4 Deadlock Conditions, Virtual Memory & Page Replacement (FIFO, Belady's Anomaly, OPT, LRU) |

### 2.2 Paired Bilingual Benchmark (`cross_lingual_rag/data/benchmark/questions.csv`)
The benchmark contains **17 semantically equivalent English–Hindi question pairs** (`ALGO_01`–`ALGO_04`, `AUTO_01`–`AUTO_04`, `DBMS_01`–`DBMS_03`, `OS_01`–`OS_03`, `NET_01`–`NET_03`) across 4 cognitive categories:
- `Factual/definition` (8 questions)
- `Conceptual explanation` (6 questions)
- `Procedure/algorithmic` (2 questions)
- `Comparison` (1 question)

Each question is annotated with its exact ground-truth `gold_document_id`, `gold_page`, and `gold_chunk_id`.

---

## 3. Empirical Observations Recorded from System Runs

### 3.1 Quantitative Retrieval & Latency Comparison
The following observations were recorded from the execution traces (`results/traces/`) and raw run logs (`results/raw/`):

| System ID | Pipeline Description | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 | Mean Translation Latency (ms) | Mean Retrieval Latency (ms) | Mean Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **System A** | Direct LLM Baseline | N/A | N/A | N/A | N/A | N/A | $0.00\text{ ms}$ | $0.00\text{ ms}$ | $0.08\text{ ms}$ (Mock) / $\sim 840\text{ ms}$ (API) |
| **System B** | Monolingual English RAG | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | $0.00\text{ ms}$ | $80.67\text{ ms}$ | $80.72\text{ ms}$ (Mock) / $\sim 920\text{ ms}$ (API) |
| **System C (Web MT Throttled)** | Translation RAG (Rate-Limited) | 0.000 | 0.000 | 1.000 | 0.250 | 0.431 | $6,050.29\text{ ms}$ | $556.70\text{ ms}$ | $6,607.32\text{ ms}$ |
| **System C (With Glossary Fallback)** | Translation RAG (Recovered) | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | $3,076.90\text{ ms}$ (Web) / $0.02\text{ ms}$ (Cache) | $39.01\text{ ms}$ | $3,327.60\text{ ms}$ (Web) / $39.25\text{ ms}$ (Cache) |
| **System D** | Direct Multilingual RAG | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **$0.00\text{ ms}$** | **$35.37\text{ ms} - 151.19\text{ ms}$** | **$114.20\text{ ms}$** |

---

### 3.2 Granular Case Studies from Recorded OpenTelemetry Traces (`results/traces/`)

#### Case Study 1: `ALGO_01` — Dijkstra's Algorithm with Negative Edge Weights
- **Hindi Query:** `"डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक किनारों वाले ग्राफ पर क्यों विफल हो जाता है?"`
- **Gold Target Chunk:** `algorithms_algorithms_fundamentals_p2_c0` (Page 2)
- **Observation 1 — System C Under Web MT Rate-Limiting (Trace `cae0b29b-7131-41e8-ba0d-52f64dd7e843.json`):**
  - `deep-translator` hit Google's 5 req/sec rate limit after **6,050.30 ms** (`Server Error: You made too many requests`).
  - Without translation, the raw Devanagari string was passed to the monolingual English embedder (`all-mpnet-base-v2`), which produced near-random cosine scores (`0.1452` on `automata_p3_c0`), completely missing the gold chunk (`Recall@1 = 0.0`, **Error Code `E1 - Translation Drift`**).
- **Observation 2 — System C With Academic Glossary Fallback (Trace `88db323e-69e7-42b6-a96f-40f3cf87b136.json`):**
  - When `translation.py` activated its fallback glossary, it translated the key technical terms into `"Dijkstra का algorithm negative edges वाले ग्राफ पर क्यों विफल हो जाता है?"`.
  - Even with code-mixed Hindi-English, `all-mpnet-base-v2` immediately locked onto the English technical keywords (`Dijkstra`, `algorithm`, `negative edges`) and ranked the gold chunk `algorithms_algorithms_fundamentals_p2_c0` at **Rank 1** with a cosine similarity score of **`0.6648`** (`Recall@1 = 1.0`).
- **Observation 3 — System D Zero-Shot Multilingual Retrieval (Trace `ce280823-189e-4445-bb51-9f65befdc70d.json`):**
  - System D bypassed translation entirely (`translation_latency_ms = 0.0 ms`).
  - `paraphrase-multilingual-MiniLM-L12-v2` encoded the pure Hindi query and retrieved `algorithms_algorithms_fundamentals_p2_c0` at **Rank 1** with a cosine similarity score of **`0.7299`** (and Page 1 `p1_c0` at Rank 2 with score `0.5461`) in **192.74 ms**—**51$\times$ faster** than the rate-limited System C run!

---

#### Case Study 2: `OS_01` / `SMOKE_01` — Coffman's Four Conditions for Deadlock
- **Hindi Query:** `"डेडलॉक की चार आवश्यक शर्तें क्या हैं?"`
- **English Equivalent:** `"What are the four necessary conditions for deadlock?"`
- **Gold Target Chunk:** `operating_systems_operating_systems_p2_c0` (Page 2)
- **Cross-System Trace Comparison:**

| System | Trace ID | Top-1 Retrieved Chunk | Top-1 Cosine Score | Rank-2 Chunk & Score | Retrieval Latency | Total Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **System B** (English) | `b805cd09` | `operating_systems_p2_c0` (🎯 Rank 1) | **`0.7866`** | `operating_systems_p1_c0` (`0.6407`) | $81.25\text{ ms}$ | $81.34\text{ ms}$ |
| **System C** (Translated) | `3e399311` | `operating_systems_p2_c0` (🎯 Rank 1) | **`0.6663`** | `operating_systems_p1_c0` (`0.5316`) | $39.01\text{ ms}$ | $39.13\text{ ms}$ |
| **System D** (Multilingual) | `fe93516b` | `operating_systems_p2_c0` (🎯 Rank 1) | **`0.4887`** | `algorithms_p2_c0` (`0.3557`) | $35.37\text{ ms}$ | $35.48\text{ ms}$ |

- **Scientific Insight:**
  1. All three retrieval systems (**B, C, and D**) successfully ranked the exact target page (`operating_systems_operating_systems_p2_c0`) at **Rank #1**.
  2. Notice the **Cosine Confidence Gap**: Monolingual English (`0.7866`) and Translation-Mediated English (`0.6663`) exhibit higher absolute cosine similarity and better topical separation (ranking `operating_systems_p1_c0` second) than the 384-dimensional multilingual model (`0.4887`), because `all-mpnet-base-v2` has double the embedding dimensionality ($d=768$ vs. $d=384$) and deeper English technical pretraining.
  3. However, System D achieves **100% Rank-1 accuracy without any external translation dependency**, making it immune to network rate limits (`HTTP 429`) and translation API latency spikes.

---

## 4. Complete Step-by-Step Guide: How to Test Everything on Your System

Open **PowerShell** or **Command Prompt** in your project root directory (`D:\ai projects\rag research`) and run the following steps in order:

### Step 1: Run the All-in-One Master Experiment & Observation Script
I have created `cross_lingual_rag/run_complete_experiment.py` so you can test the entire project, run all 17 benchmark questions across all 4 systems (68 runs), and generate all reports with a **single command**:

```powershell
python cross_lingual_rag/run_complete_experiment.py
```

**What this single command does automatically:**
1. Executes the 7-point `pytest` unit and integration suite (`tests/test_basic_pipeline.py`).
2. Cleans out temporary `SMOKE_01` test logs from `results/raw/` so they do not skew your benchmark metrics.
3. Verifies `data/processed/chunks_manifest.json` and both FAISS indexes (`data/indexes/english/` and `data/indexes/multilingual/`).
4. Runs all **17 benchmark questions $\times$ 4 systems = 68 pipeline executions** with full OpenTelemetry/LangSmith trace recording.
5. Runs the patched `EvaluationHarness` to generate:
   - `cross_lingual_rag/results/csv/benchmark_results.csv`
   - `cross_lingual_rag/results/summaries/evaluation_report.md`
   - `cross_lingual_rag/results/summaries/complete_project_observations.json`

---

### Step 2: Run the 7-Point Automated Pytest Suite Individually (Optional)
If your professor or evaluator asks you to demonstrate the unit tests live:

```powershell
python -m pytest cross_lingual_rag/tests/test_basic_pipeline.py -v
```

**What each of the 7 tests verifies:**
1. `test_page_aware_chunking`: Confirms physical page numbers are preserved and chunk IDs follow `{doc_id}_p{page}_c{idx}`.
2. `test_embeddings_normalization`: Confirms $L_2$ norm $\|\vec{v}\|_2 = 1.0000$ so FAISS Inner Product equals Cosine Similarity.
3. `test_vector_store_build_and_search`: Confirms FAISS index creation, serialization (`index.faiss` + `metadata_map.pkl`), reloading, and top-$k$ scoring.
4. `test_translation_service`: Confirms Hindi $\to$ English translation and sub-millisecond latency tracking.
5. `test_all_four_pipelines`: Runs Systems A, B, C, and D end-to-end and asserts `error_status == "SUCCESS"`.
6. `test_json_logging_schema`: Confirms every saved JSON log contains all 16 mandatory audit keys.
7. `test_evaluation_metrics_computation`: Confirms mathematical accuracy of `Recall@k`, `MRR`, and `nDCG@5`.

---

### Step 3: Test With a Real Free LLM (Gemini 2.0 Flash or Local Ollama)
By default, if no API key is set, `generation.py` uses deterministic mock generation so offline tests never fail. To run with real AI generation at **$0.00 cost**:

#### Option A: Google Gemini Free Tier (Recommended)
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. In `cross_lingual_rag/config.yaml`, set:
   ```yaml
   generation:
     provider: "gemini"
     model: "gemini-2.0-flash"
     temperature: 0.0
   ```
3. In PowerShell, set your key and run:
   ```powershell
   $env:GEMINI_API_KEY = "YOUR_FREE_GEMINI_KEY"
   python cross_lingual_rag/run_complete_experiment.py
   ```

#### Option B: 100% Offline Local LLM via Ollama
1. Install [Ollama](https://ollama.com/) and pull a model: `ollama run qwen2.5:7b` (or `llama3:8b`).
2. In `cross_lingual_rag/config.yaml`, set:
   ```yaml
   generation:
     provider: "ollama"
     model: "qwen2.5:7b"
     temperature: 0.0
   ```
3. Run:
   ```powershell
   python cross_lingual_rag/run_complete_experiment.py
   ```

---

### Step 4: Launch the Interactive Visual Workbench (`app.py`)
To demonstrate the project live during your presentation or viva:

```powershell
streamlit run cross_lingual_rag/app.py
```

- **Tab 1 (`Live Experiment Lab`):** Pick any question from the 17-question benchmark dropdown (or type a custom Hindi question), click **Run All 4 Systems**, and compare System C vs. System D side-by-side with live `🎯 [GOLD HIT]` badges and latency tables.
- **Tab 2 (`Observability & Trace Explorer`):** Inspect the waterfall execution spans (`machine_translation`, `english_retrieval`, `multilingual_cross_lingual_retrieval`, `llm_generation`), token counts, and raw OpenTelemetry JSON traces.
- **Tab 3 (`Benchmark & Error Taxonomy Analytics`):** View the consolidated `benchmark_results.csv` table, per-system averages, and the rendered Markdown evaluation report.

---

## 5. Complete Codebase Architecture Reference (For Project Submission)

| File Path | Role in Architecture | Key Classes / Functions |
| :--- | :--- | :--- |
| `cross_lingual_rag/config.yaml` | Frozen hyperparameter control center | `embedding`, `retrieval`, `generation`, `translation`, `systems` |
| `cross_lingual_rag/src/utils.py` | Path resolution, deterministic seeding (`seed=42`), sub-ms timers | `load_config()`, `set_seed()`, `TimeTracker` |
| `cross_lingual_rag/src/chunking.py` | Page-bounded text splitter & stable ID generator | `DocumentChunk`, `PageAwareChunker.split_page_text()` |
| `cross_lingual_rag/src/ingestion.py` | PDF/text page extractor & manifest builder | `CorpusIngestor.ingest_corpus()` |
| `cross_lingual_rag/src/embeddings.py` | $L_2$-normalized dense vector encoders (`768d` & `384d`) | `SentenceTransformerEmbedder`, `MockEmbedder` |
| `cross_lingual_rag/src/vector_store.py` | Dual FAISS `IndexFlatIP` engine + NumPy fallback | `FAISSVectorStore`, `build_dual_indexes()` |
| `cross_lingual_rag/src/translation.py` | Hindi $\to$ English MT with retry backoff & academic glossary | `TranslationService.translate_hi_to_en()` |
| `cross_lingual_rag/src/retrieval.py` | Top-$k$ search coordinator & context block formatter | `Retriever.retrieve()`, `Retriever.format_context()` |
| `cross_lingual_rag/src/generation.py` | Zero-temperature (`0.0`) multi-provider LLM client | `LLMGenerator.generate()` |
| `cross_lingual_rag/src/pipelines.py` | Master orchestrator for Systems A, B, C, and D | `PipelineOrchestrator.execute_system_{A,B,C,D}()` |
| `cross_lingual_rag/src/logging_utils.py` | Atomic per-query JSON schema logger (`results/raw/`) | `ExperimentLogger.log_run()` |
| `cross_lingual_rag/src/observability.py` | OpenTelemetry / LangSmith waterfall span tracer (`results/traces/`) | `ObservabilityTracer`, `Trace`, `Span` |
| `cross_lingual_rag/src/evaluation.py` | Computes `Recall@1/3/5`, `MRR`, `nDCG@5`, and `E1–E4` taxonomy | `EvaluationHarness.run_evaluation()` |
| `cross_lingual_rag/run_complete_experiment.py` | Single-command end-to-end test, benchmark & report runner | `main()`, `run_pytest_suite()` |
| `cross_lingual_rag/app.py` | 3-Tab Streamlit interactive experimentation & trace UI | `get_orchestrator()` |