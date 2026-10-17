# Enrich company leads weekly with intent signals in Google Sheets using Apify

Once a week, read a small company-domain list and retrieve intent reports in one batch. Write intent scores, open job counts, ad signals and one-line summaries back to the matching source rows.

## Who it's for

Sales operations and lead research teams.

## Setup

1. Install the official @apify/n8n-nodes-apify package in your n8n environment and select your Apify credential in the Actor node.
2. Select your Google Sheets credentials in their nodes; credentials are intentionally unassigned.
3. Create Leads with headers Domain, Intent score, Open jobs, Ads running now, Summary, Checked on. Keep Domain unique, including after normalizing www, URL paths and case; at most 5 domains.
4. Edit Configure this batch, replace resource placeholders, and confirm the Asia/Jerusalem timezone and Monday 08:00 schedule before activation.

## What you need

An n8n environment with the official Apify node, an Apify account, and Google Sheets accounts with access to your chosen resources. Select credentials in n8n; no credential IDs or tokens are included.

## Cost

$0.03 per company report, charged only when the full report was produced. Apify run cap: $1.

## Operation and limits

One Actor run per batch, with maxTotalChargeUsd = 1, no retries and no polling. Empty input produces no paid run. A capped run may be partial; inspect its Apify results before repeating any work. Do not enable automatic retry or resume from a node that starts another Actor run.

Updates match the original Domain cell exactly; keep the source rows unchanged while running. Missing signals are written as blank, never as zero or false. Free-plan results may omit ad and SEO signals.
