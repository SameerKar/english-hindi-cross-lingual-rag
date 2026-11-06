# Scientific Evaluation Report: English–Hindi Cross-Lingual Academic RAG
**Total Benchmark Executions Evaluated:** 20

## 1. System Retrieval & Quality Metrics Comparison
| System ID | Description | Questions | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 | Avg Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Direct LLM Baseline (Zero Retrieval) | 5 | N/A | N/A | N/A | N/A | N/A | 3109.4 |
| **B** | Monolingual English RAG (Upper Bound) | 5 | 0.600 | 0.800 | 1.000 | 0.740 | 0.804 | 3210.5 |
| **C** | Translation-Mediated Hindi RAG | 5 | 0.600 | 0.800 | 1.000 | 0.740 | 0.804 | 16239.7 |
| **D** | Direct Multilingual Hindi RAG | 5 | 0.600 | 0.800 | 0.800 | 0.700 | 0.726 | 10201.3 |

## 2. Latency Breakdown by Component (Mean Milliseconds)
| System ID | Translation Latency (ms) | Retrieval Latency (ms) | Generation Latency (ms) | Total Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **A** | 0.00 | 0.00 | 3109.30 | 3109.41 |
| **B** | 0.00 | 92.13 | 3118.17 | 3210.52 |
| **C** | 10142.43 | 45.69 | 6051.16 | 16239.69 |
| **D** | 0.00 | 29.36 | 10108.82 | 10201.26 |

## 3. Subject-Wise MRR Breakdown (System B vs C vs D)
| Subject | System B (English RAG) | System C (Translation RAG) | System D (Multilingual RAG) |
| :--- | :--- | :--- | :--- |
| **Algorithms** | 1.000 | 1.000 | 1.000 |
| **Automata** | 0.200 | 0.200 | 1.000 |
| **Computer Networks** | 0.500 | 0.500 | 1.000 |
| **DBMS** | 1.000 | 1.000 | 0.000 |
| **Operating Systems** | 1.000 | 1.000 | 0.500 |

## 4. Error Taxonomy Breakdown (E1 - E4)
| System ID | E1 (Translation Drift) | E2 (Retrieval Failure) | E3 (Generation Failure) | E4 (Language Failure) | Clean Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | 0 | 0 | 0 | 0 | 100.0% |
| **B** | 0 | 0 | 0 | 0 | 100.0% |
| **C** | 0 | 0 | 0 | 2 | 60.0% |
| **D** | 0 | 1 | 0 | 0 | 80.0% |