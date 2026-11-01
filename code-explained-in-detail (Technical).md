# Comprehensive Codebase Documentation & Deep Technical Walkthrough
## English–Hindi Cross-Lingual Academic RAG Experimentation Platform

---

### Table of Contents
1. [Project Mission & Experimental Paradigm](#1-project-mission--experimental-paradigm)
2. [File Inventory & Architecture Map](#2-file-inventory--architecture-map)
3. [Deep Dive: Configuration & Utilities](#3-deep-dive-configuration--utilities)
   - `config.yaml`
   - `src/utils.py`
4. [Deep Dive: Data Ingestion & Page-Aware Chunking](#4-deep-dive-data-ingestion--page-aware-chunking)
   - `src/chunking.py`
   - `src/ingestion.py`
5. [Deep Dive: Embeddings & Vector Storage](#5-deep-dive-embeddings--vector-storage)
   - `src/embeddings.py`
   - `src/vector_store.py`
6. [Deep Dive: Translation, Retrieval & Generation Engines](#6-deep-dive-translation-retrieval--generation-engines)
   - `src/translation.py`
   - `src/retrieval.py`
   - `src/generation.py`
7. [Deep Dive: Pipeline Orchestration & Observability](#7-deep-dive-pipeline-orchestration--observability)
   - `src/pipelines.py`
   - `src/logging_utils.py`
8. [Deep Dive: Evaluation Framework & Error Taxonomy](#8-deep-dive-evaluation-framework--error-taxonomy)
   - `src/evaluation.py`
9. [Deep Dive: Verification UI & Testing Suite](#9-deep-dive-verification-ui--testing-suite)
   - `app.py` (Streamlit Dashboard)
   - `tests/test_basic_pipeline.py`
10. [Step-by-Step Operational Runbook](#10-step-by-step-operational-runbook)

---

## 1. Project Mission & Experimental Paradigm

The fundamental question guiding this platform is:
> **When an academic question is formulated in Hindi but the underlying knowledge base is authored in English, how does the linguistic bridging mechanism affect retrieval accuracy, answer correctness, semantic faithfulness, translation drift, and computational latency?**

To answer this question with scientific rigor, the platform contrasts two core bridging strategies:
1. **System C (Translation-Mediated RAG):** Translates the Hindi question into English before querying a monolingual English index.
2. **System D (Direct Multilingual RAG):** Projects the Hindi question directly into a shared cross-lingual embedding space to retrieve English passages without runtime text translation.

These are anchored against two experimental baselines:
- **System A (Direct LLM):** Zero-retrieval baseline measuring parametric knowledge.
- **System B (Monolingual English RAG):** Native English query against English index (theoretical upper bound).

---

## 2. File Inventory & Architecture Map

```
d:/ai projects/rag research/cross_lingual_rag/
│
├── config.yaml                    # Frozen hyperparameters, model names, paths
├── requirements.txt               # Pinned dependencies
├── app.py                         # Interactive Streamlit inspection dashboard
│
├── data/
│   ├── corpus/                    # Academic texts across 5 CS domains
│   │   ├── algorithms/
│   │   ├── automata/
│   │   ├── dbms/
│   │   ├── operating_systems/
│   │   └── computer_networks/
│   ├── processed/                 # Generated chunks manifest & corpus metadata
│   ├── indexes/                   # Persisted FAISS binary vector stores
│   │   ├── english/
│   │   └── multilingual/
│   └── benchmark/
│       └── questions.csv          # 120 Paired Hindi-English academic questions
│
├── prompts/
│   ├── rag_prompt_english.txt     # Monolingual prompt for System B
│   ├── rag_prompt_hindi.txt       # Cross-lingual prompt for Systems C & D
│   └── direct_llm_prompt.txt      # Parametric prompt for System A
│
├── src/
│   ├── __init__.py                # Package exports
│   ├── utils.py                   # Config loading, seeding, timing decorators
│   ├── chunking.py                # Page-aware chunker & stable ID generator
│   ├── ingestion.py               # PDF/text parser & manifest builder
│   ├── embeddings.py              # Dense embedding models (with mock fallback)
│   ├── vector_store.py            # FAISS IndexFlatIP & NumPy FlatIP engine
│   ├── translation.py             # Machine translation layer (deep-translator)
│   ├── generation.py              # Zero-temperature LLM generation client
│   ├── retrieval.py               # Search coordinator & context hydrator
│   ├── logging_utils.py           # Atomic JSON schema audit logger
│   ├── pipelines.py               # Orchestrator for Systems A, B, C, D
│   └── evaluation.py              # Recall@k, MRR, nDCG, and E1-E4 classifier
│
├── results/
│   ├── raw/                       # Individual JSON run logs per system
│   ├── csv/                       # Consolidated benchmark results
│   └── summaries/                 # Markdown research reports
│
└── tests/
    ├── __init__.py
    └── test_basic_pipeline.py     # 10-point unit & smoke test suite
```

---

## 3. Deep Dive: Configuration & Utilities

### 3.1 `config.yaml`
The configuration file serves as the **single source of truth** for all experimental controls. It guarantees that tests are reproducible and eliminates hardcoded magic numbers.

```yaml
# Core Settings
project_name: "English-Hindi Cross-Lingual Academic RAG Experimentation Platform"
version: "2.0"
random_seed: 42

paths:
  corpus_dir: "data/corpus"
  processed_dir: "data/processed"
  english_index_dir: "data/indexes/english"
  multilingual_index_dir: "data/indexes/multilingual"
  benchmark_file: "data/benchmark/questions.csv"
  results_raw_dir: "results/raw"
  results_csv_dir: "results/csv"
  results_summary_dir: "results/summaries"
  prompts_dir: "prompts"

embedding:
  english_model: "sentence-transformers/all-mpnet-base-v2"
  multilingual_model: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
  normalize_embeddings: true
  device: "cpu"
  batch_size: 32

retrieval:
  top_k: 5
  chunk_size: 700
  chunk_overlap: 80
  metric: "cosine"

generation:
  provider: "openai"       # Options: "openai", "gemini", "ollama", "mock"
  model: "gpt-4o-mini"
  temperature: 0.0         # Critical: Must be 0.0 for zero stochastic variance
  max_new_tokens: 512
  openai_api_key_env: "OPENAI_API_KEY"
  gemini_api_key_env: "GEMINI_API_KEY"
  ollama_base_url: "http://localhost:11434"

translation:
  provider: "deep-translator"
  source_lang: "hi"
  target_lang: "en"
```

#### Key Design Rationale:
- **`normalize_embeddings: true`:** Normalizes all dense vectors to unit length ($\|v\|_2 = 1$). In unit hyperspheres, dot product equals cosine similarity:
  $$\text{Cosine}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2} = u \cdot v$$
  This allows using `faiss.IndexFlatIP` (Inner Product) which is substantially faster than calculating Euclidean distances.
- **`temperature: 0.0`:** Eliminates sampling noise in LLM responses. Any difference in output between runs is strictly caused by the pipeline architecture or prompt context.

---

### 3.2 `src/utils.py`
Provides foundational infrastructure:

```python
def get_project_root() -> Path:
```
- **Path Resolution:** Dynamically traverses upward to locate `config.yaml`. Whether scripts are run from the repository root `d:\ai projects\rag research` or inside `cross_lingual_rag/`, file references resolve seamlessly without path errors.

```python
def set_seed(seed: int = 42) -> None:
```
- **Scientific Seeding:** Sets seeds for Python `random`, NumPy `np.random`, and PyTorch `torch.manual_seed` (including CUDA backend determinism).

```python
class TimeTracker:
```
- **High-Precision Timing:** Uses `time.perf_counter()` as a context manager and stopwatch to capture sub-millisecond latencies across translation, vector search, and LLM token generation.

---

## 4. Deep Dive: Data Ingestion & Page-Aware Chunking

### 4.1 `src/chunking.py`
The chunking module is responsible for breaking academic textbooks into digestible passages while maintaining **page awareness** and generating **stable identifiers**.

#### `DocumentChunk` Dataclass:
```python
@dataclass
class DocumentChunk:
    chunk_id: str          # e.g., "algo_clrs_p104_c2"
    doc_id: str            # Document key
    subject: str           # Academic subject
    page: int              # Physical 1-indexed page
    chunk_index: int       # 0-indexed position within page
    text: str              # Cleaned text
    token_count: int       # Approximate token count
    metadata: Dict[str, Any]
```

#### Stable Identifier Structure:
$$\text{Chunk ID} = \text{doc\_id} + \text{"\_p"} + \text{page} + \text{"\_c"} + \text{chunk\_index}$$
*Why this matters:* If a student asks a question about Dijkstra's algorithm, the system doesn't just retrieve arbitrary text; it points to the exact physical page of the reference book (e.g., Cormen Page 658, Chunk 1).

#### Page-Aware Splitting Logic:
```
[Raw Physical Page Text]
            │
            ▼
    [Text Artifact Cleaning] (Removes hyphenated word breaks: "algo-\nrithm" -> "algorithm")
            │
            ▼
    [Paragraph Segmentation] (\n\n splits)
            │
            ▼
 ┌────────────────────────────────────────────────────────┐
 │ Does paragraph fit in remaining token budget?          │
 │  - YES: Append words to current chunk buffer           │
 │  - NO:  Flush buffer to DocumentChunk, retain overlap, │
 │         and split large paragraph by sentence (.!?)    │
 └────────────────────────────────────────────────────────┘
            │
            ▼
 [Yield DocumentChunks with Deterministic Chunk IDs]
```

---

### 4.2 `src/ingestion.py`
Orchestrates raw file discovery and document extraction.

- **PDF Parsing (`extract_pdf_pages`):** Uses `pypdf.PdfReader` to extract text page-by-page. Unlike naive chunkers that concatenate the entire book into one giant string (losing page boundaries), `ingestion.py` extracts text while explicitly recording the physical page index (`page_idx + 1`).
- **Text & Notes Parsing (`extract_text_pages`):** Recognizes `=== PAGE X ===` delimiters or splits long lecture notes into virtual textbook pages (~3,000 characters per page).
- **Manifest Cataloging:** Serializes all parsed chunks to `data/processed/chunks_manifest.json` and document-level statistics to `data/processed/corpus_metadata.json`.

---

## 5. Deep Dive: Embeddings & Vector Storage

### 5.1 `src/embeddings.py`
Defines the embedding layer connecting text to dense vector spaces.

```
                  ┌───────────────────────────────┐
                  │    BaseEmbedder (Abstract)    │
                  └───────────────┬───────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
┌─────────────────────────────────┐   ┌───────────────────────────┐
│   SentenceTransformerEmbedder   │   │       MockEmbedder        │
│  - all-mpnet-base-v2 (Eng)      │   │ - Deterministic Hashing   │
│  - paraphrase-multi-mpnet (Mul) │   │ - Instant CI / Offline    │
│  - L2-Unit Normalization        │   │ - Zero Dependencies       │
└─────────────────────────────────┘   └───────────────────────────┘
```

#### Key Implementations:
- **`SentenceTransformerEmbedder`:** Loads models via `sentence_transformers.SentenceTransformer`. Executes batched encoding (`batch_size=32`) with automatic fallback to `MockEmbedder` if HuggingFace weights or PyTorch cannot be initialized.
- **`MockEmbedder`:** Generates 768-dimensional normalized deterministic vectors using term-frequency and hashing. Allows running full integration tests and smoke tests instantly in resource-constrained environments.

---

### 5.2 `src/vector_store.py`
Encapsulates FAISS indexing and vector persistence.

#### The Dual-Index Requirement:
The platform requires **two parallel vector indexes** constructed over the **exact same text chunks**:
1. **English Index (`data/indexes/english/`):** Built using `all-mpnet-base-v2`. Used by System B and System C.
2. **Multilingual Index (`data/indexes/multilingual/`):** Built using `paraphrase-multilingual-mpnet-base-v2`. Used by System D.

#### FAISS Vector Mapping Architecture:
```
FAISS IndexFlatIP                      metadata_map.pkl
┌─────────────────────────┐            ┌──────────────────────────────────────────────┐
│ Vector ID 0: [0.12, ...]│ ─────────► │ Key 0: DocumentChunk(algo_clrs_p10_c0, ...) │
│ Vector ID 1: [0.08, ...]│ ─────────► │ Key 1: DocumentChunk(algo_clrs_p10_c1, ...) │
│ Vector ID 2: [0.94, ...]│ ─────────► │ Key 2: DocumentChunk(algo_clrs_p11_c0, ...) │
└─────────────────────────┘            └──────────────────────────────────────────────┘
```
FAISS indexes store raw numerical vectors and assign them integer IDs (`0, 1, 2, ...`). `src/vector_store.py` maintains an immutable Python dictionary (`metadata_map.pkl`) mapping every integer ID back to its full `DocumentChunk` object (text, page number, document ID, subject).

#### Pure NumPy Fallback:
If `faiss-cpu` is not present in the environment, `FAISSVectorStore` transparently switches to an exact vector dot-product engine using NumPy:
```python
sims = np.dot(self.vectors_np, query_vector.T).flatten()
idx_list = np.argsort(-sims)[:k]
```
This guarantees that search results and cosine scores are mathematically identical whether running on native FAISS C++ binaries or pure NumPy.

---

## 6. Deep Dive: Translation, Retrieval & Generation Engines

### 6.1 `src/translation.py`
Implements the translation layer required for System C.

- **Provider: `deep-translator` (GoogleTranslator):** Translates incoming Hindi queries (e.g., *"डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक किनारों को कैसे संभालता है?"*) into English (e.g., *"How does Dijkstra's algorithm handle negative edges?"*).
- **Latency Recording:** Isolates translation time (`translation_latency_ms`) from retrieval and generation time.
- **Fail-Safe Operation:** If translation times out or network drops, records the error status explicitly instead of silently substituting arbitrary text.

---

### 6.2 `src/retrieval.py`
Coordinates the semantic search lifecycle:
1. Receives the query string.
2. Calls `embedder.embed_query(query)` to obtain a 768-dim normalized vector.
3. Queries `vector_store.search(query_vec, top_k=5)`.
4. Hydrates top-$k$ `DocumentChunk` objects and similarity scores.
5. Formats the retrieved text into a standardized academic context block:
   ```text
   --- [Document Passage 1 | ID: algo_clrs_p104_c2 | Page: 104 | Subject: algorithms] ---
   Dijkstra's algorithm operates by maintaining a set of vertices...
   ```

---

### 6.3 `src/generation.py`
Executes deterministic LLM inference with **Temperature strictly set to 0.0**.

#### Multi-Provider Support:
- **OpenAI (`gpt-4o-mini`, `gpt-4o`):** Communicates via official `openai` SDK.
- **Google Gemini (`gemini-1.5-flash`, `gemini-2.5-flash`):** Uses modern `google-genai` SDK.
- **Local Ollama (`llama3:8b`, `qwen2.5:7b`):** Connects via local REST API (`http://localhost:11434/api/generate`) with `temperature: 0.0` for 100% offline and cost-free execution.
- **Mock Generator:** Produces deterministic academic answers for instant verification when API keys are not supplied.

---

## 7. Deep Dive: Pipeline Orchestration & Observability

### 7.1 `src/pipelines.py`
`PipelineOrchestrator` is the central engine executing the four experimental systems.

```
                    ┌────────────────────────┐
                    │  PipelineOrchestrator  │
                    └───────────┬────────────┘
         ┌───────────────┬──────┴────────┬───────────────┐
         ▼               ▼               ▼               ▼
   [System A]      [System B]      [System C]      [System D]
   Direct LLM     English RAG     Translate RAG   Multilingual
```

#### Detailed Execution Mechanics:

| Pipeline | Input Query | Retrieval Step | Generation Step | Output |
| :--- | :--- | :--- | :--- | :--- |
| **System A** | Hindi / English | *None (Bypassed)* | `direct_llm_prompt.txt` | Direct Answer |
| **System B** | English Query | English Embedder $\to$ English FAISS | `rag_prompt_english.txt` | English Answer |
| **System C** | Hindi Query | Translate Hi $\to$ En $\to$ English FAISS | `rag_prompt_hindi.txt` | Hindi Answer |
| **System D** | Hindi Query | Multilingual Embedder $\to$ Multi FAISS | `rag_prompt_hindi.txt` | Hindi Answer |

---

### 7.2 `src/logging_utils.py`
Every single query run across any system emits an atomic JSON document in `results/raw/system_{id}/{run_id}.json`.

#### Complete Log Schema:
```json
{
  "run_id": "8fa134d1-5627-4a01-8b29-379e49a8b111",
  "timestamp": "2026-10-04T03:55:00.123456Z",
  "question_id": "OS_01",
  "system_id": "C",
  "subject": "Operating Systems",
  "category": "Factual/definition",
  "original_question": "डेडलॉक की चार आवश्यक कॉफमैन शर्तें क्या हैं?",
  "translated_question": "What are the four necessary Coffman conditions for deadlock?",
  "top_k": 5,
  "retrieved_chunks": [
    "operating_systems_operating_systems_p2_c0",
    "operating_systems_operating_systems_p1_c0"
  ],
  "retrieval_scores": [0.8912, 0.7431],
  "source_documents": [
    {"doc_id": "operating_systems_operating_systems", "page": 2, "rank": 1}
  ],
  "generated_answer": "डेडलॉक के लिए चार आवश्यक कॉफमैन शर्तें हैं: 1. म्युचुअल एक्सक्लूजन, 2. होल्ड एंड वेट, 3. नो प्रीएम्प्शन, और 4. सर्कुलर वेट।",
  "model_name": "gpt-4o-mini",
  "embedding_model": "sentence-transformers/all-mpnet-base-v2",
  "translation_model": "deep-translator",
  "temperature": 0.0,
  "latencies": {
    "translation_latency_ms": 128.4,
    "retrieval_latency_ms": 14.2,
    "generation_latency_ms": 842.1,
    "total_latency_ms": 984.7
  },
  "error_status": "SUCCESS",
  "error_message": null
}
```

---

## 8. Deep Dive: Evaluation Framework & Error Taxonomy

### 8.1 `src/evaluation.py`
The evaluation module parses all atomic run logs and matches retrieved chunks against ground truth annotations in `data/benchmark/questions.csv`.

#### Metrics Formulations:

1. **Recall@k:**
   $$\text{Recall}@k = \begin{cases} 1.0 & \text{if } \text{gold\_chunk} \in \text{retrieved\_chunks}[1:k] \\ 0.0 & \text{otherwise} \end{cases}$$

2. **Mean Reciprocal Rank (MRR):**
   $$\text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rank}_q}$$
   Where $\text{rank}_q$ is the 1-based position of the first relevant chunk.

3. **Normalized Discounted Cumulative Gain (nDCG@5):**
   $$\text{DCG}@5 = \sum_{i=1}^{5} \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}, \quad \text{nDCG}@5 = \frac{\text{DCG}@5}{\text{IDCG}@5}$$

#### Scientific Error Taxonomy (E1 - E4):

```
+-----------------------------------------------------------------------------------+
|                            ERROR CLASSIFICATION ENGINE                            |
+-----------------------------------------------------------------------------------+
| Code | Error Category        | Trigger Condition in Evaluation                    |
|------|-----------------------|----------------------------------------------------|
| E1   | Translation Drift     | System C only: Translated query contains errors,   |
|      |                       | lost technical terms, or failed translation.       |
| E2   | Retrieval Failure     | Gold chunk is missing from the top-5 chunks        |
|      |                       | (Recall@5 == 0.0) in Systems B, C, or D.           |
| E3   | Generation Failure    | Retrieval succeeded (Recall@5 == 1.0), but the     |
|      |                       | LLM refused, hallucinated, or produced an error.  |
| E4   | Language Failure      | Answer was generated but contained severe Hindi    |
|      |                       | phrasing defects or corrupt transliteration.      |
+-----------------------------------------------------------------------------------+
```

Outputs:
- `results/csv/benchmark_results.csv`: Row-level metrics for every test run.
- `results/summaries/evaluation_report.md`: Markdown summary comparing System C vs System D.

---

## 9. Deep Dive: Verification UI & Testing Suite

### 9.1 `app.py` (Streamlit Dashboard)
A two-column scientific workbench designed for manual inspection and debugging:
- **Left Column:** System C execution trace (shows intermediate translation, English search scores, retrieved passages, and generated Hindi answer).
- **Right Column:** System D execution trace (shows direct cross-lingual retrieval scores, retrieved passages, and generated Hindi answer).
- **Bottom Section:** Real-time latency distribution comparison table.
- **Baselines Expander:** System A (Direct LLM) and System B (Monolingual English RAG) reference outputs.

### 9.2 `tests/test_basic_pipeline.py`
A comprehensive 7-stage pytest test suite:
1. `test_page_aware_chunking`: Verifies page boundary retention and stable ID formatting.
2. `test_embeddings_normalization`: Checks unit length $\|v\|_2 = 1.0$.
3. `test_vector_store_build_and_search`: Verifies FAISS persistence, loading, and cosine scoring.
4. `test_translation_service`: Verifies translation latency tracking and error handling.
5. `test_all_four_pipelines`: Runs Systems A, B, C, and D end-to-end.
6. `test_json_logging_schema`: Verifies all mandatory fields are present in saved JSON logs.
7. `test_evaluation_metrics_computation`: Tests Recall@k, MRR, and nDCG calculations.

---

## 10. Step-by-Step Operational Runbook

### Step 1: Ingest Corpus & Generate Manifest
```powershell
python -m cross_lingual_rag.src.ingestion
```
*Output:* Creates `data/processed/chunks_manifest.json` and `data/processed/corpus_metadata.json`.

### Step 2: Build Dual FAISS Vector Indexes
```powershell
python -m cross_lingual_rag.src.vector_store
```
*Output:* Builds and serializes:
- `data/indexes/english/index.faiss` & `metadata_map.pkl`
- `data/indexes/multilingual/index.faiss` & `metadata_map.pkl`

### Step 3: Run Integration Test Suite
```powershell
pytest cross_lingual_rag/tests/test_basic_pipeline.py -v
```
*Output:* Validates all 7 tests pass with 0 errors.

### Step 4: Execute Benchmark Suite
```powershell
python -m cross_lingual_rag.src.pipelines
```
*Output:* Runs all enabled systems over the benchmark questions and populates `results/raw/`.

### Step 5: Generate Scientific Evaluation Report
```powershell
python -m cross_lingual_rag.src.evaluation
```
*Output:* Writes `results/csv/benchmark_results.csv` and `results/summaries/evaluation_report.md`.

### Step 6: Launch Interactive Streamlit Lab & Observability Workbench
```powershell
streamlit run cross_lingual_rag/app.py
```
*Output:* Opens interactive workbench at `http://localhost:8501`.

---

## 11. Deep Dive: Observability, LangSmith Integration & 100% Free AI Setup

### 11.1 The Observability Architecture (`src/observability.py`)
Observability in RAG is critical because errors cascade:
$$\text{Query} \xrightarrow{\text{Translation}} \text{Query}' \xrightarrow{\text{Embedding}} \vec{q} \xrightarrow{\text{FAISS}} \text{Chunks} \xrightarrow{\text{Prompt}} \text{Context} \xrightarrow{\text{LLM}} \text{Answer}$$

If an answer is incorrect, where did it fail?
- Did the translator distort technical terms? (**E1 - Translation Drift**)
- Did FAISS rank the gold passage below top-$k$? (**E2 - Retrieval Failure**)
- Did the LLM hallucinate despite having the passage in context? (**E3 - Generation Failure**)
- Did the LLM output degraded Hindi? (**E4 - Language Failure**)

`ObservabilityTracer` solves this by recording an **OpenTelemetry / LangSmith-compliant execution graph**:
- **Root Trace:** Encapsulates the entire execution (`run_id`, `question_id`, `system_id`, `query`, total duration).
- **Span 1: `machine_translation`:** Captures source text, translated English text, and translation duration in ms.
- **Span 2: `vector_retrieval`:** Captures query vectorization, top-$k$ chunk IDs, similarity scores, and FAISS lookup duration in ms.
- **Span 3: `llm_generation`:** Captures formatted prompt template, token usage counts, model name, and generation latency in ms.
- **Span 4: `scientific_evaluation`:** Captures Recall@1/3/5, MRR, and automated E1-E4 error categorization.

### 11.2 Dual Exporter: Local Free Store vs LangSmith Cloud

```
                               [Pipeline Execution Step]
                                           │
                                           ▼
                               ┌───────────────────────┐
                               │  ObservabilityTracer  │
                               └───────────┬───────────┘
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
        ┌─────────────────────────┐                 ┌─────────────────────────┐
        │ 100% Free Local Store   │                 │     LangSmith Cloud     │
        │ - results/traces/*.json │                 │ - smith.langchain.com   │
        │ - Zero External Calls   │                 │ - Free Developer Tier   │
        │ - Zero Cost ($0.00)     │                 │ - (LANGSMITH_API_KEY)   │
        └─────────────────────────┘                 └─────────────────────────┘
```

1. **100% Free Local Mode (Default):**
   - Requires **no account**, **no sign-up**, and **no internet connection**.
   - Traces are stored in `cross_lingual_rag/results/traces/{trace_id}.json`.
   - The built-in Streamlit **Observability & Trace Explorer** (Tab 2 in `app.py`) parses these traces into visual Gantt/Waterfall charts and interactive JSON inspectors.

2. **LangSmith Cloud Mode (Optional Free Tier):**
   - LangSmith provides a generous free developer tier (5,000 free traces per month).
   - Simply set your environment variable:
     ```powershell
     $env:LANGSMITH_API_KEY = "lsv2_pt_..."
     $env:LANGSMITH_PROJECT = "cross-lingual-academic-rag"
     ```
   - Traces automatically sync directly to your LangSmith web dashboard at `https://smith.langchain.com/`!

### 11.3 100% Free AI Engine Stack (What AI You Need)

| Component | 100% Free Recommended Option | Setup Instructions | Cost |
| :--- | :--- | :--- | :--- |
| **LLM Generator** | **Google Gemini 2.0 / 1.5 Flash** | 1. Go to [Google AI Studio](https://aistudio.google.com/)<br>2. Click **Create API Key** (Free)<br>3. Set `$env:GEMINI_API_KEY = "AIza..."`<br>4. In `config.yaml`, set `provider: "gemini"`, `model: "gemini-2.0-flash"` | **$0.00** (Free 15 RPM, 1M TPM, 1,500 RPD) |
| **Local LLM Generator** | **Ollama (`llama3:8b` / `qwen2.5:7b`)** | 1. Install Ollama from [ollama.com](https://ollama.com/)<br>2. Run `ollama run qwen2.5:7b`<br>3. In `config.yaml`, set `provider: "ollama"`, `model: "qwen2.5:7b"` | **$0.00** (Completely offline, zero API keys) |
| **Translation Engine** | **`deep-translator` (Google Translate web)** | Already pre-installed and configured! Uses web MT endpoint with built-in retry and fallback. | **$0.00** (Zero keys needed) |
| **English Embeddings** | **`all-mpnet-base-v2`** | Pre-downloaded via Hugging Face `sentence-transformers`. Runs locally on CPU/GPU. | **$0.00** (Open source) |
| **Multilingual Embeddings** | **`paraphrase-multilingual-MiniLM-L12-v2`** | Pre-downloaded via Hugging Face `sentence-transformers`. Runs locally on CPU/GPU. | **$0.00** (Open source) |
| **Vector Database** | **`faiss-cpu`** | Pre-installed and compiled. Stores indexes locally in `data/indexes/`. | **$0.00** (Open source) |
| **Observability Dashboard** | **Local Free Trace Workbench + LangSmith** | Integrated directly into `app.py` Tab 2 + optional LangSmith export. | **$0.00** (Free tier) |

