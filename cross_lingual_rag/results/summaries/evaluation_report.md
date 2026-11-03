# Scientific Evaluation Report: English–Hindi Cross-Lingual Academic RAG
**Total Benchmark Executions Evaluated:** 68

## 1. System Retrieval & Quality Metrics Comparison
| System ID | Description | Questions | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 | Avg Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Direct LLM Baseline (Zero Retrieval) | 17 | N/A | N/A | N/A | N/A | N/A | 0.1 |
| **B** | Monolingual English RAG (Upper Bound) | 17 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 255.6 |
| **C** | Translation-Mediated Hindi RAG | 17 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 7176.7 |
| **D** | Direct Multilingual Hindi RAG | 17 | 0.647 | 0.765 | 0.765 | 0.706 | 0.721 | 3111.4 |

## 2. Latency Breakdown by Component (Mean Milliseconds)
| System ID | Translation Latency (ms) | Retrieval Latency (ms) | Generation Latency (ms) | Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **A** | 0.00 | 0.00 | 0.07 | 0.13 |
| **B** | 0.00 | 152.71 | 102.71 | 255.58 |
| **C** | 3820.36 | 45.24 | 3310.86 | 7176.73 |
| **D** | 0.00 | 25.85 | 3085.32 | 3111.37 |

## 3. Subject-Wise MRR Breakdown (System B vs C vs D)
| Subject | System B (English RAG) | System C (Translation RAG) | System D (Multilingual RAG) |
| :--- | :--- | :--- | :--- |
| **Algorithms** | 1.000 | 1.000 | 0.625 |
| **Automata** | 1.000 | 1.000 | 0.750 |
| **Computer Networks** | 1.000 | 1.000 | 1.000 |
| **DBMS** | 1.000 | 1.000 | 0.833 |
| **Operating Systems** | 1.000 | 1.000 | 0.333 |

## 4. Error Taxonomy Breakdown (E1 - E4)
| System ID | E1 (Translation Drift) | E2 (Retrieval Failure) | E3 (Generation Failure) | E4 (Language Failure) | Clean Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | 0 | 0 | 0 | 0 | 100.0% |
| **B** | 0 | 0 | 0 | 0 | 100.0% |
| **C** | 0 | 0 | 0 | 0 | 100.0% |
| **D** | 0 | 4 | 0 | 0 | 76.5% |