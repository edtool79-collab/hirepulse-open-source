import asyncio
import json

import pytest

from hirepulse_tools._catalog import TOOL_SLUGS
from hirepulse_tools.mcp_server import MAX_OUTPUT_BYTES, bounded_output, main, mcp
from test_tools import required_input, schema


def test_exactly_eight_tools_with_schema_defaults_and_descriptions(mock_apify):
    registered = asyncio.run(mcp.list_tools())
    assert {tool.name for tool in registered} == set(TOOL_SLUGS)
    assert len(registered) == 8
    for tool in registered:
        spec = schema(TOOL_SLUGS[tool.name])
        parameters = tool.inputSchema["properties"]
        assert set(parameters) == set(spec["properties"]) | {"result_limit", "max_total_charge_usd"}
        assert tool.inputSchema["required"] == spec["required"]
        for name, prop in spec["properties"].items():
            assert parameters[name]["description"] == prop.get("description", prop["title"])
            if "default" in prop:
                assert parameters[name]["default"] == prop["default"]
            if "enum" in prop:
                assert parameters[name]["enum"] == prop["enum"]
            value_schema = parameters[name].get("anyOf", [parameters[name]])[0]
            for constraint in ("minimum", "maximum", "minItems", "maxItems", "pattern"):
                if constraint in prop:
                    assert value_schema[constraint] == prop[constraint]
            if "uniqueItems" in prop:
                assert parameters[name]["uniqueItems"] == prop["uniqueItems"]
        assert tool.description.startswith("Returns ")
        assert "Use this when..." in tool.description
        assert "Do NOT use for..." in tool.description
        assert "Cost:" in tool.description
        assert "Actor-start event:" in tool.description
        assert "32,000" in tool.description
        assert tool.annotations.readOnlyHint is False
    mock_apify[0].assert_not_called()


@pytest.mark.parametrize("name,slug", TOOL_SLUGS.items())
def test_each_mcp_tool_calls_mocked_actor_with_caps(name, slug, mock_apify):
    result = asyncio.run(mcp.call_tool(name, required_input(slug) | {"result_limit": 2, "max_total_charge_usd": 0.1}))
    envelope = json.loads(result.content[0].text)
    assert envelope["items"] == [{"fixture": "mock row"}]
    assert result.structuredContent == envelope
    assert envelope["omitted_items"] == 0
    mock_apify[1].actor.assert_called_once_with(f"hirepulse/{slug}")
    assert mock_apify[2].call.call_args.kwargs["max_items"] == 2
    mock_apify[3].list_items.assert_called_once_with(limit=2)


def test_output_budget_preserves_whole_records_and_reports_omissions():
    small = {"fixture": "small"}
    encoded = bounded_output([{"transcript": "א" * MAX_OUTPUT_BYTES}, small], 2)
    assert len(encoded.encode("utf-8")) <= MAX_OUTPUT_BYTES
    result = json.loads(encoded)
    assert result["items"] == [small]
    assert result["returned_items"] == 1
    assert result["omitted_items"] == 1
    assert result["output_truncated"]
    assert result["result_limit_reached"]


def test_many_records_respect_byte_budget():
    encoded = bounded_output([{"fixture": "mock" * 100} for _ in range(1000)], 1000)
    assert len(encoded.encode("utf-8")) <= MAX_OUTPUT_BYTES
    result = json.loads(encoded)
    assert result["returned_items"] + result["omitted_items"] == 1000
    assert result["output_truncated"]


def test_empty_mcp_output():
    result = json.loads(bounded_output([], 60))
    assert result["items"] == []
    assert not result["output_truncated"]
    assert not result["result_limit_reached"]


def test_mcp_rejects_missing_token_without_creating_token_files(monkeypatch, mock_apify):
    monkeypatch.delenv("APIFY_TOKEN")
    result = asyncio.run(mcp.call_tool("company_intent", {"domains": ["stripe.com"]}))
    assert result.isError
    error = json.loads(result.content[0].text)["error"]
    assert "Set APIFY_TOKEN in the environment" in error["message"]
    assert "APIFY_TOKEN" in error["suggested_agent_action"]
    assert result.structuredContent == {"error": error}
    mock_apify[0].assert_not_called()


def test_stdio_entrypoint(monkeypatch, mock_apify):
    calls = []
    monkeypatch.setattr(mcp, "run", lambda **kwargs: calls.append(kwargs))
    main()
    assert calls == [{"transport": "stdio"}]
    mock_apify[0].assert_not_called()
