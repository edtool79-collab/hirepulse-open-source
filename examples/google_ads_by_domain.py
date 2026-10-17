"""Run explicitly with APIFY_TOKEN in the environment; this uses paid Apify.

Not executed by tests.
"""
from hirepulse_tools import google_ads_by_domain


def main() -> None:
    items = google_ads_by_domain(['nike.com'], result_limit=5, max_total_charge_usd=0.10)
    print(items)


if __name__ == "__main__":
    main()
