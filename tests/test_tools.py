import inspect
import json
from decimal import Decimal
from importlib.resources import files
from typing import get_args, get_origin, get_type_hints, Literal

import pytest
from apify_client._models import Run
from apify_client._resource_clients.actor import ActorClient

import hirepulse_tools as hp
from hirepulse_tools import _runner
from hirepulse_tools._catalog import TOOL_SLUGS


def schema(slug):
    return json.loads(files("hirepulse_tools").joinpath("schemas").joinpath(f"{slug}.input.json").read_text(encoding="utf-8"))


def required_input(slug):
    spec = schema(slug)
    key = spec["required"][0]
    return {key: spec["properties"][key]["prefill"][:1]}


def field_value(prop):
    if "default" in prop:
        return prop["default"]
    if "enum" in prop:
        return prop["enum"][0]
    if prop["type"] == "array":
        if "enum" in prop.get("items", {}):
            return [prop["items"]["enum"][0]]
        return prop.get("prefill", ["mock filter"])[:1]
    if prop["type"] == "integer":
        return prop.get("minimum", 1)
    if prop["type"] == "string":
        return "US" if "pattern" in prop else ""
    raise AssertionError("Unhandled field type")


@pytest.mark.parametrize("name,slug", TOOL_SLUGS.items())
def test_exact_all_input_keys_and_values(name, slug, mock_apify):
    factory, client, actor, dataset = mock_apify
    values = {key: field_value(prop) for key, prop in schema(slug)["properties"].items()}
    result = getattr(hp, name)(**values, result_limit=5, max_total_charge_usd=0.10)
    factory.assert_called_once_with("your_token_here")
    client.actor.assert_called_once_with(f"hirepulse/{slug}")
    actor.call.assert_called_once_with(
        run_input=values, max_items=5, max_total_charge_usd=Decimal("0.1"), logger=None
    )
    client.dataset.assert_called_once_with("mock-dataset")
    dataset.list_items.assert_called_once_with(limit=5)
    assert result == [{"fixture": "mock row"}]
    assert result[0] is dataset.list_items.return_value.items[0]


@pytest.mark.parametrize("name,slug", TOOL_SLUGS.items())
def test_defaults_match_schema_and_none_is_omitted(name, slug, mock_apify):
    _, _, actor, dataset = mock_apify
    spec = schema(slug)
    fn = getattr(hp, name)
    signature = inspect.signature(fn)
    assert set(signature.parameters) == set(spec["properties"]) | {"result_limit", "max_total_charge_usd"}
    hints = get_type_hints(fn)
    for key, prop in spec["properties"].items():
        param = signature.parameters[key]
        if key in spec["required"]:
            assert param.default is inspect.Parameter.empty
        else:
            assert param.kind is inspect.Parameter.KEYWORD_ONLY
            assert param.default == prop.get("default")
        annotation = hints[key]
        if "enum" in prop:
            assert get_origin(annotation) is Literal
            assert get_args(annotation) == tuple(prop["enum"])
    fn(**required_input(slug))
    expected = required_input(slug) | {
        key: prop["default"] for key, prop in spec["properties"].items() if "default" in prop
    }
    actor.call.assert_called_once_with(
        run_input=expected, max_items=60, max_total_charge_usd=Decimal("1.0"), logger=None
    )
    dataset.list_items.assert_called_once_with(limit=60)


@pytest.mark.parametrize("name,slug", TOOL_SLUGS.items())
def test_cap_still_applies_if_dataset_ignores_limit(name, slug, mock_apify):
    mock_apify[3].list_items.return_value.items = [{"fixture": str(i)} for i in range(10)]
    assert len(getattr(hp, name)(**required_input(slug), result_limit=2)) == 2


@pytest.mark.parametrize("name,slug", TOOL_SLUGS.items())
@pytest.mark.parametrize("token", [None, "", "   "])
def test_missing_token_is_clear(name, slug, token, monkeypatch, mock_apify):
    if token is None:
        monkeypatch.delenv("APIFY_TOKEN", raising=False)
    else:
        monkeypatch.setenv("APIFY_TOKEN", token)
    with pytest.raises(hp.MissingTokenError, match="Set APIFY_TOKEN in the environment"):
        getattr(hp, name)(**required_input(slug))
    mock_apify[0].assert_not_called()


