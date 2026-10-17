"""Eight synchronous functions. Actor parameters follow bundled schema snapshots."""
from __future__ import annotations

from typing import Any, Literal

from ._runner import run_actor


def search_aliexpress(
    queries: list[str],
    *,
    max_results_per_query: int = 60,
    sort: Literal['best_match', 'orders', 'price_low', 'price_high'] = 'best_match',
    currency: Literal['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'BRL', 'MXN', 'PLN', 'ILS', 'JPY', 'KRW', 'INR', 'TRY', 'CHF', 'SEK'] = 'USD',
    ship_to: str = 'US',
    min_price: int | None = None,
    max_price: int | None = None,
    result_limit: int = 60,
    max_total_charge_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Returns product_id, title, url, image_url, price, original_price, discount_percent, currency, rating, sold, sold_text, is_sponsored, listed_since and ship_to.
    Use this when... searching AliExpress products by queries with a chosen currency and ship_to country.
    Do NOT use for... seller names or seller ratings, shipping costs or delivery estimates, reviews or stock. rating is a product rating.
    Cost: $2.50 per 1,000 products. Free Apify plan: 100 products per run; 60 products per page.

    Optional inputs without schema defaults use None (omitted).
    result_limit requests a run result cap and bounds fetched rows; max_total_charge_usd
    is the spending option passed to Apify. Partial data is possible.
    """
    return run_actor(
        'aliexpress-search-scraper',
        {
            'queries': queries,
            'max_results_per_query': max_results_per_query,
            'sort': sort,
            'currency': currency,
            'ship_to': ship_to,
            'min_price': min_price,
            'max_price': max_price,
        },
        result_limit=result_limit,
        max_total_charge_usd=max_total_charge_usd,
    )


def google_ads_by_domain(
    domains: list[str],
    *,
    mode: Literal['ads', 'summary'] = 'ads',
    max_ads_per_domain: int = 40,
    country: str | None = None,
    platform: Literal['all', 'google_search', 'youtube', 'google_shopping', 'google_play', 'google_maps'] = 'all',
    format: Literal['all', 'text', 'image', 'video'] = 'all',
    date_from: str | None = None,
    date_to: str | None = None,
    only_new_ads: bool = False,
    result_limit: int = 60,
    max_total_charge_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Returns advertiser_name, advertiser_id, advertiser_verified, ad_id, format, first_shown, last_shown, preview_image_url and transparency_url; summary mode returns one row per domain.
    Use this when... researching a company's Google ads by domains, or monitoring only_new_ads.
    Do NOT use for... ad copy text, spend, impressions, launching or editing ads; this tool returns preview images and Transparency Center metadata.
    Cost: $0.005 per domain + $0.0015 per ad; summary mode has no per-ad charge. Domains with no ads cost $0. An Actor-start event is charged separately.

    Optional inputs without schema defaults use None (omitted).
    result_limit requests a run result cap and bounds fetched rows; max_total_charge_usd
    is the spending option passed to Apify. Partial data is possible.
    """
    return run_actor(
        'google-ads-transparency-scraper',
        {
            'domains': domains,
            'mode': mode,
            'max_ads_per_domain': max_ads_per_domain,
            'country': country,
            'platform': platform,
            'format': format,
            'date_from': date_from,
            'date_to': date_to,
            'only_new_ads': only_new_ads,
        },
        result_limit=result_limit,
        max_total_charge_usd=max_total_charge_usd,
    )


def company_intent(
    domains: list[str],
    *,
    country: str = 'US',
    include_jobs: bool = False,
    result_limit: int = 60,
    max_total_charge_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Returns domain, open_jobs, jobs_posted_last_30_days, ads_running_now, total_google_ads, organic_traffic_monthly, seo_trend, email_provider, intent_score and summary.
    Use this when... comparing hiring, advertising, SEO and MX email-provider signals for company domains.
    Do NOT use for... treating the 0-100 intent_score as proof a company will buy; use the underlying signals and summary.
    Cost: $0.03 per company report, charged only when the full report was produced. Free plan: hiring and email signals for 5 companies.

    Optional inputs without schema defaults use None (omitted).
    result_limit requests a run result cap and bounds fetched rows; max_total_charge_usd
    is the spending option passed to Apify. Partial data is possible.
    """
    return run_actor(
        'company-intent-radar',
        {
            'domains': domains,
            'country': country,
            'include_jobs': include_jobs,
        },
        result_limit=result_limit,
        max_total_charge_usd=max_total_charge_usd,
    )


def google_jobs(
    queries: list[str],
    *,
    country: Literal['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BR', 'IN', 'MX', 'JP', 'AL', 'DZ', 'AO', 'AR', 'AM', 'AT', 'AZ', 'BH', 'BD', 'BE', 'BO', 'BA', 'BG', 'BF', 'KH', 'CM', 'CL', 'CO', 'CR', 'CI', 'HR', 'CY', 'CZ', 'DK', 'EC', 'EG', 'SV', 'EE', 'FI', 'GH', 'GR', 'GT', 'HK', 'HU', 'ID', 'IE', 'IL', 'JO', 'KZ', 'KE', 'LV', 'LT', 'MY', 'MT', 'MD', 'MC', 'MA', 'MM', 'NZ', 'NI', 'NG', 'MK', 'NO', 'PK', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'RO', 'SA', 'SN', 'RS', 'SG', 'SK', 'SI', 'ZA', 'KR', 'LK', 'SE', 'CH', 'TW', 'TH', 'TN', 'TR', 'UA', 'AE', 'UY', 'VE', 'VN'] = 'US',
    location: str | None = None,
    radius_km: int | None = None,
    max_jobs_per_query: int = 50,
    employment_types: list[Literal['fulltime', 'partime', 'contractor', 'intern']] | None = None,
    include_descriptions: bool = True,
    language: str | None = None,
    result_limit: int = 60,
    max_total_charge_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Returns title, company, location, salary, salary_min, salary_max, contract_type, posted_at, posted_ago, source and apply_url; salary fields depend on what is shown.
    Use this when... searching Google Jobs by queries for a country or a city with radius_km.
    Do NOT use for... assuming salary is present on every job or submitting job applications.
    Cost: $0.005 per search that returns jobs + $0.001 per job. Supports 90+ countries.

    Optional inputs without schema defaults use None (omitted).
    result_limit requests a run result cap and bounds fetched rows; max_total_charge_usd
    is the spending option passed to Apify. Partial data is possible.
    """
    return run_actor(
        'google-jobs-scraper',
        {
            'queries': queries,
            'country': country,
            'location': location,
            'radius_km': radius_km,
            'max_jobs_per_query': max_jobs_per_query,
            'employment_types': employment_types,
            'include_descriptions': include_descriptions,
            'language': language,
        },
        result_limit=result_limit,
        max_total_charge_usd=max_total_charge_usd,
    )


def ats_jobs(
    companies: list[str],
    *,
    output_mode: Literal['jobs_and_summary', 'summary_only', 'jobs_only'] = 'jobs_and_summary',
    track_diff: bool = True,
    state_id: str = 'default_state',
    extract_tech_keywords: bool = True,
    only_changes: bool = False,
    title_keywords: list[str] | None = None,
    departments: list[str] | None = None,
    locations: list[str] | None = None,
    technologies: list[str] | None = None,
    remote_only: bool = False,
    max_jobs_per_company: int = 0,
    result_limit: int = 60,
    max_total_charge_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Returns record_type, company_domain, title, location, salary, apply_url, detected_technologies and status on jobs; company_summary rows include total_active_jobs, new_jobs, closed_jobs and is_first_run.
    Use this when... finding a company's job board from a domain such as stripe.com or a board slug in companies. Supports Greenhouse, Lever, Ashby, Workable, Recruitee and SmartRecruiters.
    Do NOT use for... Workday or assuming every careers site is supported. Salary requires employer-published data; technologies come from job titles and descriptions.
    Cost: $0.05 per company whose board was found and processed; not-found and failed companies are not charged. Actor-start charges are separate.
    Choose output_mode='summary_only' for short hiring checks. track_diff shares state_id; first-run NEW jobs are a baseline, not a hiring spike.

    Optional inputs without schema defaults use None (omitted).
    result_limit requests a run result cap and bounds fetched rows; max_total_charge_usd
    is the spending option passed to Apify. Partial data is possible.
    """
    return run_actor(
        'ats-job-pulse',
        {
            'companies': companies,
            'output_mode': output_mode,
            'track_diff': track_diff,
            'state_id': state_id,
            'extract_tech_keywords': extract_tech_keywords,
            'only_changes': only_changes,
            'title_keywords': title_keywords,
            'departments': departments,
            'locations': locations,
            'technologies': technologies,
            'remote_only': remote_only,
            'max_jobs_per_company': max_jobs_per_company,
        },
        result_limit=result_limit,
        max_total_charge_usd=max_total_charge_usd,
    )


def keyword_volume(
    keywords: list[str],
    *,
    mode: Literal['metrics', 'ideas', 'suggestions'] = 'metrics',
    country: Literal['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BR', 'IN', 'MX', 'JP', 'AL', 'DZ', 'AO', 'AR', 'AM', 'AT', 'AZ', 'BH', 'BD', 'BE', 'BO', 'BA', 'BG', 'BF', 'KH', 'CM', 'CL', 'CO', 'CR', 'CI', 'HR', 'CY', 'CZ', 'DK', 'EC', 'EG', 'SV', 'EE', 'FI', 'GH', 'GR', 'GT', 'HK', 'HU', 'ID', 'IE', 'IL', 'JO', 'KZ', 'KE', 'LV', 'LT', 'MY', 'MT', 'MD', 'MC', 'MA', 'MM', 'NZ', 'NI', 'NG', 'MK', 'NO', 'PK', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'RO', 'SA', 'SN', 'RS', 'SG', 'SK', 'SI', 'ZA', 'KR', 'LK', 'SE', 'CH', 'TW', 'TH', 'TN', 'TR', 'UA', 'AE', 'UY', 'VE', 'VN'] = 'US',
    language: str | None = None,
    max_results: int = 50,
    min_search_volume: int = 0,
    include_monthly_searches: bool = False,
    include_ai_search_volume: bool = False,
    result_limit: int = 60,
    max_total_charge_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Returns keyword, search_volume, cpc_usd, competition, competition_level and keyword_difficulty; metrics_available indicates whether metrics exist.
    Use this when... measuring Google monthly keyword volume, CPC and competition, or discovering keyword ideas from keywords.
    Do NOT use for... treating Google search_volume as measured visits to a website.
    Choose mode='metrics', 'ideas' or 'suggestions'. Cost: $0.03 per lookup + $0.005 per keyword result. Free-plan metrics for the first 3 keywords depend on availability and can be paused.

    Optional inputs without schema defaults use None (omitted).
    result_limit requests a run result cap and bounds fetched rows; max_total_charge_usd
    is the spending option passed to Apify. Partial data is possible.
    """
    return run_actor(
        'keyword-search-volume',
        {
            'keywords': keywords,
            'mode': mode,
            'country': country,
            'language': language,
            'max_results': max_results,
            'min_search_volume': min_search_volume,
            'include_monthly_searches': include_monthly_searches,
            'include_ai_search_volume': include_ai_search_volume,
        },
        result_limit=result_limit,
        max_total_charge_usd=max_total_charge_usd,
    )


def domain_seo(
    domains: list[str],
    *,
    country: Literal['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BR', 'IN', 'MX', 'JP', 'AL', 'DZ', 'AO', 'AR', 'AM', 'AT', 'AZ', 'BH', 'BD', 'BE', 'BO', 'BA', 'BG', 'BF', 'KH', 'CM', 'CL', 'CO', 'CR', 'CI', 'HR', 'CY', 'CZ', 'DK', 'EC', 'EG', 'SV', 'EE', 'FI', 'GH', 'GR', 'GT', 'HK', 'HU', 'ID', 'IE', 'IL', 'JO', 'KZ', 'KE', 'LV', 'LT', 'MY', 'MT', 'MD', 'MC', 'MA', 'MM', 'NZ', 'NI', 'NG', 'MK', 'NO', 'PK', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'RO', 'SA', 'SN', 'RS', 'SG', 'SK', 'SI', 'ZA', 'KR', 'LK', 'SE', 'CH', 'TW', 'TH', 'TN', 'TR', 'UA', 'AE', 'UY', 'VE', 'VN'] = 'US',
    language: str | None = None,
    top_keywords: int = 20,
    competitors: int = 10,
    result_limit: int = 60,
    max_total_charge_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Returns record_type, domain, organic_traffic_estimate, organic_keywords and organic_traffic_value_usd on overview rows; ranked_keyword and competitor rows include keyword and competitor_domain respectively.
    Use this when... comparing estimated organic traffic, ranking keywords, traffic value and competitor domains for domains.
    Do NOT use for... presenting estimated organic traffic as measured website analytics.
    Cost: $0.02 per lookup + $0.005 per returned record; overview only $0.025, defaults with 20 keywords and 10 competitors $0.215. Actor-start charges are separate.
    Set top_keywords=0 and competitors=0 for overview only; check has_data on overview rows.

    Optional inputs without schema defaults use None (omitted).
    result_limit requests a run result cap and bounds fetched rows; max_total_charge_usd
    is the spending option passed to Apify. Partial data is possible.
    """
    return run_actor(
        'domain-seo-overview',
        {
            'domains': domains,
            'country': country,
            'language': language,
            'top_keywords': top_keywords,
            'competitors': competitors,
        },
        result_limit=result_limit,
        max_total_charge_usd=max_total_charge_usd,
    )


def youtube_transcripts(
    videos: list[str],
    *,
    language: str | None = None,
    include_timestamps: bool = False,
    result_limit: int = 60,
    max_total_charge_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Returns video_id, url, status, transcript and language; include_timestamps=True adds segments with start, duration and text.
    Use this when... retrieving YouTube transcripts in bulk from videos, with timestamps when needed.
    Do NOT use for... treating an error status as a delivered transcript or ignoring missing transcript data.
    Cost: $0.003 per delivered transcript; unavailable videos, missing captions and failed fetches are not charged. Actor-start charges are separate.
    Check status on each record. Free Apify plan: first 3 videos of each run. Long transcripts may exceed the MCP output budget.

    Optional inputs without schema defaults use None (omitted).
    result_limit requests a run result cap and bounds fetched rows; max_total_charge_usd
    is the spending option passed to Apify. Partial data is possible.
    """
    return run_actor(
        'youtube-transcript-scraper',
        {
            'videos': videos,
            'language': language,
            'include_timestamps': include_timestamps,
        },
        result_limit=result_limit,
        max_total_charge_usd=max_total_charge_usd,
    )
