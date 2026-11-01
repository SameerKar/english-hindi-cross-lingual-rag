"""
Cross-Lingual Academic RAG Experimentation Platform & Observability Workbench.
Features:
1. Interactive Side-by-Side Comparison (System C vs System D vs Baselines A & B).
2. Built-in LangSmith-Style Observability & Trace Explorer (Waterfall spans, token metrics, latency breakdowns).
3. Benchmark & Error Taxonomy Analytics (Recall@1/3/5, MRR, E1-E4 errors).
"""

import os
import sys
import json
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from src.utils import load_config, get_project_root
from src.pipelines import PipelineOrchestrator
from src.observability import ObservabilityTracer

st.set_page_config(
    page_title="Cross-Lingual RAG Lab & Observability",
    page_icon="🔬",
    layout="wide"
)

@st.cache_resource
def get_orchestrator():
    config = load_config()
    return PipelineOrchestrator(config)

orchestrator = get_orchestrator()
tracer = orchestrator.tracer

st.title("🔬 Cross-Lingual Academic RAG Experimentation & Observability Platform")

# Top Status Banner: Observability & AI Engine Status
status_col1, status_col2, status_col3 = st.columns(3)
with status_col1:
    gen_provider = orchestrator.generator.provider
    gen_model = orchestrator.generator.model_name
    st.caption(f"🤖 **LLM Generator:** `{gen_provider}` (`{gen_model}` | temp=0.0)")
with status_col2:
    trans_provider = orchestrator.translator.provider
    st.caption(f"🌐 **Translation Engine:** `{trans_provider}` (100% Free)")
with status_col3:
    if tracer.langsmith_enabled:
        st.success("🟢 **LangSmith Cloud:** Connected")
    else:
        st.info("📦 **Observability Mode:** Local Free Trace Store (Zero Cost)")

tabs = st.tabs([
    "🔬 Live Experiment Lab",
    "📊 Observability & Trace Explorer (LangSmith Workbench)",
    "📈 Benchmark & Error Taxonomy Analytics"
])

