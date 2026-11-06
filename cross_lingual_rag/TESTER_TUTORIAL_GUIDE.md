# Cross-Lingual Academic RAG Platform: Tester & Evaluator Guide

Welcome to the **English–Hindi Cross-Lingual Academic Retrieval-Augmented Generation (RAG)** platform. This guide provides step-by-step instructions for non-technical evaluators and researchers to set up, run, and test the entire system from a single screen.

---

## 1. What This System Does

This platform evaluates how well modern AI systems can answer academic computer science questions in **Hindi** using open-access English textbooks across five core subjects:
1. **Algorithms** (e.g., Dijkstra's algorithm, divide & conquer, time complexity)
2. **Automata & Theory of Computation** (e.g., DFAs, NFAs, Turing machines, P vs NP)
3. **Database Management Systems (DBMS)** (e.g., ACID transactions, 3NF/BCNF normalization, SQL)
4. **Operating Systems** (e.g., Coffman deadlock conditions, paging, virtual memory)
5. **Computer Networks** (e.g., TCP 3-way handshake, routing, congestion control)

### The Four Systems Compared (A / B / C / D)

| System | Name | Pipeline Workflow | Why We Test It |
| :--- | :--- | :--- | :--- |
| **System A** | **Baseline LLM (No RAG)** | Hindi Question → Direct Gemini 3.1 Flash Lite → Hindi Answer | Measures the model's pure internal memorization without textbook citations. |
| **System B** | **Monolingual English RAG** | English Question → English FAISS Vector Store (`all-mpnet-base-v2`) → English Answer → Hindi Answer | Serves as the upper-bound benchmark when input and corpus share the same language. |
| **System C** | **Translation-Mediated RAG** | Hindi Question → Translated to English Query → English FAISS Vector Store → English Intermediate Answer → Final Hindi Answer | Tests the classic translation pipeline and observes if any translation drift occurs. |
| **System D** | **Direct Multilingual RAG** | Hindi Question → Multilingual FAISS Vector Store (`paraphrase-multilingual-MiniLM-L12-v2`) → Direct Hindi Answer Generation | Cross-lingual dense vector retrieval without query translation. |

---

## 2. Requirements & Prerequisites

- **Operating System**: Windows 10/11, macOS, or Linux.
- **Python**: Version **3.10, 3.11, or 3.12** installed ([python.org](https://www.python.org/downloads/)).
  - *Windows note*: Check the box **"Add Python to PATH"** during installation.
- **Internet Connection**: Needed on initial launch to download required Python packages and embedding models.
- **Google Gemini API Key** *(Optional but recommended)*:
  - Get a free key from [Google AI Studio](https://aistudio.google.com/).
  - If no key is supplied, the system automatically uses deterministic mock/fallback responses so you can still test everything offline.

---

## 3. Quick Start (One-Click)

### Windows Users
1. Unzip the downloaded project folder.
2. Double-click the file named:
   ```cmd
   start_windows.bat
   ```
3. The script will automatically:
   - Create a virtual environment (`.venv`).
   - Install required dependencies from `requirements.txt`.
   - Initialize `.env` if not already present.
   - Launch your web browser to **`http://127.0.0.1:8000`**.
   - Start the backend server.

### macOS & Linux Users
1. Open a terminal in the project directory.
2. Make the script executable and run it:
   ```bash
   chmod +x start_macos_linux.sh
   ./start_macos_linux.sh
   ```
3. Your browser will automatically open to **`http://127.0.0.1:8000`**.

---

## 4. Single-Screen Web UI Walkthrough

Once opened, everything can be operated from the web interface at `http://127.0.0.1:8000`:

```
┌────────────────────────────────────────────────────────────────────────┐
│  ENGLISH-HINDI CROSS-LINGUAL ACADEMIC RAG RESEARCH STUDIO              │
│  [Status: Ready]  [Corpus: 32 Docs / 4,411 Chunks]  [Model: Gemini 3.1]│
├───────────────┬────────────────────────────────────────────────────────┤
│ Navigation    │ Main Workspace Screen                                  │
│               │                                                        │
│ 1. Dashboard  │  ● System overview, indexed document count, quick stats│
│ 2. Ask & Test │  ● Interactive Side-by-Side Comparison of A / B / C / D │
│ 3. Reference  │  ● Search & read all 32 textbooks & license manifests  │
│ 4. Custom Doc │  ● Upload your own PDF/TXT/DOCX in an isolated space   │
│ 5. Benchmark  │  ● Run 1-click test suites (Smoke test, 120-Q bench)   │
│ 6. Results    │  ● Interactive tables, Recall, MRR, latency, CSV export│
│ 7. Settings   │  ● Change API keys, top-k chunks, temperature (0.0)    │
└───────────────┴────────────────────────────────────────────────────────┘
```

### Step-by-Step UI Testing:

### A. Testing "Ask & Compare A/B/C/D"
1. Click **"Ask & Compare"** in the sidebar.
2. Select one of the pre-loaded academic questions (or type your own in Hindi or English):
   - *Example Hindi Question*: `डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक किनारों (negative edge weights) पर क्यों विफल हो जाता है?`
   - *Example English Question*: `Why does Dijkstra's algorithm fail when a graph contains negative edge weights?`
3. Click **"Run All 4 Systems"**.
4. You will see four cards side-by-side:
   - **System A**: Direct LLM response (0 chunks retrieved).
   - **System B**: English RAG response with retrieved text passages from Jeff Erickson's *Algorithms*.
   - **System C**: Translated query (`"Why does Dijkstra's algorithm fail with negative edges?"`), retrieved passages, intermediate English response, and final Hindi answer.
   - **System D**: Direct multilingual dense retrieval passages and final Hindi response with technical terms preserved.
5. Inspect the **latency meters** under each card (translation time, retrieval time, generation time).

### B. Browsing the Reference Corpus
1. Click **"Reference Corpus"** in the sidebar.
2. Browse through all 32 official textbooks across Algorithms, Automata, DBMS, Operating Systems, and Networks.
3. Click on any document (e.g. *Database Design 2nd Edition* or *Operating Systems and Middleware*) to view its physical page count, chunk count, SHA-256 hash, and Creative Commons license attribution.

### C. Uploading Custom Documents (Isolated Mode)
1. Click **"Custom Uploads"**.
2. Upload any PDF, TXT, Markdown, or DOCX document.
3. The system will build a dedicated, isolated workspace index without touching the official benchmark reference corpus.
4. Test queries specifically on your uploaded material.

### D. Running Benchmarks & Viewing Reports
1. Click **"Benchmark Runner"**.
2. Select **"Run 5-Scenario Dry Run"** or **"Run Full 120-Question Benchmark"**.
3. Watch the real-time execution progress across all four systems.
4. When finished, click **"Results & Analytics"** to view Recall@1/3/5, MRR, nDCG@5, and download the full CSV report.

---

## 5. Command-Line Dry Run & Testing

If you prefer testing directly from the terminal or executing automated regression tests:

### A. Run Automated Unit Tests (15 tests)
```bash
python -m pytest cross_lingual_rag/tests/test_basic_pipeline.py cross_lingual_rag/tests/test_mandatory_spec.py -v
```
*(All 15 tests should pass with green status.)*

### B. Run the 5-Scenario Cross-Subject Dry Run
```bash
python cross_lingual_rag/run_complete_experiment.py --dry-run
```
This tests one question from every academic subject across all four systems (20 runs total), performs scientific evaluation, and generates reports.

### C. Run the Full 120-Question Academic Benchmark
```bash
python cross_lingual_rag/run_complete_experiment.py
```

---

## 6. Where to Find Reports and Output Files

All experiment logs and evaluation reports are automatically organized into standard folders:

| File / Folder Path | Description |
| :--- | :--- |
| [`results/benchmark/summaries/dry_run_evaluation_report.md`](file:///d:/ai%20projects/rag%20research/cross_lingual_rag/results/benchmark/summaries/dry_run_evaluation_report.md) | **Markdown Summary Report** with Recall@1/3/5, MRR, latency breakdowns, and error analysis. |
| [`results/benchmark/csv/dry_run_results.csv`](file:///d:/ai%20projects/rag%20research/cross_lingual_rag/results/benchmark/csv/dry_run_results.csv) | **Consolidated CSV Spreadsheet** containing run-by-run scores, retrieved chunk IDs, and latency details. Open in Excel. |
| [`results/benchmark/summaries/dry_run_observations.json`](file:///d:/ai%20projects/rag%20research/cross_lingual_rag/results/benchmark/summaries/dry_run_observations.json) | **Machine-Readable JSON Observations** with verification hashes, pytest status, and system metrics. |
| [`results/benchmark/raw/system_{A,B,C,D}/`](file:///d:/ai%20projects/rag%20research/cross_lingual_rag/results/benchmark/raw) | **Raw JSON Trace Logs** for every individual pipeline execution, recording full prompts, chunk text, and translations. |
| [`data/corpus/reference/corpus_manifest.csv`](file:///d:/ai%20projects/rag%20research/cross_lingual_rag/data/corpus/reference/corpus_manifest.csv) | **Official Reference Corpus Catalog** listing all 32 textbooks, authors, licenses, and SHA-256 hashes. |

---

## 7. Troubleshooting & FAQ

- **Port 8000 already in use?**
  Open `cross_lingual_rag/config.yaml` or run with custom port:
  ```bash
  python server.py --port 8080
  ```
- **Want to use your own Gemini API Key?**
  Open `cross_lingual_rag/.env` and replace `GEMINI_API_KEY=your_key_here`, or enter it directly into the **Settings** tab in the web UI.
- **No API key?**
  The platform will seamlessly run in mock/deterministic mode so you can evaluate retrieval and latency offline.
- **Corpus re-indexing**:
  If you ever modify files in the reference folder, click **"Refresh & Rebuild Index"** in the UI Dashboard or run:
  ```bash
  python -c "from src.utils import load_config; from src.vector_store import build_dual_indexes; build_dual_indexes(load_config(), mode='reference')"
  ```

