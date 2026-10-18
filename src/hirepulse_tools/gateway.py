"""Client for the independent HirePulse gateway. No Apify account required."""
from __future__ import annotations
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

TOOLS = ('tech-stack', 'ats-jobs', 'company-intent', 'google-ads',
         'company-profile', 'company-footprint', 'hot-buyers', 'batch')

class GatewayError(RuntimeError):
    """A gateway request failed. The original response is available in body."""
    def __init__(self, status: int, body: Any):
        super().__init__(f'HirePulse gateway returned HTTP {status}')
        self.status = status
        self.body = body

class PaymentRequired(GatewayError):
    """Free allowance exhausted; no payment was attempted by this client."""
    def __init__(self, body: Any, payment_required: str | None):
        super().__init__(402, body)
        self.payment_required = payment_required

class GatewayClient:
    """Call eight gateway tools. Never signs or pays automatically.

    Five successful calls per UTC day per IP are shared across tools.
    Batch and hot-buyers use their documented quote flows and scan limits.
    PaymentRequired exposes the x402 challenge for a separate payment client.
    """
    def __init__(self, *, timeout: float = 120):
        if timeout <= 0:
            raise ValueError('timeout must be positive')
        self.timeout = timeout
        self.base_url = 'https://gethirepulse.xyz'

    def _request(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        req = Request(self.base_url + path,
                      data=json.dumps(body).encode() if body is not None else None,
                      headers={'User-Agent': 'hirepulse-tools/gateway',
                               'Content-Type': 'application/json', 'Accept': 'application/json'},
                      method='POST' if body is not None else 'GET')
        try:
            with urlopen(req, timeout=self.timeout) as response:
                return json.load(response)
        except HTTPError as exc:
            try:
                payload = json.loads(exc.read())
            except (ValueError, OSError):
                payload = {'status': exc.code}
            if exc.code == 402:
                raise PaymentRequired(payload, exc.headers.get('PAYMENT-REQUIRED')) from None
            raise GatewayError(exc.code, payload) from None
        except URLError:
            raise GatewayError(0, {'detail': 'Gateway connection failed; request was not retried'}) from None

    def catalog(self) -> dict[str, Any]:
        return self._request('/v1/catalog')

    def lookup(self, tool: str, /, **body: Any) -> dict[str, Any]:
        if tool not in TOOLS:
            raise ValueError(f'Unknown gateway tool; choose one of {TOOLS}')
        return self._request('/v1/' + tool, body)

    def tech_stack(self, domain: str) -> dict[str, Any]:
        return self.lookup('tech-stack', domain=domain)

    def open_jobs(self, domain: str, **options: Any) -> dict[str, Any]:
        return self.lookup('ats-jobs', domain=domain, **options)

    def hiring_intent(self, domain: str) -> dict[str, Any]:
        return self.lookup('company-intent', domain=domain)

    def google_ads(self, domain: str, **options: Any) -> dict[str, Any]:
        return self.lookup('google-ads', domain=domain, **options)

    def company_profile(self, domain: str) -> dict[str, Any]:
        return self.lookup('company-profile', domain=domain)

    def company_footprint(self, domain: str) -> dict[str, Any]:
        return self.lookup('company-footprint', domain=domain)

    def hot_buyers(self, domains: list[str], *, min_intent_score: int = 70) -> dict[str, Any]:
        return self.lookup('hot-buyers', domains=domains, min_intent_score=min_intent_score)

    def batch(self, tool: str, domains: list[str]) -> dict[str, Any]:
        return self.lookup('batch', tool=tool, domains=domains)
