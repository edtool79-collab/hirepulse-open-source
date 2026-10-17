# Watch company careers boards daily and send new jobs to Slack with Apify

Check a bounded careers-board watchlist once a day with change tracking enabled. Send one Slack message listing returned NEW jobs and omit closed or existing jobs.

## Who it's for

Recruiters and account researchers watching target companies.

## Setup

1. Install the official @apify/n8n-nodes-apify package in your n8n environment and select your Apify credential in the Actor node.
2. Select your Slack credentials in their nodes; credentials are intentionally unassigned.
3. Enter up to 3 company domains or supported ATS slugs and replace YOUR_UNIQUE_WATCHLIST_STATE_ID. Select YOUR_SLACK_CHANNEL.
4. Edit Configure this batch, replace resource placeholders, and confirm the daily 08:00 schedule and workflow timezone before activation.

## What you need

An n8n environment with the official Apify node, an Apify account, and Slack accounts with access to your chosen resources. Select credentials in n8n; no credential IDs or tokens are included.

## Cost

Pay per use, see the [Apify page](https://apify.com/hirepulse/ats-job-pulse). Apify run cap: $1.

## Operation and limits

One Actor run per batch, with maxTotalChargeUsd = 1, no retries and no polling. Empty input produces no paid run. A capped run may be partial; inspect its Apify results before repeating any work. Do not enable automatic retry or resume from a node that starts another Actor run.

20 job records per company; only_changes is true and track_diff is true. On the first run every job is NEW: the digest labels this baseline possibility. Retain state_id across daily runs and use a different value for other watchlists. The bounded results are not a complete change archive.
