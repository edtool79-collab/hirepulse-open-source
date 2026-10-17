"""Run explicitly with APIFY_TOKEN in the environment; this uses paid Apify.

Not executed by tests.
"""
from hirepulse_tools import ats_jobs


def main() -> None:
    items = ats_jobs(['stripe.com'], result_limit=5, max_total_charge_usd=0.10)
    print(items)


if __name__ == "__main__":
    main()
