"""Shared environment-only authentication, validation, execution and dataset reading."""

from __future__ import annotations

import json
import math
import os
import re
from decimal import Decimal
from functools import lru_cache
from importlib.resources import files
from typing import Any

from apify_client import ApifyClient
from jsonschema import Draft7Validator

from ._run_context import KNOWN_OUTCOMES, active_context

DEFAULT_RESULT_LIMIT = 60
DEFAULT_MAX_TOTAL_CHARGE_USD = 1.0


def _capture_run_summary(client: Any, run: Any, dataset_id: str, page: Any) -> None:
    """Read only the existing run's outcome when MCP explicitly requests it.

    Summary failures never hide successfully fetched rows or trigger another run.
    Raw summaries, upstream errors, tokens and unknown outcome strings are not exposed.
    """
    context = active_context.get()
    if context is None:
        return
    run_id = getattr(run, "id", None)
    context.run_id = run_id if isinstance(run_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,80}", run_id) else None
    context.dataset_id = dataset_id
    total = getattr(page, "total", None)
    context.dataset_total = total if type(total) is int and total >= 0 else None
    store_id = getattr(run, "default_key_value_store_id", None)
    if not isinstance(store_id, str) or not store_id:
        context.summary_status = "missing_store"
        return
    try:
        record = client.key_value_store(store_id).get_record("OUTPUT")
        if record is None:
            context.summary_status = "not_found"
            return
        value = record.get("value") if isinstance(record, dict) else getattr(record, "value", None)
        outcome = value.get("outcome") if isinstance(value, dict) else None
        if not isinstance(outcome, str) or outcome not in KNOWN_OUTCOMES:
            context.summary_status = "unrecognized"
            return
        context.outcome = outcome
        context.summary_status = "available"
    except Exception:
        context.summary_status = "unavailable"


class HirePulseError(RuntimeError):
    """Safe error with a machine-readable next action for an agent."""

    def __init__(self, message: str, suggested_agent_action: str) -> None:
        super().__init__(message)
        self.message = message
        self.suggested_agent_action = suggested_agent_action

    def to_dict(self) -> dict[str, str]:
        return {"message": self.message, "suggested_agent_action": self.suggested_agent_action}


class InvalidInputError(HirePulseError, ValueError):
    """Invalid local arguments; remains compatible with ValueError handlers."""


class MissingTokenError(HirePulseError):
    """APIFY_TOKEN is missing or empty."""


class ActorRunError(HirePulseError):
    """The run failed, did not finish successfully, or had no usable dataset."""


@lru_cache(maxsize=8)
def input_schema(slug: str) -> dict[str, Any]:
    """Read the bundled input schema snapshot."""
    return json.loads(
        files("hirepulse_tools").joinpath("schemas").joinpath(f"{slug}.input.json").read_text(encoding="utf-8")
    )


def _validate_input(slug: str, run_input: dict[str, Any]) -> None:
    schema = input_schema(slug)
    if set(run_input) - set(schema["properties"]):
        raise InvalidInputError(
            "Actor input contains an unknown field",
            "Remove unknown fields; use the tool input schema or docs/inputs.md.",
        )
    # Do not echo input values: callers may have included sensitive information.
    error = next(Draft7Validator(schema).iter_errors(run_input), None)
    if error is not None:
        field = str(next(iter(error.path), "input"))
        raise InvalidInputError(
            f"Invalid {field}: violates schema {error.validator} constraint",
            f"Correct {field} using the tool input schema or docs/inputs.md; pass arrays of strings for list fields.",
        ) from None
    for name, value in run_input.items():
        # Apify stringList editors do not always include JSON Schema 'items'.
        if schema["properties"][name]["type"] == "array":
            if any(not isinstance(item, str) for item in value):
                raise InvalidInputError(
                    f"Invalid {name}: expected a list of strings",
                    f"Pass {name} as an array containing only strings.",
                )


def run_actor(
    slug: str,
    values: dict[str, Any],
    *,
    result_limit: int = DEFAULT_RESULT_LIMIT,
    max_total_charge_usd: float = DEFAULT_MAX_TOTAL_CHARGE_USD,
) -> list[dict[str, Any]]:
    """Run once, require SUCCEEDED, and return at most result_limit dataset rows.

    None means omitted for optional Actor inputs, never JSON null. Wrapper caps
    are call options, not Actor input. SDK exception text is deliberately hidden.
    """
    if type(result_limit) is not int or not 1 <= result_limit <= 1000:
        raise InvalidInputError(
            "result_limit must be an integer from 1 to 1000",
            "Set result_limit to an integer from 1 to 1000; start with 5.",
        )
    if (
        isinstance(max_total_charge_usd, bool)
        or not isinstance(max_total_charge_usd, (int, float))
        or not math.isfinite(max_total_charge_usd)
        or max_total_charge_usd <= 0
    ):
        raise InvalidInputError(
            "max_total_charge_usd must be a finite positive number",
            "Set max_total_charge_usd to a finite positive number within the approved budget.",
        )
    run_input = {key: value for key, value in values.items() if value is not None}
    _validate_input(slug, run_input)
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        raise MissingTokenError(
            "Set APIFY_TOKEN in the environment before calling a tool",
            "Set the APIFY_TOKEN environment variable in the server process; never put a token in tool arguments.",
        )
    try:
        client = ApifyClient(token)
        run = client.actor(f"hirepulse/{slug}").call(
            run_input=run_input,
            max_items=result_limit,
            max_total_charge_usd=Decimal(str(max_total_charge_usd)),
            logger=None,
        )
    except Exception:
        raise ActorRunError(
            f"Could not run hirepulse/{slug}; check Apify run details",
            "Check Apify authentication, input and run details before retrying; a run may already exist and incur charges.",
        ) from None
    if run is None or getattr(run, "status", None) != "SUCCEEDED":
        raise ActorRunError(
            f"hirepulse/{slug} did not finish with status SUCCEEDED",
            "Inspect the existing Apify run status and logs before retrying; do not automatically start another paid run.",
        )
    dataset_id = getattr(run, "default_dataset_id", None)
    if not isinstance(dataset_id, str) or not dataset_id:
        raise ActorRunError(
            f"hirepulse/{slug} returned no default dataset ID",
            "Inspect the existing Apify run and its dataset; avoid starting another paid run just to retrieve results.",
        )
    try:
        page = client.dataset(dataset_id).list_items(limit=result_limit)
        items = page.items[:result_limit]
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise TypeError("Unexpected dataset item shape")
    except Exception:
        raise ActorRunError(
            f"Could not read the dataset for hirepulse/{slug}",
            "Check access to the existing run dataset and retry retrieval there; do not rerun the Actor automatically.",
        ) from None
    _capture_run_summary(client, run, dataset_id, page)
    return items
