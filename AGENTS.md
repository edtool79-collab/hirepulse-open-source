# Working on this repository

- Use Python 3.10+. Install development dependencies with
  `python -m pip install -e ".[dev]"` from this directory.
- Run all tests with `python -m pytest -q`. Tests mock Apify and block network
  requests; never run examples or real Actors as tests. No token is needed.
- Launch stdio MCP with `python -m hirepulse_tools.mcp_server` after installing
  `.[mcp]`. Tool listing needs no token; execution reads only `APIFY_TOKEN` from
  the process environment. Keep stdout reserved for MCP.
- Never commit secrets, write real tokens to files, or add token arguments.
  `.env.example` must remain a public placeholder.
- Preserve the bundled input schemas, defaults, caps and eight exact Actor IDs.
  Tool descriptions begin with returned field names, then `Use this when...`
  and `Do NOT use for...`. Errors include `suggested_agent_action` without
  echoing SDK messages or caller values.
- Directory identity is edited only in `publishing.json`; regenerate with
  `python scripts/render_metadata.py` and verify with `--check`.
- For this handoff, work only in the supplied workspace, leave `facts/` untouched,
  and do not use git, publish, deploy, send messages or spend money.
