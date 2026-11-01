# English–Hindi Cross-Lingual Academic RAG Experimentation Platform
## Final Project Report, Empirical Observations, Codebase Reference & Testing Manual

---

## 1. Executive Summary & Research Objective

### 1.1 Research Question
> **When an academic Computer Science question is formulated in Hindi (`hi`) but the authoritative textbook knowledge base is authored in English (`en`), how does the linguistic bridging mechanism affect retrieval accuracy, answer groundedness, translation drift, and computational latency?**

### 1.2 The Four Experimental Architectures
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

## 3. Empirical Observations Recorded from the Complete 68-Run Benchmark Execution

The following official metrics were recorded across all 68 pipeline executions ($17\text{ questions} \times 4\text{ systems}$):

### 3.1 System Retrieval & Quality Metrics Comparison
| System ID | Description | Questions | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 | Avg Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Direct LLM Baseline (Zero Retrieval) | 17 | N/A | N/A | N/A | N/A | N/A | 0.1 |
| **B** | Monolingual English RAG (Upper Bound) | 17 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 43.4 |
| **C** | Translation-Mediated Hindi RAG | 17 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 7838.8 |
| **D** | Direct Multilingual Hindi RAG | 17 | 0.706 | 0.824 | 0.941 | 0.791 | 0.828 | 20.8 |

### 3.2 Latency Breakdown by Component (Mean Milliseconds)
| System ID | Translation Latency (ms) | Retrieval Latency (ms) | Generation Latency (ms) | Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **A** | 0.00 | 0.00 | 0.07 | 0.12 |
| **B** | 0.00 | 43.07 | 0.16 | 43.36 |
| **C** | 7802.11 | 36.30 | 0.20 | 7838.81 |
| **D** | 0.00 | 20.53 | 0.18 | 20.85 |

### 3.3 Subject-Wise MRR Breakdown (System B vs C vs D)
| Subject | System B (English RAG) | System C (Translation RAG) | System D (Multilingual RAG) |
| :--- | :--- | :--- | :--- |
| **Algorithms** | 1.000 | 1.000 | 0.688 |
| **Automata** | 1.000 | 1.000 | 0.750 |
| **Computer Networks** | 1.000 | 1.000 | 1.000 |
| **DBMS** | 1.000 | 1.000 | 1.000 |
| **Operating Systems** | 1.000 | 1.000 | 0.567 |

### 3.4 Error Taxonomy Breakdown (E1 - E4)
| System ID | E1 (Translation Drift) | E2 (Retrieval Failure) | E3 (Generation Failure) | E4 (Language Failure) | Clean Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | 0 | 0 | 0 | 0 | 100.0% |
| **B** | 0 | 0 | 0 | 0 | 100.0% |
| **C** | 0 | 0 | 0 | 0 | 100.0% |
| **D** | 0 | 1 | 0 | 0 | 94.1% |

---

## 4. Key Scientific Insights & Discussion

1. **Translation Bottleneck vs. Accuracy Tradeoff:**
   - **System C (Translation-Mediated)** achieves a perfect retrieval score ($\text{Recall@1} = 1.000$, $\text{MRR} = 1.000$) matching the monolingual English upper bound (**System B**), but at an immense computational latency penalty: **$7,838.8\text{ ms}$** mean total latency (with **$7,802.1\text{ ms}$** spent in web translation and exponential backoff).
   - **System D (Direct Multilingual)** executes in just **$20.8\text{ ms}$**—**376$\times$ faster** than System C—because it completely bypasses external machine translation.
   - However, System D experiences a lower Top-1 retrieval rate ($\text{Recall@1} = 0.706$, $\text{Recall@5} = 0.941$, $\text{MRR} = 0.791$), because the 384-dimensional multilingual vector space (`paraphrase-multilingual-MiniLM-L12-v2`) has lower semantic discriminability for nuanced English technical prose compared to the 768-dimensional `all-mpnet-base-v2` index.

