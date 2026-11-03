# Scientific Evaluation Report: English–Hindi Cross-Lingual Academic RAG
**Total Benchmark Executions Evaluated:** 73

## 1. System Retrieval & Quality Metrics Comparison
| System ID | Description | Questions | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 | Avg Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Direct LLM Baseline (Zero Retrieval) | 17 | N/A | N/A | N/A | N/A | N/A | 0.1 |
| **B** | Monolingual English RAG (Upper Bound) | 18 | 0.944 | 0.944 | 0.944 | 0.944 | 0.944 | 42.6 |
| **C** | Translation-Mediated Hindi RAG | 19 | 0.895 | 0.895 | 0.895 | 0.895 | 0.895 | 10416.6 |
| **D** | Direct Multilingual Hindi RAG | 19 | 0.632 | 0.737 | 0.842 | 0.708 | 0.741 | 297.5 |

## 2. Latency Breakdown by Component (Mean Milliseconds)
| System ID | Translation Latency (ms) | Retrieval Latency (ms) | Generation Latency (ms) | Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **A** | 0.00 | 0.00 | 0.06 | 0.12 |
| **B** | 0.00 | 42.28 | 0.22 | 42.64 |
| **C** | 10115.20 | 42.10 | 259.03 | 10416.55 |
| **D** | 0.00 | 25.15 | 272.22 | 297.51 |

## 3. Subject-Wise MRR Breakdown (System B vs C vs D)
| Subject | System B (English RAG) | System C (Translation RAG) | System D (Multilingual RAG) |
| :--- | :--- | :--- | :--- |
| **Algorithms** | 1.000 | 1.000 | 0.688 |
| **Automata** | 1.000 | 1.000 | 0.750 |
| **Computer Networks** | 1.000 | 1.000 | 1.000 |
| **DBMS** | 1.000 | 1.000 | 1.000 |
| **Operating Systems** | 1.000 | 1.000 | 0.567 |
| **custom** | 0.000 | 0.000 | 0.000 |
| **custom_kb** | N/A | 0.000 | 0.000 |

## 4. Error Taxonomy Breakdown (E1 - E4)
| System ID | E1 (Translation Drift) | E2 (Retrieval Failure) | E3 (Generation Failure) | E4 (Language Failure) | Clean Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | 0 | 0 | 0 | 0 | 100.0% |
| **B** | 0 | 0 | 0 | 0 | 100.0% |
| **C** | 0 | 0 | 0 | 0 | 100.0% |
| **D** | 0 | 1 | 0 | 0 | 94.7% |