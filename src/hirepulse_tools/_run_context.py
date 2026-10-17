"""Opt-in run metadata for MCP; ordinary Python calls still return plain lists."""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator, Literal

RunOutcome = Literal[
    "COMPLETE", "NO_DATA", "FREE_PLAN_LIMITED", "FREE_PLAN_PREVIEW",
    "PARTIAL_SPENDING_LIMIT", "SPENDING_LIMIT_TOO_LOW", "PARTIAL_PROVIDER_ERROR",
    "PROVIDER_ERROR", "SERVICE_UNAVAILABLE", "PARTIAL_SERVICE_UNAVAILABLE", "PARTIAL", "UNKNOWN",
]
KNOWN_OUTCOMES = {
    "COMPLETE", "NO_DATA", "FREE_PLAN_LIMITED", "FREE_PLAN_PREVIEW",
    "PARTIAL_SPENDING_LIMIT", "SPENDING_LIMIT_TOO_LOW", "PARTIAL_PROVIDER_ERROR",
    "PROVIDER_ERROR", "SERVICE_UNAVAILABLE", "PARTIAL_SERVICE_UNAVAILABLE", "PARTIAL",
}
SummaryStatus = Literal["available", "missing_store", "not_found", "unavailable", "unrecognized", "not_requested"]


@dataclass
class RunContext:
    run_id: str | None = None
    dataset_id: str | None = None
    dataset_total: int | None = None
    outcome: RunOutcome = "UNKNOWN"
    summary_status: SummaryStatus = "not_requested"


active_context: ContextVar[RunContext | None] = ContextVar("hirepulse_run_context", default=None)


@contextmanager
def collect_run_context() -> Iterator[RunContext]:
    context = RunContext()
    token = active_context.set(context)
    try:
        yield context
    finally:
        active_context.reset(token)
