"""
Cross-Lingual Academic RAG Experimentation Platform & Observability Workbench.
Advanced Frontend Features:
1. Live Experiment Lab: Side-by-side comparison (Systems A, B, C, D) with real-time latency & gold hits.
2. Chunks & Corpus Explorer: Search, filter, and inspect page-aware textbook chunks in real time.
3. PDF Ingestion Studio: Drag-and-drop any PDF, ingest page-by-page, build dual FAISS indexes with live terminal logs.
4. Master Benchmark & Test Runner: Trigger 68-run benchmark or 7-point pytest suite with live streaming console output.
5. Observability & Trace Explorer: Waterfall spans, token metrics, latency breakdowns, and LangSmith traces.
6. Benchmark Analytics: Interactive tables, metric cards, and rendered scientific evaluation report.
"""

import os
import sys
import time
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st
import pandas as pd

# Add project root and cross_lingual_rag to sys.path
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from src.utils import load_config, get_project_root, ensure_directory
from src.pipelines import PipelineOrchestrator
from src.observability import ObservabilityTracer

st.set_page_config(
    page_title="Cross-Lingual Academic RAG Studio",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Sleek Dark Theme, Terminal styling, Metric badges)
st.markdown("""
<style>
    /* Metric & Card styling */
    .metric-card {
        background: #111420;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .gold-badge {
        background: #059669;
        color: white;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85em;
    }
    .terminal-box {
        background: #07090e;
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 12px;
        font-family: 'JetBrains Mono', Consolas, monospace;
        color: #38bdf8;
    }
    .badge-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .pill-green { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .pill-blue { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
    .pill-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_orchestrator():
    config = load_config()
    return PipelineOrchestrator(config)


orchestrator = get_orchestrator()
tracer = orchestrator.tracer
cfg = orchestrator.config

# Top Banner
st.title("🔬 English–Hindi Cross-Lingual Academic RAG Studio")
st.caption("Complete Experimentation, Real-Time Chunk Explorer, PDF Ingestion & Observability Platform")

# Status Indicators
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown(f'<span class="badge-pill pill-blue">LLM</span> **{orchestrator.generator.provider}** (`{orchestrator.generator.model_name}` | T=0.0)', unsafe_allow_html=True)
with col_s2:
    st.markdown(f'<span class="badge-pill pill-green">Translation</span> **{orchestrator.translator.provider}** (Hindi ↔ English)', unsafe_allow_html=True)
with col_s3:
    st.markdown(f'<span class="badge-pill pill-purple">Embeddings</span> **768d** English / **384d** Multi', unsafe_allow_html=True)
with col_s4:
    if tracer.langsmith_enabled:
        st.markdown('<span class="badge-pill pill-green">Traces</span> **LangSmith Cloud Connected**', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-pill pill-blue">Traces</span> **Local Free Trace Store**', unsafe_allow_html=True)

st.markdown("---")

# Main Navigation Tabs
tabs = st.tabs([
    "🔬 1. Live Experiment Lab",
    "📚 2. Chunks & Corpus Explorer",
    "📥 3. PDF Ingestion Studio",
    "⚡ 4. Master Benchmark & Test Runner",
    "🌊 5. Observability & Waterfall Traces",
    "📈 6. Benchmark Analytics & Report"
])


# ==============================================================================
# TAB 1: LIVE EXPERIMENT LAB
# ==============================================================================
with tabs[0]:
    st.subheader("Interactive Query & Cross-System Comparison")
    st.markdown("Test any academic question across **Systems A, B, C, and D** with live latency tracking and passage retrieval.")

    bench_path = Path(cfg["paths"]["benchmark_file"])
    benchmark_options = []
    bench_dict = {}
    if bench_path.exists():
        try:
            df_bench = pd.read_csv(bench_path)
            for _, r in df_bench.iterrows():
                opt_label = f"[{r.get('subject', 'CS')}] {r['question_id']}: {str(r['question_hi'])[:55]}..."
                benchmark_options.append(opt_label)
                bench_dict[opt_label] = r
        except Exception as e:
            st.error(f"Failed to load benchmark CSV: {e}")

    c_sel1, c_sel2 = st.columns([3, 1])
    with c_sel1:
        selected_bench = st.selectbox(
            "Load Question from 17-Question Benchmark (or pick Custom):",
            ["-- Enter Custom Question --"] + benchmark_options
        )
    with c_sel2:
        if st.button("🔄 Reload Orchestrator / Indexes"):
            st.cache_resource.clear()
            st.rerun()

    if selected_bench != "-- Enter Custom Question --":
        row_info = bench_dict[selected_bench]
        default_hi = str(row_info["question_hi"])
        default_en = str(row_info["question_en"])
        default_qid = str(row_info["question_id"])
        default_subj = str(row_info.get("subject", "general"))
        default_cat = str(row_info.get("category", "general"))
        gold_chunk = str(row_info.get("gold_chunk_id", "N/A"))
        gold_answer = str(row_info.get("gold_answer", "N/A"))
    else:
        default_hi = "डाइक्स्ट्रा का एल्गोरिदम ऋणात्मक किनारों (negative edge weights) वाले ग्राफ पर क्यों विफल हो जाता है?"
        default_en = "Why does Dijkstra's algorithm fail when a graph contains negative edge weights?"
        default_qid = "CUSTOM_01"
        default_subj = "Algorithms"
        default_cat = "Conceptual explanation"
        gold_chunk = "algorithms_algorithms_fundamentals_p2_c0"
        gold_answer = "Dijkstra's algorithm fails with negative weights because its greedy choice assumes finalized distances."

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        hindi_input = st.text_area("Hindi Query (Input for Systems C & D):", value=default_hi, height=85)
    with col_q2:
        english_input = st.text_area("English Query (Upper Bound for System B):", value=default_en, height=85)

    if gold_chunk != "N/A":
        st.caption(f"🎯 **Ground Truth Target Chunk:** `{gold_chunk}` | **Reference Answer:** {gold_answer}")

    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    btn_all = b_col1.button("🚀 Run All 4 Systems", type="primary", use_container_width=True)
    btn_c = b_col2.button("Run System C (Translation RAG)", use_container_width=True)
    btn_d = b_col3.button("Run System D (Multilingual RAG)", use_container_width=True)
    btn_b = b_col4.button("Run System B (English Upper-Bound)", use_container_width=True)

    if btn_all or btn_c or btn_d or btn_b:
        res_a, res_b, res_c, res_d = None, None, None, None

        with st.spinner("Executing RAG pipeline(s) and logging traces..."):
            if btn_all or btn_c:
                res_c = orchestrator.execute_system_C(hindi_input, default_qid, default_subj, default_cat)
            if btn_all or btn_d:
                res_d = orchestrator.execute_system_D(hindi_input, default_qid, default_subj, default_cat)
            if btn_all or btn_b:
                res_b = orchestrator.execute_system_B(english_input, default_qid, default_subj, default_cat)
            if btn_all:
                res_a = orchestrator.execute_system_A(hindi_input, default_qid, default_subj, default_cat)

        st.markdown("---")
        st.markdown("### ⚖️ Live Execution Results & Side-by-Side Comparison")

        # System C vs System D Comparison
        if res_c and res_d:
            col_rc, col_rd = st.columns(2)
            with col_rc:
                st.info("### 🌐 System C: Translation-Mediated RAG")
                st.markdown("**1. Machine Translation (Hindi → English):**")
                st.code(res_c.get("translated_question", ""), language="text")
                st.caption(f"⏱️ Translation Latency: `{res_c['latencies']['translation_latency_ms']:.2f} ms`")

                st.markdown("**2. Top-5 Retrieved English Chunks:**")
                for r, (ch, sc) in enumerate(zip(res_c.get("retrieved_chunks", []), res_c.get("retrieval_scores", [])), 1):
                    is_gold = (gold_chunk in ch) if gold_chunk != "N/A" else False
                    badge = "🎯 <span class='gold-badge'>GOLD TARGET</span>" if is_gold else ""
                    st.markdown(f"- **Rank {r}:** `{ch}` (Score: `{sc:.4f}`) {badge}", unsafe_allow_html=True)
                st.caption(f"⏱️ Retrieval Latency: `{res_c['latencies']['retrieval_latency_ms']:.2f} ms`")

                st.markdown("**3. Generated Hindi Answer:**")
                st.success(res_c.get("generated_answer", ""))
                st.caption(f"⏱️ Gen Latency: `{res_c['latencies']['generation_latency_ms']:.2f} ms` | Total: `{res_c['latencies']['total_latency_ms']:.2f} ms`")

            with col_rd:
                st.info("### 🔀 System D: Direct Multilingual RAG")
                st.markdown("**1. Direct Cross-Lingual Search:**")
                st.caption("✨ Zero translation required! Pure Hindi query embedded into multilingual vector space.")

                st.markdown("**2. Top-5 Retrieved English Chunks:**")
                for r, (ch, sc) in enumerate(zip(res_d.get("retrieved_chunks", []), res_d.get("retrieval_scores", [])), 1):
                    is_gold = (gold_chunk in ch) if gold_chunk != "N/A" else False
                    badge = "🎯 <span class='gold-badge'>GOLD TARGET</span>" if is_gold else ""
                    st.markdown(f"- **Rank {r}:** `{ch}` (Score: `{sc:.4f}`) {badge}", unsafe_allow_html=True)
                st.caption(f"⏱️ Retrieval Latency: `{res_d['latencies']['retrieval_latency_ms']:.2f} ms`")

                st.markdown("**3. Generated Hindi Answer:**")
                st.success(res_d.get("generated_answer", ""))
                st.caption(f"⏱️ Gen Latency: `{res_d['latencies']['generation_latency_ms']:.2f} ms` | Total: `{res_d['latencies']['total_latency_ms']:.2f} ms`")

            # Comparative Latency Table
            st.markdown("#### ⏱️ Real-Time Component Latency Breakdown")
            c_lat = res_c["latencies"]
            d_lat = res_d["latencies"]
            df_lat = pd.DataFrame([
                {"System": "System C (Translation RAG)", "Translation (ms)": f"{c_lat['translation_latency_ms']:.2f}", "Retrieval (ms)": f"{c_lat['retrieval_latency_ms']:.2f}", "Generation (ms)": f"{c_lat['generation_latency_ms']:.2f}", "Total Latency (ms)": f"{c_lat['total_latency_ms']:.2f}"},
                {"System": "System D (Multilingual RAG)", "Translation (ms)": "0.00", "Retrieval (ms)": f"{d_lat['retrieval_latency_ms']:.2f}", "Generation (ms)": f"{d_lat['generation_latency_ms']:.2f}", "Total Latency (ms)": f"{d_lat['total_latency_ms']:.2f}"}
            ])
            st.dataframe(df_lat, use_container_width=True)

        if res_b or res_a:
            st.markdown("#### 📊 Baselines: Monolingual Upper Bound (B) & Direct LLM (A)")
            col_b1, col_b2 = st.columns(2)
            if res_b:
                with col_b1:
                    st.markdown("**📖 System B (Monolingual English RAG):**")
                    st.write(res_b.get("generated_answer", ""))
                    st.caption(f"Total Latency: `{res_b['latencies']['total_latency_ms']:.2f} ms` | Retrieval: `{res_b['latencies']['retrieval_latency_ms']:.2f} ms`")
            if res_a:
                with col_b2:
                    st.markdown("**🤖 System A (Direct LLM Baseline - No Retrieval):**")
                    st.write(res_a.get("generated_answer", ""))
                    st.caption(f"Total Latency: `{res_a['latencies']['total_latency_ms']:.2f} ms`")


# ==============================================================================
# TAB 2: CHUNKS & CORPUS EXPLORER
# ==============================================================================
with tabs[1]:
    st.subheader("📚 Textbook Chunks & Corpus Explorer")
    st.markdown("Inspect every page-aware chunk in the knowledge base, review physical page boundaries, and verify token lengths.")

    manifest_file = Path(cfg["paths"]["processed_dir"]) / "chunks_manifest.json"
    if not manifest_file.exists():
        st.warning(f"Manifest not found at {manifest_file}. Go to Tab 3 to ingest your corpus.")
    else:
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest_chunks = json.load(f)

        df_chunks = pd.DataFrame(manifest_chunks)

        # Overview Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Chunks", len(df_chunks))
        m2.metric("Total Documents", df_chunks["doc_id"].nunique() if "doc_id" in df_chunks else 0)
        m3.metric("Total Subjects", df_chunks["subject"].nunique() if "subject" in df_chunks else 0)
        m4.metric("Avg Chunk Tokens", f"{df_chunks['token_count'].mean():.1f}" if "token_count" in df_chunks else "N/A")

        # Filters
        c_f1, c_f2 = st.columns([1, 2])
        with c_f1:
            subj_filter = st.selectbox("Filter by Subject:", ["All Subjects"] + sorted(df_chunks["subject"].unique().tolist()))
        with c_f2:
            search_query = st.text_input("🔍 Search Chunk Text or ID:", "")

        filtered_df = df_chunks
        if subj_filter != "All Subjects":
            filtered_df = filtered_df[filtered_df["subject"] == subj_filter]
        if search_query.strip():
            filtered_df = filtered_df[
                filtered_df["text"].str.contains(search_query, case=False, na=False) |
                filtered_df["chunk_id"].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"Showing **{len(filtered_df)}** of **{len(df_chunks)}** chunks:")
        
        # Table View
        cols_to_show = ["chunk_id", "subject", "page", "chunk_index", "token_count"]
        st.dataframe(filtered_df[[c for c in cols_to_show if c in filtered_df.columns]], use_container_width=True)

        # In-depth Chunk Reader
        st.markdown("#### 📖 Inspect Chunk Content")
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📄 {row['chunk_id']} | Subject: {row.get('subject')} | Page {row.get('page')} ({row.get('token_count')} tokens)"):
                st.markdown(f"**Document ID:** `{row.get('doc_id')}`")
                st.text_area("Passage Text:", value=row.get("text", ""), height=150, key=f"chunk_txt_{idx}")


# ==============================================================================
# TAB 3: PDF INGESTION STUDIO
# ==============================================================================
with tabs[2]:
    st.subheader("📥 PDF Ingestion Studio")
    st.markdown("Upload any academic PDF textbook or research paper, extract text page-by-page, and build dual FAISS indexes live.")

    col_up, col_info = st.columns([2, 1])
    with col_up:
        uploaded_pdf = st.file_uploader("Select or Drag & Drop an Academic PDF:", type=["pdf"])
        custom_subject = st.text_input("Subject Category Name:", value="computer_science")
        btn_ingest = st.button("🚀 Ingest PDF & Build Dual Vector Indexes", type="primary", disabled=(uploaded_pdf is None))

    with col_info:
        st.info(
            "**What this does:**\n"
            "1. Saves PDF into `data/corpus/<subject>/`\n"
            "2. Extracts text page-by-page with `pypdf`\n"
            "3. Creates page-bounded chunks\n"
            "4. Builds 768d English + 384d Multilingual FAISS stores\n"
            "5. Live-streams console output below!"
        )

    if btn_ingest and uploaded_pdf is not None:
        corpus_dir = Path(cfg["paths"]["corpus_dir"])
        target_sub_dir = corpus_dir / custom_subject.lower().replace(" ", "_")
        ensure_directory(str(target_sub_dir))
        save_dest = target_sub_dir / uploaded_pdf.name

        with open(save_dest, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        st.success(f"Saved uploaded PDF to: `{save_dest}`")

        # Live terminal stream
        st.markdown("#### 📺 Live Ingestion Console Output:")
        console_placeholder = st.empty()
        log_lines = []

        cmd = [sys.executable, str(script_dir / "ingest_new_pdf.py")]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace"
        )

        for line in proc.stdout:
            log_lines.append(line)
            console_placeholder.code("".join(log_lines[-25:]), language="bash")

        proc.wait()
        if proc.returncode == 0:
            st.success("🎉 Ingestion & Dual FAISS indexing complete! Clear cache & reload to query immediately.")
            st.cache_resource.clear()
        else:
            st.error(f"Ingestion process exited with code {proc.returncode}")


# ==============================================================================
# TAB 4: MASTER BENCHMARK & TEST RUNNER
# ==============================================================================
with tabs[3]:
    st.subheader("⚡ Master Benchmark & Test Runner")
    st.markdown("Execute automated test suites and the full 68-run scientific benchmark directly from the frontend with **live streaming console output**.")

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown("#### 🧪 Automated Verification Suite")
        st.caption("Runs all 7 pytest integration tests (page chunking, vector index, translation, generation).")
        btn_run_tests = st.button("▶️ Run 7-Point Pytest Suite", use_container_width=True)

    with r_col2:
        st.markdown("#### 🔬 Complete 68-Run Benchmark")
        st.caption("Runs 17 questions × 4 systems (68 runs), clears old logs, and updates all reports.")
        btn_run_bench = st.button("🚀 Run Full 68-Run Benchmark Suite", type="primary", use_container_width=True)

    if btn_run_tests or btn_run_bench:
        script_to_run = (
            [sys.executable, "-m", "pytest", str(script_dir / "tests" / "test_basic_pipeline.py"), "-v"]
            if btn_run_tests else
            [sys.executable, str(script_dir / "run_complete_experiment.py")]
        )

        st.markdown("#### 📺 Live Console Output (Streaming in Real Time):")
        live_console = st.empty()
        streamed_logs = []

        start_time = time.perf_counter()
        proc = subprocess.Popen(
            script_to_run,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace"
        )

        for line in proc.stdout:
            streamed_logs.append(line)
            # Display last 35 lines
            live_console.code("".join(streamed_logs[-35:]), language="bash")

        proc.wait()
        duration = round(time.perf_counter() - start_time, 2)

        if proc.returncode == 0:
            st.success(f"✅ Execution finished successfully in {duration} seconds!")
            st.cache_resource.clear()
        else:
            st.error(f"❌ Execution failed with exit code {proc.returncode}")


# ==============================================================================
# TAB 5: OBSERVABILITY & WATERFALL TRACES
# ==============================================================================
with tabs[4]:
    st.subheader("🌊 Observability & Waterfall Span Explorer")
    st.markdown("Inspect granular hierarchical waterfall execution spans, sub-millisecond latencies, and token metrics.")

    traces = tracer.load_all_traces()
    if not traces:
        st.info("No trace files recorded yet. Run a query in Tab 1 or execute the benchmark in Tab 4.")
    else:
        st.caption(f"Total Traces Recorded on Disk: **{len(traces)}**")

        trace_options = [
            f"[{t.get('system_id', '?')}] {t.get('question_id', 'Q')} | {t.get('query', '')[:45]}... ({t.get('total_latency_ms', 0):.1f} ms) | Trace: {t.get('trace_id')[:8]}"
            for t in traces
        ]
        sel_idx = st.selectbox("Select Trace Record to Inspect:", range(len(trace_options)), format_func=lambda i: trace_options[i])
        active_trace = traces[sel_idx]

        # Metric Badges
        c_t1, c_t2, c_t3, c_t4 = st.columns(4)
        c_t1.metric("System ID", active_trace.get("system_id", "N/A"))
        c_t2.metric("Total Latency", f"{active_trace.get('total_latency_ms', 0):.2f} ms")
        c_t3.metric("Spans Captured", len(active_trace.get("spans", [])))
        c_t4.metric("Status", active_trace.get("status", "SUCCESS"))

        # Spans Table
        spans_list = active_trace.get("spans", [])
        if spans_list:
            st.markdown("#### ⏱️ Span Waterfall Execution Profile")
            span_records = []
            for s in spans_list:
                span_records.append({
                    "Span Name": s.get("name"),
                    "Type": s.get("span_type"),
                    "Duration (ms)": f"{s.get('latency_ms', 0):.2f}",
                    "Status": s.get("status", "SUCCESS")
                })
            st.dataframe(pd.DataFrame(span_records), use_container_width=True)

            st.markdown("#### 🔍 Granular Span Inspector (Inputs / Outputs)")
            for s in spans_list:
                with st.expander(f"🔹 {s.get('name')} ({s.get('latency_ms', 0):.2f} ms) - Type: `{s.get('span_type')}`"):
                    col_in, col_out = st.columns(2)
                    with col_in:
                        st.markdown("**Inputs:**")
                        st.json(s.get("inputs", {}))
                    with col_out:
                        st.markdown("**Outputs:**")
                        st.json(s.get("outputs", {}))

        with st.expander("📄 View Complete OpenTelemetry / LangSmith Trace JSON"):
            st.json(active_trace)


# ==============================================================================
# TAB 6: BENCHMARK ANALYTICS & REPORT
# ==============================================================================
with tabs[5]:
    st.subheader("📈 Scientific Benchmark & Error Taxonomy Analytics")

    csv_path = Path(cfg["paths"]["results_csv_dir"]) / "benchmark_results.csv"
    report_path = Path(cfg["paths"]["results_summary_dir"]) / "evaluation_report.md"

    if csv_path.exists():
        df_res = pd.read_csv(csv_path)

        # Top Summary KPIs
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Executions", len(df_res))
        k2.metric("Sys B MRR (English)", f"{df_res[df_res['system_id']=='B']['mrr'].mean():.3f}")
        k3.metric("Sys C MRR (Translation)", f"{df_res[df_res['system_id']=='C']['mrr'].mean():.3f}")
        k4.metric("Sys D MRR (Multilingual)", f"{df_res[df_res['system_id']=='D']['mrr'].mean():.3f}")
        k5.metric("Sys D Avg Latency", f"{df_res[df_res['system_id']=='D']['total_latency_ms'].mean():.1f} ms")

        st.markdown("---")
        st.markdown("#### 📊 Consolidated Benchmark Data Table")
        st.dataframe(df_res, use_container_width=True)

        st.markdown("#### ⚖️ Per-System Aggregated Metrics")
        agg_table = df_res.groupby("system_id").agg({
            "recall@1": "mean",
            "recall@3": "mean",
            "recall@5": "mean",
            "mrr": "mean",
            "ndcg@5": "mean",
            "translation_latency_ms": "mean",
            "retrieval_latency_ms": "mean",
            "generation_latency_ms": "mean",
            "total_latency_ms": "mean"
        }).reset_index()
        st.dataframe(agg_table.style.format({
            "recall@1": "{:.3f}",
            "recall@3": "{:.3f}",
            "recall@5": "{:.3f}",
            "mrr": "{:.3f}",
            "ndcg@5": "{:.3f}",
            "translation_latency_ms": "{:.2f}",
            "retrieval_latency_ms": "{:.2f}",
            "generation_latency_ms": "{:.2f}",
            "total_latency_ms": "{:.2f}"
        }), use_container_width=True)

        if report_path.exists():
            st.markdown("---")
            st.markdown("#### 📑 Official Rendered Evaluation Report")
            with open(report_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())
    else:
        st.info("No benchmark results found yet. Run the benchmark in Tab 4 to generate data.")
