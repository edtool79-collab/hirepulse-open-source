"""Agent recovery guidance must survive validation, SDK failures and MCP."""

import asyncio
import json

import pytest
from apify_client._models import Run

import hirepulse_tools as hp
from hirepulse_tools._catalog import TOOL_SLUGS
from hirepulse_tools.mcp_server import mcp
from test_tools import required_input


@pytest.mark.parametrize("name,slug", TOOL_SLUGS.items())
def test_library_missing_token_has_machine_readable_action(name, slug, monkeypatch, mock_apify):
    monkeypatch.delenv("APIFY_TOKEN")
    with pytest.raises(hp.MissingTokenError) as caught:
        getattr(hp, name)(**required_input(slug))
    error = caught.value
    assert error.to_dict() == {"message": str(error), "suggested_agent_action": error.suggested_agent_action}
    assert "APIFY_TOKEN environment variable" in error.suggested_agent_action
    mock_apify[0].assert_not_called()


@pytest.mark.parametrize("kwargs", [
    {"domains": "private-invalid-value"},
    {"domains": [1]},
    {"domains": []},
    {"domains": ["stripe.com"], "result_limit": 0},
    {"domains": ["stripe.com"], "max_total_charge_usd": float("nan")},
])
def test_library_validation_is_actionable_and_valueerror_compatible(kwargs, mock_apify):
    with pytest.raises(hp.InvalidInputError) as caught:
        hp.company_intent(**kwargs)
    assert isinstance(caught.value, ValueError)
    assert caught.value.suggested_agent_action
    assert "private-invalid-value" not in json.dumps(caught.value.to_dict())
    mock_apify[0].assert_not_called()


@pytest.mark.parametrize("stage", ["construction", "call", "status", "dataset_id", "dataset"])
def test_run_failures_suggest_inspection_without_disclosing_upstream_text(stage, mock_apify):
    if stage == "status":
        mock_apify[2].call.return_value = Run.model_construct(status="FAILED")
    elif stage == "dataset_id":
        mock_apify[2].call.return_value = Run.model_construct(status="SUCCEEDED")
    else:
        target = {"construction": mock_apify[0], "call": mock_apify[2].call, "dataset": mock_apify[3].list_items}[stage]
        target.side_effect = RuntimeError("private-upstream-details")
    with pytest.raises(hp.ActorRunError) as caught:
        hp.company_intent(["stripe.com"])
    assert caught.value.suggested_agent_action
    assert "private-upstream-details" not in json.dumps(caught.value.to_dict())


@pytest.mark.parametrize("name,arguments", [
    ("company_intent", {}),
    ("company_intent", {"domains": "private-invalid-value"}),
    ("company_intent", {"domains": [1]}),
    ("company_intent", {"domains": []}),
    ("company_intent", {"domains": ["stripe.com"], "country": "private-invalid-value"}),
    ("company_intent", {"domains": ["stripe.com"], "result_limit": 0}),
    ("company_intent", {"domains": ["stripe.com"], "max_total_charge_usd": -1}),
    ("company_intent", {"domains": ["stripe.com"], "private-invalid-value": "private-invalid-value"}),
    ("private-invalid-value", {}),
])
def test_mcp_validation_errors_are_json_errors_without_input_values(name, arguments, mock_apify):
    result = asyncio.run(mcp.call_tool(name, arguments))
    assert result.isError
    envelope = json.loads(result.content[0].text)
    assert result.structuredContent == envelope
    assert envelope["error"]["message"]
    assert envelope["error"]["suggested_agent_action"]
    assert "private-invalid-value" not in result.model_dump_json()
    mock_apify[0].assert_not_called()


def test_mcp_sdk_failure_preserves_recovery_action_and_error_flag(mock_apify):
    mock_apify[2].call.side_effect = RuntimeError("private-upstream-details")
    result = asyncio.run(mcp.call_tool("company_intent", {"domains": ["stripe.com"]}))
    assert result.isError
    error = result.structuredContent["error"]
    assert "Could not run hirepulse/company-intent-radar" in error["message"]
    assert "before retrying" in error["suggested_agent_action"]
    assert "private-upstream-details" not in result.model_dump_json()
