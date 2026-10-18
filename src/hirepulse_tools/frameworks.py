"""Optional LangChain and CrewAI tool adapters for the independent gateway."""
from __future__ import annotations
import json
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .gateway import GatewayClient

class CompanyInput(BaseModel):
    """Public company domain."""
    model_config = ConfigDict(extra='forbid')
    domain: str = Field(description='Company domain without scheme or path, e.g. linear.app')

class JobsInput(CompanyInput):
    known_job_ids: list[str] | None = Field(default=None, description='Previously seen job IDs for comparison')
    diff_only: bool = Field(default=False, description='Return only new jobs')

class AdsInput(CompanyInput):
    region: str | None = Field(default=None, description='Optional supported region code, e.g. US or GB')

class ScanInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    domains: list[str] | None = Field(default=None, min_length=2, max_length=25, description='Company domains for a free scan')
    quote_id: str | None = Field(default=None, description='Existing quote; requires a payment-enabled client to redeem')
    min_intent_score: int = Field(default=70, ge=0, le=100, description='Hot-buyer hiring score threshold')

    @model_validator(mode='after')
    def check_input(self):
        if bool(self.domains) == bool(self.quote_id):
            raise ValueError('Supply domains or quote_id, but not both')
        return self

class BatchInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    domains: list[str] | None = Field(default=None, min_length=1, max_length=50, description='Company domains for a free quote')
    tool: Literal['tech-stack', 'ats-jobs', 'company-intent', 'google-ads', 'company-profile'] | None = Field(default=None, description='Lookup to perform for every domain')
    quote_id: str | None = Field(default=None, description='Existing quote; requires a payment-enabled client to redeem')

    @model_validator(mode='after')
    def check_input(self):
        if self.quote_id:
            if self.domains or self.tool:
                raise ValueError('Send quote_id alone')
        elif not self.domains or not self.tool:
            raise ValueError('Supply domains and tool, or quote_id')
        if self.tool == 'company-profile' and len(self.domains or []) > 33:
            raise ValueError('company-profile batch limit is 33 domains')
        return self

SPECS = [
    ('detect_website_tech_stack', 'tech-stack', CompanyInput, 'Website technologies, ad pixels, analytics, CMS, hosting and email DNS.'),
    ('get_company_open_jobs', 'ats-jobs', JobsInput, 'Open company jobs from supported public ATS boards; optional job changes.'),
    ('get_company_hiring_intent', 'company-intent', CompanyInput, 'Hiring signals, role counts, hiring functions and a hiring-based intent score.'),
    ('get_google_ads_by_domain', 'google-ads', AdsInput, 'Advertisers and ads from Google Ads Transparency for a company domain.'),
    ('get_company_profile', 'company-profile', CompanyInput, 'Combined website tech, hiring signals and Google Ads company profile.'),
    ('company_footprint_check', 'company-footprint', CompanyInput, 'Public operating signals marked found, not_found or unknown; no fraud or revenue estimate.'),
    ('find_hot_buyers', 'hot-buyers', ScanInput, 'Free hiring scan and quote for 2-25 domains; paid profiles cost $0.25 per hot company.'),
    ('batch_lookup', 'batch', BatchInput, 'Free bulk lookup quote, priced by rows with data. Redeeming requires x402 payment.'),
]
NOTICE = ' Five successful daily free calls per IP are shared across lookups. Scans have separate limits. Empty results are not charged. This adapter never signs payments; HTTP 402 raises PaymentRequired.'

def _function(path: str, schema: type[BaseModel], client: GatewayClient):
    def invoke(**kwargs: Any) -> str:
        values = schema(**kwargs).model_dump(exclude_none=True)
        if values.get('quote_id'):
            values = {'quote_id': values['quote_id']}
        return json.dumps(client.lookup(path, **values))
    return invoke

def get_langchain_tools(client: GatewayClient | None = None) -> list[Any]:
    """Return eight StructuredTools; install hirepulse-tools[langchain]."""
    from langchain_core.tools import StructuredTool
    client = client or GatewayClient()
    return [StructuredTool.from_function(func=_function(path, schema, client), name=name,
            description=description+NOTICE, args_schema=schema)
            for name, path, schema, description in SPECS]

def get_crewai_tools(client: GatewayClient | None = None) -> list[Any]:
    """Return eight BaseTools; install hirepulse-tools[crewai]."""
    from crewai.tools import BaseTool
    client = client or GatewayClient()
    result = []
    for name, path, schema, description in SPECS:
        invoke = _function(path, schema, client)
        def run(self, _invoke=invoke, **kwargs: Any) -> str:
            return _invoke(**kwargs)
        cls = type('HirePulse_'+name, (BaseTool,), {
            '__module__': __name__,
            '__annotations__': {'name': str, 'description': str, 'args_schema': type[BaseModel]},
            'name': name, 'description': description+NOTICE, 'args_schema': schema, '_run': run,
        })
        result.append(cls())
    return result
