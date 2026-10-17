"""The public MCP output contract, including safe errors and unknown outcomes."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._run_context import RunOutcome, SummaryStatus


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(description="Safe error message without caller values or upstream exception text.")
    suggested_agent_action: str = Field(description="Recovery action; inspect an existing run before starting another paid call.")


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    error: ErrorDetail


class SuccessEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[dict[str, Any]] = Field(description="Unmodified Actor dataset records; fields depend on the selected tool.")
    returned_items: int = Field(ge=0, description="Number of records in this response.")
    omitted_items: int = Field(ge=0, description="Fetched records omitted by the MCP byte budget only.")
    output_truncated: bool = Field(description="True when fetched records were omitted by the MCP byte budget.")
    result_limit_reached: bool = Field(description="The requested row limit was reached; additional data is possible, not proven.")
    note: str
    run_id: str | None = Field(default=None, description="Existing Apify run ID when available; inspect it before retrying.")
    dataset_id: str | None = Field(default=None, description="Existing dataset ID when available; retrieve results without rerunning.")
    dataset_total: int | None = Field(default=None, ge=0, description="Dataset total reported by Apify, or null when unknown.")
    run_outcome: RunOutcome = Field(description="Allowlisted outcome from the Actor's OUTPUT summary, or UNKNOWN.")
    summary_status: SummaryStatus = Field(description="Whether an Actor outcome summary was available and understood.")
    data_completeness: Literal["complete", "partial", "unknown"] = Field(description="Completeness supported by the summary and fetched counts; unknown is not success evidence.")
    empty_result_reason: Literal["no_data", "spending_limit", "free_plan_limit", "service_unavailable", "provider_error", "unknown"] | None = Field(description="Actor-reported reason for no returned rows; null when records are returned.")


class MCPEnvelope(RootModel[SuccessEnvelope | ErrorEnvelope]):
    # MCP requires an object output schema. Both union alternatives are objects.
    model_config = ConfigDict(json_schema_extra={"type": "object"})
