# HirePulse automation templates

Three bounded workflows, shared for other users to configure with their own accounts:

| Workflow | Schedule | Input cap | Apify charge cap per execution |
| --- | --- | --- | --- |
| [New Google ads](n8n/competitor-new-ads-weekly.md) | Weekly | 3 domains, up to 20 ads per domain | $1 |
| [New ATS jobs](n8n/ats-new-jobs-daily.md) | Daily | 3 companies, up to 20 returned jobs per company | $1 |
| [Company enrichment](n8n/company-intent-sheet-enrichment.md) | Weekly | 5 domains | $1 |

## n8n

Download the matching JSON file from [n8n/](n8n/) and import it into your own n8n instance.
Install the official Apify node, select your credentials, replace resource placeholders,
and review the documented columns, schedule and timezone before activation.
All exports are inactive and contain no credential bindings. Each sends one bounded batch
to one Actor, without a cycle, automatic retries or paid polling. Empty input stops.
The $1 cap applies to each Actor run, not to all future scheduled runs combined.
Limits can produce partial monitoring coverage. The first tracking run is a baseline.

The files passed offline schema, graph and transformation checks. Live n8n imports,
third-party node mappings and notifications have not been certified. Do not activate a
workflow until its connections and output mappings have been reviewed in your own instance.

## Make

[make/](make/) contains three setup recipes with exact API inputs and spending caps.
These are **not native Make blueprints** and must not be imported as if they were.
Configure them manually using an Apify connection, aggregate the input into one bundle
before the paid API call, and stop on errors rather than starting another paid run.

No credentials, accounts, paid runs or active schedules are supplied by this repository.
