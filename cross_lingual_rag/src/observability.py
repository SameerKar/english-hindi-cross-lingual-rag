"""
Observability and Tracing Engine for Cross-Lingual Academic RAG.
Provides deep execution visibility equivalent to LangSmith:
1. 100% Free Local Trace Store (hierarchical waterfall spans, latency, token usage, inputs/outputs).
2. LangSmith Cloud Integration (automatically exports to LangSmith if LANGSMITH_API_KEY is configured).
"""

import os
import sys
import time
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from .utils import ensure_directory, get_project_root

@dataclass
class Span:
    span_id: str
    trace_id: str
    name: str
    span_type: str  # "chain", "translation", "embedding", "retrieval", "llm", "evaluation"
    start_time: str
    end_time: str
    latency_ms: float
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metadata: Dict[str, Any]
    status: str = "SUCCESS"  # "SUCCESS" or "ERROR"
    error: Optional[str] = None
    parent_span_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Trace:
    trace_id: str
    run_id: str
    question_id: str
    system_id: str
    query: str
    start_time: str
    end_time: str
    total_latency_ms: float
    spans: List[Span] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "SUCCESS"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["spans"] = [s.to_dict() if isinstance(s, Span) else s for s in self.spans]
        return d


class ObservabilityTracer:
    """
    Hierarchical tracer that captures multi-step execution graphs and exports to
    either local disk (100% free) or LangSmith (if API key is present).
    """
    def __init__(self, traces_dir: Optional[str] = None):
        root = get_project_root()
        if traces_dir:
            self.traces_dir = Path(traces_dir)
        else:
            self.traces_dir = root / "results" / "traces"
        ensure_directory(str(self.traces_dir))

        self.current_trace: Optional[Trace] = None
        self.active_spans: List[Span] = []

        # Check LangSmith Availability
        self.langsmith_enabled = False
        self.langsmith_client = None
        self._init_langsmith()

    def _init_langsmith(self):
        """
        Initializes LangSmith client if LANGSMITH_API_KEY is available.
        LangSmith offers a generous free developer tier (5,000 free traces/mo).
        """
        api_key = os.getenv("LANGSMITH_API_KEY")
        if api_key:
            try:
                from langsmith import Client
                project_name = os.getenv("LANGSMITH_PROJECT", "cross-lingual-academic-rag")
                self.langsmith_client = Client(api_key=api_key)
                self.langsmith_project = project_name
                self.langsmith_enabled = True
                print(f"[Observability] LangSmith Cloud Tracing ENABLED for project: {project_name}")
            except Exception as e:
                print(f"[Observability] LangSmith init failed: {e}. Using Local Free Tracing.")
                self.langsmith_enabled = False
        else:
            # 100% Free Local Mode
            self.langsmith_enabled = False

    def start_trace(self, question_id: str, system_id: str, query: str, metadata: Optional[Dict[str, Any]] = None) -> Trace:
        """
        Begins a new root trace for a query execution.
        """
        trace_id = str(uuid.uuid4())
        now_str = datetime.now(timezone.utc).isoformat()
        self.current_trace = Trace(
            trace_id=trace_id,
            run_id=trace_id,
            question_id=question_id,
            system_id=system_id,
            query=query,
            start_time=now_str,
            end_time=now_str,
            total_latency_ms=0.0,
            metadata=metadata or {},
            spans=[]
        )
        self.active_spans = []
        return self.current_trace

    def start_span(self, name: str, span_type: str, inputs: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Span:
        """
        Starts a timed child span.
        """
        if self.current_trace is None:
            self.start_trace("UNKNOWN", "UNKNOWN", "UNKNOWN")

        span_id = str(uuid.uuid4())
        parent_id = self.active_spans[-1].span_id if self.active_spans else None
        now_str = datetime.now(timezone.utc).isoformat()

        span = Span(
            span_id=span_id,
            trace_id=self.current_trace.trace_id,
            name=name,
            span_type=span_type,
            start_time=now_str,
            end_time=now_str,
            latency_ms=0.0,
            inputs=inputs,
            outputs={},
            metadata=metadata or {},
            status="SUCCESS",
            parent_span_id=parent_id
        )
        span._perf_start = time.perf_counter()
        self.active_spans.append(span)
        return span

    def end_span(self, span: Span, outputs: Dict[str, Any], error: Optional[str] = None):
        """
        Completes a timed child span and appends it to the trace.
        """
        latency_ms = (time.perf_counter() - getattr(span, "_perf_start", time.perf_counter())) * 1000.0
        span.end_time = datetime.now(timezone.utc).isoformat()
        span.latency_ms = round(latency_ms, 2)
        span.outputs = outputs
        if error:
            span.status = "ERROR"
            span.error = error

        if self.current_trace:
            self.current_trace.spans.append(span)

        if self.active_spans and self.active_spans[-1].span_id == span.span_id:
            self.active_spans.pop()

    def end_trace(self, final_output: str, error: Optional[str] = None) -> Trace:
        """
        Concludes the root trace, calculates overall latency, and persists to local disk & LangSmith.
        """
        if self.current_trace is None:
            return None

        self.current_trace.end_time = datetime.now(timezone.utc).isoformat()
        if error:
            self.current_trace.status = "ERROR"
            self.current_trace.error = error

        # Calculate total latency as sum of root components or span durations
        total_lat = sum(s.latency_ms for s in self.current_trace.spans if s.parent_span_id is None)
        if total_lat == 0 and self.current_trace.spans:
            total_lat = sum(s.latency_ms for s in self.current_trace.spans)
        self.current_trace.total_latency_ms = round(total_lat, 2)
        self.current_trace.metadata["final_output"] = final_output

        # 1. Persist to Local Free Trace Store
        self._save_local_trace(self.current_trace)

        # 2. Export to LangSmith Cloud if configured
        if self.langsmith_enabled:
            self._export_to_langsmith(self.current_trace)

        saved = self.current_trace
        self.current_trace = None
        self.active_spans = []
        return saved

    def _save_local_trace(self, trace: Trace):
        """
        Saves trace to results/traces/{trace_id}.json.
        """
        trace_file = self.traces_dir / f"{trace.trace_id}.json"
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump(trace.to_dict(), f, indent=2, ensure_ascii=False)

    def _export_to_langsmith(self, trace: Trace):
        """
        Exports trace run tree to LangSmith API.
        """
        try:
            from langsmith.run_trees import RunTree
            # Root Run
            root_run = RunTree(
                name=f"System_{trace.system_id}_Execution",
                run_type="chain",
                inputs={"query": trace.query, "question_id": trace.question_id},
                outputs={"final_output": trace.metadata.get("final_output", "")},
                extra={"metadata": trace.metadata},
                project_name=self.langsmith_project,
                client=self.langsmith_client
            )
            # Add child spans
            for span in trace.spans:
                child = root_run.create_child(
                    name=span.name,
                    run_type=span.span_type if span.span_type in ["llm", "retriever", "tool", "chain"] else "tool",
                    inputs=span.inputs,
                    outputs=span.outputs,
                    extra={"metadata": span.metadata}
                )
                child.end(outputs=span.outputs, error=span.error)
            root_run.end(outputs={"final_output": trace.metadata.get("final_output", "")})
            root_run.post()
        except Exception as e:
            print(f"[Observability] Warning: Failed to export trace to LangSmith: {e}")

    def load_all_traces(self) -> List[Dict[str, Any]]:
        """
        Loads all stored local traces for the Observability Dashboard.
        """
        traces = []
        trace_files = sorted(self.traces_dir.glob("*.json"), key=os.path.getmtime, reverse=True)
        for tf in trace_files:
            try:
                with open(tf, "r", encoding="utf-8") as f:
                    traces.append(json.load(f))
            except Exception:
                pass
        return traces
