# Input reference

Actor input schemas are bundled unchanged in `src/hirepulse_tools/schemas/`.
All optional Actor inputs are keyword arguments. `None` omits fields without schema defaults; it is not sent as JSON null.
Schema defaults are preserved, including ATS `max_jobs_per_company=0` (unlimited Actor job rows).
Every function also takes `result_limit=60` (1–1000; requested Actor max_items and fetched dataset row cap) and `max_total_charge_usd=1.0` (finite positive USD cap passed to `.call()`). These are not Actor input fields.

## `search_aliexpress`

Actor: `hirepulse/aliexpress-search-scraper`.

| Argument | Type | Default | Allowed values / constraints |
| --- | --- | --- | --- |
| `queries` | array | `required` | `{"minItems": 1, "maxItems": 20}` |
| `max_results_per_query` | integer | `60` | `{"minimum": 1, "maximum": 1200}` |
| `sort` | string | `'best_match'` | `{"enum": ["best_match", "orders", "price_low", "price_high"]}` |
| `currency` | string | `'USD'` | `{"enum": ["USD", "EUR", "GBP", "CAD", "AUD", "BRL", "MXN", "PLN", "ILS", "JPY", "KRW", "INR", "TRY", "CHF", "SEK"]}` |
| `ship_to` | string | `'US'` | `{"pattern": "^[A-Za-z]{2}$"}` |
| `min_price` | integer | `None` | `{"minimum": 0}` |
| `max_price` | integer | `None` | `{"minimum": 0}` |

## `google_ads_by_domain`

Actor: `hirepulse/google-ads-transparency-scraper`.

| Argument | Type | Default | Allowed values / constraints |
| --- | --- | --- | --- |
| `domains` | array | `required` | `{"minItems": 1, "maxItems": 100}` |
| `mode` | string | `'ads'` | `{"enum": ["ads", "summary"]}` |
| `max_ads_per_domain` | integer | `40` | `{"minimum": 1, "maximum": 120}` |
| `country` | string | `None` | `{"pattern": "^([A-Za-z]{2})?$"}` |
| `platform` | string | `'all'` | `{"enum": ["all", "google_search", "youtube", "google_shopping", "google_play", "google_maps"]}` |
| `format` | string | `'all'` | `{"enum": ["all", "text", "image", "video"]}` |
| `date_from` | string | `None` | `{}` |
| `date_to` | string | `None` | `{}` |
| `only_new_ads` | boolean | `False` | `{}` |

## `company_intent`

Actor: `hirepulse/company-intent-radar`.

| Argument | Type | Default | Allowed values / constraints |
| --- | --- | --- | --- |
| `domains` | array | `required` | `{"minItems": 1, "maxItems": 100}` |
| `country` | string | `'US'` | `{"pattern": "^[A-Za-z]{2}$"}` |
| `include_jobs` | boolean | `False` | `{}` |

## `google_jobs`

Actor: `hirepulse/google-jobs-scraper`.

| Argument | Type | Default | Allowed values / constraints |
| --- | --- | --- | --- |
| `queries` | array | `required` | `{"minItems": 1, "maxItems": 50}` |
| `country` | string | `'US'` | `{"enum": ["US", "GB", "CA", "AU", "DE", "FR", "ES", "IT", "NL", "BR", "IN", "MX", "JP", "AL", "DZ", "AO", "AR", "AM", "AT", "AZ", "BH", "BD", "BE", "BO", "BA", "BG", "BF", "KH", "CM", "CL", "CO", "CR", "CI", "HR", "CY", "CZ", "DK", "EC", "EG", "SV", "EE", "FI", "GH", "GR", "GT", "HK", "HU", "ID", "IE", "IL", "JO", "KZ", "KE", "LV", "LT", "MY", "MT", "MD", "MC", "MA", "MM", "NZ", "NI", "NG", "MK", "NO", "PK", "PA", "PY", "PE", "PH", "PL", "PT", "RO", "SA", "SN", "RS", "SG", "SK", "SI", "ZA", "KR", "LK", "SE", "CH", "TW", "TH", "TN", "TR", "UA", "AE", "UY", "VE", "VN"]}` |
| `location` | string | `None` | `{}` |
| `radius_km` | integer | `None` | `{"minimum": 1, "maximum": 300}` |
| `max_jobs_per_query` | integer | `50` | `{"minimum": 1, "maximum": 200}` |
| `employment_types` | array | `None` | `{"items": {"type": "string", "enum": ["fulltime", "partime", "contractor", "intern"], "enumTitles": ["Full-time", "Part-time", "Contractor", "Internship"]}}` |
| `include_descriptions` | boolean | `True` | `{}` |
| `language` | string | `None` | `{}` |

## `ats_jobs`

