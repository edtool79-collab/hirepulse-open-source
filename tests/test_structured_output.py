"""Exercise output contracts and Actor-reported run outcomes without network calls."""
import asyncio
import json
from types import SimpleNamespace

import pytest
from apify_client._models import Run
from jsonschema import Draft202012Validator

import hirepulse_tools as hp
from hirepulse_tools._catalog import TOOL_SLUGS
from hirepulse_tools._run_context import RunContext, collect_run_context
from hirepulse_tools._runner import _capture_run_summary
from hirepulse_tools.mcp_server import MAX_OUTPUT_BYTES, bounded_output, mcp
from test_tools import required_input


def configure_summary(mock_apify, outcome, rows=None, total=0):
    mock_apify[2].call.return_value = Run.model_construct(
        id="audit-existing-run", status="SUCCEEDED", default_dataset_id="mock-dataset",
        default_key_value_store_id="mock-store")
    mock_apify[3].list_items.return_value.items = [] if rows is None else rows
    mock_apify[3].list_items.return_value.total = total
    mock_apify[1].key_value_store.return_value.get_record.return_value = SimpleNamespace(
        value={"outcome": outcome, "private_provider_details": "never-return-this-value"})


@pytest.mark.parametrize("name,slug", TOOL_SLUGS.items())
def test_all_eight_tools_advertise_output_contract_and_return_both_formats(name, slug, mock_apify):
    tool = next(t for t in asyncio.run(mcp.list_tools()) if t.name == name)
    assert tool.title and tool.outputSchema["type"] == "object"
    validator = Draft202012Validator(tool.outputSchema)
    validator.check_schema(tool.outputSchema)
    result = asyncio.run(mcp.call_tool(name, required_input(slug)))
    assert not result.isError
    assert result.structuredContent == json.loads(result.content[0].text)
    validator.validate(result.structuredContent)
    error = asyncio.run(mcp.call_tool(name, {}))
    assert error.isError
    validator.validate(error.structuredContent)
    assert "result" not in result.structuredContent  # Preserve the existing top-level items contract.


@pytest.mark.parametrize("outcome,reason", [
    ("NO_DATA", "no_data"),
    ("SPENDING_LIMIT_TOO_LOW", "spending_limit"),
    ("PARTIAL_SPENDING_LIMIT", "spending_limit"),
    ("FREE_PLAN_LIMITED", "free_plan_limit"),
    ("FREE_PLAN_PREVIEW", "free_plan_limit"),
    ("SERVICE_UNAVAILABLE", "service_unavailable"),
    ("PARTIAL_SERVICE_UNAVAILABLE", "service_unavailable"),
    ("PROVIDER_ERROR", "provider_error"),
    ("PARTIAL_PROVIDER_ERROR", "provider_error"),
    ("COMPLETE", "unknown"),
])
def test_empty_result_uses_only_reported_reason(outcome, reason, mock_apify):
    configure_summary(mock_apify, outcome)
    result = asyncio.run(mcp.call_tool("company_intent", {"domains": ["stripe.com"]}))
    assert result.structuredContent["empty_result_reason"] == reason
    assert result.structuredContent["run_outcome"] == outcome
    assert result.structuredContent["run_id"] == "audit-existing-run"
    assert "never-return-this-value" not in result.model_dump_json()
    mock_apify[2].call.assert_called_once()
    mock_apify[1].key_value_store.return_value.get_record.assert_called_once_with("OUTPUT")


@pytest.mark.parametrize("stage,status", [
    ("no-store", "missing_store"), ("not-found", "not_found"),
    ("exception", "unavailable"), ("unrecognized", "unrecognized"),
])
def test_missing_or_unreadable_summaries_preserve_rows_and_do_not_rerun(stage, status, mock_apify):
    configure_summary(mock_apify, "COMPLETE", [{"fixture": "existing result"}], total=1)
    record = mock_apify[1].key_value_store.return_value.get_record
    if stage == "no-store":
        mock_apify[2].call.return_value.default_key_value_store_id = None
    elif stage == "not-found":
        record.return_value = None
    elif stage == "exception":
        record.side_effect = RuntimeError("private-upstream-detail")
    else:
        record.return_value = SimpleNamespace(value={"outcome": "private-upstream-detail"})
    result = asyncio.run(mcp.call_tool("company_intent", {"domains": ["stripe.com"]}))
    assert not result.isError
    assert result.structuredContent["items"] == [{"fixture": "existing result"}]
    assert result.structuredContent["summary_status"] == status
    assert result.structuredContent["run_outcome"] == "UNKNOWN"
    assert result.structuredContent["data_completeness"] == "unknown"
    assert "private-upstream-detail" not in result.model_dump_json()
    mock_apify[2].call.assert_called_once()


def test_python_list_api_does_not_add_summary_requests(mock_apify):
    configure_summary(mock_apify, "NO_DATA")
    assert type(hp.company_intent(["stripe.com"])) is list
    mock_apify[1].key_value_store.assert_not_called()


def test_empty_unknown_is_not_presented_as_no_data(mock_apify):
    mock_apify[3].list_items.return_value.items = []
    result = asyncio.run(mcp.call_tool("company_intent", {"domains": ["stripe.com"]}))
    assert result.structuredContent["run_outcome"] == "UNKNOWN"
    assert result.structuredContent["empty_result_reason"] == "unknown"
    assert result.structuredContent["data_completeness"] == "unknown"


def test_summary_complete_is_checked_against_counts_and_result_limit(mock_apify):
    configure_summary(mock_apify, "COMPLETE", [{"fixture": "row"}], total=1)
    complete = asyncio.run(mcp.call_tool("company_intent", {"domains": ["stripe.com"]}))
    assert complete.structuredContent["data_completeness"] == "complete"
    mock_apify[3].list_items.return_value.total = 5
    partial = asyncio.run(mcp.call_tool("company_intent", {"domains": ["stripe.com"]}))
    assert partial.structuredContent["data_completeness"] == "partial"
    mock_apify[3].list_items.return_value.total = 1
    capped = asyncio.run(mcp.call_tool("company_intent", {"domains": ["stripe.com"], "result_limit": 1}))
    assert capped.structuredContent["data_completeness"] == "unknown"


def test_locally_omitted_record_is_not_reported_as_empty_no_data():
    context = RunContext(outcome="NO_DATA", dataset_total=1, summary_status="available")
    encoded = bounded_output([{"fixture": "א" * MAX_OUTPUT_BYTES}], 2, context)
    assert len(encoded.encode("utf-8")) <= MAX_OUTPUT_BYTES
    result = json.loads(encoded)
    assert result["omitted_items"] == 1 and result["output_truncated"]
    assert result["empty_result_reason"] == "unknown"
    assert result["data_completeness"] == "partial"


def test_run_context_is_isolated_across_concurrent_mcp_threads():
    async def one(run_id):
        def work():
            with collect_run_context() as context:
                _capture_run_summary(SimpleNamespace(), SimpleNamespace(id=run_id), "dataset", SimpleNamespace(total=0))
                return context.run_id
        return await asyncio.to_thread(work)
    async def both():
        return await asyncio.gather(one("first-run"), one("second-run"))
    assert asyncio.run(both()) == ["first-run", "second-run"]
