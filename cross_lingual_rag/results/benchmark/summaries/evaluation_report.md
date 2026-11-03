# Scientific Evaluation Report: English–Hindi Cross-Lingual Academic RAG
**Total Benchmark Executions Evaluated:** 20

## 1. System Retrieval & Quality Metrics Comparison
| System ID | Description | Questions | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 | Avg Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Direct LLM Baseline (Zero Retrieval) | 5 | N/A | N/A | N/A | N/A | N/A | 5309.6 |
| **B** | Monolingual English RAG (Upper Bound) | 5 | 0.800 | 1.000 | 1.000 | 0.900 | 0.926 | 3324.2 |
| **C** | Translation-Mediated Hindi RAG | 5 | 0.800 | 1.000 | 1.000 | 0.900 | 0.926 | 13201.7 |
| **D** | Direct Multilingual Hindi RAG | 5 | 0.400 | 0.600 | 0.800 | 0.550 | 0.612 | 6405.8 |

## 2. Latency Breakdown by Component (Mean Milliseconds)
| System ID | Translation Latency (ms) | Retrieval Latency (ms) | Generation Latency (ms) | Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **A** | 0.00 | 0.00 | 5309.53 | 5309.64 |
| **B** | 0.00 | 65.79 | 3258.25 | 3324.24 |
| **C** | 10408.35 | 47.20 | 2745.68 | 13201.65 |
| **D** | 0.00 | 31.82 | 6373.67 | 6405.79 |

## 3. Subject-Wise MRR Breakdown (System B vs C vs D)
| Subject | System B (English RAG) | System C (Translation RAG) | System D (Multilingual RAG) |
| :--- | :--- | :--- | :--- |
| **Algorithms** | 0.900 | 0.900 | 0.550 |

## 4. Error Taxonomy Breakdown (E1 - E4)
| System ID | E1 (Translation Drift) | E2 (Retrieval Failure) | E3 (Generation Failure) | E4 (Language Failure) | Clean Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | 0 | 0 | 0 | 0 | 100.0% |
| **B** | 0 | 0 | 0 | 0 | 100.0% |
| **C** | 0 | 0 | 0 | 0 | 100.0% |
| **D** | 0 | 1 | 0 | 0 | 80.0% |