# SDK compatibility

Verified by inspecting installed Python SDK code, without contacting Apify:

- `apify-client` 3.3.0: `ActorClient.call` accepts keyword-only `run_input`,
  `max_items: int | None`, `max_total_charge_usd: Decimal | None`, and `logger`.
- The SDK describes `max_items` as the result limit, with a charge limit for
  Actors billed per result; `max_total_charge_usd` limits charges for Actors
  billed per event. The wrapper supplies both and also bounds dataset reading.
- `call()` returns a typed `Run | None`, with `status` and
  `default_dataset_id` attributes. It does not return a dictionary in this version.
- `DatasetClient.list_items(limit=...)` returns a `DatasetItemsPage` with an
  `items` list. The library preserves each record unchanged.
- `logger=None` disables propagation of Actor logs through `.call()`.
- `mcp` 1.30.0 provides the official `mcp.server.fastmcp.FastMCP` used here.

The dependency lower bounds match these inspected versions. Python 3.10 is the
declared minimum; verification for this handoff used Python 3.11.9 only.
No live Actor behavior was verified. Run limits and spending limits can produce
partial datasets; a successful platform run does not establish data completeness.