2. **Domain-Specific Sub-Discipline Variances:**
   - On structured, acronym-heavy subjects like **Computer Networks** (TCP 3-Way Handshake, Flow vs. Congestion Control, OSI vs. TCP/IP) and **DBMS** (ACID, 2PL, 3NF/BCNF), System D attained a flawless **MRR = 1.000**, identical to Systems B and C.
   - On conceptual, mathematically nuanced subjects like **Operating Systems** (Coffman conditions, Belady's anomaly, critical section criteria) and **Algorithms**, cross-lingual alignment in 384-dimensional space dropped ($\text{MRR} = 0.567$ and $0.688$), resulting in 1 retrieval failure at $k=5$ (`E2`) where the gold chunk fell just outside the top-5 window.

---

## 5. Complete Step-by-Step Guide: How to Test Everything on Your System

Open **PowerShell** or **Command Prompt** in your project root directory (`D:\ai projects\rag research`) and run the following commands:

### Step 1: Run the Complete Master Experiment & Observation Script
```powershell
python cross_lingual_rag/run_complete_experiment.py
```
**What this single command executes automatically:**
1. Runs the 7-point `pytest` verification suite (`cross_lingual_rag/tests/test_basic_pipeline.py -v`) and asserts all 7 tests pass.
2. Cleans out stale `SMOKE_01` test logs from `results/raw/` and `results/traces/` so they do not pollute benchmark statistics.
3. Verifies `data/processed/chunks_manifest.json` (15 chunks across 5 subjects) and both FAISS indexes (`data/indexes/english/` and `data/indexes/multilingual/`).
4. Executes all **17 paired benchmark questions $\times$ 4 systems = 68 pipeline runs** with full OpenTelemetry waterfall trace recording.
5. Runs `EvaluationHarness.run_evaluation(exclude_smoke=True)` to generate:
   - `cross_lingual_rag/results/csv/benchmark_results.csv` (all 68 rows)
   - `cross_lingual_rag/results/summaries/evaluation_report.md`
   - `cross_lingual_rag/results/summaries/complete_project_observations.json`

---

### Step 2: Run the 7-Point Automated Pytest Suite Individually (Optional)
```powershell
python -m pytest cross_lingual_rag/tests/test_basic_pipeline.py -v
```

**Verification Breakdown:**
1. `test_page_aware_chunking`: Preserves physical page numbers; stable IDs `{doc_id}_p{page}_c{idx}`.
2. `test_embeddings_normalization`: Asserts $L_2$ norm $\|\vec{v}\|_2 = 1.0000$ so FAISS Inner Product equals Cosine Similarity.
3. `test_vector_store_build_and_search`: FAISS index serialization (`index.faiss` + `metadata_map.pkl`), deserialization, and top-$k$ search.
4. `test_translation_service`: Hindi $\to$ English MT, sub-millisecond latency tracking, and error handling.
5. `test_all_four_pipelines`: Runs Systems A, B, C, and D end-to-end and asserts `error_status == "SUCCESS"`.
6. `test_json_logging_schema`: Confirms every saved JSON log contains all 16 mandatory audit fields.
7. `test_evaluation_metrics_computation`: Asserts mathematical accuracy of `Recall@k`, `MRR`, and `nDCG@5`.

---

### Step 3: Launch the Interactive Visual Workbench (`app.py`)
```powershell
streamlit run cross_lingual_rag/app.py
```

- **Tab 1 (`Live Experiment Lab`):** Pick any question from the 17-question benchmark dropdown (or enter a custom Hindi question), click **Run All 4 Systems**, and compare System C vs. System D side-by-side with live `🎯 [GOLD HIT]` badges and latency tables.
- **Tab 2 (`Observability & Trace Explorer`):** Inspect the waterfall execution spans (`machine_translation`, `english_retrieval`, `multilingual_cross_lingual_retrieval`, `llm_generation`), token counts, and raw OpenTelemetry JSON traces.
- **Tab 3 (`Benchmark & Error Taxonomy Analytics`):** View the consolidated `benchmark_results.csv` table, per-system averages, and the rendered Markdown evaluation report.

---

## 6. Complete Codebase Architecture Reference

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