# ==============================================================================
# TAB 1: LIVE EXPERIMENT LAB
# ==============================================================================
with tabs[0]:
    st.markdown("### Test & Compare Systems A, B, C, and D")
    
    # Sidebar / Selection
    bench_path = Path(orchestrator.config["paths"]["benchmark_file"])
    benchmark_options = []
    bench_dict = {}
    if bench_path.exists():
        try:
            df_bench = pd.read_csv(bench_path)
            for _, r in df_bench.iterrows():
                opt_label = f"[{r.get('subject', 'CS')}] {r['question_id']}: {str(r['question_hi'])[:50]}..."
                benchmark_options.append(opt_label)
                bench_dict[opt_label] = r
        except Exception as e:
            st.error(f"Failed to load benchmark CSV: {e}")

    col_sel, col_empty = st.columns([2, 1])
    with col_sel:
        selected_bench = st.selectbox(
            "Load Academic Question from Benchmark:",
            ["-- Manual Input --"] + benchmark_options
        )

    if selected_bench != "-- Manual Input --":
        row_info = bench_dict[selected_bench]
        default_hi = str(row_info["question_hi"])
        default_en = str(row_info["question_en"])
        default_qid = str(row_info["question_id"])
        default_subj = str(row_info.get("subject", "general"))
        default_cat = str(row_info.get("category", "general"))
        gold_chunk = str(row_info.get("gold_chunk_id", "N/A"))
    else:
        default_hi = "डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक किनारों (negative edge weights) वाले ग्राफ पर क्यों विफल हो जाता है?"
        default_en = "Why does Dijkstra's algorithm fail when a graph contains negative edge weights?"
        default_qid = "DEMO_01"
        default_subj = "Algorithms"
        default_cat = "Conceptual explanation"
        gold_chunk = "algorithms_algorithms_fundamentals_p2_c0"

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        hindi_input = st.text_area("Hindi Question (Input for Systems C & D):", value=default_hi, height=80)
    with col_q2:
        english_input = st.text_area("English Question (Input for System B Baseline):", value=default_en, height=80)

    btn_cols = st.columns([1, 1, 1, 1])
    btn_all = btn_cols[0].button("🚀 Run All 4 Systems", type="primary")
    btn_c = btn_cols[1].button("Run System C (Translation RAG)")
    btn_d = btn_cols[2].button("Run System D (Multilingual RAG)")
    btn_ab = btn_cols[3].button("Run Baselines (A & B)")

    if btn_all or btn_c or btn_d or btn_ab:
        res_a, res_b, res_c, res_d = None, None, None, None

        with st.spinner("Executing RAG pipelines and generating traces..."):
            if btn_all or btn_c:
                res_c = orchestrator.execute_system_C(hindi_input, default_qid, default_subj, default_cat)
            if btn_all or btn_d:
                res_d = orchestrator.execute_system_D(hindi_input, default_qid, default_subj, default_cat)
            if btn_all or btn_ab:
                res_a = orchestrator.execute_system_A(hindi_input, default_qid, default_subj, default_cat)
                res_b = orchestrator.execute_system_B(english_input, default_qid, default_subj, default_cat)

        if res_c and res_d:
            st.markdown("---")
            st.subheader("⚖️ Primary Scientific Comparison: System C vs System D")
            col_res_c, col_res_d = st.columns(2)

            with col_res_c:
                st.info("### 🌐 System C: Translation-Mediated RAG")
                st.markdown("**1. Translated English Query:**")
                st.code(res_c.get("translated_question", ""), language="text")
                st.caption(f"Translation Latency: {res_c['latencies']['translation_latency_ms']:.1f} ms")

                st.markdown("**2. Retrieved English Chunks:**")
                for r, (ch, sc) in enumerate(zip(res_c.get("retrieved_chunks", []), res_c.get("retrieval_scores", [])), 1):
                    hit = "🎯 [GOLD HIT]" if gold_chunk in ch else ""
                    st.markdown(f"- Rank {r}: `{ch}` (Score: `{sc:.4f}`) {hit}")
                st.caption(f"Retrieval Latency: {res_c['latencies']['retrieval_latency_ms']:.1f} ms")

                st.markdown("**3. Final Hindi Answer:**")
                st.success(res_c.get("generated_answer", ""))
                st.caption(f"Generation Latency: {res_c['latencies']['generation_latency_ms']:.1f} ms | Total: {res_c['latencies']['total_latency_ms']:.1f} ms")

            with col_res_d:
                st.info("### 🔀 System D: Direct Multilingual RAG")
                st.markdown("**1. Zero-Shot Cross-Lingual Search:**")
                st.caption("No text translation step. Hindi query directly mapped to cross-lingual embedding space.")

                st.markdown("**2. Retrieved English Chunks:**")
                for r, (ch, sc) in enumerate(zip(res_d.get("retrieved_chunks", []), res_d.get("retrieval_scores", [])), 1):
                    hit = "🎯 [GOLD HIT]" if gold_chunk in ch else ""
                    st.markdown(f"- Rank {r}: `{ch}` (Score: `{sc:.4f}`) {hit}")
                st.caption(f"Retrieval Latency: {res_d['latencies']['retrieval_latency_ms']:.1f} ms")

                st.markdown("**3. Final Hindi Answer:**")
                st.success(res_d.get("generated_answer", ""))
                st.caption(f"Generation Latency: {res_d['latencies']['generation_latency_ms']:.1f} ms | Total: {res_d['latencies']['total_latency_ms']:.1f} ms")

            # Comparative Latency Bar Chart
            st.markdown("#### ⏱️ Latency Breakdown Comparison")
            lat_data = {
                "Pipeline": ["System C (Translation RAG)", "System D (Multilingual RAG)"],
                "Translation (ms)": [res_c['latencies']['translation_latency_ms'], 0.0],
                "Retrieval (ms)": [res_c['latencies']['retrieval_latency_ms'], res_d['latencies']['retrieval_latency_ms']],
                "Generation (ms)": [res_c['latencies']['generation_latency_ms'], res_d['latencies']['generation_latency_ms']],
                "Total (ms)": [res_c['latencies']['total_latency_ms'], res_d['latencies']['total_latency_ms']]
            }
            st.dataframe(pd.DataFrame(lat_data), use_container_width=True)

        if res_a or res_b:
            st.markdown("---")
            st.subheader("📊 Baseline Benchmarks (Systems A & B)")
            b_col1, b_col2 = st.columns(2)
            if res_a:
                with b_col1:
                    st.warning("### 🤖 System A: Direct LLM (Zero-Retrieval)")
                    st.write(res_a.get("generated_answer", ""))
                    st.caption(f"Total Latency: {res_a['latencies']['total_latency_ms']:.1f} ms")
            if res_b:
                with b_col2:
                    st.success("### 📖 System B: Monolingual English RAG")
                    st.write(res_b.get("generated_answer", ""))
                    st.caption(f"Total Latency: {res_b['latencies']['total_latency_ms']:.1f} ms")
                    with st.expander("Retrieved Chunks (System B)"):
                        for ch, sc in zip(res_b.get("retrieved_chunks", []), res_b.get("retrieval_scores", [])):
                            st.write(f"- `{ch}` (Score: {sc:.4f})")

