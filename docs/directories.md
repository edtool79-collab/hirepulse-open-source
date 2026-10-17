# Directory drafts and offline validation

GitHub identity has one editable source: `publishing.json`. Run
`python scripts/render_metadata.py` after changing it or the release name/version
in `pyproject.toml`. The script writes `server.json`, `glama.json` and the
README's hidden MCP ownership marker; it has no network or publishing behavior.
Directory schemas require literal strings, so generated copies appear in those
files. `python scripts/render_metadata.py --check` catches stale copies.

`server.json` registers the published PyPI stdio package `hirepulse-tools`.
Its uvx command explicitly installs the `mcp` extra before running
`hirepulse-mcp`, equivalent to `python -m hirepulse_tools.mcp_server`.
The existing Apify hosted endpoint for all eight Actors is already registered
separately as `io.github.edtool79-collab/hirepulse-tools`. It remains documented
in the README, and is omitted from this entry to avoid claiming the same remote
URL twice. `publishing.json` sets `include_hosted_remote` to `false`; omitting
the setting preserves hosted metadata for older configurations. Neither
transport embeds an authentication token. Tests do not run paid Actors.

Formats checked on 2026-10-15:

- [Official MCP Registry server format](https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/generic-server-json.md),
  using the current linked
  [2025-12-11 JSON schema](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json).
- [Official Registry PyPI ownership requirements](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/package-types.mdx):
  the README `mcp-name` marker must match the registry name. Schema validation
  alone does not verify package or namespace ownership or directory acceptance.
- [Glama's format description](https://glama.ai/blog/2025-07-08-what-is-glamajson)
  and [Glama's schema](https://glama.ai/mcp/schemas/server.json). The generated
  maintainer uses the configured GitHub owner; if the owner is an organization,
  a human must review the actual individual maintainer usernames before submission.
- [Smithery's current publication documentation](https://smithery.ai/docs/build/publish)
  describes local MCPB bundles. The requested `smithery.yaml` uses the stdio
  `startCommand` descriptor with a single required `apifyToken` secret and
  `APIFY_TOKEN` environment mapping. It is not a bundle or deployment. Its YAML,
  config schema and command mapping are checked locally; current Smithery
  acceptance of this descriptor was not verified. Review that before submitting.

Unmodified fetched JSON schemas are saved under `tests/fixtures/`. The pytest
suite validates both directory JSON files against these schemas with URI format
checking; it also checks metadata synchronization and Smithery's configuration.
Tests do not fetch schemas or call directory services, Apify or any real Actor.