@pytest.mark.parametrize("status", [None, "FAILED", "ABORTED", "TIMED-OUT", "RUNNING"])
def test_unsuccessful_runs_do_not_fetch(status, mock_apify):
    mock_apify[2].call.return_value = None if status is None else Run.model_construct(status=status)
    with pytest.raises(hp.ActorRunError, match="SUCCEEDED"):
        hp.company_intent(["stripe.com"])
    mock_apify[1].dataset.assert_not_called()


@pytest.mark.parametrize("dataset_id", [None, "", 1])
def test_missing_dataset_is_clear(dataset_id, mock_apify):
    mock_apify[2].call.return_value = Run.model_construct(status="SUCCEEDED", default_dataset_id=dataset_id)
    with pytest.raises(hp.ActorRunError, match="dataset ID"):
        hp.company_intent(["stripe.com"])


@pytest.mark.parametrize("stage", ["construction", "call", "dataset"])
def test_sdk_errors_do_not_echo_exception_text(stage, mock_apify):
    boundary = {"construction": mock_apify[0], "call": mock_apify[2].call, "dataset": mock_apify[3].list_items}[stage]
    boundary.side_effect = RuntimeError("untrusted SDK exception details")
    with pytest.raises(hp.ActorRunError) as caught:
        hp.company_intent(["stripe.com"])
    assert "untrusted SDK" not in str(caught.value)
    assert caught.value.__suppress_context__


@pytest.mark.parametrize("value", [0, -1, 1001, True, 1.5, "5"])
def test_invalid_result_limit_prevents_run(value, mock_apify):
    with pytest.raises(ValueError, match="result_limit"):
        hp.company_intent(["stripe.com"], result_limit=value)
    mock_apify[0].assert_not_called()


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan"), True, "1", None])
def test_invalid_spending_cap_prevents_run(value, mock_apify):
    with pytest.raises(ValueError, match="max_total_charge_usd"):
        hp.company_intent(["stripe.com"], max_total_charge_usd=value)
    mock_apify[0].assert_not_called()


@pytest.mark.parametrize("name,slug", TOOL_SLUGS.items())
def test_enums_bounds_patterns_and_arrays_are_validated(name, slug, mock_apify):
    fn = getattr(hp, name)
    base = required_input(slug)
    for key, prop in schema(slug)["properties"].items():
        invalids = []
        if "enum" in prop:
            invalids.append("not-an-allowed-value")
        if "minimum" in prop:
            invalids.extend([prop["minimum"] - 1, True])
        if "maximum" in prop:
            invalids.append(prop["maximum"] + 1)
        if "pattern" in prop:
            invalids.append("invalid-country")
        if prop["type"] == "array":
            invalids.extend(["not-a-list", [1]])
            if "minItems" in prop:
                invalids.append([])
            if "maxItems" in prop:
                invalids.append(["mock"] * (prop["maxItems"] + 1))
            if prop.get("uniqueItems"):
                invalids.append(["mock", "mock"])
        for invalid in invalids:
            with pytest.raises(ValueError):
                fn(**(base | {key: invalid}))
    mock_apify[0].assert_not_called()


def test_employment_enum_spelling_is_exact(mock_apify):
    hp.google_jobs(["data engineer"], employment_types=["partime"])
    with pytest.raises(ValueError):
        hp.google_jobs(["data engineer"], employment_types=["parttime"])


def test_empty_and_malformed_dataset(mock_apify):
    mock_apify[3].list_items.return_value.items = []
    assert hp.company_intent(["stripe.com"]) == []
    mock_apify[3].list_items.return_value.items = ["not a dict"]
    with pytest.raises(hp.ActorRunError, match="read the dataset"):
        hp.company_intent(["stripe.com"])


def test_spending_options_exist_in_real_sdk_signature():
    parameters = inspect.signature(ActorClient.call).parameters
    assert {"run_input", "max_items", "max_total_charge_usd", "logger"} <= set(parameters)


def test_no_file_token_loading(monkeypatch, tmp_path, mock_apify):
    monkeypatch.delenv("APIFY_TOKEN")
    # Only a public placeholder, never a real token.
    (tmp_path / ".env").write_text("APIFY_TOKEN=your_token_here", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(hp.MissingTokenError):
        hp.company_intent(["stripe.com"])
    mock_apify[0].assert_not_called()