Actor: `hirepulse/ats-job-pulse`.

| Argument | Type | Default | Allowed values / constraints |
| --- | --- | --- | --- |
| `companies` | array | `required` | `{"minItems": 1, "uniqueItems": true}` |
| `output_mode` | string | `'jobs_and_summary'` | `{"enum": ["jobs_and_summary", "summary_only", "jobs_only"]}` |
| `track_diff` | boolean | `True` | `{}` |
| `state_id` | string | `'default_state'` | `{}` |
| `extract_tech_keywords` | boolean | `True` | `{}` |
| `only_changes` | boolean | `False` | `{}` |
| `title_keywords` | array | `None` | `{"uniqueItems": true}` |
| `departments` | array | `None` | `{"uniqueItems": true}` |
| `locations` | array | `None` | `{"uniqueItems": true}` |
| `technologies` | array | `None` | `{"uniqueItems": true}` |
| `remote_only` | boolean | `False` | `{}` |
| `max_jobs_per_company` | integer | `0` | `{"minimum": 0}` |

## `keyword_volume`

Actor: `hirepulse/keyword-search-volume`.

| Argument | Type | Default | Allowed values / constraints |
| --- | --- | --- | --- |
| `keywords` | array | `required` | `{"minItems": 1, "maxItems": 5000, "uniqueItems": true}` |
| `mode` | string | `'metrics'` | `{"enum": ["metrics", "ideas", "suggestions"]}` |
| `country` | string | `'US'` | `{"enum": ["US", "GB", "CA", "AU", "DE", "FR", "ES", "IT", "NL", "BR", "IN", "MX", "JP", "AL", "DZ", "AO", "AR", "AM", "AT", "AZ", "BH", "BD", "BE", "BO", "BA", "BG", "BF", "KH", "CM", "CL", "CO", "CR", "CI", "HR", "CY", "CZ", "DK", "EC", "EG", "SV", "EE", "FI", "GH", "GR", "GT", "HK", "HU", "ID", "IE", "IL", "JO", "KZ", "KE", "LV", "LT", "MY", "MT", "MD", "MC", "MA", "MM", "NZ", "NI", "NG", "MK", "NO", "PK", "PA", "PY", "PE", "PH", "PL", "PT", "RO", "SA", "SN", "RS", "SG", "SK", "SI", "ZA", "KR", "LK", "SE", "CH", "TW", "TH", "TN", "TR", "UA", "AE", "UY", "VE", "VN"]}` |
| `language` | string | `None` | `{}` |
| `max_results` | integer | `50` | `{"minimum": 1, "maximum": 1000}` |
| `min_search_volume` | integer | `0` | `{"minimum": 0}` |
| `include_monthly_searches` | boolean | `False` | `{}` |
| `include_ai_search_volume` | boolean | `False` | `{}` |

## `domain_seo`

Actor: `hirepulse/domain-seo-overview`.

| Argument | Type | Default | Allowed values / constraints |
| --- | --- | --- | --- |
| `domains` | array | `required` | `{"minItems": 1, "maxItems": 100, "uniqueItems": true}` |
| `country` | string | `'US'` | `{"enum": ["US", "GB", "CA", "AU", "DE", "FR", "ES", "IT", "NL", "BR", "IN", "MX", "JP", "AL", "DZ", "AO", "AR", "AM", "AT", "AZ", "BH", "BD", "BE", "BO", "BA", "BG", "BF", "KH", "CM", "CL", "CO", "CR", "CI", "HR", "CY", "CZ", "DK", "EC", "EG", "SV", "EE", "FI", "GH", "GR", "GT", "HK", "HU", "ID", "IE", "IL", "JO", "KZ", "KE", "LV", "LT", "MY", "MT", "MD", "MC", "MA", "MM", "NZ", "NI", "NG", "MK", "NO", "PK", "PA", "PY", "PE", "PH", "PL", "PT", "RO", "SA", "SN", "RS", "SG", "SK", "SI", "ZA", "KR", "LK", "SE", "CH", "TW", "TH", "TN", "TR", "UA", "AE", "UY", "VE", "VN"]}` |
| `language` | string | `None` | `{}` |
| `top_keywords` | integer | `20` | `{"minimum": 0, "maximum": 1000}` |
| `competitors` | integer | `10` | `{"minimum": 0, "maximum": 100}` |

## `youtube_transcripts`

Actor: `hirepulse/youtube-transcript-scraper`.

| Argument | Type | Default | Allowed values / constraints |
| --- | --- | --- | --- |
| `videos` | array | `required` | `{"minItems": 1, "maxItems": 1000, "uniqueItems": true}` |
| `language` | string | `None` | `{}` |
| `include_timestamps` | boolean | `False` | `{}` |
