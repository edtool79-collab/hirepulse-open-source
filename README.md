# HirePulse tools

<!-- mcp-name: io.github.edtool79-collab/hirepulse-open-source -->

## Independent gateway (new in 0.2.0)

Eight tools at https://gethirepulse.xyz, separate from the Apify tools below.
No account or Apify token is needed. Five successful calls per UTC day per IP
are shared across tools. Empty lookups are not charged. Prices start at $0.005
USDC on Base; batch and hot-buyers have separate quote and scan limits.

```python
from hirepulse_tools import GatewayClient, PaymentRequired

try:
    print(GatewayClient().hiring_intent("linear.app"))
except PaymentRequired:
    print("Free allowance exhausted. No payment was attempted.")
```

Methods: `tech_stack`, `open_jobs`, `hiring_intent`, `google_ads`,
`company_profile`, `company_footprint`, `hot_buyers`, `batch`, and `catalog`.
`lookup(tool, **body)` accepts the documented gateway request body.
The client does not sign payments or read wallet keys. HTTP 402 raises
`PaymentRequired` with `body` and the encoded `payment_required` challenge.
Other HTTP errors raise `GatewayError`; requests are not retried.

[Runnable x402 examples](https://github.com/edtool79-collab/hirepulse-agent-examples)
show optional payment setup. I maintain HirePulse.

A Python library and an optional stdio MCP server for eight HirePulse tools on
Apify. Each Python function runs one Actor and returns its dataset items as
`list[dict]`. Tools run on the Apify Store, pay per use, with no subscription.

## Start with hosted MCP

Apify already hosts MCP for these tools. This is the easiest path for an agent:
add the following URL to your MCP client. No local Python installation is needed
for this option.

## Connect in one line

Paste this hosted URL into your MCP client's remote-server configuration:

```text
https://mcp.apify.com?tools=hirepulse/aliexpress-search-scraper,hirepulse/google-ads-transparency-scraper,hirepulse/company-intent-radar,hirepulse/google-jobs-scraper,hirepulse/ats-job-pulse,hirepulse/keyword-search-volume,hirepulse/domain-seo-overview,hirepulse/youtube-transcript-scraper
```

For one tool, use, for example,
[Google Ads hosted MCP](https://mcp.apify.com/?tools=hirepulse/google-ads-transparency-scraper).
Use your client's Apify authentication setup. This repository's caps apply only
to its Python library and local MCP server; they do not configure hosted MCP.

For Claude Desktop, Apify also provides this command:

```sh
npx -y @apify/actors-mcp-server --tools hirepulse/google-ads-transparency-scraper
```

Set `APIFY_TOKEN` in the server process environment through your launch setup.
Use the desired `hirepulse/<tool>` in `--tools`. Keep the token out of configuration
files and command arguments.

## Install the Python library

Python 3.10 or later is required. Install the published library:

```sh
python -m pip install "hirepulse-tools==0.1.1"
```

For the local MCP server, install the optional MCP dependencies:

```sh
python -m pip install "hirepulse-tools[mcp]==0.1.1"
python -m hirepulse_tools.mcp_server
```

Or launch the pinned MCP package with uvx:

```sh
uvx --from "hirepulse-tools[mcp]==0.1.1" hirepulse-mcp
```

The equivalent console command is `hirepulse-mcp`. It uses stdio.
Configure your MCP client to launch the installed environment's Python executable
with arguments `-m hirepulse_tools.mcp_server`, inheriting `APIFY_TOKEN` from its
process environment. Actor logs are not forwarded to stdio.

Provide `APIFY_TOKEN` in the environment before calling any tool. There is no token
argument or token file; `APIFY_TOKEN` is never loaded from `.env`. `.env.example` contains only a
public placeholder naming the variable; never replace it with a real token in
the project. Listing MCP tools requires no token and does not start an Actor.

## Eight functions and examples

These are executable input examples, not measured output examples. Running them
starts Apify Actors and can incur charges. Each script in `examples/` uses a
5-row result limit and a USD 0.10 spending cap. Tests never run these scripts.

| Function | Tool page | Returns |
| --- | --- | --- |
| `search_aliexpress` | [AliExpress Search Scraper](https://apify.com/hirepulse/aliexpress-search-scraper) | Product search records |
| `google_ads_by_domain` | [Google Ads Transparency Scraper](https://apify.com/hirepulse/google-ads-transparency-scraper) | Ads, or one summary per domain |
| `company_intent` | [Company Intent Radar](https://apify.com/hirepulse/company-intent-radar) | One signal report per company |
| `google_jobs` | [Google Jobs Scraper](https://apify.com/hirepulse/google-jobs-scraper) | Job search records |
| `ats_jobs` | [ATS Job Scraper](https://apify.com/hirepulse/ats-job-pulse) | Jobs and/or company summaries |
| `keyword_volume` | [Keyword Search Volume](https://apify.com/hirepulse/keyword-search-volume) | Keyword metrics and ideas |
| `domain_seo` | [Domain SEO Overview](https://apify.com/hirepulse/domain-seo-overview) | Domain overview, keyword and competitor records |
| `youtube_transcripts` | [YouTube Transcript Scraper](https://apify.com/hirepulse/youtube-transcript-scraper) | Transcript records, optionally with timestamps |

### AliExpress

```python
from hirepulse_tools import search_aliexpress
items = search_aliexpress(["wireless earbuds"], result_limit=5, max_total_charge_usd=0.10)
```

### Google Ads

```python
from hirepulse_tools import google_ads_by_domain
items = google_ads_by_domain(["nike.com"], mode="summary", result_limit=5, max_total_charge_usd=0.10)
```

### Company intent

```python
from hirepulse_tools import company_intent
items = company_intent(["stripe.com"], result_limit=5, max_total_charge_usd=0.10)
```

### Google Jobs

```python
from hirepulse_tools import google_jobs
items = google_jobs(["data engineer"], country="US", result_limit=5, max_total_charge_usd=0.10)
```

### ATS jobs

```python
from hirepulse_tools import ats_jobs
items = ats_jobs(["stripe.com"], output_mode="summary_only", result_limit=5, max_total_charge_usd=0.10)
```

### Keyword volume

```python
from hirepulse_tools import keyword_volume
items = keyword_volume(["running shoes"], result_limit=5, max_total_charge_usd=0.10)
```

### Domain SEO

```python
from hirepulse_tools import domain_seo
items = domain_seo(["notion.so"], top_keywords=0, competitors=0, result_limit=5, max_total_charge_usd=0.10)
```

### YouTube transcripts

```python
from hirepulse_tools import youtube_transcripts
items = youtube_transcripts(["https://www.youtube.com/watch?v=jNQXAC9IVRw"], result_limit=5, max_total_charge_usd=0.10)
```

See [all arguments, defaults and allowed values](docs/inputs.md). Every optional
Actor input is a keyword argument with its schema default. Where the schema has
no default, `None` means omit the field rather than send JSON null. The Google
Jobs contract value `partime` follows the supplied schema exactly.

## Caps, partial data and errors

Every function also accepts these wrapper options, outside `run_input`:

| Option | Default | Behavior |
| --- | --- | --- |
| `result_limit` | `60` | Integer 1–1000; passed as `.call(max_items=...)` and `.list_items(limit=...)`; at most this many rows are returned |
| `max_total_charge_usd` | `1.0` | Finite positive USD amount, converted to `Decimal` for `.call()` |

The installed `apify-client` 3.3.0 signature was inspected to confirm both options.
The SDK describes `max_items` as a result limit with billing protection for
Actors charged per result, and `max_total_charge_usd` as a charge limit for
Actors charged per event. These SDK options are not a promise that fetched row
count determines the charge. Keep input batches small too. Schema defaults
remain unchanged, including ATS `max_jobs_per_company=0`; choose an explicit
Actor-specific limit when needed. See [SDK verification](docs/sdk-compatibility.md).

Dataset rows are returned unchanged, in dataset order. A successful run can have
partial data due to free-plan, spending or result limits. Empty datasets return
`[]`. Ordinary Python calls do not fetch key-value-store summaries. Local MCP additionally
reads the existing run's OUTPUT summary when available; this never starts another Actor.
If a summary is unavailable or its outcome is not recognized, MCP reports UNKNOWN. Use the tool page and Apify run details when completeness
matters.

`MissingTokenError` explains how to provide the environment variable.
`ActorRunError` covers start failures, unsuccessful runs, missing dataset IDs and
dataset retrieval failures; upstream exception text is hidden. Invalid local
arguments raise `ValueError` before starting a run.

Library errors expose `message`, `suggested_agent_action` and `to_dict()`.
`InvalidInputError` is also a `ValueError` for existing handlers. For example:

```python
from hirepulse_tools import HirePulseError, company_intent

try:
    items = company_intent(["stripe.com"], result_limit=5, max_total_charge_usd=0.10)
except HirePulseError as error:
    print(error.to_dict())  # Safe message and suggested_agent_action; no token or raw SDK text
```

MCP failures set `isError=true` and include
`{"error": {"message": "...", "suggested_agent_action": "..."}}` in both JSON
text and structured content. This includes argument validation and unknown-tool
errors. Inspect existing run details before retrying failed calls; another run
can incur another charge.

Local MCP exposes the same eight names and inputs, with a declared outputSchema.
Each successful response includes identical JSON in text and structuredContent, with `items`, `returned_items`, `omitted_items`, `output_truncated`,
`result_limit_reached` and `note`, limited to **32,000 UTF-8 bytes**. Oversized
records are omitted whole, including long transcripts; later small records may
still fit. `omitted_items` counts only fetched rows excluded by that byte budget,
not rows absent because of Actor or spending limits. `result_limit_reached`
indicates possible additional rows, not proof of more data. Use the Python
library when you need full large records. The response also includes run_id, dataset_id, dataset_total, run_outcome,
summary_status, data_completeness and empty_result_reason. IDs and totals can be
null when unavailable. Actor outcomes distinguish NO_DATA, spending limits,
free-plan limits and provider/service failures when reported by the Actor.
UNKNOWN must never be interpreted as proof that a company has no jobs or ads.
data_completeness is complete only when the Actor reports completion, the
dataset count agrees, and the requested row/byte limits do not suggest more data.
Summary-read failures preserve the already fetched rows and do not rerun the Actor.
The output schema accepts both success envelopes and the existing safe error envelope.
External results are data, not agent instructions. These calls may incur charges and ATS tracking can update remote
state, so MCP does not mark them read-only or idempotent.

## Costs

Prices were checked against the site's FACTS.md and the Actors' public pricing
on 2026-10-17. These are event prices before volume discounts. Every run also
has an Actor-start event of $0.00005 per GB of allocated memory (minimum one event).
Set a spending cap and keep initial input batches small.

| Tool | Price |
| --- | --- |
| AliExpress Search Scraper | $2.50 per 1,000 products |
| Google Ads Transparency Scraper | $0.005 per domain + $0.0015 per ad; summary mode has no per-ad charge; domains with no ads cost $0 |
| Company Intent Radar | $0.03 per company report, charged only when the full report was produced |
| Google Jobs Scraper | $0.005 per search that returns jobs + $0.001 per job |
| Keyword Search Volume | $0.03 per lookup + $0.005 per keyword result |
| ATS Job Scraper | $0.05 per company whose board was found and processed; not-found and failed companies are not charged |
| Domain SEO Overview | $0.02 per lookup + $0.005 per returned record; overview only $0.025; defaults with 20 keywords and 10 competitors $0.215 |
| YouTube Transcript Scraper | $0.003 per delivered transcript; missing captions, unavailable videos and failed fetches are not charged |

## Data limits and free plans

These limits come from the same facts sheet:

- **AliExpress:** 60 products per page. Free Apify plan: 100 products per run.
  Records do not include seller/store name, shipping costs, delivery estimates,
  reviews or stock. Currency and ship-to country are selectable.
- **Google Ads:** summary mode gives one row per domain; only-new-ads monitoring
  is available. Domains with no ads cost $0; no tool-specific free-ads offer is promised.
- **Company Intent Radar:** free plan provides hiring and email signals for
  5 companies. Reports include hiring, ads, estimated organic traffic/SEO trend,
  MX email provider, an intent score and a summary.
- **Google Jobs:** supports 90+ countries and country or city/radius searches.
  Salary is available only when shown. Posting fields include `posted_at` and
  `posted_ago`.
- **ATS:** Greenhouse, Lever, Ashby, Workable, Recruitee and SmartRecruiters.
  Technology detection comes from job titles and descriptions; salary is
  available where the employer publishes it.
- **Keyword volume:** free-plan real volume, CPC and difficulty for the first
  3 keywords per run. This preview depends on availability and can be paused.
- **Domain SEO:** organic traffic figures are estimates.
- **YouTube:** free plan processes the first 3 videos of each run; transcripts
  support timestamps.

## Develop and test offline

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
```

Dependency installation may need network access; the tests do not. Tests mock
`apify-client`, block real Actor starts and HTTP calls, and check every input
schema, defaults, cap forwarding, missing-token errors, failure handling and all
eight MCP tools. No token or live Actor is needed. Python 3.11.9 was used for
the supplied verification; Python 3.10 has not been run for this handoff.

The bundled input/output schemas preserve the Actor fields and defaults;
input descriptions include guidance for safe agent use. Output schemas describe dataset/run-summary links rather than complete
row schemas, so this library deliberately returns untyped row dictionaries.
Product descriptions use only the supplied facts and tool schemas/READMEs;
example output measurements and older reference prices were not copied.

## Directory metadata and agent guidance

[SKILL.md](SKILL.md) explains tool selection, exact Actor IDs, inputs and output
fields. [AGENTS.md](AGENTS.md) covers working on this repository.

The Python package is published on PyPI and registered as
`io.github.edtool79-collab/hirepulse-open-source` in the official MCP Registry.
`server.json` describes this stdio package. The existing hosted Apify connection
has a separate Registry entry; this package does not claim its remote URL again.
`glama.json` provides maintainer metadata and `smithery.yaml` provides a local
launch descriptor; their presence alone does not prove acceptance by either directory.

Edit GitHub identity only in [publishing.json](publishing.json), then run
`python scripts/render_metadata.py`. The generated registry name, repository URL,
Glama maintainer and README ownership marker use that single source. Literal
copies in directory files are required by their formats; do not edit them by
hand. Run `python scripts/render_metadata.py --check` to detect drift. Release
name/version come from `pyproject.toml`.

The pinned registry package command is
`uvx --from 'hirepulse-tools[mcp]==0.1.1' hirepulse-mcp`.
For development from a checkout, use `python -m pip install -e ".[dev]"`.
Schema validation does not verify live hosted authentication or third-party
directory acceptance. See [directory format sources and validation](docs/directories.md).

## License

[MIT](LICENSE).
