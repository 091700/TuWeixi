"""OpenTelemetry Tracing — Agent Observability (P2)

面试话术: "我们使用 OpenTelemetry 对整个 Agent 调用链路进行分布式追踪，
每个 LLM 调用、工具执行、RAG 检索都有独立的 Span，
可以在 Jaeger/Grafana 中可视化整个 Agent 的决策过程。"
"""

import time
import logging
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger("db_agent.telemetry")

# ── 尝试导入 OpenTelemetry ──────────────────────────
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource

    resource = Resource(attributes={SERVICE_NAME: "db-agent"})
    provider = TracerProvider(resource=resource)

    # 尝试连接 OTLP Collector（如果存在）
    try:
        exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    except Exception:
        # OTLP Collector 不可用时静默降级
        pass

    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("db_agent")
    _otel_available = True
    logger.info("[Telemetry] OpenTelemetry 已启用")
except ImportError:
    _otel_available = False
    tracer = None
    logger.debug("[Telemetry] OpenTelemetry 未安装（tracing 功能跳过）")


# ── 轻量级 Span 包装器 ───────────────────────────────

class TelemetrySpan:
    """Span 包装器 — OpenTelemetry 可用时记录，不可用时静默跳过"""

    def __init__(self, name: str, attributes: dict = None):
        self.name = name
        self._start = time.time()
        self._attrs = attributes or {}
        if tracer:
            self._span = tracer.start_as_current_span(name)
            if self._attrs:
                for k, v in self._attrs.items():
                    self._span.set_attribute(k, v)
        else:
            self._span = None

    def set_attr(self, key: str, value):
        self._attrs[key] = value
        if self._span:
            self._span.set_attribute(key, str(value)[:200])

    def finish(self, success: bool = True):
        elapsed_ms = (time.time() - self._start) * 1000
        if self._span:
            self._span.set_attribute("success", success)
            self._span.set_attribute("duration_ms", round(elapsed_ms, 2))
        logger.debug(f"[Telemetry] {self.name}: {elapsed_ms:.1f}ms (ok={success})")


def trace_llm_call(model: str, messages_count: int):
    """创建 LLM 调用的 Telemetry Span"""
    return TelemetrySpan(f"llm.{model}", {"messages": messages_count, "model": model})


def trace_tool_call(tool_name: str, session_id: str = ""):
    """创建工具调用的 Telemetry Span"""
    return TelemetrySpan(f"tool.{tool_name}", {"tool": tool_name, "session_id": session_id[:8]})


def trace_rag_retrieval(query_len: int):
    """创建 RAG 检索的 Telemetry Span"""
    return TelemetrySpan("rag.retrieve", {"query_length": query_len})