"""Exercise the real stdio transport, with the child Apify client mocked too."""

import os
import sys
import json

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from jsonschema import Draft202012Validator

from hirepulse_tools._catalog import TOOL_SLUGS

BOOTSTRAP = """
import runpy
from unittest.mock import patch
with patch('hirepulse_tools._runner.ApifyClient', side_effect=AssertionError('Real Apify calls forbidden')):
    runpy.run_module('hirepulse_tools.mcp_server', run_name='__main__')
"""


def test_stdio_initialize_and_list_eight_tools():
    async def check():
        environment = {"PYTHONDONTWRITEBYTECODE": "1"}
        for name in ("TEMP", "TMP", "PYTHONPATH"):
            if name in os.environ:
                environment[name] = os.environ[name]
        # APIFY_TOKEN is never passed to this subprocess.
        server = StdioServerParameters(
            command=sys.executable, args=["-c", BOOTSTRAP], env=environment
        )
        with anyio.fail_after(30):
            async with stdio_client(server) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    initialized = await session.initialize()
                    assert initialized.serverInfo.name == "HirePulse tools"
                    registered = await session.list_tools()
                    assert len(registered.tools) == 8
                    assert {tool.name for tool in registered.tools} == set(TOOL_SLUGS)
                    for tool in registered.tools:
                        assert tool.outputSchema and tool.outputSchema["type"] == "object"
                    # Exercise actual protocol error serialization; no Actor can run.
                    for name, arguments in [
                        ("company_intent", {"domains": ["stripe.com"]}),
                        ("company_intent", {"domains": "private-invalid-value"}),
                        ("missing_tool", {}),
                    ]:
                        result = await session.call_tool(name, arguments)
                        assert result.isError
                        envelope = json.loads(result.content[0].text)
                        assert envelope["error"]["message"]
                        assert envelope["error"]["suggested_agent_action"]
                        assert result.structuredContent == envelope
                        if name in TOOL_SLUGS:
                            tool = next(t for t in registered.tools if t.name == name)
                            Draft202012Validator(tool.outputSchema).validate(envelope)
                        assert "private-invalid-value" not in result.model_dump_json()

    anyio.run(check)