# ==============================================================================
# TAB 2: OBSERVABILITY & TRACE EXPLORER (LANGSMITH WORKBENCH)
# ==============================================================================
with tabs[1]:
    st.markdown("### 📊 Observability & Trace Explorer")
    st.markdown(
        "A deep-inspection trace viewer capturing execution spans, inputs, outputs, "
        "and latency profiles for every RAG pipeline invocation."
    )

    traces = tracer.load_all_traces()
    if not traces:
        st.info("No traces captured yet. Execute a query in Tab 1 to inspect its trace tree.")
    else:
        st.write(f"Total Traces Recorded: **{len(traces)}**")

        trace_options = [
            f"[{t.get('system_id', '?')}] {t.get('question_id', 'Q')} | {t.get('query', '')[:40]}... ({t.get('total_latency_ms', 0):.1f} ms) | ID: {t.get('trace_id')[:8]}"
            for t in traces
        ]
        selected_idx = st.selectbox("Select Trace to Inspect:", range(len(trace_options)), format_func=lambda i: trace_options[i])
        selected_trace = traces[selected_idx]

        # Trace Overview Cards
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        t_col1.metric("System ID", selected_trace.get("system_id", "N/A"))
        t_col2.metric("Total Latency", f"{selected_trace.get('total_latency_ms', 0):.1f} ms")
        t_col3.metric("Spans Count", len(selected_trace.get("spans", [])))
        t_col4.metric("Status", selected_trace.get("status", "SUCCESS"))

        # Waterfall Timeline
        st.markdown("#### 🌊 Execution Waterfall Spans")
        spans = selected_trace.get("spans", [])
        if spans:
            span_rows = []
            for sp in spans:
                span_rows.append({
                    "Span Name": sp.get("name"),
                    "Type": sp.get("span_type"),
                    "Duration (ms)": sp.get("latency_ms"),
                    "Status": sp.get("status")
                })
            st.dataframe(pd.DataFrame(span_rows), use_container_width=True)

            # Span In-Depth Inspector
            st.markdown("#### 🔍 Span Inspector (Inputs & Outputs)")
            for sp in spans:
                with st.expander(f"🔹 Span: {sp.get('name')} ({sp.get('latency_ms', 0):.1f} ms) - Type: `{sp.get('span_type')}`"):
                    c_in, c_out = st.columns(2)
                    with c_in:
                        st.markdown("**Inputs:**")
                        st.json(sp.get("inputs", {}))
                    with c_out:
                        st.markdown("**Outputs:**")
                        st.json(sp.get("outputs", {}))

        # Full Trace Raw JSON
        with st.expander("📄 View Complete OpenTelemetry / LangSmith Trace JSON"):
            st.json(selected_trace)

# ==============================================================================
# TAB 3: BENCHMARK & ERROR TAXONOMY ANALYTICS
# ==============================================================================
with tabs[2]:
    st.markdown("### 📈 Scientific Benchmark & Error Taxonomy Analytics")
    
    csv_path = Path(orchestrator.config["paths"]["results_csv_dir"]) / "benchmark_results.csv"
    summary_path = Path(orchestrator.config["paths"]["results_summary_dir"]) / "evaluation_report.md"

    if csv_path.exists():
        df_results = pd.read_csv(csv_path)
        st.subheader("Benchmark Execution Summary")
        st.dataframe(df_results, use_container_width=True)

        # Aggregated Metrics per System
        st.markdown("#### Performance Metrics per System")
        summary_agg = df_results.groupby("system_id").agg({
            "recall@1": "mean",
            "recall@3": "mean",
            "recall@5": "mean",
            "mrr": "mean",
            "total_latency_ms": "mean"
        }).reset_index()
        st.dataframe(summary_agg.style.format({
            "recall@1": "{:.3f}",
            "recall@3": "{:.3f}",
            "recall@5": "{:.3f}",
            "mrr": "{:.3f}",
            "total_latency_ms": "{:.1f} ms"
        }), use_container_width=True)

        if summary_path.exists():
            st.markdown("---")
            st.subheader("Scientific Markdown Report")
            with open(summary_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())
    else:
        st.info("No benchmark results generated yet. Run `python -m cross_lingual_rag.src.evaluation` to populate.")
