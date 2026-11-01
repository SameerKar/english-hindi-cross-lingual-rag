# Scientific Evaluation Report: English–Hindi Cross-Lingual Academic RAG
**Total Benchmark Executions Evaluated:** 70

## 1. System Retrieval & Quality Metrics Comparison
| System ID | Description | Questions | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 | Avg Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Direct LLM Baseline (Zero Retrieval) | 17 | N/A | N/A | N/A | N/A | N/A | 0.1 |
| **B** | Monolingual English RAG (Upper Bound) | 17 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 40.7 |
| **C** | Translation-Mediated Hindi RAG | 18 | 0.944 | 0.944 | 0.944 | 0.944 | 0.944 | 10445.9 |
| **D** | Direct Multilingual Hindi RAG | 18 | 0.667 | 0.778 | 0.889 | 0.747 | 0.782 | 19.6 |

## 2. Latency Breakdown by Component (Mean Milliseconds)
| System ID | Translation Latency (ms) | Retrieval Latency (ms) | Generation Latency (ms) | Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **A** | 0.00 | 0.00 | 0.06 | 0.12 |
| **B** | 0.00 | 40.37 | 0.18 | 40.69 |
| **C** | 10409.33 | 36.11 | 0.20 | 10445.86 |
| **D** | 0.00 | 19.33 | 0.18 | 19.64 |

## 3. Subject-Wise MRR Breakdown (System B vs C vs D)
| Subject | System B (English RAG) | System C (Translation RAG) | System D (Multilingual RAG) |
| :--- | :--- | :--- | :--- |
| **Algorithms** | 1.000 | 1.000 | 0.688 |
| **Automata** | 1.000 | 1.000 | 0.750 |
| **Computer Networks** | 1.000 | 1.000 | 1.000 |
| **DBMS** | 1.000 | 1.000 | 1.000 |
| **Operating Systems** | 1.000 | 1.000 | 0.567 |
| **custom_kb** | N/A | 0.000 | 0.000 |

## 4. Error Taxonomy Breakdown (E1 - E4)
| System ID | E1 (Translation Drift) | E2 (Retrieval Failure) | E3 (Generation Failure) | E4 (Language Failure) | Clean Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | 0 | 0 | 0 | 0 | 100.0% |
| **B** | 0 | 0 | 0 | 0 | 100.0% |
| **C** | 0 | 0 | 0 | 0 | 100.0% |
| **D** | 0 | 1 | 0 | 0 | 94.4% |