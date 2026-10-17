# Monitor competitors' new Google ads weekly and alert Slack with Apify

Read competitor domains from a Google Sheet once a week and request only ads not returned by earlier matching runs. Send a single Slack digest of the returned ads.

## Who it's for

Marketing teams monitoring competitor creatives.

## Setup

1. Install the official @apify/n8n-nodes-apify package in your n8n environment and select your Apify credential in the Actor node.
2. Select your Google Sheets and Slack credentials in their nodes; credentials are intentionally unassigned.
3. Create Competitors with header Domain and up to 3 unique domains. Select YOUR_SHEET_ID and YOUR_SLACK_CHANNEL.
4. Edit Configure this batch, replace resource placeholders, and confirm the workflow timezone and Monday 08:00 schedule before activation.

## What you need

An n8n environment with the official Apify node, an Apify account, and Google Sheets and Slack accounts with access to your chosen resources. Select credentials in n8n; no credential IDs or tokens are included.

## Cost

$0.005 per domain + $0.0015 per ad. Apify run cap: $1.

## Operation and limits

One Actor run per batch, with maxTotalChargeUsd = 1, no retries and no polling. Empty input produces no paid run. A capped run may be partial; inspect its Apify results before repeating any work. Do not enable automatic retry or resume from a node that starts another Actor run.

At most 3 domains and 20 ads per domain. The first run establishes what has been seen; returned ads need not have launched this week. Keep the same account and filters for monitoring. No returned ad records means no Slack message. A run cap or result limit can leave ads unreported.
