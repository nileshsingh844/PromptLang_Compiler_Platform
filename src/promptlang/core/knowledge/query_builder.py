"""Build retrieval queries from IR for smarter RAG."""

from __future__ import annotations

from typing import Any, Dict, List


_ARCH_KEYWORDS = [
    "microservices",
    "monolith",
    "event-driven",
    "event driven",
    "cqrs",
    "saga",
    "c4",
    "mvc",
    "hexagonal",
    "clean architecture",
    "ddd",
    "domain-driven",
    "api gateway",
    "service discovery",
    "circuit breaker",
    "bulkhead",
]

_TECH_STACK_KEYWORDS = [
    "docker",
    "kubernetes",
    "k8s",
    "helm",
    "terraform",
    "redis",
    "postgres",
    "postgresql",
    "mongodb",
    "kafka",
    "rabbitmq",
    "prometheus",
    "grafana",
    "opentelemetry",
    "otel",
    "ci/cd",
    "github actions",
    "gitlab ci",
    "jenkins",
    "argo cd",
    "security",
    "owasp",
    "observability",
    "monitoring",
    "logging",
    "tracing",
    "mlflow",
    "mlops",
]


def _normalize_text(s: str) -> str:
    return " ".join((s or "").strip().split()).lower()


def _extract_keywords(text: str, candidates: List[str]) -> List[str]:
    t = _normalize_text(text)
    hits: List[str] = []
    for c in candidates:
        if c in t:
            hits.append(c)
    return hits


def build_retrieval_query(ir: Dict[str, Any]) -> str:
    """Build a high-quality retrieval query from the IR.

    The goal is to focus retrieval on engineering best practices relevant to the request.
    """
    meta = ir.get("meta", {})
    intent = meta.get("intent") or meta.get("type") or ""

    task = ir.get("task", {})
    task_desc = task.get("description", "")

    constraints = ir.get("constraints", {})
    must_have = constraints.get("must_have", []) or []

    context = ir.get("context", {})
    stack = context.get("stack", {}) or {}

    stack_str = " ".join(
        [
            str(stack.get("language", "")),
            str(stack.get("framework", "")),
            str(stack.get("architecture", "")),
        ]
    )

    output_contract = ir.get("output_contract", {})
    output_format = output_contract.get("file_block_format") or output_contract.get("format") or ""

    combined = " ".join(
        [
            str(intent),
            str(task_desc),
            " ".join([str(x) for x in must_have if x]),
            stack_str,
            str(output_format),
        ]
    )

    arch_hits = _extract_keywords(combined, _ARCH_KEYWORDS)
    tech_hits = _extract_keywords(combined, _TECH_STACK_KEYWORDS)

    # Keep query deterministic but information-dense.
    parts: List[str] = []
    if intent:
        parts.append(f"Generate industry standard {intent} docs")
    else:
        parts.append("Generate industry standard engineering docs")

    if arch_hits:
        parts.append("Architecture: " + ", ".join(sorted(set(arch_hits))))

    if tech_hits:
        parts.append("Tech stack: " + ", ".join(sorted(set(tech_hits))))

    # Always encourage quality sections.
    parts.append("Include security, testing, deployment, CI/CD, and observability best practices")

    # Add a short hint of the task topic (trimmed).
    if task_desc:
        trimmed = " ".join(task_desc.split()[:30])
        parts.append(f"Project request: {trimmed}")

    query = ". ".join(parts).strip()
    return query[:500]
